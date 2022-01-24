# -*- coding: utf-8 -*-
# synadm
# Copyright (C) 2020-2022 Johannes Tiefenbacher
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

""" User-related CLI commands
"""

import click
from click_option_group import optgroup, MutuallyExclusiveOptionGroup
from click_option_group import RequiredAnyOptionGroup

from synadm import cli


# helper function to retrieve functions from within this package from another
# package (e.g used in ctx.invoke calls)
def get_function(function_name):
    if function_name == 'user_media_cmd':
        return user_media_cmd


@cli.root.group()
def user():
    """ List, add, modify, deactivate/erase users, reset passwords
    """


@user.command(name="list")
@click.option(
    "--from", "-f", "from_", type=int, default=0, show_default=True,
    help="""Offset user listing by given number. This option is also used for
    pagination.""")
@click.option(
    "--limit", "-l", type=int, default=100, show_default=True,
    help="Limit user listing to given number")
@click.option(
    "--guests/--no-guests", "-g/-G", default=None, show_default=True,
    help="Show guest users.")
@click.option(
    "--deactivated", "-d", is_flag=True, default=False,
    help="Also show deactivated/erased users", show_default=True)
@optgroup.group(
    "Search options",
    cls=MutuallyExclusiveOptionGroup,
    help="")
@optgroup.option(
    "--name", "-n", type=str,
    help="""Search users by name - filters to only return users with user ID
    localparts or displaynames that contain this value (localpart is the left
    part before the colon of the matrix ID (@user:server)""")
@optgroup.option(
    "--user-id", "-i", type=str,
    help="""Search users by ID - filters to only return users with Matrix IDs
    (@user:server) that contain this value""")
@click.pass_obj
def list_user_cmd(helper, from_, limit, guests, deactivated, name, user_id):
    """ List and search for users
    """
    users = helper.api.user_list(from_, limit, guests, deactivated, name,
                                 user_id)
    if users is None:
        click.echo("Users could not be fetched.")
        raise SystemExit(1)
    if helper.output_format == "human":
        click.echo("Total users on homeserver (excluding deactivated): {}"
                   .format(users["total"]))
        if int(users["total"]) != 0:
            helper.output(users["users"])
        if "next_token" in users:
            click.echo("There are more users than shown, use '--from {}' "
                       .format(users["next_token"]) +
                       "to go to next page")
    else:
        helper.output(users)


@user.command()
@click.argument("user_id", type=str)
@click.option(
    "--gdpr-erase", "-e", is_flag=True, default=False,
    help="""Marks the user as GDPR-erased. This means messages sent by the
    user will still be visible by anyone that was in the room when these
    messages were sent, but hidden from users joining the room
    afterwards.""", show_default=True)
@click.pass_obj
@click.pass_context
def deactivate(ctx, helper, user_id, gdpr_erase):
    """ Deactivate or gdpr-erase a user. Provide matrix user ID (@user:server)
    as argument. It removes active access tokens, resets the password, and
    deletes third-party IDs (to prevent the user requesting a password
    reset).
    """
    click.echo("""
    Note that deactivating/gdpr-erasing a user leads to the following:
    - Removal from all joined rooms
    - Password reset
    - Deletion of third-party-IDs (to prevent the user requesting a password)
    """)
    ctx.invoke(user_details_cmd, user_id=user_id)
    ctx.invoke(membership, user_id=user_id)
    m_erase_or_deact = "gdpr-erase" if gdpr_erase else "deactivate"
    m_erase_or_deact_p = "gdpr-erased" if gdpr_erase else "deactivated"
    sure = (
        helper.batch or
        click.prompt("Are you sure you want to {} this user? (y/N)"
                     .format(m_erase_or_deact),
                     type=bool, default=False, show_default=False)
    )
    if sure:
        deactivated = helper.api.user_deactivate(user_id, gdpr_erase)
        if deactivated is None:
            click.echo("User could not be {}.".format(m_erase_or_deact))
            raise SystemExit(1)
        if helper.output_format == "human":
            if deactivated["id_server_unbind_result"] == "success":
                click.echo("User successfully {}.".format(m_erase_or_deact_p))
            else:
                click.echo("Synapse returned: {}".format(
                           deactivated["id_server_unbind_result"]))
        else:
            helper.output(deactivated)
    else:
        click.echo("Abort.")


@user.command(name="prune-devices")
@click.argument("user_id", type=str)
@click.option(
    "--list-only", "-l", is_flag=True, default=False,
    help="""Dry-run: does not perform the deletion but shows what would be done.
    If you want to list all devices/sessions, you can also use the whois
    command.""",
    show_default=True)
@click.option(
    "--min-days", "-d", type=int, default=90,
    help="""How many days need to have passed from the last time a device was
    seen for it to be deleted.""",
    show_default=True)
