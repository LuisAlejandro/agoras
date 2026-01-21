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

from .auth import LinkedInAuthManager


class LinkedInAPI(BaseAPI):
    """
    LinkedIn API handler that centralizes LinkedIn operations.

    Provides methods for LinkedIn authentication, token management,
    and all LinkedIn API operations including posts, likes, shares, and media uploads.
    """

    def __init__(self, user_id, client_id, client_secret, refresh_token=None):
        """
        Initialize LinkedIn API instance.

        Args:
            user_id (str): LinkedIn user ID (object ID)
            client_id (str): LinkedIn client ID
            client_secret (str): LinkedIn client secret
            refresh_token (str, optional): LinkedIn refresh token
        """
        super().__init__(
            access_token=None,  # Will be set by auth manager
            client_id=client_id,
            client_secret=client_secret,
            refresh_token=refresh_token
        )

        # Initialize the authentication manager
        self.auth_manager = LinkedInAuthManager(
            user_id=user_id,
            client_id=client_id,
            client_secret=client_secret,
            refresh_token=refresh_token
        )
        self.api_version = "202302"

    @property
    def user_id(self):
        """Get the LinkedIn user ID from the auth manager."""
        return self.auth_manager.user_id if self.auth_manager else None

    @property
    def client_id(self):
        """Get the LinkedIn client ID from the auth manager."""
        return self.auth_manager.client_id if self.auth_manager else None

    @property
    def client_secret(self):
        """Get the LinkedIn client secret from the auth manager."""
        return self.auth_manager.client_secret if self.auth_manager else None

    @property
    def access_token(self):
        """Get the LinkedIn access token from the auth manager."""
        return self.auth_manager.access_token if self.auth_manager else None

    @property
    def refresh_token(self):
        """Get the LinkedIn refresh token from the auth manager."""
        return self.auth_manager.refresh_token if self.auth_manager else None

    @property
    def user_info(self):
        """Get the LinkedIn user info from the auth manager."""
        return self.auth_manager.user_info if self.auth_manager else None

    @property
    def object_id(self):
        """Get the LinkedIn object ID from the auth manager's user info."""
        return self.user_info.get('object_id') if self.user_info else None

    async def authenticate(self):
        """
        Authenticate with LinkedIn API using the auth manager.

        Returns:
            LinkedInAPI: Self for method chaining

        Raises:
            Exception: If authentication fails
        """
        if self._authenticated:
            return self

        success = await self.auth_manager.authenticate()
        if not success:
            raise Exception('LinkedIn authentication failed')

        # Set the client from auth manager for BaseAPI compatibility
        self.client = self.auth_manager.client
        self._authenticated = True
        return self

    async def disconnect(self):
        """
        Disconnect from LinkedIn API and clean up resources.
        """
        # Disconnect the client first
        if self.client:
            self.client.disconnect()

        # Clear auth manager data
        if self.auth_manager:
            self.auth_manager.access_token = None

        # Clear BaseAPI client
        self.client = None
        self._authenticated = False

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
        self.auth_manager.ensure_authenticated()

        if not self.client or not self.object_id:
            raise Exception('LinkedIn API not authenticated')

        await self._rate_limit_check('upload_image', 1.0)

        try:
            return await self.client.upload_image(
                image_content=image_content,
                owner_urn=f"urn:li:person:{self.object_id}"
            )
        except Exception as e:
            self._handle_api_error(e, 'LinkedIn image upload')
            raise

    async def post(self, text: str, link: Optional[str] = None,
                   link_title: Optional[str] = None,
                   link_description: Optional[str] = None,
                   image_ids: Optional[List[str]] = None) -> str:
        """
        Create a LinkedIn post.

        Args:
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
        self.auth_manager.ensure_authenticated()

        if not self.client:
            raise Exception('LinkedIn API not authenticated')

        await self._rate_limit_check('post', 1.0)

        try:
            return await self.client.create_post(
                author_urn=f"urn:li:person:{self.object_id}",
                text=text,
                link=link,
                link_title=link_title,
                link_description=link_description,
                image_ids=image_ids
            )
        except Exception as e:
            self._handle_api_error(e, 'LinkedIn post creation')
            raise

    async def like(self, post_id: str) -> str:
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

        await self._rate_limit_check('like', 0.5)

        try:
            return await self.client.like_post(
                post_id=post_id,
                actor_urn=f"urn:li:person:{self.object_id}"
            )
        except Exception as e:
            self._handle_api_error(e, 'LinkedIn like')
            raise

    async def share(self, post_id: str) -> str:
        """
        Share (repost) a LinkedIn post.

        Args:
            post_id (str): Post ID to share

        Returns:
            str: Share ID

        Raises:
            Exception: If share operation fails
        """
        if not self.client:
            raise Exception('LinkedIn API not authenticated')

        await self._rate_limit_check('share_post', 1.0)

        try:
            return await self.client.share_post(
                post_id=post_id,
                author_urn=f"urn:li:person:{self.object_id}",
                commentary=""
            )
        except Exception as e:
            self._handle_api_error(e, 'LinkedIn share')
            raise

    async def delete(self, post_id: str) -> str:
        """
        Delete a LinkedIn post.

        Args:
            post_id (str): Post ID to delete

        Returns:
            str: Post ID

        Raises:
            Exception: If deletion fails
        """
        if not self.client:
            raise Exception('LinkedIn API not authenticated')

        await self._rate_limit_check('delete', 0.5)

        try:
            return await self.client.delete_post(post_id=post_id)
        except Exception as e:
            self._handle_api_error(e, 'LinkedIn delete')
            raise
