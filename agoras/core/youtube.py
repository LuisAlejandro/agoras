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

from agoras.core.api import YouTubeAPI
from agoras.core.base import SocialNetwork


class YouTube(SocialNetwork):
    """
    YouTube social network implementation.

    This class provides YouTube-specific functionality for uploading videos,
    and managing YouTube interactions asynchronously.
    """

    def __init__(self, **kwargs):
        """
        Initialize YouTube instance.

        Args:
            **kwargs: Configuration parameters including:
                - youtube_client_id: YouTube client ID
                - youtube_client_secret: YouTube client secret
                - youtube_video_id: YouTube video ID for operations
                - youtube_title: Video title
                - youtube_description: Video description
                - youtube_category_id: YouTube category ID
                - youtube_privacy_status: Privacy status (public, private, unlisted)
                - youtube_keywords: Comma-separated keywords
                - youtube_video_url: Video URL to upload
        """
        super().__init__(**kwargs)
        self.youtube_client_id = None
        self.youtube_client_secret = None
        self.youtube_video_id = None
        self.youtube_title = None
        self.youtube_description = None
        self.youtube_category_id = None
        self.youtube_privacy_status = None
        self.youtube_keywords = None
        self.youtube_video_url = None
        self.api = None

    async def _initialize_client(self):
        """
        Initialize YouTube API client.

        This method sets up the YouTube API client with OAuth configuration.
        """
        self.youtube_client_id = self._get_config_value('youtube_client_id', 'YOUTUBE_CLIENT_ID')
        self.youtube_client_secret = self._get_config_value('youtube_client_secret', 'YOUTUBE_CLIENT_SECRET')
        self.youtube_video_id = self._get_config_value('youtube_video_id', 'YOUTUBE_VIDEO_ID')
        self.youtube_title = self._get_config_value('youtube_title', 'YOUTUBE_TITLE')
        self.youtube_description = self._get_config_value('youtube_description', 'YOUTUBE_DESCRIPTION')
        self.youtube_category_id = self._get_config_value('youtube_category_id', 'YOUTUBE_CATEGORY_ID')
        self.youtube_privacy_status = (self._get_config_value('youtube_privacy_status', 'YOUTUBE_PRIVACY_STATUS')
                                       or 'private')
        self.youtube_keywords = self._get_config_value('youtube_keywords', 'YOUTUBE_KEYWORDS')
        self.youtube_video_url = self._get_config_value('youtube_video_url', 'YOUTUBE_VIDEO_URL')

        if not self.youtube_client_id or not self.youtube_client_secret:
            raise Exception('YouTube client ID and secret are required.')

        # Initialize YouTube API
        self.api = YouTubeAPI(
            self.youtube_client_id,
            self.youtube_client_secret
        )
        await self.api.authenticate()

    async def disconnect(self):
        """
        Disconnect from YouTube API and clean up resources.
        """
        if self.api:
            await self.api.disconnect()

    async def post(self, status_text, status_link,
                   status_image_url_1=None, status_image_url_2=None,
                   status_image_url_3=None, status_image_url_4=None):
        """
        Post is not supported for YouTube (videos only).

        Args:
            status_text (str): Text content
            status_link (str): URL to include
            status_image_url_1 (str, optional): First image URL
            status_image_url_2 (str, optional): Second image URL
            status_image_url_3 (str, optional): Third image URL
            status_image_url_4 (str, optional): Fourth image URL

        Raises:
            Exception: Post not supported for YouTube
        """
        raise Exception('Regular posts not supported for YouTube. Use video action instead.')

    async def like(self, youtube_video_id=None):
        """
        Like a YouTube video.

        Args:
            youtube_video_id (str, optional): ID of the YouTube video to like.
                                               Uses instance youtube_video_id if not provided.

        Returns:
            str: Video ID
        """
        if not self.api:
            raise Exception('YouTube API not initialized')

        video_id = youtube_video_id or self.youtube_video_id
        if not video_id:
            raise Exception('YouTube video ID is required.')

        await self.api.like(video_id)
        self._output_status(video_id)
        return video_id

    async def delete(self, youtube_video_id=None):
        """
        Delete a YouTube video.

        Args:
            youtube_video_id (str, optional): ID of the YouTube video to delete.
                                               Uses instance youtube_video_id if not provided.

        Returns:
            str: Video ID
        """
        if not self.api:
            raise Exception('YouTube API not initialized')

        video_id = youtube_video_id or self.youtube_video_id
        if not video_id:
            raise Exception('YouTube video ID is required.')

        await self.api.delete(video_id)
        self._output_status(video_id)
        return video_id

    async def share(self, youtube_video_id=None):
        """
        Share is not supported for YouTube.

        Args:
            youtube_video_id (str, optional): ID of the YouTube video

        Raises:
            Exception: Share not supported for YouTube
        """
        raise Exception('Share not supported for YouTube')

    async def video(self, status_text, video_url, video_title):
        """
        Upload a video to YouTube.

        Args:
            status_text (str): Video description
            video_url (str): URL of the video to upload
            video_title (str): Title of the video

        Returns:
            str: Video ID
        """
        if not self.api:
            raise Exception('YouTube API not initialized')

        if not video_title or not video_url:
            raise Exception('Video title and URL are required.')

        # Download and validate video using the Media system
        video = await self.download_video(video_url)

        if not video.content or not video.file_type:
            video.cleanup()
            raise Exception('Failed to download or validate video')

        # Ensure video is in allowed format for YouTube
        allowed_types = ['video/quicktime', 'video/mp4', 'video/webm']
        if video.file_type.mime not in allowed_types:
            video.cleanup()
            raise Exception(f'Invalid video type "{video.file_type.mime}" for {video_url}. '
                            f'YouTube supports: {allowed_types}')

        # Ensure temp file exists
        if not video.temp_file:
            video.cleanup()
            raise Exception('No temporary file created for video')

        try:
            # Upload video using YouTube API
            response = await self.api.upload_video(
                video_file_path=video.temp_file,
                title=video_title,
                description=status_text,
                category_id=self.youtube_category_id or '',
                privacy_status=self.youtube_privacy_status or 'private',
                keywords=self.youtube_keywords
            )

            video_id = response.get('id')
            if not video_id:
                raise Exception('Failed to get video ID from upload response')

        finally:
            # Clean up using Media system
            video.cleanup()

        self._output_status(video_id)
        return video_id

    # YouTube-specific feed methods that work with videos instead of posts
    async def last_from_feed(self, feed_url, max_count, post_lookback):
        """
        Upload recent videos from RSS feed asynchronously.

        Args:
            feed_url (str): URL of the RSS feed
            max_count (int): Maximum number of videos to upload
            post_lookback (int): Lookback period in seconds
        """
        feed = await self.download_feed(feed_url)
        recent_items = feed.get_items_since(post_lookback)

        count = 0
        for item in recent_items:
            if count >= max_count:
                break

            video_title = item.title
            # Get video URL from enclosures
            video_url = ''
            try:
                if item.raw_item.enclosures and len(item.raw_item.enclosures) > 0:
                    video_url = item.raw_item.enclosures[0].url
            except (AttributeError, IndexError):
                pass

            if video_url:
                count += 1
                await self.video(self.youtube_description or '', video_url, video_title)

    async def random_from_feed(self, feed_url, max_post_age):
        """
        Upload a random video from RSS feed asynchronously.

        Args:
            feed_url (str): URL of the RSS feed
            max_post_age (int): Maximum age of posts in days
        """
        feed = await self.download_feed(feed_url)
        random_item = feed.get_random_item(max_post_age)

        video_title = random_item.title
        # Get video URL from enclosures
        video_url = ''
        try:
            if random_item.raw_item.enclosures and len(random_item.raw_item.enclosures) > 0:
                video_url = random_item.raw_item.enclosures[0].url
        except (AttributeError, IndexError):
            pass

        if video_url:
            await self.video(self.youtube_description or '', video_url, video_title)

    async def schedule(self, google_sheets_id, google_sheets_name,
                       google_sheets_client_email, google_sheets_private_key, max_count):
        """
        Schedule video uploads from Google Sheets asynchronously.

        Expected sheet columns: youtube_title, youtube_description, youtube_category_id,
        youtube_privacy_status, youtube_video_url, youtube_keywords, date, hour, state

        Args:
            google_sheets_id (str): Google Sheets document ID
            google_sheets_name (str): Worksheet name
            google_sheets_client_email (str): Service account email
            google_sheets_private_key (str): Service account private key
            max_count (int): Maximum number of videos to process
        """
        # Create and configure the schedule sheet
        sheet = await self.create_schedule_sheet(
            google_sheets_id, google_sheets_name,
            google_sheets_client_email, google_sheets_private_key
        )

        # Process scheduled videos
        videos_to_upload = await sheet.process_scheduled_posts(max_count)

        # Upload videos asynchronously
        for video_data in videos_to_upload:
            # YouTube-specific columns
            title = video_data.get('youtube_title', '')
            description = video_data.get('youtube_description', '')
            video_url = video_data.get('youtube_video_url', '')

            if title and video_url:
                # Temporarily update instance variables for this upload
                original_category = self.youtube_category_id
                original_privacy = self.youtube_privacy_status
                original_keywords = self.youtube_keywords

                self.youtube_category_id = video_data.get('youtube_category_id', '')
                self.youtube_privacy_status = video_data.get('youtube_privacy_status', 'private')
                self.youtube_keywords = video_data.get('youtube_keywords', '')

                try:
                    await self.video(description, video_url, title)
                finally:
                    # Restore original values
                    self.youtube_category_id = original_category
                    self.youtube_privacy_status = original_privacy
                    self.youtube_keywords = original_keywords

    # Override action handlers to use YouTube-specific parameter names
    async def _handle_like_action(self):
        """Handle like action with YouTube-specific parameter extraction."""
        youtube_video_id = self._get_config_value('youtube_video_id', 'YOUTUBE_VIDEO_ID')
        if not youtube_video_id:
            raise Exception('YouTube video ID is required for like action.')
        await self.like(youtube_video_id)

    async def _handle_share_action(self):
        """Handle share action with YouTube-specific parameter extraction."""
        await self.share()

    async def _handle_delete_action(self):
        """Handle delete action with YouTube-specific parameter extraction."""
        youtube_video_id = self._get_config_value('youtube_video_id', 'YOUTUBE_VIDEO_ID')
        if not youtube_video_id:
            raise Exception('YouTube video ID is required for delete action.')
        await self.delete(youtube_video_id)

    async def _handle_video_action(self):
        """Handle video action with YouTube-specific parameter extraction."""
        status_text = self._get_config_value('youtube_description', 'YOUTUBE_DESCRIPTION') or ''
        video_url = self._get_config_value('youtube_video_url', 'YOUTUBE_VIDEO_URL')
        video_title = self._get_config_value('youtube_title', 'YOUTUBE_TITLE') or ''

        if not video_url:
            raise Exception('YouTube video URL is required for video action.')
        if not video_title:
            raise Exception('YouTube video title is required for video action.')

        await self.video(status_text, video_url, video_title)


async def main_async(kwargs):
    """
    Async main function to execute YouTube actions.

    Args:
        kwargs (dict): Configuration parameters
    """
    action = kwargs.get('action', '')

    if action == '':
        raise Exception('Action is a required argument.')

    # Create YouTube instance with configuration
    instance = YouTube(**kwargs)
    # Execute the action using the base class method
    await instance.execute_action(action)
    await instance.disconnect()


def main(kwargs):
    """
    Main function to execute YouTube actions.

    Args:
        kwargs (dict): Configuration arguments
    """
    asyncio.run(main_async(kwargs))
