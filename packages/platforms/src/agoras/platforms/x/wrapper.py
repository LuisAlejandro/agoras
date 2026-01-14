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

from .api import XAPI
from agoras.core.interfaces import SocialNetwork


class X(SocialNetwork):
    """
    X social network implementation.

    This class provides X-specific functionality for posting tweets,
    images, videos, and managing X interactions asynchronously.
    """

    def __init__(self, **kwargs):
        """
        Initialize X instance.

        Args:
            **kwargs: Configuration parameters including:
                - twitter_consumer_key: X consumer key
                - twitter_consumer_secret: X consumer secret
                - twitter_oauth_token: X OAuth token
                - twitter_oauth_secret: X OAuth secret
                - tweet_id: Tweet ID for operations
        """
        super().__init__(**kwargs)
        self.twitter_consumer_key = None
        self.twitter_consumer_secret = None
        self.twitter_oauth_token = None
        self.twitter_oauth_secret = None
        self.tweet_id = None
        self.api = None

    async def _initialize_client(self):
        """
        Initialize X API client.

        Tries to load credentials from CLI params, environment variables, or storage.
        """
        # Try params/environment first
        self.twitter_consumer_key = self._get_config_value('twitter_consumer_key', 'TWITTER_CONSUMER_KEY')
        self.twitter_consumer_secret = self._get_config_value('twitter_consumer_secret', 'TWITTER_CONSUMER_SECRET')
        self.twitter_oauth_token = self._get_config_value('twitter_oauth_token', 'TWITTER_OAUTH_TOKEN')
        self.twitter_oauth_secret = self._get_config_value('twitter_oauth_secret', 'TWITTER_OAUTH_SECRET')
        self.tweet_id = self._get_config_value('tweet_id', 'TWEET_ID')

        # If any credentials missing, try loading from storage
        if not all([self.twitter_consumer_key, self.twitter_consumer_secret,
                   self.twitter_oauth_token, self.twitter_oauth_secret]):
            from .auth import XAuthManager
            auth_manager = XAuthManager(
                consumer_key=self.twitter_consumer_key or '',
                consumer_secret=self.twitter_consumer_secret or ''
            )

            if auth_manager._load_credentials_from_storage():
                # Fill in missing credentials from storage
                if not self.twitter_consumer_key:
                    self.twitter_consumer_key = auth_manager.consumer_key
                if not self.twitter_consumer_secret:
                    self.twitter_consumer_secret = auth_manager.consumer_secret
                if not self.twitter_oauth_token:
                    self.twitter_oauth_token = auth_manager.oauth_token
                if not self.twitter_oauth_secret:
                    self.twitter_oauth_secret = auth_manager.oauth_secret

        # Validate all credentials are now available
        if not self.twitter_consumer_key:
            raise Exception("Not authenticated. Please run 'agoras x authorize' first.")
        if not self.twitter_consumer_secret:
            raise Exception("Not authenticated. Please run 'agoras x authorize' first.")
        if not self.twitter_oauth_token:
            raise Exception("Not authenticated. Please run 'agoras x authorize' first.")
        if not self.twitter_oauth_secret:
            raise Exception("Not authenticated. Please run 'agoras x authorize' first.")

        # Initialize X API
        self.api = XAPI(
            self.twitter_consumer_key,
            self.twitter_consumer_secret,
            self.twitter_oauth_token,
            self.twitter_oauth_secret
        )
        await self.api.authenticate()

    async def authorize_credentials(self):
        """
        Authorize and store X credentials for future use.

        Returns:
            bool: True if authorization successful
        """
        from .auth import XAuthManager

        consumer_key = self._get_config_value('twitter_consumer_key', 'TWITTER_CONSUMER_KEY')
        consumer_secret = self._get_config_value('twitter_consumer_secret', 'TWITTER_CONSUMER_SECRET')
        oauth_token = self._get_config_value('twitter_oauth_token', 'TWITTER_OAUTH_TOKEN')
        oauth_secret = self._get_config_value('twitter_oauth_secret', 'TWITTER_OAUTH_SECRET')

        auth_manager = XAuthManager(
            consumer_key=consumer_key,
            consumer_secret=consumer_secret,
            oauth_token=oauth_token,
            oauth_secret=oauth_secret
        )

        result = await auth_manager.authorize()
        if result:
            print(result)
            return True
        return False

    async def disconnect(self):
        """
        Disconnect from X API and clean up resources.
        """
        if self.api:
            await self.api.disconnect()

    async def post(self, status_text, status_link,
                   status_image_url_1=None, status_image_url_2=None,
                   status_image_url_3=None, status_image_url_4=None):
        """
        Create a post (tweet) on X.

        Args:
            status_text (str): Text content of the tweet
            status_link (str): URL to include in the tweet
            status_image_url_1 (str, optional): First image URL
            status_image_url_2 (str, optional): Second image URL
            status_image_url_3 (str, optional): Third image URL
            status_image_url_4 (str, optional): Fourth image URL

        Returns:
            str: Tweet ID
        """
        if not self.api:
            raise Exception('X API not initialized')

        media_ids = []
        source_media = list(filter(None, [
            status_image_url_1, status_image_url_2,
            status_image_url_3, status_image_url_4
        ]))

        if not source_media and not status_text and not status_link:
            raise Exception('No status text, link, or images provided.')

        # Download and upload media using the Media system
        if source_media:
            # Handle both images and videos
            for media_url in source_media:
                try:
                    # Try to download as image first, then video
                    try:
                        image = await self.download_images([media_url])
                        if image and len(image) > 0:
                            media_obj = image[0]
                        else:
                            raise Exception('Failed to download as image')
                    except Exception:
                        # Try as video
                        video = await self.download_video(media_url)
                        media_obj = video

                    # Upload media to X
                    if media_obj.content and media_obj.file_type:
                        media_id = await self.api.upload_media(
                            media_obj.content,
                            media_obj.file_type.mime
                        )
                        if media_id:
                            media_ids.append(media_id)

                    # Clean up temporary files
                    media_obj.cleanup()

                except Exception as e:
                    print(f"Failed to upload media {media_url}: {str(e)}")

        # Compose tweet text
        tweet_text = f'{status_text} {status_link}'.strip()

        # Create the tweet
        tweet_id = await self.api.post(tweet_text, media_ids or [])

        self._output_status(tweet_id)
        return tweet_id

    async def like(self, tweet_id=None):
        """
        Like a tweet.

        Args:
            tweet_id (str, optional): ID of the tweet to like.
                                     Uses instance tweet_id if not provided.

        Returns:
            str: Tweet ID
        """
        if not self.api:
            raise Exception('X API not initialized')

        post_id = tweet_id or self.tweet_id
        if not post_id:
            raise Exception('Tweet ID is required.')

        result = await self.api.like(post_id)
        self._output_status(result)
        return result

    async def delete(self, tweet_id=None):
        """
        Delete a tweet.

        Args:
            tweet_id (str, optional): ID of the tweet to delete.
                                     Uses instance tweet_id if not provided.

        Returns:
            str: Tweet ID
        """
        if not self.api:
            raise Exception('X API not initialized')

        post_id = tweet_id or self.tweet_id
        if not post_id:
            raise Exception('Tweet ID is required.')

        result = await self.api.delete(post_id)
        self._output_status(result)
        return result

    async def share(self, tweet_id=None):
        """
        Share a tweet (retweet).

        Args:
            tweet_id (str, optional): ID of the tweet to retweet.
                                     Uses instance tweet_id if not provided.

        Returns:
            str: Tweet ID
        """
        if not self.api:
            raise Exception('X API not initialized')

        post_id = tweet_id or self.tweet_id
        if not post_id:
            raise Exception('Tweet ID is required.')

        result = await self.api.share(post_id)
        self._output_status(result)
        return result

    async def video(self, status_text, video_url, video_title):
        """
        Post a video to X.

        Args:
            status_text (str): Text content to accompany the video
            video_url (str): URL of the video to post
            video_title (str): Title of the video

        Returns:
            str: Tweet ID
        """
        if not self.api:
            raise Exception('X API not initialized')

        if not video_url:
            raise Exception('Video URL is required.')

        # Download and validate video using the Media system
        video = await self.download_video(video_url)

        if not video.content or not video.file_type:
            video.cleanup()
            raise Exception('Failed to download or validate video')

        # Ensure video is MP4 format for X
        if video.file_type.mime not in ['video/mp4']:
            video.cleanup()
            raise Exception(f'Invalid video type "{video.file_type.mime}" for {video_url}. '
                            f'X only supports MP4 videos.')

        try:
            # Upload video to X

            media_id = await self.api.upload_media(video.content, video.file_type.mime)

            # Compose tweet text with title and description
            tweet_text_parts = []
            if video_title:
                tweet_text_parts.append(video_title)
            if status_text:
                tweet_text_parts.append(status_text)

            final_text = ' - '.join(tweet_text_parts) if tweet_text_parts else ''

            # X has a 280 character limit (handled by API, but let's be safe)
            if len(final_text) > 280:
                final_text = final_text[:277] + '...'

            # Create the tweet with video
            tweet_id = await self.api.post(final_text, [media_id] if media_id else [])

        finally:
            # Clean up using Media system
            video.cleanup()

        self._output_status(tweet_id)
        return tweet_id

    # Override action handlers to use X-specific parameter names
    async def _handle_like_action(self):
        """Handle like action with X-specific parameter extraction."""
        tweet_id = self._get_config_value('tweet_id', 'TWEET_ID')
        if not tweet_id:
            raise Exception('Tweet ID is required for like action.')
        await self.like(tweet_id)

    async def _handle_share_action(self):
        """Handle share action with X-specific parameter extraction."""
        tweet_id = self._get_config_value('tweet_id', 'TWEET_ID')
        if not tweet_id:
            raise Exception('Tweet ID is required for share action.')
        await self.share(tweet_id)

    async def _handle_delete_action(self):
        """Handle delete action with X-specific parameter extraction."""
        tweet_id = self._get_config_value('tweet_id', 'TWEET_ID')
        if not tweet_id:
            raise Exception('Tweet ID is required for delete action.')
        await self.delete(tweet_id)

    async def _handle_video_action(self):
        """Handle video action with X-specific parameter extraction."""
        status_text = self._get_config_value('status_text', 'STATUS_TEXT') or ''
        video_url = self._get_config_value('twitter_video_url', 'TWITTER_VIDEO_URL')
        video_title = self._get_config_value('twitter_video_title', 'TWITTER_VIDEO_TITLE') or ''

        if not video_url:
            raise Exception('X video URL is required for video action.')

        await self.video(status_text, video_url, video_title)


async def main_async(kwargs):
    """
    Async main function to execute X actions.

    Args:
        kwargs (dict): Configuration arguments
    """
    action = kwargs.get('action', '')

    if action == '':
        raise Exception('Action is a required argument.')

    # Create X instance with configuration
    instance = X(**kwargs)
    # Execute the action using the base class method
    await instance.execute_action(action)
    await instance.disconnect()


def main(kwargs):
    """
    Main function to execute X actions (for backwards compatibility).

    Args:
        kwargs (dict): Configuration arguments
    """
    asyncio.run(main_async(kwargs))
