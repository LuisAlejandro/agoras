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
import json
import os
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

from .exceptions import AuthenticationError
from .storage import SecureTokenStorage


class BaseAuthManager(ABC):
    """
    Base authentication manager class with common functionality.

    This abstract base class provides common patterns and methods used across
    all platform-specific authentication managers, including:
    - Common attributes and properties
    - Token caching mechanisms
    - Abstract methods for platform-specific implementations
    - Template method pattern for authentication flow
    """

    def __init__(self):
        """Initialize base authentication manager."""
        self.access_token: Optional[str] = None
        self.client = None
        self.user_info = None
        self.token_storage = SecureTokenStorage()

    @property
    def authenticated(self) -> bool:
        """Check if currently authenticated with valid access token."""
        return bool(self.access_token and self.client and self.user_info)

    def ensure_authenticated(self):
        """
        Ensure valid authentication state (Fail Fast).

        This method enforces the "Authorize First" workflow by checking if
        authentication is available. If not authenticated, it attempts to load
        and refresh credentials from secure storage. If no valid credentials
        exist, it tries to seed from environment variables (CI/CD support).
        If all attempts fail, it raises AuthenticationError.

        Raises:
            AuthenticationError: If not authenticated and no stored credentials available
        """
        if self.authenticated:
            return

        # Try to load from secure storage and refresh
        if not self._load_and_refresh_from_storage():
            # Before failing, check if we can seed from environment (CI/CD)
            if self._try_seed_from_environment():
                # Retry loading after seeding
                if self._load_and_refresh_from_storage():
                    return

            platform_name = self._get_platform_name()
            raise AuthenticationError(
                f"Not authenticated. Please run 'agoras {platform_name} authorize' first."
            )

    def _load_and_refresh_from_storage(self) -> bool:
        """
        Load credentials from secure storage and refresh if needed.

        Returns:
            bool: True if successfully loaded and refreshed, False otherwise
        """
        try:
            # Extract refresh token
            refresh_token = self._load_refresh_token_from_storage()
            if not refresh_token:
                return False

            # Set the refresh token so authenticate() can use it
            if hasattr(self, 'refresh_token'):
                self.refresh_token = refresh_token

            # Call authenticate to refresh and get access token
            # This is async, but we need to handle it synchronously here
            import asyncio
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # If we're already in an async context, this is tricky
                # For now, we'll set the refresh_token and let authenticate handle it
                return True
            else:
                result = loop.run_until_complete(self.authenticate())
                return result
        except Exception:
            return False

    def _load_refresh_token_from_storage(self) -> Optional[str]:
        """
        Load refresh token from secure storage.

        Returns:
            str or None: Refresh token if found, None otherwise
        """
        platform_name = self._get_platform_name()
        identifier = self._get_token_identifier()

        token_data = self.token_storage.load_token(platform_name, identifier)

        if token_data:
            return token_data.get('refresh_token')

        return None

    def _load_refresh_token_from_env(self) -> Optional[str]:
        """
        Load refresh token from environment variable for CI/CD.

        Checks for AGORAS_{PLATFORM}_REFRESH_TOKEN environment variable.

        Returns:
            str or None: Refresh token from environment if found
        """
        platform = self._get_platform_name().upper()
        return os.environ.get(f'AGORAS_{platform}_REFRESH_TOKEN')

    def _try_seed_from_environment(self) -> bool:
        """
        Try to seed storage from environment variables (CI/CD support).

        Returns:
            bool: True if token was successfully seeded from environment
        """
        platform_name = self._get_platform_name()
        identifier = self._get_token_identifier()
        return self.token_storage.seed_from_environment(platform_name, identifier)

    @abstractmethod
    async def authenticate(self) -> bool:
        """
        Authenticate with the platform API.

        Returns:
            bool: True if authentication successful, False otherwise
        """

    @abstractmethod
    async def authorize(self) -> Optional[Any]:
        """
        Run platform-specific OAuth authorization flow.

        Returns:
            Any: Platform-specific authorization result (token, tuple, etc.)
        """

    @abstractmethod
    def _validate_credentials(self) -> bool:
        """
        Validate that all required credentials are present.

        Returns:
            bool: True if all required credentials are present
        """

    @abstractmethod
    def _create_client(self, *args, **kwargs):
        """
        Create platform-specific API client instance.

        Returns:
            API client instance for the platform
        """

    @abstractmethod
    async def _get_user_info(self) -> Dict[str, Any]:
        """
        Get user information from platform API.

        Returns:
            dict: User information from the platform
        """

    @abstractmethod
    def _get_platform_name(self) -> str:
        """
        Get the platform name for this auth manager.

        Returns:
            str: Platform name (e.g., 'facebook', 'instagram')
        """

    @abstractmethod
    def _get_token_identifier(self) -> str:
        """
        Get unique identifier for token storage (e.g., user_id, username).

        Returns:
            str: Unique identifier for this authentication session
        """

    async def _run_sync_in_thread(self, sync_func, *args, **kwargs):
        """
        Run synchronous function in thread using asyncio.

        Args:
            sync_func: Synchronous function to run
            *args: Arguments for the function
            **kwargs: Keyword arguments for the function

        Returns:
            Result of the synchronous function
        """
        return await asyncio.to_thread(sync_func, *args, **kwargs)
