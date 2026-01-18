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

from .api import FacebookAPI


class Facebook(SocialNetwork):
    """
    Facebook social network implementation.

    This class provides Facebook-specific functionality for posting messages,
    videos, and managing Facebook interactions asynchronously.
    """

    def __init__(self, **kwargs):
        """
        Initialize Facebook instance.

        Args:
            **kwargs: Configuration parameters including:
                - facebook_access_token: Facebook access token
                - facebook_client_id: Facebook client ID
                - facebook_client_secret: Facebook client secret
                - facebook_refresh_token: Facebook refresh token
                - facebook_object_id: Facebook object ID
                - facebook_post_id: Facebook post ID
                - facebook_profile_id: Facebook profile ID
                - facebook_app_id: Facebook app ID
        """
        super().__init__(**kwargs)
        self.facebook_access_token = None
        self.facebook_client_id = None
        self.facebook_client_secret = None
        self.facebook_refresh_token = None
        self.facebook_object_id = None
        self.facebook_post_id = None
        self.facebook_profile_id = None
        self.facebook_app_id = None
        self.api = None

    async def _initialize_client(self):
        """
        Initialize Facebook API client.

        Tries to load credentials from CLI params, environment variables, or storage.
        """
        # Try params/environment first
        self.facebook_access_token = self._get_config_value('facebook_access_token', 'FACEBOOK_ACCESS_TOKEN')
        self.facebook_client_id = self._get_config_value('facebook_client_id', 'FACEBOOK_CLIENT_ID')
        self.facebook_client_secret = self._get_config_value('facebook_client_secret', 'FACEBOOK_CLIENT_SECRET')
        self.facebook_refresh_token = self._get_config_value('facebook_refresh_token', 'FACEBOOK_REFRESH_TOKEN')
        # Object ID should always come from config/env, not storage (allows switching between page/user)
        self.facebook_object_id = self._get_config_value('facebook_object_id', 'FACEBOOK_OBJECT_ID')
        self.facebook_post_id = self._get_config_value('facebook_post_id', 'FACEBOOK_POST_ID')
        self.facebook_profile_id = self._get_config_value('facebook_profile_id', 'FACEBOOK_PROFILE_ID')
        self.facebook_app_id = self._get_config_value('facebook_app_id', 'FACEBOOK_APP_ID')

        # If auth credentials not provided, try loading from storage
        # Facebook needs client_id, client_secret, and refresh_token to authenticate
        # Note: object_id is NOT loaded from storage to allow switching targets
        if not all([self.facebook_client_id,
                    self.facebook_client_secret,
                    self.facebook_refresh_token]):
            from .auth import FacebookAuthManager
            auth_manager = FacebookAuthManager(
                user_id=self.facebook_object_id or '',
                client_id=self.facebook_client_id or '',
                client_secret=self.facebook_client_secret or ''
            )

            if auth_manager._load_credentials_from_storage():
                # Fill in missing auth credentials from storage
                if not self.facebook_client_id:
                    self.facebook_client_id = auth_manager.client_id
                if not self.facebook_client_secret:
                    self.facebook_client_secret = auth_manager.client_secret
                if not self.facebook_refresh_token:
                    self.facebook_refresh_token = auth_manager.refresh_token
                # Fill in object_id from storage only if not provided via config/env
                if not self.facebook_object_id:
                    self.facebook_object_id = auth_manager.user_id

        # If we have the required auth credentials, authenticate to get access token
        if (self.facebook_client_id and
                self.facebook_client_secret and
                self.facebook_refresh_token):
            from .auth import FacebookAuthManager
            auth_manager = FacebookAuthManager(
                user_id=self.facebook_object_id,
                client_id=self.facebook_client_id,
                client_secret=self.facebook_client_secret,
                refresh_token=self.facebook_refresh_token
            )
            authenticated = await auth_manager.authenticate()
            if authenticated:
                self.facebook_access_token = auth_manager.access_token

        # Check if we need to exchange for page token
        self._is_page_target = False  # Track if we're posting to a page
        if self.facebook_access_token and self.facebook_object_id:
            try:
                # Create temporary API instance with user token to check if it's a page
                temp_api = FacebookAPI(
                    self.facebook_access_token,
                    self.facebook_client_id,
                    self.facebook_client_secret,
                    self.facebook_refresh_token,
                    self.facebook_app_id
                )
                await temp_api.authenticate()

                # Check if the object_id is a page
                is_page = await temp_api.check_if_page(self.facebook_object_id)
                self._is_page_target = is_page

                if is_page:
                    try:
                        # Exchange user token for page token
                        page_token = await temp_api.get_page_token(self.facebook_object_id)
                        if page_token:
                            self.facebook_access_token = page_token
                        else:
                            raise Exception(
                                f'Could not obtain page access token for page {self.facebook_object_id}. '
                                'Make sure you are an admin/editor of this page and have granted the required '
                                'permissions (pages_read_engagement, pages_manage_posts).')
                    except Exception as page_error:
                        raise Exception(
                            f'Cannot post to Facebook Page {self.facebook_object_id}: '
                            f'Page token exchange failed. {str(page_error)}')

            except Exception as e:
                # If page detection fails, continue with user token
                # This allows posting to work even if we can't determine object type
                print(f"[WARNING] Page detection/token exchange failed: {str(e)}")
                pass

        # Validate all credentials are now available
        if not self.facebook_access_token:
            raise Exception("Not authenticated. Please run 'agoras facebook authorize' first.")

        # Initialize Facebook API
        self.api = FacebookAPI(
            self.facebook_access_token,
            self.facebook_client_id,
            self.facebook_client_secret,
            self.facebook_refresh_token,
            self.facebook_app_id
        )

        # If we have a page token (detected by _is_page_target), skip auth manager refresh
        # Page tokens should be used as-is without refreshing through auth manager
        if getattr(self, '_is_page_target', False):
            # Manually initialize the client with the page token
            from .client import FacebookAPIClient
            self.api.client = FacebookAPIClient(self.facebook_access_token)
            await self.api.client.authenticate()
            self.api._authenticated = True
            # Mark the auth manager as authenticated too
            self.api.auth_manager.access_token = self.facebook_access_token
            self.api.auth_manager.client = self.api.client
            # Set dummy user_info for page tokens (not needed for page posting)
            self.api.auth_manager.user_info = {'id': self.facebook_object_id, 'name': 'Facebook Page'}
        else:
            # For user tokens, go through normal auth manager flow
            await self.api.authenticate()

    async def disconnect(self):
        """
        Disconnect from Facebook API and clean up resources.
        """
        if self.api:
            await self.api.disconnect()

    async def post(self, status_text, status_link,
                   status_image_url_1=None, status_image_url_2=None,
                   status_image_url_3=None, status_image_url_4=None):
        """
        Create a post on Facebook.

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
            raise Exception('Facebook API not initialized')

        if not self.facebook_object_id:
            raise Exception('Facebook object ID is required.')

        attached_media = []
        source_media = list(filter(None, [
            status_image_url_1, status_image_url_2,
            status_image_url_3, status_image_url_4
        ]))

        if not source_media and not status_text and not status_link:
            raise Exception('No status text, link, or images provided.')

        # Handle posting differently for pages vs profiles
        is_page_target = getattr(self, '_is_page_target', False)

        if is_page_target:
            # For Facebook Pages: Post directly with image URLs
            # Pages support posting images via URLs in the feed
            if source_media:
                # Use the first image URL as the link parameter
                link_to_use = status_link or source_media[0]
            else:
                link_to_use = status_link

            post_id = await self.api.post(
                self.facebook_object_id,
                message=status_text,
                link=link_to_use,
                attached_media=None  # Pages don't use attached_media for images
            )
        else:
            # For Facebook Profiles: Upload media first, then attach
            # Download and validate images using the Media system
            if source_media:
                images = await self.download_images(source_media)
                for image in images:
                    try:
                        # Upload media to Facebook
                        media_response = await self.api.upload_media(
                            self.facebook_object_id,
                            image.url,
                            published=True
                        )
                        if media_response and 'id' in media_response:
                            attached_media.append({
                                'media_fbid': media_response['id']
                            })
                    finally:
                        # Clean up temporary files
                        image.cleanup()

            # Create the post
            post_id = await self.api.post(
                self.facebook_object_id,
                message=status_text,
                link=status_link,
                attached_media=attached_media if attached_media else None
            )

        self._output_status(post_id)
        return post_id

    async def like(self, facebook_post_id=None):
        """
        Like a Facebook post.

        Args:
            facebook_post_id (str, optional): ID of the Facebook post to like.
                                               Uses instance facebook_post_id if not provided.

        Returns:
            str: Post ID
        """
        if not self.api:
            raise Exception('Facebook API not initialized')

        post_id = facebook_post_id or self.facebook_post_id
        if not post_id:
            raise Exception('Facebook post ID is required.')
        if not self.facebook_object_id:
            raise Exception('Facebook object ID is required.')

        result = await self.api.like(self.facebook_object_id, post_id)
        self._output_status(result)
        return result

    async def delete(self, facebook_post_id=None):
        """
        Delete a Facebook post.

        Args:
            facebook_post_id (str, optional): ID of the Facebook post to delete.
                                               Uses instance facebook_post_id if not provided.

        Returns:
            str: Post ID
        """
        if not self.api:
            raise Exception('Facebook API not initialized')

        post_id = facebook_post_id or self.facebook_post_id
        if not post_id:
            raise Exception('Facebook post ID is required.')
        if not self.facebook_object_id:
            raise Exception('Facebook object ID is required.')

        result = await self.api.delete(self.facebook_object_id, post_id)
        self._output_status(result)
        return result

    async def share(self, facebook_post_id=None):
        """
        Share a Facebook post.

        Args:
            facebook_post_id (str, optional): ID of the Facebook post to share.
                                               Uses instance facebook_post_id if not provided.

        Returns:
            str: New post ID
        """
        if not self.api:
            raise Exception('Facebook API not initialized')

        post_id = facebook_post_id or self.facebook_post_id
        if not post_id:
            raise Exception('Facebook post ID is required.')
        if not self.facebook_object_id:
            raise Exception('Facebook object ID is required.')
        if not self.facebook_profile_id:
            raise Exception('Facebook profile ID is required.')

        result = await self.api.share(
            self.facebook_profile_id,
            self.facebook_object_id,
            post_id
        )
        self._output_status(result)
        return result

    async def _upload_reel_or_story(self, video_type, status_text, video_url):
        """
        Upload a video as a reel or story to Facebook.

        Args:
            video_type (str): Type of video ('reel' or 'story')
            status_text (str): Text content to accompany the video
            video_url (str): URL of the video to post

        Returns:
            str: Video/Post ID
        """
        if not self.api:
            raise Exception('Facebook API client not initialized')

        assert self.api is not None  # Help type checker
        assert self.facebook_object_id is not None  # Help type checker

        return await self.api.upload_reel_or_story(
            object_id=self.facebook_object_id,
            video_type=video_type,
            status_text=status_text,
            video_url=video_url
        )

    async def _upload_regular_video(self, video, status_text, video_title):
        """
        Upload a regular video to Facebook.

        Args:
            video: Video object from Media system
            status_text (str): Text content to accompany the video
            video_title (str): Title of the video

        Returns:
            str: Post ID
        """
        if not self.facebook_app_id:
            raise Exception('Facebook app ID is required for regular video uploads.')

        assert self.api is not None  # Help type checker
        assert self.facebook_object_id is not None  # Help type checker

        # Get video file info
        video_content = video.content or b""
        video_file_type = video.file_type.mime if video.file_type else "video/mp4"
        video_file_size = video.get_file_size()
        video_filename = f"video.{video.file_type.extension}" if video.file_type else "video.mp4"

        return await self.api.upload_regular_video(
            object_id=self.facebook_object_id,
            video_content=video_content,
            video_file_type=video_file_type,
            video_file_size=video_file_size,
            video_filename=video_filename,
            status_text=status_text,
            video_title=video_title
        )

    async def video(self, status_text, video_url, video_title):
        """
        Post a video to Facebook.

        Args:
            status_text (str): Text content to accompany the video (description)
            video_url (str): URL of the video to post
            video_title (str): Title of the video

        Returns:
            str: Post ID
        """
        if not self.api:
            raise Exception('Facebook API not initialized')

        if not video_title or not status_text:
            raise Exception('Video title and description are required.')
        if not video_url:
            raise Exception('Video URL is required.')
        if not self.facebook_object_id:
            raise Exception('Facebook object ID is required.')

        # Get video type from config
        video_type = self._get_config_value('facebook_video_type', 'FACEBOOK_VIDEO_TYPE') or ''

        # Download and validate video using the Media system
        video = await self.download_video(video_url)

        if not video.content or not video.file_type:
            video.cleanup()
            raise Exception('Failed to download or validate video')

        # Ensure video is MP4 format for Facebook
        if video.file_type.mime not in ['video/mp4']:
            video.cleanup()
            raise Exception(f'Invalid video type "{video.file_type.mime}" for {video_url}. '
                            f'Facebook requires MP4 format.')

        try:
            # Handle different video types
            if video_type in ['reel', 'story']:
                post_id = await self._upload_reel_or_story(video_type, status_text, video_url)
            else:
                post_id = await self._upload_regular_video(video, status_text, video_title)

        finally:
            # Clean up using Media system
            video.cleanup()

        self._output_status(post_id)
        return post_id

    async def authorize_credentials(self):
        """
        Authorize and store Facebook credentials for future use.

        Returns:
            bool: True if authorization successful
        """
        from .auth import FacebookAuthManager

        object_id = self._get_config_value('facebook_object_id', 'FACEBOOK_OBJECT_ID')
        client_id = self._get_config_value('facebook_client_id', 'FACEBOOK_CLIENT_ID')
        client_secret = self._get_config_value('facebook_client_secret', 'FACEBOOK_CLIENT_SECRET')
        self._get_config_value('facebook_app_id', 'FACEBOOK_APP_ID')

        auth_manager = FacebookAuthManager(
            user_id=object_id,
            client_id=client_id,
            client_secret=client_secret
        )

        result = await auth_manager.authorize()
        if result:
            print(result)
            return True
        return False

    # Override action handlers to use Facebook-specific parameter names
    async def _handle_like_action(self):
        """Handle like action with Facebook-specific parameter extraction."""
        facebook_post_id = self._get_config_value('facebook_post_id', 'FACEBOOK_POST_ID')
        if not facebook_post_id:
            raise Exception('Facebook post ID is required for like action.')
        await self.like(facebook_post_id)

    async def _handle_share_action(self):
        """Handle share action with Facebook-specific parameter extraction."""
        facebook_post_id = self._get_config_value('facebook_post_id', 'FACEBOOK_POST_ID')
        if not facebook_post_id:
            raise Exception('Facebook post ID is required for share action.')
        await self.share(facebook_post_id)

    async def _handle_delete_action(self):
        """Handle delete action with Facebook-specific parameter extraction."""
        facebook_post_id = self._get_config_value('facebook_post_id', 'FACEBOOK_POST_ID')
        if not facebook_post_id:
            raise Exception('Facebook post ID is required for delete action.')
        await self.delete(facebook_post_id)

    async def _handle_video_action(self):
        """Handle video action with Facebook-specific parameter extraction."""
        status_text = self._get_config_value('facebook_video_description', 'FACEBOOK_VIDEO_DESCRIPTION') or ''
        video_url = self._get_config_value('facebook_video_url', 'FACEBOOK_VIDEO_URL')
        video_title = self._get_config_value('facebook_video_title', 'FACEBOOK_VIDEO_TITLE') or ''

        if not video_url:
            raise Exception('Facebook video URL is required for video action.')

        await self.video(status_text, video_url, video_title)


async def main_async(kwargs):
    """
    Async main function to execute Facebook actions.

    Args:
        kwargs (dict): Configuration arguments
    """
    action = kwargs.get('action', '')

    if action == '':
        raise Exception('Action is a required argument.')

    # Create Facebook instance with configuration
    instance = Facebook(**kwargs)

    # Handle authorize action separately (doesn't need client initialization)
    if action == 'authorize':
        success = await instance.authorize_credentials()
        return 0 if success else 1

    # Execute other actions using the base class method
    await instance.execute_action(action)
    await instance.disconnect()


def main(kwargs):
    """
    Main function to execute Facebook actions.

    Args:
        kwargs (dict): Configuration arguments
    """
    asyncio.run(main_async(kwargs))
