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
from typing import Any, Dict, List, Optional

from agoras.core.api_base import BaseAPI

from .auth import TelegramAuthManager


class TelegramAPI(BaseAPI):
    """
    Telegram API handler that centralizes Telegram operations.

    Provides methods for Telegram authentication, message sending,
    media posting, and all Telegram Bot API operations.
    """

    def __init__(self, bot_token: str, chat_id: Optional[str] = None):
        """
        Initialize Telegram API instance.

        Args:
            bot_token (str): Telegram bot token from @BotFather
            chat_id (str, optional): Target chat ID (user, group, or channel)
        """
        super().__init__(bot_token=bot_token, chat_id=chat_id)

        # Initialize the authentication manager
        self.auth_manager = TelegramAuthManager(bot_token=bot_token, chat_id=chat_id)
        self.chat_id = chat_id

    @property
    def bot_token(self):
        """Get the Telegram bot token from the auth manager."""
        return self.auth_manager.bot_token if self.auth_manager else None

    @property
    def user_info(self):
        """Get the Telegram bot info from the auth manager."""
        return self.auth_manager.user_info if self.auth_manager else None

    async def authenticate(self):
        """
        Authenticate with Telegram API using the auth manager.

        Returns:
            TelegramAPI: Self for method chaining

        Raises:
            Exception: If authentication fails
        """
        if self._authenticated:
            return self

        # Authenticate with auth manager (this creates and sets up the client)
        auth_success = await self.auth_manager.authenticate()
        if not auth_success:
            raise Exception('Telegram authentication failed')

        # Ensure client was created during authentication
        if not self.auth_manager.client:
            raise Exception('Telegram client not available after authentication')

        self.client = self.auth_manager.client
        self._authenticated = True
        return self

    async def disconnect(self):
        """
        Disconnect from Telegram API and clean up resources.
        """
        # Clear auth manager data
        if self.auth_manager:
            self.auth_manager.access_token = None
            self.auth_manager.user_info = None
            self.auth_manager.client = None

        # Clear BaseAPI client
        self.client = None
        self._authenticated = False

    async def get_bot_info(self) -> Dict[str, Any]:
        """
        Get information about the bot.

        Returns:
            dict: Bot information

        Raises:
            Exception: If API call fails
        """
        if not self._authenticated:
            await self.authenticate()

        if not self.client:
            raise Exception('Telegram client not available')

        try:
            return await self.client.get_me()
        except Exception as e:
            self._handle_api_error(e, 'Telegram get bot info')
            raise

    async def send_message(self, chat_id: str, text: str,
                           parse_mode: Optional[str] = None) -> str:
        """
        Send text message asynchronously.

        Args:
            chat_id (str): Target chat ID (user, group, or channel)
            text (str): Message text
            parse_mode (str, optional): Parse mode (HTML, Markdown, MarkdownV2)

        Returns:
            str: Message ID

        Raises:
            Exception: If message sending fails
        """
        if not self._authenticated:
            await self.authenticate()

        if not self.client:
            raise Exception('Telegram client not available')

        await self._rate_limit_check('send_message', 1.0)

        try:
            response = await self.client.send_message(
                chat_id=chat_id,
                text=text,
                parse_mode=parse_mode
            )
            return str(response['message_id'])
        except Exception as e:
            self._handle_api_error(e, 'Telegram send message')
            raise

    async def send_photo(self, chat_id: str, photo_url: Optional[str] = None,
                         photo_content: Optional[bytes] = None,
                         caption: Optional[str] = None,
                         parse_mode: Optional[str] = None) -> str:
        """
        Send photo with Media system integration.

        Args:
            chat_id (str): Target chat ID (user, group, or channel)
            photo_url (str, optional): URL to download image from (uses Media system)
            photo_content (bytes, optional): Direct bytes content (bypasses Media system)
            caption (str, optional): Photo caption
            parse_mode (str, optional): Parse mode for caption

        Returns:
            str: Message ID

        Raises:
            Exception: If photo sending fails
        """
        if not self._authenticated:
            await self.authenticate()

        if not self.client:
            raise Exception('Telegram client not available')

        await self._rate_limit_check('send_photo', 1.0)

        # If URL provided, download using Media system
        if photo_url:
            from agoras.media import MediaFactory
            images = await MediaFactory.download_images([photo_url])
            try:
                if images and len(images) > 0:
                    image = images[0]
                    if image.content and image.file_type:
                        photo_content = image.content
                    else:
                        raise Exception(f'Failed to validate image: {image.url}')
                else:
                    raise Exception('Failed to download image')
            finally:
                for image in images:
                    image.cleanup()

        if not photo_content:
            raise Exception('No photo content available')

        try:
            response = await self.client.send_photo(
                chat_id=chat_id,
                photo=photo_content,
                caption=caption,
                parse_mode=parse_mode
            )
            return str(response['message_id'])
        except Exception as e:
            self._handle_api_error(e, 'Telegram send photo')
            raise

    async def send_video(self, chat_id: str, video_url: Optional[str] = None,
                         video_content: Optional[bytes] = None,
                         caption: Optional[str] = None,
                         parse_mode: Optional[str] = None) -> str:
        """
        Send video with Media system integration.

        Args:
            chat_id (str): Target chat ID (user, group, or channel)
            video_url (str, optional): URL to download video from (uses Media system)
            video_content (bytes, optional): Direct bytes content (bypasses Media system)
            caption (str, optional): Video caption
            parse_mode (str, optional): Parse mode for caption

        Returns:
            str: Message ID

        Raises:
            Exception: If video sending fails
        """
        if not self._authenticated:
            await self.authenticate()

        if not self.client:
            raise Exception('Telegram client not available')

        await self._rate_limit_check('send_video', 1.0)

        # If URL provided, download using Media system
        if video_url:
            from agoras.media import MediaFactory
            video = MediaFactory.create_video(video_url, platform='telegram')
            try:
                await video.download()
                if video.content and video.file_type:
                    video_content = video.content
                else:
                    raise Exception(f'Failed to validate video: {video.url}')
            finally:
                video.cleanup()

        if not video_content:
            raise Exception('No video content available')

        try:
            response = await self.client.send_video(
                chat_id=chat_id,
                video=video_content,
                caption=caption,
                parse_mode=parse_mode
            )
            return str(response['message_id'])
        except Exception as e:
            self._handle_api_error(e, 'Telegram send video')
            raise

    async def delete_message(self, chat_id: str, message_id: int) -> str:
        """
        Delete a message.

        Args:
            chat_id (str): Chat ID where the message is located
            message_id (int): ID of the message to delete

        Returns:
            str: Message ID

        Raises:
            Exception: If message deletion fails
        """
        if not self._authenticated:
            await self.authenticate()

        if not self.client:
            raise Exception('Telegram client not available')

        await self._rate_limit_check('delete_message', 0.5)

        try:
            await self.client.delete_message(chat_id=chat_id, message_id=int(message_id))
            return str(message_id)
        except Exception as e:
            self._handle_api_error(e, 'Telegram delete message')
            raise

    async def post(self, *args, **kwargs) -> str:
        """
        Create a post on Telegram (text message).

        Args:
            *args: Positional arguments (not used)
            **kwargs: Keyword arguments
                - chat_id (str): Target chat ID
                - text (str): Message text
                - parse_mode (str, optional): Parse mode

        Returns:
            str: Message ID

        Raises:
            Exception: If posting fails
        """
        chat_id = kwargs.get('chat_id', self.chat_id)
        text = kwargs.get('text', '')

        if not chat_id:
            raise Exception('Telegram chat_id is required for posting')
        if not text:
            raise Exception('Telegram text is required for posting')

        return await self.send_message(
            chat_id=chat_id,
            text=text,
            parse_mode=kwargs.get('parse_mode')
        )

    async def like(self, post_id: str, *args, **kwargs) -> str:
        """
        Like is not supported for Telegram.

        Args:
            post_id (str): Post ID

        Raises:
            Exception: Like not supported for Telegram
        """
        raise Exception('Like not supported for Telegram')

    async def delete(self, post_id: str, *args, **kwargs) -> str:
        """
        Delete a Telegram message.

        Args:
            post_id (str): Message ID to delete
            **kwargs: Keyword arguments
                - chat_id (str): Chat ID where the message is located

        Returns:
            str: Message ID

        Raises:
            Exception: If deletion fails
        """
        chat_id = kwargs.get('chat_id', self.chat_id)
        if not chat_id:
            raise Exception('Telegram chat_id is required for deletion')

        try:
            message_id = int(post_id)
        except ValueError:
            raise Exception(f'Invalid message ID: {post_id}')

        return await self.delete_message(chat_id=chat_id, message_id=message_id)

    async def share(self, post_id: str, *args, **kwargs) -> str:
        """
        Share is not supported for Telegram.

        Args:
            post_id (str): Post ID

        Raises:
            Exception: Share not supported for Telegram
        """
        raise Exception('Share not supported for Telegram')

    async def send_media_group(self, chat_id: str, media: List[Dict[str, Any]]) -> List[str]:
        """
        Send multiple media items as an album (media group).

        Args:
            chat_id (str): Target chat ID (user, group, or channel)
            media (List[Dict]): List of media items, each with 'type' and 'media' keys

        Returns:
            List[str]: List of message IDs for each media item

        Raises:
            Exception: If media group sending fails
        """
        if not self._authenticated:
            await self.authenticate()

        if not self.client:
            raise Exception('Telegram client not available')

        await self._rate_limit_check('send_media_group', 1.0)

        try:
            response = await self.client.send_media_group(
                chat_id=chat_id,
                media=media
            )
            # Return list of message IDs
            return [str(msg['message_id']) for msg in response]
        except Exception as e:
            self._handle_api_error(e, 'Telegram send media group')
            raise
