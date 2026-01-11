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
import time
from abc import ABC, abstractmethod


class BaseAPI(ABC):
    """
    Abstract base class for social network API implementations.

    Provides common functionality and patterns for API interactions
    including authentication, rate limiting, and error handling.
    """

    def __init__(self, **credentials):
        """
        Initialize API instance with credentials.

        Args:
            **credentials: API-specific authentication credentials
        """
        self.credentials = credentials
        self.client = None
        self._authenticated = False
        self._rate_limit_cache = {}
        self._last_request_time = 0

    @abstractmethod
    async def authenticate(self):
        """
        Authenticate with the API asynchronously.

        Returns:
            BaseAPI: Self for method chaining

        Raises:
            Exception: If authentication fails
        """
        pass

    @abstractmethod
    async def disconnect(self):
        """
        Disconnect from the API and clean up resources.
        """
        pass

    def is_authenticated(self):
        """
        Check if API is authenticated.

        Returns:
            bool: True if authenticated, False otherwise
        """
        return self._authenticated

    async def _rate_limit_check(self, operation_type='default', min_interval=1.0):
        """
        Perform rate limiting check before API operations.

        Args:
            operation_type (str): Type of operation for specific limits
            min_interval (float): Minimum interval between requests in seconds
        """
        current_time = time.time()
        last_time = self._rate_limit_cache.get(operation_type, 0)

        if current_time - last_time < min_interval:
            sleep_time = min_interval - (current_time - last_time)
            await asyncio.sleep(sleep_time)

        self._rate_limit_cache[operation_type] = time.time()

    def _handle_api_error(self, error, operation_name):
        """
        Handle API errors with consistent error messages.

        Args:
            error: The exception that occurred
            operation_name (str): Name of the operation that failed

        Raises:
            Exception: Formatted exception with context
        """
        error_msg = f'{operation_name} failed: {str(error)}'
        raise Exception(error_msg) from error

    @abstractmethod
    async def post(self, *args, **kwargs):
        """
        Create a post on the social media platform.

        Returns:
            str: Post ID

        Raises:
            Exception: If posting fails
        """
        pass

    @abstractmethod
    async def like(self, post_id, *args, **kwargs):
        """
        Like/react to a post on the social media platform.

        Args:
            post_id (str): ID of the post to like

        Returns:
            str: Post ID

        Raises:
            Exception: If liking fails or not supported
        """
        pass

    @abstractmethod
    async def delete(self, post_id, *args, **kwargs):
        """
        Delete a post from the social media platform.

        Args:
            post_id (str): ID of the post to delete

        Returns:
            str: Post ID

        Raises:
            Exception: If deletion fails or not supported
        """
        pass

    @abstractmethod
    async def share(self, post_id, *args, **kwargs):
        """
        Share/repost a post on the social media platform.

        Args:
            post_id (str): ID of the post to share

        Returns:
            str: Share/Post ID

        Raises:
            Exception: If sharing fails or not supported
        """
        pass
