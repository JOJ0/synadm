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

"""Synapse admin API and regular Matrix API clients

Most API calls defined in this module respect the API's defaults and only pass
what's necessary in the request body.

A fully qualified Matrix user ID looks like this: @user:server, where server
often is a domain name only, e.g @user@example.org

See https://github.com/matrix-org/synapse/tree/master/docs/admin_api for
documentation of the Synapse admin APIs and the Matrix spec at
https://matrix.org/docs/spec/#matrix-apis.
"""

import requests
from http.client import HTTPConnection
import datetime
import json


class ApiRequest:
    """Basic API request handling and helper utilities

    This is subclassed by SynapseAdmin and Matrix
    """
    def __init__(self, log, user, token, base_url, path, timeout, debug):
        """Initialize an APIRequest object

        Args:
            log (logger object): an already initialized logger object
            user (string): the user with access to the API (currently unused).
                This can either be the fully qualified Matrix user ID, or just
                the localpart of the user ID.
            token (string): the API user's token
            base_url (string): URI e.g https://fqdn:port
            path (string): the path to the API endpoint; it's put after
                base_url to form the basis for all API endpoint paths
            timeout (int): requests module timeout used in query method
            debug (bool): enable/disable debugging in requests module
        """
        self.log = log
        self.user = user
        self.token = token
        self.base_url = base_url.strip("/")
        self.path = path.strip("/")
        self.headers = {
            "Accept": "application/json",
            "Authorization": "Bearer " + self.token
        }
        self.timeout = timeout
        if debug:
            HTTPConnection.debuglevel = 1

    def query(self, method, urlpart, params=None, data=None, token=None):
        """Generic wrapper around requests methods

        Handles requests methods, logging and exceptions

        Args:
            urlpart (string): the path to the API endpoint, excluding
                self.base_url and self.path (the part after
                proto://fqdn:port/path).
            params (dict, optional): URL parameters (?param1&paarm2).  Defaults
                to None.
            data (dict, optional): request body used in POST, PUT, DELETE
                requests.  Defaults to None.

        Returns:
            string or None: usually a JSON string containing
                the response of the API; responses that are not 200(OK) (usally
                error messages returned by the API) will also be returned as
                JSON strings; on exceptions the error type and description are
                logged and None is returned.
        """
        url = f"{self.base_url}/{self.path}/{urlpart}"
        self.log.info("Querying %s on %s", method, url)
        if token:
            self.log.debug("Token override! Adjusting headers.")
            self.headers["Authorization"] = "Bearer " + token
        try:
            resp = getattr(requests, method)(
                url, headers=self.headers, timeout=self.timeout,
                params=params, json=data
            )
            if not resp.ok:
                self.log.warning(
                    f"Synapse returned status code {resp.status_code}"
                )
            return resp.json()
        except Exception as error:
            self.log.error("%s while querying Synapse: %s",
                           type(error).__name__, error)
        return None

    def _timestamp_from_days_ago(self, days):
        """Get a unix timestamp in ms from days ago

        Args:
            days (int): number of days

        Returns:
            int: a unix timestamp in milliseconds (ms)
        """
        return int((
            datetime.datetime.now() - datetime.timedelta(days=days)
        ).timestamp() * 1000)

    def _timestamp_from_days_ahead(self, days):
        """Get a unix timestamp in ms for the given number of days ahead

        Args:
            days (int): number of days

        Returns:
            int: a unix timestamp in milliseconds (ms)
        """
        return int((
            datetime.datetime.now() + datetime.timedelta(days=days)
        ).timestamp() * 1000)

    def _timestamp_from_datetime(self, _datetime):
        """Get a unix timestamp in ms from a datetime object

        Args:
            _datetime (datetime object): an object built by datetime.datetime

        Returns:
            int: a unix timestamp in milliseconds (ms)
        """
        return int(_datetime.timestamp()) * 1000

    def _datetime_from_timestamp(self, timestamp):
        """ Get a datetime object from a unix timestamp in ms

        Args:
            timestamp (int): a unix timestamp in milliseconds (ms)

        Returns:
            datetime object: an object built by datetime.datetime
        """
        return datetime.datetime.fromtimestamp(timestamp / 1000)


