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
from pyfacebook import GraphAPI

from .base import BaseAPI


class FacebookAPI(BaseAPI):
    """
    Facebook API handler that centralizes Facebook operations.

    Provides methods for Facebook authentication, token management,
    and all Facebook API operations including posts, likes, shares, and videos.
    """

    def __init__(self, access_token, client_id=None, client_secret=None, refresh_token=None):
        """
        Initialize Facebook API instance.

        Args:
            access_token (str): Facebook access token
            client_id (str, optional): Facebook client ID for token refresh
            client_secret (str, optional): Facebook client secret for token refresh
            refresh_token (str, optional): Facebook refresh token
        """
        super().__init__(
            access_token=access_token,
            client_id=client_id,
            client_secret=client_secret,
            refresh_token=refresh_token
        )
        self.access_token = access_token
        self.client_id = client_id
        self.client_secret = client_secret
        self.refresh_token = refresh_token
        self.client = None

    async def authenticate(self):
        """
        Authenticate with Facebook API and validate/refresh token if needed.

        Returns:
            FacebookAPI: Self for method chaining

        Raises:
            Exception: If authentication fails
        """
        if self._authenticated:
            return self

        if not self.access_token:
            raise Exception('Facebook access token is required.')

        # Create GraphAPI client
        self.client = GraphAPI(access_token=self.access_token, version="21.0")

        # Validate and refresh token if needed
        self.access_token = await self._validate_and_refresh_token()

        # Update client with potentially new token
        self.client = GraphAPI(access_token=self.access_token, version="21.0")

        self._authenticated = True
        return self

    async def disconnect(self):
        """
        Disconnect from Facebook API and clean up resources.
        """
        self.client = None
        self._authenticated = False

    async def _refresh_access_token(self):
        """
        Refresh Facebook access token using refresh token.

        Returns:
            tuple: (new_access_token, new_refresh_token)

        Raises:
            Exception: If token refresh fails
        """
        if not all([self.client_id, self.client_secret, self.refresh_token]):
            raise Exception('Client ID, client secret, and refresh token required for token refresh.')

        await self._rate_limit_check('token_refresh', 5.0)

        try:
            url = 'https://graph.facebook.com/v21.0/oauth/access_token'
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
            raise Exception(f'Failed to refresh Facebook access token: {str(e)}')

    async def _validate_and_refresh_token(self):
        """
        Validate Facebook access token and refresh if expired.

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
                    raise Exception('Facebook access token has expired and no refresh credentials provided.')

                # Attempt to refresh the token
                try:
                    new_access_token, new_refresh_token = await self._refresh_access_token()
                    print(f"Facebook token refreshed successfully. New access token: {new_access_token[:20]}...")
                    if new_refresh_token:
                        print(f"New refresh token: {new_refresh_token[:20]}...")

                    self.access_token = new_access_token
                    if new_refresh_token:
                        self.refresh_token = new_refresh_token

                    return new_access_token
                except Exception as refresh_error:
                    raise Exception(f'Facebook access token has expired and refresh failed: {str(refresh_error)}')
            else:
                # Re-raise the original exception if it's not token-related
                raise e

    async def create_post(self, object_id: str, message: Optional[str] = None,
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

        await self._rate_limit_check('create_post', 1.0)

        data: Dict[str, Any] = {'published': True}

        if link:
            data['link'] = link
        if message:
            data['message'] = message
        if attached_media:
            data['attached_media'] = json.dumps(attached_media)

        try:
            request = self.client.post_object(
                object_id=object_id,
                connection='feed',
                data=data
            )
            return request['id'].split('_')[1]
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
            return self.client.post_object(
                object_id=object_id,
                connection='photos',
                data={
                    'url': media_url,
                    'published': published
                }
            )
        except Exception as e:
            self._handle_api_error(e, 'Facebook media upload')
            raise

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
        if not self.client:
            raise Exception('Facebook API not authenticated')

        await self._rate_limit_check('like_post', 0.5)

        try:
            self.client.post_object(
                object_id=f'{object_id}_{post_id}',
                connection='likes'
            )
            return post_id
        except Exception as e:
            self._handle_api_error(e, 'Facebook like')
            raise

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
        if not self.client:
            raise Exception('Facebook API not authenticated')

        await self._rate_limit_check('delete_post', 0.5)

        try:
            self.client.delete_object(object_id=f'{object_id}_{post_id}')
            return post_id
        except Exception as e:
            self._handle_api_error(e, 'Facebook delete')
            raise

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
        if not self.client:
            raise Exception('Facebook API not authenticated')

        await self._rate_limit_check('share_post', 1.0)

        try:
            host = 'https://www.facebook.com'
            data = {
                'link': f'{host}/{object_id}/posts/{post_id}',
                'published': True
            }
            request = self.client.post_object(
                object_id=profile_id,
                connection='feed',
                data=data
            )
            return request['id'].split('_')[1]
        except Exception as e:
            self._handle_api_error(e, 'Facebook share')
            raise

    def get_api_info(self) -> Dict[str, Any]:
        """
        Get Facebook API configuration information.

        Returns:
            dict: API configuration details
        """
        return {
            'platform': 'Facebook',
            'authenticated': self._authenticated,
            'has_refresh_token': bool(self.refresh_token),
            'rate_limits': list(self._rate_limit_cache.keys())
        }
