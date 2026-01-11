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

from .base import BaseAuthManager
from .callback_server import OAuthCallbackServer
from ..clients.instagram import InstagramAPIClient


def facebook_compliance_fix(session):
    """
    Facebook compliance fix for non-standard OAuth2 implementation.
    Instagram uses Facebook's OAuth system, which uses 'fb_exchange_token'
    instead of standard 'refresh_token' grant type.
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


class InstagramAuthManager(BaseAuthManager):
    """Instagram authentication manager using Authlib OAuth2Session with Facebook compliance fixes."""

    def __init__(self, user_id: str, client_id: str, client_secret: str,
                 refresh_token: Optional[str] = None):
        """Initialize Instagram authentication manager."""
        super().__init__()
        self.user_id = user_id
        self.client_id = client_id
        self.client_secret = client_secret
        self.refresh_token = refresh_token or self._load_refresh_token_from_cache()

        # Authlib OAuth2Session configuration for Instagram (uses Facebook's OAuth)
        self.oauth_session = OAuth2Session(
            client_id=self.client_id,
            client_secret=self.client_secret,
            scope="instagram_basic,instagram_content_publish,pages_read_engagement,pages_show_list",
            redirect_uri="http://localhost:3458/callback"
        )

        # Apply Facebook-specific compliance fixes for Instagram
        self.oauth_session = facebook_compliance_fix(self.oauth_session)

    async def authenticate(self) -> bool:
        """
        Authenticate with Instagram API using Authlib OAuth2Session.

        Returns:
            bool: True if authentication successful, False otherwise
        """
        if not self._validate_credentials():
            return False

        # If we don't have a refresh token, fail fast (don't trigger OAuth)
        if not self.refresh_token:
            return False

        try:
            # Refresh access token using authlib's built-in method with Facebook compliance
            token_data = await self._refresh_access_token()
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
        Run Instagram OAuth authorization flow using Authlib.

        Supports both interactive mode (with local callback server) and
        headless mode (using environment variables for CI/CD).

        Returns:
            str or None: The refresh token if successful, None if failed
        """
        if not self._validate_credentials():
            raise Exception('Instagram credentials are required for authorization.')

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
                    'Headless mode enabled but AGORAS_INSTAGRAM_REFRESH_TOKEN not set.'
                )

            self._save_refresh_token_to_storage(refresh_token)
            print("Successfully seeded Instagram credentials from environment variables.")
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
                'https://www.facebook.com/v21.0/dialog/oauth',
                state=state
            )

            print("Opening browser for Instagram authorization...")
            print(f"If browser doesn't open automatically, visit: {authorization_url}")
            webbrowser.open(authorization_url)

            auth_code = await callback_server.start_and_wait(timeout=300)

            def _sync_exchange():
                token = self.oauth_session.fetch_token(
                    'https://graph.facebook.com/v21.0/oauth/access_token',
                    code=auth_code,
                    redirect_uri=redirect_uri
                )

                long_lived_token = self._exchange_for_long_lived_token(token['access_token'])
                self._save_refresh_token_to_storage(long_lived_token)
                return long_lived_token

            return await asyncio.to_thread(_sync_exchange)
        except Exception as e:
            print(f"Interactive authorization failed: {e}")
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
        Refresh Instagram access token using authlib's built-in method.
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

    def _create_client(self, access_token: str) -> InstagramAPIClient:
        """Create Instagram API client instance."""
        return InstagramAPIClient(access_token=access_token)

    async def _get_user_info(self) -> dict:
        """Get user information from Instagram API."""
        if not self.client:
            raise Exception('No client available')

        # Authenticate the client first
        await self.client.authenticate()

        def _sync_get_info():
            if not self.client:
                raise Exception('No client available')

            # Get basic user data
            user_data = self.client.get_object(object_id='me', fields='id,name')

            # Verify user ID matches
            if user_data.get('id') != self.user_id:
                raise Exception(f"User ID mismatch: {user_data.get('id')} != {self.user_id}")

            # Get Instagram business accounts using get_object instead of get_connections
            accounts_data = self.client.get_object(
                object_id=f"{self.user_id}/accounts",
                fields='id,name,instagram_business_account'
            )

            # Find Instagram business account
            instagram_account = None
            accounts_list = accounts_data.get('data') if accounts_data else []
            if accounts_list:
                for page in accounts_list:
                    if page.get('instagram_business_account'):
                        instagram_account = page['instagram_business_account']
                        break

            if not instagram_account:
                raise Exception("No Instagram business account found for this user")

            # Get Instagram account details
            ig_account_data = self.client.get_object(
                object_id=instagram_account['id'],
                fields='id,name,username'
            )

            # Combine user data with Instagram account info
            user_data['instagram_account'] = ig_account_data
            return user_data

        return await asyncio.to_thread(_sync_get_info)

    def _validate_credentials(self) -> bool:
        """Validate that all required credentials are present."""
        return all([self.user_id, self.client_id, self.client_secret])

    def _get_cache_filename(self) -> str:
        """Get cache filename for storing refresh token. DEPRECATED."""
        return f'instagram-{self.user_id}.json'

    def _get_platform_name(self) -> str:
        """Get the platform name for this auth manager."""
        return 'instagram'

    def _get_token_identifier(self) -> str:
        """Get unique identifier for token storage."""
        return self.user_id

    def _load_refresh_token_from_cache(self) -> Optional[str]:
        """Load refresh token from secure storage."""
        return self._load_refresh_token_from_storage()

    def _save_refresh_token_to_cache(self, refresh_token: str):
        """Save refresh token to secure storage. DEPRECATED - use _save_refresh_token_to_storage."""
        self._save_refresh_token_to_storage(refresh_token)
