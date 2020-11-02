#!/usr/bin/env python3
import click
import requests
import requests.exceptions as reqerrors
import logging
from pathlib import Path
import os
import json
from pprint import pprint
from tabulate import tabulate
import yaml
#from click_option_group import optgroup, MutuallyExclusiveOptionGroup

def create_config_dir():
    home = Path(os.getenv('HOME'))
    Path.mkdir(home / '.config', exist_ok=True)
    synadm_config = home / '.config'
    return synadm_config

def create_data_dir():
    home = Path(os.getenv('HOME'))
    Path.mkdir(home / '.local' / 'share' / 'synadm', parents=True, exist_ok=True)
    synadm_data = home / '.local' / 'share' / 'synadm'
    return synadm_data

def logger_init():
    synadm_data = create_data_dir()
    debug_log = synadm_data / "debug.log"

    log = logging.getLogger('synadm')
    log.setLevel(logging.DEBUG) # level of logger itself
    f_handle = logging.FileHandler(debug_log, encoding='utf-8') # create file handler
    f_handle.setLevel(logging.DEBUG) # which logs even debug messages
    c_handle = logging.StreamHandler() # console handler with a higher log level
    c_handle.setLevel(logging.WARNING) # level of the console handler
    # create formatters and add it to the handlers
    f_form = logging.Formatter('%(asctime)s %(name)-8s %(levelname)-7s %(message)s',
             datefmt='%Y-%m-%d %H:%M:%S')
    c_form = logging.Formatter('%(levelname)-5s %(message)s')
    c_handle.setFormatter(c_form)
    f_handle.setFormatter(f_form)
    log.addHandler(c_handle) # add the handlers to logger
    log.addHandler(f_handle)
    return log

class Synapse_admin (object):
    def __init__(self, user, token, host, port, ssl):
        self.proto = 'https' if ssl == True else 'http'
        self.host = host
        self.port = port
        self.user = user
        self.token = token

    def _get(self, urlpart):
        headers={'Accept': 'application/json', 'Authorization': 'Bearer ' + self.token }
        url=f'{self.proto}://{self.host}:{self.port}/_synapse/admin/{urlpart}'
        log.info('_get url: {}\n'.format(url))
        try:
            resp = requests.get(url, headers=headers, timeout=7)
            resp.raise_for_status()
            if resp.ok:
                _json = json.loads(resp.content)
                return _json
            else:
                log.warning("No valid response from Synapse. Returning None.")
                return None
        except reqerrors.HTTPError as errh:
            log.error("HTTPError: %s\n", errh)
            #if "Not found" in errh.response.text:
            #    log.warning("AcousticBrainz doesn't have this recording yet. Consider submitting it!")
            return None
        except reqerrors.ConnectionError as errc:
            log.error("ConnectionError: %s\n", errc)
            return None
        except reqerrors.Timeout as errt:
            log.error("Timeout: %s\n", errt)
            return None
        except reqerrors.RequestException as erre:
            log.error("RequestException: %s\n", erre)
            return None

    def _post(self, urlpart, post_data):
        headers={'Accept': 'application/json', 'Authorization': 'Bearer ' + self.token }
        url=f'{self.proto}://{self.host}:{self.port}/_synapse/admin/{urlpart}'
        log.info('_post url: {}\n'.format(url))
        log.info('_post data: {}\n'.format(post_data))
        try:
            resp = requests.post(url, headers=headers, timeout=7, data=post_data)
            resp.raise_for_status()
            if resp.ok:
                _json = json.loads(resp.content)
                return _json
            else:
                log.warning("No valid response from Synapse. Returning None.")
                return None
        except reqerrors.HTTPError as errh:
            log.error("HTTPError: %s\n", errh)
            return None
        except reqerrors.ConnectionError as errc:
            log.error("ConnectionError: %s\n", errc)
            return None
        except reqerrors.Timeout as errt:
            log.error("Timeout: %s\n", errt)
            return None
        except reqerrors.RequestException as erre:
            log.error("RequestException: %s\n", erre)
            return None

    def user_list(self, _from=0, _limit=100, _guests=False, _deactivated=False,
          _name=None, _user_id=None): # if --options missing they are None too, let's stick with that.
        _deactivated_s = 'true' if _deactivated else 'false'
        _guests_s = 'true' if _guests else 'false'
        urlpart = f'v2/users?from={_from}&limit={_limit}&guests={_guests_s}&deactivated={_deactivated_s}'
        # optional filters
        if _name:
            urlpart+= f'&name={_name}'
        elif _user_id:
            urlpart+= f'&user_id={_user_id}'
        return self._get(urlpart)

    def user_deactivate(self, user_id, gdpr_erase):
        urlpart = f'v1/deactivate/{user_id}'
        data = '{"erase": true}' if gdpr_erase else {}
        return self._post(urlpart, data)

    def room_list(self):
        urlpart = f'v1/rooms'
        return self._get(urlpart)

    def version(self):
        urlpart = f'v1/server_version'
        return self._get(urlpart)

