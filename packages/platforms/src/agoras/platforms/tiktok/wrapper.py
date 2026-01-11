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

from .api import TikTokAPI
from agoras.core.interfaces import SocialNetwork


class TikTok(SocialNetwork):
    """
    TikTok social network implementation.

    This class provides TikTok-specific functionality for posting videos and photos,
    and managing TikTok interactions asynchronously.
    """

    def __init__(self, **kwargs):
        """
        Initialize TikTok instance.

        Args:
            **kwargs: Configuration parameters including:
                - tiktok_username: TikTok username
                - tiktok_client_key: TikTok client key
                - tiktok_client_secret: TikTok client secret
                - tiktok_refresh_token: TikTok refresh token
                - tiktok_title: Title for posts
                - tiktok_privacy_status: Privacy status (SELF_ONLY, PUBLIC_TO_EVERYONE, etc.)
                - tiktok_allow_comments: Whether to allow comments
                - tiktok_allow_duet: Whether to allow duets
                - tiktok_allow_stitch: Whether to allow stitches
                - tiktok_auto_add_music: Whether to auto-add music for photos
                - brand_organic: Whether content is brand organic
                - brand_content: Whether content is brand content
        """
        super().__init__(**kwargs)
        self.tiktok_username = None
        self.tiktok_client_key = None
        self.tiktok_client_secret = None
        self.tiktok_refresh_token = None
        self.tiktok_title = None
        self.tiktok_privacy_status = None
        self.tiktok_allow_comments = None
        self.tiktok_allow_duet = None
        self.tiktok_allow_stitch = None
        self.tiktok_auto_add_music = None
        self.brand_organic = None
        self.brand_content = None
        self.api = None

    async def _initialize_client(self):
        """
        Initialize TikTok API client.

        This method sets up the TikTok API client with configuration.
        """
        # Get configuration values
        self.tiktok_username = self._get_config_value('tiktok_username', 'TIKTOK_USERNAME')
        self.tiktok_client_key = self._get_config_value('tiktok_client_key', 'TIKTOK_CLIENT_KEY')
        self.tiktok_client_secret = self._get_config_value('tiktok_client_secret', 'TIKTOK_CLIENT_SECRET')
        self.tiktok_refresh_token = self._get_config_value('tiktok_refresh_token', 'TIKTOK_REFRESH_TOKEN')

        # Configuration options
        self.tiktok_title = self._get_config_value('tiktok_title', 'TIKTOK_TITLE') or ''
        self.tiktok_privacy_status = (
            self._get_config_value('tiktok_privacy_status', 'TIKTOK_PRIVACY_STATUS') or 'SELF_ONLY'
        )
        self.tiktok_allow_comments = self._get_config_value('tiktok_allow_comments', 'TIKTOK_ALLOW_COMMENTS')
        self.tiktok_allow_duet = self._get_config_value('tiktok_allow_duet', 'TIKTOK_ALLOW_DUET')
        self.tiktok_allow_stitch = self._get_config_value('tiktok_allow_stitch', 'TIKTOK_ALLOW_STITCH')
        self.tiktok_auto_add_music = self._get_config_value('tiktok_auto_add_music', 'TIKTOK_AUTO_ADD_MUSIC')
        self.brand_organic = self._get_config_value('brand_organic', 'TIKTOK_BRAND_ORGANIC')
        self.brand_content = self._get_config_value('brand_content', 'TIKTOK_BRAND_CONTENT')

        # Convert string booleans
        self.tiktok_allow_comments = self._convert_bool(self.tiktok_allow_comments, True)
        self.tiktok_allow_duet = self._convert_bool(self.tiktok_allow_duet, True)
        self.tiktok_allow_stitch = self._convert_bool(self.tiktok_allow_stitch, True)
        self.tiktok_auto_add_music = self._convert_bool(self.tiktok_auto_add_music, False)
        self.brand_organic = self._convert_bool(self.brand_organic, False)
        self.brand_content = self._convert_bool(self.brand_content, False)

        if not self.tiktok_username:
            raise Exception('TikTok username is required.')

        if not self.tiktok_client_key:
            raise Exception('TikTok client key is required.')

        if not self.tiktok_client_secret:
            raise Exception('TikTok client secret is required.')

        # Initialize TikTok API (it will handle loading refresh token from cache if needed)
        self.api = TikTokAPI(
            self.tiktok_username,
            self.tiktok_client_key,
            self.tiktok_client_secret,
            self.tiktok_refresh_token
        )
        await self.api.authenticate()

    async def disconnect(self):
        """
        Disconnect from TikTok API and clean up resources.
        """
        if self.api:
            await self.api.disconnect()

    def _convert_bool(self, value, default=False):
        """Convert various boolean representations to bool."""
        if value is None:
            return default
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            return value.upper() in ['TRUE', '1', 'YES', 'ON']
        return bool(value)

    async def post(self, status_text, status_link,
                   status_image_url_1=None, status_image_url_2=None,
                   status_image_url_3=None, status_image_url_4=None):
        """
        Create a photo post on TikTok.

        Args:
            status_text (str): Text content of the post (title)
            status_link (str): Not used for TikTok
            status_image_url_1 (str, optional): First image URL
            status_image_url_2 (str, optional): Second image URL
            status_image_url_3 (str, optional): Third image URL
            status_image_url_4 (str, optional): Fourth image URL

        Returns:
            str: Post ID

        Raises:
            Exception: If post creation fails or duet/stitch not supported for photos
        """
        if not self.api:
            raise Exception('TikTok API not initialized')

        # Validate settings for photo posts
        if self.tiktok_allow_duet:
            raise Exception('--allow-duet is not supported for photo posts.')

        if self.tiktok_allow_stitch:
            raise Exception('--allow-stitch is not supported for photo posts.')

        # Collect source media
        source_media = list(filter(None, [
            status_image_url_1, status_image_url_2,
            status_image_url_3, status_image_url_4
        ]))

        if not source_media:
            raise Exception('At least one image is required for TikTok photo posts.')

        if not status_text:
            status_text = self.tiktok_title or ''

        # Validate images using Media system
        validated_media = []
        images = await self.download_images(source_media)

        try:
            for image in images:
                if not image.content or not image.file_type:
                    image.cleanup()
                    raise Exception(f'Failed to download or validate image: {image.url}')

                # Ensure image is valid format for TikTok
                if image.file_type.mime not in ['image/jpeg', 'image/png', 'image/jpg']:
                    image.cleanup()
                    raise Exception(f'Invalid image type "{image.file_type.mime}" for {image.url}')

                validated_media.append(image.url)

            # Validate brand content settings
            if self.brand_content and self.tiktok_privacy_status == 'ONLY_ME':
                raise Exception('You cannot use brand content with ONLY_ME privacy status')

            # Print brand content notices
            self._print_brand_content_notices()

            # Create the post
            response = await self.api.upload_photo(
                validated_media,
                status_text,
                str(self.tiktok_privacy_status),
                bool(self.tiktok_allow_comments),
                bool(self.brand_organic),
                bool(self.brand_content),
                bool(self.tiktok_auto_add_music)
            )

            post_id = response.get('publish_id')
            self._output_status(post_id)
            return post_id

        finally:
            # Clean up all downloaded images
            for image in images:
                image.cleanup()

    async def video(self, status_text, video_url, video_title):
        """
        Post a video to TikTok.

        Args:
            status_text (str): Text content to accompany the video (used as title if video_title not provided)
            video_url (str): URL of the video to post
            video_title (str): Title of the video (optional, status_text used if not provided)

        Returns:
            str: Post ID
        """
        if not self.api:
            raise Exception('TikTok API not initialized')

        if not video_url:
            raise Exception('Video URL is required.')

        title = video_title or status_text or self.tiktok_title or ''
        if not title:
            raise Exception('Video title is required.')

        # Validate settings for video posts
        if self.tiktok_auto_add_music:
            raise Exception('Auto-add music is not supported for video posts.')

        # Download and validate video using Media system
        video = await self.download_video(video_url)

        try:
            if not video.content or not video.file_type:
                raise Exception('Failed to download or validate video')

            # Ensure video is valid format for TikTok
            if video.file_type.mime not in ['video/quicktime', 'video/mp4', 'video/webm']:
                raise Exception(f'Invalid video type "{video.file_type.mime}" for {video_url}')

            # Check video duration against creator limits
            if hasattr(self.api, 'creator_info') and self.api.creator_info:
                max_duration = self.api.creator_info.get('max_video_post_duration_sec', 0)
                video_duration = video.get_duration()
                if video_duration and video_duration > max_duration:
                    raise Exception(f'Video duration {video_duration}s exceeds max duration of {max_duration}s')

            # Validate brand content settings
            if self.brand_content and self.tiktok_privacy_status == 'ONLY_ME':
                raise Exception('You cannot use brand content with ONLY_ME privacy status')

            # Print brand content notices
            self._print_brand_content_notices()

            print(f'Uploading video to @{self.tiktok_username}...')

            # Upload the video
            response = await self.api.upload_video(
                video_url,
                title,
                str(self.tiktok_privacy_status),
                bool(self.tiktok_allow_comments),
                bool(self.tiktok_allow_duet),
                bool(self.tiktok_allow_stitch),
                bool(self.brand_organic),
                bool(self.brand_content)
            )

            post_id = response.get('publish_id')
            self._output_status(post_id)
            return post_id

        finally:
            # Clean up downloaded video
            video.cleanup()

    async def like(self, post_id):
        """
        Like a TikTok post.

        TikTok API doesn't support liking posts through the API.

        Args:
            post_id (str): ID of the post to like

        Raises:
            Exception: Always, as like is not supported
        """
        raise Exception('Like not supported for TikTok')

    async def delete(self, post_id):
        """
        Delete a TikTok post.

        TikTok API doesn't support deleting posts through the API.

        Args:
            post_id (str): ID of the post to delete

        Raises:
            Exception: Always, as delete is not supported
        """
        raise Exception('Delete not supported for TikTok')

    async def share(self, post_id):
        """
        Share a TikTok post.

        TikTok API doesn't support sharing posts through the API.

        Args:
            post_id (str): ID of the post to share

        Raises:
            Exception: Always, as share is not supported
        """
        raise Exception('Share not supported for TikTok')

    def _print_brand_content_notices(self):
        """Print brand content compliance notices."""
        if self.brand_organic and self.brand_content:
            print("Your photo/video will be labeled as 'Paid partnership'")
            print("By posting, you agree to TikTok's Branded Content Policy "
                  "(https://www.tiktok.com/legal/page/global/bc-policy/en) "
                  "and Music Usage Confirmation "
                  "(https://www.tiktok.com/legal/page/global/music-usage-confirmation/en).")
        elif self.brand_organic:
            print("Your photo/video will be labeled as 'Promotional content'")
            print("By posting, you agree to TikTok's Music Usage Confirmation "
                  "(https://www.tiktok.com/legal/page/global/music-usage-confirmation/en).")
        elif self.brand_content:
            print("Your photo/video will be labeled as 'Paid partnership'")
            print("By posting, you agree to TikTok's Branded Content Policy "
                  "(https://www.tiktok.com/legal/page/global/bc-policy/en) "
                  "and Music Usage Confirmation "
                  "(https://www.tiktok.com/legal/page/global/music-usage-confirmation/en).")

    # Override action handlers to use TikTok-specific parameter names
    async def _handle_post_action(self):
        """Handle post action with TikTok-specific parameter extraction."""
        status_image_url_1 = self._get_config_value('status_image_url_1', 'STATUS_IMAGE_URL_1')
        status_image_url_2 = self._get_config_value('status_image_url_2', 'STATUS_IMAGE_URL_2')
        status_image_url_3 = self._get_config_value('status_image_url_3', 'STATUS_IMAGE_URL_3')
        status_image_url_4 = self._get_config_value('status_image_url_4', 'STATUS_IMAGE_URL_4')

        await self.post('', '', status_image_url_1, status_image_url_2,
                        status_image_url_3, status_image_url_4)

    async def _handle_video_action(self):
        """Handle video action with TikTok-specific parameter extraction."""
        video_url = self._get_config_value('tiktok_video_url', 'TIKTOK_VIDEO_URL')
        video_title = self.tiktok_title or ''

        if not video_url:
            raise Exception('TikTok video URL is required for video action.')

        await self.video(video_title, video_url, video_title)

    async def _handle_like_action(self):
        """Handle like action - not supported for TikTok."""
        await self.like(None)

    async def _handle_share_action(self):
        """Handle share action - not supported for TikTok."""
        await self.share(None)

    async def _handle_delete_action(self):
        """Handle delete action - not supported for TikTok."""
        await self.delete(None)


async def main_async(kwargs):
    """
    Async main function to execute TikTok actions.

    Args:
        kwargs (dict): Configuration arguments
    """
    action = kwargs.get('action', '')

    if action == '':
        raise Exception('Action is a required argument.')

    # Create TikTok instance with configuration
    instance = TikTok(**kwargs)
    # Execute the action using the base class method
    await instance.execute_action(action)
    await instance.disconnect()


def main(kwargs):
    """
    Main function to execute TikTok actions.

    Args:
        kwargs (dict): Configuration arguments
    """
    asyncio.run(main_async(kwargs))
