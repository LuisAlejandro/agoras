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
import json
import time
from typing import Any, Dict, List

import requests

from agoras import __version__
from .base import BaseAPI
from .tiktok_oauth import refresh, get_creator_info


class TikTokAPI(BaseAPI):
    """
    TikTok API handler that centralizes TikTok operations.

    Provides methods for TikTok authentication, video uploads, photo posts,
    and all TikTok API operations.
    """

    # TikTok API URLs
    DIRECT_POST_URL = "https://open.tiktokapis.com/v2/post/publish/video/init/"
    GET_VIDEO_STATUS_URL = "https://open.tiktokapis.com/v2/post/publish/status/fetch/"

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
        self.username = username
        self.client_key = client_key
        self.client_secret = client_secret
        self.refresh_token = refresh_token
        self.access_token = None
        self.creator_info = None

    async def authenticate(self):
        """
        Authenticate with TikTok API using refresh token.

        Returns:
            TikTokAPI: Self for method chaining

        Raises:
            Exception: If authentication fails
        """
        if self._authenticated:
            return self

        if not self.refresh_token:
            raise Exception('TikTok refresh token is required for authentication.')

        def _sync_refresh():
            return refresh(self.username, self.refresh_token, self.client_key, self.client_secret)

        try:
            self.access_token = await asyncio.to_thread(_sync_refresh)
            self.creator_info = await self.get_creator_info()
            self._authenticated = True
            return self
        except Exception as e:
            self._handle_api_error(e, 'TikTok authentication')
            raise

    async def disconnect(self):
        """
        Disconnect from TikTok API and clean up resources.
        """
        self.access_token = None
        self.creator_info = None
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
            return get_creator_info(self.access_token)

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
        if not self.access_token:
            raise Exception('TikTok API not authenticated')

        await self._rate_limit_check('upload_video', 2.0)

        data = {
            "post_info": {
                "title": title,
                "privacy_level": privacy_status,
                "disable_duet": not allow_duet,
                "disable_comment": not allow_comments,
                "disable_stitch": not allow_stitch,
                "video_cover_timestamp_ms": 0,
                "brand_content_toggle": is_brand_content,
                "brand_organic_toggle": is_brand_organic,
            },
            "source_info": {
                "source": "PULL_FROM_URL",
                "video_url": video_url,
            },
        }

        def _sync_upload():
            res = requests.post(
                url=self.DIRECT_POST_URL,
                headers={
                    "Authorization": f"Bearer {self.access_token}",
                    "Content-Type": "application/json; charset=UTF-8",
                    'User-Agent': f'Agoras/{__version__}',
                },
                data=json.dumps(data)
            )
            return res.json()

        try:
            response = await asyncio.to_thread(_sync_upload)

            post_error_code = response.get('error', {}).get('code')
            post_error_message = response.get('error', {}).get('message')

            if post_error_code or post_error_message:
                raise Exception(f'Error uploading video: [{post_error_code}] {post_error_message}')

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
        if not self.access_token:
            raise Exception('TikTok API not authenticated')

        await self._rate_limit_check('upload_photo', 2.0)

        data = {
            "media_type": "PHOTO",
            "post_mode": "DIRECT_POST",
            "post_info": {
                "title": title,
                "description": "",
                "privacy_level": privacy_status,
                "disable_comment": not allow_comments,
                "auto_add_music": auto_add_music,
                "brand_content_toggle": is_brand_content,
                "brand_organic_toggle": is_brand_organic,
            },
            "source_info": {
                "source": "PULL_FROM_URL",
                "photo_cover_index": 0,
                "photo_images": photo_images,
            },
        }

        def _sync_upload():
            res = requests.post(
                url=self.DIRECT_POST_URL,
                headers={
                    "Authorization": f"Bearer {self.access_token}",
                    "Content-Type": "application/json",
                    'User-Agent': f'Agoras/{__version__}',
                },
                data=json.dumps(data)
            )
            return res.json()

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
                st = requests.post(
                    url=self.GET_VIDEO_STATUS_URL,
                    headers={
                        "Authorization": f"Bearer {self.access_token}",
                        "Content-Type": "application/json; charset=UTF-8",
                        'User-Agent': f'Agoras/{__version__}',
                    },
                    data=json.dumps({"publish_id": publish_id}),
                )
                return st.json()

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

    def get_api_info(self) -> Dict[str, Any]:
        """
        Get TikTok API configuration information.

        Returns:
            dict: API configuration details
        """
        return {
            'platform': 'TikTok',
            'authenticated': self._authenticated,
            'username': self.username,
            'has_creator_info': bool(self.creator_info),
            'rate_limits': list(self._rate_limit_cache.keys())
        } 