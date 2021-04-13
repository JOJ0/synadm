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

""" Purge-history-related CLI commands
"""

import click
from click_option_group import optgroup, RequiredMutuallyExclusiveOptionGroup

from synadm import cli


@cli.root.group()
def history():
    """ purge historic events from Synapse database
    """


@history.command(name="purge")
@click.argument("room_id", type=str)
@optgroup.group(
    "Purge before",
    cls=RequiredMutuallyExclusiveOptionGroup,
    help="")
@optgroup.option(
    "--event-id", "-i", type=str,
    help="""purge all history before this event ID.""")
@optgroup.option(
    "--before-days", "-d", type=int,
    help="""purge all history before this number of days ago.""")
@optgroup.option(
    "--before", type=click.DateTime(),
    help="""purge all history before this point in time. Eg. '2021-01-01', see
    above for available date/time formats.""")
@optgroup.option(
    "--before-ts", type=int,
    help="""purge all history before this point in time giving a unix
    timestamp in ms. """)
@click.option(
    "--delete-local", is_flag=True,
    help="""this option overrides the default behavior and forces removal of
    events sent by local users.""")
@click.pass_obj
def history_purge_cmd(helper, event_id, days, before, before_ts):
    """ purge room events before a point in time or before an event ID.

    The purge history API allows server admins to purge historic events from
    their database, reclaiming disk space.

    Depending on the amount of history being purged a call to the API may
    take several minutes or longer. During this period users will not be able
    to paginate further back in the room from the point being purged from.

    Note that Synapse requires at least one message in each room, so it will
    never delete the last message in a room.

    By default, events sent by local users are not deleted, as they may
    represent the only copies of this content in existence. (Events sent by
    remote users are deleted.)

    Room state data (such as joins, leaves, topic) is always preserved.

    The API starts the purge running, and returns immediately with a JSON
    body with a purge id. Use 'synadm history purge-status <purge id>' to
    poll for updates on the running purge.
    """
    history_purged = helper.api.purge_history(event_id, days, before,
                                              before_ts)
    if history_purged is None:
        click.echo("History could not be purged.")
        raise SystemExit(1)
    helper.output(history_purged)
