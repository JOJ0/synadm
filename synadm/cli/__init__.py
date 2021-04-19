# -*- coding: utf-8 -*-
# synadm
# Copyright (C) 2020-2021 Johannes Tiefenbacher
#
# synadm is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# synadm is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

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
        "matrix_path": "/_matrix/",
        "timeout": 7
    }

    def __init__(self, config_path, verbose, batch, output_format_cli):
        self.config = APIHelper.CONFIG.copy()
        self.config_path = os.path.expanduser(config_path)
        self.batch = batch
        self.api = None
        self.init_logger(verbose)
        self.requests_debug = False
        if verbose >= 3:
            self.requests_debug = True
        self.output_format_cli = output_format_cli  # override from cli

    def init_logger(self, verbose):
        """ Log both to console (defaults to WARNING) and file (DEBUG)
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

    def _set_formatter(self, _output_format):
        for name, formatter in APIHelper.FORMATTERS.items():
            if name.startswith(_output_format):
                self.output_format = name
                self.formatter = formatter
                break
        self.log.debug("Formatter in use: %s - %s", self.output_format,
                       self.formatter)
        return True

    def load(self):
        """ Load the configuration and initialize the client
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
        if self.output_format_cli:  # we have a cli output format override
            self._set_formatter(self.output_format_cli)
        else:  # we use the configured default output format
            self._set_formatter(self.config["format"])
        self.api = api.SynapseAdmin(
            self.log,
            self.config["user"], self.config["token"],
            self.config["base_url"], self.config["admin_path"],
            self.config["timeout"], self.requests_debug
        )
        self.matrix_api = api.Matrix(
            self.log,
            self.config["user"], self.config["token"],
            self.config["base_url"], self.config["matrix_path"],
            self.config["timeout"], self.requests_debug
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
            if os.name == "posix":
                click.echo("Restricting access to config file to user only")
                os.chmod(self.config_path, 0o600)
            else:
                click.echo(
                    f"Unsupported OS, please adjust permissions of {self.config_path} manually"
                )

            return True
        except Exception as error:
            self.log.error("%s trying to write configuration", error)
            return False

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
    "--output", "-o", default="",
    type=click.Choice(["yaml", "json", "human", "pprint",
                       "y", "j", "h", "p", ""]),
    show_choices=True,
    help="""override default output format.""")
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
    "--user", "-u", type=str,
    help="admin user for accessing the Synapse admin API's")
@click.option(
    "--token", "-t", type=str,
    help="admin user's access token for the Synapse admin API's")
@click.option(
    "--base-url", "-b", type=str,
    help="""the base URL Synapse is running on. Typically this is
    https://localhost:8008 or https://localhost:8448. If Synapse is
    configured to expose its admin API's to the outside world it might as
    well be something like this: https://example.org:8448""")
@click.option(
    "--admin-path", "-p", type=str,
    help="""the path Synapse provides its admin API's, usually the default is
    alright for most installations.""")
@click.option(
    "--matrix-path", "-m", type=str,
    help="""the path Synapse provides the Matrix client API's, usually the
    default is alright for most installations.""")
@click.option(
    "--timeout", "-w", type=int,
    help="""the timeout for http queries to admin API's or Matrix Client
    API's. The default is 7 seconds. """)
@click.option(
    "--output", "-o", type=click.Choice(["yaml", "json", "human", "pprint"]),
    help="""how should synadm display data by default? 'human' gives a
    tabular or list view depending on the fetched data. This mode needs your
    terminal to be quite wide! 'json' displays exactely as the API responded.
    'pprint' shows nicely formatted json. 'yaml' is the currently recommended
    output format. It doesn't need as much terminal width as 'human' does.
    Note that the default output format can always be overridden by using
    global switch -o (eg 'synadm -o pprint user list').""")
@click.pass_obj
def config_cmd(helper, user, token, base_url, admin_path, matrix_path,
               output, timeout):
    """ Modify synadm's configuration. Configuration details are generally
    always asked interactively. Command line options override the suggested
    defaults in the prompts.
    """

    if helper.batch:
        if not all([user, token, base_url, admin_path, matrix_path,
                    output, timeout]):
            click.echo(
                "Missing config options for batch configuration!"
            )
            raise SystemExit(3)
        else:
            click.echo("Saving to config file.")
            if helper.write_config({
                "user": user,
                "token": token,
                "base_url": base_url,
                "admin_path": admin_path,
                "matrix_path": matrix_path,
                "format": output,
                "timeout": timeout
            }):
                raise SystemExit(0)
            else:
                raise SystemExit(4)

    click.echo("Running configurator...")
    helper.write_config({
        "user": click.prompt(
            "Synapse admin user name",
            default=user if user else helper.config.get("user", user)),
        "token": click.prompt(
            "Synapse admin user token",
            default=token if token else helper.config.get("token", token)),
        "base_url": click.prompt(
            "Synapse base URL",
            default=base_url if base_url else helper.config.get(
                "base_url", base_url)),
        "admin_path": click.prompt(
            "Synapse admin API path",
            default=admin_path if admin_path else helper.config.get(
                "admin_path", admin_path)),
        "matrix_path": click.prompt(
            "Matrix client API path",
            default=matrix_path if matrix_path else helper.config.get(
                "matrix_path", matrix_path)),
        "format": click.prompt(
            "Default output format",
            default=output if output else helper.config.get("format", output),
            type=click.Choice(["yaml", "json", "human", "pprint"])),
        "timeout": click.prompt(
            "Default http timeout",
            default=timeout if timeout else helper.config.get(
                "timeout", timeout)),
    })
    if not helper.load():
        click.echo("Configuration incomplete, quitting.")
        raise SystemExit(5)


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
from synadm.cli import room, user, media, group, history
