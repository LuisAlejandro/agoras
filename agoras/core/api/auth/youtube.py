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
import secrets
import webbrowser
from typing import Optional

from authlib.integrations.requests_client import OAuth2Session

from .base import BaseAuthManager
from .callback_server import OAuthCallbackServer
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

        # If we don't have a refresh token, fail fast (don't trigger OAuth)
        if not self.refresh_token:
            return False

        try:
            # Refresh access token using authlib's built-in method
            token_data = await self._refresh_access_token_with_authlib()
            self.access_token = token_data['access_token']

            # Update refresh token if new one provided
            if token_data.get('refresh_token') and token_data['refresh_token'] != self.refresh_token:
                self.refresh_token = token_data['refresh_token']
                self._save_refresh_token_to_storage(self.refresh_token)

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

        Supports both interactive mode (with local callback server) and
        headless mode (using environment variables for CI/CD).

        Returns:
            str or None: The refresh token if successful, None if failed
        """
        if not self._validate_credentials():
            raise Exception('YouTube credentials are required for authorization.')

        # Check for headless mode (CI/CD)
        if self._check_headless_mode():
            return await self._authorize_headless()

        # Interactive mode with callback server
        return await self._authorize_interactive()

    async def _authorize_headless(self) -> Optional[str]:
        """Authorize using environment variables (CI/CD mode)."""
        try:
            refresh_token = self._load_refresh_token_from_env()
            if not refresh_token:
                raise Exception(
                    'Headless mode enabled but AGORAS_YOUTUBE_REFRESH_TOKEN not set.'
                )

            self._save_refresh_token_to_storage(refresh_token)
            print("Successfully seeded YouTube credentials from environment variables.")
            return refresh_token
        except Exception as e:
            print(f"Headless authorization failed: {e}")
            return None

    async def _authorize_interactive(self) -> Optional[str]:
        """Authorize using local callback server (interactive mode)."""
        try:
            state = secrets.token_urlsafe(32)
            callback_server = OAuthCallbackServer(expected_state=state)
            port = await callback_server.get_available_port()
            redirect_uri = f"http://localhost:{port}/callback"

            self.oauth_session.redirect_uri = redirect_uri

            authorization_url, _ = self.oauth_session.create_authorization_url(
                'https://accounts.google.com/o/oauth2/auth',
                access_type='offline',
                prompt='consent',
                state=state
            )

            print("Opening browser for YouTube authorization...")
            print(f"If browser doesn't open automatically, visit: {authorization_url}")
            webbrowser.open(authorization_url)

            auth_code = await callback_server.start_and_wait(timeout=300)

            def _sync_exchange():
                token = self.oauth_session.fetch_token(
                    'https://oauth2.googleapis.com/token',
                    code=auth_code,
                    redirect_uri=redirect_uri
                )

                refresh_token = token.get('refresh_token')
                if refresh_token:
                    self._save_refresh_token_to_storage(refresh_token)
                    return refresh_token
                else:
                    raise Exception('No refresh token in YouTube/Google response. '
                                    'Try revoking access and re-authorizing.')

            return await asyncio.to_thread(_sync_exchange)
        except Exception as e:
            print(f"Interactive authorization failed: {e}")
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
        """Get cache filename for storing refresh token. DEPRECATED."""
        return f'youtube-{self.client_id}.json'

    def _get_platform_name(self) -> str:
        """Get the platform name for this auth manager."""
        return 'youtube'

    def _get_token_identifier(self) -> str:
        """Get unique identifier for token storage."""
        return self.client_id

    def _load_refresh_token_from_cache(self) -> Optional[str]:
        """Load refresh token from secure storage."""
        return self._load_refresh_token_from_storage()

    def _save_refresh_token_to_cache(self, refresh_token: str):
        """Save refresh token to secure storage. DEPRECATED - use _save_refresh_token_to_storage."""
        self._save_refresh_token_to_storage(refresh_token)
