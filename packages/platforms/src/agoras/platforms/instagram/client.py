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
from typing import Any, Dict, List, Optional

from pyfacebook import GraphAPI


class InstagramAPIClient:
    """
    Instagram API client that centralizes Instagram operations.

    Handles all Instagram API interactions through Facebook's GraphAPI,
    including media creation, carousel posts, publishing, and basic operations.
    Uses the same GraphAPI as Facebook since Instagram is part of Meta's ecosystem.
    """

    def __init__(self, access_token: str):
        """
        Initialize Instagram API client.

        Args:
            access_token (str): Instagram access token (Facebook token with Instagram permissions)
        """
        self.access_token = access_token
        self.graph_api: Optional[GraphAPI] = None
        self.api_version = "21.0"
        self._authenticated = False

    async def authenticate(self) -> bool:
        """
        Authenticate and initialize GraphAPI client for Instagram.

        Returns:
            bool: True if authentication successful

        Raises:
            Exception: If authentication fails
        """
        if self._authenticated:
            return True

        if not self.access_token:
            raise Exception('Instagram access token is required')

        try:
            self.graph_api = GraphAPI(access_token=self.access_token, version=self.api_version)
            self._authenticated = True
            return True
        except Exception as e:
            raise Exception(f'Instagram client authentication failed: {str(e)}')

    def disconnect(self):
        """
        Disconnect and clean up client resources.
        """
        self.graph_api = None
        self._authenticated = False

    def post_object(self, object_id: str, connection: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Post to an Instagram object connection using GraphAPI.

        Args:
            object_id (str): Instagram object ID
            connection (str): Connection type (media, media_publish, etc.)
            data (dict, optional): Data to post

        Returns:
            dict: Response from Instagram API

        Raises:
            Exception: If post fails
        """
        if not self.graph_api:
            raise Exception('Instagram GraphAPI not initialized')

        try:
            return self.graph_api.post_object(
                object_id=object_id,
                connection=connection,
                data=data or {}
            )
        except Exception as e:
            raise Exception(f'Instagram post_object failed: {str(e)}')

    def get_object(self, object_id: str, fields: Optional[str] = None) -> Dict[str, Any]:
        """
        Get an Instagram object using GraphAPI.

        Args:
            object_id (str): Instagram object ID
            fields (str, optional): Fields to retrieve

        Returns:
            dict: Object data from Instagram API

        Raises:
            Exception: If get fails
        """
        if not self.graph_api:
            raise Exception('Instagram GraphAPI not initialized')

        try:
            if fields:
                return self.graph_api.get_object(object_id=object_id, fields=fields)
            else:
                return self.graph_api.get_object(object_id=object_id)
        except Exception as e:
            raise Exception(f'Instagram get_object failed: {str(e)}')

    async def create_media(self, object_id: str, image_url: Optional[str] = None,
                           video_url: Optional[str] = None, caption: Optional[str] = None,
                           is_carousel_item: bool = False, media_type: Optional[str] = None) -> str:
        """
        Create media for Instagram post.

        Args:
            object_id (str): Instagram object ID
            image_url (str, optional): Image URL
            video_url (str, optional): Video URL
            caption (str, optional): Media caption
            is_carousel_item (bool): Whether this is part of a carousel
            media_type (str, optional): Media type (REELS, STORIES, VIDEO)

        Returns:
            str: Media ID

        Raises:
            Exception: If media creation fails
        """
        def _sync_create_media():
            data: Dict[str, Any] = {
                'is_carousel_item': is_carousel_item,
            }

            if video_url:
                data['video_url'] = video_url
                if media_type:
                    data['media_type'] = media_type
                elif not is_carousel_item:
                    data['media_type'] = 'VIDEO'
            elif image_url:
                data['image_url'] = image_url

            if caption and not is_carousel_item:
                data['caption'] = caption

            response = self.post_object(
                object_id=object_id,
                connection='media',
                data=data
            )
            return response['id']

        return await asyncio.to_thread(_sync_create_media)

    async def create_carousel(self, object_id: str, media_ids: List[str],
                              caption: Optional[str] = None) -> str:
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
        def _sync_create_carousel():
            data = {
                'media_type': 'CAROUSEL',
                'children': ','.join(media_ids),
            }

            if caption:
                data['caption'] = caption

            response = self.post_object(
                object_id=object_id,
                connection='media',
                data=data
            )
            return response['id']

        return await asyncio.to_thread(_sync_create_carousel)

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
        def _sync_publish_media():
            data = {
                'creation_id': creation_id,
            }

            response = self.post_object(
                object_id=object_id,
                connection='media_publish',
                data=data
            )
            return response['id']

        return await asyncio.to_thread(_sync_publish_media)

    async def create_post(self, object_id: str, image_url: Optional[str] = None,
                          video_url: Optional[str] = None, caption: Optional[str] = None,
                          media_type: Optional[str] = None) -> str:
        """
        Create and publish an Instagram post in one operation.

        Args:
            object_id (str): Instagram object ID
            image_url (str, optional): Image URL
            video_url (str, optional): Video URL
            caption (str, optional): Post caption
            media_type (str, optional): Media type (REELS, STORIES, VIDEO)

        Returns:
            str: Published post ID

        Raises:
            Exception: If post creation fails
        """
        # Create media first
        media_id = await self.create_media(
            object_id=object_id,
            image_url=image_url,
            video_url=video_url,
            caption=caption,
            media_type=media_type
        )

        # Then publish it
        return await self.publish_media(object_id=object_id, creation_id=media_id)

    async def create_carousel_post(self, object_id: str, media_items: List[Dict[str, Any]],
                                   caption: Optional[str] = None) -> str:
        """
        Create and publish a carousel post with multiple media items.

        Args:
            object_id (str): Instagram object ID
            media_items (list): List of media items, each with 'image_url' or 'video_url'
            caption (str, optional): Carousel caption

        Returns:
            str: Published carousel post ID

        Raises:
            Exception: If carousel creation fails
        """
        # Create individual media items
        media_ids = []
        for item in media_items:
            media_id = await self.create_media(
                object_id=object_id,
                image_url=item.get('image_url'),
                video_url=item.get('video_url'),
                is_carousel_item=True
            )
            media_ids.append(media_id)

        # Create carousel
        carousel_id = await self.create_carousel(
            object_id=object_id,
            media_ids=media_ids,
            caption=caption
        )

        # Publish carousel
        return await self.publish_media(object_id=object_id, creation_id=carousel_id)

    async def get_user_media(self, object_id: str, fields: Optional[str] = None,
                             limit: int = 25) -> Dict[str, Any]:
        """
        Get user's Instagram media.

        Args:
            object_id (str): Instagram object ID
            fields (str, optional): Fields to retrieve
            limit (int): Number of media items to retrieve

        Returns:
            dict: Media data from Instagram API

        Raises:
            Exception: If get fails
        """
        def _sync_get_user_media():
            default_fields = "id,caption,media_type,media_url,permalink,timestamp"
            query_fields = fields or default_fields

            return self.get_object(
                object_id=f"{object_id}/media",
                fields=f"{query_fields}&limit={limit}"
            )

        return await asyncio.to_thread(_sync_get_user_media)

    async def get_media_insights(self, media_id: str, metrics: List[str]) -> Dict[str, Any]:
        """
        Get insights for a specific Instagram media item.

        Args:
            media_id (str): Instagram media ID
            metrics (list): List of metrics to retrieve

        Returns:
            dict: Insights data from Instagram API

        Raises:
            Exception: If insights retrieval fails
        """
        def _sync_get_media_insights():
            return self.get_object(
                object_id=f"{media_id}/insights",
                fields=f"metric={','.join(metrics)}"
            )

        return await asyncio.to_thread(_sync_get_media_insights)
