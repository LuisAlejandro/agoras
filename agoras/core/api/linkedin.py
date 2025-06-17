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
from linkedin_api.clients.restli.client import RestliClient
from linkedin_api.clients.auth.client import AuthClient

from .base import BaseAPI


class LinkedInAPI(BaseAPI):
    """
    LinkedIn API handler that centralizes LinkedIn operations.

    Provides methods for LinkedIn authentication, token management,
    and all LinkedIn API operations including posts, likes, shares, and media uploads.
    """

    def __init__(self, access_token, client_id=None, client_secret=None, refresh_token=None):
        """
        Initialize LinkedIn API instance.

        Args:
            access_token (str): LinkedIn access token
            client_id (str, optional): LinkedIn client ID for token refresh
            client_secret (str, optional): LinkedIn client secret for token refresh
            refresh_token (str, optional): LinkedIn refresh token
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
        self.object_id = None
        self.api_version = "202302"

    async def authenticate(self):
        """
        Authenticate with LinkedIn API and validate/refresh token if needed.

        Returns:
            LinkedInAPI: Self for method chaining

        Raises:
            Exception: If authentication fails
        """
        if self._authenticated:
            return self

        if not self.access_token:
            raise Exception('LinkedIn access token is required.')

        # Create RestliClient
        self.client = RestliClient()

        # Get object ID and validate/refresh token
        self.object_id, self.access_token = await self._get_object_id_and_validate_token()

        self._authenticated = True
        return self

    async def disconnect(self):
        """
        Disconnect from LinkedIn API and clean up resources.
        """
        self.client = None
        self.object_id = None
        self._authenticated = False

    async def _refresh_access_token(self):
        """
        Refresh LinkedIn access token using refresh token.

        Returns:
            tuple: (new_access_token, new_refresh_token)

        Raises:
            Exception: If token refresh fails
        """
        if not all([self.client_id, self.client_secret, self.refresh_token]):
            raise Exception('Client ID, client secret, and refresh token required for token refresh.')

        await self._rate_limit_check('token_refresh', 5.0)

        try:
            if not all([self.client_id, self.client_secret, self.refresh_token]):
                raise Exception('Missing required credentials for token refresh')
            auth_client = AuthClient(client_id=str(self.client_id), client_secret=str(self.client_secret))
            token_response = auth_client.exchange_refresh_token_for_access_token(refresh_token=str(self.refresh_token))
            
            new_access_token = token_response.access_token
            new_refresh_token = getattr(token_response, 'refresh_token', None)

            if not new_access_token:
                raise Exception('No access token in refresh response')

            return new_access_token, new_refresh_token
        except Exception as e:
            raise Exception(f'Failed to refresh LinkedIn access token: {str(e)}')

    async def _get_object_id_and_validate_token(self):
        """
        Get LinkedIn object ID and validate/refresh token if needed.

        Returns:
            tuple: (object_id, valid_access_token)

        Raises:
            Exception: If unable to get object ID or refresh token
        """
        def _sync_get_object_id():
            if not self.client:
                raise Exception('LinkedIn client not initialized')
            me = self.client.get(resource_path='/userinfo', access_token=self.access_token)
            return me.response.json()

        try:
            result = await asyncio.to_thread(_sync_get_object_id)
        except Exception as e:
            raise Exception(f'Failed to get LinkedIn user info: {str(e)}')

        if result.get('code', '') == 'EXPIRED_ACCESS_TOKEN':
            if not all([self.client_id, self.client_secret, self.refresh_token]):
                raise Exception('LinkedIn access token has expired and no refresh credentials provided.')

            # Attempt to refresh the token
            try:
                new_access_token, new_refresh_token = await self._refresh_access_token()
                print(f"LinkedIn token refreshed successfully. New access token: {new_access_token[:20]}...")
                if new_refresh_token:
                    print(f"New refresh token: {new_refresh_token[:20]}...")

                # Retry the request with the new token
                self.access_token = new_access_token
                if new_refresh_token:
                    self.refresh_token = new_refresh_token

                def _retry_get():
                    if not self.client:
                        raise Exception('LinkedIn client not initialized')
                    return self.client.get(resource_path='/userinfo', access_token=self.access_token).response.json()
                result = await asyncio.to_thread(_retry_get)

            except Exception as refresh_error:
                raise Exception(f'LinkedIn access token has expired and refresh failed: {str(refresh_error)}')

        object_id = result.get('sub', '')
        if not object_id:
            raise Exception('Unable to get LinkedIn object ID.')

        return object_id, self.access_token

    async def upload_image(self, image_content: bytes) -> str:
        """
        Upload an image to LinkedIn.

        Args:
            image_content (bytes): Raw image content

        Returns:
            str: Media ID for the uploaded image

        Raises:
            Exception: If image upload fails
        """
        if not self.client or not self.object_id:
            raise Exception('LinkedIn API not authenticated')

        await self._rate_limit_check('upload_image', 1.0)

        def _sync_upload():
            if not self.client:
                raise Exception('LinkedIn client not initialized')
            # Initialize upload
            request = self.client.action(
                resource_path="/images",
                action_name="initializeUpload",
                action_params={
                    "initializeUploadRequest": {
                        "owner": f"urn:li:person:{self.object_id}",
                    }
                },
                version_string=self.api_version,
                access_token=self.access_token
            )

            response = request.response.json()
            upload_url = response.get('value', {}).get('uploadUrl', '')
            media_id = response.get('value', {}).get('image', '')

            if not upload_url or not media_id:
                raise Exception('Failed to get upload URL or media ID from LinkedIn')

            # Upload the image content
            upload_response = requests.put(
                upload_url,
                headers={'Authorization': f'Bearer {self.access_token}'},
                data=image_content
            )

            if upload_response.status_code != 201:
                raise Exception(f'Failed to upload image: {upload_response.status_code}')

            return media_id

        try:
            await asyncio.sleep(random.randrange(1, 5))
            media_id = await asyncio.to_thread(_sync_upload)
            return media_id
        except Exception as e:
            self._handle_api_error(e, 'LinkedIn image upload')
            raise

    async def create_post(self, text: str, link: Optional[str] = None, 
                          link_title: Optional[str] = None, link_description: Optional[str] = None, 
                          media_ids: Optional[List[str]] = None) -> str:
        """
        Create a LinkedIn post.

        Args:
            text (str): Post text content
            link (str, optional): Link URL
            link_title (str, optional): Link title
            link_description (str, optional): Link description
            media_ids (list, optional): List of media IDs

        Returns:
            str: Post ID

        Raises:
            Exception: If post creation fails
        """
        if not self.client or not self.object_id:
            raise Exception('LinkedIn API not authenticated')

        await self._rate_limit_check('create_post', 1.0)

        entity = {
            "author": f"urn:li:person:{self.object_id}",
            "commentary": text,
            "visibility": "PUBLIC",
            "distribution": {
                "feedDistribution": "MAIN_FEED",
                "targetEntities": [],
                "thirdPartyDistributionChannels": []
            },
            "lifecycleState": "PUBLISHED",
            "isReshareDisabledByAuthor": False
        }

        # Handle link content
        if link and text:
            entity["content"] = {
                "article": {
                    "source": link,
                    "title": text,
                }
            }

            if media_ids and len(media_ids) > 0:
                entity["content"]["article"]["thumbnail"] = media_ids[0]

            if link_title:
                entity["content"]["article"]["title"] = link_title

            if link_description:
                entity["content"]["article"]["description"] = link_description

        # Handle media content (without link)
        elif not link and media_ids:
            if len(media_ids) == 1:
                entity["content"] = {
                    "media": {"id": media_ids[0]}
                }
            elif len(media_ids) > 1:
                entity["content"] = {
                    "multiImage": {
                        "images": [{"id": media_id} for media_id in media_ids]
                    }
                }

        def _sync_create_post():
            if not self.client:
                raise Exception('LinkedIn client not initialized')
            request = self.client.create(
                resource_path='/posts',
                entity=entity,
                version_string=self.api_version,
                access_token=self.access_token
            )
            if hasattr(request, 'entity_id') and request.entity_id:
                return str(request.entity_id)
            else:
                raise Exception('Invalid response from LinkedIn API')

        try:
            await asyncio.sleep(random.randrange(1, 5))
            post_id = await asyncio.to_thread(_sync_create_post)
            return post_id
        except Exception as e:
            self._handle_api_error(e, 'LinkedIn post creation')
            raise

    async def like_post(self, post_id: str) -> str:
        """
        Like a LinkedIn post.

        Args:
            post_id (str): Post ID to like

        Returns:
            str: Post ID

        Raises:
            Exception: If like operation fails
        """
        if not self.client or not self.object_id:
            raise Exception('LinkedIn API not authenticated')

        await self._rate_limit_check('like_post', 0.5)

        entity = {
            "actor": f"urn:li:person:{self.object_id}",
            "object": post_id,
        }

        def _sync_like():
            if not self.client:
                raise Exception('LinkedIn client not initialized')
            request = self.client.create(
                resource_path='/socialActions/{id}/likes',
                path_keys={"id": post_id},
                entity=entity,
                version_string=self.api_version,
                access_token=self.access_token
            )
            if request.status_code != 201:
                raise Exception(f'Unable to like post {post_id}')
            return post_id

        try:
            await asyncio.sleep(random.randrange(1, 5))
            result = await asyncio.to_thread(_sync_like)
            return result
        except Exception as e:
            self._handle_api_error(e, 'LinkedIn like')
            raise

    async def share_post(self, post_id: str) -> str:
        """
        Share a LinkedIn post.

        Args:
            post_id (str): Post ID to share

        Returns:
            str: New post ID

        Raises:
            Exception: If sharing fails
        """
        if not self.client or not self.object_id:
            raise Exception('LinkedIn API not authenticated')

        await self._rate_limit_check('share_post', 1.0)

        entity = {
            "author": f"urn:li:person:{self.object_id}",
            "commentary": "",
            "visibility": "PUBLIC",
            "distribution": {
                "feedDistribution": "MAIN_FEED",
                "targetEntities": [],
                "thirdPartyDistributionChannels": []
            },
            "lifecycleState": "PUBLISHED",
            "isReshareDisabledByAuthor": False,
            "reshareContext": {
                "parent": post_id
            }
        }

        def _sync_share():
            if not self.client:
                raise Exception('LinkedIn client not initialized')
            request = self.client.create(
                resource_path='/posts',
                entity=entity,
                version_string=self.api_version,
                access_token=self.access_token
            )
            if request.status_code != 201:
                raise Exception(f'Unable to share post {post_id}')
            if hasattr(request, 'entity_id') and request.entity_id:
                return str(request.entity_id)
            else:
                raise Exception('Invalid response from LinkedIn API')

        try:
            await asyncio.sleep(random.randrange(1, 5))
            new_post_id = await asyncio.to_thread(_sync_share)
            return new_post_id
        except Exception as e:
            self._handle_api_error(e, 'LinkedIn share')
            raise

    async def delete_post(self, post_id: str) -> str:
        """
        Delete a LinkedIn post.

        Args:
            post_id (str): Post ID to delete

        Returns:
            str: Post ID

        Raises:
            Exception: If deletion fails
        """
        if not self.client or not self.object_id:
            raise Exception('LinkedIn API not authenticated')

        await self._rate_limit_check('delete_post', 0.5)

        def _sync_delete():
            if not self.client:
                raise Exception('LinkedIn client not initialized')
            request = self.client.delete(
                resource_path='/posts/{id}',
                path_keys={"id": post_id},
                version_string=self.api_version,
                access_token=self.access_token
            )
            if request.status_code != 204:
                raise Exception(f'Unable to delete post {post_id}')
            return post_id

        try:
            await asyncio.sleep(random.randrange(1, 5))
            result = await asyncio.to_thread(_sync_delete)
            return result
        except Exception as e:
            self._handle_api_error(e, 'LinkedIn delete')
            raise

    def get_api_info(self) -> Dict[str, Any]:
        """
        Get LinkedIn API configuration information.

        Returns:
            dict: API configuration details
        """
        return {
            'platform': 'LinkedIn',
            'authenticated': self._authenticated,
            'has_refresh_token': bool(self.refresh_token),
            'object_id': self.object_id,
            'rate_limits': list(self._rate_limit_cache.keys())
        } 