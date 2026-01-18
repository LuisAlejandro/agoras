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

import asyncio
import json
from typing import Any, Dict, List, Optional

import requests
from pyfacebook import GraphAPI

from agoras.common import __version__


class FacebookAPIClient:
    """
    Facebook API client that centralizes Facebook operations.

    Handles all Facebook API interactions including GraphAPI operations,
    media uploads, video uploads, and manual HTTP requests for advanced features.
    """

    def __init__(self, access_token: str):
        """
        Initialize Facebook API client.

        Args:
            access_token (str): Facebook access token
        """
        self.access_token = access_token
        self.graph_api: Optional[GraphAPI] = None
        self._authenticated = False

    async def authenticate(self) -> bool:
        """
        Authenticate and initialize GraphAPI client.

        Returns:
            bool: True if authentication successful

        Raises:
            Exception: If authentication fails
        """
        if self._authenticated:
            return True

        if not self.access_token:
            raise Exception('Facebook access token is required')

        try:
            self.graph_api = GraphAPI(access_token=self.access_token, version="21.0")
            self._authenticated = True
            return True
        except Exception as e:
            raise Exception(f'Facebook client authentication failed: {str(e)}')

    def disconnect(self):
        """
        Disconnect and clean up client resources.
        """
        self.graph_api = None
        self._authenticated = False

    def post_object(self, object_id: str, connection: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Post to a Facebook object connection using GraphAPI.

        Args:
            object_id (str): Facebook object ID
            connection (str): Connection type (feed, photos, etc.)
            data (dict, optional): Data to post

        Returns:
            dict: Response from Facebook API

        Raises:
            Exception: If post fails
        """
        if not self.graph_api:
            raise Exception('Facebook GraphAPI not initialized')

        try:
            return self.graph_api.post_object(
                object_id=object_id,
                connection=connection,
                data=data or {}
            )
        except Exception as e:
            raise Exception(f'Facebook post_object failed: {str(e)}')

    def delete_object(self, object_id: str) -> None:
        """
        Delete a Facebook object using GraphAPI.

        Args:
            object_id (str): Facebook object ID to delete

        Raises:
            Exception: If deletion fails
        """
        if not self.graph_api:
            raise Exception('Facebook GraphAPI not initialized')

        try:
            self.graph_api.delete_object(object_id=object_id)
        except Exception as e:
            raise Exception(f'Facebook delete_object failed: {str(e)}')

    def get_object(self, object_id: str, fields: Optional[str] = None) -> Dict[str, Any]:
        """
        Get a Facebook object using GraphAPI.

        Args:
            object_id (str): Facebook object ID
            fields (str, optional): Fields to retrieve

        Returns:
            dict: Object data from Facebook API

        Raises:
            Exception: If get fails
        """
        if not self.graph_api:
            raise Exception('Facebook GraphAPI not initialized')

        try:
            if fields:
                return self.graph_api.get_object(object_id=object_id, fields=fields)
            else:
                return self.graph_api.get_object(object_id=object_id)
        except Exception as e:
            raise Exception(f'Facebook get_object failed: {str(e)}')

    async def is_page(self, object_id: str) -> bool:
        """
        Check if the given object_id represents a Facebook Page.

        Args:
            object_id (str): Facebook object ID to check

        Returns:
            bool: True if object is a Facebook Page, False otherwise

        Raises:
            Exception: If API call fails
        """
        if not self.graph_api:
            raise Exception('Facebook GraphAPI not initialized')

        try:
            # Pages have 'category' or 'category_list' fields, profiles don't
            page_data = self.graph_api.get_object(
                object_id=object_id,
                fields='category,category_list,about'
            )

            # If we got category or category_list fields, it's a page
            return bool(page_data.get('category') or page_data.get('category_list'))
        except Exception:
            # If we can't access the object, assume it's not a page
            # (could be privacy settings or invalid ID)
            return False

    async def get_page_access_token(self, object_id: str, user_access_token: str) -> str:
        """
        Exchange user access token for page access token.

        Args:
            object_id (str): Facebook Page ID
            user_access_token (str): User access token with page permissions

        Returns:
            str: Page access token

        Raises:
            Exception: If page token cannot be obtained
        """
        if not self.graph_api:
            raise Exception('Facebook GraphAPI not initialized')

        try:
            # Use direct HTTP request to /me/accounts endpoint
            import requests

            url = "https://graph.facebook.com/v21.0/me/accounts"
            params = {
                'access_token': user_access_token,
                'fields': 'id,access_token'
            }

            response = requests.get(url, params=params)
            response.raise_for_status()

            accounts_data = response.json()

            # Find the page matching our object_id
            for account in accounts_data.get('data', []):
                if account.get('id') == object_id:
                    page_token = account.get('access_token')
                    if page_token:
                        return page_token

            raise Exception(f'Page {object_id} not found in user accounts or no access token available')

        except Exception as e:
            raise Exception(f'Facebook page token exchange failed: {str(e)}')

    async def create_post(self, object_id: str, message: Optional[str] = None,
                          link: Optional[str] = None,
                          attached_media: Optional[List[Dict[str, Any]]] = None) -> str:
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
        def _sync_create_post():
            data: Dict[str, Any] = {'published': True}

            if link:
                data['link'] = link
            if message:
                data['message'] = message
            if attached_media:
                data['attached_media'] = json.dumps(attached_media)

            response = self.post_object(
                object_id=object_id,
                connection='feed',
                data=data
            )
            return response['id'].split('_')[1]

        return await asyncio.to_thread(_sync_create_post)

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
        def _sync_upload_media():
            return self.post_object(
                object_id=object_id,
                connection='photos',
                data={
                    'url': media_url,
                    'published': published
                }
            )

        return await asyncio.to_thread(_sync_upload_media)

    async def like_post(self, object_id: str, post_id: str) -> str:
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
        def _sync_like():
            self.post_object(
                object_id=f'{object_id}_{post_id}',
                connection='likes'
            )
            return post_id

        return await asyncio.to_thread(_sync_like)

    async def delete_post(self, object_id: str, post_id: str) -> str:
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
        def _sync_delete():
            self.delete_object(object_id=f'{object_id}_{post_id}')
            return post_id

        return await asyncio.to_thread(_sync_delete)

    async def share_post(self, profile_id: str, object_id: str, post_id: str) -> str:
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
        def _sync_share():
            host = 'https://www.facebook.com'
            data = {
                'link': f'{host}/{object_id}/posts/{post_id}',
                'published': True
            }
            response = self.post_object(
                object_id=profile_id,
                connection='feed',
                data=data
            )
            return response['id'].split('_')[1]

        return await asyncio.to_thread(_sync_share)

    async def upload_reel_or_story(self, object_id: str, video_type: str, status_text: str, video_url: str) -> str:
        """
        Upload a video as a reel or story to Facebook using manual HTTP requests.

        Args:
            object_id (str): Facebook object ID
            video_type (str): Type of video ('reel' or 'story')
            status_text (str): Text content to accompany the video
            video_url (str): URL of the video to post

        Returns:
            str: Video/Post ID

        Raises:
            Exception: If upload fails
        """
        def _sync_upload_reel_or_story():
            connection = 'video_reels' if video_type == 'reel' else 'video_stories'

            # Start upload
            response = self.post_object(
                object_id=object_id,
                connection=connection,
                data={"upload_phase": "start"}
            )
            video_id = response.get('video_id')
            upload_url = response.get('upload_url')

            # Upload video
            if upload_url:
                requests.post(upload_url, headers={
                    "file_url": video_url,
                    "Authorization": f"OAuth {self.access_token}",
                    'User-Agent': f'Agoras/{__version__}',
                })

            # Finish upload
            self.post_object(
                object_id=object_id,
                connection=connection,
                data={
                    "upload_phase": "finish",
                    "video_state": "PUBLISHED",
                    "video_id": video_id,
                    "description": status_text,
                }
            )

            return str(video_id) if video_id else ""

        return await asyncio.to_thread(_sync_upload_reel_or_story)

    async def upload_regular_video(self, object_id: str, app_id: str, video_content: bytes,
                                   video_file_type: str, video_file_size: int, video_filename: str,
                                   status_text: str, video_title: str) -> str:
        """
        Upload a regular video to Facebook using manual HTTP requests.

        Args:
            object_id (str): Facebook object ID
            app_id (str): Facebook app ID
            video_content (bytes): Video file content
            video_file_type (str): Video MIME type
            video_file_size (int): Video file size in bytes
            video_filename (str): Video filename
            status_text (str): Text content to accompany the video
            video_title (str): Title of the video

        Returns:
            str: Post ID

        Raises:
            Exception: If upload fails
        """
        def _sync_upload_regular_video():
            # Create upload session
            upload_response = requests.post(
                f"https://graph.facebook.com/v21.0/{app_id}/uploads",
                headers={
                    "Authorization": f"OAuth {self.access_token}",
                    'User-Agent': f'Agoras/{__version__}',
                },
                data={
                    "file_type": video_file_type,
                    "file_length": str(video_file_size),
                    "file_name": video_filename,
                }
            )
            upload_response.raise_for_status()
            upload_session_id = upload_response.json().get('id')

            if not upload_session_id:
                raise Exception('Failed to create upload session')

            # Upload video file
            upload_data_response = requests.post(
                f"https://graph.facebook.com/v21.0/{upload_session_id}",
                headers={
                    "Content-Type": video_file_type,
                    "file_offset": "0",
                    "Authorization": f"OAuth {self.access_token}",
                    'User-Agent': f'Agoras/{__version__}',
                },
                data=video_content
            )
            upload_data_response.raise_for_status()
            file_handle = upload_data_response.json().get('h')

            if not file_handle:
                raise Exception('Failed to upload video data')

            # Create video post
            video_response = requests.post(
                f"https://graph-video.facebook.com/v21.0/{object_id}/videos",
                headers={
                    "Authorization": f"OAuth {self.access_token}",
                    'User-Agent': f'Agoras/{__version__}',
                },
                data={
                    'title': video_title,
                    'description': status_text,
                    "fbuploader_video_file_chunk": file_handle,
                }
            )
            video_response.raise_for_status()
            return str(video_response.json()['id'])

        return await asyncio.to_thread(_sync_upload_regular_video)
