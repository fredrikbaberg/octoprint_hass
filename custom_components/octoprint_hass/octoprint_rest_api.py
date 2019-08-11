# -*- coding: utf-8 -*-

"""Main module."""

import time
import requests


class OctoPrint():
    """ Class for OctoPrint communication """
    def __init__(self, host, port, path='/'):
        self.base_url = 'http://{}:{}{}'.format(host, port, path)
        self.headers = {}
        self.api_key = None
        self.connected = False

    def _set_api_key(self, key):
        """ Set API key and header internally. """
        self.api_key = key
        self.headers = {
            'X-Api-Key': self.api_key
        }
        return True

    async def get_api_key(self, app_name, user_name=None, timeout=9):
        """Retrieve API key, which is then stored locally.

        Parameters:
            app_name (str): Application name in OctoPrint
            user_name (str): User who should accept request (default is anyone)
            timeout (int): Timeout for server in seconds, default is 9.

        Returns:
            bool: boolean indicating success or failure.
        """
        try:
            response = requests.get(
                self.base_url+'plugin/appkeys/probe',
                headers=self.headers,
                timeout=timeout
            )
        except requests.exceptions.ReadTimeout:
            raise requests.exceptions.ReadTimeout(
                "Could not connect to server, no response"
            )
        except requests.exceptions.ConnectionError:
            raise requests.exceptions.ConnectionError(
                "Could not connect to server, connection refused"
            )
        # If response status code is 204, can continue.
        if response.status_code == 204:
            response = requests.post(
                url=self.base_url+'plugin/appkeys/request',
                headers=self.headers,
                json={
                    'app': app_name,
                    'user': user_name
                },
                timeout=timeout
            )
            # If response status code is 201, token is valid.
            if response.status_code == 201:
                app_token = response.json()['app_token']
                # Request API key
                response = requests.get(
                    self.base_url+'plugin/appkeys/request/'+app_token,
                    headers=self.headers,
                    timeout=timeout
                )
                # Wait for user to accept token.
                while response.status_code == 202:
                    response = requests.get(
                        self.base_url+'plugin/appkeys/request/'+app_token,
                        headers=self.headers,
                        timeout=timeout
                    )
                    time.sleep(1.0)
                    if response.status_code == 200:
                        self._set_api_key(response.json()['api_key'])
                        self.connected = True
                        return True
                    elif response.status_code == 404:
                        raise Exception("User denied access")
            else:
                raise Exception("User not created")
        else:
            raise Exception(
                "Instance does not seem to support Application Keys Plugin"
            )
        return False

    def deregister(self):
        """ Remove API key from OctoPrint instance """
        try:
            response = requests.post(
                url=self.base_url+'api/plugin/appkeys',
                headers=self.headers,
                json={
                    "command": "revoke",
                    "key": self.api_key
                },
                timeout=1
            )
            if response.status_code == 204:
                # Successfully removed API key.
                self.connected = False
                return True
        except requests.exceptions.ConnectionError:
            print("Could not connect.")
        return False

    def retrieve_appkeys(self):
        try:
            return requests.get(
                self.base_url+'api/plugin/appkeys',
                headers=self.headers,
                timeout=9
            ).json()
        except ValueError:
            return False

    def get_printer_version(self):
        try:
            return requests.get(
                url=self.base_url+'api/version',
                headers=self.headers,
                timeout=9
            ).json()
        except ValueError:
            return False

    def get_printer_status(self):
        """ Retrieve printer status """
        try:
            return requests.get(
                url=self.base_url+'api/printer',
                headers=self.headers,
                timeout=9
            ).json()
        except ValueError:
            return False

    def get_printer_connection(self):
        """ Retrieve printer connections """
        try:
            return requests.get(
                url=self.base_url+'api/connection',
                headers=self.headers,
                timeout=9
            ).json()
        except ValueError:
            return False

    def get_printer_files(self):
        """ Retrieve printer files """
        try:
            return requests.get(
                url=self.base_url+'api/files?recursive=true',
                headers=self.headers,
                timeout=9
            ).json()
        except ValueError:
            return False

    def get_printer_job(self):
        """ Retrieve printer job information """
        try:
            return requests.get(
                url=self.base_url+'api/job',
                headers=self.headers,
                timeout=9
            ).json()
        except ValueError:
            return False

    def pause_print(self):
        """ Pause print """
        if self.connected:
            try:
                return requests.post(
                    url=self.base_url+'api/job',
                    headers=self.headers,
                    json={
                        'command': 'pause',
                        'action': 'pause'
                    },
                    timeout=9
                )
            except requests.exceptions.ConnectionError:
                print("Connection refused.")
                return False
        return False

    def resume_print(self):
        """ Resume print """
        if self.connected:
            try:
                return requests.post(
                    url=self.base_url+'api/job',
                    headers=self.headers,
                    json={
                        'command': 'pause',
                        'action': 'resume'
                    },
                    timeout=9
                )
            except requests.exceptions.ConnectionError:
                print("Connection refused.")
                return False
        return False

    def get_printer_tool_state(self):
        """ Get printer tool state """
        try:
            return requests.get(
                url=self.base_url+'api/printer/tool',
                headers=self.headers,
                timeout=9
            ).json()
        except ValueError:
            return False

    def get_printer_bed_state(self):
        """ Get printer tool state """
        try:
            return requests.get(
                url=self.base_url+'api/printer/bed',
                headers=self.headers,
                timeout=9
            ).json()
        except ValueError:
            return False

    def get_printer_chamber_state(self):
        """ Get printer tool state """
        try:
            return requests.get(
                url=self.base_url+'api/printer/chamber',
                headers=self.headers,
                timeout=9
            ).json()
        except ValueError:
            return False

    def get_printer_sd_state(self):
        """ Get printer tool state """
        try:
            return requests.get(
                url=self.base_url+'api/printer/sd',
                headers=self.headers,
                timeout=9
            ).json()
        except ValueError:
            return False

    def get_printer_profiles(self):
        """ Get printer profiles """
        try:
            return requests.get(
                url=self.base_url+'api/printerprofiles',
                headers=self.headers,
                timeout=9
            ).json()
        except ValueError:
            return False

    def get_printer_settings(self):
        """ Get printer profiles """
        try:
            return requests.get(
                url=self.base_url+'api/settings',
                headers=self.headers,
                timeout=9
            ).json()
        except ValueError:
            return False

    def set_printer_settings(self):
        """ Set settings for OctoPrint """
        return requests.post(
            url=self.base_url+'api/settings',
            headers=self.headers,
            json={
                'appearance': {
                    'color': 'green'
                }
            },
            timeout=9
        )

    def get_slicing(self):
        """ Get slicers and slicing profiles """
        try:
            return requests.get(
                url=self.base_url+'api/slicing',
                headers=self.headers,
                timeout=9
            ).json()
        except ValueError:
            return False

    def get_system_commands(self):
        """ Get slicers and slicing profiles """
        try:
            return requests.get(
                url=self.base_url+'api/system/commands',
                headers=self.headers,
                timeout=9
            ).json()
        except ValueError:
            return False

    def get_timelapse(self):
        """ Retrieve a list of timelapses and the current config """
        try:
            return requests.get(
                url=self.base_url+'api/timelapse',
                headers=self.headers,
                timeout=9
            ).json()
        except ValueError:
            return False