@click.option(
    "--min-surviving", "-s", type=int, default=1,
    help="""Stop processing devices when only this number of devices is left for
    this user. Allows to reduce disruption by preserving recently used
    devices/sessions.""",
    show_default=True)
@click.option(
    "--device-id", "-i", type=str, default=None,
    help="""Only search devices with this ID. The other options still apply if
    they're not 0.""",
    show_default=True)
@click.option(
    "--datetime/--timestamp", "--dt/--ts", default=True,
    help="""Display 'last seen date/time' in a human readable format, or as a
    unix timestamp in milliseconds.  [default: datetime].""")
@click.pass_obj
def prune_devices_cmd(helper, user_id, list_only, min_days, min_surviving,
                      device_id, datetime):
    """ Delete devices and invalidate access tokens of a user.

    Deletes devices of a user and invalidates any access token associated with
    them. Starts from deleting the oldest devices, not seen in a number of days,
    which may be abandoned.

    Note that this will affect the encryption and decryption of messages sent by
    other users to this user or to rooms where the user is present.
    """
    devices_data = helper.api.user_devices(user_id)
    if "devices" not in devices_data:
        # Most probably the requested user is not existing, show error and quit.
        helper.output(devices_data)
        raise SystemExit(1)

    devices_todelete = helper.api.user_devices_get_todelete(
        devices_data, min_days, min_surviving, device_id, datetime
    )
    if len(devices_todelete) < 1:
        # We didn't find anything to do.
        if helper.output_format == "human":
            click.echo(f"User {user_id} had no relevant devices to delete.")
        raise SystemExit(0)
    else:
        if helper.output_format == "human":
            keep_count = len(devices_data["devices"]) - len(devices_todelete)
            click.echo("User {} has {} device(s) marked for deletion "
                       "and {} device(s) to be kept alive."
                       .format(user_id, len(devices_todelete), keep_count))

    helper.output(devices_todelete)
    if not list_only:
        devices_todelete_ids = [
            d.get("device_id", None) for d in devices_todelete
        ]
        deleted = helper.api.user_devices_delete(user_id, devices_todelete_ids)
        # We should have received an empty dict
        if len(deleted) > 0:
            helper.log.error(f"Failed deleting user {user_id} "
                             f"devices: {deleted}.")
            raise SystemExit(1)
        if helper.output_format == "human":
            click.echo("User {} devices successfully deleted: {}."
                       .format(user_id, ", ".join(devices_todelete_ids)))


@user.command(name="password")
@click.argument("user_id", type=str)
@click.option(
    "--no-logout", "-n", is_flag=True, default=False,
    help="Don't log user out of all sessions on all devices.")
@click.option(
    "--password", "-p", prompt=True, hide_input=True,
    confirmation_prompt=True, help="New password.")
@click.pass_obj
def password_cmd(helper, user_id, password, no_logout):
    """ Change a user's password.

    To prevent the user from being logged out of all sessions use option -n.
    """
    changed = helper.api.user_password(user_id, password, no_logout)
    if changed is None:
        click.echo("Password could not be reset.")
        raise SystemExit(1)
    if helper.output_format == "human":
        if changed == {}:
            click.echo("Password reset successfully.")
        else:
            click.echo("Synapse returned: {}".format(changed))
    else:
        helper.output(changed)


@user.command()
@click.argument("user_id", type=str)
@click.option(
    "--aliases/--ids", is_flag=True, default=True,
    help="Display rooms as canonical aliases or room ID's.  [default: aliases]")
@click.pass_obj
def membership(helper, user_id, aliases):
    """ List all rooms a user is member of.

    Provide matrix user ID (@user:server) as argument.
    """
    joined_rooms = helper.api.user_membership(user_id, aliases,
                                              helper.matrix_api)
    if joined_rooms is None:
        click.echo("Membership could not be fetched.")
        raise SystemExit(1)

    if helper.output_format == "human":
        click.echo("User is member of {} rooms."
                   .format(joined_rooms["total"]))
        if int(joined_rooms["total"]) != 0:
            helper.output(joined_rooms["joined_rooms"])
    else:
        helper.output(joined_rooms)


@user.command(name="search")
@click.argument("search-term", type=str)
@click.option(
    "--from", "-f", "from_", type=int, default=0, show_default=True,
    help="""Offset user listing by given number. This option is also used
    for pagination.""")
@click.option(
    "--limit", "-l", type=int, default=100, show_default=True,
    help="Maximum amount of users to return.")
