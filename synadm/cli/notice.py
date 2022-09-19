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

"""server notice-related CLI commands
"""

import re
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
    help="""Interpret arguments as file paths instead of notice content and 
    read content from those files""")
@click.option("--paginate", type=int, default=100,
    help="Sets how many users will be retrieved from the server at once")
@click.option("--to-regex", "-r", default=False, show_default=True, 
    is_flag=True, help="Interpret TO as regular expression")
@click.argument("to", type=str, default=None)
@click.argument("plain", type=str, default=None)
@click.argument("formatted", type=str, default=None, required=False)
@click.pass_obj
def notice_send_cmd(helper, from_file, paginate, to_regex, to, plain, formatted):
    """Send server notices to local users.

    TO - localpart or full matrix ID of the notice receiver. If --to-regex is
        set this will be interpreted as regular expression.
    
    PLAIN - plain text content of the notice
    
    FORMATTED - (HTML-) formatted content of the notice. If not set, PLAIN 
        will be used.
    """
    if from_file:
        with open(plain, "r") as plain_file:
            plain_content = plain_file.read()
        if formatted:
            with open(formatted, "r") as formatted_file:
                formatted_content = formatted_file.read()
        else:
            formatted_content = plain_content
    else:
        plain_content = plain
        if formatted is None:
            formatted_content = plain
        else:
            formatted_content = formatted
    
    def confirm_prompt(users):
            if helper.batch:
                return True
            prompt = "Recipients (list may be incomplete):\n"
            ctr = 0
            for user in users:
                if not re.search(to, user) is None:
                    prompt = prompt + " - " + user + "\n"
                    ctr = ctr + 1
                    if ctr >= 10:
                        prompt = prompt + " - ..."
                        break
            prompt = prompt + "\nUnformatted message:\n---\n" + plain_content\
                + "\n---\nFormatted message:\n---\n" + formatted_content\
                + "\n---\nSend now?"
            return click.confirm(prompt)
    
    if to_regex:
        first_batch = helper.api.user_list(0, paginate, True, False, "", "")
        if "users" not in first_batch:
            return
        if not confirm_prompt([user['name'] for user in first_batch["users"]]):
            return
    else:
        to = helper.generate_mxid(to)
        if not confirm_prompt([to]):
            return
    
    helper.api.notice_send(to, plain_content, formatted_content, paginate, to_regex)
