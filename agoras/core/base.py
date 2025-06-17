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

import datetime
import json
import os
from abc import ABC, abstractmethod

from agoras.core.media import MediaFactory
from agoras.core.feed import Feed
from agoras.core.sheet import ScheduleSheet


class SocialNetwork(ABC):
    """
    Abstract base class for social network implementations.

    This class provides common functionality and defines the interface
    that all social network implementations must follow. All methods
    are asynchronous by default.
    """

    def __init__(self, **kwargs):
        """
        Initialize the social network instance with configuration.

        Args:
            **kwargs: Configuration parameters specific to each social network
        """
        self.config = kwargs
        self.client = None

    @abstractmethod
    async def _initialize_client(self):
        """
        Initialize the API client for the specific social network.

        This method must be implemented by each social network to set up
        their specific API clients and authentication.
        """
        pass

    @abstractmethod
    async def post(self, status_text, status_link,
                   status_image_url_1=None, status_image_url_2=None,
                   status_image_url_3=None, status_image_url_4=None):
        """
        Create a post on the social network.

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
        pass

    @abstractmethod
    async def like(self, post_id):
        """
        Like/react to a post.

        Args:
            post_id (str): ID of the post to like

        Returns:
            str: Post ID
        """
        pass

    @abstractmethod
    async def delete(self, post_id):
        """
        Delete a post.

        Args:
            post_id (str): ID of the post to delete

        Returns:
            str: Post ID
        """
        pass

    @abstractmethod
    async def share(self, post_id):
        """
        Share/retweet a post.

        Args:
            post_id (str): ID of the post to share

        Returns:
            str: Post ID
        """
        pass

    async def video(self, status_text, video_url, video_title):
        """
        Post a video. Default implementation raises not supported error.

        Args:
            status_text (str): Text content to accompany the video
            video_url (str): URL of the video to post
            video_title (str): Title of the video

        Returns:
            str: Post ID

        Raises:
            Exception: If video posting is not supported
        """
        raise Exception(f'Video posting not supported for {self.__class__.__name__}')

    async def authorize(self):
        """
        Perform authorization flow for platforms that require it.
        
        Default implementation does nothing. Override in subclasses that need
        special authorization flows (like YouTube OAuth).

        Returns:
            SocialNetwork: Self for method chaining
        """
        return self

    def get_platform_name(self):
        """
        Get the platform name for media handling.

        Returns:
            str: Platform name (class name without 'Network' suffix if present)
        """
        name = self.__class__.__name__
        if name.endswith('Network'):
            return name[:-7]  # Remove 'Network' suffix
        return name

    async def download_images(self, image_urls):
        """
        Download multiple images using the Media system.

        Args:
            image_urls (list): List of image URLs

        Returns:
            list: List of downloaded Image instances
        """
        return await MediaFactory.download_images(image_urls)

    async def download_video(self, video_url):
        """
        Download video using the Media system with platform-specific limits.

        Args:
            video_url (str): Video URL

        Returns:
            Video: Downloaded Video instance
        """
        platform = self.get_platform_name()
        video = MediaFactory.create_video(video_url, platform)
        await video.download()
        return video

    async def download_feed(self, feed_url):
        """
        Download and parse RSS feed using the Feed system.

        Args:
            feed_url (str): RSS feed URL

        Returns:
            Feed: Downloaded Feed instance
        """
        feed = Feed(feed_url)
        await feed.download()
        return feed

    async def create_schedule_sheet(self, google_sheets_id, google_sheets_name,
                                    google_sheets_client_email, google_sheets_private_key):
        """
        Create a ScheduleSheet instance with proper configuration.

        Args:
            google_sheets_id (str): Google Sheets document ID
            google_sheets_name (str): Worksheet name
            google_sheets_client_email (str): Service account email
            google_sheets_private_key (str): Service account private key

        Returns:
            ScheduleSheet: Configured schedule sheet instance
        """
        # Clean up private key format
        if google_sheets_private_key:
            google_sheets_private_key = google_sheets_private_key.replace('\\n', '\n')

        sheet = ScheduleSheet(
            google_sheets_id,
            google_sheets_client_email,
            google_sheets_private_key,
            google_sheets_name
        )

        await sheet.authenticate()
        await sheet.get_worksheet()

        return sheet

    async def last_from_feed(self, feed_url, max_count, post_lookback):
        """
        Post recent items from RSS feed asynchronously.

        Args:
            feed_url (str): URL of the RSS feed
            max_count (int): Maximum number of posts to create
            post_lookback (int): Lookback period in seconds
        """
        feed = await self.download_feed(feed_url)
        recent_items = feed.get_items_since(post_lookback)

        count = 0
        today = datetime.datetime.now()

        for item in recent_items:
            if count >= max_count:
                break

            status_link = item.get_timestamped_link(today.strftime('%Y%m%d%H%M%S')) if item.link else ''
            status_title = item.title
            status_image = item.image_url

            count += 1
            await self.post(status_title, status_link, status_image)

    async def random_from_feed(self, feed_url, max_post_age):
        """
        Post a random item from RSS feed asynchronously.

        Args:
            feed_url (str): URL of the RSS feed
            max_post_age (int): Maximum age of posts in days
        """
        feed = await self.download_feed(feed_url)
        random_item = feed.get_random_item(max_post_age)

        today = datetime.datetime.now()
        status_link = random_item.get_timestamped_link(today.strftime('%Y%m%d%H%M%S')) if random_item.link else ''
        status_title = random_item.title
        status_image = random_item.image_url

        await self.post(status_title, status_link, status_image)

    async def schedule(self, google_sheets_id, google_sheets_name,
                       google_sheets_client_email, google_sheets_private_key, max_count):
        """
        Schedule posts from Google Sheets asynchronously.

        Args:
            google_sheets_id (str): Google Sheets document ID
            google_sheets_name (str): Worksheet name
            google_sheets_client_email (str): Service account email
            google_sheets_private_key (str): Service account private key
            max_count (int): Maximum number of posts to process
        """
        # Create and configure the schedule sheet
        sheet = await self.create_schedule_sheet(
            google_sheets_id, google_sheets_name,
            google_sheets_client_email, google_sheets_private_key
        )

        # Process scheduled posts
        posts_to_create = await sheet.process_scheduled_posts(max_count)

        # Create posts asynchronously
        for post_data in posts_to_create:
            await self.post(
                post_data['status_text'],
                post_data['status_link'],
                post_data['status_image_url_1'],
                post_data['status_image_url_2'],
                post_data['status_image_url_3'],
                post_data['status_image_url_4']
            )

    def _output_status(self, post_id):
        """
        Output status response in JSON format.

        Args:
            post_id (str): ID of the created/modified post
        """
        status = {"id": post_id}
        print(json.dumps(status, separators=(',', ':')))

    def _get_config_value(self, key, env_key=None):
        """
        Get configuration value from kwargs or environment.

        Args:
            key (str): Configuration key
            env_key (str, optional): Environment variable key

        Returns:
            Configuration value or None
        """
        env_key = env_key or key.upper()
        return self.config.get(key) or os.environ.get(env_key)

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

        # Handle authorize action before client initialization
        if action == 'authorize':
            await self.authorize()
            return

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

    async def _handle_post_action(self):
        """Handle post action with common parameter extraction."""
        status_text = self._get_config_value('status_text', 'STATUS_TEXT') or ''
        status_link = self._get_config_value('status_link', 'STATUS_LINK') or ''
        status_image_url_1 = self._get_config_value('status_image_url_1', 'STATUS_IMAGE_URL_1')
        status_image_url_2 = self._get_config_value('status_image_url_2', 'STATUS_IMAGE_URL_2')
        status_image_url_3 = self._get_config_value('status_image_url_3', 'STATUS_IMAGE_URL_3')
        status_image_url_4 = self._get_config_value('status_image_url_4', 'STATUS_IMAGE_URL_4')

        await self.post(status_text, status_link,
                        status_image_url_1, status_image_url_2,
                        status_image_url_3, status_image_url_4)

    async def _handle_like_action(self):
        """Handle like action with common parameter extraction."""
        post_id = self._get_config_value('post_id')
        if not post_id:
            raise Exception('Post ID is required for like action.')
        await self.like(post_id)

    async def _handle_share_action(self):
        """Handle share action with common parameter extraction."""
        post_id = self._get_config_value('post_id')
        if not post_id:
            raise Exception('Post ID is required for share action.')
        await self.share(post_id)

    async def _handle_delete_action(self):
        """Handle delete action with common parameter extraction."""
        post_id = self._get_config_value('post_id')
        if not post_id:
            raise Exception('Post ID is required for delete action.')
        await self.delete(post_id)

    async def _handle_video_action(self):
        """Handle video action with common parameter extraction."""
        status_text = self._get_config_value('status_text', 'STATUS_TEXT') or ''
        video_url = self._get_config_value('video_url')
        video_title = self._get_config_value('video_title') or ''

        if not video_url:
            raise Exception('Video URL is required for video action.')

        await self.video(status_text, video_url, video_title)

    async def _handle_last_from_feed_action(self):
        """Handle last-from-feed action with common parameter extraction."""
        feed_url = self._get_config_value('feed_url', 'FEED_URL')
        max_count = int(self._get_config_value('max_count', 'MAX_COUNT') or 1)
        post_lookback = int(self._get_config_value('post_lookback', 'POST_LOOKBACK') or 3600)

        await self.last_from_feed(feed_url, max_count, post_lookback)

    async def _handle_random_from_feed_action(self):
        """Handle random-from-feed action with common parameter extraction."""
        feed_url = self._get_config_value('feed_url', 'FEED_URL')
        max_post_age = int(self._get_config_value('max_post_age', 'MAX_POST_AGE') or 365)

        await self.random_from_feed(feed_url, max_post_age)

    async def _handle_schedule_action(self):
        """Handle schedule action with common parameter extraction."""
        google_sheets_id = self._get_config_value('google_sheets_id', 'GOOGLE_SHEETS_ID')
        google_sheets_name = self._get_config_value('google_sheets_name', 'GOOGLE_SHEETS_NAME')
        google_sheets_client_email = self._get_config_value('google_sheets_client_email', 'GOOGLE_SHEETS_CLIENT_EMAIL')
        google_sheets_private_key = self._get_config_value('google_sheets_private_key', 'GOOGLE_SHEETS_PRIVATE_KEY')
        max_count = int(self._get_config_value('max_count', 'MAX_COUNT') or 1)

        await self.schedule(google_sheets_id, google_sheets_name,
                            google_sheets_client_email, google_sheets_private_key, max_count)
