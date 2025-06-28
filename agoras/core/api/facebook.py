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

from typing import Any, Dict, List, Optional

from .auth import FacebookAuthManager
from .base import BaseAPI


class FacebookAPI(BaseAPI):
    """
    Facebook API handler that centralizes Facebook operations.

    Provides methods for Facebook authentication, token management,
    and all Facebook API operations including posts, likes, shares, and videos.
    """

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
        super().__init__(
            user_id=user_id,
            client_id=client_id,
            client_secret=client_secret,
            refresh_token=refresh_token
        )

        self.app_id = app_id

        # Initialize the authentication manager
        self.auth_manager = FacebookAuthManager(
            user_id=user_id,
            client_id=client_id,
            client_secret=client_secret,
            refresh_token=refresh_token
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
            raise Exception('Facebook authentication failed')

        # Set the client from auth manager for BaseAPI compatibility
        self.client = self.auth_manager.client
        self._authenticated = True
        return self

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

    async def post(self, object_id: str, message: Optional[str] = None,
                   link: Optional[str] = None, attached_media: Optional[List[Dict[str, Any]]] = None) -> str:
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
        if not self.client:
            raise Exception('Facebook API not authenticated')

        await self._rate_limit_check('post', 1.0)

        try:
            return await self.client.create_post(
                object_id=object_id,
                message=message,
                link=link,
                attached_media=attached_media
            )
        except Exception as e:
            self._handle_api_error(e, 'Facebook post creation')
            raise

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
        if not self.client:
            raise Exception('Facebook API not authenticated')

        await self._rate_limit_check('upload_media', 1.0)

        try:
            return await self.client.upload_media(object_id, media_url, published)
        except Exception as e:
            self._handle_api_error(e, 'Facebook media upload')
            raise

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
        if not self.client:
            raise Exception('Facebook API not authenticated')

        await self._rate_limit_check('like', 0.5)

        try:
            return await self.client.like_post(object_id, post_id)
        except Exception as e:
            self._handle_api_error(e, 'Facebook like')
            raise

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
        if not self.client:
            raise Exception('Facebook API not authenticated')

        await self._rate_limit_check('delete', 0.5)

        try:
            return await self.client.delete_post(object_id, post_id)
        except Exception as e:
            self._handle_api_error(e, 'Facebook delete')
            raise

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
        if not self.client:
            raise Exception('Facebook API not authenticated')

        await self._rate_limit_check('share', 1.0)

        try:
            return await self.client.share_post(profile_id, object_id, post_id)
        except Exception as e:
            self._handle_api_error(e, 'Facebook share')
            raise

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
        if not self.client:
            raise Exception('Facebook API not authenticated')

        await self._rate_limit_check('upload_reel_or_story', 1.0)

        try:
            return await self.client.upload_reel_or_story(object_id, video_type, status_text, video_url)
        except Exception as e:
            self._handle_api_error(e, 'Facebook reel or story upload')
            raise

    async def upload_regular_video(
            self,
            object_id: str,
            video_content: bytes,
            video_file_type: str,
            video_file_size: int,
            video_filename: str,
            status_text: str,
            video_title: str) -> str:
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

        Returns:
            str: Post ID

        Raises:
            Exception: If upload fails
        """
        if not self.client:
            raise Exception('Facebook API not authenticated')

        await self._rate_limit_check('upload_regular_video', 1.0)

        if not self.app_id:
            raise Exception('Facebook app ID is required for regular video uploads')

        try:
            return await self.client.upload_regular_video(
                object_id, self.app_id, video_content, video_file_type,
                video_file_size, video_filename, status_text, video_title
            )
        except Exception as e:
            self._handle_api_error(e, 'Facebook regular video upload')
            raise
