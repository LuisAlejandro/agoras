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
import hashlib
import secrets
import webbrowser
from typing import Optional

from authlib.integrations.requests_client import OAuth2Session

from agoras.core.auth import BaseAuthManager
from agoras.core.auth.callback_server import OAuthCallbackServer

from .client import TikTokAPIClient


def tiktok_compliance_fix(session):
    """
    TikTok compliance fix for non-standard OAuth2 implementation.
    TikTok uses 'client_key' instead of 'client_id' in token requests.
    """
    def _fix_token_request(url, headers, body):
        # Convert client_id to client_key for TikTok API
        if 'client_id=' in body:
            body = body.replace('client_id=', 'client_key=')
        return url, headers, body

    session.register_compliance_hook('refresh_token_request', _fix_token_request)
    return session


class TikTokAuthManager(BaseAuthManager):
    """TikTok authentication manager using Authlib OAuth2Session with PKCE and compliance fixes."""

    def __init__(self, username: str, client_key: str, client_secret: str,
                 refresh_token: Optional[str] = None):
        """Initialize TikTok authentication manager."""
        super().__init__()
        self.username = username
        self.client_key = client_key
        self.client_secret = client_secret
        self.refresh_token = refresh_token or self._load_refresh_token_from_storage()

        # Authlib OAuth2Session configuration for TikTok with PKCE
        # Note: video.upload and video.publish require Production app approval
        self.oauth_session = OAuth2Session(
            client_id=self.client_key,
            client_secret=self.client_secret,
            scope=["user.info.basic"],  # Only basic scope available in Sandbox mode
            redirect_uri="https://localhost:3456/callback",
            code_challenge_method='S256'
        )

        # Apply TikTok-specific compliance fixes
        self.oauth_session = tiktok_compliance_fix(self.oauth_session)

    async def authenticate(self) -> bool:
        """
        Authenticate with TikTok API using Authlib OAuth2Session.

        Returns:
            bool: True if authentication successful, False otherwise
        """
        if not self._validate_credentials():
            return False

        # If we don't have any tokens, fail fast (don't trigger OAuth)
        if not self.refresh_token and not self.access_token:
            return False

        try:
            # If we have a refresh token (not the fake access_only one), try to refresh
            if self.refresh_token and not self.refresh_token.startswith('access_only_'):
                # Refresh access token using direct HTTP request
                token_data = await self._refresh_access_token()
                self.access_token = token_data['access_token']

                # Update refresh token if new one provided
                if token_data.get('refresh_token') and token_data['refresh_token'] != self.refresh_token:
                    self.refresh_token = token_data['refresh_token']
                    # Save all credentials to storage
                    self._save_credentials_to_storage()
            # If we only have an access token (Sandbox mode), use it directly
            elif self.access_token or (self.refresh_token and self.refresh_token.startswith('access_only_')):
                # Extract access token from fake refresh token if needed
                if self.refresh_token.startswith('access_only_'):
                    self.access_token = self.refresh_token.replace('access_only_', '', 1)
                # Access token is already set, use it
            else:
                return False

            # Create client (skip user info retrieval as it's not essential for video operations)
            if self.access_token:
                self.client = self._create_client(self.access_token)
                # Set dummy user info since we don't need it for video operations
                self.user_info = {"username": self.username, "user_id": "unknown"}

            return True
        except Exception:
            return False

    async def authorize(self) -> Optional[str]:
        """
        Run TikTok OAuth authorization flow using Authlib with PKCE.

        Uses interactive mode with local callback server.

        Returns:
            str or None: The refresh token if successful, None if failed
        """
        if not self._validate_credentials():
            raise Exception('TikTok credentials are required for authorization.')

        # Interactive mode with callback server
        return await self._authorize_interactive()

    async def _authorize_interactive(self) -> Optional[str]:
        """Authorize using local callback server (interactive mode)."""
        try:
            state = secrets.token_urlsafe(32)

            callback_server = OAuthCallbackServer(expected_state=state, port=3456)
            redirect_uri = "https://localhost:3456/callback"

            self.oauth_session.redirect_uri = redirect_uri

            # Generate PKCE parameters manually for TikTok compatibility
            code_verifier, code_challenge = self._generate_pkce()

            authorization_url, _ = self.oauth_session.create_authorization_url(
                'https://www.tiktok.com/v2/auth/authorize/',
                state=state
            )

            # TikTok uses client_key instead of client_id in authorization URLs
            authorization_url = authorization_url.replace('client_id=', 'client_key=')

            # Add PKCE parameters manually since Authlib doesn't generate them in URL
            authorization_url += f'&code_challenge={code_challenge}&code_challenge_method=S256'

            print("Opening browser for TikTok authorization...")
            print(f"If browser doesn't open automatically, visit: {authorization_url}")
            webbrowser.open(authorization_url)

            auth_code = await callback_server.start_and_wait(timeout=300)

            def _sync_exchange():
                import requests
                data = {
                    'client_key': self.client_key,
                    'client_secret': self.client_secret,
                    'code': auth_code,
                    'grant_type': 'authorization_code',
                    'redirect_uri': redirect_uri,
                    'code_verifier': code_verifier
                }

                response = requests.post('https://open.tiktokapis.com/v2/oauth/token/', data=data, timeout=30)
                if response.status_code == 200:
                    token = response.json()
                    refresh_token = token.get('refresh_token')
                    access_token = token.get('access_token')

                    if refresh_token:
                        self.refresh_token = refresh_token
                        # Save all credentials to storage
                        self._save_credentials_to_storage()
                        return refresh_token
                    elif access_token:
                        # TikTok sometimes doesn't provide refresh tokens in Sandbox mode
                        # Store the access token temporarily for immediate use
                        self.access_token = access_token
                        # Create a fake refresh token that will fail on refresh but allow immediate use
                        self.refresh_token = f"access_only_{access_token[:20]}"
                        # Save credentials (though refresh will fail later)
                        self._save_credentials_to_storage()
                        return self.refresh_token
                    else:
                        raise Exception('No tokens in TikTok response')
                else:
                    raise Exception(f"Token exchange failed: {response.status_code} {response.text}")

            return await asyncio.to_thread(_sync_exchange)
        except Exception as e:
            print(f"Interactive authorization failed: {e}")
            return None

    def _generate_pkce(self) -> tuple[str, str]:
        """Generate PKCE code verifier and challenge for TikTok compatibility."""
        # Generate code verifier (43-128 characters, URL-safe)
        code_verifier = secrets.token_urlsafe(64)

        # Generate code challenge (SHA256 hash, hex encoded for TikTok)
        code_challenge = hashlib.sha256(code_verifier.encode()).hexdigest()

        return code_verifier, code_challenge

    async def _refresh_access_token(self) -> dict:
        """
        Refresh TikTok access token using direct HTTP request.
        """
        def _sync_refresh():
            import requests
            data = {
                'client_key': self.client_key,
                'client_secret': self.client_secret,
                'grant_type': 'refresh_token',
                'refresh_token': self.refresh_token
            }
            response = requests.post('https://open.tiktokapis.com/v2/oauth/token/', data=data, timeout=30)
            if response.status_code == 200:
                return response.json()
            else:
                raise Exception(f"Token refresh failed: {response.status_code} {response.text}")

        return await asyncio.to_thread(_sync_refresh)

    def _create_client(self, access_token: str) -> TikTokAPIClient:
        """Create TikTok API client instance."""
        return TikTokAPIClient(access_token=access_token)

    async def _get_user_info(self) -> dict:
        """Get creator information from TikTok API."""
        if not self.client:
            raise Exception('No client available')

        def _sync_get_info():
            if not self.client:
                raise Exception('No client available')

            user_data = self.client.get_user_info()

            # Verify username matches
            username = user_data.get('creator_username')
            if username != self.username:
                raise Exception(f'Username mismatch: {username} != {self.username}')

            return user_data

        return await asyncio.to_thread(_sync_get_info)

    def _validate_credentials(self) -> bool:
        """Validate that all required credentials are present."""
        return all([self.username, self.client_key, self.client_secret])

    def _get_platform_name(self) -> str:
        """Get the platform name for this auth manager."""
        return 'tiktok'

    def _get_token_identifier(self) -> str:
        """Get unique identifier for token storage."""
        return self.username

    def _save_credentials_to_storage(self):
        """Save all TikTok credentials to secure storage."""
        platform_name = self._get_platform_name()
        identifier = self._get_token_identifier()

        token_data = {
            'username': self.username,
            'client_key': self.client_key,
            'client_secret': self.client_secret,
            'refresh_token': self.refresh_token
        }

        self.token_storage.save_token(platform_name, identifier, token_data)
        # Also save as default so it becomes the primary credential loaded
        self.token_storage.save_token(platform_name, "default", token_data)

    def _load_credentials_from_storage(self) -> bool:
        """Load TikTok credentials from secure storage."""
        platform_name = self._get_platform_name()

        # Try to load with default identifier first
        identifier = "default"
        token_data = self.token_storage.load_token(platform_name, identifier)

        if not token_data:
            # If no default, try to find any stored token
            tokens = self.token_storage.list_tokens(platform_name)
            if tokens:
                # Use the first available token
                identifier = tokens[0][1]
                token_data = self.token_storage.load_token(platform_name, identifier)

        if token_data:
            # Load all credentials from the token data
            self.username = token_data.get('username')
            self.client_key = token_data.get('client_key')
            self.client_secret = token_data.get('client_secret')
            self.refresh_token = token_data.get('refresh_token')

            return bool(all([self.username, self.client_key, self.client_secret, self.refresh_token]))

        return False
