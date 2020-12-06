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
from click_option_group import optgroup, MutuallyExclusiveOptionGroup, RequiredAnyOptionGroup

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

class Http_request:
    def __init__(self, token, base_url, path):
        self.token = token
        self.base_url = base_url.strip('/')
        self.path = path.strip('/')
        self.headers = {'Accept': 'application/json',
                        'Authorization': 'Bearer ' + self.token
        }

    def _get(self, urlpart):
        url=f'{self.base_url}/{self.path}/{urlpart}'
        log.info('_get url: {}\n'.format(url))
        try:
            resp = requests.get(url, headers=self.headers, timeout=7)
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

    def _post(self, urlpart, post_data, log_post_data=True):
        url=f'{self.base_url}/{self.path}/{urlpart}'
        log.info('_post url: {}\n'.format(url))
        if log_post_data:
            log.info('_post data: {}\n'.format(post_data))
        try:
            resp = requests.post(url, headers=self.headers, timeout=7, data=post_data)
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

    def _put(self, urlpart, put_data, log_put_data=True):
        url=f'{self.base_url}/{self.path}/{urlpart}'
        log.info('_put url: {}\n'.format(url))
        if log_put_data:
            log.info('_put data: {}\n'.format(put_data))
        try:
            resp = requests.put(url, headers=self.headers, timeout=7, data=put_data)
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

class Synapse_admin(Http_request):
    def __init__(self, user, token, base_url, admin_path):
        super().__init__(token, base_url, admin_path)
        self.user = user

    def user_list(self, _from, _limit, _guests, _deactivated,
          _name, _user_id):
        urlpart = f'v2/users?from={_from}&limit={_limit}'
        # optional filters
        if _guests == False:
            urlpart+= f'&guests=false' # true is API default
        elif _guests == True:
            urlpart+= f'&guests=true'
        # no else - fall back to API default if None, which is "true"

        # only add when present, deactivated=false will never be added
        if _deactivated:
            urlpart+= f'&deactivated=true' # false is API default

        # either of both is added, never both, Click MutEx prevents it
        if _name:
            urlpart+= f'&name={_name}'
        if _user_id:
            urlpart+= f'&user_id={_user_id}'
        return self._get(urlpart)

    def user_membership(self, user_id):
        urlpart = f'v1/users/{user_id}/joined_rooms'
        return self._get(urlpart)

    def user_deactivate(self, user_id, gdpr_erase):
        urlpart = f'v1/deactivate/{user_id}'
        data = '{"erase": true}' if gdpr_erase else {}
        return self._post(urlpart, data)

    def user_password(self, user_id, password, no_logout):
        urlpart = f'v1/reset_password/{user_id}'
        data = {"new_password": password}
        if no_logout:
            data.update({"logout_devices": no_logout})
        json_data = json.dumps(data)
        return self._post(urlpart, json_data, log_post_data=False)

    def user_details(self, user_id): # called "Query User Account" in API docs.
        urlpart = f'v2/users/{user_id}'
        return self._get(urlpart)

    def user_modify(self, user_id, password, display_name, threepid, avatar_url,
          admin, deactivation):
        'threepid is a tuple in a tuple'
        urlpart = f'v2/users/{user_id}'
        data = {}
        if password:
            data.update({"password": password})
        if display_name:
            data.update({"displayname": display_name})
        if threepid:
            threep_list = [
                {'medium': k, 'address': i} for k,i in dict(threepid).items()
            ]
            data.update({'threepids': threep_list})
        if avatar_url:
            data.update({"avatar_url": avatar_url})
        if admin:
            data.update({"admin": admin})
        if deactivation == 'deactivate':
            data.update({"deactivated": True})
        if deactivation == 'activate':
            data.update({"deactivated": False})
        json_data = json.dumps(data)
        return self._put(urlpart, json_data, log_put_data=False)

    def room_list(self, _from, limit, name, order_by, reverse):
        urlpart = f'v1/rooms?from={_from}&limit={limit}'
        if name:
            urlpart+= f'&search_term={name}'
        if order_by:
            urlpart+= f'&order_by={order_by}'
        if reverse:
            urlpart+= f'&dir=b'
        return self._get(urlpart)

    def room_details(self, room_id):
        urlpart = f'v1/rooms/{room_id}'
        return self._get(urlpart)

    def room_members(self, room_id):
        urlpart = f'v1/rooms/{room_id}/members'
        return self._get(urlpart)

    def room_delete(self, room_id, new_room_user_id, room_name, message,
          block, no_purge):
        urlpart = f'v1/rooms/{room_id}/delete'
        purge = False if no_purge else True
        data = {
            "block": block, # data with proper defaults from cli
            "purge": purge  # should go here
        }
        # everything else is optional and shouldn't even exist in post body
        if new_room_user_id:
            data.update({"new_room_user_id": new_room_user_id})
        if room_name:
            data.update({"room_name": room_name})
        if message:
            data.update({"message": message})
        json_data = json.dumps(data)
        return self._post(urlpart, json_data)

    def version(self):
        urlpart = f'v1/server_version'
        return self._get(urlpart)

