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

from typing import Any, Dict, Optional

from .auth import YouTubeAuthManager
from agoras.core.api_base import BaseAPI


class YouTubeAPI(BaseAPI):
    """
    YouTube API handler that centralizes YouTube operations.

    Provides methods for YouTube OAuth authentication, video uploads,
    and all YouTube API operations.
    """

    def __init__(self, client_id, client_secret):
        """
        Initialize YouTube API instance.

        Args:
            client_id (str): YouTube client ID
            client_secret (str): YouTube client secret
        """
        super().__init__(
            client_id=client_id,
            client_secret=client_secret
        )

        # Initialize the authentication manager
        self.auth_manager = YouTubeAuthManager(
            client_id=client_id,
            client_secret=client_secret
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
            raise Exception('YouTube authorization failed')
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
            raise Exception('YouTube authentication failed - please run authorization first')

        # Set the client from auth manager for BaseAPI compatibility
        self.client = self.auth_manager.client
        self._authenticated = True
        return self

    async def disconnect(self):
        """
        Disconnect from YouTube API and clean up resources.
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

    async def upload_video(self, video_file_path: str, title: str, description: str,
                           category_id: str, privacy_status: str, keywords: Optional[str] = None) -> Dict[str, Any]:
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
        self.auth_manager.ensure_authenticated()

        if not self.client:
            raise Exception('YouTube API not authenticated')

        await self._rate_limit_check('upload_video', 2.0)

        try:
            return await self.client.upload_video(
                video_file_path=video_file_path,
                title=title,
                description=description,
                category_id=category_id,
                privacy_status=privacy_status,
                keywords=keywords
            )
        except Exception as e:
            self._handle_api_error(e, 'YouTube video upload')
            raise

    async def like(self, video_id: str) -> None:
        """
        Like a YouTube video.

        Args:
            video_id (str): YouTube video ID

        Raises:
            Exception: If like operation fails
        """
        self.auth_manager.ensure_authenticated()

        if not self.client:
            raise Exception('YouTube API not authenticated')

        await self._rate_limit_check('like', 1.0)

        try:
            await self.client.like_video(video_id)
        except Exception as e:
            self._handle_api_error(e, 'YouTube video like')
            raise

    async def delete(self, video_id: str) -> None:
        """
        Delete a YouTube video.

        Args:
            video_id (str): YouTube video ID

        Raises:
            Exception: If delete operation fails
        """
        if not self.client:
            raise Exception('YouTube API not authenticated')

        await self._rate_limit_check('delete', 1.0)

        try:
            await self.client.delete_video(video_id)
        except Exception as e:
            self._handle_api_error(e, 'YouTube video deletion')
            raise

    async def post(self, *args, **kwargs) -> str:
        """
        Regular posts are not supported on YouTube (video platform only).

        Raises:
            Exception: Post not supported for YouTube
        """
        raise Exception('Regular posts not supported for YouTube - use upload_video() method instead')

    async def share(self, video_id: str) -> str:
        """
        Share is not supported for YouTube via API.

        Args:
            video_id (str): Video ID to share

        Raises:
            Exception: Share not supported for YouTube
        """
        raise Exception('Share not supported for YouTube')
