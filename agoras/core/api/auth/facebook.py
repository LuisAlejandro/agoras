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

import asyncio
import webbrowser
from typing import Optional

from authlib.integrations.requests_client import OAuth2Session

from .base import BaseAuthManager
from ..clients.facebook import FacebookAPIClient


def facebook_compliance_fix(session):
    """
    Facebook compliance fix for non-standard OAuth2 implementation.
    Facebook uses 'fb_exchange_token' instead of standard 'refresh_token' grant type.
    """
    def _fix_refresh_request(url, headers, body):
        # Convert standard refresh_token request to Facebook's fb_exchange_token format
        if 'grant_type=refresh_token' in body:
            # Extract refresh_token from body
            import urllib.parse
            params = urllib.parse.parse_qs(body)
            refresh_token = params.get('refresh_token', [None])[0]

            if refresh_token:
                # Replace with Facebook's custom grant type
                new_params = {
                    'grant_type': 'fb_exchange_token',
                    'client_id': session.client_id,
                    'client_secret': session.client_secret,
                    'fb_exchange_token': refresh_token,
                }
                body = urllib.parse.urlencode(new_params)

        return url, headers, body

    session.register_compliance_hook('refresh_token_request', _fix_refresh_request)
    return session


class FacebookAuthManager(BaseAuthManager):
    """Facebook authentication manager using Authlib OAuth2Session with Facebook compliance fixes."""

    def __init__(self, user_id: str, client_id: str, client_secret: str,
                 refresh_token: Optional[str] = None):
        """Initialize Facebook authentication manager."""
        super().__init__()
        self.user_id = user_id
        self.client_id = client_id
        self.client_secret = client_secret
        self.refresh_token = refresh_token or self._load_refresh_token_from_cache()

        # Authlib OAuth2Session configuration with Facebook compliance fix
        self.oauth_session = OAuth2Session(
            client_id=self.client_id,
            client_secret=self.client_secret,
            scope="email,public_profile,pages_manage_posts,pages_read_engagement",
            redirect_uri="http://localhost:3457/callback"
        )

        # Apply Facebook-specific compliance fixes
        self.oauth_session = facebook_compliance_fix(self.oauth_session)

    async def authenticate(self) -> bool:
        """
        Authenticate with Facebook API using Authlib OAuth2Session.

        Returns:
            bool: True if authentication successful, False otherwise
        """
        if not self._validate_credentials():
            return False

        # If we don't have a refresh token, need to authorize first
        if not self.refresh_token:
            self.refresh_token = await self.authorize()
            if not self.refresh_token:
                return False

        try:
            # Refresh access token using authlib's built-in method with Facebook compliance
            token_data = await self._refresh_access_token()
            self.access_token = token_data['access_token']

            # Update refresh token if new one provided
            if token_data.get('refresh_token') and token_data['refresh_token'] != self.refresh_token:
                self.refresh_token = token_data['refresh_token']
                self._save_refresh_token_to_cache(self.refresh_token)

            # Create client and get user info
            if self.access_token:
                self.client = self._create_client(self.access_token)
                self.user_info = await self._get_user_info()

            return True
        except Exception:
            return False

    async def authorize(self) -> Optional[str]:
        """
        Run Facebook OAuth authorization flow using Authlib.

        Returns:
            str or None: The refresh token if successful, None if failed
        """
        if not self._validate_credentials():
            raise Exception('Facebook credentials are required for authorization.')

        try:
            def _sync_authorize():
                # Create authorization URL
                authorization_url, state = self.oauth_session.create_authorization_url(
                    'https://www.facebook.com/v21.0/dialog/oauth'
                )

                print("Opening browser for Facebook authorization...")
                print(f"Authorization URL: {authorization_url}")
                webbrowser.open(authorization_url)

                # Wait for user to complete authorization and provide callback URL
                callback_url = input("Please complete authorization in browser and paste the callback URL here: ")

                # Exchange authorization code for tokens
                token = self.oauth_session.fetch_token(
                    'https://graph.facebook.com/v21.0/oauth/access_token',
                    authorization_response=callback_url
                )

                # Exchange short-lived token for long-lived token
                long_lived_token = self._exchange_for_long_lived_token(token['access_token'])

                # Save the long-lived token as refresh token
                self._save_refresh_token_to_cache(long_lived_token)
                return long_lived_token

            return await asyncio.to_thread(_sync_authorize)
        except Exception:
            return None

    def _exchange_for_long_lived_token(self, short_lived_token: str) -> str:
        """Exchange short-lived token for long-lived token using authlib."""
        try:
            # Use authlib's fetch_token with custom grant type and parameters
            token_data = self.oauth_session.fetch_token(
                url='https://graph.facebook.com/v21.0/oauth/access_token',
                grant_type='fb_exchange_token',
                fb_exchange_token=short_lived_token
            )

            return token_data.get('access_token')
        except Exception as e:
            raise Exception(f"Long-lived token exchange failed: {str(e)}")

    async def _refresh_access_token(self) -> dict:
        """
        Refresh Facebook access token using authlib's built-in refresh_token method.
        The compliance hook will convert this to Facebook's fb_exchange_token format.
        """
        def _sync_refresh():
            # Use authlib's refresh_token method - compliance hook handles Facebook specifics
            token_data = self.oauth_session.refresh_token(
                token_url='https://graph.facebook.com/v21.0/oauth/access_token',
                refresh_token=self.refresh_token
            )
            return token_data

        return await asyncio.to_thread(_sync_refresh)

    def _create_client(self, access_token: str) -> FacebookAPIClient:
        """Create Facebook API client instance."""
        return FacebookAPIClient(access_token=access_token)

    async def _get_user_info(self) -> dict:
        """Get user information from Facebook API."""
        if not self.client:
            raise Exception('No client available')

        def _sync_get_info():
            if not self.client:
                raise Exception('No client available')

            user_data = self.client.get_object(object_id='me', fields='id,name')

            # Verify username matches
            if user_data.get('id') != self.user_id:
                raise Exception(f"User ID mismatch: {user_data.get('id')} != {self.user_id}")

            return user_data

        return await asyncio.to_thread(_sync_get_info)

    def _validate_credentials(self) -> bool:
        """Validate that all required credentials are present."""
        return all([self.user_id, self.client_id, self.client_secret])

    def _get_cache_filename(self) -> str:
        """Get cache filename for storing refresh token."""
        return f'facebook-{self.user_id}.json'

    def _load_refresh_token_from_cache(self) -> Optional[str]:
        """Load refresh token from cache file."""
        cache_file = self._get_cache_filename()
        return self._load_token_from_cache(cache_file, 'facebook_refresh_token')

    def _save_refresh_token_to_cache(self, refresh_token: str):
        """Save refresh token to cache file."""
        cache_file = self._get_cache_filename()
        self._save_token_to_cache(cache_file, 'facebook_refresh_token', refresh_token)