class Matrix_client(Http_request):
    def __init__(self, user, token, base_url, client_path):
        super().__init__(token, base_url, client_path)
        self.user = user

    def user_login(self, user_id, password):
        urlpart = f'r0/login/{user_id}'
        data = {"password": password,
                "type": "m.login.password",
                "user": f"{user_id}"}
        json_data = json.dumps(data)
        return self._post(urlpart, json_data, log_post_data=False)

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

def get_table(data, listify=False):
    '''expects lists of dicts, fetches header information from first list element
       and saves as a dict (tabulate expects headers arg as dict)
       then uses tabulate to return a pretty printed tables. The listify argument is used
       to wrap very simple "one-dimensional" API responses into a list so tabulate accepts it.'''

    data_list = []
    if listify == False:
        data_list = data
        log.debug('get_table using data as is. Got this: {}'.format(data_list))
    else:
        data_list.append(data)
        log.debug('get_table listified data. Now looks like this: {}'.format(data_list))

    headers_dict = {}
    for header in data_list[0]:
        headers_dict.update({header: header})
    return tabulate(data_list, tablefmt="simple",
          headers=headers_dict)

class Config(object):
    def __init__(self, config_yaml):
        self.config_yaml = os.path.expanduser(config_yaml)
        self.incomplete = False # save whether reconfiguration is necessary
        self.empty = False # save whether synadm.yaml was just created and is empty
        try:
            conf = self._read_yaml(self.config_yaml)
            log.debug("Successfully read configuration from {}".format(
                  self.config_yaml))
        except IOError:
            log.debug('Creating empty configuration file.')
            Path(self.config_yaml).touch()
            conf = self._read_yaml(self.config_yaml)

        self.user = self._get_config_entry(conf, 'user')
        self.token = self._get_config_entry(conf, 'token', hide_log=True)
        self.base_url = self._get_config_entry(conf, 'base_url')
        self.admin_path = self._get_config_entry(conf, 'admin_api_path')
        self.view = self._get_config_entry(conf, 'view')

    def _get_config_entry(self, conf_dict, yaml_key, hide_log=False):
        value = ''
        try:
            if conf_dict[yaml_key] == '': # Type- or KeyError would raise here
                log.warning(f'Empty entry in configuration file: "{yaml_key}"')
                self.incomplete = True
            else:
                value = conf_dict[yaml_key]
                log_value = 'SECRET' if hide_log else value
                log.debug(f'Configuration entry "{yaml_key}": {log_value}')
        except KeyError:
            log.warning(f'Missing entry in configuration file: "{yaml_key}"')
            self.incomplete = True
        except TypeError:
            log.debug(f"Can't fetch value from empty configuration file.")
            self.incomplete = True
            self.empty = True
        return value

    def write(self, config_values):
        click.echo('Writing configuration to {}'.format(
              self.config_yaml))
        self._write_yaml(config_values)
        click.echo('Done.')

    def _read_yaml(self, yamlfile):
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

    def _write_yaml(self, data):
        """data expects dict, self.config_yaml expects path/file"""
        try:
            with open(self.config_yaml, "w") as fconfig_yaml:
                yaml.dump(data, fconfig_yaml, default_flow_style=False,
                                 allow_unicode=True)
                return True
        except IOError as errio:
            log.error("IOError: could not write file %s \n\n", self.config_yaml)
            raise errio
        except Exception as err:
            log.error(" trying to write %s \n\n", self.config_yaml)
            raise err
            raise SystemExit(2)



