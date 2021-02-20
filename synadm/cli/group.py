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

""" Group-related CLI commands
"""

import click

from synadm import cli


@cli.root.group()
def group():
    """ Manage groups (communities)
    """


@group.command(name="delete")
@click.argument("group_id", type=str)
@click.pass_obj
def delete(helper, group_id):
    """ delete a local group (community)
    """
    sure = (
        helper.batch or
        click.prompt("Are you sure you want to delete this group? (y/N)",
                     type=bool, default=False, show_default=False)
    )
    if sure:
        group_del = helper.api.group_delete(group_id)
        if group_del is None:
            click.echo("Group not deleted.")
            raise SystemExit(1)
        helper.output(group_del)
    else:
        click.echo("Abort.")

