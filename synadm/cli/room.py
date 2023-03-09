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

""" Room-related CLI commands
"""

import click

from synadm import cli


@cli.root.group()
def room():
    """ Manipulate rooms and room membership.

    The syntax of room IDs in synadm is as the Matrix spec defines:
    https://spec.matrix.org/latest/#room-structure.
    Make sure to escape the ! character from your shell. In bash and zsh this
    can be achieved by using single quotes ('), eg. '!id123abc:matrix.DOMAIN'
    """


@room.command()
@click.argument("room_id_or_alias", type=str)
@click.argument("user_id", type=str)
@click.pass_obj
def join(helper, room_id_or_alias, user_id):
    """ Join a room.
    """
    mxid = helper.generate_mxid(user_id)
    out = helper.api.room_join(room_id_or_alias, mxid)
    helper.output(out)


@room.command()
@click.argument("room_id_or_alias", type=str)
@click.option(
    "--reverse", "-r", is_flag=True, default=False, show_default=True,
    help="""Fetch all room aliases corresponding to a given room ID,
    instead of the other way round.
    """)
@click.pass_obj
def resolve(helper, room_id_or_alias, reverse):
    """ Lookup room ID from alias or vice versa.
    """
    if reverse:
        out = helper.matrix_api.room_get_aliases(room_id_or_alias)
    else:
        out = helper.matrix_api.room_get_id(room_id_or_alias)

    if out is None:
        click.echo("Room resolve failed.")
        raise SystemExit(1)
    helper.output(out)


@room.command(name="list")
@click.pass_obj
@click.option(
    "--from", "-f", "from_", type=int, default=0, show_default=True,
    help="""Offset room listing by given number. This option is used for
    pagination.""")
@click.option(
    "--limit", "-l", type=int, default=100, show_default=True,
    help="Maximum amount of rooms to return.")
@click.option(
    "--name", "-n", type=str,
    help="""Filter rooms by parts of their room name, canonical alias and room
    id.""")
@click.option(
    "--sort", "-s", type=click.Choice(
        ["name", "canonical_alias", "joined_members", "joined_local_members",
         "version", "creator", "encryption", "federatable", "public",
         "join_rules", "guest_access", "history_visibility", "state_events"]),
    help="The method in which to sort the returned list of rooms.")
@click.option(
    "--reverse", "-r", is_flag=True, default=False,
    help="""Direction of room order. If set it will reverse the sort order of
    --order-by method.""")
def list_room_cmd(helper, from_, limit, name, sort, reverse):
    """ List and search for rooms.
    """
    rooms = helper.api.room_list(from_, limit, name, sort, reverse)
    if rooms is None:
        click.echo("Rooms could not be fetched.")
        raise SystemExit(1)
    if helper.output_format == "human":
        if int(rooms["total_rooms"]) != 0:
            helper.output(rooms["rooms"])
        if "next_batch" in rooms:
            click.echo("There are more rooms than shown, use '--from {}'"
                       .format(rooms["next_batch"]))
    else:
        helper.output(rooms)


@room.command()
@click.argument("room_id", type=str)
@click.pass_obj
def details(helper, room_id):
    """ Get room details.
    """
    room_details = helper.api.room_details(room_id)
    if room_details is None:
        click.echo("Room details could not be fetched.")
        raise SystemExit(1)
    helper.output(room_details)


@room.command()
@click.argument("room_id", type=str)
@click.pass_obj
def state(helper, room_id):
    """ Get a list of all state events in a room.
    """
    room_state = helper.api.room_state(room_id)
    if room_state is None:
        click.echo("Room state could not be fetched.")
        raise SystemExit(1)
    helper.output(room_state)


@room.command()
@click.option(
    "--room-id", "-i", type=str,
    help="""View power levels of this room only.""")
@click.option(
    "--all-details", "-a", is_flag=True, default=False,
    help="""Show detailed information about each room. The default is to only
    show room_id, name, canonical_alias and power_levels.""")
@click.option(
    "--from", "-f", "from_", type=int, default=0, show_default=True,
    help="""Offset room listing by given number. This option is used for
    pagination.""")
@click.option(
    "--limit", "-l", type=int, default=10, show_default=True,
    help="Maximum amount of rooms to return.")
@click.option(
    "--name", "-n", type=str,
    help="""Filter rooms by parts of their room name, canonical alias and room
    id.""")
@click.option(
    "--sort", "-s", type=click.Choice(
        ["name", "canonical_alias", "joined_members", "joined_local_members",
         "version", "creator", "encryption", "federatable", "public",
         "join_rules", "guest_access", "history_visibility", "state_events"]),
    help="The method in which to sort the returned list of rooms.")
@click.option(
    "--reverse", "-r", is_flag=True, default=False,
    help="""Direction of room order. If set it will reverse the sort order of
    --order-by method.""")
@click.pass_obj
def power_levels(helper, room_id, all_details, from_, limit, name, sort,
                 reverse):
    """ List user's power levels set in rooms.

    A combination of commands `room list` and `room state`. It enriches
    the room list response with a list of users and their corresponding
    power levels set. It only displays a subset of the available information
    (room name, id, aliases and power levels). Increase the number of rooms
    fetched using --limit/-l (default: 10) or use the pagination option
    --from/-f to go beyond the default. Use --name/-n to search. This command
    can require quite some time to complete depending on those options.
    """
    rooms_power = helper.api.room_power_levels(
        from_, limit, name, sort, reverse, room_id, all_details,
        helper.output_format)
    if rooms_power is None:
        click.echo("Rooms and power levels could not be fetched.")
        raise SystemExit(1)

    if helper.output_format == "human":
        if int(rooms_power["total_rooms"]) != 0:
            helper.output(rooms_power["rooms"])
            click.echo("Rooms with power levels found in current batch: {}"
                       .format(rooms_power["rooms_w_power_levels_curr_batch"]))
            click.echo("Total rooms: {}"
                       .format(rooms_power["total_rooms"]))
        if "next_batch" in rooms_power:
            click.echo("Use '--from/-f {}' to view next batch."
                       .format(rooms_power["next_batch"]))
    else:
        helper.output(rooms_power)


