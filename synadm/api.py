""" Synapse admin API functions

See https://github.com/matrix-org/synapse/tree/master/docs/admin_api for
documentaiton.
"""

import requests


class SynapseAdmin:
    """ Synapse API client
    """

    def __init__(self, log, user, token, base_url, admin_path, timeout):
        self.log = log
        self.user = user
        self.token = token
        self.base_url = base_url.strip("/")
        self.admin_path = admin_path.strip("/")
        self.headers = {
            "Accept": "application/json",
            "Authorization": "Bearer " + self.token
        }
        self.timeout = timeout

    def query(self, method, urlpart, params=None, data=None):
        """ Generic wrapper around requests methods, handles logging
        and exceptions
        """
        url = f"{self.base_url}/{self.admin_path}/{urlpart}"
        self.log.info("Querying %s on %s", method, url)
        try:
            resp = getattr(requests, method)(
                url, headers=self.headers, timeout=self.timeout,
                params=params, json=data
            )
            resp.raise_for_status()
            if resp.ok:
                return resp.json()
            self.log.warning("No valid response from Synapse")
        except Exception as error:
            self.log.error("%s while querying Synapse: %s",
                           type(error).__name__, error)
        return None

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
        """ Set the user password, and logs the user out if requested
        """
        data = {"new_password": password}
        if no_logout:
            data.update({"logout_devices": no_logout})
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

    def media_delete(self, server_name, media_id):
        """ Delete a specific (local) media_id
        """
        return self.query(
            "delete", f"v1/media/{server_name}/{media_id}/", data={}
        )

    def media_delete_by_date_or_size(self, server_name, before_ts,
                                     size_gt=None, keep_profiles=None):
        """ Delete local media by date and/or size FIXME and/or?
        """
        return self.query(
            "post", f"v1/media/{server_name}/delete", data={}, params={
                "server_name": server_name,
                "before_ts": before_ts,
                "size_gt": size_gt if size_gt else None,
                "keep_profiles": "false" if keep_profiles is False else None
            }
        )

    def purge_remote_media(self, user_id, before_ts):
        """ Purge old cached remote media
        """
        return self.query(
            "post", f"v1/purge_media_cache/{before_ts}", data={}, params={
                "before_ts": before_ts
            }
        )

    def version(self):
        """ Get the server version
        """
        return self.query("get", "v1/server_version")
