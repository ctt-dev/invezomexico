import requests
from urllib.parse import urlencode
import json
import logging
_logger = logging.getLogger(__name__)

class MeliApi():

    AUTH_URL = "https://auth.mercadolibre.com.mx/authorization"

    host = "https://api.mercadolibre.com"

    response = ""
    code = ""
    rjson = {}

    user = {}

    def __init__(self, dict):
        self.tg_code = None
        self.access_token = None
        self.refresh_token = None
        self.redirect_uri = None

        for key, value in dict.items():
            setattr(self, key, value)

    def authorize(self):
        params = { 'grant_type' : 'authorization_code', 'client_id' : self.client_id, 'client_secret' : self.client_secret, 'code' : self.tg_code, 'redirect_uri' : self.redirect_uri}
        headers = {'Accept': 'application/json', 'User-Agent': 'My custom agent', 'Content-type':'application/json'}

        response = requests.post(self.host + '/oauth/token', params=urlencode(params), headers=headers)

        if response.status_code == requests.codes.ok:
            data = {}
            response_info = response.json()
            data['access_token'] = response_info['access_token']
            data['refresh_token'] = response_info['refresh_token']

            return data
        else:
            response.raise_for_status()

