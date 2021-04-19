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

""" Synapse admin API functions

See https://github.com/matrix-org/synapse/tree/master/docs/admin_api for
documentaiton.
"""

import requests
from http.client import HTTPConnection
import datetime


class ApiRequest:
    """ Basic API request handling and helper utilities
    """
    def __init__(self, log, user, token, base_url, path, timeout, debug):
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

    def query(self, method, urlpart, params=None, data=None):
        """ Generic wrapper around requests methods, handles logging
        and exceptions
        """
        url = f"{self.base_url}/{self.path}/{urlpart}"
        self.log.info("Querying %s on %s", method, url)
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

    def _timestamp_from_days(self, days):
        """ Get a unix timestamp in ms from days ago
        """
        return int((
            datetime.datetime.now() - datetime.timedelta(days=days)
        ).timestamp() * 1000)

    def _timestamp_from_datetime(self, _datetime):
        """ Get a unix timestamp in ms from a datetime object
        """
        return int(_datetime.timestamp()) * 1000

    def _datetime_from_timestamp(self, timestamp):
        """ Get a datetime object from a unix timestamp in ms int
        """
        return datetime.datetime.fromtimestamp(timestamp / 1000)


class Matrix(ApiRequest):
    """ Matrix API client
    """
    def __init__(self, log, user, token, base_url, matrix_path,
                 timeout, debug):
        super().__init__(
            log, user, token,
            base_url, matrix_path,
            timeout, debug
        )
        self.user = user

    def user_login(self, user_id, password):
        return self.query("get", f"client/r0/login/{user_id}", data={
            "password": password,
            "type": "m.login.password",
            "user": f"{user_id}"
        })


class SynapseAdmin(ApiRequest):
    """ Synapse admin API client
    """

    def __init__(self, log, user, token, base_url, admin_path, timeout, debug):
        super().__init__(
            log, user, token,
            base_url, admin_path,
            timeout, debug
        )
        self.user = user

    def user_list(self, _from, _limit, _guests, _deactivated,
                  _name, _user_id):
        """ List and search users
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
        """ Get a given user room list
        """
        return self.query("get", f"v1/users/{user_id}/joined_rooms")

    def user_deactivate(self, user_id, gdpr_erase):
        """ Delete a given user
        """
        return self.query("post", f"v1/deactivate/{user_id}", data={
            "erase": gdpr_erase
        })

    def user_password(self, user_id, password, no_logout):
        """ Set the user password, and log the user out if requested
        """
        data = {"new_password": password}
        if no_logout:
            data.update({"logout_devices": False})
        return self.query("post", f"v1/reset_password/{user_id}", data=data)

    def user_details(self, user_id):
        """ Get information about a given user

        Called "Query User Account" in API docs.
        """
        return self.query("get", f"v2/users/{user_id}")

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
        return self.query("post", f"v1/rooms/{room_id}/delete", data=data)

    def room_make_admin(self, room_id, user_id):
        """ Grant a user room admin permission. If the user is not in the room,
        and it is not publicly joinable, then invite the user.
        """
        data = {}
        if user_id:
            data.update({"user_id": user_id})
        return self.query("post", f"v1/rooms/{room_id}/make_room_admin", data=data)

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
            before_ts = self._timestamp_from_days(before_days)
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
            before_ts = self._timestamp_from_days(before_days)
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
            before_ts = self._timestamp_from_days(before_days)
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