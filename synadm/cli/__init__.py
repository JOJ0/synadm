# -*- coding: utf-8 -*-
# synadm
# Copyright (C) 2020-2022 Johannes Tiefenbacher
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
from urllib.parse import urlparse
import dns.resolver
import re

from synadm import api


def humanize(data):
    """ Try to display data in a human-readable form:
    - Lists of dicts are displayed as tables.
    - Dicts are displayed as pivoted tables.
    - Lists are displayed as a simple list.
    """
    if isinstance(data, list) and len(data):
        if isinstance(data[0], dict):
            headers = {header: header for header in data[0]}
            return tabulate.tabulate(data, tablefmt="simple", headers=headers)
    if isinstance(data, list):
        return "\n".join(data)
    if isinstance(data, dict):
        return tabulate.tabulate(data.items(), tablefmt="plain")
    return str(data)


class APIHelper:
    """ API client enriched with CLI-level functions, used as a proxy to the
    client object.
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
        "matrix_path": "/_matrix",
        "timeout": 30,
        "server_discovery": "well-known",
        "homeserver": "auto-retrieval"
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
        """ Log both to console (defaults to WARNING) and file (DEBUG).
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
        """ Load the configuration and initialize the client.
        """
        try:
            with open(self.config_path) as handle:
                self.config.update(yaml.load(handle, Loader=yaml.SafeLoader))
        except Exception as error:
            self.log.error("%s while reading configuration file", error)
        for key, value in self.config.items():
            if not value:
                self.log.error("Config entry missing: %s", key)
                return False
            else:
                if key == "token":
                    self.log.debug("Config entry read. %s: REDACTED", key)
                else:
                    self.log.debug("Config entry read. %s: %s", key, value)
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
        self.misc_request = api.MiscRequest(
            self.log,
            self.config["timeout"], self.requests_debug,
        )
        return True

    def write_config(self, config):
        """ Write a new version of the configuration to file.
        """
        try:
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            with open(self.config_path, "w") as handle:
                yaml.dump(config, handle, default_flow_style=False,
                          allow_unicode=True)
            if os.name == "posix":
                click.echo("Restricting access to config file to user only.")
                os.chmod(self.config_path, 0o600)
            else:
                click.echo(f"Unsupported OS, please adjust permissions of "
                           f"{self.config_path} manually")

            return True
        except Exception as error:
            self.log.error("%s trying to write configuration", error)
            return False

    def output(self, data):
        """ Output data object using the configured formatter.
        """
        click.echo(self.formatter(data))

    def retrieve_homeserver_name(self, uri=None):
        """Try to retrieve the homeserver name.

        When homeserver is set in the config already, it's just returned and
        nothing is tried to be fetched automatically. If not, either the
        location of the Federation API is looked up via a .well-known resource
        or a DNS SRV lookup. This depends on the server_discovery setting in the
        config. Finally the Federation API is used to retrieve the homeserver
        name.

        Args:
            uri (string): proto://name:port or proto://fqdn:port

        Returns:
            string: hostname, FQDN or DOMAIN; or None on errors.
        """
        uri = uri if uri else self.config["base_url"]
        echo = self.log.info if self.batch else click.echo
        if self.config["homeserver"] != "auto-retrieval":
            return  self.config["homeserver"]

        if self.config["server_discovery"] == "well-known":
            if "localhost" in self.config["base_url"]:
                echo(
                    "Trying to fetch homeserver name via localhost..."
                )
                return self.matrix_api.server_name_keys_api(
                    self.config["base_url"]
                )
            else:
                echo(
                    "Trying to fetch federation URI via well-known resource..."
                )
                federation_uri = self.misc_request.federation_uri_well_known(uri)
                if not federation_uri:
                    return None
            return self.matrix_api.server_name_keys_api(federation_uri)
        elif self.config["server_discovery"] == "dns":
            echo(
                "Trying to fetch federation URI via DNS SRV record..."
            )
            hostname = urlparse(uri).hostname
            try:
                record = dns.resolver.query(
                    "_matrix._tcp.{}".format(hostname),
                    "SRV"
                )
            except Exception as error:
                self.log.error(
                    "resolving Matrix delegation for %s: %s: %s",
                    hostname, type(error).__name__, error
                )
            else:
                federation_uri = "https://{}:{}".format(
                    record[0].target, record[0].port
                )
                return self.matrix_api.server_name_keys_api(federation_uri)
        else:
            self.log.error("Unknown server_discovery mode. "
                           "Launch synadm config!")
        return None

    def generate_mxid(self, user_id):
        """ Checks whether the given user ID is an MXID already or else
        generates it from the passed string and the homeserver name fetched
        via the retrieve_homeserver_name method.

        Args:
            user_id (string): User ID given by user as command argument.

        Returns:
            string: the fully qualified Matrix User ID (MXID) or None if the
                user_id parameter is None.
        """
        if user_id is None:
            return None
        elif re.match(r"@[-./=\w]+:[-.\w]+", user_id):
            return user_id
        else:
            localpart = re.sub("[@:]", "", user_id)
            mxid = "@{}:{}".format(localpart, self.retrieve_homeserver_name())
            return mxid



@click.group(
    invoke_without_command=False,
    context_settings=dict(help_option_names=["-h", "--help"]))
@click.option(
    "--verbose", "-v", count=True, default=False,
    help="Enable INFO (-v) or DEBUG (-vv) logging on console.")
@click.option(
    "--batch/--no-batch", default=False,
    help="Enable batch behavior (no interactive prompts).")
@click.option(
    "--output", "-o", default="",
    type=click.Choice(["yaml", "json", "human", "pprint",
                       "y", "j", "h", "p", ""]),
    show_choices=True,
    help="""Override default output format.""")
