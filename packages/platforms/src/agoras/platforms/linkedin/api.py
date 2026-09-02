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
"""agoras.platforms.linkedin.api module."""

from typing import Any, Dict, List, Optional

from agoras.core.api_base import (
    BaseAPI,
    guard_client_presence,
    guard_ensure_auth_manager,
    guard_error_wrap,
    guard_rate_limit,
)
from agoras.core.auth import raise_authentication_error_from_manager

from .auth import LinkedInAuthManager


class LinkedInAPI(BaseAPI):
    """
    LinkedIn API handler that centralizes LinkedIn operations.

    Provides methods for LinkedIn authentication, token management,
    and all LinkedIn API operations including posts, likes, shares, and media uploads.
    """

    # Guard message template (read by the composable guard decorators)
    _client_not_available_message = "LinkedIn API not authenticated"

    def __init__(self, user_id, client_id, client_secret, refresh_token=None, access_token=None):
        """
        Initialize LinkedIn API instance.

        Args:
            user_id (str): LinkedIn user ID (object ID)
            client_id (str): LinkedIn client ID
            client_secret (str): LinkedIn client secret
            refresh_token (str, optional): LinkedIn refresh token
            access_token (str, optional): LinkedIn access token
        """
        super().__init__(
            access_token=access_token,
            client_id=client_id,
            client_secret=client_secret,
            refresh_token=refresh_token,
        )

        # Initialize the authentication manager
        self.auth_manager = LinkedInAuthManager(
            user_id=user_id,
            client_id=client_id,
            client_secret=client_secret,
            refresh_token=refresh_token,
            access_token=access_token,
        )
        self.api_version = "202302"

    @property
    def user_id(self):
        """Get the LinkedIn user ID from the auth manager."""
        return self.auth_manager.user_id if self.auth_manager else None

    @property
    def client_id(self):
        """Get the LinkedIn client ID from the auth manager."""
        return self.auth_manager.client_id if self.auth_manager else None

    @property
    def access_token(self):
        """Get the LinkedIn access token from the auth manager."""
        return self.auth_manager.access_token if self.auth_manager else None

    @property
    def object_id(self):
        """Get the LinkedIn object ID from the auth manager's user info."""
        return self.auth_manager.user_info.get("object_id") if self.auth_manager.user_info else None

    async def authenticate(self):
        """
        Authenticate with LinkedIn API using the auth manager.

        Returns:
            LinkedInAPI: Self for method chaining

        Raises:
            Exception: If authentication fails
        """
        if self._authenticated:
            return self

        success = await self.auth_manager.authenticate()
        if not success:
            raise_authentication_error_from_manager(self.auth_manager)

        return await super().authenticate()

    @guard_ensure_auth_manager
    @guard_client_presence
    @guard_rate_limit("upload_video", 2.0)
    async def upload_video(self, video_content: bytes) -> str:
        """
        Upload a video to LinkedIn.

        Args:
            video_content (bytes): Raw video content

        Returns:
            str: Video URN for the uploaded video

        Raises:
            Exception: If video upload fails
        """
        if not self.object_id:
            raise Exception("LinkedIn API not authenticated")

        try:
            assert self.client is not None
            return await self.client.upload_video(
                video_content=video_content, owner_urn=f"urn:li:person:{self.object_id}"
            )
        except Exception as e:
            self._handle_api_error(e, "LinkedIn video upload")
            raise

    @guard_ensure_auth_manager
    @guard_client_presence
    @guard_rate_limit("upload_image", 1.0)
    async def upload_image(self, image_content: bytes) -> str:
        """
        Upload an image to LinkedIn.

        Args:
            image_content (bytes): Raw image content

        Returns:
            str: Media ID for the uploaded image

        Raises:
            Exception: If image upload fails
        """
        if not self.object_id:
            raise Exception("LinkedIn API not authenticated")

        try:
            assert self.client is not None
            return await self.client.upload_image(
                image_content=image_content, owner_urn=f"urn:li:person:{self.object_id}"
            )
        except Exception as e:
            self._handle_api_error(e, "LinkedIn image upload")
            raise

    @guard_ensure_auth_manager
    @guard_client_presence
    @guard_rate_limit("post", 1.0)
    @guard_error_wrap("LinkedIn post creation")
    async def post(
        self,
        text: str,
        link: Optional[str] = None,
        link_title: Optional[str] = None,
        link_description: Optional[str] = None,
        image_ids: Optional[List[str]] = None,
        video_id: Optional[str] = None,
        video_title: Optional[str] = None,
    ) -> str:
        """
        Create a LinkedIn post.

        Args:
            text (str): Post text content
            link (str, optional): URL to include
            link_title (str, optional): Title of the link
            link_description (str, optional): Description of the link
            image_ids (list, optional): List of uploaded image IDs
            video_id (str, optional): Uploaded video URN
            video_title (str, optional): Title for the video post

        Returns:
            str: Post ID

        Raises:
            Exception: If post creation fails
        """
        assert self.client is not None
        return await self.client.create_post(
            author_urn=f"urn:li:person:{self.object_id}",
            text=text,
            link=link,
            link_title=link_title,
            link_description=link_description,
            image_ids=image_ids,
            video_id=video_id,
            video_title=video_title,
        )

    @guard_client_presence
    @guard_rate_limit("like", 0.5)
    async def like(self, post_id: str) -> str:
        """
        Like a LinkedIn post.

        Args:
            post_id (str): Post ID to like

        Returns:
            str: Post ID

        Raises:
            Exception: If like operation fails
        """
        if not self.object_id:
            raise Exception("LinkedIn API not authenticated")

        try:
            assert self.client is not None
            return await self.client.like_post(post_id=post_id, actor_urn=f"urn:li:person:{self.object_id}")
        except Exception as e:
            self._handle_api_error(e, "LinkedIn like")
            raise

    @guard_client_presence
    @guard_rate_limit("reply", 0.5)
    async def reply(self, post_id: str, text: str, image_ids: Optional[List[str]] = None) -> str:
        """
        Comment on a LinkedIn post.

        Args:
            post_id (str): Post ID to comment on
            text (str): Comment text
            image_ids (list, optional): List of uploaded image IDs to attach

        Returns:
            str: Comment ID

        Raises:
            Exception: If comment operation fails
        """
        if not self.object_id:
            raise Exception("LinkedIn API not authenticated")

        try:
            assert self.client is not None
            return await self.client.create_comment(
                post_id=post_id,
                actor_urn=f"urn:li:person:{self.object_id}",
                text=text,
                image_ids=image_ids,
            )
        except Exception as e:
            self._handle_api_error(e, "LinkedIn comment")
            raise

    @guard_client_presence
    @guard_rate_limit("share_post", 1.0)
    @guard_error_wrap("LinkedIn share")
    async def share(self, post_id: str) -> str:
        """
        Share (repost) a LinkedIn post.

        Args:
            post_id (str): Post ID to share

        Returns:
            str: Share ID

        Raises:
            Exception: If share operation fails
        """
        assert self.client is not None
        return await self.client.share_post(
            post_id=post_id, author_urn=f"urn:li:person:{self.object_id}", commentary=""
        )

    @guard_client_presence
    @guard_rate_limit("delete", 0.5)
    @guard_error_wrap("LinkedIn delete")
    async def delete(self, post_id: str) -> str:
        """
        Delete a LinkedIn post.

        Args:
            post_id (str): Post ID to delete

        Returns:
            str: Post ID

        Raises:
            Exception: If deletion fails
        """
        assert self.client is not None
        return await self.client.delete_post(post_id=post_id)

    @guard_client_presence
    @guard_rate_limit("delete", 0.5)
    @guard_error_wrap("LinkedIn delete-reply")
    async def delete_reply(self, comment_id: str, parent_post_id: str) -> str:
        """
        Delete a LinkedIn comment.

        Args:
            comment_id (str): ID of the comment to delete
            parent_post_id (str): Parent post URN the comment belongs to

        Returns:
            str: Deleted comment ID

        Raises:
            Exception: If deletion fails
        """
        assert self.client is not None
        return await self.client.delete_comment(comment_id=comment_id, parent_post_id=parent_post_id)

    @guard_ensure_auth_manager
    @guard_client_presence
    @guard_rate_limit("get_post", 0.5)
    @guard_error_wrap("LinkedIn get-post")
    async def get_post(self, post_id: str) -> Dict[str, Any]:
        """
        Read a LinkedIn post by URN.

        Args:
            post_id (str): Post URN to read

        Returns:
            dict: Post entity

        Raises:
            Exception: If the post cannot be read
        """
        assert self.client is not None
        return await self.client.get_post(post_id=post_id)

    @guard_ensure_auth_manager
    @guard_client_presence
    @guard_rate_limit("get_reply", 0.5)
    @guard_error_wrap("LinkedIn get-reply")
    async def get_reply(self, comment_id: str, parent_post_id: str) -> Dict[str, Any]:
        """
        Read a LinkedIn comment by ID and parent post URN.

        Args:
            comment_id (str): Comment ID to read
            parent_post_id (str): Parent post URN the comment belongs to

        Returns:
            dict: Comment entity

        Raises:
            Exception: If the comment cannot be read
        """
        assert self.client is not None
        return await self.client.get_comment(comment_id=comment_id, parent_post_id=parent_post_id)

    @guard_ensure_auth_manager
    @guard_client_presence
    @guard_rate_limit("get_media", 0.5)
    @guard_error_wrap("LinkedIn get-media")
    async def get_media(self, media_urn: str) -> Dict[str, Any]:
        """
        Resolve a LinkedIn media URN to its downloadable URL.

        Args:
            media_urn (str): Media URN (e.g. "urn:li:image:123" or "urn:li:video:456")

        Returns:
            dict: Media entity containing a ``downloadUrl``

        Raises:
            Exception: If the media cannot be resolved
        """
        assert self.client is not None
        return await self.client.get_media(media_urn=media_urn)

    @guard_ensure_auth_manager
    @guard_client_presence
    @guard_rate_limit("list_posts", 0.5)
    async def list_posts(self, limit: int) -> List[Dict[str, Any]]:
        """
        List the authenticated user's recent posts.

        Args:
            limit (int): Maximum number of posts to return

        Returns:
            list: Post entities

        Raises:
            Exception: If the posts cannot be read
        """
        if not self.object_id:
            raise Exception("LinkedIn API not authenticated")

        try:
            assert self.client is not None
            return await self.client.list_posts(author_urn=f"urn:li:person:{self.object_id}", limit=limit)
        except Exception as e:
            self._handle_api_error(e, "LinkedIn list-posts")
            raise