# handle logging and configuration prerequisites
log = logger_init()
create_config_dir()
# change default help options
cont_set = dict(help_option_names=['-h', '--help'])
#usage: @click.command(context_settings=cont_set)

#############################################
### main synadm command group starts here ###
#############################################
@click.group(invoke_without_command=False, context_settings=cont_set)
@click.option('--verbose', '-v', count=True, default=False,
      help="enable INFO (-v) or DEBUG (-vv) logging on console")
@click.option('--raw', '-r', is_flag=True, default=False,
      help="print raw json data (overrides default setting)")
@click.option('--table', '-t', is_flag=True, default=False,
      help="print tables (overrides default setting)")
@click.option('--config-file', '-c', type=click.Path(), default='~/.config/synadm.yaml',
      help="configuration file path", show_default=True)
@click.pass_context
def synadm(ctx, verbose, raw, table, config_file):
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

    configuration = Config(config_file)

    if raw and table:
        view = configuration.view
    elif raw:
        view = 'raw'
    elif table:
        view = 'table'
    else:
        view = configuration.view

    ctx.obj = {'config': configuration, 'view': view }
    log.debug("ctx.obj: {}\n".format(ctx.obj))

    if configuration.incomplete:
        _eventually_run_config()


### the config command starts here ###
@synadm.command(context_settings=cont_set)
@click.option('--user', '-u', type=str, default='admin',
    help="admin user for accessing the Synapse admin API's",)
@click.option('--token', '-t', type=str,
    help="admin user's access token for the Synapse admin API's",)
@click.option('--base-url', '-b', type=str, default='http://localhost:8008',
    help="""the base URL Synapse is running on. Typically this is
    https://localhost:8008 or https://localhost:8448. If Synapse is
    configured to expose its admin API's to the outside world it could also be
    https://example.org:8448""", show_default=True)
@click.option('--admin-api-path', '-p', type=str, default='/_synapse/admin',
    help="""the path Synapse provides its admin API's, usually the default is
    alright for most installations.""", show_default=True)
@click.option('--view', type=click.Choice(['table', 'raw']), default='raw',
    help="""how should synadm display data by default? 'table' gives a
    tabular view but needs your terminal to be quite width. 'raw' shows
    formatted json exactely as the API responded. Note that this can always
    be overridden by using global switches -r and -t (eg 'synadm -r user
    list')""", show_default=True)
@click.pass_context
def config(ctx, user, token, base_url, admin_api_path, view):
    """modify synadm's configuration. configuration details are asked
    interactively but can also be provided using command line options."""
    click.echo('Running configurator...')
    cfg = ctx.obj['config']
    # get defaults for prompts from either config file or commandline
    user_default = cfg.user if cfg.user else user
    token_default = cfg.token if cfg.token else token
    base_url_default = cfg.base_url if cfg.base_url else base_url
    admin_path_default = cfg.admin_path if cfg.admin_path else admin_api_path
    view_default = cfg.view if cfg.view else view
    # prompts
    api_user = click.prompt("Synapse admin user name", default=user_default)
    api_token = click.prompt("Synapse admin user token", default=token_default)
    api_base_url = click.prompt("Synapse base URL", default=base_url_default)
    api_admin_path = click.prompt("Synapse admin API path", default=admin_path_default)
    api_view = click.prompt("How should data be viewed by default?",
           default=view_default, type=click.Choice(['table', 'raw']))

    conf_dict = {"user": api_user, "token": api_token, "base_url": api_base_url,
          "admin_api_path": api_admin_path, "view": api_view}
    cfg.write(conf_dict)


