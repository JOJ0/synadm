""" Synapse admin API functions

See https://github.com/matrix-org/synapse/tree/master/docs/admin_api for
documentaiton.
"""

import requests
import json


class Synapse_admin(object):
    """ Synapse API client
    """

    def __init__(self, log, user, token, base_url, admin_path):
        self.log = log
        self.user = user
        self.token = token
        self.base_url = base_url.strip('/')
        self.admin_path = admin_path.strip('/')
        self.headers = {'Accept': 'application/json',
                        'Authorization': 'Bearer ' + self.token
        }

    def _get(self, urlpart):
        url=f'{self.base_url}/{self.admin_path}/{urlpart}'
        self.log.info('_get url: {}\n'.format(url))
        try:
            resp = requests.get(url, headers=self.headers, timeout=7)
            resp.raise_for_status()
            if resp.ok:
                _json = json.loads(resp.content)
                return _json
            else:
                self.log.warning("No valid response from Synapse. Returning None.")
                return None
        except requests.exceptions.HTTPError as errh:
            self.log.error("HTTPError: %s\n", errh)
            #if "Not found" in errh.response.text:
            #    self.log.warning("AcousticBrainz doesn't have this recording yet. Consider submitting it!")
            return None
        except requests.exceptions.ConnectionError as errc:
            self.log.error("ConnectionError: %s\n", errc)
            return None
        except requests.exceptions.Timeout as errt:
            self.log.error("Timeout: %s\n", errt)
            return None
        except requests.exceptions.RequestException as erre:
            self.log.error("RequestException: %s\n", erre)
            return None

    def _post(self, urlpart, post_data, log_post_data=True):
        url=f'{self.base_url}/{self.admin_path}/{urlpart}'
        self.log.info('_post url: {}\n'.format(url))
        if log_post_data:
            self.log.info('_post data: {}\n'.format(post_data))
        try:
            resp = requests.post(url, headers=self.headers, timeout=7, data=post_data)
            resp.raise_for_status()
            if resp.ok:
                _json = json.loads(resp.content)
                return _json
            else:
                self.log.warning("No valid response from Synapse. Returning None.")
                return None
        except requests.exceptions.HTTPError as errh:
            self.log.error("HTTPError: %s\n", errh)
            return None
        except requests.exceptions.ConnectionError as errc:
            self.log.error("ConnectionError: %s\n", errc)
            return None
        except requests.exceptions.Timeout as errt:
            self.log.error("Timeout: %s\n", errt)
            return None
        except requests.exceptions.RequestException as erre:
            self.log.error("RequestException: %s\n", erre)
            return None

    def _put(self, urlpart, put_data, log_put_data=True):
        url=f'{self.base_url}/{self.admin_path}/{urlpart}'
        self.log.info('_put url: {}\n'.format(url))
        if log_put_data:
            self.log.info('_put data: {}\n'.format(put_data))
        try:
            resp = requests.put(url, headers=self.headers, timeout=7, data=put_data)
            resp.raise_for_status()
            if resp.ok:
                _json = json.loads(resp.content)
                return _json
            else:
                self.log.warning("No valid response from Synapse. Returning None.")
                return None
        except requests.exceptions.HTTPError as errh:
            self.log.error("HTTPError: %s\n", errh)
            return None
        except requests.exceptions.ConnectionError as errc:
            self.log.error("ConnectionError: %s\n", errc)
            return None
        except requests.exceptions.Timeout as errt:
            self.log.error("Timeout: %s\n", errt)
            return None
        except requests.exceptions.RequestException as erre:
            self.log.error("RequestException: %s\n", erre)
            return None

    def user_list(self, _from, _limit, _guests, _deactivated,
          _name, _user_id):
        urlpart = f'v2/users?from={_from}&limit={_limit}'
        # optional filters
        if _guests == False:
            urlpart+= f'&guests=false' # true is API default
        elif _guests == True:
            urlpart+= f'&guests=true'
        # no else - fall back to API default if None, which is "true"

        # only add when present, deactivated=false will never be added
        if _deactivated:
            urlpart+= f'&deactivated=true' # false is API default

        # either of both is added, never both, Click MutEx prevents it
        if _name:
            urlpart+= f'&name={_name}'
        if _user_id:
            urlpart+= f'&user_id={_user_id}'
        return self._get(urlpart)

    def user_membership(self, user_id):
        urlpart = f'v1/users/{user_id}/joined_rooms'
        return self._get(urlpart)

    def user_deactivate(self, user_id, gdpr_erase):
        urlpart = f'v1/deactivate/{user_id}'
        data = '{"erase": true}' if gdpr_erase else {}
        return self._post(urlpart, data)

    def user_password(self, user_id, password, no_logout):
        urlpart = f'v1/reset_password/{user_id}'
        data = {"new_password": password}
        if no_logout:
            data.update({"logout_devices": no_logout})
        json_data = json.dumps(data)
        return self._post(urlpart, json_data, log_post_data=False)

    def user_details(self, user_id): # called "Query User Account" in API docs.
        urlpart = f'v2/users/{user_id}'
        return self._get(urlpart)

    def user_modify(self, user_id, password, display_name, threepid, avatar_url,
          admin, deactivation):
        'threepid is a tuple in a tuple'
        urlpart = f'v2/users/{user_id}'
        data = {}
        if password:
            data.update({"password": password})
        if display_name:
            data.update({"displayname": display_name})
        if threepid:
            threep_list = [
                {'medium': k, 'address': i} for k,i in dict(threepid).items()
            ]
            data.update({'threepids': threep_list})
        if avatar_url:
            data.update({"avatar_url": avatar_url})
        if admin:
            data.update({"admin": admin})
        if deactivation == 'deactivate':
            data.update({"deactivated": True})
        if deactivation == 'activate':
            data.update({"deactivated": False})
        json_data = json.dumps(data)
        return self._put(urlpart, json_data, log_put_data=False)

    def room_list(self, _from, limit, name, order_by, reverse):
        urlpart = f'v1/rooms?from={_from}&limit={limit}'
        if name:
            urlpart+= f'&search_term={name}'
        if order_by:
            urlpart+= f'&order_by={order_by}'
        if reverse:
            urlpart+= f'&dir=b'
        return self._get(urlpart)

    def room_details(self, room_id):
        urlpart = f'v1/rooms/{room_id}'
        return self._get(urlpart)

    def room_members(self, room_id):
        urlpart = f'v1/rooms/{room_id}/members'
        return self._get(urlpart)

    def room_delete(self, room_id, new_room_user_id, room_name, message,
          block, no_purge):
        urlpart = f'v1/rooms/{room_id}/delete'
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
        json_data = json.dumps(data)
        return self._post(urlpart, json_data)

    def version(self):
        urlpart = f'v1/server_version'
        return self._get(urlpart)
