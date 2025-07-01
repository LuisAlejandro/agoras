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
from typing import Any, Dict, List, Optional

from .auth import ThreadsAuthManager
from .base import BaseAPI


class ThreadsAPI(BaseAPI):
    """
    Threads API handler that centralizes Threads operations.

    Provides methods for Threads authentication, post creation, replies,
    reposts, and all Threads API operations using threadspipepy.
    """

    def __init__(self, app_id: str, app_secret: str, redirect_uri: str,
                 refresh_token: Optional[str] = None):
        """
        Initialize Threads API instance.

        Args:
            app_id (str): Threads app ID
            app_secret (str): Threads app secret
            redirect_uri (str): OAuth redirect URI
            refresh_token (str, optional): Threads refresh token
        """
        super().__init__(
            app_id=app_id,
            app_secret=app_secret,
            redirect_uri=redirect_uri,
            refresh_token=refresh_token
        )

        # Initialize the authentication manager
        self.auth_manager = ThreadsAuthManager(
            app_id=app_id,
            app_secret=app_secret,
            redirect_uri=redirect_uri,
            refresh_token=refresh_token
        )

    @property
    def access_token(self):
        """Get the Threads access token from the auth manager."""
        return self.auth_manager.access_token if self.auth_manager else None

    @property
    def user_id(self):
        """Get the Threads user ID from the auth manager."""
        return self.auth_manager.user_id if self.auth_manager else None

    @property
    def user_info(self):
        """Get the Threads user info from the auth manager."""
        return self.auth_manager.user_info if self.auth_manager else None

    async def authenticate(self):
        """
        Authenticate with Threads API using the auth manager.

        Returns:
            ThreadsAPI: Self for method chaining

        Raises:
            Exception: If authentication fails
        """
        if self._authenticated:
            return self

        success = await self.auth_manager.authenticate()
        if not success:
            raise Exception('Threads authentication failed')

        self.client = self.auth_manager.client
        self._authenticated = True
        return self

    async def disconnect(self):
        """
        Disconnect from Threads API and clean up resources.
        """
        # Clear BaseAPI client
        self.client = None
        self._authenticated = False

    async def get_profile(self) -> Dict[str, Any]:
        """
        Get user profile information from Threads API.

        Returns:
            dict: User profile information

        Raises:
            Exception: If API call fails
        """
        if not self.access_token:
            raise Exception('Threads API not authenticated')

        def _sync_get_profile():
            if not self.client:
                raise Exception('Threads client not available')
            return self.client.get_profile()

        try:
            profile_info = await asyncio.to_thread(_sync_get_profile)
            return profile_info
        except Exception as e:
            self._handle_api_error(e, 'Threads get profile')
            raise

    async def create_post(self, post_text: str, files: Optional[List[str]] = None,
                          who_can_reply: str = "everyone") -> str:
        """
        Create a post on Threads.

        Args:
            post_text (str): Text content of the post
            files (list, optional): List of file URLs to attach
            who_can_reply (str): Who can reply to this post

        Returns:
            str: Post ID

        Raises:
            Exception: If post creation fails
        """
        if not self.access_token:
            raise Exception('Threads API not authenticated')

        if not self.client:
            raise Exception('Threads client not available')

        await self._rate_limit_check('create_post', 2.0)

        def _sync_create_post():
            if not self.client:
                raise Exception('Threads client not available')
            return self.client.create_post(
                post_text=post_text,
                files=files or [],
                who_can_reply=who_can_reply
            )

        try:
            response = await asyncio.to_thread(_sync_create_post)

            # Extract post ID from response
            post_id = response.get('id') or response.get('post_id') or str(response)
            return post_id
        except Exception as e:
            self._handle_api_error(e, 'Threads post creation')
            raise

    async def create_reply(self, reply_text: str, reply_to_id: str) -> str:
        """
        Create a reply to a specific post.

        Args:
            reply_text (str): Text content of the reply
            reply_to_id (str): ID of the post to reply to

        Returns:
            str: Reply ID

        Raises:
            Exception: If reply creation fails
        """
        if not self.access_token:
            raise Exception('Threads API not authenticated')

        if not self.client:
            raise Exception('Threads client not available')

        await self._rate_limit_check('create_reply', 2.0)

        def _sync_create_reply():
            if not self.client:
                raise Exception('Threads client not available')
            return self.client.create_reply(
                reply_text=reply_text,
                reply_to_id=reply_to_id
            )

        try:
            response = await asyncio.to_thread(_sync_create_reply)

            # Extract reply ID from response
            reply_id = response.get('id') or response.get('reply_id') or str(response)
            return reply_id
        except Exception as e:
            self._handle_api_error(e, 'Threads reply creation')
            raise

    async def repost_post(self, post_id: str) -> str:
        """
        Repost an existing post.

        Args:
            post_id (str): ID of the post to repost

        Returns:
            str: Repost ID

        Raises:
            Exception: If repost fails
        """
        if not self.access_token:
            raise Exception('Threads API not authenticated')

        if not self.client:
            raise Exception('Threads client not available')

        await self._rate_limit_check('repost_post', 2.0)

        def _sync_repost():
            if not self.client:
                raise Exception('Threads client not available')
            return self.client.repost_post(post_id=post_id)

        try:
            response = await asyncio.to_thread(_sync_repost)

            # Extract repost ID from response
            repost_id = response.get('id') or response.get('repost_id') or str(response)
            return repost_id
        except Exception as e:
            self._handle_api_error(e, 'Threads repost')
            raise

    async def get_posts(self, limit: int = 25) -> Dict[str, Any]:
        """
        Get user's posts.

        Args:
            limit (int): Maximum number of posts to retrieve

        Returns:
            dict: Posts data

        Raises:
            Exception: If API call fails
        """
        if not self.access_token:
            raise Exception('Threads API not authenticated')

        if not self.client:
            raise Exception('Threads client not available')

        await self._rate_limit_check('get_posts', 1.0)

        def _sync_get_posts():
            if not self.client:
                raise Exception('Threads client not available')
            return self.client.get_posts(limit=limit)

        try:
            response = await asyncio.to_thread(_sync_get_posts)
            return response
        except Exception as e:
            self._handle_api_error(e, 'Threads get posts')
            raise

    async def get_post_insights(self, post_id: str) -> Dict[str, Any]:
        """
        Get insights/analytics for a specific post.

        Args:
            post_id (str): ID of the post to get insights for

        Returns:
            dict: Post insights data

        Raises:
            Exception: If API call fails
        """
        if not self.access_token:
            raise Exception('Threads API not authenticated')

        if not self.client:
            raise Exception('Threads client not available')

        await self._rate_limit_check('get_post_insights', 1.0)

        def _sync_get_insights():
            if not self.client:
                raise Exception('Threads client not available')
            return self.client.get_post_insights(post_id=post_id)

        try:
            response = await asyncio.to_thread(_sync_get_insights)
            return response
        except Exception as e:
            self._handle_api_error(e, 'Threads get post insights')
            raise

    async def hide_reply(self, reply_id: str) -> str:
        """
        Hide a reply (moderation functionality).

        Args:
            reply_id (str): ID of the reply to hide

        Returns:
            str: Reply ID

        Raises:
            Exception: If API call fails
        """
        if not self.access_token:
            raise Exception('Threads API not authenticated')

        if not self.client:
            raise Exception('Threads client not available')

        await self._rate_limit_check('hide_reply', 1.0)

        def _sync_hide_reply():
            if not self.client:
                raise Exception('Threads client not available')
            return self.client.hide_reply(reply_id=reply_id)

        try:
            await asyncio.to_thread(_sync_hide_reply)
            return reply_id
        except Exception as e:
            self._handle_api_error(e, 'Threads hide reply')
            raise

    # BaseAPI abstract method implementations
    async def post(self, post_text: str, files: Optional[List[str]] = None) -> str:
        """
        Create a post on Threads (BaseAPI interface implementation).

        Args:
            post_text (str): Text content of the post
            files (list, optional): List of file URLs to attach

        Returns:
            str: Post ID
        """
        return await self.create_post(post_text, files)

    async def like(self, post_id: str) -> str:
        """
        Like a Threads post (not supported via API).

        Args:
            post_id (str): Post ID to like

        Raises:
            Exception: Like not supported for Threads
        """
        raise Exception('Like not supported for Threads')

    async def delete(self, post_id: str) -> str:
        """
        Delete a Threads post (not supported via API).

        Args:
            post_id (str): Post ID to delete

        Raises:
            Exception: Delete not supported for Threads
        """
        raise Exception('Delete not supported for Threads')

    async def share(self, post_id: str) -> str:
        """
        Share/repost a Threads post.

        Args:
            post_id (str): Post ID to share

        Returns:
            str: Share/Repost ID
        """
        return await self.repost_post(post_id)
