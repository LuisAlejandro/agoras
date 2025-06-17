# -*- coding: utf-8 -*-
#
# Please refer to AUTHORS.md for a complete list of Copyright holders.
# Copyright (C) 2022-2023, Agoras Developers.

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import hashlib
import json
import os
import random
import urllib.parse as urlparse
import http.server
import socketserver

import requests
from platformdirs import user_cache_dir

from agoras import __version__


# TikTok API URLs
AUTHORIZE_URL = "https://www.tiktok.com/v2/auth/authorize/"
TOKEN_URL = "https://open.tiktokapis.com/v2/oauth/token/"
CREATOR_INFO_URL = "https://open.tiktokapis.com/v2/post/publish/creator_info/query/"

# HTTP Response codes
RESPONSE_OK = 200
RESPONSE_PARTIAL_CONTENT = 206
RESPONSE_CREATED = 201
RESPONSE_REDIRECT = 302
RESPONSE_ERROR = 400


class TCPServer(socketserver.TCPServer):
    allow_reuse_address = True


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        self.params = {}
        self.username = kwargs.pop('username')
        self.client_key = kwargs.pop('client_key')
        self.client_secret = kwargs.pop('client_secret')
        self.code_verifier = kwargs.pop('code_verifier')
        self.scope = kwargs.pop('scope')
        self.state = kwargs.pop('state')
        super().__init__(*args, **kwargs)

    def do_GET(self):
        parsed_url = urlparse.urlparse(self.path)
        query = urlparse.parse_qs(parsed_url.query)

        if parsed_url.path.startswith('/oauth'):
            print('Authorizing...')
            code_challenge = _sha256_hash(self.code_verifier)
            self.params = {
                'client_key': self.client_key,
                'scope': self.scope,
                'redirect_uri': 'http://127.0.0.1:3456/callback/',
                'state': self.state,
                'response_type': 'code',
                'code_challenge': code_challenge,
                'code_challenge_method': 'S256',
            }
            self.send_response(RESPONSE_REDIRECT)
            self.send_header('Location', f'{AUTHORIZE_URL}?{urlparse.urlencode(self.params)}')
            self.end_headers()

        elif parsed_url.path.startswith('/callback'):
            state = query.get('state', [None])[0]
            code = query.get('code', [None])[0]
            error = query.get('error', [None])[0]

            if error:
                self.send_response(RESPONSE_ERROR)
                self.end_headers()
                self.wfile.write(f'Error: {query.get("error_description", ["Unknown error"])[0]}'.encode())

            if state != self.state:
                self.send_response(RESPONSE_ERROR)
                self.end_headers()
                self.wfile.write('Error: CSRF mismatch'.encode())

            token_response_data = fetch_access_token(code, self.client_key, self.client_secret, self.code_verifier)

            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()

            if 'error' in token_response_data:
                self.wfile.write(f"Error fetching access token: {token_response_data}".encode())
            else:
                self.wfile.write("Authorization workflow successful. You can go back to the terminal console.".encode())
                access_token = token_response_data.get('access_token')
                refresh_token = token_response_data.get('refresh_token')
                original_username = get_username(access_token)

                if original_username != self.username:
                    raise Exception(f'Username mismatch: {original_username} != {self.username}')

                print(f'Username: {original_username}')
                print(f'Access token: {access_token}')
                print(f'Refresh token: {refresh_token}')

                cachedir = user_cache_dir("Agoras", "Agoras")
                cachefile = os.path.join(cachedir, f'tiktok-{self.username}.json')

                with open(cachefile, 'w') as f:
                    f.write(json.dumps({
                        'tiktok_refresh_token': refresh_token,
                    }))

                raise KeyboardInterrupt

        else:
            super().do_GET()


def fetch_access_token(code, client_key, client_secret, code_verifier):
    data = {
        'client_key': client_key,
        'client_secret': client_secret,
        'code': code,
        'grant_type': 'authorization_code',
        'redirect_uri': 'http://127.0.0.1:3456/callback/',
        'code_verifier': code_verifier,
    }
    try:
        res = requests.post(
            TOKEN_URL,
            headers={
                'Content-Type': 'application/x-www-form-urlencoded',
                'User-Agent': f'Agoras/{__version__}',
            },
            data=data)
        response = res.json()
    except Exception as e:
        response = {'error': 'Error', 'error_description': str(e)}

    return response


def refresh(username, refresh_token, client_key, client_secret):
    data = {
        'client_key': client_key,
        'client_secret': client_secret,
        'grant_type': 'refresh_token',
        'refresh_token': refresh_token,
    }
    response = requests.post(
        TOKEN_URL,
        headers={
            'Content-Type': 'application/x-www-form-urlencoded',
            'Cache-Control': 'no-cache',
            'User-Agent': f'Agoras/{__version__}',
        },
        data=data)
    new_refresh_token = response.json().get('refresh_token', refresh_token)
    new_access_token = response.json().get('access_token')
    original_username = get_username(new_access_token)

    if original_username != username:
        raise Exception(f'Username mismatch: {original_username} != {username}')

    print(f'Username: {original_username}')
    print(f'New access token: {new_access_token}')
    print(f'New refresh token: {new_refresh_token}')

    cachedir = user_cache_dir("Agoras", "Agoras")
    cachefile = os.path.join(cachedir, f'tiktok-{original_username}.json')

    with open(cachefile, 'w') as f:
        f.write(json.dumps({
            'tiktok_refresh_token': new_refresh_token,
        }))
    return new_access_token


def _sha256_hash(input_string):
    sha256 = hashlib.sha256()
    sha256.update(input_string.encode())
    return sha256.hexdigest()


def authorize(username, client_key, client_secret):

    if not username:
        raise Exception('No --tiktok-username provided.')

    if not client_key:
        raise Exception('No --tiktok-client-key provided.')

    if not client_secret:
        raise Exception('No --tiktok-client-secret provided.')

    csrf_state = ''.join(random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-._~')
                         for _ in range(16))
    code_verifier = ''.join(random.choice(
        'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-._~') for _ in range(64))

    def handler(*args, **kwargs):
        return Handler(
            *args,
            username=username,
            client_key=client_key,
            client_secret=client_secret,
            code_verifier=code_verifier,
            scope=",".join(['user.info.basic', 'video.upload', 'video.publish']),
            state=csrf_state,
            **kwargs)

    with TCPServer(('', 3456), handler) as httpd:

        print('Open the following URL in your browser:')
        print('http://127.0.0.1:3456/oauth')

        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            pass
        finally:
            httpd.server_close()


def get_username(access_token):
    try:
        res = requests.post(url=CREATOR_INFO_URL, headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json; charset=UTF-8",
            'User-Agent': f'Agoras/{__version__}',
        })
        response = res.json()
        return response["data"]["creator_username"]
    except Exception:
        return None


def get_creator_info(access_token):
    try:
        res = requests.post(url=CREATOR_INFO_URL, headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json; charset=UTF-8",
            'User-Agent': f'Agoras/{__version__}',
        })
        response = res.json()
        return response["data"]
    except Exception:
        return None 