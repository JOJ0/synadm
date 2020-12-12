""" CLI base functions and settings
"""

from synadm import api
from pathlib import Path
from tabulate import tabulate

import os
import sys
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


class APIClient:
    """ API client enriched with CLI-level functions
    """

    FORMATTERS = {
        "human": humanize,
        "pprint": pprint.pformat,
        "json": json.dumps,
        "yaml": yaml.dump
    }

    CONFIG = {
        "user": "",
        "token": "",
        "base_url": "",
        "admin_path": "/_synapse/admin",
    }

    def __init__(self, config_path, verbose, format):
        self.config = APIClient.CONFIG.copy()
        self.config_path = os.path.expanduser(config_path)
        self.format = format
        self.log = self.init_logger(verbose)
        self.api = None

    def __getattr__(self, name):
        print(name)
        return getattr(self.api, name)          

    def init_logger(self, verbose):
        log_path = os.path.expanduser("~/.local/share/synadm/debug.log")
        os.makedirs(os.path.dirname(log_path), exist_ok=True)
        log = logging.getLogger('synadm')
        log.setLevel(logging.DEBUG) # level of logger itself
        f_handle = logging.FileHandler(log_path, encoding='utf-8') # create file handler
        f_handle.setLevel(logging.DEBUG) # which logs even debug messages
        c_handle = logging.StreamHandler() # console handler with a higher log level
        c_handle.setLevel(
            logging.DEBUG if verbose > 1 else
            logging.INFO if verbose == 1 else
            logging.WARNING
        )
        # create formatters and add it to the handlers
        f_form = logging.Formatter('%(asctime)s %(name)-8s %(levelname)-7s %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S')
        c_form = logging.Formatter('%(levelname)-5s %(message)s')
        c_handle.setFormatter(c_form)
        f_handle.setFormatter(f_form)
        log.addHandler(c_handle) # add the handlers to logger
        log.addHandler(f_handle)
        return log

    def read_config(self):
        try:
            with open(self.config_path) as handle:
                self.config.update(yaml.load(handle, Loader=yaml.SafeLoader))
            self.log.debug("configuration read: {}".format(self.config))
        except Exception as error:
            self.log.error("{} while reading configuration file".format(error))
        for key, value in self.config.items():
            if not value:
                self.log.error(f"config entry {key} missing")
                return False
        self.api = api.Synapse_admin(
            self.log,
            self.config["user"], self.config["token"],
            self.config["base_url"], self.config["admin_path"]
        )
        return True

    def write_config(self, config):
        try:
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            with open(self.config_path, "w") as handle:
                yaml.dump(config, handle, default_flow_style=False,
                    allow_unicode=True)
        except Exception as error:
            self.log.error("{} trying to write configuration".format(error))

    def output(self, data):
        click.echo(APIClient.FORMATTERS[self.format](data))


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


@click.group(invoke_without_command=False, context_settings=dict(help_option_names=['-h', '--help']))
@click.option('--verbose', '-v', count=True, default=False,
      help="enable INFO (-v) or DEBUG (-vv) logging on console")
@click.option('--output', '-o', default="human",
      help="print raw json data (overrides default setting)")
@click.option('--config-file', '-c', type=click.Path(), default='~/.config/synadm.yaml',
      help="configuration file path", show_default=True)
@click.pass_context
def root(ctx, verbose, output, config_file):
    ctx.obj = APIClient(config_file, verbose, output)
    if ctx.invoked_subcommand != 'config' and not ctx.obj.read_config():
        click.echo("Please setup synadm: " + sys.argv[0] + " config")
        raise SystemExit(2)


@root.command()
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
@click.option('--output', type=click.Choice(['human', 'json', 'yaml', 'pprint']), default='human',
    help="""how should synadm display data by default? 'table' gives a
    tabular view but needs your terminal to be quite width. 'raw' shows
    formatted json exactely as the API responded. Note that this can always
    be overridden by using global switches -r and -t (eg 'synadm -r user
    list')""", show_default=True)
@click.pass_obj
def config(api, user, token, base_url, admin_api_path, output):
    """modify synadm's configuration. configuration details are asked
    interactively but can also be provided using command line options."""
    click.echo('Running configurator...')
    api.write_config({
        "user": click.prompt("Synapse admin user name",
            default=api.config.get("user", user)),
        "token": click.prompt("Synapse admin user token",
            default=api.config.get("token", token)),
        "base_url": click.prompt("Synapse base URL",
            default=api.config.get("base_url", base_url)),
        "admin_api_path": click.prompt("Synapse admin API path",
            default=api.config.get("admin_api_path", admin_api_path)),
        "format": click.prompt("How should data be viewed by default?",
            default=api.config.get("format", output),
            type=click.Choice(['human', 'json', 'yaml', 'pprint']))
    })


@root.command()
@click.pass_obj
def version(api):
    version = api.version()
    if version == None:
        click.echo("Version could not be fetched.")
        raise SystemExit(1)
    api.output(version)