### the version command starts here ###
@synadm.command(context_settings=cont_set)
@click.pass_context
def version(ctx):
    synadm = Synapse_admin(ctx.obj['config'].user, ctx.obj['config'].token,
          ctx.obj['config'].base_url, ctx.obj['config'].admin_path)

    version = synadm.version()
    if version == None:
        click.echo("Version could not be fetched.")
        raise SystemExit(1)

    if ctx.obj['view'] == 'raw':
        pprint(version)
    else:
        click.echo("Synapse version: {}".format(version['server_version']))
        click.echo("Python version: {}".format(version['python_version']))




#######################################
### user commands group starts here ###
#######################################
@synadm.group(context_settings=cont_set)
@click.pass_context
def user(ctx):
    """list, add, modify, deactivate/erase users,
       reset passwords.
    """


#### user commands start here ###
@user.command(name='list', context_settings=cont_set)
@click.option('--from', '-f', 'from_', type=int, default=0, show_default=True,
      help='''offset user listing by given number. This option is also used for
      pagination.''')
@click.option('--limit', '-l', type=int, default=100, show_default=True,
      help="limit user listing to given number")
@click.option('--guests/--no-guests', '-g/-G', default=None, show_default=True,
      help="show guest users.")
@click.option('--deactivated', '-d', is_flag=True, default=False,
      help="also show deactivated/erased users", show_default=True)
@optgroup.group('Search options', cls=MutuallyExclusiveOptionGroup,
                help='')
@optgroup.option('--name', '-n', type=str,
      help='''search users by name - filters to only return users with user ID
      localparts or displaynames that contain this value (localpart is the left
      part before the colon of the matrix ID (@user:server)''')
@optgroup.option('--user-id', '-i', type=str,
      help='''search users by ID - filters to only return users with Matrix IDs
      (@user:server) that contain this value''')
@click.pass_context
def list_user_cmd(ctx, from_, limit, guests, deactivated, name, user_id):
    log.info(f'user list options: {ctx.params}\n')
    synadm = Synapse_admin(ctx.obj['config'].user, ctx.obj['config'].token,
          ctx.obj['config'].base_url, ctx.obj['config'].admin_path)
    users = synadm.user_list(from_, limit, guests, deactivated, name, user_id)
    if users == None:
        click.echo("Users could not be fetched.")
        raise SystemExit(1)

    if ctx.obj['view'] == 'raw':
        pprint(users)
    else:
        click.echo(
              "\nTotal users on homeserver (excluding deactivated): {}\n".format(
              users['total']))
        if int(users['total']) != 0:
            tab_users = get_table(users['users'])
            click.echo(tab_users)
        if 'next_token' in users:
            m_n ="\nThere is more users than shown, use '--from {}' ".format(
                  users['next_token'])
            m_n+="to go to next page.\n"
            click.echo(m_n)


@user.command(context_settings=cont_set)
@click.argument('user_id', type=str)
      #help='the matrix user ID to deactivate/erase (user:server')
@click.option('--gdpr-erase', '-e', is_flag=True, default=False,
      help="""marks the user as GDPR-erased. This means messages sent by the
      user will still be visible by anyone that was in the room when these
      messages were sent, but hidden from users joining the room
      afterwards.""", show_default=True)
@click.pass_context
def deactivate(ctx, user_id, gdpr_erase):
    """deactivate or gdpr-erase a user. Provide matrix user ID (@user:server)
    as argument. It removes active access tokens, resets the password, and
    deletes third-party IDs (to prevent the user requesting a password
    reset).
    """
    log.info(f'user deactivate options: {ctx.params}\n')
    synadm = Synapse_admin(ctx.obj['config'].user, ctx.obj['config'].token,
          ctx.obj['config'].base_url, ctx.obj['config'].admin_path)

    #ctx.invoke(query, user_id=user_id) # FIXME implement user query cmd
    m_kick = '\nNote that deactivating/gdpr-erasing a user leads to the following:\n'
    m_kick+= '  - Removal from all joined rooms\n'
    m_kick+= '  - Removal of all active access tokens\n'
    m_kick+= '  - Password reset\n'
    m_kick+= '  - Deletion of third-party-IDs (to prevent the user requesting '
    m_kick+= 'a password)\n' if ctx.obj['view'] == 'raw' else 'a password)'
    click.echo(m_kick)
    ctx.invoke(user_details_cmd, user_id=user_id)
    ctx.invoke(membership, user_id=user_id)
    m_erase_or_deact = '"gdpr-erase"' if gdpr_erase else 'deactivate'
    m_erase_or_deact_p = '"gdpr-erased"' if gdpr_erase else 'deactivated'
    sure = click.prompt("\nAre you sure you want to {} this user? (y/N)".format(
          m_erase_or_deact), type=bool, default=False, show_default=False)
    if sure:
        deactivated = synadm.user_deactivate(user_id, gdpr_erase)
        if deactivated == None:
            click.echo("User could not be {}.".format(m_erase_or_deact))
            raise SystemExit(1)

        if ctx.obj['view'] == 'raw':
            pprint(deactivated)
        else:
            if deactivated['id_server_unbind_result'] == 'success':
                click.echo('User successfully {}.'.format(m_erase_or_deact_p))
            else:
                click.echo('Synapse returned: {}'.format(
                      deactivated['id_server_unbind_result']))
    else:
        click.echo('Abort.')