class Matrix(ApiRequest):
    """ Matrix API client

    Inheritance:
        ApiRequest (object): parent class containing general properties and
            methods for requesting REST API's
    """
    def __init__(self, log, user, token, base_url, matrix_path,
                 timeout, debug):
        """Initialize the Matrix API object

        Args:
            log (logger object): an already initialized logger object
            user (string): the user with access to the Matrix API (currently
                unused); This can either be the fully qualified Matrix user ID,
                or just the localpart of the user ID.
            token (string): the Matrix API user's token
            base_url (string): URI e.g https://fqdn:port
            path (string): the path to the API endpoint; it's put after
                base_url and forms the basis for all API endpoint paths
            timeout (int): requests module timeout used in ApiRequest.query
                method
            debug (bool): enable/disable debugging in requests module
        """
        super().__init__(
            log, user, token,
            base_url, matrix_path,
            timeout, debug
        )
        self.user = user

    def user_login(self, user_id, password):
        """Login as a Matrix user and retrieve an access token

        Args:
            user_id (string): a fully qualified Matrix user ID
            password (string): the Matrix user's password

        Returns:
            string: JSON string containing a token suitable to access the
                Matrix API on the user's behalf, a device_id and some more
                details on Matrix server and user.
        """
        return self.query("post", "client/r0/login", data={
            "password": password,
            "type": "m.login.password",
            "user": f"{user_id}",
            "initial_device_display_name": "synadm matrix login command"
        })

    def raw_request(self, endpoint, method, data, token=None):
        data_dict = {}
        if method != "get":
            self.log.debug("The data we are trying to parse and submit:")
            self.log.debug(data)
            try:  # user provided json might be crap
                data_dict = json.loads(data)
            except Exception as error:
                self.log.error("loading data: %s: %s",
                               type(error).__name__, error)
                return None

        return self.query(method, endpoint, data=data_dict, token=token)

    def server_name(self):
        """Fetch the local server name

        using the API for retrieving public server keys:
        https://matrix.org/docs/spec/server_server/r0.1.4#retrieving-server-keys

        Returns:
            string: the local Matrix server name or None if the query method
                could not fetch it for any reason.
        """
        resp = self.query("get", "key/v2/server")
        if "server_name" not in resp:
            self.log.error("Local server name could not be fetched.")
            return None
        return resp['server_name']


