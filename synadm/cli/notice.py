# -*- coding: utf-8 -*-
# synadm
# Copyright (C) 2020-2022 Philip (a-0)
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

"""server notice-related CLI commands
"""

import click
from click_option_group import optgroup, MutuallyExclusiveOptionGroup
from click_option_group import RequiredAnyOptionGroup

from synadm import cli

@cli.root.group()
def notice():
    """ Send server notices to local users
    """

@notice.command(name="send")
@click.option("--from-file/--from-argument", "-f/-a", default=False,
    help="Interpret arguments as file paths instead of notice content and read content from those files")
@click.option("--batch", "--non-interactive", is_flag=True, default=False,
    help="Skip the confirmation step before sending notices")
@click.option("--paginate", type=int, default=100,
    help="Sets how many users will be retrieved from the server at once")
@click.argument("to", type=str, default=None)
@click.argument("plain", type=str, default=None)
@click.argument("formatted", type=str, default=None, required=False)
@click.pass_obj
def notice_send_cmd(helper, from_file, batch, paginate, to, plain, formatted):
    """Send server notices to local users.

    TO - either a matrix ID (e.g. '@abc:example.com') or a regular expression as used in python (e.g. '^.*' to send to all users)
    
    PLAIN - plain text content of the notice
    
    FORMATTED - (HTML-) formatted content of the notice. If not set, PLAIN will be used.
    """
    if from_file:
        plain_content = open(plain, "r").read()
        if formatted:
            formatted_content = open(formatted, "r").read()
        else:
            formatted_content = plain_content
    else:
        plain_content = plain
        formatted_content = formatted
    
    helper.api.notice_send(to, plain_content, formatted_content, batch, paginate)