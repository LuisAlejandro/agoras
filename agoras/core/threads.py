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

from agoras.core.api.threads import ThreadsAPI
from agoras.core.base import SocialNetwork


class Threads(SocialNetwork):
    """
    Threads social network implementation.

    This class provides Threads-specific functionality for posting messages,
    images, videos, replies, and managing Threads interactions asynchronously.
    """

    def __init__(self, **kwargs):
        """
        Initialize Threads instance.

        Args:
            **kwargs: Configuration parameters including:
                - threads_app_id: Threads (Meta) app ID
                - threads_app_secret: Threads (Meta) app secret
                - threads_redirect_uri: OAuth redirect URI
                - threads_refresh_token: Threads refresh token
                - threads_who_can_reply: Who can reply setting
                - threads_post_id: Post ID for share actions
        """
        super().__init__(**kwargs)
        self.threads_app_id = None
        self.threads_app_secret = None
        self.threads_redirect_uri = None
        self.threads_refresh_token = None
        self.threads_who_can_reply = None
        # Action-specific attributes
        self.threads_post_id = None
        self.api = None

    async def _initialize_client(self):
        """
        Initialize Threads API client.

        This method sets up the Threads API client with configuration.
        """
        # Get configuration values
        self.threads_app_id = self._get_config_value('threads_app_id', 'THREADS_APP_ID')
        self.threads_app_secret = self._get_config_value('threads_app_secret', 'THREADS_APP_SECRET')
        self.threads_redirect_uri = self._get_config_value('threads_redirect_uri', 'THREADS_REDIRECT_URI')
        self.threads_refresh_token = self._get_config_value('threads_refresh_token', 'THREADS_REFRESH_TOKEN')

        # Configuration options
        self.threads_who_can_reply = (
            self._get_config_value('threads_who_can_reply', 'THREADS_WHO_CAN_REPLY') or 'everyone'
        )

        # Action-specific attributes
        self.threads_post_id = self._get_config_value('threads_post_id', 'THREADS_POST_ID')

        # Validate required credentials
        if not self.threads_app_id:
            raise Exception('Threads app ID is required.')

        if not self.threads_app_secret:
            raise Exception('Threads app secret is required.')

        if not self.threads_redirect_uri:
            raise Exception('Threads redirect URI is required.')

        # Initialize Threads API (it will handle loading refresh token from cache if needed)
        self.api = ThreadsAPI(
            self.threads_app_id,
            self.threads_app_secret,
            self.threads_redirect_uri,
            self.threads_refresh_token
        )
        await self.api.authenticate()

    async def disconnect(self):
        """
        Disconnect from Threads API and clean up resources.
        """
        if self.api:
            await self.api.disconnect()

    async def post(self, status_text, status_link,
                   status_image_url_1=None, status_image_url_2=None,
                   status_image_url_3=None, status_image_url_4=None):
        """
        Create a post on Threads.

        Args:
            status_text (str): Text content of the post
            status_link (str): URL to include in the post
            status_image_url_1 (str, optional): First image URL
            status_image_url_2 (str, optional): Second image URL
            status_image_url_3 (str, optional): Third image URL
            status_image_url_4 (str, optional): Fourth image URL

        Returns:
            str: Post ID
        """
        if not self.api:
            raise Exception('Threads API not initialized')

        # Combine text and link
        post_text = f'{status_text} {status_link}'.strip()

        # Collect media files
        files = list(filter(None, [
            status_image_url_1, status_image_url_2,
            status_image_url_3, status_image_url_4
        ]))

        # Call ThreadsAPI.create_post() which handles Media system validation
        post_id = await self.api.create_post(
            post_text,
            files if files else None,
            who_can_reply=self.threads_who_can_reply
        )

        self._output_status(post_id)
        return post_id

    async def like(self, post_id):
        """
        Like a Threads post (not supported via API).

        Args:
            post_id (str): Post ID to like

        Raises:
            Exception: Like not supported for Threads
        """
        raise Exception('Like not supported for Threads')

    async def delete(self, post_id):
        """
        Delete a Threads post (not supported via API).

        Args:
            post_id (str): Post ID to delete

        Raises:
            Exception: Delete not supported for Threads
        """
        raise Exception('Delete not supported for Threads')

    async def share(self, post_id):
        """
        Share/repost a Threads post.

        Args:
            post_id (str): Post ID to share/repost

        Returns:
            str: Repost ID
        """
        if not self.api:
            raise Exception('Threads API not initialized')

        # Get post_id from parameter or instance attribute
        if not post_id:
            post_id = self.threads_post_id

        if not post_id:
            raise Exception('Post ID is required for share action.')

        repost_id = await self.api.repost_post(post_id)
        self._output_status(repost_id)
        return repost_id

    # Override action handlers to use Threads-specific parameter names
    async def _handle_post_action(self):
        """Handle post action with Threads-specific parameter extraction."""
        status_text = self._get_config_value('status_text', 'STATUS_TEXT') or ''
        status_link = self._get_config_value('status_link', 'STATUS_LINK') or ''
        status_image_url_1 = self._get_config_value('status_image_url_1', 'STATUS_IMAGE_URL_1')
        status_image_url_2 = self._get_config_value('status_image_url_2', 'STATUS_IMAGE_URL_2')
        status_image_url_3 = self._get_config_value('status_image_url_3', 'STATUS_IMAGE_URL_3')
        status_image_url_4 = self._get_config_value('status_image_url_4', 'STATUS_IMAGE_URL_4')

        await self.post(status_text, status_link,
                        status_image_url_1, status_image_url_2,
                        status_image_url_3, status_image_url_4)

    async def _handle_share_action(self):
        """Handle share action with Threads-specific parameter extraction."""
        threads_post_id = self._get_config_value('threads_post_id', 'THREADS_POST_ID')
        if not threads_post_id:
            raise Exception('Threads post ID is required for share action.')
        await self.share(threads_post_id)

    async def _handle_like_action(self):
        """Handle like action - not supported for Threads."""
        await self.like(None)

    async def _handle_delete_action(self):
        """Handle delete action - not supported for Threads."""
        await self.delete(None)

    async def execute_action(self, action):
        """
        Execute the specified action asynchronously.

        Args:
            action (str): Action to execute

        Raises:
            Exception: If action is not supported or required arguments missing
        """
        if action == '':
            raise Exception('Action is a required argument.')

        # Initialize client before executing other actions
        await self._initialize_client()

        if action == 'post':
            await self._handle_post_action()
        elif action == 'like':
            await self._handle_like_action()
        elif action == 'share':
            await self._handle_share_action()
        elif action == 'delete':
            await self._handle_delete_action()
        elif action == 'video':
            await self._handle_video_action()
        elif action == 'last-from-feed':
            await self._handle_last_from_feed_action()
        elif action == 'random-from-feed':
            await self._handle_random_from_feed_action()
        elif action == 'schedule':
            await self._handle_schedule_action()
        else:
            raise Exception(f'"{action}" action not supported.')


async def main_async(kwargs):
    """
    Async main function to execute Threads actions.

    Args:
        kwargs (dict): Configuration arguments
    """
    action = kwargs.get('action', '')

    if action == '':
        raise Exception('Action is a required argument.')

    # Create Threads instance with configuration
    instance = Threads(**kwargs)
    # Execute the action using the base class method
    await instance.execute_action(action)
    await instance.disconnect()


def main(kwargs):
    """
    Main function to execute Threads actions.

    Args:
        kwargs (dict): Configuration arguments
    """
    asyncio.run(main_async(kwargs))
