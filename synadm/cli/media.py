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

""" Media-related CLI commands
"""

import click
from click_option_group import optgroup
from click_option_group import RequiredAnyOptionGroup, OptionGroup
from click_option_group import RequiredMutuallyExclusiveOptionGroup

from synadm import cli


@cli.root.group()
def media():
    """ Manage local and remote media.
    """


@media.command(name="list")
@optgroup.group(
    "List media by",
    cls=RequiredAnyOptionGroup,
    help="")
@optgroup.option(
    "--room-id", "-r", type=str,
    help="""List all media in room with this room ID ('!abcdefg').""")
@optgroup.option(
    "--user-id", "-u", type=str,
    help="""List all media uploaded by user with this matrix ID
    (@user:server).""")
@click.option(
    "--from", "-f", "from_", type=int, default=0, show_default=True,
    help="""Offset media listing by given number. This option is also used for
    pagination but only supported together with --user-id.""")
@click.option(
    "--limit", "-l", type=int, default=100, show_default=True,
    help="""Limit media listing to given number. This option is only supported
    together with --user-id.""")
@click.option(
    "--sort", "-s", type=click.Choice([
        "media_id", "upload_name", "created_ts", "last_access_ts",
        "media_length", "media_type", "quarantined_by",
        "safe_from_quarantine"]),
    help="""The method by which to sort the returned list of media. If the
    ordered field has duplicates, the second order is always by ascending
    media_id, which guarantees a stable ordering. This option is only
    supported together with --user-id.""")
@click.option(
    "--reverse", "-R", is_flag=True, default=False,
    help="""Direction of media order. If set it will reverse the sort order of
    --order-by method. This option is only supported together with --user-id.
    """)
@click.option(
    "--datetime/--timestamp", "--dt/--ts", default=True,
    help="""Display created and last accessed timestamps in a human readable
    format, or as a unix timestamp in milliseconds. This option only applies to
    user media and is ignored with room media.  [default: datetime].""")
@click.pass_obj
@click.pass_context
def media_list_cmd(ctx, helper, room_id, user_id, from_, limit, sort, reverse,
                   datetime):
    """ List local media by room or user.
    """
    if room_id:
        media_list = helper.api.room_media_list(room_id)
        if media_list is None:
            click.echo("Media list could not be fetched.")
            raise SystemExit(1)
        helper.output(media_list)
    elif user_id:
        from synadm.cli import user
        mxid = helper.generate_mxid(user_id)
        ctx.invoke(
            user.get_function("user_media_cmd"),
            user_id=mxid, from_=from_, limit=limit, sort=sort,
            reverse=reverse, datetime=datetime
        )


@media.command(name="quarantine")
@optgroup.group(
    "Quarantine media by",
    cls=RequiredAnyOptionGroup,
    help="")
@optgroup.option(
    "--media-id", "-i", type=str,
    help="""The media with this specific media ID will be quarantined.
    """)
@optgroup.option(
    "--room-id", "-r", type=str,
    help="""All media in room with this room ID (!abcdefg) will be
    quarantined.""")
@optgroup.option(
    "--user-id", "-u", type=str,
    help="""All media uploaded by user with this matrix ID (@user:server) will
    be quarantined.""")
@click.option(
    "--server-name", "-s", type=str,
    help="""The server name of the media, mandatory when --media-id is used and
    _remote_ media should be processed. For locally stored media this option
    can be omitted.
    """)
@click.pass_obj
def media_quarantine_cmd(helper, server_name, media_id, user_id, room_id):
    """ Quarantine media in rooms, by users or by media ID.
    """
    if media_id and not server_name:
        # We assume it is local media and fetch our own server name.
        fetched_name = helper.retrieve_homeserver_name(
            helper.config["base_url"])
        media_quarantined = helper.api.media_quarantine(fetched_name, media_id)
    elif server_name and not media_id:
        click.echo("Media ID missing.")
        media_quarantined = None
    elif media_id and server_name:
        media_quarantined = helper.api.media_quarantine(server_name, media_id)
    elif room_id:
        media_quarantined = helper.api.room_media_quarantine(room_id)
    elif user_id:
        mxid = helper.generate_mxid(user_id)
        media_quarantined = helper.api.user_media_quarantine(mxid)

    if media_quarantined is None:
        click.echo("Media could not be quarantined.")
        raise SystemExit(1)
    helper.output(media_quarantined)


@media.command(name="unquarantine")
@optgroup.group(
    "unquarantine media by",
    cls=RequiredAnyOptionGroup,
    help="")
