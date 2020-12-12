""" Synapse admin API functions

See https://github.com/matrix-org/synapse/tree/master/docs/admin_api for
documentaiton.
"""

import requests


class Synapse_admin(object):
    """ Synapse API client
    """

    def __init__(self, log, user, token, base_url, admin_path):
        self.log = log
        self.user = user
        self.token = token
        self.base_url = base_url.strip("/")
        self.admin_path = admin_path.strip("/")
        self.headers = {
            "Accept": "application/json",
            "Authorization": "Bearer " + self.token
        }

    def query(self, method, urlpart, params=None, data=None):
        url=f"{self.base_url}/{self.admin_path}/{urlpart}"
        self.log.info("{} url: {}\n".format(method, url))
        try:
            resp = getattr(requests, method)(
                url, json=data, headers=self.headers, params=params, timeout=7
            )
            resp.raise_for_status()
            if resp.ok:
                return resp.json()
            else:
                self.log.warning("No valid response from Synapse. Returning None.")
                return None
        except Exception as error:
            self.log.error("%s while querying synapse: %s", type(error).__name__, error)
            return None

    def user_list(self, _from, _limit, _guests, _deactivated,
          _name, _user_id):
        return self.query("get", "v2/users", params={
            "from": _from,
            "limit": _limit,
            "guests": str(_guests).lower() if type(_guests) is bool else None,
            "deactivated": "true" if _deactivated else None,
            "name": _name,
            "user_id": _user_id
        })

    def user_membership(self, user_id):
        return self.query("get", f"v1/users/{user_id}/joined_rooms")

    def user_deactivate(self, user_id, gdpr_erase):
        return self.query("post", f"v1/deactivate/{user_id}", data={
            "erase": gdpr_erase
        })

    def user_password(self, user_id, password, no_logout):
        data = {"new_password": password}
        if no_logout:
            data.update({"logout_devices": no_logout})
        return self.query("post", f"v1/reset_password/{user_id}", data=data)

    def user_details(self, user_id): # called "Query User Account" in API docs.
        return self.query("get", f"v2/users/{user_id}")

    def user_modify(self, user_id, password, display_name, threepid, avatar_url,
          admin, deactivation):
        """ threepid is a tuple in a tuple
        """
        data = {}
        if password:
            data.update({"password": password})
        if display_name:
            data.update({"displayname": display_name})
        if threepid:
            data.update({"threepids": [
                {"medium": k, "address": i} for k,i in dict(threepid).items()
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
        return self.query("get", "v1/rooms", params={
            "from": _from,
            "limit": limit,
            "search_term": name,
            "order_by": order_by,
            "dir": "b" if reverse else None
        })

    def room_details(self, room_id):
        return self.query("get", f"v1/rooms/{room_id}")

    def room_members(self, room_id):
        return self.query("get", f"v1/rooms/{room_id}/members")

    def room_delete(self, room_id, new_room_user_id, room_name, message,
          block, no_purge):
        purge = False if no_purge else True
        data = {
            "block": block, # data with proper defaults from cli
            "purge": purge  # should go here
        }
        # everything else is optional and shouldn't even exist in post body
        if new_room_user_id:
            data.update({"new_room_user_id": new_room_user_id})
        if room_name:
            data.update({"room_name": room_name})
        if message:
            data.update({"message": message})
        return self.query("post", f"v1/rooms/{room_id}/delete", data=data)

    def version(self):
        return self.query("get", "v1/server_version")
