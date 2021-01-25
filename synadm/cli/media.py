""" Media-related CLI commands
"""

import click

from synadm import cli


@cli.root.group()
def media():
    """ Manage local and remote media
    """


@media.command(name="list")
@click.argument("room_id", type=str)
@click.pass_obj
def media_list_cmd(helper,room_id):
    """ list all media in a room
    """
    media_list = helper.api.room_media_list(room_id)
    if media_list is None:
        click.echo("Media list could not be fetched.")
        raise SystemExit(1)
    helper.output(media_list)