@user.command(context_settings=cont_set)
@click.argument('user_id', type=str)
@click.option('--no-logout', '-n', is_flag=True, default=False,
      help="don't log user out of all sessions on all devices.")
@click.option('--password', '-p', prompt=True, hide_input=True,
              confirmation_prompt=True, help="new password")
@click.pass_context
def password(ctx, user_id, password, no_logout):
    """change a user's password. To prevent the user from being logged out of all
       sessions use option -n
    """
    m='user password options: user_id: {}, password: secrect, no_logout: {}'.format(
            ctx.params['user_id'], ctx.params['no_logout'])
    log.info(m)
    synadm = Synapse_admin(ctx.obj['config'].user, ctx.obj['config'].token,
          ctx.obj['config'].base_url, ctx.obj['config'].admin_path)
    changed = synadm.user_password(user_id, password, no_logout)
    if changed == None:
        click.echo("Password could not be reset.")
        raise SystemExit(1)

    if ctx.obj['view'] == 'raw':
        pprint(changed)
    else:
        if changed == {}:
            click.echo('Password reset successfully.')
        else:
            click.echo('Synapse returned: {}'.format(changed))


@user.command(context_settings=cont_set)
@click.argument('user_id', type=str)
@click.pass_context
def membership(ctx, user_id):
    '''list all rooms a user is member of. Provide matrix user ID (@user:server) as argument.'''
    log.info(f'user membership options: {ctx.params}\n')
    synadm = Synapse_admin(ctx.obj['config'].user, ctx.obj['config'].token,
          ctx.obj['config'].base_url, ctx.obj['config'].admin_path)
    joined_rooms = synadm.user_membership(user_id)
    if joined_rooms == None:
        click.echo("Membership could not be fetched.")
        raise SystemExit(1)

    if ctx.obj['view'] == 'raw':
        pprint(joined_rooms)
    else:
        click.echo(
              "\nUser is member of {} rooms.\n".format(
              joined_rooms['total']))
        if int(joined_rooms['total']) != 0:
            # joined_rooms is just a list, we don't need get_table() tabulate wrapper
            # (it's for key-value json data aka dicts). Just simply print the list:
            for room in joined_rooms['joined_rooms']:
                click.echo(room)

                
@user.command(name='search', context_settings=cont_set)
@click.pass_context
@click.argument('search-term', type=str)
@click.option('--from', '-f', 'from_', type=int, default=0, show_default=True,
      help='''offset user listing by given number. This option is also used
      for pagination.''')
@click.option('--limit', '-l', type=int, default=100, show_default=True,
      help='maximum amount of users to return.')
