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
from ..clients.tiktok import TikTokAPIClient


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
        self.refresh_token = refresh_token or self._load_refresh_token_from_cache()
        
        # Authlib OAuth2Session configuration for TikTok with PKCE
        self.oauth_session = OAuth2Session(
            client_id=self.client_key,
            client_secret=self.client_secret,
            scope="user.info.basic,video.upload,video.publish",
            redirect_uri="http://localhost:3456/callback",
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

        # If we don't have a refresh token, need to authorize first
        if not self.refresh_token:
            self.refresh_token = await self.authorize()
            if not self.refresh_token:
                return False

        try:
            # Refresh access token using authlib's built-in method with TikTok compliance
            token_data = await self._refresh_access_token()
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
        Run TikTok OAuth authorization flow using Authlib with PKCE.

        Returns:
            str or None: The refresh token if successful, None if failed
        """
        if not self._validate_credentials():
            raise Exception('TikTok credentials are required for authorization.')

        try:
            def _sync_authorize():
                # Generate code verifier for PKCE
                code_verifier = self._generate_code_verifier()
                
                # Create authorization URL with PKCE
                authorization_url, state = self.oauth_session.create_authorization_url(
                    'https://www.tiktok.com/v2/auth/authorize/',
                    code_verifier=code_verifier
                )
                
                print("Opening browser for TikTok authorization...")
                print(f"Authorization URL: {authorization_url}")
                webbrowser.open(authorization_url)
                
                # Wait for user to complete authorization and provide callback URL
                callback_url = input("Please complete authorization in browser and paste the callback URL here: ")
                
                # Exchange authorization code for tokens with PKCE
                token = self.oauth_session.fetch_token(
                    'https://open.tiktokapis.com/v2/oauth/token/',
                    authorization_response=callback_url,
                    code_verifier=code_verifier
                )
                
                # Save the refresh token
                refresh_token = token.get('refresh_token')
                if refresh_token:
                    self._save_refresh_token_to_cache(refresh_token)
                    return refresh_token
                else:
                    raise Exception('No refresh token in TikTok response')

            return await asyncio.to_thread(_sync_authorize)
        except Exception:
            return None

    def _generate_code_verifier(self) -> str:
        """Generate a cryptographically secure code verifier for PKCE."""
        return secrets.token_urlsafe(64)

    async def _refresh_access_token(self) -> dict:
        """
        Refresh TikTok access token using authlib's built-in method.
        The compliance hook will convert client_id to client_key for TikTok's API.
        """
        def _sync_refresh():
            # Use authlib's refresh_token method
            token_data = self.oauth_session.refresh_token(
                token_url='https://open.tiktokapis.com/v2/oauth/token/',
                refresh_token=self.refresh_token
            )
            return token_data

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

    def _get_cache_filename(self) -> str:
        """Get cache filename for storing refresh token."""
        return f'tiktok-{self.username}.json'

    def _load_refresh_token_from_cache(self) -> Optional[str]:
        """Load refresh token from cache file."""
        cache_file = self._get_cache_filename()
        return self._load_token_from_cache(cache_file, 'tiktok_refresh_token')

    def _save_refresh_token_to_cache(self, refresh_token: str):
        """Save refresh token to cache file."""
        cache_file = self._get_cache_filename()
        self._save_token_to_cache(cache_file, 'tiktok_refresh_token', refresh_token) 