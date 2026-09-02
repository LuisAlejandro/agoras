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
"""agoras.platforms.facebook.api module."""

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

from .auth import FacebookAuthManager


class FacebookAPI(BaseAPI):
    """
    Facebook API handler that centralizes Facebook operations.

    Provides methods for Facebook authentication, token management,
    and all Facebook API operations including posts, likes, shares, and videos.
    """

    # Guard message template (read by the composable guard decorators)
    _client_not_available_message = "Facebook API not authenticated"

    def __init__(self, user_id, client_id, client_secret, refresh_token=None, app_id=None):
        """
        Initialize Facebook API instance.

        Args:
            user_id (str): Facebook user ID for cache identification
            client_id (str): Facebook client ID for token refresh
            client_secret (str): Facebook client secret for token refresh
            refresh_token (str, optional): Facebook refresh token
            app_id (str, optional): Facebook app ID for video uploads
        """
        super().__init__(user_id=user_id, client_id=client_id, client_secret=client_secret, refresh_token=refresh_token)

        self.app_id = app_id

        # Initialize the authentication manager
        self.auth_manager = FacebookAuthManager(
            user_id=user_id, client_id=client_id, client_secret=client_secret, refresh_token=refresh_token
        )

    async def authenticate(self):
        """
        Authenticate with Facebook API using the auth manager.

        Returns:
            FacebookAPI: Self for method chaining

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

    @guard_ensure_auth_manager
    @guard_client_presence
    @guard_rate_limit("check_if_page", 0.1)
    @guard_error_wrap("Facebook page check")
    async def check_if_page(self, object_id: str) -> bool:
        """
        Check if the given object_id represents a Facebook Page.

        Args:
            object_id (str): Facebook object ID to check

        Returns:
            bool: True if object is a Facebook Page, False otherwise
        """
        assert self.client is not None
        return await self.client.is_page(object_id)

    @guard_ensure_auth_manager
    @guard_client_presence
    @guard_rate_limit("get_page_token", 0.5)
    @guard_error_wrap("Facebook page token exchange")
    async def get_page_token(self, object_id: str) -> str:
        """
        Exchange user access token for page access token.

        Args:
            object_id (str): Facebook Page ID

        Returns:
            str: Page access token
        """
        # We need to pass the current user access token to get page token
        user_token = self.auth_manager.access_token
        if not user_token:
            raise Exception("Facebook access token not available")
        assert self.client is not None
        return await self.client.get_page_access_token(object_id, user_token)

    async def disconnect(self):
        """
        Disconnect from Facebook API and clean up resources.
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
    @guard_error_wrap("Facebook post creation")
    async def post(
        self,
        object_id: str,
        message: Optional[str] = None,
        link: Optional[str] = None,
        attached_media: Optional[List[Dict[str, Any]]] = None,
    ) -> str:
        """
        Create a Facebook post.

        Args:
            object_id (str): Facebook object ID (page/user)
            message (str, optional): Post message
            link (str, optional): Link to include
            attached_media (list, optional): List of media attachments

        Returns:
            str: Post ID

        Raises:
            Exception: If post creation fails
        """
        assert self.client is not None
        return await self.client.create_post(
            object_id=object_id, message=message, link=link, attached_media=attached_media
        )

    @guard_ensure_auth_manager
    @guard_client_presence
    @guard_rate_limit("upload_media", 1.0)
    @guard_error_wrap("Facebook media upload")
    async def upload_media(self, object_id: str, media_url: str, published: bool = False) -> Dict[str, Any]:
        """
        Upload media to Facebook.

        Args:
            object_id (str): Facebook object ID
            media_url (str): URL of media to upload
            published (bool): Whether to publish immediately

        Returns:
            dict: Media upload response

        Raises:
            Exception: If media upload fails
        """
        assert self.client is not None
        return await self.client.upload_media(object_id, media_url, published)

    @guard_ensure_auth_manager
    @guard_client_presence
    @guard_rate_limit("upload_photo_file", 1.0)
    @guard_error_wrap("Facebook photo file upload")
    async def upload_photo_file(
        self,
        object_id: str,
        file_content: bytes,
        published: bool = True,
        filename: str = "photo.jpg",
        mime_type: str = "image/jpeg",
        message: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Upload a local photo file to Facebook.

        Args:
            object_id (str): Facebook object ID
            file_content (bytes): Raw image bytes
            published (bool): Whether to publish immediately
            filename (str): Multipart filename
            mime_type (str): Image MIME type
            message (str, optional): Caption/message for published photos

        Returns:
            dict: Photo upload response

        Raises:
            Exception: If photo upload fails
        """
        assert self.client is not None
        return await self.client.upload_photo_file(
            object_id,
            file_content,
            published=published,
            filename=filename,
            mime_type=mime_type,
            message=message,
        )

    @guard_ensure_auth_manager
    @guard_client_presence
    @guard_rate_limit("like", 0.5)
    @guard_error_wrap("Facebook like")
    async def like(self, object_id: str, post_id: str) -> str:
        """
        Like a Facebook post.

        Args:
            object_id (str): Facebook object ID
            post_id (str): Post ID to like

        Returns:
            str: Post ID

        Raises:
            Exception: If like operation fails
        """
        assert self.client is not None
        return await self.client.like_post(object_id, post_id)

    @guard_ensure_auth_manager
    @guard_client_presence
    @guard_rate_limit("reply", 0.5)
    @guard_error_wrap("Facebook comment")
    async def reply(self, post_id: str, text: str, image_url: Optional[str] = None) -> str:
        """
        Comment on a Facebook post.

        Args:
            post_id (str): Post ID to comment on
            text (str): Comment text
            image_url (str, optional): Image URL to attach to the comment

        Returns:
            str: Comment ID

        Raises:
            Exception: If comment operation fails
        """
        assert self.client is not None
        return await self.client.create_comment(post_id, text, image_url=image_url)

    @guard_ensure_auth_manager
    @guard_client_presence
    @guard_rate_limit("delete", 0.5)
    @guard_error_wrap("Facebook delete")
    async def delete(self, object_id: str, post_id: str) -> str:
        """
        Delete a Facebook post.

        Args:
            object_id (str): Facebook object ID
            post_id (str): Post ID to delete

        Returns:
            str: Post ID

        Raises:
            Exception: If deletion fails
        """
        assert self.client is not None
        return await self.client.delete_post(object_id, post_id)

    @guard_ensure_auth_manager
    @guard_client_presence
    @guard_rate_limit("delete", 0.5)
    @guard_error_wrap("Facebook delete-reply")
    async def delete_reply(self, comment_id: str) -> str:
        """
        Delete a Facebook comment.

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
    @guard_error_wrap("Facebook get-post")
    async def get_post(self, post_id: str) -> Dict[str, Any]:
        """
        Read a Facebook post/object by ID.

        Args:
            post_id (str): Post or object ID to read

        Returns:
            dict: Object fields from Graph API

        Raises:
            Exception: If the object cannot be read
        """
        assert self.client is not None
        return await asyncio.to_thread(
            self.client.get_object,
            post_id,
            "id,message,created_time,from,full_picture,permalink_url",
        )

    @guard_ensure_auth_manager
    @guard_client_presence
    @guard_rate_limit("get_reply", 0.5)
    @guard_error_wrap("Facebook get-reply")
    async def get_reply(self, comment_id: str) -> Dict[str, Any]:
        """
        Read a Facebook comment by ID.

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
            "id,message,created_time,from,attachment{type,url,media{image{src},source}}",
        )

    @guard_ensure_auth_manager
    @guard_client_presence
    @guard_rate_limit("list_posts", 0.5)
    @guard_error_wrap("Facebook list-posts")
    async def list_posts(self, object_id: str, limit: int) -> List[Dict[str, Any]]:
        """
        List recent posts from a Facebook object's feed.

        Args:
            object_id (str): Facebook object ID (page/user)
            limit (int): Maximum number of posts to return

        Returns:
            list: Post fields from the Graph API

        Raises:
            Exception: If the posts cannot be read
        """
        assert self.client is not None
        result = await asyncio.to_thread(
            self.client.get_object,
            f"{object_id}/feed",
            "id,message,created_time,from,full_picture,permalink_url,type,source,attachments{media,type,media_type,url,subattachments}",
        )
        data = result.get("data") or []
        return data[:limit]

    @guard_ensure_auth_manager
    @guard_client_presence
    @guard_rate_limit("share", 1.0)
    @guard_error_wrap("Facebook share")
    async def share(self, profile_id: str, object_id: str, post_id: str) -> str:
        """
        Share a Facebook post.

        Args:
            profile_id (str): Profile ID to share from
            object_id (str): Original object ID
            post_id (str): Post ID to share

        Returns:
            str: New post ID

        Raises:
            Exception: If sharing fails
        """
        assert self.client is not None
        return await self.client.share_post(profile_id, object_id, post_id)

    @guard_ensure_auth_manager
    @guard_client_presence
    @guard_rate_limit("upload_reel_or_story", 1.0)
    @guard_error_wrap("Facebook reel or story upload")
    async def upload_reel_or_story(self, object_id: str, video_type: str, status_text: str, video_url: str) -> str:
        """
        Upload a video as a reel or story to Facebook.

        Args:
            object_id (str): Facebook object ID
            video_type (str): Type of video ('reel' or 'story')
            status_text (str): Text content to accompany the video
            video_url (str): URL of the video to post

        Returns:
            str: Post ID

        Raises:
            Exception: If upload fails
        """
        assert self.client is not None
        return await self.client.upload_reel_or_story(object_id, video_type, status_text, video_url)

    @guard_ensure_auth_manager
    @guard_client_presence
    @guard_rate_limit("upload_regular_video", 1.0)
    async def upload_regular_video(
        self,
        object_id: str,
        video_content: bytes,
        video_file_type: str,
        video_file_size: int,
        video_filename: str,
        status_text: str,
        video_title: str,
        source_video_url: Optional[str] = None,
    ) -> str:
        """
        Upload a regular video to Facebook.

        Args:
            object_id (str): Facebook object ID
            video_content (bytes): Video content
            video_file_type (str): Video file type
            video_file_size (int): Video file size
            video_filename (str): Video filename
            status_text (str): Text content to accompany the video
            video_title (str): Title of the video
            source_video_url (str, optional): Original public URL for fallback
                URL publishing if Facebook rejects the uploaded file handle

        Returns:
            str: Post ID

        Raises:
            Exception: If upload fails
        """
        if not self.app_id:
            raise Exception("Facebook app ID is required for regular video uploads")

        try:
            assert self.client is not None
            return await self.client.upload_regular_video(
                object_id,
                self.app_id,
                video_content,
                video_file_type,
                video_file_size,
                video_filename,
                status_text,
                video_title,
                source_video_url=source_video_url,
            )
        except Exception as e:
            self._handle_api_error(e, "Facebook regular video upload")
            raise
