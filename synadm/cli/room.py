from synadm.cli import root, cont_set, log, get_table
from synadm import api

from pprint import pprint

import click


@root.group(context_settings=cont_set)
def room():
    """list/delete rooms, show/invite/join members, ...
    """


@room.command(name='list', context_settings=cont_set)
@click.pass_context
@click.option('--from', '-f', 'from_', type=int, default=0, show_default=True,
      help="""offset room listing by given number. This option is also used
      for pagination.""")
@click.option('--limit', '-l', type=int, default=100, show_default=True,
      help="Maximum amount of rooms to return.")
@click.option('--name', '-n', type=str,
      help="""Filter rooms by their room name. Search term can be contained in
      any part of the room name)""")
@click.option('--order-by', '-o', type=click.Choice(['name', 'canonical_alias',
      'joined_members', 'joined_local_members', 'version', 'creator',
      'encryption', 'federatable', 'public', 'join_rules', 'guest_access',
      'history_visibility', 'state_events']),
      help="The method in which to sort the returned list of rooms.")
@click.option('--reverse', '-r', is_flag=True, default=False,
      help="""Direction of room order. If set it will reverse the sort order of
      --order-by method.""")
def list_room_cmd(ctx, from_, limit, name, order_by, reverse):
    synadm = api.Synapse_admin(log, ctx.obj['config'].user, ctx.obj['config'].token,
          ctx.obj['config'].base_url, ctx.obj['config'].admin_path)
    rooms = synadm.room_list(from_, limit, name, order_by, reverse)
    if rooms == None:
        click.echo("Rooms could not be fetched.")
        raise SystemExit(1)

    if ctx.obj['view'] == 'raw':
        pprint(rooms)
    else:
        if int(rooms['total_rooms']) != 0:
            tab_rooms = get_table(rooms['rooms'])
            click.echo(tab_rooms)
        if 'next_batch' in rooms:
            m_n = "\nThere is more rooms than shown, use '--from {}' ".format(
                  rooms['next_batch'])
            m_n+="to go to next page.\n"
            click.echo(m_n)


@room.command(context_settings=cont_set)
@click.argument('room_id', type=str)
@click.pass_context
def details(ctx, room_id):
    synadm = api.Synapse_admin(log, ctx.obj['config'].user, ctx.obj['config'].token,
          ctx.obj['config'].base_url, ctx.obj['config'].admin_path)
    room = synadm.room_details(room_id)
    if room == None:
        click.echo("Room details could not be fetched.")
        raise SystemExit(1)

    if ctx.obj['view'] == 'raw':
        pprint(room)
    else:
        if room != {}:
            tab_room = get_table(room, listify=True)
            click.echo(tab_room)


@room.command(context_settings=cont_set)
@click.argument('room_id', type=str)
@click.pass_context
def members(ctx, room_id):
    synadm = api.Synapse_admin(log, ctx.obj['config'].user, ctx.obj['config'].token,
          ctx.obj['config'].base_url, ctx.obj['config'].admin_path)
    members = synadm.room_members(room_id)
    if members == None:
        click.echo("Room members could not be fetched.")
        raise SystemExit(1)

    if ctx.obj['view'] == 'raw':
        pprint(members)
    else:
        click.echo(
              "\nTotal members in room: {}\n".format(
              members['total']))
        if int(members['total']) != 0:
            for member in members['members']:
                click.echo(member)


@room.command(context_settings=cont_set)
@click.pass_context
@click.argument('room_id', type=str)
@click.option('--new-room-user-id', '-u', type=str,
      help='''If set, a new room will be created with this user ID as the
      creator and admin, and all users in the old room will be moved into
      that room. If not set, no new room will be created and the users will
      just be removed from the old room. The user ID must be on the local
      server, but does not necessarily have to belong to a registered
      user.''')
@click.option('--room-name', '-n', type=str,
       help='''A string representing the name of the room that new users will
       be invited to. Defaults to "Content Violation Notification"''')
@click.option('--message', '-m', type=str,
      help='''A string containing the first message that will be sent as
      new_room_user_id in the new room. Ideally this will clearly convey why
      the original room was shut down. Defaults to "Sharing illegal content
      on this server is not permitted and rooms in violation will be
      blocked."''')
@click.option('--block', '-b', is_flag=True, default=False, show_default=True,
      help='''If set, this room will be added to a blocking list,
      preventing future attempts to join the room''')
@click.option('--no-purge', is_flag=True, default=False, show_default=True,
      help='''Prevent removing of all traces of the room from your
      database.''')
def delete(ctx, room_id, new_room_user_id, room_name, message, block, no_purge):
    synadm = api.Synapse_admin(log, ctx.obj['config'].user, ctx.obj['config'].token,
          ctx.obj['config'].base_url, ctx.obj['config'].admin_path)

    ctx.invoke(details, room_id=room_id)
    ctx.invoke(members, room_id=room_id)

    sure = click.prompt("\nAre you sure you want to delete this room? (y/N)",
          type=bool, default=False, show_default=False)
    if sure:
        room_del = synadm.room_delete(room_id, new_room_user_id, room_name,
              message, block, no_purge)
        if room_del == None:
            click.echo("Room not deleted.")
            raise SystemExit(1)

        if ctx.obj['view'] == 'raw':
            pprint(room_del)
        else:
            if room_del != {}:
                tab_room = get_table(room_del, listify=True)
                click.echo(tab_room)
    else:
        click.echo('Abort.')


@room.command(name='search', context_settings=cont_set)
@click.pass_context
@click.argument('search-term', type=str)
@click.option('--from', '-f', 'from_', type=int, default=0, show_default=True,
      help='''offset room listing by given number. This option is also used
      for pagination.''')
@click.option('--limit', '-l', type=int, default=100, show_default=True,
      help='Maximum amount of rooms to return.')
def search_room_cmd(ctx, search_term, from_, limit):
    '''a simplified shortcut to \'synadm room list -n <search-term>\'. Also
    it executes a case-insensitive search compared to the original
    command.'''
    if search_term[0].isupper():
        search_term_cap = search_term
        search_term_nocap = search_term[0].lower() + search_term[1:]
    else:
        search_term_cap = search_term[0].upper() + search_term[1:]
        search_term_nocap = search_term

    click.echo("\nRoom search results for '{}':\n".format(search_term_nocap))
    ctx.invoke(list_room_cmd, from_=from_, limit=limit, name=search_term_nocap)
    click.echo("\nRoom search results for '{}':\n".format(search_term_cap))
    ctx.invoke(list_room_cmd, from_=from_, limit=limit, name=search_term_cap)