def modify_usage_error(main_command):
    '''a method to append the help menu to an usage error
    :param main_command: top-level group or command object constructed by click wrapper
    '''
    from click._compat import get_text_stderr
    from click.utils import echo
    def show(self, file=None):
        import sys
        if file is None:
            file = get_text_stderr()
        color = None
        if self.ctx is not None:
            color = self.ctx.color
            echo(self.ctx.get_usage() + '\n', file=file, color=color)
        echo('Error: %s\n' % self.format_message(), file=file, color=color)
        sys.argv = [sys.argv[0]]
        main_command()

    click.exceptions.UsageError.show = show
  
def read_yaml(yamlfile):
    """expects path/file"""
    try:
        with open(str(yamlfile), "r") as fyamlfile:
            return yaml.load(fyamlfile, Loader=yaml.SafeLoader)
    except IOError as errio:
        log.error("Can't find %s.", yamlfile)
        raise errio
        #raise SystemExit(3)
        #return False
    except yaml.parser.ParserError as errparse:
        log.error("ParserError in %s.", yamlfile)
        #raise errparse
        raise SystemExit(3)
    except yaml.scanner.ScannerError as errscan:
        log.error("ScannerError in %s.", yamlfile)
        #raise errscan
        raise SystemExit(3)
    except Exception as err:
        log.error(" trying to load %s.", yamlfile)
        raise err
        #raise SystemExit(3)

def write_yaml(data, yamlfile):
    """data expects dict, yamlfile expects path/file"""
    try:
        with open(yamlfile, "w") as fyamlfile:
            yaml.dump(data, fyamlfile, default_flow_style=False,
                             allow_unicode=True)
            return True
    except IOError as errio:
        log.error("IOError: could not write file %s \n\n", yamlfile)
        #raise errio
        raise SystemExit(3)
    except Exception as err:
        log.error(" trying to write %s \n\n", yamlfile)
        #raise err
        raise SystemExit(3)

def get_table(data):
    headers_dict = {}
    for header in data[0]:
        headers_dict.update({header: header})
    return tabulate(data, tablefmt="simple",
          headers=headers_dict)




# handle logging and configuration prerequisites
log = logger_init()
create_config_dir()

### main synadm command group starts here ###
@click.group(invoke_without_command=False)
@click.option('--verbose', '-v', count=True, default=False,
      help="enable INFO (-v) or DEBUG (-vv) logging on console")
@click.option('--raw', '-r', is_flag=True, default=False,
      help="print raw json data (no tables)")
@click.option('--config-file', '-c', type=click.Path(), default='~/.config/synadm.yaml',
      help="configuration file path", show_default=True)
@click.pass_context
def synadm(ctx, verbose, raw, config_file):
    def _eventually_run_config():
        if ctx.invoked_subcommand != 'config':
            ctx.invoke(config)
            click.echo("Now try running your command again!")
            raise SystemExit(1)
        return None # do nothing if it's config command already

    if verbose == 1:
        log.handlers[0].setLevel(logging.INFO) # set cli handler to INFO,
    elif verbose > 1:
        log.handlers[0].setLevel(logging.DEBUG) # or to DEBUG level

    filename = os.path.expanduser(config_file)
    try:
        conf = read_yaml(filename)
    except IOError:
        Path(filename).touch()
        conf = read_yaml(filename)
    log.debug("read configuration from file {}".format(filename))
    log.debug("{}\n".format(conf))

    ctx.obj = {
        'config_file': filename,
        'raw': raw,
    }
    log.debug("ctx.obj: {}\n".format(ctx.obj))
    try:
        ctx.obj['user'] = conf['user']
        ctx.obj['token'] = conf['token']
        ctx.obj['host'] = conf['host']
        ctx.obj['port'] = conf['port']
        ctx.obj['ssl'] = conf['ssl']
        log.debug("ctx.obj: {}\n".format(ctx.obj))
    except KeyError as keyerr:
        click.echo("Missing entry in configuration file: {}".format(keyerr))
        _eventually_run_config()
    except TypeError as typeerr:
        click.echo("Configuration file is empty")
        _eventually_run_config()


### user commands group starts here ###
@synadm.group()
@click.pass_context
def user(ctx):
    """list, add, modify, deactivate/erase users,
       reset passwords.
    """


#### user commands start here ###
@user.command()
@click.option('--start-from', '-f', type=int, default=0, show_default=True,
      help="offset user listing by given number. This option is also used for pagination.")
@click.option('--limit', '-l', type=int, default=100, show_default=True,
      help="limit user listing to given number")
@click.option('--no-guests', '-N', is_flag=True, default=True, show_default=True,
      help="don't show guest users")
@click.option('--deactivated', '-d', is_flag=True, default=False, show_default=True,
      help="also show deactivated/erased users")
#@optgroup.group('Search options', cls=MutuallyExclusiveOptionGroup,
#                help='')
@click.option('--name', '-n', type=str,
      help="search users by name - the full matrix ID's (@user:server) and display names")
