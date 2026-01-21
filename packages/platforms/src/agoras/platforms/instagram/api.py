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

from typing import List, Optional

from agoras.core.api_base import BaseAPI

from .auth import InstagramAuthManager


class InstagramAPI(BaseAPI):
    """
    Instagram API handler that centralizes Instagram operations.

    Provides methods for Instagram authentication, token management,
    and all Instagram API operations including posts, videos, and media uploads.
    """

    def __init__(self, user_id, client_id, client_secret, refresh_token=None):
        """
        Initialize Instagram API instance.

        Args:
            user_id (str): Facebook user ID for Instagram business account
            client_id (str): Facebook client ID for token refresh
            client_secret (str): Facebook client secret for token refresh
            refresh_token (str, optional): Instagram refresh token
        """
        super().__init__(
            user_id=user_id,
            client_id=client_id,
            client_secret=client_secret,
            refresh_token=refresh_token
        )

        # Initialize the authentication manager
        self.auth_manager = InstagramAuthManager(
            user_id=user_id,
            client_id=client_id,
            client_secret=client_secret,
            refresh_token=refresh_token
        )

    @property
    def access_token(self):
        """Get the Instagram access token from the auth manager."""
        return self.auth_manager.access_token if self.auth_manager else None

    @property
    def user_info(self):
        """Get the Instagram user info from the auth manager."""
        return self.auth_manager.user_info if self.auth_manager else None

    async def authenticate(self):
        """
        Authenticate with Instagram API using the auth manager.

        Returns:
            InstagramAPI: Self for method chaining

        Raises:
            Exception: If authentication fails
        """
        if self._authenticated:
            return self

        success = await self.auth_manager.authenticate()
        if not success:
            raise Exception('Instagram authentication failed')

        # Set the client from auth manager for BaseAPI compatibility
        self.client = self.auth_manager.client
        self._authenticated = True
        return self

    async def disconnect(self):
        """
        Disconnect from Instagram API and clean up resources.
        """
        # Disconnect the client first
        if self.client:
            self.client.disconnect()

        # Clear auth manager tokens
        if self.auth_manager:
            self.auth_manager.access_token = None

        # Clear BaseAPI client
        self.client = None
        self._authenticated = False

    async def post(self, object_id: str, image_url: Optional[str] = None,
                   caption: Optional[str] = None, video_url: Optional[str] = None) -> str:
        """
        Create an Instagram post (media).

        Args:
            object_id (str): Instagram object ID
            image_url (str, optional): Image URL
            caption (str, optional): Post caption
            video_url (str, optional): Video URL (if posting video)

        Returns:
            str: Post ID

        Raises:
            Exception: If post creation fails
        """
        self.auth_manager.ensure_authenticated()

        if not self.client:
            raise Exception('Instagram API not authenticated')

        await self._rate_limit_check('post', 1.0)

        try:
            # Use client's create_post method which creates and publishes in one step
            return await self.client.create_post(
                object_id=object_id,
                image_url=image_url,
                video_url=video_url,
                caption=caption
            )
        except Exception as e:
            self._handle_api_error(e, 'Instagram post creation')
            raise

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
        self.auth_manager.ensure_authenticated()

        if not self.client:
            raise Exception('Instagram API not authenticated')

        await self._rate_limit_check('create_media', 1.0)

        try:
            return await self.client.create_media(
                object_id=object_id,
                image_url=image_url,
                video_url=video_url,
                caption=caption,
                is_carousel_item=is_carousel_item,
                media_type=media_type
            )
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

        try:
            return await self.client.create_carousel(
                object_id=object_id,
                media_ids=media_ids,
                caption=caption
            )
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

        try:
            return await self.client.publish_media(
                object_id=object_id,
                creation_id=creation_id
            )
        except Exception as e:
            self._handle_api_error(e, 'Instagram media publishing')
            raise

    async def like(self, post_id: str) -> str:
        """
        Like an Instagram post (not supported via API).

        Args:
            post_id (str): Post ID to like

        Raises:
            Exception: Like not supported for Instagram
        """
        raise Exception('Like not supported for Instagram')

    async def delete(self, post_id: str) -> str:
        """
        Delete an Instagram post (not supported via API).

        Args:
            post_id (str): Post ID to delete

        Raises:
            Exception: Delete not supported for Instagram
        """
        raise Exception('Delete not supported for Instagram')

    async def share(self, post_id: str) -> str:
        """
        Share an Instagram post (not supported via API).

        Args:
            post_id (str): Post ID to share

        Raises:
            Exception: Share not supported for Instagram
        """
        raise Exception('Share not supported for Instagram')
