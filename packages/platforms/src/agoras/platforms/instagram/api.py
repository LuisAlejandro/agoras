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
"""agoras.platforms.instagram.api module."""

import asyncio
from typing import Any, Dict, List, Optional

from agoras.core.api_base import (
    BaseAPI,
    guard_client_presence,
    guard_ensure_auth_manager,
    guard_error_wrap,
    guard_rate_limit,
)
from agoras.core.auth import raise_authentication_error_from_manager

from .auth import InstagramAuthManager


class InstagramAPI(BaseAPI):
    """
    Instagram API handler that centralizes Instagram operations.

    Provides methods for Instagram authentication, token management,
    and all Instagram API operations including posts, videos, and media uploads.
    """

    # Guard message template (read by the composable guard decorators)
    _client_not_available_message = "Instagram API not authenticated"

    def __init__(self, user_id, client_id, client_secret, refresh_token=None):
        """
        Initialize Instagram API instance.

        Args:
            user_id (str): Facebook user ID for Instagram business account
            client_id (str): Facebook client ID for token refresh
            client_secret (str): Facebook client secret for token refresh
            refresh_token (str, optional): Instagram refresh token
        """
        super().__init__(user_id=user_id, client_id=client_id, client_secret=client_secret, refresh_token=refresh_token)

        # Initialize the authentication manager
        self.auth_manager = InstagramAuthManager(
            user_id=user_id, client_id=client_id, client_secret=client_secret, refresh_token=refresh_token
        )

    async def authenticate(self):
        """
        Authenticate with Instagram API using the auth manager.

        Returns:
            InstagramAPI: Self for method chaining

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
        Disconnect from Instagram API and clean up resources.
        """
        # Disconnect the client first
        if self.client:
            self.client.disconnect()

        # Clear auth manager tokens
        if self.auth_manager:
            self.auth_manager.access_token = None

        # Clear BaseAPI client
        self.client = None
        self._authenticated = False

    @guard_ensure_auth_manager
    @guard_client_presence
    @guard_rate_limit("post", 1.0)
    @guard_error_wrap("Instagram post creation")
    async def post(
        self,
        object_id: str,
        image_url: Optional[str] = None,
        caption: Optional[str] = None,
        video_url: Optional[str] = None,
    ) -> str:
        """
        Publish media to Instagram.

        Args:
            object_id (str): Instagram object ID
            image_url (str, optional): Image URL
            caption (str, optional): Post caption
            video_url (str, optional): Video URL (if posting video)

        Returns:
            str: Post ID

        Raises:
            Exception: If post creation fails
        """
        assert self.client is not None
        return await self.client.create_post(
            object_id=object_id, image_url=image_url, video_url=video_url, caption=caption
        )

    @guard_ensure_auth_manager
    @guard_client_presence
    @guard_rate_limit("create_media", 1.0)
    @guard_error_wrap("Instagram media creation")
    async def create_media(
        self,
        object_id: str,
        image_url: Optional[str] = None,
        video_url: Optional[str] = None,
        caption: Optional[str] = None,
        is_carousel_item: bool = False,
        media_type: Optional[str] = None,
    ) -> str:
        """
        Create media for Instagram post.

        Args:
            object_id (str): Instagram object ID
            image_url (str, optional): Image URL
            video_url (str, optional): Video URL
            caption (str, optional): Media caption
            is_carousel_item (bool): Whether this is part of a carousel
            media_type (str, optional): Media type (REELS, STORIES)

        Returns:
            str: Media ID

        Raises:
            Exception: If media creation fails
        """
        assert self.client is not None
        return await self.client.create_media(
            object_id=object_id,
            image_url=image_url,
            video_url=video_url,
            caption=caption,
            is_carousel_item=is_carousel_item,
            media_type=media_type,
        )

    @guard_ensure_auth_manager
    @guard_client_presence
    @guard_rate_limit("create_resumable_video", 1.0)
    @guard_error_wrap("Instagram resumable video upload")
    async def create_resumable_video(
        self,
        object_id: str,
        video_content: bytes,
        caption: Optional[str] = None,
        media_type: Optional[str] = None,
    ) -> str:
        """
        Upload a local video via Instagram's resumable rupload protocol.

        Args:
            object_id (str): Instagram object ID
            video_content (bytes): Raw video file bytes
            caption (str, optional): Video caption
            media_type (str, optional): REELS or STORIES

        Returns:
            str: Media container ID

        Raises:
            Exception: If upload fails
        """
        assert self.client is not None
        return await self.client.create_resumable_video(
            object_id=object_id,
            video_content=video_content,
            caption=caption,
            media_type=media_type,
        )

    @guard_client_presence
    @guard_rate_limit("create_carousel", 1.0)
    @guard_error_wrap("Instagram carousel creation")
    async def create_carousel(self, object_id: str, media_ids: List[str], caption: Optional[str] = None) -> str:
        """
        Create carousel media for Instagram.

        Args:
            object_id (str): Instagram object ID
            media_ids (list): List of media IDs
            caption (str, optional): Carousel caption

        Returns:
            str: Carousel ID

        Raises:
            Exception: If carousel creation fails
        """
        assert self.client is not None
        return await self.client.create_carousel(object_id=object_id, media_ids=media_ids, caption=caption)

    @guard_client_presence
    @guard_rate_limit("publish_media", 1.0)
    @guard_error_wrap("Instagram media publishing")
    async def publish_media(self, object_id: str, creation_id: str) -> str:
        """
        Publish created media to Instagram.

        Args:
            object_id (str): Instagram object ID
            creation_id (str): Media creation ID

        Returns:
            str: Published post ID

        Raises:
            Exception: If media publishing fails
        """
        assert self.client is not None
        return await self.client.publish_media(object_id=object_id, creation_id=creation_id)

    async def like(self, post_id: str) -> str:
        """
        Like an Instagram post (not supported via API).

        Args:
            post_id (str): Post ID to like

        Raises:
            Exception: Like not supported for Instagram
        """
        raise Exception("Like not supported for Instagram")

    @guard_ensure_auth_manager
    @guard_client_presence
    @guard_rate_limit("delete", 0.5)
    @guard_error_wrap("Instagram delete")
    async def delete(self, post_id: str) -> str:
        """
        Delete an Instagram media post.

        Args:
            post_id (str): Media ID to delete

        Returns:
            str: Deleted media ID

        Raises:
            Exception: If deletion fails
        """
        assert self.client is not None
        return await self.client.delete_media(post_id)

    async def share(self, post_id: str) -> str:
        """
        Share an Instagram post (not supported via API).

        Args:
            post_id (str): Post ID to share

        Raises:
            Exception: Share not supported for Instagram
        """
        raise Exception("Share not supported for Instagram")

    @guard_ensure_auth_manager
    @guard_client_presence
    @guard_rate_limit("reply", 0.5)
    @guard_error_wrap("Instagram comment")
    async def reply(self, post_id: str, text: str) -> str:
        """
        Comment on an Instagram media post.

        Args:
            post_id (str): Media ID to comment on
            text (str): Comment text

        Returns:
            str: Comment ID

        Raises:
            Exception: If comment operation fails
        """
        assert self.client is not None
        return await self.client.create_comment(post_id, text)

    @guard_ensure_auth_manager
    @guard_client_presence
    @guard_rate_limit("delete", 0.5)
    @guard_error_wrap("Instagram delete-reply")
    async def delete_reply(self, comment_id: str) -> str:
        """
        Delete an Instagram comment.

        Args:
            comment_id (str): ID of the comment to delete

        Returns:
            str: Deleted comment ID

        Raises:
            Exception: If deletion fails
        """
        assert self.client is not None
        return await self.client.delete_comment(comment_id)

    @guard_ensure_auth_manager
    @guard_client_presence
    @guard_rate_limit("get_post", 0.5)
    @guard_error_wrap("Instagram get-post")
    async def get_post(self, post_id: str) -> Dict[str, Any]:
        """
        Read an Instagram media object by ID.

        Args:
            post_id (str): Media ID to read

        Returns:
            dict: Media fields from Graph API

        Raises:
            Exception: If the media cannot be read
        """
        assert self.client is not None
        return await asyncio.to_thread(
            self.client.get_object,
            post_id,
            "id,caption,timestamp,username,media_type,media_url,permalink",
        )

    @guard_ensure_auth_manager
    @guard_client_presence
    @guard_rate_limit("get_reply", 0.5)
    @guard_error_wrap("Instagram get-reply")
    async def get_reply(self, comment_id: str) -> Dict[str, Any]:
        """
        Read an Instagram comment by ID.

        Args:
            comment_id (str): Comment ID to read

        Returns:
            dict: Comment fields from Graph API

        Raises:
            Exception: If the comment cannot be read
        """
        assert self.client is not None
        return await asyncio.to_thread(
            self.client.get_object,
            comment_id,
            "id,text,timestamp,username,from",
        )

    @guard_ensure_auth_manager
    @guard_client_presence
    @guard_rate_limit("list_posts", 0.5)
    @guard_error_wrap("Instagram list-posts")
    async def list_posts(self, object_id: str, limit: int) -> List[Dict[str, Any]]:
        """
        List recent media from an Instagram account.

        Args:
            object_id (str): Instagram object ID
            limit (int): Maximum number of media items to return

        Returns:
            list: Media fields from the Graph API

        Raises:
            Exception: If the media cannot be read
        """
        assert self.client is not None
        result = await self.client.get_user_media(
            object_id,
            fields="id,caption,timestamp,username,media_type,media_url,permalink",
            limit=limit,
        )
        return result.get("data") or []
