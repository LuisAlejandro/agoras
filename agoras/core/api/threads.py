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
from typing import Any, Dict, List, Optional, Tuple

from agoras.core.media import MediaFactory

from .auth import ThreadsAuthManager
from .base import BaseAPI


class ThreadsAPI(BaseAPI):
    """
    Threads API handler that centralizes Threads operations.

    Provides methods for Threads authentication, post creation, replies,
    reposts, and all Threads API operations using threadspipepy.
    """

    def __init__(self, app_id: str, app_secret: str, redirect_uri: str,
                 refresh_token: Optional[str] = None):
        """
        Initialize Threads API instance.

        Args:
            app_id (str): Threads app ID
            app_secret (str): Threads app secret
            redirect_uri (str): OAuth redirect URI
            refresh_token (str, optional): Threads refresh token
        """
        super().__init__(
            app_id=app_id,
            app_secret=app_secret,
            redirect_uri=redirect_uri,
            refresh_token=refresh_token
        )

        # Initialize the authentication manager
        self.auth_manager = ThreadsAuthManager(
            app_id=app_id,
            app_secret=app_secret,
            redirect_uri=redirect_uri,
            refresh_token=refresh_token
        )

    @property
    def access_token(self):
        """Get the Threads access token from the auth manager."""
        return self.auth_manager.access_token if self.auth_manager else None

    @property
    def user_id(self):
        """Get the Threads user ID from the auth manager."""
        return self.auth_manager.user_id if self.auth_manager else None

    @property
    def user_info(self):
        """Get the Threads user info from the auth manager."""
        return self.auth_manager.user_info if self.auth_manager else None

    async def authenticate(self):
        """
        Authenticate with Threads API using the auth manager.

        Returns:
            ThreadsAPI: Self for method chaining

        Raises:
            Exception: If authentication fails
        """
        if self._authenticated:
            return self

        success = await self.auth_manager.authenticate()
        if not success:
            raise Exception('Threads authentication failed')

        self.client = self.auth_manager.client
        self._authenticated = True
        return self

    async def disconnect(self):
        """
        Disconnect from Threads API and clean up resources.
        """
        # Clear BaseAPI client
        self.client = None
        self._authenticated = False

    async def _validate_and_download_images(
        self, files: List[str], file_captions: Optional[List[str]]
    ) -> Tuple[List[str], List[str], List[Any]]:
        """
        Download and validate images using Media system.

        Args:
            files: List of file URLs to download and validate
            file_captions: Optional list of captions for files

        Returns:
            tuple: (validated_files, validated_captions, images)

        Raises:
            Exception: If validation or download fails
        """
        validated_files = []
        validated_captions = []
        images = []

        # Filter out None/empty values
        valid_file_urls = [f for f in files if f]

        if not valid_file_urls:
            raise Exception('Files list contains no valid URLs')

        try:
            # Download and validate all images concurrently
            images = await MediaFactory.download_images(valid_file_urls)

            # Validate each image and collect validated URLs
            for idx, image in enumerate(images):
                if not image.content or not image.file_type:
                    raise Exception(f'Failed to download or validate image: {image.url}')

                # Validate image format (Threads supports JPEG, PNG)
                if image.file_type.mime not in ['image/jpeg', 'image/png', 'image/jpg']:
                    raise Exception(
                        f'Invalid image type "{image.file_type.mime}" for {image.url}. '
                        'Threads supports JPEG and PNG only.'
                    )

                # Use the original URL (ThreadsPipe handles URL downloads)
                # Media system validation ensures the URL is valid and accessible
                validated_files.append(image.url)

                # Handle file captions - align with validated files
                if file_captions and idx < len(file_captions):
                    validated_captions.append(file_captions[idx])

            return validated_files, validated_captions, images

        except Exception as e:
            # Clean up any downloaded images on error
            for image in images:
                try:
                    image.cleanup()
                except Exception:
                    pass
            # Re-raise with more context if it's not already our formatted exception
            error_msg = str(e)
            if not error_msg.startswith('Media validation failed'):
                raise Exception(f'Media validation failed: {error_msg}')
            raise

    async def get_profile(self) -> Dict[str, Any]:
        """
        Get user profile information from Threads API.

        Returns:
            dict: User profile information

        Raises:
            Exception: If API call fails
        """
        if not self.access_token:
            raise Exception('Threads API not authenticated')

        def _sync_get_profile():
            if not self.client:
                raise Exception('Threads client not available')
            return self.client.get_profile()

        try:
            profile_info = await asyncio.to_thread(_sync_get_profile)
            return profile_info
        except Exception as e:
            self._handle_api_error(e, 'Threads get profile')
            raise

    async def create_post(self, post_text: str, files: Optional[List[str]] = None,
                          file_captions: Optional[List[str]] = None,
                          who_can_reply: str = "everyone") -> str:
        """
        Create a post on Threads.

        Args:
            post_text (str): Text content of the post
            files (list, optional): List of file URLs to attach
            file_captions (list, optional): Captions for files (must align with files array)
            who_can_reply (str): Who can reply to this post

        Returns:
            str: Post ID

        Raises:
            Exception: If post creation fails
        """
        self.auth_manager.ensure_authenticated()

        if not self.access_token:
            raise Exception('Threads API not authenticated')

        if not self.client:
            raise Exception('Threads client not available')

        await self._rate_limit_check('create_post', 2.0)

        # Validate file_captions length matches files if both provided
        if file_captions and files and len(file_captions) != len(files):
            raise Exception(
                f'File captions count ({len(file_captions)}) must match files count '
                f'({len(files)})'
            )

        # Download and validate images using Media system if files are provided
        validated_files = []
        validated_captions = []
        images = []

        if files:
            validated_files, validated_captions, images = await self._validate_and_download_images(
                files, file_captions
            )

        def _sync_create_post():
            if not self.client:
                raise Exception('Threads client not available')
            return self.client.create_post(
                post_text=post_text,
                files=validated_files if validated_files else None,
                file_captions=validated_captions if validated_captions else None,
                who_can_reply=who_can_reply
            )

        try:
            response = await asyncio.to_thread(_sync_create_post)

            # Extract post ID from response
            post_id = response.get('id') or response.get('post_id') or str(response)
            return post_id
        except Exception as e:
            self._handle_api_error(e, 'Threads post creation')
            raise
        finally:
            # Clean up all downloaded images
            for image in images:
                try:
                    image.cleanup()
                except Exception:
                    pass

    async def repost_post(self, post_id: str) -> str:
        """
        Repost an existing post.

        Args:
            post_id (str): ID of the post to repost

        Returns:
            str: Repost ID

        Raises:
            Exception: If repost fails
        """
        self.auth_manager.ensure_authenticated()

        if not self.access_token:
            raise Exception('Threads API not authenticated')

        if not self.client:
            raise Exception('Threads client not available')

        await self._rate_limit_check('repost_post', 2.0)

        def _sync_repost():
            if not self.client:
                raise Exception('Threads client not available')
            return self.client.repost_post(post_id=post_id)

        try:
            response = await asyncio.to_thread(_sync_repost)

            # Extract repost ID from response
            repost_id = response.get('id') or response.get('repost_id') or str(response)
            return repost_id
        except Exception as e:
            self._handle_api_error(e, 'Threads repost')
            raise

    # BaseAPI abstract method implementations
    async def post(self, post_text: str, files: Optional[List[str]] = None,
                   file_captions: Optional[List[str]] = None) -> str:
        """
        Create a post on Threads (BaseAPI interface implementation).

        Args:
            post_text (str): Text content of the post
            files (list, optional): List of file URLs to attach
            file_captions (list, optional): Captions for files

        Returns:
            str: Post ID
        """
        return await self.create_post(post_text, files, file_captions)

    async def like(self, post_id: str) -> str:
        """
        Like a Threads post (not supported via API).

        Args:
            post_id (str): Post ID to like

        Raises:
            Exception: Like not supported for Threads
        """
        raise Exception('Like not supported for Threads')

    async def delete(self, post_id: str) -> str:
        """
        Delete a Threads post (not supported via API).

        Args:
            post_id (str): Post ID to delete

        Raises:
            Exception: Delete not supported for Threads
        """
        raise Exception('Delete not supported for Threads')

    async def share(self, post_id: str) -> str:
        """
        Share/repost a Threads post.

        Args:
            post_id (str): Post ID to share

        Returns:
            str: Share/Repost ID
        """
        return await self.repost_post(post_id)
