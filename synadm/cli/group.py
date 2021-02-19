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

