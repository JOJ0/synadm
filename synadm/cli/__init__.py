""" CLI base functions and settings
"""

from synadm import api
from pathlib import Path
from tabulate import tabulate

import os
import yaml
import click
import logging
import pprint
import json


def humanize(data):
    """ Try to display data in a human-readable form:
    - lists of dicts are displayed as tables
    - dicts are displayed as pivoted tables
    - lists are displayed as a simple list
    """
    if type(data) is list and type(data[0]) is dict:
        headers = {header: header for header in data[0]}
        return tabulate(data, tablefmt="simple", headers=headers)
    elif type(data) is list:
        return "\n".join(data)
    elif type(data) is dict:
        return tabulate(data.items(), tablefmt="simple")


class APIClient(api.Synapse_admin):
    """ API client enriched with CLI-level functions
    """

    FORMATTERS = {
        "human": humanize,
        "pprint": pprint.pformat,
        "json": json.dumps,
        "yaml": yaml.dump
    }

    def __init__(self, config, format="raw"):
        self.config = config
        self.format = format
        super(APIClient, self).__init__(log, config.user, config.token,
            config.base_url, config.admin_path)

    def output(self, data):
        click.echo(APIClient.FORMATTERS[self.format](data))
        


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


# change default help options
#usage: @click.command(context_settings=cont_set)
cont_set = dict(help_option_names=['-h', '--help'])


# handle logging and configuration prerequisites
log = logger_init()


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


@click.group(invoke_without_command=False, context_settings=cont_set)
@click.option('--verbose', '-v', count=True, default=False,
      help="enable INFO (-v) or DEBUG (-vv) logging on console")
@click.option('--output', '-o', default="human",
      help="print raw json data (overrides default setting)")
@click.option('--config-file', '-c', type=click.Path(), default='~/.config/synadm.yaml',
      help="configuration file path", show_default=True)
@click.pass_context
def root(ctx, verbose, output, config_file):
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
    ctx.obj = APIClient(configuration, output)
    log.debug("ctx.obj: {}\n".format(ctx.obj))

    if configuration.incomplete:
        _eventually_run_config()


@root.command(context_settings=cont_set)
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
@click.pass_obj
def config(api, user, token, base_url, admin_api_path, view):
    """modify synadm's configuration. configuration details are asked
    interactively but can also be provided using command line options."""
    click.echo('Running configurator...')
    cfg = api.config
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


@root.command(context_settings=cont_set)
@click.pass_obj
def version(api):
    version = api.version()
    if version == None:
        click.echo("Version could not be fetched.")
        raise SystemExit(1)
    api.output(version)
