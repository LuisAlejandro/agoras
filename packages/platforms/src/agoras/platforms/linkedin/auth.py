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
import secrets
import webbrowser
from typing import Optional

from authlib.integrations.requests_client import OAuth2Session

from .client import LinkedInAPIClient
from agoras.core.auth import BaseAuthManager
from agoras.core.auth.callback_server import OAuthCallbackServer


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
                # Save all credentials to storage
                self._save_credentials_to_storage()

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

        Supports both interactive mode (with local callback server) and
        headless mode (using environment variables for CI/CD).

        Returns:
            str or None: The refresh token if successful, None if failed
        """
        if not self._validate_credentials():
            raise Exception('LinkedIn credentials are required for authorization.')

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
                    'Headless mode enabled but AGORAS_LINKEDIN_REFRESH_TOKEN not set.'
                )

            self.refresh_token = refresh_token
            # Save all credentials to storage
            self._save_credentials_to_storage()
            print("Successfully seeded LinkedIn credentials from environment variables.")
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
                'https://www.linkedin.com/oauth/v2/authorization',
                state=state
            )

            print("Opening browser for LinkedIn authorization...")
            print(f"If browser doesn't open automatically, visit: {authorization_url}")
            webbrowser.open(authorization_url)

            auth_code = await callback_server.start_and_wait(timeout=300)

            def _sync_exchange():
                token = self.oauth_session.fetch_token(
                    'https://www.linkedin.com/oauth/v2/accessToken',
                    code=auth_code,
                    redirect_uri=redirect_uri
                )

                refresh_token = token.get('refresh_token')
                if refresh_token:
                    self.refresh_token = refresh_token
                    # Save all credentials to storage
                    self._save_credentials_to_storage()
                    return refresh_token
                else:
                    # LinkedIn might not always return refresh tokens
                    access_token = token.get('access_token')
                    if access_token:
                        self.refresh_token = access_token
                        # Save all credentials to storage
                        self._save_credentials_to_storage()
                        return access_token
                    raise Exception('No refresh token or access token in LinkedIn response')

            return await asyncio.to_thread(_sync_exchange)
        except Exception as e:
            print(f"Interactive authorization failed: {e}")
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
        """Get cache filename for storing refresh token. DEPRECATED."""
        return f'linkedin-{self.user_id}.json'

    def _get_platform_name(self) -> str:
        """Get the platform name for this auth manager."""
        return 'linkedin'

    def _get_token_identifier(self) -> str:
        """Get unique identifier for token storage."""
        return self.user_id

    def _load_refresh_token_from_cache(self) -> Optional[str]:
        """Load refresh token from secure storage."""
        return self._load_refresh_token_from_storage()

    def _save_refresh_token_to_cache(self, refresh_token: str):
        """Save refresh token to secure storage. DEPRECATED - use _save_refresh_token_to_storage."""
        self._save_refresh_token_to_storage(refresh_token)

    def _save_credentials_to_storage(self):
        """Save all LinkedIn credentials to secure storage."""
        platform_name = self._get_platform_name()
        identifier = self._get_token_identifier()

        token_data = {
            'user_id': self.user_id,
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'refresh_token': self.refresh_token
        }

        self.token_storage.save_token(platform_name, identifier, token_data)

    def _load_credentials_from_storage(self) -> bool:
        """Load LinkedIn credentials from secure storage."""
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
            if not self.user_id:
                self.user_id = token_data.get('user_id')
            if not self.client_id:
                self.client_id = token_data.get('client_id')
            if not self.client_secret:
                self.client_secret = token_data.get('client_secret')
            if not self.refresh_token:
                self.refresh_token = token_data.get('refresh_token')

            return bool(all([self.user_id, self.client_id, self.client_secret, self.refresh_token]))

        return False
