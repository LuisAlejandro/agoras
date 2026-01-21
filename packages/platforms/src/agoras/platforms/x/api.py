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

from typing import List, Optional

from agoras.core.api_base import BaseAPI

from .auth import XAuthManager


class XAPI(BaseAPI):
    """
    X API handler that centralizes X operations.

    Provides methods for X authentication and all X API operations
    including tweets, likes, retweets, and media uploads using both v1.1 and v2 APIs.
    """

    def __init__(self, consumer_key, consumer_secret, oauth_token, oauth_secret):
        """
        Initialize X API instance.

        Args:
            consumer_key (str): X consumer key
            consumer_secret (str): X consumer secret
            oauth_token (str): X OAuth token
            oauth_secret (str): X OAuth secret
        """
        super().__init__(
            access_token=oauth_token,
            client_id=consumer_key,
            client_secret=consumer_secret
        )

        # Initialize the authentication manager
        self.auth_manager = XAuthManager(
            consumer_key=consumer_key,
            consumer_secret=consumer_secret,
            oauth_token=oauth_token,
            oauth_secret=oauth_secret
        )

    @property
    def consumer_key(self):
        """Get the Twitter consumer key from the auth manager."""
        return self.auth_manager.consumer_key if self.auth_manager else None

    @property
    def consumer_secret(self):
        """Get the Twitter consumer secret from the auth manager."""
        return self.auth_manager.consumer_secret if self.auth_manager else None

    @property
    def oauth_token(self):
        """Get the Twitter OAuth token from the auth manager."""
        return self.auth_manager.oauth_token if self.auth_manager else None

    @property
    def oauth_secret(self):
        """Get the Twitter OAuth secret from the auth manager."""
        return self.auth_manager.oauth_secret if self.auth_manager else None

    @property
    def access_token(self):
        """Get the Twitter access token from the auth manager."""
        return self.auth_manager.access_token if self.auth_manager else None

    @property
    def user_info(self):
        """Get the Twitter user info from the auth manager."""
        return self.auth_manager.user_info if self.auth_manager else None

    async def authenticate(self):
        """
        Authenticate with X API using the auth manager.

        Returns:
            XAPI: Self for method chaining

        Raises:
            Exception: If authentication fails
        """
        if self._authenticated:
            return self

        success = await self.auth_manager.authenticate()
        if not success:
            raise Exception('X authentication failed')

        # Set the client from auth manager for BaseAPI compatibility
        self.client = self.auth_manager.client
        self._authenticated = True
        return self

    async def disconnect(self):
        """
        Disconnect from X API and clean up resources.
        """
        # Disconnect the client first
        if self.client:
            self.client.disconnect()

        # Clear auth manager data
        if self.auth_manager:
            self.auth_manager.access_token = None

        # Clear BaseAPI client
        self.client = None
        self._authenticated = False

    async def upload_media(self, media_content: bytes, media_type: str) -> str:
        """
        Upload media to X.

        Args:
            media_content (bytes): Raw media content
            media_type (str): Media MIME type

        Returns:
            str: Media ID

        Raises:
            Exception: If media upload fails
        """
        if not self._authenticated or not self.client:
            raise Exception('X API not authenticated')

        await self._rate_limit_check('upload_media', 1.0)

        try:
            media_id = await self.client.upload_media(media_content, media_type)
            return media_id
        except Exception as e:
            self._handle_api_error(e, 'X media upload')
            raise

    async def post(self, text: str, media_ids: Optional[List[str]] = None) -> str:
        """
        Create a tweet (post).

        Args:
            text (str): Tweet text content
            media_ids (list, optional): List of media IDs

        Returns:
            str: Tweet ID

        Raises:
            Exception: If tweet creation fails
        """
        if not self._authenticated or not self.client:
            raise Exception('X API not authenticated')

        await self._rate_limit_check('post', 1.0)

        # X has a 280 character limit
        if len(text) > 280:
            text = text[:277] + '...'

        try:
            tweet_id = await self.client.create_tweet(text, media_ids)
            return tweet_id
        except Exception as e:
            self._handle_api_error(e, 'X tweet creation')
            raise

    async def like(self, tweet_id: str) -> str:
        """
        Like a tweet.

        Args:
            tweet_id (str): Tweet ID to like

        Returns:
            str: Tweet ID

        Raises:
            Exception: If like operation fails
        """
        if not self._authenticated or not self.client:
            raise Exception('X API not authenticated')

        await self._rate_limit_check('like', 0.5)

        try:
            result = await self.client.like_tweet(tweet_id)
            return result
        except Exception as e:
            self._handle_api_error(e, 'X like')
            raise

    async def share(self, tweet_id: str) -> str:
        """
        Retweet (share) a tweet.

        Args:
            tweet_id (str): Tweet ID to retweet

        Returns:
            str: Tweet ID

        Raises:
            Exception: If retweet operation fails
        """
        if not self._authenticated or not self.client:
            raise Exception('X API not authenticated')

        await self._rate_limit_check('share', 0.5)

        try:
            result = await self.client.retweet(tweet_id)
            return result
        except Exception as e:
            self._handle_api_error(e, 'X retweet')
            raise

    async def delete(self, tweet_id: str) -> str:
        """
        Delete a tweet.

        Args:
            tweet_id (str): Tweet ID to delete

        Returns:
            str: Tweet ID

        Raises:
            Exception: If deletion fails
        """
        if not self._authenticated or not self.client:
            raise Exception('X API not authenticated')

        await self._rate_limit_check('delete', 0.5)

        try:
            result = await self.client.delete_tweet(tweet_id)
            return result
        except Exception as e:
            self._handle_api_error(e, 'X delete')
            raise
