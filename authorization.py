import base64
import random
import string
from urllib import parse
import requests
from flask import request
from requests import PreparedRequest
from config import Config


class Authorization():
    __client_id__ = Config.__client_id__
    __client_secret__ = Config.__client_secret__
    __redirect_uri__ = Config.__redirect_uri__
    __code1__ = None
    __state__ = None
    __access_token__ = None
    __refresh_token__ = None
    __bearer__ = None
    __token_type__ = None
    __scope__ = None
    __expires_in__ = None
    __response_type__ = 'code'
    # encoding client_id+client_secret with base64 encoding
    id = __client_id__ + ':' + __client_secret__
    id_string_bytes = id.encode("ascii")
    base64_bytes = base64.b64encode(id_string_bytes)
    __id_base64_client__ = base64_bytes.decode("ascii")

    @classmethod
    def get_auth_params(cls):
        return {
            'client_id': cls.__client_id__,
            'client_secret': cls.__client_secret__,
            'redirect_url': cls.__redirect_uri__,
            'code1': cls.__code1__,
            'state': cls.__state__,
            'access_token': cls.__access_token__,
            'refresh_token': cls.__refresh_token__,
            'bearer': cls.__bearer__,
            'token_type': cls.__token_type__,
            'scope': cls.__scope__,
            'expires_in': cls.__expires_in__,
            'id_base64_client': cls.__id_base64_client__,
            'response_type': cls.__response_type__
        }

    @classmethod
    async def set_auth_params(cls):
        cls.__code1__ = parse.parse_qs(parse.urlparse(request.url).query)['code'][0]
        cls.__state__ = parse.parse_qs(parse.urlparse(request.url).query)['state'][0]
        # get access token using code & state
        if cls.__code1__:
            res = await cls.get_access_token()
            if 'access_token' in res:
                cls.__access_token__ = res['access_token']
                cls.__refresh_token__ = res['refresh_token']
                cls.__expires_in__ = res['expires_in']
                cls.__token_type__ = res['token_type']
                cls.__scope__ = res['scope']
        return cls.get_auth_params()

    @classmethod
    def initialize_client_credentials(cls):
        # Making a POST request
        url = 'https://accounts.spotify.com/api/token'
        headers = {
            'Authorization': 'Basic ' + cls.__id_base64_client__,
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        params = {'json': True}
        data = {'grant_type': 'client_credentials'}
        r = requests.post(url=url, headers=headers, params=params, data=data)
        return r.json()

    @classmethod
    def initialize_authorization_code(cls, response_type='code'):
        cls.__response_type__ = response_type
        state = ''.join(random.choices(string.ascii_letters, k=16))
        scope = 'user-read-private user-read-email user-top-read playlist-modify-public playlist-modify-private user-library-read'
        # Making a redirect request
        url = 'https://accounts.spotify.com/authorize?'
        params = {
            'response_type': response_type,
            'client_id': cls.__client_id__,
            'scope': scope,
            'redirect_uri': cls.__redirect_uri__,
            'state': state,
            'show_dialog': True
        }
        req = PreparedRequest()
        req.prepare_url(url, params)
        url = req.url
        return url

    @classmethod
    async def get_access_token(cls):
        # Making a POST request
        url = 'https://accounts.spotify.com/api/token'
        headers = {
            'Authorization': 'Basic ' + cls.__id_base64_client__,
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        params = {'json': True}
        data = {
            'grant_type': 'authorization_code',
            'code': cls.__code1__,
            'redirect_uri': cls.__redirect_uri__
        }
        r = requests.post(url=url, headers=headers, params=params, data=data)
        return r.json()

    @classmethod
    def get_refresh_token(cls):
        url = 'https://accounts.spotify.com/api/token'
        headers = {
            'Authorization': 'Basic ' + cls.__id_base64_client__,
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        params = {'json': True}
        data = {
            'grant_type': 'refresh_token',
            'refresh_token': cls.__refresh_token__,
            # 'redirect_uri': 'http://localhost:5000',
            # 'client_id': cls.__client_id__
        }
        r = requests.post(url=url, headers=headers, params=params, data=data)
        res = r.json()
        cls.__access_token__ = res['access_token']
        cls.__expires_in__ = res['expires_in']
        cls.__token_type__ = res['token_type']
        cls.__scope__ = res['scope']
        return res


