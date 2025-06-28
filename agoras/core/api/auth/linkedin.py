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
from ..clients.linkedin import LinkedInAPIClient


class LinkedInAuthManager(BaseAuthManager):
    """LinkedIn authentication manager using Authlib OAuth2Session for OAuth 2.0."""

    def __init__(self, user_id: str, client_id: str, client_secret: str,
                 refresh_token: Optional[str] = None):
        """
        Initialize LinkedIn authentication manager.

        Args:
            user_id (str): LinkedIn user ID (object ID)
            client_id (str): LinkedIn client ID
            client_secret (str): LinkedIn client secret
            refresh_token (str, optional): LinkedIn refresh token
        """
        super().__init__()
        self.user_id = user_id
        self.client_id = client_id
        self.client_secret = client_secret
        self.refresh_token = refresh_token or self._load_refresh_token_from_cache()
        self.api_version = "202302"

        # Authlib OAuth2Session configuration for LinkedIn
        self.oauth_session = OAuth2Session(
            client_id=self.client_id,
            client_secret=self.client_secret,
            scope="openid profile email w_member_social",
            redirect_uri="http://localhost:3460/callback"
        )

    async def authenticate(self) -> bool:
        """
        Authenticate with LinkedIn API using Authlib OAuth2Session.

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
            # Refresh access token using authlib's built-in method
            token_data = await self._refresh_access_token_with_authlib()
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
        Run LinkedIn OAuth authorization flow using Authlib.

        Returns:
            str or None: The refresh token if successful, None if failed
        """
        if not self._validate_credentials():
            raise Exception('LinkedIn credentials are required for authorization.')

        try:
            def _sync_authorize():
                # Create authorization URL
                authorization_url, state = self.oauth_session.create_authorization_url(
                    'https://www.linkedin.com/oauth/v2/authorization',
                    state=None  # Let authlib generate state
                )

                print("Opening browser for LinkedIn authorization...")
                print(f"Authorization URL: {authorization_url}")
                webbrowser.open(authorization_url)

                # Wait for user to complete authorization and provide callback URL
                callback_url = input("Please complete authorization in browser and paste the callback URL here: ")

                # Exchange authorization code for tokens
                token = self.oauth_session.fetch_token(
                    'https://www.linkedin.com/oauth/v2/accessToken',
                    authorization_response=callback_url
                )

                # Save the refresh token
                refresh_token = token.get('refresh_token')
                if refresh_token:
                    self._save_refresh_token_to_cache(refresh_token)
                    return refresh_token
                else:
                    # LinkedIn might not always return refresh tokens
                    # In such cases, we'll store the access token as a long-lived token
                    access_token = token.get('access_token')
                    if access_token:
                        self._save_refresh_token_to_cache(access_token)
                        return access_token
                    raise Exception('No refresh token or access token in LinkedIn response')

            return await asyncio.to_thread(_sync_authorize)
        except Exception:
            return None

    async def _refresh_access_token_with_authlib(self) -> dict:
        """
        Refresh LinkedIn access token using authlib's built-in method.
        LinkedIn uses standard OAuth2 refresh token flow.
        """
        def _sync_refresh():
            try:
                # Try to refresh using refresh_token method
                token_data = self.oauth_session.refresh_token(
                    token_url='https://www.linkedin.com/oauth/v2/accessToken',
                    refresh_token=self.refresh_token
                )
                return token_data
            except Exception:
                # If refresh fails, the stored token might be an access token
                # In this case, return it as-is (LinkedIn tokens can be long-lived)
                return {
                    'access_token': self.refresh_token,
                    'token_type': 'bearer'
                }

        return await asyncio.to_thread(_sync_refresh)

    def _create_client(self, access_token: str) -> LinkedInAPIClient:
        """Create LinkedIn API client instance."""
        return LinkedInAPIClient(access_token=access_token)

    async def _get_user_info(self) -> dict:
        """Get user information from LinkedIn API."""
        if not self.client:
            raise Exception('No client available')

        # Authenticate the client first
        await self.client.authenticate()

        try:
            # Get user info using LinkedIn API client
            result = await self.client.get_user_info()

            # Extract object_id and validate
            object_id = result.get('sub', '')
            if not object_id:
                raise Exception('Unable to get LinkedIn object ID from user info')

            # Verify user ID matches
            if object_id != self.user_id:
                raise Exception(f"LinkedIn user ID mismatch: {object_id} != {self.user_id}")

            # Return enriched user data
            return {
                'object_id': object_id,
                'sub': object_id,
                'name': result.get('name', ''),
                'given_name': result.get('given_name', ''),
                'family_name': result.get('family_name', ''),
                'email': result.get('email', ''),
                'picture': result.get('picture', ''),
                'locale': result.get('locale', '')
            }
        except Exception as e:
            raise Exception(f'Failed to get LinkedIn user info: {str(e)}')

    def _validate_credentials(self) -> bool:
        """Validate that all required credentials are present."""
        return all([self.user_id, self.client_id, self.client_secret])

    def _get_cache_filename(self) -> str:
        """Get cache filename for storing refresh token."""
        return f'linkedin-{self.user_id}.json'

    def _load_refresh_token_from_cache(self) -> Optional[str]:
        """Load refresh token from cache file."""
        cache_file = self._get_cache_filename()
        return self._load_token_from_cache(cache_file, 'linkedin_refresh_token')

    def _save_refresh_token_to_cache(self, refresh_token: str):
        """Save refresh token to cache file."""
        cache_file = self._get_cache_filename()
        self._save_token_to_cache(cache_file, 'linkedin_refresh_token', refresh_token) 