@click.pass_context
def user_search_cmd(ctx, search_term, from_, limit):
    """ A shortcut to \'synadm user list -d -g -n <search-term>\'.

    Searches for users by name/matrix-ID, including deactivated users as well as
    guest users. Also, compared to the original command, a case-insensitive
    search is done.
    """
    click.echo("User search results for '{}':".format(search_term.lower()))
    ctx.invoke(list_user_cmd, from_=from_, limit=limit,
               name=search_term.lower(), deactivated=True, guests=True)
    click.echo("User search results for '{}':"
               .format(search_term.capitalize()))
    ctx.invoke(list_user_cmd, from_=from_, limit=limit,
               name=search_term.capitalize(), deactivated=True, guests=True)


@user.command(name="details")
@click.argument("user_id", type=str)
@click.pass_obj
def user_details_cmd(helper, user_id):
    """ View details of a user account.
    """
    user_data = helper.api.user_details(user_id)
    if user_data is None:
        click.echo("User details could not be fetched.")
        raise SystemExit(1)
    helper.output(user_data)


class UserModifyOptionGroup(RequiredAnyOptionGroup):
    @property
    def name_extra(self):
        return []


@user.command()
@click.argument("user_id", type=str)
@optgroup.group(cls=UserModifyOptionGroup)
@optgroup.option(
    "--password-prompt", "-p", is_flag=True,
    help="Set password interactively.")
@optgroup.option(
    "--password", "-P", type=str,
    help="Set password on command line.")
@optgroup.option(
    "--display-name", "-n", type=str,
    help="Set display name. defaults to the value of user_id")
@optgroup.option(
    "--threepid", "-t", type=str, multiple=True, nargs=2,
    help="""Add a third-party identifier. This can be an email address or a
    phone number. Threepids are used for several things: For use when
    logging in, as an alternative to the user id. In the case of email, as
    an alternative contact to help with account recovery, as well as
    to receive notifications of missed messages. Format: medium
    value (eg. --threepid email <user@example.org>). This option can also
    be stated multiple times, i.e. a user can have multiple threepids
    configured.""")
@optgroup.option(
    "--avatar-url", "-v", type=str,
    help="""Set avatar URL. Must be a MXC URI
    (https://matrix.org/docs/spec/client_server/r0.6.0#matrix-content-mxc-uris)
    """)
@optgroup.option(
    "--admin/--no-admin", "-a/-u", default=None,
    help="""Grant user admin permission. Eg user is allowed to use the admin
    API.""", show_default=True,)
@optgroup.option(
    "--activate", "deactivation", flag_value="activate",
    help="""Re-activate user.""")
@optgroup.option(
    "--deactivate", "deactivation", flag_value="deactivate",
    help="""Deactivate user. Use with caution! Deactivating a user
    removes their active access tokens, resets their password, kicks them out
    of all rooms and deletes third-party identifiers (to prevent the user
    requesting a password reset). See also "user deactivate" command.""")
@click.pass_obj
@click.pass_context
def modify(ctx, helper, user_id, password, password_prompt, display_name,
           threepid, avatar_url, admin, deactivation):
    """ Create or modify a local user. Provide matrix user ID (@user:server)
    as argument.
    """
    # sanity checks that can't easily be handled by Click.
    if password_prompt and password:
        click.echo("Use either '-p' or '-P secret', not both.")
        raise SystemExit(1)
    if deactivation == "deactivate" and (password_prompt or password):
        click.echo(
            "Deactivating a user and setting a password doesn't make sense.")
        raise SystemExit(1)

    click.echo("Current user account settings:")
    ctx.invoke(user_details_cmd, user_id=user_id)
    click.echo("User account settings to be modified:")
    for key, value in ctx.params.items():
        if key in ["user_id", "password", "password_prompt"]:  # skip these
            continue
        if key == "threepid":
            if value != ():
                for t_key, t_val in value:
                    click.echo(f"{key}: {t_key} {t_val}")
                    if t_key not in ["email", "msisdn"]:
                        helper.log.warning(
                            f"{t_key} is probably not a supported medium "
                            "type. Threepid medium types according to the "
                            "current matrix spec are: email, msisdn.")
        elif value not in [None, {}, []]:  # only show non-empty (aka changed)
            click.echo(f"{key}: {value}")

    if password_prompt:
        if helper.batch:
            click.echo("Password prompt not available in batch mode. Use -P.")
        else:
            password = click.prompt("Password", hide_input=True,
                                    confirmation_prompt=True)
    elif password:
        click.echo("Password will be set as provided on command line.")
    else:
        password = None
    sure = (
        helper.batch or
        click.prompt("Are you sure you want to modify user? (y/N)",
                     type=bool, default=False, show_default=False)
    )
    if sure:
        modified = helper.api.user_modify(
            user_id, password, display_name, threepid,
            avatar_url, admin, deactivation)
        if modified is None:
            click.echo("User could not be modified.")
            raise SystemExit(1)
        if helper.output_format == "human":
            if modified != {}:
                helper.output(modified)
                click.echo("User successfully modified.")
            else:
                click.echo("Synapse returned: {}".format(modified))
        else:
            helper.output(modified)
    else:
        click.echo("Abort.")


