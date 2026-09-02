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
"""agoras.platforms.x.auth module."""

import asyncio
import sys
import webbrowser
from typing import Optional, cast

from authlib.integrations.requests_client import OAuth1Session
from requests import Session
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from agoras.core.auth import BaseAuthManager
from agoras.core.auth.callback_server import OAuthCallbackServer

from .client import XAPIClient

OAUTH_HTTP_TIMEOUT = 30


class XAuthManager(BaseAuthManager):
    """X authentication manager using Authlib OAuth1Session for OAuth 1.0a."""

    def __init__(
        self,
        consumer_key: Optional[str] = None,
        consumer_secret: Optional[str] = None,
        oauth_token: Optional[str] = None,
        oauth_secret: Optional[str] = None,
        profile: Optional[str] = None,
    ):
        """
        Initialize X authentication manager.

        Args:
            consumer_key (str): X consumer key
            consumer_secret (str): X consumer secret
            oauth_token (str, optional): X OAuth token (if already obtained)
            oauth_secret (str, optional): X OAuth secret (if already obtained)
            profile (str, optional): Explicit profile composite (app-derived key)
        """
        super().__init__()
        self.profile = profile
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret
        self.oauth_token = oauth_token
        self.oauth_secret = oauth_secret
        self.subscription_type: Optional[str] = None

    async def authenticate(self) -> bool:
        """
        Authenticate with X API using OAuth 1.0a credentials.

        Returns:
            bool: True if authentication successful, False otherwise
        """
        self.last_auth_failure = None
        # Validate all credentials are present (fail fast if missing)
        if not self._validate_credentials():
            return self._missing_credentials_failed()

        try:
            # For Twitter OAuth 1.0a, we use the oauth_token as the access_token
            self.access_token = self.oauth_token

            # Create client and authenticate it
            if self.access_token and self.oauth_token and self.oauth_secret:
                self.client = self._create_client()
                await self.client.authenticate()

            return True
        except Exception as exc:
            return self._authentication_failed(exc)

    def _has_stored_or_env_credentials(self) -> bool:
        return self._validate_credentials()

    async def authorize(self) -> Optional[str]:
        """
        Authorize X account and store credentials.

        Returns:
            str: Success message if authorization successful, None otherwise
        """
        if not self._validate_basic_credentials():
            raise Exception("X consumer key and secret are required for authorization.")

        # If OAuth tokens are already provided, just save them
        if self.oauth_token and self.oauth_secret:
            await self._refresh_and_store_subscription_type()
            self._save_credentials_to_storage()
            return self._authorize_success_message()

        # Interactive mode with callback server
        return await self._authorize_interactive()

    def _authorize_success_message(self) -> str:
        """Build authorize result message; warn when Premium tier was not detected."""
        base = "Authorization successful. Credentials stored securely."
        if self.subscription_type is None:
            return (
                f"{base} Warning: X Premium subscription was not detected; "
                "free-tier (280) text limits will apply until subscription_type is stored."
            )
        return base

    async def _refresh_and_store_subscription_type(self) -> None:
        """Fetch subscription_type via API v2; keep prior stored tier on failure."""
        previous = self.subscription_type
        if previous is None:
            previous = self.load_subscription_type_from_storage()
        try:
            client = self._create_client()
            await client.authenticate()
            self.subscription_type = await client.get_subscription_type()
            client.disconnect()
        except Exception as exc:
            # Fail closed to free-tier limits when lookup fails and nothing was stored
            print(f"Warning: could not fetch X subscription_type: {exc}", file=sys.stderr)
            if previous:
                print(
                    f"Warning: keeping previously stored subscription_type={previous}",
                    file=sys.stderr,
                )
                self.subscription_type = previous
            else:
                print(
                    "Warning: Premium was not detected; free-tier (280) limits will apply.",
                    file=sys.stderr,
                )
                self.subscription_type = None

    async def _authorize_interactive(self) -> Optional[str]:
        """Authorize using local callback server (interactive mode)."""
        try:
            # Create OAuth session for authorization
            oauth_session = OAuth1Session(client_id=self.consumer_key, client_secret=self.consumer_secret)
            no_retries = HTTPAdapter(max_retries=Retry(total=0, connect=0, read=0))
            session = cast(Session, oauth_session)
            session.mount("https://", no_retries)
            session.mount("http://", no_retries)
            self.oauth_session = oauth_session

            callback_server = OAuthCallbackServer(oauth_version="1.0a", port=3456)
            redirect_uri = "https://localhost:3456/callback"

            def _sync_oauth_flow():
                request_token_url = "https://api.x.com/oauth/request_token"
                self.oauth_session.redirect_uri = redirect_uri

                print(
                    f"Requesting OAuth request token from X API (timeout {OAUTH_HTTP_TIMEOUT}s)...",
                    file=sys.stderr,
                    flush=True,
                )
                request_token = self.oauth_session.fetch_request_token(
                    request_token_url,
                    timeout=OAUTH_HTTP_TIMEOUT,
                )

                authorization_url = "https://api.x.com/oauth/authorize"
                auth_url = f"{authorization_url}?oauth_token={request_token['oauth_token']}"

                print("Opening browser for X authorization...", file=sys.stderr, flush=True)
                print(f"Authorization URL: {auth_url}", file=sys.stderr, flush=True)
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
                access_token_url = "https://api.x.com/oauth/access_token"
                print(
                    f"Exchanging OAuth verifier for access token (timeout {OAUTH_HTTP_TIMEOUT}s)...",
                    file=sys.stderr,
                    flush=True,
                )
                access_token = self.oauth_session.fetch_access_token(
                    access_token_url,
                    timeout=OAUTH_HTTP_TIMEOUT,
                )

                self.oauth_token = access_token["oauth_token"]
                self.oauth_secret = access_token["oauth_token_secret"]

            await asyncio.to_thread(_sync_complete_oauth)
            await self._refresh_and_store_subscription_type()
            self._save_credentials_to_storage()

            return self._authorize_success_message()

        except Exception as e:
            error = str(e)
            if "timed out" in error.lower() or "timeout" in error.lower():
                raise Exception(
                    "X authorization failed: could not reach api.x.com within "
                    f"{OAUTH_HTTP_TIMEOUT}s. Check network connectivity and "
                    "whether api.x.com is blocked or unreachable from your network."
                ) from e
            raise Exception(f"X authorization failed: {error}") from e

    def _create_client(self) -> XAPIClient:
        """Create X API client instance."""
        if not self.oauth_token or not self.oauth_secret:
            raise Exception("OAuth tokens are required to create X client")

        consumer_key = self.consumer_key
        consumer_secret = self.consumer_secret
        if not consumer_key or not consumer_secret:
            raise Exception("Consumer key and secret are required to create X client")

        return XAPIClient(
            consumer_key=consumer_key,
            consumer_secret=consumer_secret,
            oauth_token=self.oauth_token,
            oauth_secret=self.oauth_secret,
        )

    async def _get_user_info(self) -> dict:
        """Get user information from X API."""
        if not self.client:
            raise Exception("No client available")

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

        if self.profile:
            return self.profile
        if self.consumer_key:
            return hashlib.md5(self.consumer_key.encode(), usedforsecurity=False).hexdigest()[:8]
        return "unbound"

    def _save_credentials_to_storage(self):
        """Save all X credentials to secure storage."""
        platform_name = self._get_platform_name()
        identifier = self._get_token_identifier()

        token_data = {
            "consumer_key": self.consumer_key,
            "consumer_secret": self.consumer_secret,
            "oauth_token": self.oauth_token,
            "oauth_secret": self.oauth_secret,
            "subscription_type": self.subscription_type,
        }

        self.token_storage.save_token(platform_name, identifier, token_data)

    def load_subscription_type_from_storage(self) -> Optional[str]:
        """Load stored subscription_type without requiring full re-auth."""
        platform_name = self._get_platform_name()
        identifier = self._get_token_identifier()
        token_data = self.token_storage.load_token(platform_name, identifier)
        if not token_data:
            return None
        return token_data.get("subscription_type")

    def load_subscription_type_for_active_oauth(self) -> Optional[str]:
        """
        Load subscription_type only when stored oauth matches this manager's tokens.

        Never adopts an unrelated list_tokens entry for tier selection — mismatch
        or missing bind fails closed to free (None).
        """
        if not self.oauth_token or not self.oauth_secret:
            return None

        platform_name = self._get_platform_name()
        identifier = self._get_token_identifier()
        token_data = self.token_storage.load_token(platform_name, identifier)
        if not token_data:
            return None

        if token_data.get("oauth_token") != self.oauth_token or token_data.get("oauth_secret") != self.oauth_secret:
            return None

        return token_data.get("subscription_type")

    def _load_credentials_from_storage(self) -> bool:
        """Load X credentials from secure storage."""
        platform_name = self._get_platform_name()

        identifier = self._get_token_identifier()
        token_data = self.token_storage.load_token(platform_name, identifier)

        if not token_data and self.profile is None:
            # Restore the pre-refactor single-token auto-load: when no profile
            # is selected and exactly one non-reserved token exists for the
            # platform, adopt it (no silent first-listed pick among several).
            loadable = []
            for stored_platform, stored_identifier in self.token_storage.list_tokens(platform_name):
                if stored_platform != platform_name:
                    continue
                candidate = self.token_storage.load_token(platform_name, stored_identifier)
                if candidate is None:
                    continue
                loadable.append((stored_identifier, candidate))
            if len(loadable) == 1:
                self.profile = loadable[0][0]
                token_data = loadable[0][1]

        if token_data:
            self.consumer_key = token_data.get("consumer_key")
            self.consumer_secret = token_data.get("consumer_secret")
            self.oauth_token = token_data.get("oauth_token")
            self.oauth_secret = token_data.get("oauth_secret")
            self.subscription_type = token_data.get("subscription_type")
            return bool(all([self.consumer_key, self.consumer_secret, self.oauth_token, self.oauth_secret]))

        return False
