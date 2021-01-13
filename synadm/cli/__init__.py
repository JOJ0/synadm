""" CLI base functions and settings
"""

import os
import sys
import logging
import pprint
import json
import click
import yaml
import tabulate

from synadm import api


def humanize(data):
    """ Try to display data in a human-readable form:
    - lists of dicts are displayed as tables
    - dicts are displayed as pivoted tables
    - lists are displayed as a simple list
    """
    if isinstance(data, list) and isinstance(data[0], dict):
        headers = {header: header for header in data[0]}
        return tabulate.tabulate(data, tablefmt="simple", headers=headers)
    if isinstance(data, list):
        return "\n".join(data)
    if isinstance(data, dict):
        return tabulate.tabulate(data.items(), tablefmt="simple")
    return None


class APIHelper:
    """ API client enriched with CLI-level functions, used as a proxy to the
    client object
    """

    FORMATTERS = {
        "pprint": pprint.pformat,
        "json": json.dumps,
        "yaml": yaml.dump,
        "human": humanize
    }

    CONFIG = {
        "user": "",
        "token": "",
        "base_url": "http://localhost:8008",
        "admin_path": "/_synapse/admin",
    }

    def __init__(self, config_path, verbose, batch, output_format):
        self.config = APIHelper.CONFIG.copy()
        self.config_path = os.path.expanduser(config_path)
        self.batch = batch
        self.api = None
        self.init_logger(verbose)
        for name, formatter in APIHelper.FORMATTERS.items():
            self.output_format = name
            self.formatter = formatter
            if name.startswith(output_format):
                break

    def init_logger(self, verbose):
        """ Log both to console (defaults to INFO) and file (DEBUG)
        """
        log_path = os.path.expanduser("~/.local/share/synadm/debug.log")
        os.makedirs(os.path.dirname(log_path), exist_ok=True)
        log = logging.getLogger("synadm")
        log.setLevel(logging.DEBUG)
        file_handler = logging.FileHandler(log_path, encoding="utf-8")
        file_handler.setLevel(logging.DEBUG)
        console_handler = logging.StreamHandler()
        console_handler.setLevel(
            logging.DEBUG if verbose > 1 else
            logging.INFO if verbose == 1 else
            logging.WARNING
        )
        file_formatter = logging.Formatter(
            "%(asctime)s %(name)-8s %(levelname)-7s %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        console_formatter = logging.Formatter("%(levelname)-5s %(message)s")
        console_handler.setFormatter(console_formatter)
        file_handler.setFormatter(file_formatter)
        log.addHandler(console_handler)
        log.addHandler(file_handler)
        self.log = log

    def load(self):
        """ Load the configuration and initializes the client
        """
        try:
            with open(self.config_path) as handle:
                self.config.update(yaml.load(handle, Loader=yaml.SafeLoader))
            self.log.debug("configuration read: %s", self.config)
        except Exception as error:
            self.log.error("%s while reading configuration file", error)
        for key, value in self.config.items():
            if not value:
                self.log.error("config entry %s missing", key)
                return False
        self.api = api.SynapseAdmin(
            self.log,
            self.config["user"], self.config["token"],
            self.config["base_url"], self.config["admin_path"]
        )
        return True

    def write_config(self, config):
        """ Write a new version of the configuration to file
        """
        try:
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            with open(self.config_path, "w") as handle:
                yaml.dump(config, handle, default_flow_style=False,
                          allow_unicode=True)
        except Exception as error:
            self.log.error("%s trying to write configuration", error)

    def output(self, data):
        """ Output data object using the configured formatter
        """
        click.echo(self.formatter(data))


@click.group(
    invoke_without_command=False,
    context_settings=dict(help_option_names=["-h", "--help"]))
@click.option(
    "--verbose", "-v", count=True, default=False,
    help="enable INFO (-v) or DEBUG (-vv) logging on console")
@click.option(
    "--batch/--no-batch", default=False,
    help="enable batch behavior (no interactive prompts)")
@click.option(
    "--output", "-o", default="yaml",
    type=click.Choice(["yaml", "json", "human", "pprint"]),
    show_choices=True,
    help="""override default output format. Abbreviation is possible
    (eg. '-o pp', '-o h', ...)""")
@click.option(
    "--config-file", "-c", type=click.Path(),
    default="~/.config/synadm.yaml",
    help="configuration file path", show_default=True)
@click.pass_context
def root(ctx, verbose, batch, output, config_file):
    """ Synapse Administration toolkit
    """
    ctx.obj = APIHelper(config_file, verbose, batch, output)
    helper_loaded = ctx.obj.load()
    if ctx.invoked_subcommand != "config" and not helper_loaded:
        if batch:
            click.echo("Please setup synadm: " + sys.argv[0] + " config")
            raise SystemExit(2)
        else:
            ctx.invoke(config_cmd)


@root.command(name="config")
@click.option(
    "--user", "-u", type=str, default="admin",
    help="admin user for accessing the Synapse admin API's",)
@click.option(
    "--token", "-t", type=str,
    help="admin user's access token for the Synapse admin API's",)
@click.option(
    "--base-url", "-b", type=str, default="http://localhost:8008",
    help="""the base URL Synapse is running on. Typically this is
    https://localhost:8008 or https://localhost:8448. If Synapse is
    configured to expose its admin API's to the outside world it could also be
    https://example.org:8448""", show_default=True)
@click.option(
    "--admin-path", "-p", type=str, default="/_synapse/admin",
    help="""the path Synapse provides its admin API's, usually the default is
    alright for most installations.""", show_default=True)
@click.option(
    "--output", type=click.Choice(["yaml", "json", "human", "pprint"]),
    default="yaml",
    help="""how should synadm display data by default? 'human' gives a
    tabular or list view depending on the fetched data. This mode needs your
    terminal to be quite wide! 'json' displays exactely as the API responded.
    'pprint' shows nicely formatted json. 'yaml' is the currently recommended
    output format. It doesn't need as much terminal width as 'human' does.
    Note that the default output format can always be overridden by using
    global switch -o (eg 'synadm -o pprint user list')""", show_default=True)
@click.pass_obj
def config_cmd(helper, user, token, base_url, admin_path, output):
    """ Modify synadm's configuration. configuration details are asked
    interactively but can also be provided using command line options.
    """
    click.echo("Running configurator...")
    helper.write_config({
        "user": click.prompt(
            "Synapse admin user name",
            default=helper.config.get("user", user)),
        "token": click.prompt(
            "Synapse admin user token",
            default=helper.config.get("token", token)),
        "base_url": click.prompt(
            "Synapse base URL",
            default=helper.config.get("base_url", base_url)),
        "admin_path": click.prompt(
            "Synapse admin API path",
            default=helper.config.get("admin_path", admin_path)),
        "format": click.prompt(
            "Default output format",
            default=helper.config.get("format", output),
            type=click.Choice(["yaml", "json", "human", "pprint"]))
    })
    helper.load()


@root.command()
@click.pass_obj
def version(helper):
    """ Get the synapse server version
    """
    version_info = helper.api.version()
    if version_info is None:
        click.echo("Version could not be fetched.")
        raise SystemExit(1)
    helper.output(version_info)


# Import additional commands
from synadm.cli import room, user