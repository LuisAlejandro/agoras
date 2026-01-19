# -*- coding: utf-8 -*-
#
# Please refer to AUTHORS.md for a complete list of Copyright holders.
# Copyright (C) 2022-2026, Agoras Developers.

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
import secrets
import webbrowser
from typing import Any, Dict, Optional

from agoras.core.auth import BaseAuthManager
from agoras.core.auth.callback_server import OAuthCallbackServer

from .client import ThreadsAPIClient


class ThreadsAuthManager(BaseAuthManager):
    """Threads authentication manager using OAuth 2.0 flow."""

    def __init__(self, app_id: str, app_secret: str,
                 refresh_token: Optional[str] = None):
        """Initialize Threads authentication manager."""
        super().__init__()
        self.app_id = app_id
        self.app_secret = app_secret
        self.redirect_uri = "https://localhost:3456/callback"
        self.refresh_token = refresh_token or self._load_refresh_token_from_storage()
        self.user_id = None

    async def authenticate(self) -> bool:
        """
        Authenticate with Threads API using OAuth 2.0.

        Returns:
            bool: True if authentication successful, False otherwise
        """
        # If already authenticated, return True
        if self.authenticated:
            return True

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
        except Exception:
            # Log error for debugging but don't expose to user
            # Following the pattern from TikTokAuthManager
            return False

    async def authorize(self) -> Optional[str]:
        """
        Run Threads OAuth authorization flow.

        Uses interactive mode with local callback server.

        Returns:
            str or None: The refresh token if successful, None if failed
        """
        if not self._validate_credentials():
            raise Exception('Threads app ID, app secret, and redirect URI are required for authorization.')

        # Interactive mode with callback server
        return await self._authorize_interactive()

    async def _authorize_interactive(self) -> Optional[str]:
        """Authorize using local callback server (interactive mode)."""
        try:
            state = secrets.token_urlsafe(32)
            callback_server = OAuthCallbackServer(expected_state=state, port=3456)

            # Use the provided redirect URI (must be HTTPS)
            redirect_uri = self.redirect_uri

            # Create authorization URL directly using Meta's Threads OAuth endpoint
            print("Creating authorization URL directly...")
            auth_url = (
                f"https://threads.net/oauth/authorize?"
                f"client_id={self.app_id}&"
                f"redirect_uri={redirect_uri}&"
                f"scope=threads_basic,threads_content_publish&"
                f"response_type=code&"
                f"state={state}"
            )
            print(f"Authorization URL: {auth_url}")

            print("Opening browser for Threads authorization...")
            print(f"If browser doesn't open automatically, visit: {auth_url}")
            webbrowser.open(auth_url)

            auth_code = await callback_server.start_and_wait(timeout=300)

            if not auth_code:
                raise Exception("No authorization code received from OAuth callback")

            def _sync_exchange():
                try:
                    # Exchange authorization code for tokens
                    print(f"Exchanging code for tokens with app_id={self.app_id[:10]}...")
                    print(f"Auth code: {auth_code[:20] if auth_code else 'None'}...")
                    print(f"Redirect URI: {redirect_uri}")

                    # Exchange authorization code for tokens using direct Meta API call
                    import requests

                    token_url = "https://graph.threads.net/oauth/access_token"
                    token_data = {
                        'client_id': self.app_id,
                        'client_secret': self.app_secret,
                        'grant_type': 'authorization_code',
                        'redirect_uri': redirect_uri,
                        'code': auth_code
                    }

                    response = requests.post(token_url, data=token_data, timeout=30)

                    if response.status_code != 200:
                        raise Exception(f"Token exchange failed: HTTP {response.status_code} - {response.text}")

                    tokens = response.json()

                    if not isinstance(tokens, dict):
                        raise Exception(f"Invalid token response format: {type(tokens)}")

                    long_lived_token = tokens.get('access_token')
                    user_id = tokens.get('user_id')

                    if not long_lived_token or not user_id:
                        raise Exception('Invalid token response: missing access_token or user_id')

                    # Save all credentials to storage
                    self.refresh_token = long_lived_token
                    self.user_id = user_id
                    self._save_credentials_to_storage(long_lived_token, user_id)
                    return long_lived_token

                except Exception as e:
                    raise Exception(f"Token exchange failed: {str(e)}")

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
        return all([self.app_id, self.app_secret])

    def _get_platform_name(self) -> str:
        """Get the platform name for this auth manager."""
        return 'threads'

    def _get_token_identifier(self) -> str:
        """Get unique identifier for token storage."""
        return self.app_id

    def _load_user_id_from_storage(self) -> Optional[str]:
        """Load user ID from secure storage."""
        token_data = self.token_storage.load_token('threads', self.app_id)
        if token_data:
            return token_data.get('user_id')
        return None

    def _save_credentials_to_storage(self, refresh_token: str, user_id: str):
        """Save all Threads credentials to secure storage."""
        platform_name = self._get_platform_name()
        identifier = self._get_token_identifier()

        token_data = {
            'app_id': self.app_id,
            'app_secret': self.app_secret,
            'refresh_token': refresh_token,
            'user_id': user_id
        }

        self.token_storage.save_token(platform_name, identifier, token_data)

    def _load_credentials_from_storage(self) -> bool:
        """Load Threads credentials from secure storage."""
        platform_name = self._get_platform_name()

        # Try default identifier first
        identifier = self._get_token_identifier()
        token_data = self.token_storage.load_token(platform_name, identifier)

        if not token_data:
            # Try to find any stored token
            tokens = self.token_storage.list_tokens(platform_name)
            if tokens:
                identifier = tokens[0][1]
                token_data = self.token_storage.load_token(platform_name, identifier)

        if token_data:
            # Only update if not already set (allow override from constructor)
            if not self.app_id:
                self.app_id = token_data.get('app_id')
            if not self.app_secret:
                self.app_secret = token_data.get('app_secret')
            if not self.refresh_token:
                self.refresh_token = token_data.get('refresh_token')
            if not self.user_id:
                self.user_id = token_data.get('user_id')

            return bool(all([self.app_id, self.app_secret, self.refresh_token]))

        return False
