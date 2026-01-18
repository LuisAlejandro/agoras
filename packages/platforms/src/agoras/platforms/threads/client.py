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

import time
from typing import Any, Dict, List, Optional

import requests


class ThreadsAPIClient:
    """
    Threads API client for making HTTP requests to Threads endpoints.

    Centralizes all Threads API calls including authentication, content publishing,
    and user profile operations using Meta's Threads Graph API.
    """

    def __init__(self, access_token: str, user_id: str):
        """
        Initialize Threads API client.

        Args:
            access_token (str): Threads access token for authenticated requests
            user_id (str): Threads user ID for API operations
        """
        self.access_token = access_token
        self.user_id = user_id
        self.base_url = "https://graph.threads.net/v1.0"

    def get_profile(self) -> Dict[str, Any]:
        """
        Get user profile information from Threads API.

        Returns:
            dict: User profile information containing user_id and token validity

        Raises:
            Exception: If API call fails or not authenticated
        """
        if not self.access_token:
            raise Exception('No access token available')

        if not self.user_id:
            raise Exception('No user ID available')

        try:
            # Return basic info we have (no API call needed for profile)
            profile_data = {
                'user_id': self.user_id,
                'access_token_valid': bool(self.access_token)
            }

            return profile_data
        except Exception as e:
            raise Exception(f"Failed to get profile: {str(e)}")

    def create_post(self, post_text: str, files: Optional[List[str]] = None,
                    file_captions: Optional[List[str]] = None,
                    who_can_reply: str = "everyone") -> Dict[str, Any]:
        """
        Create a post on Threads using Meta's Graph API.

        Args:
            post_text (str): Text content of the post
            files (list, optional): List of file URLs to attach
            file_captions (list, optional): Captions for files
            who_can_reply (str): Who can reply to this post

        Returns:
            dict: Post creation response

        Raises:
            Exception: If post creation fails or not authenticated
        """
        if not self.access_token:
            raise Exception('No access token available')

        if not self.user_id:
            raise Exception('No user ID available')

        files = files or []
        file_captions = file_captions or []

        try:
            # Determine post type and build container creation data
            container_data = {
                'access_token': self.access_token,
                'text': post_text,
                'reply_control': who_can_reply
            }

            if len(files) == 0:
                # Text-only post
                container_data['media_type'] = 'TEXT'
            elif len(files) == 1:
                # Single image post
                container_data['media_type'] = 'IMAGE'
                container_data['image_url'] = files[0]
                if file_captions and file_captions[0]:
                    container_data['alt_text'] = file_captions[0]
            else:
                # Carousel post (2-4 images)
                # First create individual carousel item containers
                item_ids = []
                for image_url in files:
                    item_data = {
                        'access_token': self.access_token,
                        'media_type': 'IMAGE',
                        'image_url': image_url,
                        'is_carousel_item': True
                    }
                    resp = requests.post(
                        f"{self.base_url}/me/threads",
                        data=item_data,
                        timeout=30
                    )
                    self._check_response(resp)
                    item_ids.append(resp.json()['id'])

                # Now create the carousel container
                container_data['media_type'] = 'CAROUSEL'
                container_data['children'] = ','.join(item_ids)

            # Create the container
            resp = requests.post(
                f"{self.base_url}/me/threads",
                data=container_data,
                timeout=30
            )
            self._check_response(resp)
            creation_id = resp.json()['id']

            # Wait a bit for container to be ready (Meta recommends this)
            time.sleep(2)

            # Publish the container
            publish_data = {
                'access_token': self.access_token,
                'creation_id': creation_id
            }

            publish_resp = requests.post(
                f"{self.base_url}/{self.user_id}/threads_publish",
                data=publish_data,
                timeout=30
            )
            self._check_response(publish_resp)

            return {'id': publish_resp.json()['id']}

        except Exception as e:
            raise Exception(f"Failed to create post: {str(e)}")

    def _check_response(self, response: requests.Response):
        """Check API response for errors and raise appropriate exceptions."""
        if response.status_code != 200:
            try:
                error_data = response.json()
                if 'error' in error_data:
                    raise Exception(f"API error: {error_data['error'].get('message', str(error_data))}")
            except ValueError:
                pass
            raise Exception(f"HTTP {response.status_code}: {response.text}")

    def repost_post(self, post_id: str) -> Dict[str, Any]:
        """
        Repost an existing post using Meta's Graph API.

        Args:
            post_id (str): ID of the post to repost

        Returns:
            dict: Repost response

        Raises:
            Exception: If repost fails or not authenticated
        """
        if not self.access_token:
            raise Exception('No access token available')

        if not self.user_id:
            raise Exception('No user ID available')

        try:
            data = {'access_token': self.access_token}

            response = requests.post(
                f"{self.base_url}/{post_id}/repost",
                data=data,
                timeout=30
            )
            self._check_response(response)

            return {'id': response.json()['id']}
        except Exception as e:
            raise Exception(f"Failed to repost: {str(e)}")
