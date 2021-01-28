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
