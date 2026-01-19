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

from typing import Any, Dict, List, Optional

from telegram import Bot
from telegram.constants import ParseMode
from telegram.error import TelegramError


class TelegramAPIClient:
    """
    Telegram API client for making requests to Telegram Bot API.

    Centralizes all Telegram API calls using python-telegram-bot library.
    """

    def __init__(self, bot_token: str):
        """
        Initialize Telegram API client.

        Args:
            bot_token (str): Telegram bot token from @BotFather
        """
        self.bot_token = bot_token
        self.bot = Bot(token=bot_token)
        self.default_parse_mode = ParseMode.HTML

    async def get_me(self) -> Dict[str, Any]:
        """
        Get bot information from Telegram API.

        Returns:
            dict: Bot information including id, username, first_name, is_bot

        Raises:
            Exception: If API call fails or not authenticated
        """
        if not self.bot_token:
            raise Exception('No bot token available')

        try:
            bot_info = await self.bot.get_me()
            return {
                'id': bot_info.id,
                'username': bot_info.username,
                'first_name': bot_info.first_name,
                'is_bot': bot_info.is_bot,
                'can_join_groups': getattr(bot_info, 'can_join_groups', None),
                'can_read_all_group_messages': getattr(bot_info, 'can_read_all_group_messages', None),
                'supports_inline_queries': getattr(bot_info, 'supports_inline_queries', None)
            }
        except TelegramError as e:
            raise Exception(f"Failed to get bot info: {e}") from e
        except Exception as e:
            raise Exception(f"Unexpected error getting bot info: {e}") from e

    async def send_message(self, chat_id: str, text: str,
                           parse_mode: Optional[str] = None,
                           reply_markup=None) -> Dict[str, Any]:
        """
        Send text message with optional formatting and keyboards.

        Args:
            chat_id (str): Target chat ID (user, group, or channel)
            text (str): Message text
            parse_mode (str, optional): Parse mode (HTML, Markdown, MarkdownV2)
            reply_markup: Inline keyboard or reply keyboard markup

        Returns:
            dict: Message data including message_id

        Raises:
            Exception: If message sending fails
        """
        if not self.bot_token:
            raise Exception('No bot token available')

        try:
            message = await self.bot.send_message(
                chat_id=chat_id,
                text=text,
                parse_mode=parse_mode or self.default_parse_mode,
                reply_markup=reply_markup
            )
            return message.to_dict()
        except TelegramError as e:
            raise Exception(f"Failed to send message: {e}") from e
        except Exception as e:
            raise Exception(f"Unexpected error sending message: {e}") from e

    async def send_photo(self, chat_id: str, photo, caption: Optional[str] = None,
                         parse_mode: Optional[str] = None) -> Dict[str, Any]:
        """
        Send photo with optional caption.

        Args:
            chat_id (str): Target chat ID (user, group, or channel)
            photo: Photo to send (file-like object, bytes, file path, or URL)
            caption (str, optional): Photo caption (up to 1024 characters)
            parse_mode (str, optional): Parse mode for caption (HTML, Markdown, MarkdownV2)

        Returns:
            dict: Message data including message_id

        Raises:
            Exception: If photo sending fails
        """
        if not self.bot_token:
            raise Exception('No bot token available')

        try:
            message = await self.bot.send_photo(
                chat_id=chat_id,
                photo=photo,
                caption=caption,
                parse_mode=parse_mode or self.default_parse_mode
            )
            return message.to_dict()
        except TelegramError as e:
            raise Exception(f"Failed to send photo: {e}") from e
        except Exception as e:
            raise Exception(f"Unexpected error sending photo: {e}") from e

    async def send_video(self, chat_id: str, video, caption: Optional[str] = None,
                         parse_mode: Optional[str] = None,
                         duration: Optional[int] = None,
                         width: Optional[int] = None,
                         height: Optional[int] = None) -> Dict[str, Any]:
        """
        Send video with optional caption.

        Args:
            chat_id (str): Target chat ID (user, group, or channel)
            video: Video to send (file-like object, bytes, file path, or URL)
            caption (str, optional): Video caption (up to 1024 characters)
            parse_mode (str, optional): Parse mode for caption (HTML, Markdown, MarkdownV2)
            duration (int, optional): Video duration in seconds
            width (int, optional): Video width
            height (int, optional): Video height

        Returns:
            dict: Message data including message_id

        Raises:
            Exception: If video sending fails
        """
        if not self.bot_token:
            raise Exception('No bot token available')

        try:
            message = await self.bot.send_video(
                chat_id=chat_id,
                video=video,
                caption=caption,
                parse_mode=parse_mode or self.default_parse_mode,
                duration=duration,
                width=width,
                height=height
            )
            return message.to_dict()
        except TelegramError as e:
            raise Exception(f"Failed to send video: {e}") from e
        except Exception as e:
            raise Exception(f"Unexpected error sending video: {e}") from e

    async def delete_message(self, chat_id: str, message_id: int) -> bool:
        """
        Delete a message.

        Args:
            chat_id (str): Chat ID where the message is located
            message_id (int): ID of the message to delete

        Returns:
            bool: True if message was deleted successfully

        Raises:
            Exception: If message deletion fails
        """
        if not self.bot_token:
            raise Exception('No bot token available')

        try:
            return await self.bot.delete_message(chat_id=chat_id, message_id=message_id)
        except TelegramError as e:
            raise Exception(f"Failed to delete message: {e}") from e
        except Exception as e:
            raise Exception(f"Unexpected error deleting message: {e}") from e

    async def send_media_group(self, chat_id: str, media: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Send multiple photos/videos as an album (media group).

        Args:
            chat_id (str): Target chat ID (user, group, or channel)
            media (List[Dict]): List of media items, each with 'type' and 'media' keys
                Example: [
                    {'type': 'photo', 'media': photo_bytes, 'caption': 'First image'},
                    {'type': 'photo', 'media': photo_bytes2}
                ]

        Returns:
            List[dict]: List of message data for each media item

        Raises:
            Exception: If media group sending fails
        """
        if not self.bot_token:
            raise Exception('No bot token available')

        from telegram import InputMediaPhoto, InputMediaVideo

        try:
            # Convert media dicts to InputMedia objects
            input_media = []
            for item in media:
                media_type = item.get('type', 'photo')
                media_content = item.get('media')
                caption = item.get('caption')

                if media_type == 'photo':
                    input_media.append(InputMediaPhoto(media=media_content, caption=caption))
                elif media_type == 'video':
                    input_media.append(InputMediaVideo(media=media_content, caption=caption))
                else:
                    raise Exception(f'Unsupported media type: {media_type}')

            # Send media group (all items must be same type: all photos or all videos)
            messages = await self.bot.send_media_group(
                chat_id=chat_id,
                media=input_media
            )

            # Return list of message dicts
            return [msg.to_dict() for msg in messages]
        except TelegramError as e:
            raise Exception(f"Failed to send media group: {e}") from e
        except Exception as e:
            raise Exception(f"Unexpected error sending media group: {e}") from e
