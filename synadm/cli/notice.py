# -*- coding: utf-8 -*-
# synadm
# Copyright (C) 2022 Philip (a-0)
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

"""Server notice-related CLI commands
"""

import re
import click

from synadm import cli


@cli.root.group()
def notice():
    """ Send messages to users.
    """


@notice.command(name="send")
@click.option(
    "--from-file", "-f", default=False, show_default=True, is_flag=True,
    help="""Interpret arguments as file paths instead of notice content and
    read content from those files.""")
@click.option(
    "--batch-size", "--paginate", "-p", type=int, default=100,
    show_default=True, metavar="SIZE",
    help="""The send command retrieves "pages" of users from the homeserver,
    filters them and sends out the notices, before retrieving the next page.
    SIZE sets how many users are in each of these "pages". It is a performance
    setting and may be useful for servers with a large amount of users.""")
@click.option(
    "--regex", "-r", default=False, show_default=True, is_flag=True,
    help="Interpret TO as regular expression.")
@click.option(
    "--preview-length", "-l", type=int, default=10, show_default=True,
    metavar="LENGTH", help="""Length of the displayed list of matched
    recipients shown in the confirmation prompt. Does not impact sending
    behavior. Is ignored when global --non-interactive flag is given.""")
@click.option(
    "--silent", "-s", default=False, show_default=True, is_flag=True,
    help="""Usually synadm commands print to console what the API returned.
    With the "Server Notices Admin API", an event ID or an error messages
    would be printed for each message sent. Large amounts of recipients could
    possibly lead to performance impacts, thus this option can be used to
    disable printing of what the API responded.
    """)
@click.argument("to", type=str, default=None)
@click.argument("plain", type=str, default=None)
@click.argument("formatted", type=str, default=None, required=False)
@click.pass_obj
def notice_send_cmd(helper, from_file, batch_size, regex, preview_length,
                    silent, to, plain, formatted):
    """Send server notices to users on the local homeserver.

    \b
    TO
        Localpart or full matrix ID of the notice receiver. If --regex is set
        this will be interpreted as a regular expression.

    \b
    PLAIN
        Plain text content of the notice.

    \b
    FORMATTED
        Formatted content of the notice. If omitted, PLAIN will be used.
    """
    def confirm_prompt():
        prompt = ""
        if helper.no_confirm:
            return True
        if not silent:
            prompt += "\nNote: When sending to a large amount of recipients, "
            prompt += "consider using the --silent option.\n\n"
        prompt += "Recipients:\n"
        if not regex:
            prompt += " - " + to + "\n"
        else:
            # Build and print a list of receivers matching the regex
            ctr, next_token = 0, 0
            # Outer loop: If fetching >1 pages of users is required
            while ctr < preview_length:
                batch = helper.api.user_list(
                    next_token, batch_size, True, False, "", "")
                if "users" not in batch:
                    break
                batch_mxids = [user['name'] for user in batch["users"]]
                # Match every matrix ID of this batch
                for mxid in batch_mxids:
                    if re.match(to, mxid):
                        if ctr < preview_length:
                            prompt += " - " + mxid + "\n"
                            ctr += 1
                        else:
                            prompt += " - ...\n"
                            break
                if "next_token" not in batch:
                    break
                next_token = batch["next_token"]
            if ctr == 0:
                prompt += "(no recipient matched)\n"
        prompt += f"\nPlaintext message:\n---\n{plain_content}\n---"
        prompt += f"\nFormatted message:\n---\n{formatted_content}\n---"
        prompt += "\nSend now?"
        return click.confirm(prompt)

    if from_file:
        try:
            with open(plain, "r") as plain_file:
                plain_content = plain_file.read()
            if formatted:
                with open(formatted, "r") as formatted_file:
                    formatted_content = formatted_file.read()
            else:
                formatted_content = plain_content
        except Exception as error:
            helper.log.error(error)
            raise SystemExit(1)
    else:
        plain_content = plain
        formatted_content = formatted if formatted else plain_content

    if regex:
        if "users" not in helper.api.user_list(0, 100, True, False, "", ""):
            return
        if not confirm_prompt():
            return
    else:
        to = helper.generate_mxid(to)
        if to is None:
            click.echo("The recipient you specified is invalid.")
            return
        if not confirm_prompt():
            return

    outputs = helper.api.notice_send(to, plain_content, formatted_content,
                                     batch_size, regex)
    if not silent:
        helper.output(outputs)
