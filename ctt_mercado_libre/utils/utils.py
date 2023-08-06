import requests
from urllib.parse import urlencode
from odoo.http import request
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

    def json(self):
        return self.rjson

    def authorize(self):
        params = { 'grant_type' : 'authorization_code', 'client_id' : self.client_id, 'client_secret' : self.client_secret, 'code' : self.tg_code, 'redirect_uri' : self.redirect_uri}
        headers = {'Accept': 'application/json', 'User-Agent': 'My custom agent', 'Content-type':'application/json'}

        response = requests.post(self.host + '/oauth/token', params=urlencode(params), headers=headers)

        if response.status_code == requests.codes.ok:
            data = {}
            response_info = response.json()
            return response_info
        
        else:
            response.raise_for_status()

    def refresh(self):
        params = { 'grant_type': 'refresh_token', 'client_id': self.client_id, 'client_secret': self.client_secret, 'refresh_token': self.refresh_token,}
        headers = {'Accept': 'application/json', 'User-Agent': 'My custom agent', 'Content-type':'application/json'}

        response = requests.post(self.host + '/oauth/token', params=urlencode(params), headers=headers)

        if response.status_code == requests.codes.ok:
            data = {}
            response_info = response.json()
            
            return response_info
        else:
            response.raise_for_status()

    def get(self, path, params={}):
        headers = {
            'Accept': 'application/json', 
            'User-Agent':'My custom agent', 
            'Content-type':'application/json',
            'Authorization': 'Bearer ' + self.access_token
        }
        self.response = requests.get(self.host + path, params=urlencode(params), headers=headers)
        self.rjson = self.response.json()
        return self

    def post(self, path, body=None, params={}):
        headers = {
            'Accept': 'application/json', 
            'User-Agent':'My custom agent', 
            'Content-type':'application/json',
            'Authorization': 'Bearer ' + self.access_token
        }
        if body:
            body = json.dumps(body)
            _logger.warning(body)

        self.response = requests.post(self.host + path, data=body, params=urlencode(params), headers=headers)
        _logger.warning(self.response)
        self.rjson = self.response.json()
        _logger.warning(self.json())
        return self
        
    def upload(self, path, files, params={}):
        headers = {'Accept': 'application/json', 'User-Agent':'My custom agent', 'Content-type':'multipart/form-data'}
        self.response = requests.post(self.host + path, files=files, params=urlencode(params), headers=headers)
        self.rjson = self.response.json()
        return self

    def put(self, path, body=None, params={}):
        headers = {'Accept': 'application/json', 'User-Agent':'My custom agent', 'Content-type':'application/json'}
        if body:
            body = json.dumps(body)

        self.response = requests.put(self.host + path, data=body, params=urlencode(params), headers=headers)
        self.rjson = self.response
        return self
        
    def delete(self, path, params={}):
        headers = {'Accept': 'application/json', 'User-Agent':'My custom agent', 'Content-type':'application/json'}
        self.response = requests.delete(self.host + path, params=params, headers=headers)
        self.rjson = self.response
        return self
        
    def options(self, path, params={}):
        headers = {'Accept': 'application/json', 'User-Agent':'My custom agent', 'Content-type':'application/json'}
        self.response = requests.options(self.host + path, params=urlencode(params), headers=headers)
        self.rjson = self.response
        return self