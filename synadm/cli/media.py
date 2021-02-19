# -*- coding: utf-8 -*-
# synadm - Matrix-Synapse admin CLI
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

""" Media-related CLI commands
"""

import click

from synadm import cli
import click_option_group


@cli.root.group()
def media():
    """ Manage local and remote media
    """


@media.command(name="list")
@click.argument("room_id", type=str)
@click.pass_obj
def media_list_cmd(helper, room_id):
    """ list all media in a room
    """
    media_list = helper.api.room_media_list(room_id)
    if media_list is None:
        click.echo("Media list could not be fetched.")
        raise SystemExit(1)
    helper.output(media_list)


@media.command(name="quarantine")
@click_option_group.optgroup.group(
    "Quarantine media by",
    cls=click_option_group.RequiredAnyOptionGroup,
    help="")
@click_option_group.optgroup.option(
    "--media-id", "-i", type=str,
    help="""the media with this specific media ID will be quarantined.
    """)
@click_option_group.optgroup.option(
    "--room-id", "-r", type=str,
    help="""all media in room with this room ID (!abcdefg) will be
    quarantined.""")
@click_option_group.optgroup.option(
    "--user-id", "-u", type=str,
    help="""all media uploaded by user with this matrix ID (@user:server) will
    be quarantined.""")
@click.option(
    "--server-name", "-s", type=str,
    help="""the server name of the media, mandatory when --media-id is used.
    """)
@click.pass_obj
def media_quarantine_cmd(helper, server_name, media_id, user_id, room_id):
    """ quarantine media in rooms, by users or by media ID
    """
    if media_id and not server_name:
        click.echo("Server name missing.")
        media_quarantined = None
    elif server_name and not media_id:
        click.echo("Media ID missing.")
        media_quarantined = None
    elif media_id and server_name:
        media_quarantined = helper.api.media_quarantine(server_name, media_id)
    elif room_id:
        media_quarantined = helper.api.room_media_quarantine(room_id)
    elif user_id:
        media_quarantined = helper.api.user_media_quarantine(user_id)

    if media_quarantined is None:
        click.echo("Media could not be quarantined.")
        raise SystemExit(1)
    helper.output(media_quarantined)


@media.command(name="protect")
@click.argument("media_id", type=str)
@click.pass_obj
def media_protect_cmd(helper, media_id):
    """ protect specific media from being quarantined
    """
    media_protected = helper.api.media_protect(media_id)
    if media_protected is None:
        click.echo("Media could not be protected.")
        raise SystemExit(1)
    helper.output(media_protected)


@media.command(name="purge")
@click_option_group.optgroup.group(
    "Purge by",
    cls=click_option_group.RequiredMutuallyExclusiveOptionGroup,
    help="")
@click_option_group.optgroup.option(
    "--days", "-d", type=int,
    help="""Purge all media that was last accessed before this number of days.
    """)
@click_option_group.optgroup.option(
    "--before", "-b", type=click.DateTime(),
    help="""Purge all media that was last accessed before this date/time. Eg.
    '2021-01-01', see above for available date/time formats.""")
@click_option_group.optgroup.option(
    "--before-ts", "-t", type=int,
    help="""Purge all media that was last accessed before this unix
    timestamp in ms.
    """)
@click.pass_obj
def media_purge_cmd(helper, days, before, before_ts):
    """ Purge old cached remote media
    """
    media_purged = helper.api.purge_media_cache(days, before, before_ts)
    if media_purged is None:
        click.echo("Media cache could not be purged.")
        raise SystemExit(1)
    helper.output(media_purged)


@media.command(name="delete")
@click_option_group.optgroup.group(
    "delete criteria",
    cls=click_option_group.RequiredMutuallyExclusiveOptionGroup,
    help="")
@click_option_group.optgroup.option(
    "--media-id", "-i", type=str,
    help="""the media with this specific media ID will be deleted.""")
@click_option_group.optgroup.option(
    "--days", "-d", type=int,
    help="""delete all media that was last accessed before this number of days.
    """)
@click_option_group.optgroup.option(
    "--before", "-b", type=click.DateTime(),
    help="""delete all media that was last accessed before this date/time. Eg.
    '2021-01-01', see above for available date/time formats.""")
@click_option_group.optgroup.option(
    "--before-ts", "-t", type=int,
    help="""delete all media that was last accessed before this unix
    timestamp in ms.""")
@click_option_group.optgroup.group(
    "additional switches",
    cls=click_option_group.OptionGroup,
    help="")
@click_option_group.optgroup.option(
    "--size", "--kib", type=int,
    help="""delete all media that is larger than this size in KiB
    (1 KiB = 1024 bytes).""")
@click_option_group.optgroup.option(
    "--delete-profiles", "--all", is_flag=True,
    help="""also delete files that are still used in image data
    (e.g user profile, room avatar). If set, these files will be
    deleted too. Not valid when a specific media is being deleted
    (--media-id)""")
@click.option(
    "--server-name", "-s", type=str,
    help="""your local matrix server name. Note: Currently this is a mandatory
    argument but will be automatically retrieved via the matrix API in
    the future.""")
@click.pass_obj
def media_delete_cmd(helper, media_id, server_name, days, before, before_ts,
                     size, delete_profiles):
    """ delete media by ID, size or age
    """
    if not server_name:  # FIXME pull local server name programatically
        click.echo("--server-name missing.")
        media_deleted = None
    elif media_id and delete_profiles:
        click.echo("Combination of --media-id and --delete-profiles not valid.")
        media_deleted = None
    elif media_id and size:
        click.echo("Combination of --media-id and --size not valid.")
        media_deleted = None
    elif media_id:
        media_deleted = helper.api.media_delete(server_name, media_id)
    else:
        media_deleted = helper.api.media_delete_by_date_or_size(
            server_name, days, before, before_ts, size, delete_profiles
        )

    if media_deleted is None:
        click.echo("Media could not be deleted.")
        raise SystemExit(1)
    helper.output(media_deleted)
