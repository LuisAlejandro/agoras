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
import os
import secrets
import webbrowser
from typing import Any, Dict, Optional

from threadspipepy.threadspipe import ThreadsPipe

from .client import ThreadsAPIClient
from agoras.core.auth import BaseAuthManager
from agoras.core.auth.callback_server import OAuthCallbackServer


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

        # If we don't have a refresh token, fail fast (don't trigger OAuth)
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
        except Exception as e:
            # Log error for debugging but don't expose to user
            # Following the pattern from TikTokAuthManager
            return False

    async def authorize(self) -> Optional[str]:
        """
        Run Threads OAuth authorization flow using threadspipepy.

        Supports both interactive mode (with local callback server) and
        headless mode (using environment variables for CI/CD).

        Returns:
            str or None: The refresh token if successful, None if failed
        """
        if not self._validate_credentials():
            raise Exception('Threads app ID, app secret, and redirect URI are required for authorization.')

        # Check for headless mode (CI/CD)
        if self._check_headless_mode():
            return await self._authorize_headless()

        # Interactive mode with callback server
        return await self._authorize_interactive()

    async def _authorize_headless(self) -> Optional[str]:
        """Authorize using environment variables (CI/CD mode)."""
        try:
            refresh_token = self._load_refresh_token_from_env()
            user_id_env = os.environ.get('AGORAS_THREADS_USER_ID')

            if not refresh_token or not user_id_env:
                raise Exception(
                    'Headless mode enabled but AGORAS_THREADS_REFRESH_TOKEN '
                    'or AGORAS_THREADS_USER_ID not set.'
                )

            # Save both token and user_id to storage
            self._save_tokens_to_storage(refresh_token, user_id_env)
            print("Successfully seeded Threads credentials from environment variables.")
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
            dynamic_redirect_uri = f"http://localhost:{port}/callback"

            # Create ThreadsPipe instance for authorization
            threads_pipe = ThreadsPipe(
                user_id="",
                access_token=""
            )

            # Get authorization URL (ThreadsPipe doesn't support state parameter directly)
            # We'll append it to the URL manually
            auth_url = threads_pipe.get_auth_token(
                app_id=self.app_id,
                redirect_uri=dynamic_redirect_uri
            )

            # Append state parameter for CSRF protection
            if '?' in auth_url:
                auth_url += f"&state={state}"
            else:
                auth_url += f"?state={state}"

            print("Opening browser for Threads authorization...")
            print(f"If browser doesn't open automatically, visit: {auth_url}")
            webbrowser.open(auth_url)

            auth_code = await callback_server.start_and_wait(timeout=300)

            def _sync_exchange():
                # Exchange authorization code for tokens
                tokens = threads_pipe.get_access_tokens(
                    app_id=self.app_id,
                    app_secret=self.app_secret,
                    auth_code=auth_code,
                    redirect_uri=dynamic_redirect_uri
                )

                long_lived_token = tokens.get('access_token')
                user_id = tokens.get('user_id')

                if not long_lived_token:
                    raise Exception('No access token in Threads response')

                if not user_id:
                    raise Exception('No user ID in Threads response')

                # Save both token and user_id to storage
                self._save_tokens_to_storage(long_lived_token, user_id)
                return long_lived_token

            return await asyncio.to_thread(_sync_exchange)
        except Exception as e:
            print(f"Interactive authorization failed: {e}")
            return None

    async def _refresh_or_get_token(self) -> Dict[str, Any]:
        """
        Refresh Threads access token or use cached long-lived token.
        Meta's long-lived tokens last 60 days and don't need frequent refresh.

        Returns:
            dict: Token data containing 'access_token' and 'user_id'
        """
        def _sync_refresh():
            # For Threads, we use the long-lived token directly
            # Meta's long-lived tokens are valid for 60 days
            if not self.refresh_token:
                raise Exception('No refresh token available')

            # Load user_id from storage
            user_id = self._load_user_id_from_storage()
            if not user_id:
                raise Exception('No user ID found in storage')

            # Return the cached token data
            return {
                'access_token': self.refresh_token,
                'user_id': user_id
            }

        return await asyncio.to_thread(_sync_refresh)

    def _create_client(self, access_token: str, user_id: str) -> ThreadsAPIClient:
        """Create Threads API client instance."""
        return ThreadsAPIClient(access_token=access_token, user_id=user_id)

    async def _get_user_info(self) -> Dict[str, Any]:
        """
        Get user information from Threads API.

        Returns:
            dict: User information from the Threads API
        """
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
        """Get cache filename for storing refresh token. DEPRECATED."""
        return f'threads-{self.app_id}.json'

    def _get_platform_name(self) -> str:
        """Get the platform name for this auth manager."""
        return 'threads'

    def _get_token_identifier(self) -> str:
        """Get unique identifier for token storage."""
        return self.app_id

    def _load_refresh_token_from_cache(self) -> Optional[str]:
        """
        Load refresh token from secure storage.

        Note: Despite the name, this method loads from SecureTokenStorage,
        not from deprecated cache files. The name is kept for compatibility
        with the base class interface.
        """
        token_data = self.token_storage.load_token('threads', self.app_id)
        if token_data:
            return token_data.get('refresh_token')
        return None

    def _load_user_id_from_storage(self) -> Optional[str]:
        """Load user ID from secure storage."""
        token_data = self.token_storage.load_token('threads', self.app_id)
        if token_data:
            return token_data.get('user_id')
        return None

    def _save_refresh_token_to_cache(self, refresh_token: str):
        """Save refresh token to secure storage. DEPRECATED - use _save_tokens_to_storage."""
        self._save_refresh_token_to_storage(refresh_token)

    def _save_tokens_to_storage(self, refresh_token: str, user_id: str):
        """Save both refresh token and user ID to secure storage."""
        token_data = {
            'refresh_token': refresh_token,
            'user_id': user_id
        }
        self.token_storage.save_token('threads', self.app_id, token_data)