class SynapseAdmin(ApiRequest):
    """Synapse admin API client

    Inheritance:
        ApiRequest (object): parent class containing general properties and
            methods for requesting REST API's
    """
    def __init__(self, log, user, token, base_url, admin_path, timeout, debug):
        """Initialize the SynapseAdmin object

        Args:
            log (logger object): an already initialized logger object
            user (string): an admin-enabled Synapse user (currently unused).
                This can either be the fully qualified Matrix user ID,
                or just the localpart of the user ID. FIXME is that true?
            token (string): the admin user's token
            base_url (string): URI e.g https://fqdn:port
            path (string): the path to the API endpoint; it's put after
                base_url and the basis for all API endpoint paths
            timeout (int): requests module timeout used in ApiRequest.query
                method
            debug (bool): enable/disable debugging in requests module
        """
        super().__init__(
            log, user, token,
            base_url, admin_path,
            timeout, debug
        )
        self.user = user

    def user_list(self, _from, _limit, _guests, _deactivated,
                  _name, _user_id):
        """List and search users

        Args:
            _from (int): offsets user list by this number, used for pagination
            _limit (int): maximum number of users returned, used for pagination
            _guests (bool): enable/disable fetching of guest users
            _deactivated (bool): enable/disable fetching of deactivated users
            _name (string): user name localpart to search for, see Synapse
                admin API docs for details
            _user_id (string): fully qualified Matrix user ID to search for

        Returns:
            string: JSON string containing the found users
        """
        return self.query("get", "v2/users", params={
            "from": _from,
            "limit": _limit,
            "guests": (str(_guests).lower() if isinstance(_guests, bool)
                       else None),
            "deactivated": "true" if _deactivated else None,
            "name": _name,
            "user_id": _user_id
        })

    def user_membership(self, user_id):
        """Get a list of rooms the given user is member of

        Args:
            user_id (string): fully qualified Matrix user ID

        Returns:
            string: JSON string containing the admin API's response or None if
                an exception occured. See Synapse admin API docs for details.
        """
        return self.query("get", f"v1/users/{user_id}/joined_rooms")

    def user_deactivate(self, user_id, gdpr_erase):
        """Delete a given user

        Args:
            user_id (string): fully qualified Matrix user ID
            gdpr_erase (bool): enable/disable gdpr-erasing the user, see
                Synapse admin API docs for details.

        Returns:
            string: JSON string containing the admin API's response or None if
                an exception occured. See Synapse admin API docs for details.
        """
        return self.query("post", f"v1/deactivate/{user_id}", data={
            "erase": gdpr_erase
        })

    def user_password(self, user_id, password, no_logout):
        """Set the user password, and log the user out if requested

        Args:
            user_id (string): fully qualified Matrix user ID
            password (string): new password that should be set
            no_logout (bool): the API defaults to logging out the user after
                password reset via the admin API, this option can be used to
                disable this behaviour.

        Returns:
            string: JSON string containing the admin API's response or None if
            an exception occured. See Synapse admin API docs for details.
        """
        data = {"new_password": password}
        if no_logout:
            data.update({"logout_devices": False})
        return self.query("post", f"v1/reset_password/{user_id}", data=data)

    def user_details(self, user_id):
        """Get information about a given user

        Note that the admin API docs describe this function as "Query User
        Account".

        Args:
            user_id (string): fully qualified Matrix user ID

        Returns:
            string: JSON string containing the admin API's response or None if
                an exception occured. See Synapse admin API docs for details.

        """
        return self.query("get", f"v2/users/{user_id}")

    def user_login(self, user_id, expire_days, expire, _expire_ts):
        """Get an access token that can be used to authenticate as that user.

        If one of the args expire_days, expire or _expire_ts is set, the
        valid_until_ms field will be sent to the API endpoint. If this is not
        the case the default of the API would be used. At the time of writing,
        this would be that tokens never expire.

        Note: If this method is called by the CLI frontend code
        (synadm.cli.user.user_login_cmd), a default expiry date of 1 day (24h)
        is passed.

        Args:
            user_id (string): fully qualified Matrix user ID
            expire_days (int): token should expire after this number of days
            expire (datetime): token should expire after this date/time - a
                datetime object (e.g. as generated by Click.DateTime())
            _expire_ts (int):  token should expire after this date/time - a
                unix timestamp in ms.
        Returns:
            string: JSON string containing the admin API's response or None if
            an exception occured. See Synapse admin API docs for details.
        """
        expire_ts = None
        if expire_days:
            self.log.debug("Received expire_days: %s", expire_days)
            expire_ts = self._timestamp_from_days_ahead(expire_days)
        elif expire:
            self.log.debug("Received expire: %s", expire)
            expire_ts = self._timestamp_from_datetime(expire)
        elif _expire_ts:
            self.log.debug("Received expire_ts: %s",
                           _expire_ts)
            expire_ts = _expire_ts  # Click checks for int already

        data = {}
        if expire_ts is not None:
            data.update({
                "valid_until_ms": expire_ts,
            })
            self.log.info("Token expiry date set to timestamp: %d,",
                          expire_ts)
            self.log.info("which is the date/time: %s",
                          self._datetime_from_timestamp(expire_ts))
        else:
            self.log.info("Token will never expire.")

        return self.query("post", f"v1/users/{user_id}/login", data=data)

    def user_modify(self, user_id, password, display_name, threepid,
                    avatar_url, admin, deactivation):
        """ Create or update information about a given user

        Threepid should be passed as a tuple in a tuple
        """
        data = {}
        if password:
            data.update({"password": password})
        if display_name:
            data.update({"displayname": display_name})
        if threepid:
            data.update({"threepids": [
                {"medium": k, "address": i} for k, i in dict(threepid).items()
            ]})
        if avatar_url:
            data.update({"avatar_url": avatar_url})
        if admin:
            data.update({"admin": admin})
        if deactivation == "deactivate":
            data.update({"deactivated": True})
        if deactivation == "activate":
            data.update({"deactivated": False})
        return self.query("put", f"v2/users/{user_id}", data=data)

    def user_whois(self, user_id):
        """ Return information about the active sessions for a specific user
        """
        return self.query("get", f"v1/whois/{user_id}")

    def room_join(self, room_id_or_alias, user_id):
        """ Allow an administrator to join an user account with a given user_id
        to a room with a given room_id_or_alias
        """
        data = {"user_id": user_id}
        return self.query("post", f"v1/join/{room_id_or_alias}", data=data)

    def room_list(self, _from, limit, name, order_by, reverse):
        """ List and search rooms
        """
        return self.query("get", "v1/rooms", params={
            "from": _from,
            "limit": limit,
            "search_term": name,
            "order_by": order_by,
            "dir": "b" if reverse else None
        })

    def room_details(self, room_id):
        """ Get details about a room
        """
        return self.query("get", f"v1/rooms/{room_id}")

    def room_members(self, room_id):
        """ Get a list of room members
        """
        return self.query("get", f"v1/rooms/{room_id}/members")

    def room_delete(self, room_id, new_room_user_id, room_name, message,
                    block, no_purge):
        """ Delete a room and purge it if requested
        """
        data = {
            "block": block,  # data with proper defaults from cli
            "purge": not bool(no_purge)  # should go here
        }
        # everything else is optional and shouldn't even exist in post body
        if new_room_user_id:
            data.update({"new_room_user_id": new_room_user_id})
        if room_name:
            data.update({"room_name": room_name})
        if message:
            data.update({"message": message})
        return self.query("delete", f"v1/rooms/{room_id}", data=data)

    def room_make_admin(self, room_id, user_id):
        """ Grant a user room admin permission. If the user is not in the room,
        and it is not publicly joinable, then invite the user.
        """
        data = {}
        if user_id:
            data.update({"user_id": user_id})
        return self.query("post", f"v1/rooms/{room_id}/make_room_admin",
                          data=data)

    def room_media_list(self, room_id):
        """ Get a list of known media in an (unencrypted) room.
        """
        return self.query("get", f"v1/room/{room_id}/media")

    def media_quarantine(self, server_name, media_id):
        """ Quarantine a single piece of local or remote media
        """
        return self.query(
            "post", f"v1/media/quarantine/{server_name}/{media_id}/", data={}
        )

    def room_media_quarantine(self, room_id):
        """ Quarantine all local and remote media in a room
        """
        return self.query(
            "post", f"v1/room/{room_id}/media/quarantine", data={}
        )

    def user_media_quarantine(self, user_id):
        """ Quarantine all local and remote media of a user
        """
        return self.query(
            "post", f"v1/user/{user_id}/media/quarantine", data={}
        )

    def user_media(self, user_id, _from, limit, order_by, reverse):
        """ Get a user's uploaded media
        """
        return self.query("get", f"v1/users/{user_id}/media", params={
            "from": _from,
            "limit": limit,
            "order_by": order_by,
            "dir": "b" if reverse else None
        })

    def media_delete(self, server_name, media_id):
        """ Delete a specific (local) media_id
        """
        return self.query(
            "delete", f"v1/media/{server_name}/{media_id}/", data={}
        )

    def media_delete_by_date_or_size(self, server_name, before_days, before,
                                     _before_ts, _size_gt, delete_profiles):
        """ Delete local media by date and/or size FIXME and/or?
        """
        if before_days:
            self.log.debug("Received --before-days: %s", before_days)
            before_ts = self._timestamp_from_days_ago(before_days)
        elif before:
            self.log.debug("Received --before: %s", before)
            before_ts = self._timestamp_from_datetime(before)
        elif _before_ts is not None:  # Could be 0 if it's an older server ;-)
            self.log.debug("Received --before-ts: %s",
                           _before_ts)
            before_ts = _before_ts  # Click checks for int already
        else:
            self.log.debug("Something wrong in click FIXME")

        self.log.info("Deleting local media older than timestamp: %d,",
                      before_ts)
        self.log.info("which is the date: %s",
                      self._datetime_from_timestamp(before_ts))
        params = {
            "server_name": server_name,
        }
        if before_ts is not None:
            params.update({
                "before_ts": before_ts,
            })
        if _size_gt:
            size_gt = _size_gt * 1024
            self.log.info("Deleting local media greater than %d bytes,",
                          size_gt)
            params.update({
                "size_gt": size_gt
            })
        if delete_profiles:
            params.update({
                "keep_profiles": "false"
            })
        return self.query(
            "post", f"v1/media/{server_name}/delete", data={}, params=params
        )

    def media_protect(self, media_id):
        """ Protect a single piece of local or remote media

        from being quarantined
        """
        return self.query(
            "post", f"v1/media/protect/{media_id}/", data={}
        )

    def purge_media_cache(self, before_days, before, _before_ts):
        """ Purge old cached remote media
        """
        if before_days:
            self.log.debug("Received --before-days: %s", before_days)
            before_ts = self._timestamp_from_days_ago(before_days)
        if before:
            self.log.debug("Received --before: %s", before)
            before_ts = self._timestamp_from_datetime(before)
        if _before_ts:
            self.log.debug("Received --before-ts: %s",
                           _before_ts)
            before_ts = _before_ts  # Click checks for int already

        self.log.info("Purging cached remote media older than timestamp: %d,",
                      before_ts)
        self.log.info("which is the date: %s",
                      self._datetime_from_timestamp(before_ts))

        return self.query(
            "post", "v1/purge_media_cache", data={}, params={
                "before_ts": str(before_ts)
            }
        )

    def version(self):
        """ Get the server version
        """
        return self.query("get", "v1/server_version")

    def group_delete(self, group_id):
        """ Delete a local group (community)
        """
        return self.query("post", f"v1/delete_group/{group_id}")

    def purge_history(self, room_id, before_event_id, before_days, before,
                      _before_ts, delete_local):
        """ Purge room history
        """
        before_ts = None
        if before_days:
            self.log.debug("Received --before-days: %s", before_days)
            before_ts = self._timestamp_from_days_ago(before_days)
        elif before:
            self.log.debug("Received --before: %s", before)
            before_ts = self._timestamp_from_datetime(before)
        elif _before_ts:
            self.log.debug("Received --before-ts: %s",
                           _before_ts)
            before_ts = _before_ts  # Click checks for int already
        elif before_event_id:
            self.log.debug("Received --event-id: %s",
                           before_event_id)

        data = {}
        if before_ts is not None:
            data.update({
                "purge_up_to_ts": before_ts,
            })
            self.log.info("Purging history older than timestamp: %d,",
                          before_ts)
            self.log.info("which is the date/time: %s",
                          self._datetime_from_timestamp(before_ts))
        elif before_event_id:
            data.update({
                "purge_up_to_event_id": before_event_id,
            })

        if delete_local:
            data.update({
                "delete_local_events": True,
            })

        return self.query("post", f"v1/purge_history/{room_id}", data=data)

    def purge_history_status(self, purge_id):
        """ Get status of a recent history purge

        The status will be one of active, complete, or failed.
        """
        return self.query("get", f"v1/purge_history_status/{purge_id}")

    def regtok_list(self, valid, readable_expiry):
        """ List registration tokens

        Args:
            valid (bool): List only valid (if True) or invalid (if False)
                tokens. Default is to list all tokens regardless of validity.
            readable_expiry (bool): If True, replace the expiry_time field with
                a human readable datetime. If False, expiry_time will be a unix
                timestamp.

        Returns:
            string: JSON string containing the admin API's response or None if
                an exception occured. See Synapse admin API docs for details.

        """
        result = self.query("get", "v1/registration_tokens", params={
            "valid": (str(valid).lower() if isinstance(valid, bool) else None)
        })

        # Change expiry_time to a human readable format if requested
        if readable_expiry and result is not None and "registration_tokens" in result:
            for i, regtok in enumerate(result["registration_tokens"]):
                expiry_time = regtok["expiry_time"]
                if expiry_time is not None:
                    result["registration_tokens"][i][
                        "expiry_time"
                    ] = self._datetime_from_timestamp(expiry_time).strftime(
                        "%Y-%m-%d %H:%M:%S"
                    )

        return result

    def regtok_details(self, token, readable_expiry):
        """ Get details about the given registration token

        Args:
            token (string): The registration token in question
            readable_expiry (bool): If True, replace the expiry_time field with
                a human readable datetime. If False, expiry_time will be a unix
                timestamp.

        Returns:
            string: JSON string containing the admin API's response or None if
                an exception occured. See Synapse admin API docs for details.

        """
        result = self.query("get", f"v1/registration_tokens/{token}")

        # Change expiry_time to a human readable format if requested
        if readable_expiry and result is not None:
            if result.get("expiry_time") is not None:
                result["expiry_time"] = self._datetime_from_timestamp(
                    result["expiry_time"]
                ).strftime("%Y-%m-%d %H:%M:%S")

        return result

    def regtok_new(self, token, length, uses_allowed, expiry_ts, expire_at):
        """ Create a new registration token

        Args:
            token (string): Registration token to create. Default is randomly
                generated by the server.
            length (int): The length of the token to generate if the token is
                not provided.
            uses_allowed (int): The number of times the token can be used to
                complete a registration before it becomes invalid.
            expiry_ts (int): The latest time the registration token is valid.
                Given as the number of milliseconds since
                1970-01-01 00:00:00 UTC.
            expire_at (click.DateTime): The latest time the registration token
                is valid.

        Returns:
            string: JSON string containing the admin API's response or None if
                an exception occured. See Synapse admin API docs for details.

        """
        data = {
            "length": length,
            "uses_allowed": uses_allowed,
        }

        if expiry_ts:
            self.log.debug(f"Received --expiry-ts: {expiry_ts}")
            data["expiry_time"] = expiry_ts
        elif expire_at:
            self.log.debug(f"Received --expire-at: {expire_at}")
            data["expiry_time"] = self._timestamp_from_datetime(expire_at)
        else:
            data["expiry_time"] = None

        # The token cannot be null, it must be a string
        if isinstance(token, str):
            data["token"] = token

        return self.query("post", "v1/registration_tokens/new", data=data)

    def regtok_update(self, token, uses_allowed, expiry_ts, expire_at):
        """ Update a registration token

        Args:
            token (string): Registration token to update.
            uses_allowed (int): The number of times the token can be used to
                complete a registration before it becomes invalid.
            expiry_ts (int): The latest time the registration token is valid.
                Given as the number of milliseconds since
                1970-01-01 00:00:00 UTC. -1 indicates no expiry.
            expire_at (click.DateTime): The latest time the registration token
                is valid.

        Returns:
            string: JSON string containing the admin API's response or None if
                an exception occured. See Synapse admin API docs for details.

        """
        # If uses_allowed or expiry time were not provided by the user,
        # do not add the corresponding parameter to the request so that
        # the server will not modify its value.
        data = {}

        if uses_allowed == -1:
            # A null value indicates unlimited uses
            data["uses_allowed"] = None
        elif uses_allowed is not None:
            data["uses_allowed"] = uses_allowed

        if expiry_ts:
            self.log.debug(f"Received --expiry-ts: {expiry_ts}")
            if expiry_ts == -1:
                # A null value indicates no expiry
                data["expiry_time"] = None
            else:
                data["expiry_time"] = expiry_ts
        elif expire_at:
            self.log.debug(f"Received --expire-at: {expire_at}")
            data["expiry_time"] = self._timestamp_from_datetime(expire_at)

        return self.query("put", f"v1/registration_tokens/{token}", data=data)

    def regtok_delete(self, token):
        """ Delete a registration token

        Args:
            token (string): The registration token to delete

        Returns:
            string: JSON string containing the admin API's response or None if
                an exception occured. See Synapse admin API docs for details.

        """
        return self.query("delete", f"v1/registration_tokens/{token}")