@click.option(
    "--config-file", "-c", type=click.Path(),
    default="~/.config/synadm.yaml",
    help="Configuration file path.", show_default=True)
@click.pass_context
def root(ctx, verbose, batch, output, config_file):
    """ the Matrix-Synapse admin CLI
    """
    ctx.obj = APIHelper(config_file, verbose, batch, output)
    helper_loaded = ctx.obj.load()
    if ctx.invoked_subcommand != "config" and not helper_loaded:
        if batch:
            click.echo("Please setup synadm: " + sys.argv[0] + " config.")
            raise SystemExit(2)
        else:
            ctx.invoke(config_cmd)


@root.command(name="config")
@click.option(
    "--user", "-u", type=str,
    help="Admin user allowed to access the Synapse admin API's.")
@click.option(
    "--token", "-t", type=str,
    help="The Admin user's access token.")
@click.option(
    "--base-url", "-b", type=str,
    help="""The base URL Synapse is running on. Typically this is
    https://localhost:8008 or https://localhost:8448. If Synapse is
    configured to expose its admin API's to the outside world it might as
    well be something like this: https://example.org:8448""")
@click.option(
    "--admin-path", "-p", type=str,
    help="""The path Synapse provides its admin API's, usually the default fits
    most installations.""")
@click.option(
    "--matrix-path", "-m", type=str,
    help="""The path Synapse provides the regular Matrix API's, usually the
    default fits most installations.""")
@click.option(
    "--timeout", "-w", type=int,
    help="""The time in seconds synadm should wait for responses from admin
    API's or Matrix API's. The default is 7 seconds. """)
@click.option(
    "--output", "-o", type=click.Choice(["yaml", "json", "human", "pprint"]),
    help="""How synadm displays data by default. 'human' gives a tabular or list
    view depending on the fetched data. This mode needs your terminal to be
    quite wide! 'json' displays exactly as the API responded. 'pprint' shows
    nicely formatted json. 'yaml' is the currently recommended output format. It
    doesn't need as much terminal width as 'human' does. Note that the default
    output format can always be overridden by using global switch -o (eg 'synadm
    -o pprint user list').""")
@click.option(
    "--server-discovery", "-d", type=click.Choice(["well-known", "dns"]),
    help="""The method used for discovery of "the own homeserver name". Since
    none of the currently existing Admin API endpoints provide this
    information, the federation API among other things is asked for help. If
    set to "well-known" the URI of the federation API is tried to be fetched
    via the well-known resource of the configured "Synapse base URL". If set to
    "dns" the SRV record of the domain name found in the "Synapse base URL" is
    used to get that information. Once the federation URI is known, the
    homeserver name can be retrieved. In case "Synapse base URL" contains
    "localhost", it's assumed that the required federation API is listening on
    localhost:port already (the "keys" Matrix API endpoint). If that is failing
    as well, as a last resort solution, the homeserver name can just be saved
    to the configuration directly via the "homeserver" setting. Note that the
    fetching of the homeserver name is only executed when a synadm subcommand
    requires it (eg. like some of the media and user subcommands do), and the
    "homeserver" directive in the config is set to "auto-retrieval".
    """)
@click.option(
    "--homeserver", "-n", type=str,
    help="""Synapse homeserver hostname. Usually matrix.DOMAIN or DOMAIN. The
    default value 'auto-retrieval' will try to discover the name using the
    method set by --server-discovery."""
)
@click.pass_obj
def config_cmd(helper, user, token, base_url, admin_path, matrix_path,
               output, timeout, server_discovery, homeserver):
    """ Modify synadm's configuration. Configuration details are generally
    always asked interactively. Command line options override the suggested
    defaults in the prompts.
    """
    def get_redacted_token_prompt(cli_token):
        redacted = "NOT SET"  # Show as empty: [].
        if cli_token:
            redacted = "REDACTED"  # Token passed via cli, show [REDACTED]
        else:
            conf_token = helper.config.get("token", None)
            if conf_token:
                redacted = "REDACTED"  # Token found in config, show [REDACTED]
        return f"Synapse admin user token [{redacted}]"

    if helper.batch:
        if not all([user, token, base_url, admin_path, matrix_path,
                    output, timeout, server_discovery, homeserver]):
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
                "timeout": timeout,
                "server_discovery": server_discovery,
                "homeserver": homeserver
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
            get_redacted_token_prompt(token),
            default=token if token else helper.config.get("token", token),
            show_default=False,),
        "base_url": click.prompt(
            "Synapse base URL",
            default=base_url if base_url else helper.config.get(
                "base_url", base_url)),
        "admin_path": click.prompt(
            "Synapse admin API path",
            default=admin_path if admin_path else helper.config.get(
                "admin_path", admin_path)),
        "matrix_path": click.prompt(
            "Matrix API path",
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
        "homeserver": click.prompt(
            "Homeserver name (auto-retrieval or matrix.DOMAIN)",
            default=homeserver if homeserver else helper.config.get(
                "homeserver", homeserver)),
        "server_discovery": click.prompt(
            "Server discovery mode (used with homeserver name auto-retrieval)",
            default=server_discovery if server_discovery else helper.config.get(
                "server_discovery", server_discovery),
            type=click.Choice(["well-known", "dns"])),
    })
    if not helper.load():
        click.echo("Configuration incomplete, quitting.")
        raise SystemExit(5)


@root.command()
@click.pass_obj
def version(helper):
    """ Get the Synapse server version.
    """
    version_info = helper.api.version()
    if version_info is None:
        click.echo("Version could not be fetched.")
        raise SystemExit(1)
    helper.output(version_info)


# Import additional commands
from synadm.cli import room, user, media, group, history, matrix, regtok
