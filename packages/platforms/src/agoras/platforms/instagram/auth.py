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
from typing import Optional

from authlib.integrations.requests_client import OAuth2Session

from agoras.core.auth import BaseAuthManager
from agoras.core.auth.callback_server import OAuthCallbackServer

from .client import InstagramAPIClient


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
        self.refresh_token = refresh_token or self._load_refresh_token_from_storage()

        # Authlib OAuth2Session configuration for Instagram (uses Facebook's OAuth)
        self.oauth_session = OAuth2Session(
            client_id=self.client_id,
            client_secret=self.client_secret,
            scope="instagram_basic,instagram_content_publish,pages_read_engagement,pages_show_list",
            redirect_uri="https://localhost:3456/callback"
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

        # Ensure OAuth session has correct credentials
        if not hasattr(self, 'oauth_session') or self.oauth_session.client_id != self.client_id:
            print(f"[DEBUG] Recreating OAuth session with correct credentials: {self.client_id}")
            self.oauth_session = OAuth2Session(
                client_id=self.client_id,
                client_secret=self.client_secret,
                scope="instagram_basic,instagram_content_publish,pages_read_engagement,pages_show_list",
                redirect_uri="https://localhost:3456/callback"
            )
            # Apply Facebook-specific compliance fixes for Instagram
            self.oauth_session = facebook_compliance_fix(self.oauth_session)

        try:
            # Refresh access token using direct HTTP method
            token_data = await self._refresh_access_token()
            self.access_token = token_data['access_token']

            # Update refresh token if new one provided
            if token_data.get('refresh_token') and token_data['refresh_token'] != self.refresh_token:
                self.refresh_token = token_data['refresh_token']
                self._save_credentials_to_storage()

            # Create client and get user info
            if self.access_token:
                self.client = self._create_client(self.access_token)
                await self.client.authenticate()
                self.user_info = await self._get_user_info()

            return True
        except Exception:
            return False

    async def authorize(self) -> Optional[str]:
        """
        Run Instagram OAuth authorization flow using Authlib.

        Uses interactive mode with local callback server.

        Returns:
            str or None: The refresh token if successful, None if failed
        """
        if not self._validate_credentials():
            raise Exception('Instagram credentials are required for authorization.')

        # Interactive mode with callback server
        return await self._authorize_interactive()

    async def _authorize_interactive(self) -> Optional[str]:
        """Authorize using local callback server (interactive mode)."""
        try:
            state = secrets.token_urlsafe(32)
            callback_server = OAuthCallbackServer(expected_state=state, port=3456)
            redirect_uri = "https://localhost:3456/callback"

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
                self.refresh_token = long_lived_token
                self._save_credentials_to_storage()
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
            # Make direct HTTP request for token refresh
            import requests

            data = {
                'grant_type': 'fb_exchange_token',
                'client_id': self.client_id,
                'client_secret': self.client_secret,
                'fb_exchange_token': self.refresh_token
            }

            response = requests.post('https://graph.facebook.com/v21.0/oauth/access_token', data=data)
            response.raise_for_status()
            return response.json()

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

            # Get basic Facebook user data - 'me' returns Facebook user info
            user_data = self.client.get_object(object_id='me', fields='id,name')

            # For Instagram authentication, just return basic user info
            # The stored user_id is already the Instagram Business Account ID
            return {
                'id': self.user_id,  # Instagram Business Account ID
                'name': user_data.get('name', 'Instagram Account'),
                'facebook_user_id': user_data.get('id')  # Facebook user ID
            }

        return await asyncio.to_thread(_sync_get_info)

    def _validate_credentials(self) -> bool:
        """Validate that all required credentials are present."""
        # For authentication/token refresh, we need client_id and client_secret
        # user_id is used for storage identification but not strictly required for auth
        return all([self.client_id, self.client_secret])

    def _get_platform_name(self) -> str:
        """Get the platform name for this auth manager."""
        return 'instagram'

    def _get_token_identifier(self) -> str:
        """Get unique identifier for token storage."""
        return self.user_id

    def _save_credentials_to_storage(self):
        """Save all Instagram credentials to secure storage."""
        platform_name = self._get_platform_name()
        identifier = self._get_token_identifier()

        token_data = {
            'user_id': self.user_id,
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'refresh_token': self.refresh_token
        }

        self.token_storage.save_token(platform_name, identifier, token_data)
        # Also save as default so it becomes the primary credential loaded
        self.token_storage.save_token(platform_name, "default", token_data)

    def _load_credentials_from_storage(self) -> bool:
        """Load Instagram credentials from secure storage."""
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
