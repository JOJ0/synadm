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

def logger_init():
    synadmin_root = Path(os.path.dirname(os.path.abspath(__file__)))
    debug_log = synadmin_root / "debug.log"

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
    def __init__(self, user, token, host, port):
        self.host = host
        self.port = port
        self.user = user
        self.token = token

    def _get(self, urlpart):
        headers={'Accept': 'application/json' }
        tokenpart=f"access_token={self.token}"
        # take care of putting & or ? at end of urlpart in calling method already!
        url="http://{}:{}/_synapse/admin/{}{}".format(self.host, self.port,
              urlpart, tokenpart)
        log.debug('_get_synapse url: {}\n'.format(url))
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

    def user_list(self):
        ufrom = 0
        ulimit = 50
        udeactivated = 'false'
        urlpart = f'v2/users?from={ufrom}&limit={ulimit}&deactivated={udeactivated}&'
        return self._get(urlpart)

    def room_list(self):
        urlpart = f'v1/rooms?'
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




log = logger_init()

### main synadm command group starts here ###
@click.group(invoke_without_command=False)
@click.option('--verbose', '-v', count=True, default=False,
      help="enable INFO or DEBUG logging on console")
@click.option('--raw', '-r', is_flag=True, default=False,
      help="print raw json data (no tables)")
@click.option('--config-file', '-c', type=click.Path(), default='~/.synadm',
      help="configuration file path")
@click.pass_context
def synadm(ctx, verbose, raw, config_file):
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
        log.debug("ctx.obj: {}\n".format(ctx.obj))
    except KeyError as keyerr:
        click.echo("Missing entry in configuration file: {}".format(keyerr))
        #raise SystemExit(1)
    except TypeError as typeerr:
        click.echo("Configuration file is empty")


### user commands group starts here ###
@synadm.group()
@click.pass_context
def user(ctx):
    """list, add, modify or deactivate/delete users
       and reset passwords.
    """


#### user commands start here ###
@user.command()
@click.pass_context
def list(ctx):
    synadm = Synapse_admin(ctx.obj['user'], ctx.obj['token'], ctx.obj['host'],
          ctx.obj['port'])
    users = synadm.user_list()
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


### room commands group starts here ###
@synadm.group()
def room():
    """list rooms, modify their settings,... FIXME
    """


### room commands starts here ###
@room.command()
@click.pass_context
def list(ctx):
    synadm = Synapse_admin(ctx.obj['user'], ctx.obj['token'], ctx.obj['host'],
          ctx.obj['port'])
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


### the config command starts here ###
@synadm.command()
@click.option('--user', '-u', type=str, default="admin",
    help="admin user for accessing the Synapse Admin API's",)
@click.option('--token', '-t', type=str,
    help="admin user's access token for the Synapse Admin API's",)
@click.option('--host', '-h', type=str, default="localhost",
    help="the hostname running the Synapse Admin API's",)
@click.option('--port', '-p', type=str, default="8008",
    help="the port the Synapse API is listening on (default: 8008)",)
@click.pass_context
def config(ctx, user, token, host, port):
    """store synadm's configuration in a file (default: ~/.synadm)."""
    config_file = os.path.expanduser(ctx.obj['config_file'])

    api_user = click.prompt("Please enter your API user", default=user)
    api_token = click.prompt("Please enter your API token", default=token)
    api_host = click.prompt("Please enter your API host", default=token)
    api_port = click.prompt("Please enter your API port", default=token)
    conf_dict = {"user": api_user, "token": api_token, "host": api_host, "port": api_port}
    write_yaml(conf_dict, config_file)


if __name__ == '__main__':
    synadm(obj={})