def user_search_cmd(ctx, search_term, from_, limit):
    '''a simplified shortcut to \'synadm user list -d -g -n <search-term>\'
    (Searches for users by name/matrix-ID, including deactivated users
    as well as guest users). Also it executes a case-insensitive search
    compared to the original command.'''
    if search_term[0].isupper():
        search_term_cap = search_term
        search_term_nocap = search_term[0].lower() + search_term[1:]
    else:
        search_term_cap = search_term[0].upper() + search_term[1:]
        search_term_nocap = search_term

    click.echo("\nUser search results for '{}':\n".format(search_term_nocap))
    ctx.invoke(list_user_cmd, from_=from_, limit=limit, name=search_term_nocap,
          deactivated=True, guests=True)
    click.echo("\nUser search results for '{}':\n".format(search_term_cap))
    ctx.invoke(list_user_cmd, from_=from_, limit=limit, name=search_term_cap,
          deactivated=True, guests=True)


@user.command(name='details', context_settings=cont_set)
@click.pass_context
@click.argument('user_id', type=str)
def user_details_cmd(ctx, user_id):
    '''view details of a user account.'''
    log.info(f'user details options: {ctx.params}\n')
    synadm = Synapse_admin(ctx.obj['config'].user, ctx.obj['config'].token,
          ctx.obj['config'].base_url, ctx.obj['config'].admin_path)
    user = synadm.user_details(user_id)
    if user == None:
        click.echo('User details could not be fetched.')
        raise SystemExit(1)

    if ctx.obj['view'] == 'raw':
        pprint(user)
    else:
        tab_user = get_table(user, listify=True)
        click.echo(tab_user)


#user_detail = RequiredAnyOptionGroup('At least one of the following options is required', help='', hidden=False)
user_detail = RequiredAnyOptionGroup('', help='', hidden=False)

@user.command(context_settings=cont_set)
@click.pass_context
@click.argument('user_id', type=str)
@user_detail.option('--password-prompt', '-p', is_flag=True,
      help="set password interactively.")
@user_detail.option('--password', '-P', type=str,
      help="set password on command line.")
@user_detail.option('--display-name', '-n', type=str,
      help='''set display name. defaults to the value of user_id''')
@user_detail.option('--threepid', '-t', type=str, multiple=True, nargs=2,
      help='''add a third-party identifier. This can be an email address or a
      phone number. Threepids are used for several things: For use when
      logging in, as an alternative to the user id. In the case of email, as
      an alternative contact to help with account recovery, as well as
      to receive notifications of missed messages. Format: medium
      value (eg. --threepid email <user@example.org>). This option can also
      be stated multiple times, i.e. a user can have multiple threepids
      configured.''')
@user_detail.option('--avatar-url', '-v', type=str,
      help='''set avatar URL. Must be a MXC URI
      (https://matrix.org/docs/spec/client_server/r0.6.0#matrix-content-mxc-uris).''')
@user_detail.option('--admin/--no-admin', '-a/-u', default=None,
      help='''grant user admin permission. Eg user is allowed to use the admin
      API''', show_default=True,)
@user_detail.option('--activate', 'deactivation', flag_value='activate',
      help='''re-activate user.''')
@user_detail.option('--deactivate', 'deactivation', flag_value='deactivate',
      help='''deactivate user. Use with caution! Deactivating a user
      removes their active access tokens, resets their password, kicks them out
      of all rooms and deletes third-party identifiers (to prevent the user
      requesting a password reset). See also "user deactivate" command.''')
