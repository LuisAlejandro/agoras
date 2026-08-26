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
"""agoras.platforms.linkedin.auth module."""

import asyncio
import os
import secrets
import sys
import webbrowser
from typing import Optional

from authlib.integrations.requests_client import OAuth2Session

from agoras.core.auth import BaseAuthManager
from agoras.core.auth.callback_server import OAuthCallbackServer
from agoras.core.auth.failure import env_has_refresh_token

from .client import LinkedInAPIClient


class LinkedInAuthManager(BaseAuthManager):
    """LinkedIn authentication manager using Authlib OAuth2Session for OAuth 2.0."""

    def __init__(
        self,
        user_id: str,
        client_id: str,
        client_secret: str,
        refresh_token: Optional[str] = None,
        access_token: Optional[str] = None,
    ):
        """
        Initialize LinkedIn authentication manager.

        Args:
            user_id (str): LinkedIn user ID (object ID)
            client_id (str): LinkedIn client ID
            client_secret (str): LinkedIn client secret
            refresh_token (str, optional): LinkedIn refresh token
            access_token (str, optional): LinkedIn access token (used when no refresh token)
        """
        super().__init__()
        self.user_id = user_id
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token = access_token
        self.refresh_token = refresh_token or self._load_refresh_token_from_storage()
        if not self.access_token:
            self.access_token = self._load_access_token_from_storage()
        self.api_version = "202503"

        # Authlib OAuth2Session configuration for LinkedIn
        self.oauth_session = OAuth2Session(
            client_id=self.client_id,
            client_secret=self.client_secret,
            scope="openid profile email w_member_social",
            redirect_uri="https://localhost:3456/callback",
        )

    async def authenticate(self) -> bool:
        """
        Authenticate with LinkedIn API using Authlib OAuth2Session.

        Returns:
            bool: True if authentication successful, False otherwise
        """
        self.last_auth_failure = None
        if not self._validate_credentials():
            return self._missing_credentials_failed()

        # Fail fast when no stored token material (don't trigger OAuth interactively)
        if not self.refresh_token and not self.access_token:
            return self._missing_credentials_failed()

        try:
            if self.refresh_token:
                # Refresh access token using authlib's built-in method
                token_data = await self._refresh_access_token_with_authlib()
                self.access_token = token_data["access_token"]

                # Update refresh token if new one provided
                if token_data.get("refresh_token") and token_data["refresh_token"] != self.refresh_token:
                    self.refresh_token = token_data["refresh_token"]
                    # Save all credentials to storage
                    self._save_credentials_to_storage()
            # Standard LinkedIn apps only issue 60-day access tokens (no refresh token)

            # Create client and get user info
            if self.access_token:
                self.client = self._create_client(self.access_token)
                self.user_info = await self._get_user_info()

            return True
        except Exception as exc:
            return self._authentication_failed(exc)

    async def authorize(self) -> Optional[str]:
        """
        Run LinkedIn OAuth authorization flow using Authlib.

        Uses interactive mode with local callback server.

        Returns:
            str or None: The refresh token if successful, None if failed
        """
        if not self._validate_credentials():
            raise Exception("LinkedIn credentials are required for authorization.")

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
                "https://www.linkedin.com/oauth/v2/authorization", state=state
            )

            print("Opening browser for LinkedIn authorization...", file=sys.stderr)
            print(f"If browser doesn't open automatically, visit: {authorization_url}", file=sys.stderr)
            webbrowser.open(authorization_url)

            auth_code = await callback_server.start_and_wait(timeout=300)

            def _sync_exchange():
                token = self.oauth_session.fetch_token(
                    "https://www.linkedin.com/oauth/v2/accessToken",
                    code=auth_code,
                    redirect_uri=redirect_uri,
                    client_secret=self.client_secret,
                )

                access_token = token.get("access_token")
                if not access_token:
                    raise Exception("No access token in LinkedIn response")

                refresh_token = token.get("refresh_token")
                if refresh_token:
                    self.refresh_token = refresh_token
                else:
                    print(
                        "Note: LinkedIn did not return a refresh token (normal for standard apps). "
                        "The access token is valid for about 60 days; re-run authorize before it expires.",
                        file=sys.stderr,
                    )

                self.access_token = access_token
                return access_token

            access_token = await asyncio.to_thread(_sync_exchange)
            if access_token:
                # Create temporary client to get user info and update user_id
                temp_client = self._create_client(access_token)
                await temp_client.authenticate()  # Authenticate the client first
                # Get the actual LinkedIn user ID from API
                user_info = await temp_client.get_user_info()
                api_user_id = user_info.get("sub", "")
                if api_user_id:
                    # Update user_id to the API's user ID
                    self.user_id = api_user_id

                # Save all credentials to storage with correct user_id
                self._save_credentials_to_storage()
                return access_token
        except Exception as e:
            print(f"Interactive authorization failed: {e}", file=sys.stderr)
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
                    token_url="https://www.linkedin.com/oauth/v2/accessToken", refresh_token=self.refresh_token
                )
                return token_data
            except Exception as exc:
                raise Exception(f"Token refresh failed: 401 {exc}") from exc

        return await asyncio.to_thread(_sync_refresh)

    def _create_client(self, access_token: str) -> LinkedInAPIClient:
        """Create LinkedIn API client instance."""
        return LinkedInAPIClient(access_token=access_token)

    async def _get_user_info(self) -> dict:
        """Get user information from LinkedIn API."""
        if not self.client:
            raise Exception("No client available")

        # Authenticate the client first
        await self.client.authenticate()

        try:
            # Get user info using LinkedIn API client
            result = await self.client.get_user_info()

            # Extract object_id
            object_id = result.get("sub", "")
            if not object_id:
                raise Exception("Unable to get LinkedIn object ID from user info")

            # Return enriched user data
            return {
                "object_id": object_id,
                "sub": object_id,
                "name": result.get("name", ""),
                "given_name": result.get("given_name", ""),
                "family_name": result.get("family_name", ""),
                "email": result.get("email", ""),
                "picture": result.get("picture", ""),
                "locale": result.get("locale", ""),
            }
        except Exception as e:
            raise Exception(f"Failed to get LinkedIn user info: {str(e)}")

    def _validate_credentials(self) -> bool:
        """Validate that all required credentials are present."""
        # For authentication/token refresh, we need client_id and client_secret
        # user_id is used for storage identification but not strictly required for auth
        return all([self.client_id, self.client_secret])

    def _get_platform_name(self) -> str:
        """Get the platform name for this auth manager."""
        return "linkedin"

    def _get_token_identifier(self) -> str:
        """Get unique identifier for token storage."""
        return self.user_id or "default"

    def _has_stored_or_env_credentials(self) -> bool:
        """Return True when stored or env credentials appear present for LinkedIn."""
        if self._load_credentials_from_storage():
            return bool(self.refresh_token or self.access_token)
        if env_has_refresh_token("linkedin"):
            return True
        return bool(os.environ.get("LINKEDIN_ACCESS_TOKEN"))

    def _load_and_refresh_from_storage(self) -> bool:
        """Load credentials from storage and authenticate (refresh or use access token)."""
        try:
            if not self._load_credentials_from_storage():
                return False
            if not (self.refresh_token or self.access_token):
                return False

            loop = asyncio.get_event_loop()
            if loop.is_running():
                return True
            return loop.run_until_complete(self.authenticate())
        except Exception as exc:
            return self._authentication_failed(exc)

    def _load_access_token_from_storage(self) -> Optional[str]:
        """Load access token from secure storage."""
        platform_name = self._get_platform_name()
        identifier = self._get_token_identifier()

        token_data = self.token_storage.load_token(platform_name, identifier)
        if token_data:
            return token_data.get("access_token")

        return None

    def _save_credentials_to_storage(self):
        """Save all LinkedIn credentials to secure storage."""
        platform_name = self._get_platform_name()
        identifier = self._get_token_identifier()

        token_data = {
            "user_id": self.user_id,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "refresh_token": self.refresh_token,
        }
        if self.access_token:
            token_data["access_token"] = self.access_token

        self.token_storage.save_token(platform_name, identifier, token_data)
        # Also save as default so it becomes the primary credential loaded
        self.token_storage.save_token(platform_name, "default", token_data)

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
                self.user_id = token_data.get("user_id")
            if not self.client_id:
                self.client_id = token_data.get("client_id")
            if not self.client_secret:
                self.client_secret = token_data.get("client_secret")
            if not self.refresh_token:
                self.refresh_token = token_data.get("refresh_token")
            if not self.access_token:
                self.access_token = token_data.get("access_token")

            has_core = all([self.user_id, self.client_id, self.client_secret])
            has_token = bool(self.refresh_token or self.access_token)
            return bool(has_core and has_token)

        return False
