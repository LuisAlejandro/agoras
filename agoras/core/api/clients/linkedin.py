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

import requests
from linkedin_api.clients.restli.client import RestliClient


class LinkedInAPIClient:
    """
    LinkedIn API client that centralizes LinkedIn operations.

    Handles all LinkedIn API interactions through RestliClient,
    including posts, image uploads, likes, shares, and deletions.
    """

    def __init__(self, access_token: str):
        """
        Initialize LinkedIn API client.

        Args:
            access_token (str): LinkedIn access token
        """
        self.access_token = access_token
        self.restli_client: Optional[RestliClient] = None
        self.api_version = "202302"
        self._authenticated = False

    async def authenticate(self) -> bool:
        """
        Authenticate and initialize RestliClient.

        Returns:
            bool: True if authentication successful

        Raises:
            Exception: If authentication fails
        """
        if self._authenticated:
            return True

        if not self.access_token:
            raise Exception('LinkedIn access token is required')

        try:
            self.restli_client = RestliClient()
            self._authenticated = True
            return True
        except Exception as e:
            raise Exception(f'LinkedIn client authentication failed: {str(e)}')

    def disconnect(self):
        """
        Disconnect and clean up client resources.
        """
        self.restli_client = None
        self._authenticated = False

    async def upload_image(self, image_content: bytes, owner_urn: str) -> str:
        """
        Upload an image to LinkedIn.

        Args:
            image_content (bytes): Raw image content
            owner_urn (str): LinkedIn owner URN (e.g., "urn:li:person:12345")

        Returns:
            str: Media ID for the uploaded image

        Raises:
            Exception: If image upload fails
        """
        def _sync_upload():
            if not self.restli_client:
                raise Exception('LinkedIn RestliClient not initialized')
            if not self.access_token:
                raise Exception('No access token available')

            # Initialize upload
            request = self.restli_client.action(
                resource_path="/images",
                action_name="initializeUpload",
                action_params={
                    "initializeUploadRequest": {
                        "owner": owner_urn,
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

        return await asyncio.to_thread(_sync_upload)

    async def create_post(self,
                          author_urn: str,
                          text: str,
                          link: Optional[str] = None,
                          link_title: Optional[str] = None,
                          link_description: Optional[str] = None,
                          image_ids: Optional[List[str]] = None) -> str:
        """
        Create a LinkedIn post.

        Args:
            author_urn (str): LinkedIn author URN (e.g., "urn:li:person:12345")
            text (str): Post text content
            link (str, optional): URL to include
            link_title (str, optional): Title of the link
            link_description (str, optional): Description of the link
            image_ids (list, optional): List of uploaded image IDs

        Returns:
            str: Post ID

        Raises:
            Exception: If post creation fails
        """
        def _sync_create_post():
            if not self.restli_client:
                raise Exception('LinkedIn RestliClient not initialized')
            if not self.access_token:
                raise Exception('No access token available')

            entity = {
                "author": author_urn,
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

                if image_ids and len(image_ids) > 0:
                    entity["content"]["article"]["thumbnail"] = image_ids[0]

                if link_title:
                    entity["content"]["article"]["title"] = link_title

                if link_description:
                    entity["content"]["article"]["description"] = link_description

            # Handle media content (without link)
            elif not link and image_ids:
                if len(image_ids) == 1:
                    entity["content"] = {
                        "media": {"id": image_ids[0]}
                    }
                elif len(image_ids) > 1:
                    entity["content"] = {
                        "multiImage": {
                            "images": [{"id": image_id} for image_id in image_ids]
                        }
                    }

            request = self.restli_client.create(
                resource_path='/posts',
                entity=entity,
                version_string=self.api_version,
                access_token=self.access_token
            )

            if hasattr(request, 'entity_id') and request.entity_id:
                return str(request.entity_id)
            else:
                raise Exception('Invalid response from LinkedIn API')

        return await asyncio.to_thread(_sync_create_post)

    async def like_post(self, post_id: str, actor_urn: str) -> str:
        """
        Like a LinkedIn post.

        Args:
            post_id (str): Post ID to like
            actor_urn (str): LinkedIn actor URN (e.g., "urn:li:person:12345")

        Returns:
            str: Post ID

        Raises:
            Exception: If like operation fails
        """
        def _sync_like():
            if not self.restli_client:
                raise Exception('LinkedIn RestliClient not initialized')
            if not self.access_token:
                raise Exception('No access token available')

            entity = {
                "actor": actor_urn,
                "object": post_id,
            }

            request = self.restli_client.create(
                resource_path='/socialActions/{id}/likes',
                path_keys={"id": post_id},
                entity=entity,
                version_string=self.api_version,
                access_token=self.access_token
            )

            if request.status_code != 201:
                raise Exception(f'Unable to like post {post_id}')
            return post_id

        return await asyncio.to_thread(_sync_like)

    async def share_post(self, post_id: str, author_urn: str, commentary: str = "") -> str:
        """
        Share (repost) a LinkedIn post.

        Args:
            post_id (str): Post ID to share
            author_urn (str): LinkedIn author URN (e.g., "urn:li:person:12345")
            commentary (str, optional): Commentary to add to the share

        Returns:
            str: Share ID

        Raises:
            Exception: If share operation fails
        """
        def _sync_share():
            if not self.restli_client:
                raise Exception('LinkedIn RestliClient not initialized')
            if not self.access_token:
                raise Exception('No access token available')

            entity = {
                "author": author_urn,
                "commentary": commentary,
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

            request = self.restli_client.create(
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

        return await asyncio.to_thread(_sync_share)

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
        def _sync_delete():
            if not self.restli_client:
                raise Exception('LinkedIn RestliClient not initialized')
            if not self.access_token:
                raise Exception('No access token available')

            request = self.restli_client.delete(
                resource_path='/posts/{id}',
                path_keys={"id": post_id},
                version_string=self.api_version,
                access_token=self.access_token
            )

            if request.status_code != 204:
                raise Exception(f'Unable to delete post {post_id}')
            return post_id

        return await asyncio.to_thread(_sync_delete)

    async def get_user_info(self) -> Dict[str, Any]:
        """
        Get user information from LinkedIn API.

        Returns:
            dict: User information

        Raises:
            Exception: If request fails
        """
        def _sync_get_user_info():
            if not self.restli_client:
                raise Exception('LinkedIn RestliClient not initialized')
            if not self.access_token:
                raise Exception('No access token available')

            me = self.restli_client.get(resource_path='/userinfo', access_token=self.access_token)
            result = me.response.json()

            # Handle potential token expiration
            if result.get('code', '') == 'EXPIRED_ACCESS_TOKEN':
                raise Exception('LinkedIn access token has expired')

            return result

        return await asyncio.to_thread(_sync_get_user_info)
