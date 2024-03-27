# -*- coding: utf-8 -*-
# synadm
# Copyright (C) 2020-2023 Johannes Tiefenbacher
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

""" CLI root-level commands; Subcommands are imported at the bottom of file
"""

import sys
import click

output_format_help = """The 'human' mode gives a tabular or list view depending
on the fetched data, but often needs a lot of horizontal space to display
correctly. 'json' returns formatted json. 'minified' is minified json, suitable
for scripting purposes. 'pprint' shows a formatted output with the help of
Python's built-in pprint module. 'yaml' is a compromise between human- and
machine-readable output, it doesn't need as much terminal width as 'human' does
and is the default on fresh installations."""


@click.group(
    invoke_without_command=False,
    context_settings=dict(help_option_names=["-h", "--help"]))
@click.version_option()
@click.option(
    "--verbose", "-v", count=True, default=False,
    help="Enable INFO (-v) or DEBUG (-vv) logging on console.")
@click.option(
    "--no-confirm", "--batch", "--yes", "--non-interactive", "--scripting",
    default=False, is_flag=True,
    help="""Enable non-interactive mode. Use with caution! This will:

    \b
        - Disable all interactive prompts.
        - Disable automatic translation of unix timestamps to human readable
          formats.
    """)
@click.option(
    "--output", "-o", default="",
    type=click.Choice(["yaml", "json", "minified", "human", "pprint",
                       "y", "j", "m", "h", "p", ""]),
    show_choices=True,
    help=f"Override default output format. {output_format_help}")
@click.option(
    "--config-file", "-c", type=click.Path(),
    default="~/.config/synadm.yaml",
    help="Configuration file path.", show_default=True)
@click.pass_context
def root(ctx, verbose, no_confirm, output, config_file):
    """ the Matrix-Synapse admin CLI
    """
    from synadm.cli._helper import APIHelper
    ctx.obj = APIHelper(config_file, verbose, no_confirm, output)
    helper_loaded = ctx.obj.load()
    if ctx.invoked_subcommand != "config" and not helper_loaded:
        if no_confirm:
            click.echo("Please setup synadm: " + sys.argv[0] + " config.")
            raise SystemExit(2)
        else:
            ctx.invoke(config_cmd)


@root.command(name="config")
@click.option(
    "--user", "-u", "user_", type=str,
    help="Admin user allowed to access the Synapse Admin API's.")
@click.option(
    "--token", "-t", type=str,
    help="The Admin user's access token.")
@click.option(
    "--base-url", "-b", type=str,
    help="""The base URL Synapse is running on. Typically this is
    https://localhost:8008 or https://localhost:8448. If Synapse is
    configured to expose its Admin API's to the outside world it might as
    well be something like this: https://example.org:8448""")
@click.option(
    "--admin-path", "-p", type=str,
    help="""The path Synapse provides its Admin API's, usually the default fits
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
    "--output", "-o", type=click.Choice([
        "yaml", "json", "minified", "human", "pprint"]),
    help=f"""How synadm displays data by default. {output_format_help} The
    default output format can always be overridden by using the global
    --output/-o switch (eg 'synadm -o pprint user list').""")
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
@click.option(
    "--ssl-verify", "-i",  is_flag=True, show_default=True,
    help="""Whether or not SSL certificates should be verified. Set to False
    to allow self-signed certifcates."""
)
@click.pass_obj
def config_cmd(helper, user_, token, base_url, admin_path, matrix_path,
               output, timeout, server_discovery, homeserver, ssl_verify):
    """ Modify synadm's configuration.

    Configuration details are generally always asked interactively. Command
    line options override the suggested defaults in the prompts.
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

    if helper.no_confirm:
        if not all([user, token, base_url, admin_path, matrix_path,
                    output, timeout, server_discovery, homeserver,
                    ssl_verify]):
            click.echo(
                "Missing config options for non-interactive configuration!"
            )
            raise SystemExit(3)
        else:
            click.echo("Saving to config file.")
            if helper.write_config({
                "user": user_,
                "token": token,
                "base_url": base_url,
                "admin_path": admin_path,
                "matrix_path": matrix_path,
                "format": output,
                "timeout": timeout,
                "server_discovery": server_discovery,
                "homeserver": homeserver,
                "ssl_verify": ssl_verify
            }):
                raise SystemExit(0)
            else:
                raise SystemExit(4)

    click.echo("Running configurator...")
    helper.write_config({
        "user": click.prompt(
            "Synapse admin user name",
            default=user_ if user_ else helper.config.get("user", user_)),
        "token": click.prompt(
            get_redacted_token_prompt(token),
            default=token if token else helper.config.get("token", token),
            show_default=False, hide_input=True),
        "base_url": click.prompt(
            "Synapse base URL",
            default=base_url if base_url else helper.config.get(
                "base_url", base_url)),
        "admin_path": click.prompt(
            "Synapse Admin API path",
            default=admin_path if admin_path else helper.config.get(
                "admin_path", admin_path)),
        "matrix_path": click.prompt(
            "Matrix API path",
            default=matrix_path if matrix_path else helper.config.get(
                "matrix_path", matrix_path)),
        "format": click.prompt(
            "Default output format",
            default=output if output else helper.config.get("format", output),
            type=click.Choice([
                "yaml", "json", "minified", "human", "pprint"])),
        "timeout": click.prompt(
            "Default http timeout",
            default=timeout if timeout else helper.config.get(
                "timeout", timeout)),
        "homeserver": click.prompt(
            "Homeserver name (\"auto-retrieval\" or the domain part in your "
            "MXID)",
            default=homeserver if homeserver else helper.config.get(
                "homeserver", homeserver)),
        "ssl_verify": click.prompt(
            "Verify certificate",
            type=bool,
            default=ssl_verify if ssl_verify else helper.config.get(
                "ssl_verify", ssl_verify)),
        "server_discovery": click.prompt(
            "Server discovery mode (used with homeserver name auto-retrieval)",
            default=server_discovery if server_discovery else helper.config.get(  # noqa: E501
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
from synadm.cli import room, user, media, group, history, matrix, regtok, notice, raw  # noqa: F401, E402, E501