def modify(ctx, user_id, password, password_prompt, display_name, threepid,
      avatar_url, admin, deactivation):
    '''create or modify a local user. Provide matrix user ID (@user:server)
    as argument.'''
    synadm = Synapse_admin(ctx.obj['config'].user, ctx.obj['config'].token,
          ctx.obj['config'].base_url, ctx.obj['config'].admin_path)
    #log.info(f'user modify options: {ctx.params}\n')

    # sanity checks that can't easily be handled by Click.
    if password_prompt and password:
        log.error('Use either "-p" or "-P secret", not both.')
        raise SystemExit(1)
    if deactivation == 'activate' and not (password_prompt or password):
        m_act = 'Need to set password when activating a user. Add either "-p" '
        m_act+= 'or "-P secret" to your command.'
        log.error(m_act)
        raise SystemExit(1)
    if deactivation == 'deactivate' and (password_prompt or password):
        m_act = "Deactivating a user and setting a password doesn't make sense."
        log.error(m_act)
        raise SystemExit(1)

    click.echo('Current user account settings:')
    ctx.invoke(user_details_cmd, user_id=user_id)
    click.echo()
    click.echo('User account settings after modification:')
    for key,value in ctx.params.items():
        if key in ['user_id', 'password', 'password_prompt']: # skip these
            continue
        elif key == 'threepid':
            if value != ():
                for t_key, t_val in value:
                    click.echo(f'{key}: {t_key} {t_val}')
                    if t_key not in ['email', 'msisdn']:
                        m_m =f'{t_key} is probably not a supported medium type. '
                        m_m+='Are you sure you want to add it?. Supported medium '
                        m_m+='types according to the current matrix spec are: '
                        m_m+='email, msisdn'
                        log.warning(m_m)
        elif value not in [None, {}, []]: # only show non-empty (aka changed)
            click.echo(f'{key}: {value}')

    if password_prompt:
        pw = click.prompt('Password', hide_input=True, confirmation_prompt=True)
    elif password:
        click.echo('Password will be set as provided on command line')
        pw = password
    else:
        pw = None

    sure = click.prompt("\nAre you sure you want to modify user? (y/N)",
          type=bool, default=False, show_default=False)
    if sure:
        modified = synadm.user_modify(user_id, pw, display_name, threepid,
              avatar_url, admin, deactivation)

        if modified == None:
            click.echo("User could not be modified.")
            raise SystemExit(1)

        if ctx.obj['view'] == 'raw':
            pprint(modified)
        else:
            if modified != {}:
                tab_mod = get_table(modified, listify=True)
                click.echo(tab_mod)
                click.echo('User successfully modified.')
            else:
                click.echo('Synapse returned: {}'.format(
                      modified))
    else:
        click.echo('Abort.')



#######################################
### room commands group starts here ###
#######################################
@synadm.group(context_settings=cont_set)
def room():
    """list/delete rooms, show/invite/join members, ...
    """


### room commands start here ###
@room.command(name='list', context_settings=cont_set)
@click.pass_context
@click.option('--from', '-f', 'from_', type=int, default=0, show_default=True,
      help="""offset room listing by given number. This option is also used
      for pagination.""")
@click.option('--limit', '-l', type=int, default=100, show_default=True,
      help="Maximum amount of rooms to return.")
@click.option('--name', '-n', type=str,
      help="""Filter rooms by their room name. Search term can be contained in
      any part of the room name)""")
@click.option('--order-by', '-o', type=click.Choice(['name', 'canonical_alias',
      'joined_members', 'joined_local_members', 'version', 'creator',
      'encryption', 'federatable', 'public', 'join_rules', 'guest_access',
      'history_visibility', 'state_events']),
      help="The method in which to sort the returned list of rooms.")
@click.option('--reverse', '-r', is_flag=True, default=False,
      help="""Direction of room order. If set it will reverse the sort order of
      --order-by method.""")
def list_room_cmd(ctx, from_, limit, name, order_by, reverse):
    synadm = Synapse_admin(ctx.obj['config'].user, ctx.obj['config'].token,
          ctx.obj['config'].base_url, ctx.obj['config'].admin_path)
    rooms = synadm.room_list(from_, limit, name, order_by, reverse)
    if rooms == None:
        click.echo("Rooms could not be fetched.")
        raise SystemExit(1)

    if ctx.obj['view'] == 'raw':
        pprint(rooms)
    else:
        if int(rooms['total_rooms']) != 0:
            tab_rooms = get_table(rooms['rooms'])
            click.echo(tab_rooms)
        if 'next_batch' in rooms:
            m_n = "\nThere is more rooms than shown, use '--from {}' ".format(
                  rooms['next_batch'])
            m_n+="to go to next page.\n"
            click.echo(m_n)


@room.command(context_settings=cont_set)
@click.argument('room_id', type=str)
@click.pass_context
def details(ctx, room_id):
    synadm = Synapse_admin(ctx.obj['config'].user, ctx.obj['config'].token,
          ctx.obj['config'].base_url, ctx.obj['config'].admin_path)
    room = synadm.room_details(room_id)
    if room == None:
        click.echo("Room details could not be fetched.")
        raise SystemExit(1)

    if ctx.obj['view'] == 'raw':
        pprint(room)
    else:
        if room != {}:
            tab_room = get_table(room, listify=True)
            click.echo(tab_room)


