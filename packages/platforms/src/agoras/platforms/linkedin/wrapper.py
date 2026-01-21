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

from agoras.common.utils import parse_metatags
from agoras.core.interfaces import SocialNetwork

from .api import LinkedInAPI


class LinkedIn(SocialNetwork):
    """
    LinkedIn social network implementation.

    This class provides LinkedIn-specific functionality for posting messages,
    images, and managing LinkedIn interactions asynchronously.
    """

    def __init__(self, **kwargs):
        """
        Initialize LinkedIn instance.

        Args:
            **kwargs: Configuration parameters including:
                - linkedin_access_token: LinkedIn access token
                - linkedin_client_id: LinkedIn client ID
                - linkedin_client_secret: LinkedIn client secret
                - linkedin_refresh_token: LinkedIn refresh token
                - linkedin_object_id: LinkedIn object ID
                - linkedin_post_id: LinkedIn post ID
        """
        super().__init__(**kwargs)
        self.linkedin_access_token = None
        self.linkedin_client_id = None
        self.linkedin_client_secret = None
        self.linkedin_refresh_token = None
        self.linkedin_object_id = None
        self.linkedin_post_id = None
        self.api = None

    async def _initialize_client(self):
        """
        Initialize LinkedIn API client.

        Tries to load credentials from CLI params, environment variables, or storage.
        """
        # Try params/environment first
        self.linkedin_access_token = self._get_config_value('linkedin_access_token', 'LINKEDIN_ACCESS_TOKEN')
        self.linkedin_client_id = self._get_config_value('linkedin_client_id', 'LINKEDIN_CLIENT_ID')
        self.linkedin_client_secret = self._get_config_value('linkedin_client_secret', 'LINKEDIN_CLIENT_SECRET')
        self.linkedin_refresh_token = self._get_config_value('linkedin_refresh_token', 'LINKEDIN_REFRESH_TOKEN')
        self.linkedin_object_id = self._get_config_value('linkedin_object_id', 'LINKEDIN_OBJECT_ID')
        self.linkedin_post_id = self._get_config_value('linkedin_post_id', 'LINKEDIN_POST_ID')

        # If credentials not provided, try loading from storage
        # LinkedIn needs user_id (object_id), client_id, client_secret, and refresh_token to authenticate
        if not all([self.linkedin_object_id,
                    self.linkedin_client_id,
                    self.linkedin_client_secret,
                    self.linkedin_refresh_token]):
            from .auth import LinkedInAuthManager
            auth_manager = LinkedInAuthManager(
                user_id=self.linkedin_object_id or '',
                client_id=self.linkedin_client_id or '',
                client_secret=self.linkedin_client_secret or ''
            )

            if auth_manager._load_credentials_from_storage():
                # Fill in missing credentials from storage
                if not self.linkedin_object_id:
                    self.linkedin_object_id = auth_manager.user_id
                if not self.linkedin_client_id:
                    self.linkedin_client_id = auth_manager.client_id
                if not self.linkedin_client_secret:
                    self.linkedin_client_secret = auth_manager.client_secret
                if not self.linkedin_refresh_token:
                    self.linkedin_refresh_token = auth_manager.refresh_token

        # If we have the required auth credentials, authenticate to get access token
        if (self.linkedin_client_id and
                self.linkedin_client_secret and
                self.linkedin_refresh_token):
            from .auth import LinkedInAuthManager
            auth_manager = LinkedInAuthManager(
                user_id=self.linkedin_object_id,
                client_id=self.linkedin_client_id,
                client_secret=self.linkedin_client_secret,
                refresh_token=self.linkedin_refresh_token
            )
            authenticated = await auth_manager.authenticate()
            if authenticated:
                self.linkedin_access_token = auth_manager.access_token

        # Validate all credentials are now available
        if not self.linkedin_access_token:
            raise Exception("Not authenticated. Please run 'agoras linkedin authorize' first.")

        # Initialize LinkedIn API
        self.api = LinkedInAPI(
            self.linkedin_object_id,
            self.linkedin_client_id,
            self.linkedin_client_secret,
            self.linkedin_refresh_token
        )
        await self.api.authenticate()

    async def disconnect(self):
        """
        Disconnect from LinkedIn API and clean up resources.
        """
        if self.api:
            await self.api.disconnect()

    async def post(self, status_text, status_link,
                   status_image_url_1=None, status_image_url_2=None,
                   status_image_url_3=None, status_image_url_4=None):
        """
        Create a post on LinkedIn.

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
            raise Exception('LinkedIn API not initialized')

        status_link_title = ''
        status_link_description = ''
        status_link_image = ''
        media_ids = []
        source_media = list(filter(None, [
            status_image_url_1, status_image_url_2,
            status_image_url_3, status_image_url_4
        ]))

        if not source_media and not status_text and not status_link:
            raise Exception('No status text, link, or images provided.')

        # Parse link metadata if link is provided
        if status_link:
            scraped_data = parse_metatags(status_link)
            status_link_title = scraped_data.get('title', '')
            status_link_description = scraped_data.get('description', '')
            status_link_image = scraped_data.get('image', '')

            if status_link_image and not source_media:
                source_media = [status_link_image]

        # Download and upload images using the Media system
        if source_media:
            images = await self.download_images(source_media)
            for image in images:
                try:
                    # Upload image to LinkedIn
                    if image.content:
                        media_id = await self.api.upload_image(image.content)
                        if media_id:
                            media_ids.append(media_id)
                except Exception as e:
                    print(f"Failed to upload image {image.url}: {str(e)}")
                finally:
                    # Clean up temporary files
                    image.cleanup()

        # Create the post
        post_id = await self.api.post(
            text=status_text,
            link=status_link,
            link_title=status_link_title,
            link_description=status_link_description,
            image_ids=media_ids
        )

        self._output_status(post_id)
        return post_id

    async def like(self, linkedin_post_id=None):
        """
        Like a LinkedIn post.

        Args:
            linkedin_post_id (str, optional): ID of the LinkedIn post to like.
                                               Uses instance linkedin_post_id if not provided.

        Returns:
            str: Post ID
        """
        if not self.api:
            raise Exception('LinkedIn API not initialized')

        post_id = linkedin_post_id or self.linkedin_post_id
        if not post_id:
            raise Exception('LinkedIn post ID is required.')

        result = await self.api.like(post_id)
        self._output_status(result)
        return result

    async def delete(self, linkedin_post_id=None):
        """
        Delete a LinkedIn post.

        Args:
            linkedin_post_id (str, optional): ID of the LinkedIn post to delete.
                                               Uses instance linkedin_post_id if not provided.

        Returns:
            str: Post ID
        """
        if not self.api:
            raise Exception('LinkedIn API not initialized')

        post_id = linkedin_post_id or self.linkedin_post_id
        if not post_id:
            raise Exception('LinkedIn post ID is required.')

        result = await self.api.delete(post_id)
        self._output_status(result)
        return result

    async def share(self, linkedin_post_id=None):
        """
        Share a LinkedIn post.

        Args:
            linkedin_post_id (str, optional): ID of the LinkedIn post to share.
                                               Uses instance linkedin_post_id if not provided.

        Returns:
            str: New post ID
        """
        if not self.api:
            raise Exception('LinkedIn API not initialized')

        post_id = linkedin_post_id or self.linkedin_post_id
        if not post_id:
            raise Exception('LinkedIn post ID is required.')

        result = await self.api.share(post_id)
        self._output_status(result)
        return result

    async def video(self, status_text, video_url, video_title):
        """
        LinkedIn doesn't support direct video uploads in the same way as other platforms.
        This method is a placeholder that raises a NotImplementedError.

        Args:
            status_text (str): Text content to accompany the video
            video_url (str): URL of the video to post
            video_title (str): Title of the video

        Raises:
            NotImplementedError: LinkedIn video uploads require different approach
        """
        raise NotImplementedError(
            'LinkedIn video uploads require specialized handling through LinkedIn Video API. '
            'Use post() method with video links instead.'
        )

    # The base class already provides last_from_feed, random_from_feed, and schedule methods.
    # We only need to override the action handlers for LinkedIn-specific parameter names.

    # Override action handlers to use LinkedIn-specific parameter names
    async def _handle_like_action(self):
        """Handle like action with LinkedIn-specific parameter extraction."""
        linkedin_post_id = self._get_config_value('linkedin_post_id', 'LINKEDIN_POST_ID')
        if not linkedin_post_id:
            raise Exception('LinkedIn post ID is required for like action.')
        await self.like(linkedin_post_id)

    async def _handle_share_action(self):
        """Handle share action with LinkedIn-specific parameter extraction."""
        linkedin_post_id = self._get_config_value('linkedin_post_id', 'LINKEDIN_POST_ID')
        if not linkedin_post_id:
            raise Exception('LinkedIn post ID is required for share action.')
        await self.share(linkedin_post_id)

    async def _handle_delete_action(self):
        """Handle delete action with LinkedIn-specific parameter extraction."""
        linkedin_post_id = self._get_config_value('linkedin_post_id', 'LINKEDIN_POST_ID')
        if not linkedin_post_id:
            raise Exception('LinkedIn post ID is required for delete action.')
        await self.delete(linkedin_post_id)

    # The base class already provides default action handlers for last-from-feed,
    # random-from-feed, and schedule actions with the correct parameter names.
    # No need to override them for LinkedIn.

    async def authorize_credentials(self):
        """
        Authorize and store LinkedIn credentials for future use.

        Returns:
            bool: True if authorization successful
        """
        from .auth import LinkedInAuthManager

        object_id = self._get_config_value('linkedin_object_id', 'LINKEDIN_OBJECT_ID')
        client_id = self._get_config_value('linkedin_client_id', 'LINKEDIN_CLIENT_ID')
        client_secret = self._get_config_value('linkedin_client_secret', 'LINKEDIN_CLIENT_SECRET')

        auth_manager = LinkedInAuthManager(
            user_id=object_id,
            client_id=client_id,
            client_secret=client_secret
        )

        result = await auth_manager.authorize()
        if result:
            print(result)
            return True
        return False


async def main_async(kwargs):
    """
    Async main function to execute LinkedIn actions.

    Args:
        kwargs (dict): Configuration arguments
    """
    action = kwargs.get('action', '')

    if action == '':
        raise Exception('Action is a required argument.')

    # Create LinkedIn instance with configuration
    instance = LinkedIn(**kwargs)

    # Handle authorize action separately (doesn't need client initialization)
    if action == 'authorize':
        success = await instance.authorize_credentials()
        return 0 if success else 1

    # Execute other actions using the base class method
    await instance.execute_action(action)
    await instance.disconnect()


def main(kwargs):
    """
    Main function to execute LinkedIn actions (for backwards compatibility).

    Args:
        kwargs (dict): Configuration arguments
    """
    asyncio.run(main_async(kwargs))
