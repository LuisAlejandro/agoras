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
import webbrowser
from typing import Optional

from authlib.integrations.requests_client import OAuth1Session

from agoras.core.auth import BaseAuthManager
from agoras.core.auth.callback_server import OAuthCallbackServer

from .client import XAPIClient


class XAuthManager(BaseAuthManager):
    """X authentication manager using Authlib OAuth1Session for OAuth 1.0a."""

    def __init__(self, consumer_key: Optional[str] = None, consumer_secret: Optional[str] = None,
                 oauth_token: Optional[str] = None, oauth_secret: Optional[str] = None):
        """
        Initialize X authentication manager.

        Args:
            consumer_key (str): X consumer key
            consumer_secret (str): X consumer secret
            oauth_token (str, optional): X OAuth token (if already obtained)
            oauth_secret (str, optional): X OAuth secret (if already obtained)
        """
        super().__init__()
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret
        self.oauth_token = oauth_token
        self.oauth_secret = oauth_secret

    async def authenticate(self) -> bool:
        """
        Authenticate with X API using OAuth 1.0a credentials.

        Returns:
            bool: True if authentication successful, False otherwise
        """
        # Validate all credentials are present (fail fast if missing)
        if not self._validate_credentials():
            raise Exception('X OAuth tokens are required for authentication. Please run "agoras x authorize" first.')

        try:
            # For Twitter OAuth 1.0a, we use the oauth_token as the access_token
            self.access_token = self.oauth_token

            # Create client and authenticate it
            if self.access_token and self.oauth_token and self.oauth_secret:
                self.client = self._create_client()
                await self.client.authenticate()

            return True
        except Exception as e:
            # Log the error for debugging
            import logging
            logger = logging.getLogger(__name__)
            logger.debug(f'X authentication failed: {str(e)}', exc_info=True)
            return False

    async def authorize(self) -> Optional[str]:
        """
        Authorize X account and store credentials.

        Returns:
            str: Success message if authorization successful, None otherwise
        """
        if not self._validate_basic_credentials():
            raise Exception('X consumer key and secret are required for authorization.')

        # If OAuth tokens are already provided, just save them
        if self.oauth_token and self.oauth_secret:
            self._save_credentials_to_storage()
            return "Authorization successful. Credentials stored securely."

        # Interactive mode with callback server
        return await self._authorize_interactive()

    async def _authorize_interactive(self) -> Optional[str]:
        """Authorize using local callback server (interactive mode)."""
        try:
            # Create OAuth session for authorization
            self.oauth_session = OAuth1Session(
                client_id=self.consumer_key,
                client_secret=self.consumer_secret
            )

            callback_server = OAuthCallbackServer(
                oauth_version='1.0a',
                port=3456
            )
            redirect_uri = "https://localhost:3456/callback"

            def _sync_oauth_flow():
                # Fetch request token
                request_token_url = 'https://api.x.com/oauth/request_token'
                self.oauth_session.redirect_uri = redirect_uri
                request_token = self.oauth_session.fetch_request_token(request_token_url)

                # Create authorization URL and open browser
                authorization_url = 'https://api.x.com/oauth/authorize'
                auth_url = f"{authorization_url}?oauth_token={request_token['oauth_token']}"

                print("Opening browser for X authorization...")
                print(f"Authorization URL: {auth_url}")
                webbrowser.open(auth_url)

                return True

            # Execute sync OAuth setup (fetch token, open browser)
            await asyncio.to_thread(_sync_oauth_flow)

            # Wait for callback from browser
            callback_path = await callback_server.start_and_wait(timeout=300)
            callback_url = f"http://localhost:{callback_server.port}{callback_path}"

            # Complete OAuth flow (parse callback and fetch access token)
            def _sync_complete_oauth():
                self.oauth_session.parse_authorization_response(callback_url)
                access_token_url = 'https://api.x.com/oauth/access_token'
                access_token = self.oauth_session.fetch_access_token(access_token_url)

                self.oauth_token = access_token['oauth_token']
                self.oauth_secret = access_token['oauth_token_secret']
                self._save_credentials_to_storage()

            await asyncio.to_thread(_sync_complete_oauth)

            return "Authorization successful. Credentials stored securely."

        except Exception as e:
            raise Exception(f'X authorization failed: {str(e)}')

    def _create_client(self) -> XAPIClient:
        """Create X API client instance."""
        if not self.oauth_token or not self.oauth_secret:
            raise Exception('OAuth tokens are required to create X client')

        return XAPIClient(
            consumer_key=self.consumer_key,
            consumer_secret=self.consumer_secret,
            oauth_token=self.oauth_token,
            oauth_secret=self.oauth_secret
        )

    async def _get_user_info(self) -> dict:
        """Get user information from X API."""
        if not self.client:
            raise Exception('No client available')

        # Authenticate the client first
        await self.client.authenticate()

        return await self.client.get_user_info()

    def _validate_basic_credentials(self) -> bool:
        """Validate that basic credentials (consumer key/secret) are present."""
        return all([self.consumer_key, self.consumer_secret])

    def _validate_credentials(self) -> bool:
        """Validate that all required credentials are present."""
        return all([self.consumer_key, self.consumer_secret, self.oauth_token, self.oauth_secret])

    def _get_platform_name(self) -> str:
        """Get platform name for token storage."""
        return "x"

    def _get_token_identifier(self) -> str:
        """Get token identifier (use consumer key hash)."""
        import hashlib
        if self.consumer_key:
            return hashlib.md5(self.consumer_key.encode()).hexdigest()[:8]
        return "default"

    def _save_credentials_to_storage(self):
        """Save all X credentials to secure storage."""
        platform_name = self._get_platform_name()
        identifier = self._get_token_identifier()

        token_data = {
            'consumer_key': self.consumer_key,
            'consumer_secret': self.consumer_secret,
            'oauth_token': self.oauth_token,
            'oauth_secret': self.oauth_secret
        }

        self.token_storage.save_token(platform_name, identifier, token_data)

    def _load_credentials_from_storage(self) -> bool:
        """Load X credentials from secure storage."""
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
            self.consumer_key = token_data.get('consumer_key')
            self.consumer_secret = token_data.get('consumer_secret')
            self.oauth_token = token_data.get('oauth_token')
            self.oauth_secret = token_data.get('oauth_secret')
            return bool(all([self.consumer_key, self.consumer_secret,
                            self.oauth_token, self.oauth_secret]))

        return False
