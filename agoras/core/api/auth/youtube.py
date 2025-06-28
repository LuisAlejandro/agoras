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
import json
import os
import webbrowser
from typing import Optional

from authlib.integrations.requests_client import OAuth2Session

from .base import BaseAuthManager
from ..clients.youtube import YouTubeAPIClient


class YouTubeAuthManager(BaseAuthManager):
    """YouTube authentication manager using Authlib OAuth2Session with Google OAuth2."""

    def __init__(self, client_id: str, client_secret: str,
                 refresh_token: Optional[str] = None):
        """Initialize YouTube authentication manager."""
        super().__init__()
        self.client_id = client_id
        self.client_secret = client_secret
        self.refresh_token = refresh_token or self._load_refresh_token_from_cache()

        # Authlib OAuth2Session configuration for Google/YouTube OAuth
        self.oauth_session = OAuth2Session(
            client_id=self.client_id,
            client_secret=self.client_secret,
            scope="https://www.googleapis.com/auth/youtube.upload",
            redirect_uri="http://localhost:3456/callback"
        )

    async def authenticate(self) -> bool:
        """
        Authenticate with YouTube API using Authlib OAuth2Session.

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
        Run YouTube OAuth authorization flow using Authlib.

        Returns:
            str or None: The refresh token if successful, None if failed
        """
        if not self._validate_credentials():
            raise Exception('YouTube credentials are required for authorization.')

        try:
            def _sync_authorize():
                # Create authorization URL with offline access for refresh token
                authorization_url, state = self.oauth_session.create_authorization_url(
                    'https://accounts.google.com/o/oauth2/auth',
                    access_type='offline',
                    prompt='consent'  # Force consent to ensure refresh token
                )

                print("Opening browser for YouTube authorization...")
                print(f"Authorization URL: {authorization_url}")
                webbrowser.open(authorization_url)

                # Wait for user to complete authorization and provide callback URL
                callback_url = input("Please complete authorization in browser and paste the callback URL here: ")

                # Exchange authorization code for tokens
                token = self.oauth_session.fetch_token(
                    'https://oauth2.googleapis.com/token',
                    authorization_response=callback_url
                )

                # Save the refresh token
                refresh_token = token.get('refresh_token')
                if refresh_token:
                    self._save_refresh_token_to_cache(refresh_token)
                    return refresh_token
                else:
                    raise Exception('No refresh token in YouTube/Google response. '
                                    'Try revoking access and re-authorizing.')

            return await asyncio.to_thread(_sync_authorize)
        except Exception:
            return None

    async def _refresh_access_token_with_authlib(self) -> dict:
        """
        Refresh YouTube access token using authlib's built-in method.
        Google uses standard OAuth2 refresh token flow.
        """
        def _sync_refresh():
            # Use authlib's refresh_token method for Google's standard OAuth2
            token_data = self.oauth_session.refresh_token(
                token_url='https://oauth2.googleapis.com/token',
                refresh_token=self.refresh_token
            )
            return token_data

        return await asyncio.to_thread(_sync_refresh)

    def _create_client(self, access_token: str) -> YouTubeAPIClient:
        """Create YouTube API client instance."""
        return YouTubeAPIClient(access_token=access_token)

    async def _get_user_info(self) -> dict:
        """Get user information from YouTube API."""
        if not self.client:
            raise Exception('No client available')

        # Authenticate the client first
        await self.client.authenticate()

        try:
            # Get channel info using YouTube API client
            return await self.client.get_channel_info()
        except Exception as e:
            raise Exception(f'Failed to get YouTube channel info: {str(e)}')

    def _validate_credentials(self) -> bool:
        """Validate that all required credentials are present."""
        return all([self.client_id, self.client_secret])

    def _get_cache_filename(self) -> str:
        """Get cache filename for storing refresh token."""
        return f'youtube-{self.client_id}.json'

    def _load_refresh_token_from_cache(self) -> Optional[str]:
        """Load refresh token from cache file."""
        cache_file = self._get_cache_filename()
        return self._load_token_from_cache(cache_file, 'youtube_refresh_token')

    def _save_refresh_token_to_cache(self, refresh_token: str):
        """Save refresh token to cache file."""
        cache_file = self._get_cache_filename()
        self._save_token_to_cache(cache_file, 'youtube_refresh_token', refresh_token)