@user.command()
@click.argument("user_id", type=str)
@click.pass_obj
def whois(helper, user_id):
    """ Return information about the active sessions for a specific user
    """
    user_data = helper.api.user_whois(user_id)
    helper.output(user_data)


@user.command(name="media")
@click.argument("user_id", type=str)
@click.option(
    "--from", "-f", "from_", type=int, default=0, show_default=True,
    help="""Offset media listing by given number. This option is also used for
    pagination.""")
@click.option(
    "--limit", "-l", type=int, default=100, show_default=True,
    help="Limit media listing to given number")
@click.option(
    "--sort", "-s", type=click.Choice([
        "media_id", "upload_name", "created_ts", "last_access_ts",
        "media_length", "media_type", "quarantined_by",
        "safe_from_quarantine"]),
    help="""The method by which to sort the returned list of media. If the
    ordered field has duplicates, the second order is always by ascending
    media_id, which guarantees a stable ordering.""")
@click.option(
    "--reverse", "-r", is_flag=True, default=False,
    help="""Direction of media order. If set it will reverse the sort order of
    --order-by method.""")
@click.option(
    "--datetime/--timestamp", "--dt/--ts", default=True,
    help="""Display created and last accessed timestamps in a human readable
    format, or as a unix timestamp in milliseconds.  [default: datetime].""")
@click.pass_obj
def user_media_cmd(helper, user_id, from_, limit, sort, reverse, datetime):
    """ List all local media uploaded by a user.

    Provide matrix user ID (@user:server) as argument.

    Gets a list of all local media that a specific user_id has created. By
    default, the response is ordered by descending creation date and
    ascending media ID. The newest media is on top. You can change the order
    with options --order-by and --reverse.

    Caution. The database only has indexes on the columns media_id, user_id
    and created_ts. This means that if a different sort order is used
    (upload_name, last_access_ts, media_length, media_type, quarantined_by or
    safe_from_quarantine), this can cause a large load on the database,
    especially for large environments
    """
    media = helper.api.user_media(user_id, from_, limit, sort, reverse,
                                  datetime)
    if media is None:
        click.echo("Media could not be fetched.")
        raise SystemExit(1)
    if helper.output_format == "human":
        click.echo("User has uploaded {} media blobs."
                   .format(media["total"]))
        if int(media["total"]) != 0:
            helper.output(media["media"])
        if "next_token" in media:
            click.echo("There are more results available than shown, "
                       "use '--from {}' "
                       "to go to next page (Total results: {})".format(
                           media["next_token"],
                           media["total"]
                       ))
    else:
        helper.output(media)


@user.command(name="login")
@click.argument("user_id", type=str)
@optgroup.group(
    "Token expires",
    cls=MutuallyExclusiveOptionGroup,
    help="")
@optgroup.option(
    "--expire-days", "-d", type=int,
    help="""Expire token after this number of days.""")
@optgroup.option(
    "--expire", type=click.DateTime(),
    help="""Expire token after this point in time. Eg. '2021-01-01', see
    above for available date/time formats.""")
@optgroup.option(
    "--expire-ts", type=int,
    help="""Expire token after this point in time giving a unix
    timestamp in ms.""")
@optgroup.option(
    "--expire-never", is_flag=True, default=False, show_default=True,
    help="""Never expire token.""")
@click.pass_obj
def user_login_cmd(helper, user_id, expire_days, expire, expire_ts,
                   expire_never):
    """Get an access token for a given user.

    Useful for when admins wish to do actions on behalf of a user.

    If no --expire* option is given, a default token expiry time of exactly 1
    day (24h) is used. If it's desired that the token never expires, use
    --expire-never

    This API does not generate a new device for the user, and so will not appear
    in their /devices list, and in general the target user should not be able to
    tell they have been logged in as.

    To expire the token before the expiry date/time is reached, call the
    standard /logout API with the token. Note: The token will expire if the
    admin user calls /logout/all from any of their devices, but the token will
    not expire if the target user does the same.
    """
    if expire_never:
        user_login = helper.api.user_login(user_id, None, None, None)
    elif not expire_days and not expire and not expire_ts:
        user_login = helper.api.user_login(user_id, 1, expire, expire_ts)
    else:
        user_login = helper.api.user_login(user_id, expire_days, expire,
                                           expire_ts)

    if helper.batch:
        if user_login is None:
            raise SystemExit(1)
        helper.output(user_login)
    else:
        click.echo("You are fetching an authentication token of a user, which "
                   "enables you to execute any Matrix command on their behalf. "
                   "Please respect their privacy and know what you are doing! "
                   "Be responsible!\n")
        if user_login is None:
            click.echo(f"Login as user {user_id} not successful.")
            raise SystemExit(1)
        else:
            helper.output(user_login)