@click.option('--user-id', '-i', type=str,
      help="search users by id - the left part before the colon of the matrix ID's (@user:server)")
@click.pass_context
def list(ctx, start_from, limit, no_guests, deactivated, name, user_id):
    log.info(f'user list options: {ctx.params}\n')
    synadm = Synapse_admin(ctx.obj['user'], ctx.obj['token'], ctx.obj['host'],
          ctx.obj['port'], ctx.obj['ssl'])
    users = synadm.user_list(start_from, limit, no_guests, deactivated, name, user_id)
    if users == None:
        click.echo("Users could not be fetched.")
        raise SystemExit(1)

    if ctx.obj['raw']:
        pprint(users)
    else:
        click.echo(
              "\nTotal users on homeserver (excluding deactivated): {}\n".format(
              users['total']))
        if int(users['total']) != 0:
            tab_users = get_table(users['users'])
            click.echo(tab_users)
        if 'next_token' in users:
            click.echo(
                "\nThere is more users than shown, use '--from {}' to view them.\n".format(
                users['next_token']))

@user.command()
@click.argument('user_id', type=str)
      #help='the matrix user ID to deactivate/erase (user:server')
@click.option('--gdpr-erase', '-e', is_flag=True, default=False, show_default=True,
      help="""marks the user as GDPR-erased. This means messages sent by the user
              will still be visible by anyone that was in the room when these messages
              were sent, but hidden from users joining the room afterwards.""")
@click.pass_context
def deactivate(ctx, user_id, gdpr_erase):
    """deactivate or gdpr-erase users. Provide matrix user ID (@user:server) as argument.
    """
    log.info(f'user deactivate options: {ctx.params}\n')
    synadm = Synapse_admin(ctx.obj['user'], ctx.obj['token'], ctx.obj['host'],
          ctx.obj['port'], ctx.obj['ssl'])
    deactivated = synadm.user_deactivate(user_id, gdpr_erase)
    if deactivated == None:
        click.echo("User could not be deactivated/erased.")
        raise SystemExit(1)

    if ctx.obj['raw']:
        pprint(deactivated)
    else:
        if deactivated['id_server_unbind_result'] == 'success':
            click.echo('User successfully deactivated/erased.')
        else:
            click.echo('Synapse returned: {}'.format(deactivated['id_server_unbind_result']))



### room commands group starts here ###
@synadm.group()
def room():
    """list/delete rooms, show/invite/join members, ...
    """


### room commands starts here ###
@room.command()
@click.pass_context
def list(ctx):
    synadm = Synapse_admin(ctx.obj['user'], ctx.obj['token'], ctx.obj['host'],
          ctx.obj['port'], ctx.obj['ssl'])
    rooms = synadm.room_list()
    if rooms == None:
        click.echo("Rooms could not be fetched.")
        raise SystemExit(1)

    if ctx.obj['raw']:
        pprint(rooms)
    else:
        if int(rooms['total_rooms']) != 0:
            tab_rooms = get_table(rooms['rooms'])
            click.echo(tab_rooms)


### the version command starts here ###
@synadm.command()
@click.pass_context
def version(ctx):
    synadm = Synapse_admin(ctx.obj['user'], ctx.obj['token'], ctx.obj['host'],
                           ctx.obj['port'], ctx.obj['ssl'])

    version = synadm.version()
    if version == None:
        click.echo("Version could not be fetched.")
        raise SystemExit(1)

    if ctx.obj['raw']:
        pprint(version)
    else:
        click.echo("Synapse version: {}".format(version['server_version']))
        click.echo("Python version: {}".format(version['python_version']))


### the config command starts here ###
@synadm.command()
@click.option('--user', '-u', type=str, default="admin",
    help="admin user for accessing the Synapse admin API's",)
@click.option('--token', '-t', type=str,
    help="admin user's access token for the Synapse admin API's",)
@click.option('--host', '-h', type=str, default="localhost",
    help="the hostname running the Synapse admin API's",)
@click.option('--port', '-p', type=int, default=8008,
    help="the port the Synapse admin API's are listening on",)
@click.option('--ssl', '-s', is_flag=True, default=False,
    help="weather https should be used or not.",)
@click.pass_context
def config(ctx, user, token, host, port, ssl):
    """modify synadm's configuration.
       configuration details are asked interactively but can also be provided using Options:"""
    config_file = os.path.expanduser(ctx.obj['config_file'])

    api_user = click.prompt("Synapse admin user name", default=user)
    api_token = click.prompt("Synapse admin user token", default=token)
    api_host = click.prompt("Synapse admin API host", default=host)
    api_port = click.prompt("Synapse admin API port", default=port)
    api_ssl = click.prompt("Use SSL (y/N)?", default=ssl, type=bool, show_default=False)
    conf_dict = {"user": api_user, "token": api_token, "host": api_host,
          "port": api_port, "ssl": api_ssl}
    click.echo('Configuration will now be written to {}'.format(config_file))
    write_yaml(conf_dict, config_file)
    click.echo('Done.')


if __name__ == '__main__':
    synadm(obj={})