@room.command(context_settings=cont_set)
@click.argument('room_id', type=str)
@click.pass_context
def members(ctx, room_id):
    synadm = Synapse_admin(ctx.obj['config'].user, ctx.obj['config'].token,
          ctx.obj['config'].base_url, ctx.obj['config'].admin_path)
    members = synadm.room_members(room_id)
    if members == None:
        click.echo("Room members could not be fetched.")
        raise SystemExit(1)

    if ctx.obj['view'] == 'raw':
        pprint(members)
    else:
        click.echo(
              "\nTotal members in room: {}\n".format(
              members['total']))
        if int(members['total']) != 0:
            for member in members['members']:
                click.echo(member)


@room.command(context_settings=cont_set)
@click.pass_context
@click.argument('room_id', type=str)
@click.option('--new-room-user-id', '-u', type=str,
      help='''If set, a new room will be created with this user ID as the
      creator and admin, and all users in the old room will be moved into
      that room. If not set, no new room will be created and the users will
      just be removed from the old room. The user ID must be on the local
      server, but does not necessarily have to belong to a registered
      user.''')
@click.option('--room-name', '-n', type=str,
       help='''A string representing the name of the room that new users will
       be invited to. Defaults to "Content Violation Notification"''')
@click.option('--message', '-m', type=str,
      help='''A string containing the first message that will be sent as
      new_room_user_id in the new room. Ideally this will clearly convey why
      the original room was shut down. Defaults to "Sharing illegal content
      on this server is not permitted and rooms in violation will be
      blocked."''')
@click.option('--block', '-b', is_flag=True, default=False, show_default=True,
      help='''If set, this room will be added to a blocking list,
      preventing future attempts to join the room''')
@click.option('--no-purge', is_flag=True, default=False, show_default=True,
      help='''Prevent removing of all traces of the room from your
      database.''')
def delete(ctx, room_id, new_room_user_id, room_name, message, block, no_purge):
    synadm = Synapse_admin(ctx.obj['config'].user, ctx.obj['config'].token,
          ctx.obj['config'].base_url, ctx.obj['config'].admin_path)

    ctx.invoke(details, room_id=room_id)
    ctx.invoke(members, room_id=room_id)

    sure = click.prompt("\nAre you sure you want to delete this room? (y/N)",
          type=bool, default=False, show_default=False)
    if sure:
        room_del = synadm.room_delete(room_id, new_room_user_id, room_name,
              message, block, no_purge)
        if room_del == None:
            click.echo("Room not deleted.")
            raise SystemExit(1)

        if ctx.obj['view'] == 'raw':
            pprint(room_del)
        else:
            if room_del != {}:
                tab_room = get_table(room_del, listify=True)
                click.echo(tab_room)
    else:
        click.echo('Abort.')


@room.command(name='search', context_settings=cont_set)
@click.pass_context
@click.argument('search-term', type=str)
@click.option('--from', '-f', 'from_', type=int, default=0, show_default=True,
      help='''offset room listing by given number. This option is also used
      for pagination.''')
@click.option('--limit', '-l', type=int, default=100, show_default=True,
      help='Maximum amount of rooms to return.')
def search_room_cmd(ctx, search_term, from_, limit):
    '''a simplified shortcut to \'synadm room list -n <search-term>\'. Also
    it executes a case-insensitive search compared to the original
    command.'''
    if search_term[0].isupper():
        search_term_cap = search_term
        search_term_nocap = search_term[0].lower() + search_term[1:]
    else:
        search_term_cap = search_term[0].upper() + search_term[1:]
        search_term_nocap = search_term

    click.echo("\nRoom search results for '{}':\n".format(search_term_nocap))
    ctx.invoke(list_room_cmd, from_=from_, limit=limit, name=search_term_nocap)
    click.echo("\nRoom search results for '{}':\n".format(search_term_cap))
    ctx.invoke(list_room_cmd, from_=from_, limit=limit, name=search_term_cap)



if __name__ == '__main__':
    synadm(obj={})
