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
"""agoras.platforms.youtube.api module."""

from typing import Any, Dict, List, Optional

from agoras.core.api_base import (
    BaseAPI,
    guard_client_presence,
    guard_ensure_auth_manager,
    guard_error_wrap,
    guard_rate_limit,
)
from agoras.core.auth import raise_authentication_error_from_manager

from .auth import YouTubeAuthManager


class YouTubeAPI(BaseAPI):
    """
    YouTube API handler that centralizes YouTube operations.

    Provides methods for YouTube OAuth authentication, video uploads,
    and all YouTube API operations.
    """

    # Guard message templates (read by the composable guard decorators)
    _not_authenticated_message = "YouTube API not authenticated"
    _client_not_available_message = "YouTube API not authenticated"

    def __init__(self, client_id, client_secret, refresh_token=None):
        """
        Initialize YouTube API instance.

        Args:
            client_id (str): YouTube client ID
            client_secret (str): YouTube client secret
            refresh_token (str, optional): YouTube refresh token
        """
        super().__init__(client_id=client_id, client_secret=client_secret)

        # Initialize the authentication manager
        self.auth_manager = YouTubeAuthManager(
            client_id=client_id, client_secret=client_secret, refresh_token=refresh_token
        )

    @property
    def client_id(self):
        """Get the YouTube client ID from the auth manager."""
        return self.auth_manager.client_id if self.auth_manager else None

    @property
    def client_secret(self):
        """Get the YouTube client secret from the auth manager."""
        return self.auth_manager.client_secret if self.auth_manager else None

    @property
    def access_token(self):
        """Get the YouTube access token from the auth manager."""
        return self.auth_manager.access_token if self.auth_manager else None

    @property
    def user_info(self):
        """Get the YouTube user info from the auth manager."""
        return self.auth_manager.user_info if self.auth_manager else None

    async def authorize(self):
        """
        Perform OAuth authorization flow using the auth manager.

        This method should be called first to authorize the application
        with YouTube API.

        Returns:
            YouTubeAPI: Self for method chaining
        """
        access_token = await self.auth_manager.authorize()
        if not access_token:
            raise Exception("YouTube authorization failed")
        return self

    async def authenticate(self):
        """
        Authenticate with YouTube API using the auth manager.

        Returns:
            YouTubeAPI: Self for method chaining

        Raises:
            Exception: If authentication fails or authorization is needed
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
    @guard_error_wrap("YouTube video upload")
    async def upload_video(
        self,
        video_file_path: str,
        title: str,
        description: str,
        category_id: str,
        privacy_status: str,
        keywords: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Upload a video to YouTube.

        Args:
            video_file_path (str): Path to video file
            title (str): Video title
            description (str): Video description
            category_id (str): YouTube category ID
            privacy_status (str): Privacy status (public, private, unlisted)
            keywords (str, optional): Comma-separated keywords

        Returns:
            dict: Upload response with video ID

        Raises:
            Exception: If upload fails
        """
        return await self.client.upload_video(
            video_file_path=video_file_path,
            title=title,
            description=description,
            category_id=category_id,
            privacy_status=privacy_status,
            keywords=keywords,
        )

    @guard_ensure_auth_manager
    @guard_client_presence
    @guard_rate_limit("like", 1.0)
    @guard_error_wrap("YouTube video like")
    async def like(self, video_id: str) -> None:
        """
        Like a YouTube video.

        Args:
            video_id (str): YouTube video ID

        Raises:
            Exception: If like operation fails
        """
        await self.client.like_video(video_id)

    @guard_client_presence
    @guard_rate_limit("delete", 1.0)
    @guard_error_wrap("YouTube video deletion")
    async def delete(self, video_id: str) -> None:
        """
        Delete a YouTube video.

        Args:
            video_id (str): YouTube video ID

        Raises:
            Exception: If delete operation fails
        """
        await self.client.delete_video(video_id)

    async def post(self, *args, **kwargs) -> str:
        """
        Regular posts are not supported on YouTube (video platform only).

        Raises:
            Exception: Post not supported for YouTube
        """
        raise Exception("Regular posts not supported for YouTube - use upload_video() method instead")

    async def share(self, video_id: str) -> str:
        """
        Share is not supported for YouTube via API.

        Args:
            video_id (str): Video ID to share

        Raises:
            Exception: Share not supported for YouTube
        """
        raise Exception("Share not supported for YouTube")

    @guard_ensure_auth_manager
    @guard_client_presence
    @guard_rate_limit("reply", 1.0)
    @guard_error_wrap("YouTube comment")
    async def reply(self, video_id: str, text: str) -> str:
        """
        Comment on a YouTube video.

        Args:
            video_id (str): YouTube video ID to comment on
            text (str): Comment text

        Returns:
            str: Comment ID

        Raises:
            Exception: If comment operation fails
        """
        return await self.client.insert_comment(video_id, text)

    @guard_ensure_auth_manager
    @guard_client_presence
    @guard_rate_limit("delete", 1.0)
    @guard_error_wrap("YouTube delete-reply")
    async def delete_reply(self, comment_id: str) -> str:
        """
        Delete a YouTube comment.

        Args:
            comment_id (str): ID of the comment to delete

        Returns:
            str: Deleted comment ID

        Raises:
            Exception: If deletion fails
        """
        return await self.client.delete_comment(comment_id)

    @guard_ensure_auth_manager
    @guard_client_presence
    @guard_rate_limit("get_post", 1.0)
    @guard_error_wrap("YouTube get-post")
    async def get_post(self, video_id: str) -> Dict[str, Any]:
        """
        Read a YouTube video by ID.

        Args:
            video_id (str): Video ID to read

        Returns:
            dict: Video information

        Raises:
            Exception: If the video cannot be read
        """
        return await self.client.get_video_info(video_id)

    @guard_ensure_auth_manager
    @guard_client_presence
    @guard_rate_limit("get_reply", 1.0)
    @guard_error_wrap("YouTube get-reply")
    async def get_reply(self, comment_id: str) -> Dict[str, Any]:
        """
        Read a YouTube comment by ID.

        Args:
            comment_id (str): Comment ID to read

        Returns:
            dict: Comment fields

        Raises:
            Exception: If the comment cannot be read
        """
        return await self.client.get_comment(comment_id)

    @guard_ensure_auth_manager
    @guard_client_presence
    @guard_rate_limit("list_posts", 1.0)
    @guard_error_wrap("YouTube list-posts")
    async def list_posts(self, limit: int) -> List[Dict[str, Any]]:
        """
        List recent uploads from the authenticated user's channel.

        Args:
            limit (int): Maximum number of videos to return

        Returns:
            list: Video fields

        Raises:
            Exception: If the uploads cannot be read
        """
        return await self.client.list_uploads(limit)
