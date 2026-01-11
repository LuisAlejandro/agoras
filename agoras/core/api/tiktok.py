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
from typing import Any, Dict, List

from .auth import TikTokAuthManager
from .base import BaseAPI


class TikTokAPI(BaseAPI):
    """
    TikTok API handler that centralizes TikTok operations.

    Provides methods for TikTok authentication, video uploads, photo posts,
    and all TikTok API operations.
    """

    # TikTok API URLs - moved to client
    # DIRECT_POST_URL = "https://open.tiktokapis.com/v2/post/publish/video/init/"
    # GET_VIDEO_STATUS_URL = "https://open.tiktokapis.com/v2/post/publish/status/fetch/"

    def __init__(self, username, client_key, client_secret, refresh_token=None):
        """
        Initialize TikTok API instance.

        Args:
            username (str): TikTok username
            client_key (str): TikTok client key
            client_secret (str): TikTok client secret
            refresh_token (str, optional): TikTok refresh token
        """
        super().__init__(
            username=username,
            client_key=client_key,
            client_secret=client_secret,
            refresh_token=refresh_token
        )

        # Initialize the authentication manager
        self.auth_manager = TikTokAuthManager(
            username=username,
            client_key=client_key,
            client_secret=client_secret,
            refresh_token=refresh_token
        )

    @property
    def access_token(self):
        """Get the TikTok access token from the auth manager."""
        return self.auth_manager.access_token if self.auth_manager else None

    @property
    def creator_info(self):
        """Get the TikTok creator info from the auth manager."""
        return self.auth_manager.user_info if self.auth_manager else None

    async def authenticate(self):
        """
        Authenticate with TikTok API using the auth manager.

        Returns:
            TikTokAPI: Self for method chaining

        Raises:
            Exception: If authentication fails
        """
        if self._authenticated:
            return self

        success = await self.auth_manager.authenticate()
        if not success:
            raise Exception('TikTok authentication failed')

        self.client = self.auth_manager.client
        self._authenticated = True
        return self

    async def disconnect(self):
        """
        Disconnect from TikTok API and clean up resources.
        """
        # Clear auth manager tokens and user info
        if self.auth_manager:
            self.auth_manager.access_token = None
            self.auth_manager.user_info = None
            self.auth_manager.client = None

        # Clear BaseAPI client
        self.client = None
        self._authenticated = False

    async def get_creator_info(self) -> Dict[str, Any]:
        """
        Get creator information from TikTok API.

        Returns:
            dict: Creator information

        Raises:
            Exception: If API call fails
        """
        if not self.access_token:
            raise Exception('TikTok API not authenticated')

        def _sync_get_creator_info():
            return self.creator_info

        try:
            creator_info = await asyncio.to_thread(_sync_get_creator_info)
            if not creator_info:
                raise Exception('Failed to get creator info')
            return creator_info
        except Exception as e:
            self._handle_api_error(e, 'TikTok get creator info')
            raise

    async def upload_video(self, video_url: str, title: str, privacy_status: str,
                           allow_comments: bool = True, allow_duet: bool = True,
                           allow_stitch: bool = True, is_brand_organic: bool = False,
                           is_brand_content: bool = False) -> Dict[str, Any]:
        """
        Upload a video to TikTok.

        Args:
            video_url (str): URL of the video to upload
            title (str): Video title
            privacy_status (str): Privacy level (PUBLIC_TO_EVERYONE, SELF_ONLY, etc.)
            allow_comments (bool): Whether to allow comments
            allow_duet (bool): Whether to allow duets
            allow_stitch (bool): Whether to allow stitches
            is_brand_organic (bool): Whether this is brand organic content
            is_brand_content (bool): Whether this is brand content

        Returns:
            dict: Upload response with publish ID

        Raises:
            Exception: If upload fails
        """
        self.auth_manager.ensure_authenticated()

        if not self.access_token:
            raise Exception('TikTok API not authenticated')

        if not self.client:
            raise Exception('TikTok client not available')

        await self._rate_limit_check('upload_video', 2.0)

        def _sync_upload():
            if not self.client:
                raise Exception('TikTok client not available')
            return self.client.upload_video(
                video_url=video_url,
                title=title,
                privacy_status=privacy_status,
                allow_comments=allow_comments,
                allow_duet=allow_duet,
                allow_stitch=allow_stitch,
                is_brand_organic=is_brand_organic,
                is_brand_content=is_brand_content
            )

        try:
            response = await asyncio.to_thread(_sync_upload)

            publish_id = response.get('data', {}).get('publish_id')

            # Wait for video processing to complete
            await self._wait_for_publish_completion(publish_id)

            return {"publish_id": publish_id}
        except Exception as e:
            self._handle_api_error(e, 'TikTok video upload')
            raise

    async def upload_photo(self, photo_images: List[str], title: str, privacy_status: str,
                           allow_comments: bool = True, is_brand_organic: bool = False,
                           is_brand_content: bool = False, auto_add_music: bool = False) -> Dict[str, Any]:
        """
        Upload photos to TikTok.

        Args:
            photo_images (list): List of photo URLs
            title (str): Post title
            privacy_status (str): Privacy level
            allow_comments (bool): Whether to allow comments
            is_brand_organic (bool): Whether this is brand organic content
            is_brand_content (bool): Whether this is brand content
            auto_add_music (bool): Whether to auto-add music

        Returns:
            dict: Upload response

        Raises:
            Exception: If upload fails
        """
        self.auth_manager.ensure_authenticated()

        if not self.access_token:
            raise Exception('TikTok API not authenticated')

        if not self.client:
            raise Exception('TikTok client not available')

        await self._rate_limit_check('upload_photo', 2.0)

        def _sync_upload():
            if not self.client:
                raise Exception('TikTok client not available')
            return self.client.upload_photo(
                photo_images=photo_images,
                title=title,
                privacy_status=privacy_status,
                allow_comments=allow_comments,
                is_brand_organic=is_brand_organic,
                is_brand_content=is_brand_content,
                auto_add_music=auto_add_music
            )

        try:
            response = await asyncio.to_thread(_sync_upload)
            return response.get('data', {})
        except Exception as e:
            self._handle_api_error(e, 'TikTok photo upload')
            raise

    async def _wait_for_publish_completion(self, publish_id: str, max_wait_time: int = 300) -> None:
        """
        Wait for TikTok post to be published.

        Args:
            publish_id (str): Publish ID to check status for
            max_wait_time (int): Maximum time to wait in seconds

        Raises:
            Exception: If publish fails or times out
        """
        start_time = time.time()

        while True:
            # Check if we've exceeded max wait time
            if time.time() - start_time > max_wait_time:
                raise Exception(f'Publish timeout after {max_wait_time} seconds')

            await asyncio.sleep(10)
            print('Waiting for post status ...')

            def _sync_check_status():
                if not self.client:
                    raise Exception('TikTok client not available')
                return self.client.get_publish_status(publish_id)

            try:
                status = await asyncio.to_thread(_sync_check_status)
                publish_status = status.get('data', {}).get('status')
                publish_id_list = status.get('data', {}).get('publicaly_available_post_id', [])

                if len(publish_id_list) > 0 or publish_status == 'PUBLISH_COMPLETE':
                    print('Post published!')
                    break

            except Exception as e:
                self._handle_api_error(e, 'TikTok status check')
                raise

    async def post(self, *args, **kwargs) -> str:
        """
        Regular posts are not supported on TikTok (use upload_photo instead).

        Raises:
            Exception: Post not supported for TikTok
        """
        raise Exception('Regular posts not supported for TikTok - use upload_photo() method instead')

    async def like(self, post_id: str) -> str:
        """
        Like a TikTok post (not supported via API).

        Args:
            post_id (str): Post ID to like

        Raises:
            Exception: Like not supported for TikTok
        """
        raise Exception('Like not supported for TikTok')

    async def delete(self, post_id: str) -> str:
        """
        Delete a TikTok post (not supported via API).

        Args:
            post_id (str): Post ID to delete

        Raises:
            Exception: Delete not supported for TikTok
        """
        raise Exception('Delete not supported for TikTok')

    async def share(self, post_id: str) -> str:
        """
        Share a TikTok post (not supported via API).

        Args:
            post_id (str): Post ID to share

        Raises:
            Exception: Share not supported for TikTok
        """
        raise Exception('Share not supported for TikTok')
