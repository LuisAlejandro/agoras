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
import random
from typing import Any, Dict, List, Optional

import requests
from pyfacebook import GraphAPI

from .base import BaseAPI


class InstagramAPI(BaseAPI):
    """
    Instagram API handler that centralizes Instagram operations.

    Provides methods for Instagram authentication, token management,
    and all Instagram API operations including posts, videos, and media uploads.
    """

    def __init__(self, access_token, client_id=None, client_secret=None, refresh_token=None):
        """
        Initialize Instagram API instance.

        Args:
            access_token (str): Instagram access token
            client_id (str, optional): Instagram client ID for token refresh
            client_secret (str, optional): Instagram client secret for token refresh
            refresh_token (str, optional): Instagram refresh token
        """
        super().__init__(
            access_token=access_token or '',
            client_id=client_id or '',
            client_secret=client_secret or '',
            refresh_token=refresh_token or ''
        )
        self.access_token = access_token
        self.client_id = client_id
        self.client_secret = client_secret
        self.refresh_token = refresh_token
        self.client = None

    async def authenticate(self):
        """
        Authenticate with Instagram API and validate/refresh token if needed.

        Returns:
            InstagramAPI: Self for method chaining

        Raises:
            Exception: If authentication fails
        """
        if self._authenticated:
            return self

        if not self.access_token:
            raise Exception('Instagram access token is required.')

        # Create GraphAPI client
        self.client = GraphAPI(access_token=self.access_token, version="14.0")

        # Validate and refresh token if needed
        self.access_token = await self._validate_and_refresh_token()

        # Update client with potentially new token
        self.client = GraphAPI(access_token=self.access_token, version="14.0")

        self._authenticated = True
        return self

    async def disconnect(self):
        """
        Disconnect from Instagram API and clean up resources.
        """
        self.client = None
        self._authenticated = False

    async def _refresh_access_token(self):
        """
        Refresh Instagram access token using refresh token.

        Returns:
            tuple: (new_access_token, new_refresh_token)

        Raises:
            Exception: If token refresh fails
        """
        if not all([self.client_id, self.client_secret, self.refresh_token]):
            raise Exception('Client ID, client secret, and refresh token required for token refresh.')

        await self._rate_limit_check('token_refresh', 5.0)

        try:
            url = 'https://graph.facebook.com/v14.0/oauth/access_token'
            params = {
                'grant_type': 'refresh_token',
                'refresh_token': self.refresh_token,
                'client_id': self.client_id,
                'client_secret': self.client_secret
            }

            response = requests.get(url, params=params)
            response.raise_for_status()

            token_data = response.json()
            new_access_token = token_data.get('access_token')
            new_refresh_token = token_data.get('refresh_token')

            if not new_access_token:
                raise Exception('No access token in refresh response')

            return new_access_token, new_refresh_token
        except Exception as e:
            raise Exception(f'Failed to refresh Instagram access token: {str(e)}')

    async def _validate_and_refresh_token(self):
        """
        Validate Instagram access token and refresh if expired.

        Returns:
            str: Valid access token

        Raises:
            Exception: If token validation and refresh both fail
        """
        try:
            # Test token validity by making a simple API call
            if self.client:
                self.client.get_object(object_id='me', fields='id,name')
            return self.access_token  # Token is valid
        except Exception as e:
            error_str = str(e).lower()
            if 'expired' in error_str or 'invalid' in error_str or 'token' in error_str:
                if not all([self.client_id, self.client_secret, self.refresh_token]):
                    raise Exception('Instagram access token has expired and no refresh credentials provided.')

                # Attempt to refresh the token
                try:
                    new_access_token, new_refresh_token = await self._refresh_access_token()
                    print(f"Instagram token refreshed successfully. New access token: {new_access_token[:20]}...")
                    if new_refresh_token:
                        print(f"New refresh token: {new_refresh_token[:20]}...")

                    self.access_token = new_access_token
                    if new_refresh_token:
                        self.refresh_token = new_refresh_token

                    return new_access_token
                except Exception as refresh_error:
                    raise Exception(f'Instagram access token has expired and refresh failed: {str(refresh_error)}')
            else:
                # Re-raise the original exception if it's not token-related
                raise e

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
        if not self.client:
            raise Exception('Instagram API not authenticated')

        await self._rate_limit_check('create_media', 1.0)

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

        try:
            await asyncio.sleep(random.randrange(1, 5))
            media = self.client.post_object(
                object_id=object_id,
                connection='media',
                data=data
            )
            return media['id']
        except Exception as e:
            self._handle_api_error(e, 'Instagram media creation')
            raise

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
        if not self.client:
            raise Exception('Instagram API not authenticated')

        await self._rate_limit_check('create_carousel', 1.0)

        data = {
            'media_type': 'CAROUSEL',
            'children': ','.join(media_ids),
        }

        if caption:
            data['caption'] = caption

        try:
            await asyncio.sleep(random.randrange(1, 5))
            carousel = self.client.post_object(
                object_id=object_id,
                connection='media',
                data=data
            )
            return carousel['id']
        except Exception as e:
            self._handle_api_error(e, 'Instagram carousel creation')
            raise

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
        if not self.client:
            raise Exception('Instagram API not authenticated')

        await self._rate_limit_check('publish_media', 1.0)

        data = {
            'creation_id': creation_id,
        }

        try:
            await asyncio.sleep(random.randrange(1, 5))
            request = self.client.post_object(
                object_id=object_id,
                connection='media_publish',
                data=data
            )
            return request['id']
        except Exception as e:
            self._handle_api_error(e, 'Instagram media publishing')
            raise

    def get_api_info(self) -> Dict[str, Any]:
        """
        Get Instagram API configuration information.

        Returns:
            dict: API configuration details
        """
        return {
            'platform': 'Instagram',
            'authenticated': self._authenticated,
            'has_refresh_token': bool(self.refresh_token),
            'rate_limits': list(self._rate_limit_cache.keys())
        }
