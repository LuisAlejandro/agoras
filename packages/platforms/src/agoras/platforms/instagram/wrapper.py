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

import asyncio

from agoras.core.interfaces import SocialNetwork

from .api import InstagramAPI


class Instagram(SocialNetwork):
    """
    Instagram social network implementation.

    This class provides Instagram-specific functionality for posting messages,
    videos, and managing Instagram interactions asynchronously.
    """

    def __init__(self, **kwargs):
        """
        Initialize Instagram instance.

        Args:
            **kwargs: Configuration parameters including:
                - instagram_access_token: Instagram access token
                - instagram_client_id: Instagram client ID
                - instagram_client_secret: Instagram client secret
                - instagram_refresh_token: Instagram refresh token
                - instagram_object_id: Instagram object ID
                - instagram_post_id: Instagram post ID
                - instagram_video_type: Instagram video type
                - instagram_video_url: Instagram video URL
                - instagram_video_caption: Instagram video caption
        """
        super().__init__(**kwargs)
        self.instagram_access_token = None
        self.instagram_client_id = None
        self.instagram_client_secret = None
        self.instagram_refresh_token = None
        self.instagram_object_id = None
        self.instagram_post_id = None
        self.instagram_video_type = None
        self.instagram_video_url = None
        self.instagram_video_caption = None
        self.api = None

    async def _initialize_client(self):
        """
        Initialize Instagram API client.

        Tries to load credentials from CLI params, environment variables, or storage.
        """
        # Try params/environment first
        self.instagram_access_token = self._get_config_value('instagram_access_token', 'INSTAGRAM_ACCESS_TOKEN')
        self.instagram_client_id = self._get_config_value('instagram_client_id', 'INSTAGRAM_CLIENT_ID')
        self.instagram_client_secret = self._get_config_value('instagram_client_secret', 'INSTAGRAM_CLIENT_SECRET')
        self.instagram_refresh_token = self._get_config_value('instagram_refresh_token', 'INSTAGRAM_REFRESH_TOKEN')
        self.instagram_object_id = self._get_config_value('instagram_object_id', 'INSTAGRAM_OBJECT_ID')
        self.instagram_post_id = self._get_config_value('instagram_post_id', 'INSTAGRAM_POST_ID')
        self.instagram_video_type = self._get_config_value('instagram_video_type', 'INSTAGRAM_VIDEO_TYPE')
        self.instagram_video_url = self._get_config_value('instagram_video_url', 'INSTAGRAM_VIDEO_URL')
        self.instagram_video_caption = self._get_config_value('instagram_video_caption', 'INSTAGRAM_VIDEO_CAPTION')

        # If credentials not provided, try loading from storage
        # Instagram needs user_id (object_id), client_id, client_secret, and refresh_token to authenticate
        if not all([self.instagram_object_id,
                    self.instagram_client_id,
                    self.instagram_client_secret,
                    self.instagram_refresh_token]):
            from .auth import InstagramAuthManager
            auth_manager = InstagramAuthManager(
                user_id=self.instagram_object_id or '',
                client_id=self.instagram_client_id or '',
                client_secret=self.instagram_client_secret or ''
            )

            if auth_manager._load_credentials_from_storage():
                # Fill in missing credentials from storage
                if not self.instagram_object_id:
                    self.instagram_object_id = auth_manager.user_id
                if not self.instagram_client_id:
                    self.instagram_client_id = auth_manager.client_id
                if not self.instagram_client_secret:
                    self.instagram_client_secret = auth_manager.client_secret
                if not self.instagram_refresh_token:
                    self.instagram_refresh_token = auth_manager.refresh_token

        # If we have the required auth credentials, authenticate to get access token
        if (self.instagram_client_id and
                self.instagram_client_secret and
                self.instagram_refresh_token):
            from .auth import InstagramAuthManager
            auth_manager = InstagramAuthManager(
                user_id=self.instagram_object_id,
                client_id=self.instagram_client_id,
                client_secret=self.instagram_client_secret,
                refresh_token=self.instagram_refresh_token
            )
            authenticated = await auth_manager.authenticate()
            if authenticated:
                self.instagram_access_token = auth_manager.access_token

        # Validate all credentials are now available
        if not self.instagram_access_token:
            raise Exception("Not authenticated. Please run 'agoras instagram authorize' first.")

        # Initialize Instagram API
        self.api = InstagramAPI(
            self.instagram_access_token,
            self.instagram_client_id,
            self.instagram_client_secret,
            self.instagram_refresh_token
        )
        await self.api.authenticate()

    async def disconnect(self):
        """
        Disconnect from Instagram API and clean up resources.
        """
        if self.api:
            await self.api.disconnect()

    async def post(self, status_text, status_link,
                   status_image_url_1=None, status_image_url_2=None,
                   status_image_url_3=None, status_image_url_4=None):
        """
        Create a post on Instagram.

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
            raise Exception('Instagram API not initialized')

        if not self.instagram_object_id:
            raise Exception('Instagram object ID is required.')

        attached_media = []
        source_media = list(filter(None, [
            status_image_url_1, status_image_url_2,
            status_image_url_3, status_image_url_4
        ]))

        if not source_media:
            raise Exception('Instagram requires at least one status image.')

        is_carousel_item = len(source_media) > 1

        # Download and validate images using the Media system
        if source_media:
            images = await self.download_images(source_media)
            for image in images:
                try:
                    # Create media for each image
                    media_id = await self.api.create_media(
                        self.instagram_object_id,
                        image_url=image.url,
                        is_carousel_item=is_carousel_item
                    )
                    attached_media.append(media_id)
                finally:
                    # Clean up temporary files
                    image.cleanup()

        # Create carousel or single post
        if is_carousel_item:
            caption = f'{status_text} {status_link}'
            creation_id = await self.api.create_carousel(
                self.instagram_object_id,
                attached_media,
                caption
            )
        else:
            # For single image, the caption needs to be set in create_media
            # We need to recreate the media with caption for single posts
            if attached_media:
                # Remove the media without caption
                media_id = attached_media[0]
                # Create new media with caption for single posts
                creation_id = await self.api.create_media(
                    self.instagram_object_id,
                    image_url=images[0].url,
                    caption=f'{status_text} {status_link}',
                    is_carousel_item=False
                )
            else:
                raise Exception('No media created')

        # Publish the media
        post_id = await self.api.publish_media(self.instagram_object_id, creation_id)

        self._output_status(post_id)
        return post_id

    async def like(self, instagram_post_id=None):
        """
        Like is not supported for Instagram.

        Args:
            instagram_post_id (str, optional): ID of the Instagram post

        Raises:
            Exception: Like not supported for Instagram
        """
        raise Exception('Like not supported for Instagram')

    async def delete(self, instagram_post_id=None):
        """
        Delete is not supported for Instagram.

        Args:
            instagram_post_id (str, optional): ID of the Instagram post

        Raises:
            Exception: Delete not supported for Instagram
        """
        raise Exception('Delete not supported for Instagram')

    async def share(self, instagram_post_id=None):
        """
        Share is not supported for Instagram.

        Args:
            instagram_post_id (str, optional): ID of the Instagram post

        Raises:
            Exception: Share not supported for Instagram
        """
        raise Exception('Share not supported for Instagram')

    async def video(self, status_text, video_url, video_title):
        """
        Post a video to Instagram.

        Args:
            status_text (str): Text content to accompany the video (caption)
            video_url (str): URL of the video to post
            video_title (str): Title of the video (not used by Instagram)

        Returns:
            str: Post ID
        """
        if not self.api:
            raise Exception('Instagram API not initialized')

        if not self.instagram_object_id:
            raise Exception('Instagram object ID is required.')
        if not video_url:
            raise Exception('Instagram video URL is required.')

        video_type = self.instagram_video_type or ''

        # Download and validate video using the Media system
        video = await self.download_video(video_url)

        if not video.content or not video.file_type:
            video.cleanup()
            raise Exception('Failed to download or validate video')

        # Ensure video is in allowed format for Instagram
        if video.file_type.mime not in ['video/mp4']:
            video.cleanup()
            raise Exception(f'Invalid video type "{video.file_type.mime}" for {video_url}. '
                            f'Instagram requires MP4 format.')

        try:
            # Set media type based on video type
            media_type = None
            if video_type == 'reel':
                media_type = 'REELS'
            elif video_type == 'story':
                media_type = 'STORIES'
            else:
                media_type = 'VIDEO'

            # Create media for video
            creation_id = await self.api.create_media(
                self.instagram_object_id,
                video_url=video_url,
                caption=status_text,
                is_carousel_item=False,
                media_type=media_type
            )

            # Publish the video
            post_id = await self.api.publish_media(self.instagram_object_id, creation_id)

        finally:
            # Clean up using Media system
            video.cleanup()

        self._output_status(post_id)
        return post_id

    async def authorize_credentials(self):
        """
        Authorize and store Instagram credentials for future use.

        Returns:
            bool: True if authorization successful
        """
        from .auth import InstagramAuthManager

        object_id = self._get_config_value('instagram_object_id', 'INSTAGRAM_OBJECT_ID')
        client_id = self._get_config_value('instagram_client_id', 'INSTAGRAM_CLIENT_ID')
        client_secret = self._get_config_value('instagram_client_secret', 'INSTAGRAM_CLIENT_SECRET')

        auth_manager = InstagramAuthManager(
            user_id=object_id,
            client_id=client_id,
            client_secret=client_secret
        )

        result = await auth_manager.authorize()
        if result:
            print(result)
            return True
        return False

    # Override action handlers to use Instagram-specific parameter names
    async def _handle_like_action(self):
        """Handle like action with Instagram-specific parameter extraction."""
        instagram_post_id = self._get_config_value('instagram_post_id', 'INSTAGRAM_POST_ID')
        await self.like(instagram_post_id)

    async def _handle_share_action(self):
        """Handle share action with Instagram-specific parameter extraction."""
        instagram_post_id = self._get_config_value('instagram_post_id', 'INSTAGRAM_POST_ID')
        await self.share(instagram_post_id)

    async def _handle_delete_action(self):
        """Handle delete action with Instagram-specific parameter extraction."""
        instagram_post_id = self._get_config_value('instagram_post_id', 'INSTAGRAM_POST_ID')
        await self.delete(instagram_post_id)

    async def _handle_video_action(self):
        """Handle video action with Instagram-specific parameter extraction."""
        status_text = self._get_config_value('instagram_video_caption', 'INSTAGRAM_VIDEO_CAPTION') or ''
        video_url = self._get_config_value('instagram_video_url', 'INSTAGRAM_VIDEO_URL')
        video_title = ''  # Instagram doesn't use video titles

        if not video_url:
            raise Exception('Instagram video URL is required for video action.')

        await self.video(status_text, video_url, video_title)


async def main_async(kwargs):
    """
    Async main function to execute Instagram actions.

    Args:
        kwargs (dict): Configuration arguments
    """
    action = kwargs.get('action', '')

    if action == '':
        raise Exception('Action is a required argument.')

    # Create Instagram instance with configuration
    instance = Instagram(**kwargs)

    # Handle authorize action separately (doesn't need client initialization)
    if action == 'authorize':
        success = await instance.authorize_credentials()
        return 0 if success else 1

    # Execute other actions using the base class method
    await instance.execute_action(action)
    await instance.disconnect()


def main(kwargs):
    """
    Main function to execute Instagram actions.

    Args:
        kwargs (dict): Configuration arguments
    """
    asyncio.run(main_async(kwargs))
