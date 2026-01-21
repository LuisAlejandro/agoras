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
from typing import List, Optional

from agoras.core.interfaces import SocialNetwork

from .api import WhatsAppAPI


class WhatsApp(SocialNetwork):
    """
    WhatsApp social network implementation.

    This class provides WhatsApp-specific functionality for sending messages,
    images, videos, and managing WhatsApp Business API interactions asynchronously.
    """

    def __init__(self, **kwargs):
        """
        Initialize WhatsApp instance.

        Args:
            **kwargs: Configuration parameters including:
                - whatsapp_access_token: Meta Graph API access token
                - whatsapp_phone_number_id: WhatsApp Business phone number ID
                - whatsapp_business_account_id: WhatsApp Business Account ID
                - whatsapp_recipient: Target recipient phone number
                - whatsapp_message_id: WhatsApp message ID
        """
        super().__init__(**kwargs)
        # Platform-specific configuration attributes
        self.whatsapp_access_token = None
        self.whatsapp_phone_number_id = None
        self.whatsapp_business_account_id = None
        # WhatsApp-specific settings
        self.whatsapp_recipient = None
        self.whatsapp_message_id = None
        self.api = None

    async def _initialize_client(self):
        """
        Initialize WhatsApp API client.

        This method sets up the WhatsApp API client with configuration.
        Tries to load credentials from storage if not provided via parameters.
        """
        # Get configuration using existing pattern
        self.whatsapp_access_token = self._get_config_value('whatsapp_access_token', 'WHATSAPP_ACCESS_TOKEN')
        self.whatsapp_phone_number_id = self._get_config_value('whatsapp_phone_number_id', 'WHATSAPP_PHONE_NUMBER_ID')
        self.whatsapp_business_account_id = self._get_config_value(
            'whatsapp_business_account_id', 'WHATSAPP_BUSINESS_ACCOUNT_ID')

        # If credentials not provided, try loading from storage
        if not self.whatsapp_access_token or not self.whatsapp_phone_number_id:
            from .auth import WhatsAppAuthManager
            auth_manager = WhatsAppAuthManager()
            if auth_manager._load_credentials_from_storage():
                if not self.whatsapp_access_token:
                    self.whatsapp_access_token = auth_manager.access_token
                if not self.whatsapp_phone_number_id:
                    self.whatsapp_phone_number_id = auth_manager.phone_number_id
                if not self.whatsapp_business_account_id:
                    self.whatsapp_business_account_id = auth_manager.business_account_id

        # Required recipient for messaging
        self.whatsapp_recipient = self._get_config_value('whatsapp_recipient', 'WHATSAPP_RECIPIENT')

        # Optional message ID for status/tracking actions
        self.whatsapp_message_id = self._get_config_value('whatsapp_message_id', 'WHATSAPP_MESSAGE_ID')

        # Validation
        if not all([self.whatsapp_access_token, self.whatsapp_phone_number_id]):
            raise Exception("Not authenticated. Please run 'agoras whatsapp authorize' first.")

        if not self.whatsapp_recipient:
            raise Exception('WhatsApp recipient phone number is required.')

        # Initialize API
        self.api = WhatsAppAPI(
            self.whatsapp_access_token,
            self.whatsapp_phone_number_id,
            self.whatsapp_business_account_id
        )
        await self.api.authenticate()

    async def disconnect(self):
        """
        Disconnect from WhatsApp API and clean up resources.
        """
        if self.api:
            await self.api.disconnect()

    async def post(self, status_text, status_link,
                   status_image_url_1=None, status_image_url_2=None,
                   status_image_url_3=None, status_image_url_4=None):
        """
        Create a WhatsApp message (text, image, or video).

        Args:
            status_text (str): Text content of the message
            status_link (str): URL to include in the message
            status_image_url_1 (str, optional): First image URL
            status_image_url_2 (str, optional): Second image URL
            status_image_url_3 (str, optional): Third image URL
            status_image_url_4 (str, optional): Fourth image URL

        Returns:
            str: Message ID
        """
        if not self.api:
            raise Exception('WhatsApp API not initialized')

        # Combine text and link
        message_text = f'{status_text}\n{status_link}'.strip() if status_link else status_text

        # Handle images
        image_urls = list(filter(None, [
            status_image_url_1, status_image_url_2,
            status_image_url_3, status_image_url_4
        ]))

        if image_urls:
            # WhatsApp supports multiple media in sequence
            message_ids = []
            images = await self.download_images(image_urls)

            try:
                for i, image in enumerate(images):
                    if image.content and image.file_type:
                        # First image gets the full caption, others get minimal caption
                        caption = message_text if i == 0 else f"Image {i + 1}"

                        message_id = await self.api.send_image(
                            to=self.whatsapp_recipient,
                            image_url=image.url,
                            caption=caption
                        )
                        message_ids.append(message_id)
                    else:
                        raise Exception(f'Failed to validate image: {image.url}')
            finally:
                for image in images:
                    image.cleanup()

            # Return first message ID for consistency
            primary_message_id = message_ids[0] if message_ids else None
        else:
            # Text-only message
            if not message_text:
                raise Exception('No status text, link, or images provided.')

            primary_message_id = await self.api.send_message(
                to=self.whatsapp_recipient,
                text=message_text
            )

        self._output_status(primary_message_id)
        return primary_message_id

    async def like(self, message_id=None):
        """
        Like a WhatsApp message (not supported).

        Args:
            message_id (str, optional): ID of the message to like.
                                       Uses instance whatsapp_message_id if not provided.

        Raises:
            Exception: Like not supported for WhatsApp
        """
        raise Exception('Like not supported for WhatsApp')

    async def delete(self, message_id=None):
        """
        Delete a WhatsApp message (not supported via API).

        Args:
            message_id (str, optional): ID of the message to delete.
                                      Uses instance whatsapp_message_id if not provided.

        Raises:
            Exception: Delete not supported for WhatsApp
        """
        raise Exception('Delete not supported for WhatsApp')

    async def share(self, message_id=None):
        """
        Share a WhatsApp message (not supported via API).

        Args:
            message_id (str, optional): ID of the message to share.
                                       Uses instance whatsapp_message_id if not provided.

        Raises:
            Exception: Share not supported for WhatsApp
        """
        raise Exception('Share not supported for WhatsApp')

    async def video(self, status_text, video_url, video_title):
        """
        Post a video message to WhatsApp.

        Args:
            status_text (str): Text content to accompany the video (caption)
            video_url (str): URL of the video to post
            video_title (str): Title of the video (not used by WhatsApp, but kept for interface compatibility)

        Returns:
            str: Message ID
        """
        if not self.api:
            raise Exception('WhatsApp API not initialized')

        if not video_url:
            raise Exception('Video URL is required.')

        # Download and validate video using the Media system
        video = await self.download_video(video_url)

        if not video.content or not video.file_type:
            video.cleanup()
            raise Exception('Failed to download or validate video')

        # Ensure video is in supported format (MP4, 3GP)
        supported_formats = ['video/mp4', 'video/3gp', 'video/3gpp']
        if video.file_type.mime not in supported_formats:
            video.cleanup()
            raise Exception(f'Invalid video type "{video.file_type.mime}" for {video_url}. '
                            f'WhatsApp supports MP4 and 3GP formats.')

        try:
            # Send video with caption (status_text)
            message_id = await self.api.send_video(
                to=self.whatsapp_recipient,
                video_url=video.url,
                caption=status_text
            )
        finally:
            # Clean up using Media system
            video.cleanup()

        self._output_status(message_id)
        return message_id

    async def send_template(
            self,
            template_name: str,
            language_code: str = "en",
            components: Optional[List] = None) -> str:
        """
        Send a template message.

        Args:
            template_name (str): Name of the pre-approved template
            language_code (str): Language code (ISO 639-1 format, default: "en")
            components (list, optional): Template components (parameters, buttons, etc.)

        Returns:
            str: Message ID
        """
        if not self.api:
            raise Exception('WhatsApp API not initialized')

        if not template_name:
            raise Exception('Template name is required.')

        message_id = await self.api.send_template(
            to=self.whatsapp_recipient,
            template_name=template_name,
            language_code=language_code,
            components=components
        )
        self._output_status(message_id)
        return message_id

    # Override action handlers to use WhatsApp-specific parameter names
    async def _handle_like_action(self):
        """Handle like action with WhatsApp-specific parameter extraction."""
        whatsapp_message_id = self._get_config_value('whatsapp_message_id', 'WHATSAPP_MESSAGE_ID')
        if not whatsapp_message_id:
            raise Exception('WhatsApp message ID is required for like action.')
        await self.like(whatsapp_message_id)

    async def _handle_share_action(self):
        """Handle share action with WhatsApp-specific parameter extraction."""
        whatsapp_message_id = self._get_config_value('whatsapp_message_id', 'WHATSAPP_MESSAGE_ID')
        if not whatsapp_message_id:
            raise Exception('WhatsApp message ID is required for share action.')
        await self.share(whatsapp_message_id)

    async def _handle_delete_action(self):
        """Handle delete action with WhatsApp-specific parameter extraction."""
        whatsapp_message_id = self._get_config_value('whatsapp_message_id', 'WHATSAPP_MESSAGE_ID')
        if not whatsapp_message_id:
            raise Exception('WhatsApp message ID is required for delete action.')
        await self.delete(whatsapp_message_id)

    async def _handle_video_action(self):
        """Handle video action with WhatsApp-specific parameter extraction."""
        status_text = self._get_config_value('status_text', 'STATUS_TEXT') or ''
        video_url = self._get_config_value('video_url', 'VIDEO_URL')
        video_title = self._get_config_value('video_title', 'VIDEO_TITLE') or ''

        if not video_url:
            raise Exception('Video URL is required for video action.')

        await self.video(status_text, video_url, video_title)

    async def _handle_template_action(self):
        """Handle template action with WhatsApp-specific parameter extraction."""
        template_name = self._get_config_value('whatsapp_template_name', 'WHATSAPP_TEMPLATE_NAME')
        language_code = self._get_config_value('whatsapp_template_language', 'WHATSAPP_TEMPLATE_LANGUAGE') or 'en'
        # Note: Template components would need JSON parsing if provided
        # For now, support simple template sending without components
        components = None

        if not template_name:
            raise Exception('Template name is required for template action.')

        await self.send_template(template_name, language_code=language_code, components=components)

    async def authorize_credentials(self):
        """
        Authorize and store WhatsApp credentials for future use.

        Returns:
            bool: True if authorization successful
        """
        from .auth import WhatsAppAuthManager

        access_token = self._get_config_value('whatsapp_access_token', 'WHATSAPP_ACCESS_TOKEN')
        phone_number_id = self._get_config_value('whatsapp_phone_number_id', 'WHATSAPP_PHONE_NUMBER_ID')
        business_account_id = self._get_config_value('whatsapp_business_account_id', 'WHATSAPP_BUSINESS_ACCOUNT_ID')

        auth_manager = WhatsAppAuthManager(
            access_token=access_token,
            phone_number_id=phone_number_id,
            business_account_id=business_account_id
        )

        result = await auth_manager.authorize()
        if result:
            print(result)
            return True
        return False

    async def execute_action(self, action):
        """
        Execute the specified action asynchronously.

        Override base class to support WhatsApp-specific actions.

        Args:
            action (str): Action to execute

        Raises:
            Exception: If action is not supported or required arguments missing
        """
        if action == '':
            raise Exception('Action is a required argument.')

        # Handle authorize action separately (doesn't need client initialization)
        if action == 'authorize':
            success = await self.authorize_credentials()
            if not success:
                raise Exception('WhatsApp authorization failed.')
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
        elif action == 'template':
            await self._handle_template_action()
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
    Async main function to execute WhatsApp actions.

    Args:
        kwargs (dict): Configuration arguments
    """
    action = kwargs.get('action', '')

    if action == '':
        raise Exception('Action is a required argument.')

    # Create WhatsApp instance with configuration
    instance = WhatsApp(**kwargs)

    # Execute the action (authorize is handled in execute_action)
    await instance.execute_action(action)

    # Only disconnect if client was initialized (not for authorize action)
    if action != 'authorize':
        await instance.disconnect()


def main(kwargs):
    """
    Main function to execute WhatsApp actions.

    Args:
        kwargs (dict): Configuration arguments
    """
    asyncio.run(main_async(kwargs))
