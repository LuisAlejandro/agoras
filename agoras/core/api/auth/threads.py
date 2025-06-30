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

from threadspipepy import ThreadsPipe

from ..clients.threads import ThreadsAPIClient
from .base import BaseAuthManager


class ThreadsAuthManager(BaseAuthManager):
    """Threads authentication manager using OAuth 2.0 flow with threadspipepy."""

    def __init__(self, app_id: str, app_secret: str, redirect_uri: str,
                 refresh_token: Optional[str] = None):
        """Initialize Threads authentication manager."""
        super().__init__()
        self.app_id = app_id
        self.app_secret = app_secret
        self.redirect_uri = redirect_uri
        self.refresh_token = refresh_token or self._load_refresh_token_from_cache()
        self.user_id = None

    async def authenticate(self) -> bool:
        """
        Authenticate with Threads API using OAuth 2.0.

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
            # Refresh or validate access token
            token_data = await self._refresh_or_get_token()
            self.access_token = token_data['access_token']
            self.user_id = token_data.get('user_id')

            # Create client and get user info
            if self.access_token and self.user_id:
                self.client = self._create_client(self.access_token, self.user_id)
                self.user_info = await self._get_user_info()

            return True
        except Exception:
            return False

    async def authorize(self) -> Optional[str]:
        """
        Run Threads OAuth authorization flow using threadspipepy.

        Returns:
            str or None: The refresh token if successful, None if failed
        """
        if not self._validate_credentials():
            raise Exception('Threads app ID, app secret, and redirect URI are required for authorization.')

        try:
            def _sync_authorize():
                # Create ThreadsPipe instance for authorization
                threads_pipe = ThreadsPipe(
                    app_id=self.app_id,
                    app_secret=self.app_secret,
                    redirect_uri=self.redirect_uri
                )

                # Get authorization URL
                auth_url = threads_pipe.get_auth_token()

                print("Opening browser for Threads authorization...")
                print(f"Authorization URL: {auth_url}")
                webbrowser.open(auth_url)

                # Wait for user to complete authorization and provide callback URL
                callback_url = input("Please complete authorization in browser and paste the callback URL here: ")

                # Extract authorization code from callback URL
                if 'code=' in callback_url:
                    code = callback_url.split('code=')[1].split('&')[0]
                else:
                    raise Exception('No authorization code found in callback URL')

                # Exchange authorization code for tokens
                tokens = threads_pipe.get_access_tokens(code)

                # Extract long-lived token (refresh token)
                long_lived_token = tokens.get('access_token')
                user_id = tokens.get('user_id')

                if long_lived_token:
                    # Save both token and user_id to cache
                    self._save_tokens_to_cache(long_lived_token, user_id)
                    return long_lived_token
                else:
                    raise Exception('No access token in Threads response')

            return await asyncio.to_thread(_sync_authorize)
        except Exception:
            return None

    async def _refresh_or_get_token(self) -> dict:
        """
        Refresh Threads access token or use cached long-lived token.
        Meta's long-lived tokens last 60 days and don't need frequent refresh.
        """
        def _sync_refresh():
            # For Threads, we use the long-lived token directly
            # Meta's long-lived tokens are valid for 60 days
            if not self.refresh_token:
                raise Exception('No refresh token available')

            # Load user_id from cache
            user_id = self._load_user_id_from_cache()
            if not user_id:
                raise Exception('No user ID found in cache')

            # Return the cached token data
            return {
                'access_token': self.refresh_token,
                'user_id': user_id
            }

        return await asyncio.to_thread(_sync_refresh)

    def _create_client(self, access_token: str, user_id: str) -> ThreadsAPIClient:
        """Create Threads API client instance."""
        return ThreadsAPIClient(access_token=access_token, user_id=user_id)

    async def _get_user_info(self) -> dict:
        """Get user information from Threads API."""
        if not self.client:
            raise Exception('No client available')

        def _sync_get_info():
            if not self.client:
                raise Exception('No client available')

            user_data = self.client.get_profile()
            return user_data

        return await asyncio.to_thread(_sync_get_info)

    def _validate_credentials(self) -> bool:
        """Validate that all required credentials are present."""
        return all([self.app_id, self.app_secret, self.redirect_uri])

    def _get_cache_filename(self) -> str:
        """Get cache filename for storing refresh token."""
        return f'threads-{self.app_id}.json'

    def _load_refresh_token_from_cache(self) -> Optional[str]:
        """Load refresh token from cache file."""
        cache_file = self._get_cache_filename()
        return self._load_token_from_cache(cache_file, 'threads_refresh_token')

    def _load_user_id_from_cache(self) -> Optional[str]:
        """Load user ID from cache file."""
        cache_file = self._get_cache_filename()
        return self._load_token_from_cache(cache_file, 'threads_user_id')

    def _save_refresh_token_to_cache(self, refresh_token: str):
        """Save refresh token to cache file."""
        cache_file = self._get_cache_filename()
        self._save_token_to_cache(cache_file, 'threads_refresh_token', refresh_token)

    def _save_tokens_to_cache(self, refresh_token: str, user_id: str):
        """Save both refresh token and user ID to cache file."""
        cache_file = self._get_cache_filename()
        data = self._load_cache_data(cache_file)
        data.update({
            'threads_refresh_token': refresh_token,
            'threads_user_id': user_id
        })
        self._save_cache_data(cache_file, data)
