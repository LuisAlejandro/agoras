# -*- coding: utf-8 -*-
#
# Please refer to AUTHORS.md for a complete list of Copyright holders.
# Copyright (C) 2022-2023, Agoras Developers.

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import asyncio
from typing import Any, Dict, Optional

from telegram import Bot
from telegram.error import TelegramError

from agoras.core.auth import BaseAuthManager
from .client import TelegramAPIClient


class TelegramAuthManager(BaseAuthManager):
    """Telegram authentication manager using bot token authentication."""

    def __init__(self, bot_token: str, chat_id: Optional[str] = None):
        """
        Initialize Telegram authentication manager.

        Args:
            bot_token (str): Telegram bot token from @BotFather
            chat_id (str, optional): Target chat ID (user, group, or channel)
        """
        super().__init__()
        self.bot_token = bot_token
        self.chat_id = chat_id

    async def authenticate(self) -> bool:
        """
        Authenticate with Telegram API using bot token.

        Validates bot token and retrieves bot information.

        Returns:
            bool: True if authentication successful, False otherwise
        """
        if not self._validate_credentials():
            return False

        try:
            # Validate bot token by getting bot info
            success = await self._validate_bot_token()
            if success:
                # Set access token to bot token for consistency with other auth managers
                self.access_token = self.bot_token

                # Create Telegram client
                self.client = self._create_client(self.access_token)

                # Get bot information
                self.user_info = await self._get_user_info()

                return True
            return False
        except Exception:
            return False

    async def authorize(self) -> Optional[str]:
        """
        Telegram doesn't use OAuth authorization - bot tokens are provided directly.
        This method validates the bot token and returns it if valid.

        Returns:
            str: The bot token if valid, None otherwise
        """
        if not self._validate_credentials():
            raise Exception('Telegram bot token is required.')

        try:
            if await self._validate_bot_token():
                return self.bot_token
            return None
        except Exception:
            return None

    async def _validate_bot_token(self) -> bool:
        """
        Validate Telegram bot token by calling getMe API.

        Returns:
            bool: True if token is valid, False otherwise
        """
        def _sync_validate():
            try:
                bot = Bot(token=self.bot_token)
                # Use synchronous get_me() method
                bot_info = bot.get_me()
                return {
                    'success': True,
                    'bot_info': {
                        'id': bot_info.id,
                        'username': bot_info.username,
                        'first_name': bot_info.first_name,
                        'is_bot': bot_info.is_bot
                    }
                }
            except TelegramError as e:
                return {
                    'success': False,
                    'error': str(e)
                }
            except Exception as e:
                return {
                    'success': False,
                    'error': str(e)
                }

        try:
            result = await asyncio.to_thread(_sync_validate)
            if result['success']:
                # Store bot info for later use
                self._cached_bot_info = result['bot_info']
                return True
            return False
        except Exception:
            return False

    def _create_client(self, access_token: str) -> TelegramAPIClient:
        """Create Telegram API client instance."""
        return TelegramAPIClient(bot_token=access_token)

    async def _get_user_info(self) -> Dict[str, Any]:
        """Get bot information from Telegram API."""
        def _sync_get_info():
            # Return cached bot info from validation if available
            if hasattr(self, '_cached_bot_info') and self._cached_bot_info:
                return {
                    'bot_token': self.bot_token[:20] + '...',  # Partial token for security
                    'chat_id': self.chat_id,
                    'bot_info': self._cached_bot_info
                }

            # Fallback: try to get info from client if available
            if self.client:
                try:
                    bot_info = self.client.get_me()
                    return {
                        'bot_token': self.bot_token[:20] + '...',
                        'chat_id': self.chat_id,
                        'bot_info': bot_info
                    }
                except Exception:
                    pass

            # Fallback to basic info if no cached validation
            return {
                'bot_token': self.bot_token[:20] + '...',
                'chat_id': self.chat_id,
                'bot_info': None
            }

        return await asyncio.to_thread(_sync_get_info)

    def _validate_credentials(self) -> bool:
        """Validate that all required credentials are present."""
        return bool(self.bot_token)

    def _get_cache_filename(self) -> str:
        """Get cache filename for storing validation results."""
        # Use bot username if available, otherwise use token hash
        if hasattr(self, '_cached_bot_info') and self._cached_bot_info:
            username = self._cached_bot_info.get('username', 'unknown')
            return f'telegram-{username}.json'
        return 'telegram-bot.json'

    def _get_platform_name(self) -> str:
        """Get the platform name for this auth manager."""
        return 'telegram'

    def _get_token_identifier(self) -> str:
        """Get unique identifier for token storage."""
        # Use bot username if available, otherwise use token hash
        if hasattr(self, '_cached_bot_info') and self._cached_bot_info:
            username = self._cached_bot_info.get('username')
            if username:
                return username
        # Fallback to token hash
        return str(hash(self.bot_token))
