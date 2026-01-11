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
from typing import List

from .api import TelegramAPI
from agoras.core.interfaces import SocialNetwork


class Telegram(SocialNetwork):
    """
    Telegram social network implementation.

    This class provides Telegram-specific functionality for posting messages,
    images, videos, and managing Telegram interactions asynchronously.
    """

    def __init__(self, **kwargs):
        """
        Initialize Telegram instance.

        Args:
            **kwargs: Configuration parameters including:
                - telegram_bot_token: Telegram bot token from @BotFather
                - telegram_chat_id: Target chat ID (user, group, or channel)
                - telegram_parse_mode: Message parse mode (HTML, Markdown, MarkdownV2)
                - telegram_message_id: Message ID for edit/delete actions
                - telegram_reply_to_message_id: Message ID to reply to
        """
        super().__init__(**kwargs)
        # Platform-specific configuration attributes
        self.telegram_bot_token = None
        self.telegram_chat_id = None
        self.telegram_parse_mode = None
        # Action-specific attributes
        self.telegram_message_id = None
        self.telegram_reply_to_message_id = None
        self.api = None

    async def _initialize_client(self):
        """
        Initialize Telegram API client.

        This method sets up the Telegram API client with configuration.
        """
        # Get configuration values
        self.telegram_bot_token = self._get_config_value('telegram_bot_token', 'TELEGRAM_BOT_TOKEN')
        self.telegram_chat_id = self._get_config_value('telegram_chat_id', 'TELEGRAM_CHAT_ID')

        # Optional configuration
        self.telegram_parse_mode = self._get_config_value('telegram_parse_mode', 'TELEGRAM_PARSE_MODE') or 'HTML'
        self.telegram_reply_to_message_id = self._get_config_value('telegram_reply_to_message_id', 'TELEGRAM_REPLY_TO_MESSAGE_ID')
        self.telegram_message_id = self._get_config_value('telegram_message_id', 'TELEGRAM_MESSAGE_ID')

        # Validation
        if not self.telegram_bot_token:
            raise Exception('Telegram bot token is required.')

        if not self.telegram_chat_id:
            raise Exception('Telegram chat ID is required.')

        # Initialize Telegram API
        self.api = TelegramAPI(self.telegram_bot_token, self.telegram_chat_id)
        await self.api.authenticate()

    async def disconnect(self):
        """
        Disconnect from Telegram API and clean up resources.
        """
        if self.api:
            await self.api.disconnect()

    async def post(self, status_text, status_link,
                   status_image_url_1=None, status_image_url_2=None,
                   status_image_url_3=None, status_image_url_4=None):
        """
        Create a post on Telegram.

        Args:
            status_text (str): Text content of the post
            status_link (str): URL to include in the post
            status_image_url_1 (str, optional): First image URL
            status_image_url_2 (str, optional): Second image URL
            status_image_url_3 (str, optional): Third image URL
            status_image_url_4 (str, optional): Fourth image URL

        Returns:
            str: Message ID
        """
        if not self.api:
            raise Exception('Telegram API not initialized')

        # Combine text and link
        message_text = f'{status_text}\n{status_link}'.strip() if status_link else status_text

        # Handle images
        image_urls = list(filter(None, [
            status_image_url_1, status_image_url_2,
            status_image_url_3, status_image_url_4
        ]))

        if image_urls:
            # For multiple images, create a media group
            if len(image_urls) > 1:
                message_id = await self._send_media_group(image_urls, message_text)
            else:
                # Single image
                images = await self.download_images(image_urls)
                try:
                    image = images[0]
                    if image.content and image.file_type:
                        message_id = await self.api.send_photo(
                            chat_id=self.telegram_chat_id,
                            photo_url=image.url,
                            caption=message_text,
                            parse_mode=self.telegram_parse_mode
                        )
                    else:
                        raise Exception(f'Failed to validate image: {image.url}')
                finally:
                    for image in images:
                        image.cleanup()
        else:
            # Text-only message
            message_id = await self.api.send_message(
                chat_id=self.telegram_chat_id,
                text=message_text,
                parse_mode=self.telegram_parse_mode
            )

        self._output_status(message_id)
        return message_id

    async def _send_media_group(self, image_urls: List[str], caption: str) -> str:
        """
        Send multiple images as a media group (album).

        Full implementation for Phase 4.

        Args:
            image_urls (List[str]): List of image URLs
            caption (str): Caption text (applied to first image only)

        Returns:
            str: Message ID of first message in group
        """
        # Download all images
        images = await self.download_images(image_urls)
        try:
            # Prepare media items for Telegram API
            media_items = []
            for i, image in enumerate(images):
                if image.content and image.file_type:
                    media_items.append({
                        'type': 'photo',
                        'media': image.content,
                        'caption': caption if i == 0 else None  # Caption only on first
                    })
                else:
                    raise Exception(f'Failed to validate image: {image.url}')

            if not media_items:
                raise Exception('No valid images to send')

            # Send as media group
            message_ids = await self.api.send_media_group(
                chat_id=self.telegram_chat_id,
                media=media_items
            )

            # Return first message ID
            return message_ids[0] if message_ids else ''
        finally:
            for image in images:
                image.cleanup()

    async def video(self, status_text, video_url, video_title):
        """
        Post a video to Telegram.

        Args:
            status_text (str): Text content to accompany the video
            video_url (str): URL of the video to post
            video_title (str): Title of the video

        Returns:
            str: Message ID
        """
        if not self.api:
            raise Exception('Telegram API not initialized')

        if not video_url:
            raise Exception('Video URL is required.')

        # Use status_text or video_title as caption
        caption = status_text or video_title or ''

        # Download and validate video using Media system
        video = await self.download_video(video_url)

        try:
            if not video.content or not video.file_type:
                raise Exception('Failed to download or validate video')

            # Send video with caption
            message_id = await self.api.send_video(
                chat_id=self.telegram_chat_id,
                video_url=video_url,
                caption=caption,
                parse_mode=self.telegram_parse_mode
            )

            self._output_status(message_id)
            return message_id
        finally:
            # Clean up downloaded video
            video.cleanup()

    async def like(self, post_id):
        """
        Like is not supported for Telegram.

        Args:
            post_id (str): Message ID

        Raises:
            Exception: Like not supported for Telegram
        """
        raise Exception('Like not supported for Telegram')

    async def delete(self, post_id):
        """
        Delete a Telegram message.

        Args:
            post_id (str): Message ID to delete

        Returns:
            str: Message ID
        """
        if not self.api:
            raise Exception('Telegram API not initialized')

        if not post_id:
            raise Exception('Message ID is required for deletion')

        message_id = await self.api.delete(
            post_id=post_id,
            chat_id=self.telegram_chat_id
        )

        self._output_status(message_id)
        return message_id

    async def share(self, post_id):
        """
        Share is not supported for Telegram.

        Args:
            post_id (str): Message ID

        Raises:
            Exception: Share not supported for Telegram
        """
        raise Exception('Share not supported for Telegram')

    async def edit_message(self, message_id: str = None, new_text: str = None) -> str:
        """
        Edit a previously sent message.

        Args:
            message_id (str, optional): ID of the message to edit (uses telegram_message_id if not provided)
            new_text (str, optional): New message text (uses status_text if not provided)

        Returns:
            str: Message ID
        """
        if not self.api:
            raise Exception('Telegram API not initialized')

        # Get message_id from parameter or configuration
        msg_id = message_id or self.telegram_message_id
        if not msg_id:
            raise Exception('Message ID is required for editing')

        # Get new_text from parameter or configuration
        text = new_text or self._get_config_value('status_text', 'STATUS_TEXT')
        if not text:
            raise Exception('New message text is required for editing')

        edited_id = await self.api.edit_message(
            chat_id=self.telegram_chat_id,
            message_id=int(msg_id),
            text=text,
            parse_mode=self.telegram_parse_mode
        )

        self._output_status(edited_id)
        return edited_id

    async def send_poll(self, question: str = None, options: List[str] = None,
                        is_anonymous: bool = True) -> str:
        """
        Send a poll to the chat.

        Args:
            question (str, optional): Poll question (uses telegram_poll_question if not provided)
            options (List[str], optional): List of poll options (uses telegram_poll_options if not provided)
            is_anonymous (bool): Whether poll is anonymous

        Returns:
            str: Message ID
        """
        if not self.api:
            raise Exception('Telegram API not initialized')

        # Get question from parameter or configuration
        poll_question = question or self._get_config_value('telegram_poll_question', 'TELEGRAM_POLL_QUESTION')
        if not poll_question:
            raise Exception('Poll question is required')

        # Get options from parameter or configuration
        poll_options = options
        if not poll_options:
            options_str = self._get_config_value('telegram_poll_options', 'TELEGRAM_POLL_OPTIONS')
            if options_str:
                poll_options = [opt.strip() for opt in options_str.split(',')]
            else:
                raise Exception('Poll options are required')

        # Validate options
        if len(poll_options) < 2 or len(poll_options) > 10:
            raise Exception('Poll must have between 2 and 10 options')

        # Get is_anonymous from configuration if not provided
        if is_anonymous is True:
            anonymous_str = self._get_config_value('telegram_poll_anonymous', 'TELEGRAM_POLL_ANONYMOUS')
            if anonymous_str is not None:
                is_anonymous = anonymous_str.upper() in ['TRUE', '1', 'YES', 'ON']

        message_id = await self.api.send_poll(
            chat_id=self.telegram_chat_id,
            question=poll_question,
            options=poll_options,
            is_anonymous=is_anonymous
        )

        self._output_status(message_id)
        return message_id

    async def send_document(self, document_url: str = None, caption: str = None) -> str:
        """
        Send a document file.

        Args:
            document_url (str, optional): URL of the document to send (uses telegram_document_url if not provided)
            caption (str, optional): Document caption

        Returns:
            str: Message ID
        """
        if not self.api:
            raise Exception('Telegram API not initialized')

        # Get document_url from parameter or configuration
        doc_url = document_url or self._get_config_value('telegram_document_url', 'TELEGRAM_DOCUMENT_URL')
        if not doc_url:
            raise Exception('Document URL is required')

        # Get caption from parameter or configuration
        doc_caption = caption or self._get_config_value('status_text', 'STATUS_TEXT')

        message_id = await self.api.send_document(
            chat_id=self.telegram_chat_id,
            document_url=doc_url,
            caption=doc_caption,
            parse_mode=self.telegram_parse_mode
        )

        self._output_status(message_id)
        return message_id

    async def send_audio(self, audio_url: str = None, caption: str = None,
                         duration: int = None, performer: str = None,
                         title: str = None) -> str:
        """
        Send an audio file.

        Args:
            audio_url (str, optional): URL of the audio to send (uses telegram_audio_url if not provided)
            caption (str, optional): Audio caption
            duration (int, optional): Audio duration in seconds
            performer (str, optional): Performer name
            title (str, optional): Track title

        Returns:
            str: Message ID
        """
        if not self.api:
            raise Exception('Telegram API not initialized')

        # Get audio_url from parameter or configuration
        aud_url = audio_url or self._get_config_value('telegram_audio_url', 'TELEGRAM_AUDIO_URL')
        if not aud_url:
            raise Exception('Audio URL is required')

        # Get caption from parameter or configuration
        aud_caption = caption or self._get_config_value('status_text', 'STATUS_TEXT')

        message_id = await self.api.send_audio(
            chat_id=self.telegram_chat_id,
            audio_url=aud_url,
            caption=aud_caption,
            parse_mode=self.telegram_parse_mode,
            duration=duration,
            performer=performer,
            title=title
        )

        self._output_status(message_id)
        return message_id


async def main_async(kwargs):
    """
    Async main function to execute Telegram actions.

    Args:
        kwargs (dict): Configuration arguments
    """
    action = kwargs.get('action', '')

    if action == '':
        raise Exception('Action is a required argument.')

    # Create Telegram instance with configuration
    instance = Telegram(**kwargs)
    # Execute the action using the base class method
    await instance.execute_action(action)
    await instance.disconnect()


def main(kwargs):
    """
    Main function to execute Telegram actions.

    Args:
        kwargs (dict): Configuration arguments
    """
    asyncio.run(main_async(kwargs))
