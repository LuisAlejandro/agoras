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
"""agoras.platforms.x.api module."""

from typing import Any, Dict, List, Optional

from agoras.core.api_base import (
    BaseAPI,
    guard_assert_auth,
    guard_error_wrap,
    guard_rate_limit,
)
from agoras.core.auth import raise_authentication_error_from_manager
from agoras.core.text_limits import validate_text, x_mode_for_subscription

from .auth import XAuthManager


class XAPI(BaseAPI):
    """
    X API handler that centralizes X operations.

    Provides methods for X authentication and all X API operations
    including tweets, likes, retweets, and media uploads using both v1.1 and v2 APIs.
    """

    # Guard message template (read by the composable guard decorators)
    _not_authenticated_message = "X API not authenticated"

    def __init__(self, consumer_key, consumer_secret, oauth_token, oauth_secret):
        """
        Initialize X API instance.

        Args:
            consumer_key (str): X consumer key
            consumer_secret (str): X consumer secret
            oauth_token (str): X OAuth token
            oauth_secret (str): X OAuth secret
        """
        super().__init__(access_token=oauth_token, client_id=consumer_key, client_secret=consumer_secret)

        # Initialize the authentication manager
        self.auth_manager = XAuthManager(
            consumer_key=consumer_key,
            consumer_secret=consumer_secret,
            oauth_token=oauth_token,
            oauth_secret=oauth_secret,
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
            raise_authentication_error_from_manager(self.auth_manager)

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

    @guard_assert_auth
    @guard_rate_limit("upload_media", 1.0)
    @guard_error_wrap("X media upload")
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
        assert self.client is not None
        media_id = await self.client.upload_media(media_content, media_type)
        return media_id

    def _subscription_type(self) -> Optional[str]:
        """Return stored X subscription type when available (fail closed to free)."""
        user_info = self.user_info if isinstance(self.user_info, dict) else None
        if user_info:
            return user_info.get("subscription_type") or user_info.get("subscription_type_v2")
        return None

    @guard_assert_auth
    @guard_rate_limit("post", 1.0)
    async def post(
        self,
        text: str,
        media_ids: Optional[List[str]] = None,
        in_reply_to_tweet_id: Optional[str] = None,
        *,
        validate: bool = True,
    ) -> str:
        """
        Create a tweet (post).

        Args:
            text (str): Tweet text content
            media_ids (list, optional): List of media IDs
            in_reply_to_tweet_id (str, optional): Parent tweet ID for reply chains
            validate (bool): When True, reject over-limit text via weighted limits

        Returns:
            str: Tweet ID

        Raises:
            Exception: If tweet creation fails
        """
        if validate:
            mode = x_mode_for_subscription(self._subscription_type())
            validate_text("twitter", "text", text, mode=mode)

        try:
            assert self.client is not None
            tweet_id = await self.client.create_tweet(text, media_ids, in_reply_to_tweet_id=in_reply_to_tweet_id)
            return tweet_id
        except Exception as e:
            self._handle_api_error(e, "X tweet creation")
            raise

    @guard_assert_auth
    @guard_rate_limit("like", 0.5)
    @guard_error_wrap("X like")
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
        assert self.client is not None
        result = await self.client.like_tweet(tweet_id)
        return result

    @guard_assert_auth
    @guard_rate_limit("post", 1.0)
    @guard_error_wrap("X reply creation")
    async def reply(
        self, text: str, media_ids: Optional[List[str]] = None, in_reply_to_tweet_id: Optional[str] = None
    ) -> str:
        """
        Reply to a tweet.

        Args:
            text (str): Reply text content
            media_ids (list, optional): List of media IDs
            in_reply_to_tweet_id (str): Parent tweet ID to reply to

        Returns:
            str: Reply tweet ID

        Raises:
            Exception: If reply creation fails
        """
        assert self.client is not None
        tweet_id = await self.client.create_tweet(text, media_ids, in_reply_to_tweet_id=in_reply_to_tweet_id)
        return tweet_id

    @guard_assert_auth
    @guard_rate_limit("share", 0.5)
    @guard_error_wrap("X retweet")
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
        assert self.client is not None
        result = await self.client.retweet(tweet_id)
        return result

    @guard_assert_auth
    @guard_rate_limit("delete", 0.5)
    @guard_error_wrap("X delete")
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
        assert self.client is not None
        result = await self.client.delete_tweet(tweet_id)
        return result

    @guard_assert_auth
    @guard_rate_limit("get_post", 0.5)
    @guard_error_wrap("X get-post")
    async def get_post(self, tweet_id: str) -> Dict[str, Any]:
        """
        Read a tweet by ID.

        Args:
            tweet_id (str): Tweet ID to read

        Returns:
            dict: Tweet content fields

        Raises:
            Exception: If the tweet cannot be read
        """
        assert self.client is not None
        return await self.client.get_tweet(tweet_id)

    @guard_assert_auth
    @guard_rate_limit("list_posts", 0.5)
    @guard_error_wrap("X list-posts")
    async def list_posts(self, limit: int) -> List[Dict[str, Any]]:
        """
        List the authenticated user's recent tweets.

        Args:
            limit (int): Maximum number of tweets to return

        Returns:
            list: Tweet content fields

        Raises:
            Exception: If the tweets cannot be read
        """
        assert self.client is not None
        user_info = await self.client.get_user_info()
        user_id = user_info.get("user_id")
        if not user_id:
            raise Exception("Unable to resolve X user id for list-posts.")
        assert self.client is not None
        return await self.client.get_users_tweets(user_id, limit)