@room.command()
@click.argument("room_id", type=str)
@click.pass_obj
def members(helper, room_id):
    """ List current room members.
    """
    room_members = helper.api.room_members(room_id)
    if room_members is None:
        click.echo("Room members could not be fetched.")
        raise SystemExit(1)
    if helper.output_format == "human":
        click.echo("Total members in room: {}"
                   .format(room_members["total"]))
        if int(room_members["total"]) != 0:
            helper.output(room_members["members"])
    else:
        helper.output(room_members)


@room.command()
@click.argument("room_id", type=str)
@click.option(
    "--new-room-user-id", "-u", type=str,
    help="""If set, a new room will be created with this user ID as the
    creator and admin, and all users in the old room will be moved into
    that room. If not set, no new room will be created and the users will
    just be removed from the old room. The user ID must be on the local
    server, but does not necessarily have to belong to a registered
    user.""")
@click.option(
    "--room-name", "-n", type=str,
    help="""A string representing the name of the room that new users will
    be invited to. Defaults to "Content Violation Notification" """)
@click.option(
    "--message", "-m", type=str,
    help="""A string containing the first message that will be sent as
    new_room_user_id in the new room. Ideally this will clearly convey why
    the original room was shut down. Defaults to "Sharing illegal content
    on this server is not permitted and rooms in violation will be
    blocked." """)
@click.option(
    "--block", "-b", is_flag=True, default=False, show_default=True,
    help="""If set, this room will be added to a blocking list,
    preventing future attempts to join the room""")
@click.option(
    "--no-purge", is_flag=True, default=False, show_default=True,
    help="""Prevent removing of all traces of the room from your
    database.""")
@click.pass_obj
@click.pass_context
def delete(ctx, helper, room_id, new_room_user_id, room_name, message, block,
           no_purge):
    """ Delete and possibly purge a room.
    """
    room_details = helper.api.room_details(room_id)
    if "errcode" in room_details.keys():
        if room_details["errcode"] == "M_NOT_FOUND":
            click.echo("Room not found.")
            raise SystemExit(1)
        else:
            click.echo("Unrecognized error")
            helper.output(room_details)
            raise SystemExit(1)
    helper.output(room_details)
    ctx.invoke(members, room_id=room_id)
    sure = (
        helper.no_confirm or
        click.prompt("Are you sure you want to delete this room? (y/N)",
                     type=bool, default=False, show_default=False)
    )
    if sure:
        mxid = helper.generate_mxid(new_room_user_id)
        room_del = helper.api.room_delete(
            room_id, mxid, room_name,
            message, block, no_purge)
        if room_del is None:
            click.echo("Room not deleted.")
            raise SystemExit(1)
        helper.output(room_del)
    else:
        click.echo("Abort.")


@room.command(name="search")
@click.argument("search-term", type=str)
@click.option(
    "--from", "-f", "from_", type=int, default=0, show_default=True,
    help="""Offset room listing by given number. This option is used for
    pagination.""")
@click.option(
    "--limit", "-l", type=int, default=100, show_default=True,
    help="Maximum amount of rooms to return.")
@click.option(
    "--sort", "-s", type=click.Choice(
        ["name", "canonical_alias", "joined_members", "joined_local_members",
         "version", "creator", "encryption", "federatable", "public",
         "join_rules", "guest_access", "history_visibility", "state_events"]),
    help="The method in which to sort the returned list of rooms.")
@click.option(
    "--reverse", "-r", is_flag=True, default=False,
    help="""Direction of room order. If set it will reverse the sort order of
    --order-by method.""")
@click.pass_context
def search_room_cmd(ctx, search_term, from_, limit, sort, reverse):
    """ An alias to `synadm room list -n <search-term>`.
    """
    ctx.invoke(list_room_cmd, from_=from_, limit=limit, name=search_term,
               sort=sort, reverse=reverse)


@room.command()
@click.argument("room_id", type=str)
@click.option(
    "--user-id", "-u", type=str,
    help="""By default the server admin (the caller) is granted power, but
    another user can optionally be specified.""")
@click.pass_obj
def make_admin(helper, room_id, user_id):
    """ Grant a user room admin permission.

    If the user is not in the room, and it is not publicly joinable, then
    invite the user.
    """

    mxid = helper.generate_mxid(user_id)
    out = helper.api.room_make_admin(room_id, mxid)
    helper.output(out)


@room.command()
@click.argument("room_id", type=str)
@click.option(
    "--block/--unblock", "-b/-u", type=bool, default=True, show_default=True,
    help="Specifies whether to block or unblock a room."
)
@click.pass_obj
def block(helper, room_id, block):
    """ Block or unblock a room.
    """
    out = helper.api.block_room(room_id, block)
    helper.output(out)


@room.command()
@click.argument("room_id", type=str)
@click.pass_obj
def block_status(helper, room_id):
    """ Get if a room is blocked, and who blocked it.
    """
    out = helper.api.room_block_status(room_id)
    helper.output(out)