@optgroup.option(
    "--media-id", "-i", type=str,
    help="""The media with this specific media ID will be removed from
    quarantine.
    """)
@click.option(
    "--server-name", "-s", type=str,
    help="""The server name of the media, mandatory when --media-id is used and
    _remote_ media should be processed. For locally stored media this option
    can be omitted.
    """)
@click.pass_obj
def media_unquarantine_cmd(helper, server_name, media_id):
    """ Remove media from quarantine.
    """
    if media_id and not server_name:
        # We assume it is local media and fetch our own server name.
        fetched_name = helper.retrieve_homeserver_name(
            helper.config["base_url"])
        unquarantinend = helper.api.media_unquarantine(fetched_name, media_id)
    elif server_name and not media_id:
        click.echo("Media ID missing.")
        unquarantinend = None
    elif media_id and server_name:
        unquarantinend = helper.api.media_unquarantine(server_name, media_id)

    if unquarantinend is None:
        click.echo("Media could not be removed from quarantine.")
        raise SystemExit(1)
    helper.output(unquarantinend)


@media.command(name="protect")
@click.argument("media_id", type=str)
@click.pass_obj
def media_protect_cmd(helper, media_id):
    """ Protect specific media from being quarantined.
    """
    media_protected = helper.api.media_protect(media_id)
    if media_protected is None:
        click.echo("Media could not be protected.")
        raise SystemExit(1)
    helper.output(media_protected)


@media.command(name="purge")
@optgroup.group(
    "Purge by",
    cls=RequiredMutuallyExclusiveOptionGroup,
    help="")
@optgroup.option(
    "--before-days", "-d", type=int,
    help="""Purge all media that was last accessed before this number of days
    ago.
    """)
@optgroup.option(
    "--before", "-b", type=click.DateTime(),
    help="""Purge all media that was last accessed before this date/time. Eg.
    '2021-01-01', see above for available date/time formats.""")
@optgroup.option(
    "--before-ts", "-t", type=int,
    help="""Purge all media that was last accessed before this unix
    timestamp in ms.
    """)
@click.pass_obj
def media_purge_cmd(helper, before_days, before, before_ts):
    """ Purge old cached remote media

    To delete local media, use `synadm media delete`
    """
    media_purged = helper.api.purge_media_cache(before_days, before, before_ts)
    if media_purged is None:
        click.echo("Media cache could not be purged.")
        raise SystemExit(1)
    helper.output(media_purged)


@media.command(name="delete")
@optgroup.group(
    "delete criteria",
    cls=RequiredMutuallyExclusiveOptionGroup,
    help="")
@optgroup.option(
    "--media-id", "-i", type=str,
    help="""The media with this specific media ID will be deleted.""")
@optgroup.option(
    "--before-days", "-d", type=int,
    help="""Delete all media that was last accessed before this number of
    days ago.
    """)
@optgroup.option(
    "--before", "-b", type=click.DateTime(),
    help="""Delete all media that was last accessed before this date/time. Eg.
    '2021-01-01', see above for available date/time formats.""")
@optgroup.option(
    "--before-ts", "-t", type=int,
    help="""Delete all media that was last accessed before this unix
    timestamp in ms.""")
@optgroup.group(
    "Additional switches",
    cls=OptionGroup,
    help="")
@optgroup.option(
    "--size", "--kib", type=int,
    help="""Delete all media that is larger than this size in KiB
    (1 KiB = 1024 bytes).""")
@optgroup.option(
    "--delete-profiles", "--all", is_flag=True,
    help="""Also delete files that are still used in image data
    (e.g user profile, room avatar). If set, these files will be
    deleted too. Not valid when a specific media is being deleted
    (--media-id)""")
@click.pass_obj
def media_delete_cmd(helper, media_id, before_days, before, before_ts,
                     size, delete_profiles):
    """ Delete local media by ID, size or age

    To delete cached remote media, use `synadm media purge`
    """
    if media_id and delete_profiles:
        click.echo("Combination of --media-id and --delete-profiles not "
                   "valid.")
        media_deleted = None
    elif media_id and size:
        click.echo("Combination of --media-id and --size not valid.")
        media_deleted = None
    elif media_id:
        server_name = helper.retrieve_homeserver_name(
                helper.config["base_url"])
        media_deleted = helper.api.media_delete(server_name, media_id)
    else:
        media_deleted = helper.api.media_delete_by_date_or_size(
            before_days, before, before_ts, size, delete_profiles
        )

    if media_deleted is None:
        click.echo("Media could not be deleted.")
        raise SystemExit(1)
    helper.output(media_deleted)
