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

import json
from typing import Any, Dict, List, Optional

import requests

from agoras import __version__


class TikTokAPIClient:
    """
    TikTok API client for making HTTP requests to TikTok endpoints.

    Centralizes all TikTok API calls including authentication, content publishing,
    and status checking operations.
    """

    # TikTok API URLs
    CREATOR_INFO_URL = "https://open.tiktokapis.com/v2/post/publish/creator_info/query/"
    DIRECT_POST_URL = "https://open.tiktokapis.com/v2/post/publish/video/init/"
    GET_VIDEO_STATUS_URL = "https://open.tiktokapis.com/v2/post/publish/status/fetch/"

    def __init__(self, access_token: Optional[str] = None):
        """
        Initialize TikTok API client.

        Args:
            access_token (str, optional): TikTok access token for authenticated requests
        """
        self.access_token = access_token

    def get_user_info(self) -> Dict[str, Any]:
        """
        Get creator information from TikTok API.

        Returns:
            dict: Creator information

        Raises:
            Exception: If API call fails or not authenticated
        """
        if not self.access_token:
            raise Exception('No access token available')

        response = requests.post(
            self.CREATOR_INFO_URL,
            headers={
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json; charset=UTF-8",
                'User-Agent': f'Agoras/{__version__}',
            }
        )

        result = response.json()

        if 'error' in result:
            raise Exception(f"Failed to get creator info: {result.get('error_description', 'Unknown error')}")

        creator_data = result.get('data')
        if not creator_data:
            raise Exception('No creator data in response')

        return creator_data

    def upload_video(self, video_url: str, title: str, privacy_status: str,
                     allow_comments: bool = True, allow_duet: bool = True,
                     allow_stitch: bool = True, is_brand_organic: bool = False,
                     is_brand_content: bool = False) -> Dict[str, Any]:
        """
        Upload a video to TikTok.

        Args:
            video_url (str): URL of the video to upload
            title (str): Video title
            privacy_status (str): Privacy level
            allow_comments (bool): Whether to allow comments
            allow_duet (bool): Whether to allow duets
            allow_stitch (bool): Whether to allow stitches
            is_brand_organic (bool): Whether this is brand organic content
            is_brand_content (bool): Whether this is brand content

        Returns:
            dict: Upload response

        Raises:
            Exception: If upload fails or not authenticated
        """
        if not self.access_token:
            raise Exception('No access token available')

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

        response = requests.post(
            self.DIRECT_POST_URL,
            headers={
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json; charset=UTF-8",
                'User-Agent': f'Agoras/{__version__}',
            },
            data=json.dumps(data)
        )

        result = response.json()

        post_error_code = result.get('error', {}).get('code')
        post_error_message = result.get('error', {}).get('message')

        if post_error_code or post_error_message:
            raise Exception(f'Error uploading video: [{post_error_code}] {post_error_message}')

        return result

    def upload_photo(self, photo_images: List[str], title: str, privacy_status: str,
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
            Exception: If upload fails or not authenticated
        """
        if not self.access_token:
            raise Exception('No access token available')

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

        response = requests.post(
            self.DIRECT_POST_URL,
            headers={
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json",
                'User-Agent': f'Agoras/{__version__}',
            },
            data=json.dumps(data)
        )

        result = response.json()
        return result

    def get_publish_status(self, publish_id: str) -> Dict[str, Any]:
        """
        Get the status of a published post.

        Args:
            publish_id (str): Publish ID to check status for

        Returns:
            dict: Status response

        Raises:
            Exception: If status check fails or not authenticated
        """
        if not self.access_token:
            raise Exception('No access token available')

        response = requests.post(
            self.GET_VIDEO_STATUS_URL,
            headers={
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json; charset=UTF-8",
                'User-Agent': f'Agoras/{__version__}',
            },
            data=json.dumps({"publish_id": publish_id}),
        )

        return response.json()
