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
import webbrowser
from typing import Optional

from authlib.integrations.requests_client import OAuth1Session

from .base import BaseAuthManager
from ..clients.x import XAPIClient


class XAuthManager(BaseAuthManager):
    """X authentication manager using Authlib OAuth1Session for OAuth 1.0a."""

    def __init__(self, consumer_key: str, consumer_secret: str,
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
        self.oauth_token = oauth_token or self._load_oauth_token_from_cache()
        self.oauth_secret = oauth_secret or self._load_oauth_secret_from_cache()

        # Authlib OAuth1Session configuration for Twitter
        self.oauth_session = OAuth1Session(
            client_id=self.consumer_key,
            client_secret=self.consumer_secret,
            token=self.oauth_token if self.oauth_token and self.oauth_secret else None,
            token_secret=self.oauth_secret if self.oauth_token and self.oauth_secret else None
        )

    async def authenticate(self) -> bool:
        """
        Authenticate with X API using OAuth 1.0a credentials.

        Returns:
            bool: True if authentication successful, False otherwise
        """
        if not self._validate_basic_credentials():
            return False

        # If we don't have oauth tokens, need to authorize first
        if not self.oauth_token or not self.oauth_secret:
            tokens = await self.authorize()
            if not tokens:
                return False
            self.oauth_token, self.oauth_secret = tokens

        try:
            # For Twitter OAuth 1.0a, we use the oauth_token as the access_token
            self.access_token = self.oauth_token

            # Update OAuth session with tokens
            self.oauth_session.token = self.oauth_token
            self.oauth_session.token_secret = self.oauth_secret

            # Create client and get user info
            if self.access_token and self.oauth_token and self.oauth_secret:
                self.client = self._create_client()
                self.user_info = await self._get_user_info()

            return True
        except Exception:
            return False

    async def authorize(self) -> Optional[tuple]:
        """
        Run X OAuth 1.0a authorization flow using Authlib.

        Returns:
            tuple or None: (oauth_token, oauth_secret) if successful, None if failed
        """
        if not self._validate_basic_credentials():
            raise Exception('X consumer key and secret are required for authorization.')

        try:
            def _sync_authorize():
                # Step 1: Fetch request token
                request_token_url = 'https://api.twitter.com/oauth/request_token'
                self.oauth_session.redirect_uri = "http://localhost:3459/callback"

                request_token = self.oauth_session.fetch_request_token(request_token_url)

                # Step 2: Redirect to authorization URL
                authorization_url = 'https://api.twitter.com/oauth/authorize'
                auth_url = self.oauth_session.create_authorization_url(
                    authorization_url,
                    request_token['oauth_token']
                )

                print("Opening browser for X authorization...")
                print(f"Authorization URL: {auth_url}")
                webbrowser.open(auth_url)

                # Wait for user to complete authorization and provide callback URL
                callback_url = input("Please complete authorization in browser and paste the callback URL here: ")

                # Step 3: Parse authorization response and fetch access token
                self.oauth_session.parse_authorization_response(callback_url)

                access_token_url = 'https://api.twitter.com/oauth/access_token'
                access_token = self.oauth_session.fetch_access_token(access_token_url)

                oauth_token = access_token['oauth_token']
                oauth_secret = access_token['oauth_token_secret']

                # Save tokens to cache
                self._save_tokens_to_cache(oauth_token, oauth_secret)

                return oauth_token, oauth_secret

            return await asyncio.to_thread(_sync_authorize)
        except Exception:
            return None

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

        return await self.client.get_user_info()

    def _validate_basic_credentials(self) -> bool:
        """Validate that basic credentials (consumer key/secret) are present."""
        return all([self.consumer_key, self.consumer_secret])

    def _validate_credentials(self) -> bool:
        """Validate that all required credentials are present."""
        return all([self.consumer_key, self.consumer_secret, self.oauth_token, self.oauth_secret])

    def _get_cache_filename(self) -> str:
        """Get cache filename for storing OAuth tokens."""
        # Use consumer key as identifier since tokens are user-specific
        import hashlib
        key_hash = hashlib.md5(self.consumer_key.encode()).hexdigest()[:8]
        return f'x-{key_hash}.json'

    def _load_oauth_token_from_cache(self) -> Optional[str]:
        """Load OAuth token from cache file."""
        cache_file = self._get_cache_filename()
        return self._load_token_from_cache(cache_file, 'x_oauth_token')

    def _load_oauth_secret_from_cache(self) -> Optional[str]:
        """Load OAuth secret from cache file."""
        cache_file = self._get_cache_filename()
        return self._load_token_from_cache(cache_file, 'x_oauth_secret')

    def _save_tokens_to_cache(self, oauth_token: str, oauth_secret: str):
        """Save OAuth tokens to cache file."""
        cache_file = self._get_cache_filename()
        data = {
            'x_oauth_token': oauth_token,
            'x_oauth_secret': oauth_secret
        }
        self._save_cache_data(cache_file, data)
