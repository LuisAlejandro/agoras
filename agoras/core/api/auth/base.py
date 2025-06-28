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
import json
import os
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


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

    @property
    def authenticated(self) -> bool:
        """Check if currently authenticated with valid access token."""
        return bool(self.access_token and self.client and self.user_info)

    @abstractmethod
    async def authenticate(self) -> bool:
        """
        Authenticate with the platform API.

        Returns:
            bool: True if authentication successful, False otherwise
        """
        pass

    @abstractmethod
    async def authorize(self) -> Optional[Any]:
        """
        Run platform-specific OAuth authorization flow.

        Returns:
            Any: Platform-specific authorization result (token, tuple, etc.)
        """
        pass

    @abstractmethod
    def _validate_credentials(self) -> bool:
        """
        Validate that all required credentials are present.

        Returns:
            bool: True if all required credentials are present
        """
        pass

    @abstractmethod
    def _create_client(self, *args, **kwargs):
        """
        Create platform-specific API client instance.

        Returns:
            API client instance for the platform
        """
        pass

    @abstractmethod
    async def _get_user_info(self) -> Dict[str, Any]:
        """
        Get user information from platform API.

        Returns:
            dict: User information from the platform
        """
        pass

    @abstractmethod
    def _get_cache_filename(self) -> str:
        """
        Get cache filename for storing platform-specific tokens.

        Returns:
            str: Cache filename
        """
        pass

    # Common utility methods for token caching
    def _load_token_from_cache(self, cache_file: str, token_key: str) -> Optional[str]:
        """
        Load token from cache file.

        Args:
            cache_file (str): Cache filename
            token_key (str): Key for the token in the cache file

        Returns:
            str or None: Token if found, None otherwise
        """
        if os.path.exists(cache_file):
            try:
                with open(cache_file, 'r') as f:
                    data = json.load(f)
                    return data.get(token_key)
            except Exception:
                pass
        return None

    def _save_token_to_cache(self, cache_file: str, token_key: str, token_value: str):
        """
        Save token to cache file.

        Args:
            cache_file (str): Cache filename
            token_key (str): Key for the token in the cache file
            token_value (str): Token value to save
        """
        data = {token_key: token_value}
        try:
            with open(cache_file, 'w') as f:
                json.dump(data, f)
        except Exception:
            pass  # Fail silently if can't save cache

    def _load_cache_data(self, cache_file: str) -> Dict[str, Any]:
        """
        Load all data from cache file.

        Args:
            cache_file (str): Cache filename

        Returns:
            dict: Cache data or empty dict if file doesn't exist or can't be read
        """
        if os.path.exists(cache_file):
            try:
                with open(cache_file, 'r') as f:
                    return json.load(f)
            except Exception:
                pass
        return {}

    def _save_cache_data(self, cache_file: str, data: Dict[str, Any]):
        """
        Save data to cache file.

        Args:
            cache_file (str): Cache filename
            data (dict): Data to save
        """
        try:
            with open(cache_file, 'w') as f:
                json.dump(data, f)
        except Exception:
            pass  # Fail silently if can't save cache

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