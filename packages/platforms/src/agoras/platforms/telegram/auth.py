# -*- coding: utf-8 -*-
#
# Please refer to AUTHORS.md for a complete list of Copyright holders.
# Copyright (C) 2022-2026, Agoras Developers.

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""agoras.platforms.telegram.auth module."""

import asyncio
import os
import sys
from typing import Any, Dict, Optional

from telegram import Bot
from telegram.error import TelegramError

from agoras.core.auth import BaseAuthManager

from .client import TelegramAPIClient


def normalize_chat_id(chat_id: Optional[str]) -> Optional[str]:
    """
    Normalize a Telegram chat identifier.

    Strips whitespace and ensures public channel usernames include a leading @.
    Numeric IDs (including negative group/channel IDs) are left unchanged.
    """
    if chat_id is None:
        return None

    normalized = chat_id.strip()
    if not normalized:
        return None

    if normalized.lstrip("-").isdigit():
        return normalized

    if not normalized.startswith("@"):
        return f"@{normalized}"

    return normalized


class TelegramAuthManager(BaseAuthManager):
    """Telegram authentication manager using bot token authentication."""

    client: Optional[TelegramAPIClient] = None
    user_info: Optional[Dict[str, Any]] = None

    def __init__(self, bot_token: Optional[str] = None, chat_id: Optional[str] = None):
        """
        Initialize Telegram authentication manager.

        Args:
            bot_token (str, optional): Telegram bot token from @BotFather
            chat_id (str, optional): Target chat ID (user, group, or channel)
        """
        super().__init__()
        # Try loading from storage first if credentials not provided
        if not bot_token:
            loaded = self._load_credentials_from_storage()
            if loaded:
                if not bot_token:
                    bot_token = getattr(self, "bot_token", None)
                if not chat_id:
                    chat_id = getattr(self, "chat_id", None)

        self.bot_token = bot_token
        self.chat_id = normalize_chat_id(chat_id)

    async def authenticate(self) -> bool:
        """
        Authenticate with Telegram API using bot token.

        Validates bot token and retrieves bot information.

        Returns:
            bool: True if authentication successful, False otherwise
        """
        self.last_auth_failure = None
        if not self._validate_credentials():
            return self._missing_credentials_failed()

        try:
            # Validate bot token by getting bot info
            success = await self._validate_bot_token()
            if success:
                # Set access token to bot token for consistency with other auth managers
                self.access_token = self.bot_token

                # Create Telegram client
                self.client = self._create_client(self._require_bot_token())

                # Get bot information
                self.user_info = await self._get_user_info()

                return True
            return self._wrong_token_failed()
        except Exception as exc:
            return self._authentication_failed(exc)

    def _has_stored_or_env_credentials(self) -> bool:
        if getattr(self, "bot_token", None):
            return True
        return bool(__import__("os").environ.get("TELEGRAM_BOT_TOKEN"))

    async def authorize(self) -> Optional[str]:
        """
        Authorize Telegram by validating and storing bot token credentials.

        Accepts credentials from parameters or environment variables, validates them,
        and stores them securely for future use.

        Returns:
            str: Success message if authorization successful, None otherwise
        """
        # Get credentials from parameters or environment variables
        bot_token = self.bot_token or os.environ.get("TELEGRAM_BOT_TOKEN")
        chat_id = normalize_chat_id(self.chat_id or os.environ.get("TELEGRAM_CHAT_ID"))

        if not bot_token:
            raise Exception(
                "Telegram bot token is required. Provide via parameter or environment variable (TELEGRAM_BOT_TOKEN)."
            )

        if not chat_id:
            raise Exception(
                "Telegram chat ID is required. Provide via parameter or environment variable (TELEGRAM_CHAT_ID)."
            )

        # Set credentials for validation
        self.bot_token = bot_token
        self.chat_id = chat_id

        # Validate credentials
        if not await self._validate_bot_token():
            raise Exception("Telegram bot token validation failed. Please check your credentials.")

        await self._validate_chat_id()

        # Save credentials to secure storage
        self._save_credentials_to_storage(bot_token, chat_id)

        return "Authorization successful. Credentials stored securely."

    async def _validate_chat_id(self) -> None:
        """
        Validate that the bot can access the configured chat.

        Raises:
            Exception: If chat ID is invalid or the bot cannot access the chat
        """
        if not self.chat_id:
            raise Exception("Telegram chat ID is required.")

        try:
            bot = Bot(token=self._require_bot_token())
            await bot.get_chat(self.chat_id)
        except TelegramError as e:
            error_text = str(e)
            if "Chat not found" in error_text:
                raise Exception(
                    "Telegram chat ID validation failed: chat not found. "
                    "For private chats, open the bot in Telegram and send /start first. "
                    "For groups or channels, add the bot as a member/admin and use the "
                    "numeric chat ID (groups/channels are usually negative, e.g. -100...)."
                ) from e
            raise Exception(f"Telegram chat ID validation failed: {error_text}") from e
        except Exception as e:
            raise Exception(f"Telegram chat ID validation failed: {e}") from e

    async def _validate_bot_token(self) -> bool:
        """
        Validate Telegram bot token by calling getMe API.

        Returns:
            bool: True if token is valid, False otherwise
        """
        try:
            bot = Bot(token=self._require_bot_token())
            # get_me() is an async coroutine, so we need to await it
            bot_info = await bot.get_me()
            # Store bot info for later use
            self._cached_bot_info = {
                "id": bot_info.id,
                "username": bot_info.username,
                "first_name": bot_info.first_name,
                "is_bot": bot_info.is_bot,
            }
            return True
        except TelegramError as e:
            print(f"Telegram API error during validation: {e}", file=sys.stderr)
            return False
        except Exception as e:
            print(f"Unexpected error during bot token validation: {e}", file=sys.stderr)
            return False

    def _create_client(self, access_token: str) -> TelegramAPIClient:
        """Create Telegram API client instance."""
        return TelegramAPIClient(bot_token=access_token)

    async def _get_user_info(self) -> Dict[str, Any]:
        """Get bot information from Telegram API."""

        def _sync_get_info():
            bot_token = self._require_bot_token()
            # Return cached bot info from validation if available
            if hasattr(self, "_cached_bot_info") and self._cached_bot_info:
                return {
                    "bot_token": bot_token[:20] + "...",  # Partial token for security
                    "chat_id": self.chat_id,
                    "bot_info": self._cached_bot_info,
                }

            # Fallback: try to get info from client if available
            if self.client:
                try:
                    bot_info = self.client.get_me()
                    return {"bot_token": bot_token[:20] + "...", "chat_id": self.chat_id, "bot_info": bot_info}
                except Exception:
                    pass

            # Fallback to basic info if no cached validation
            return {"bot_token": bot_token[:20] + "...", "chat_id": self.chat_id, "bot_info": None}

        return await asyncio.to_thread(_sync_get_info)

    def _require_bot_token(self) -> str:
        if not self.bot_token:
            raise ValueError("Telegram bot token is required")
        return self.bot_token

    def _validate_credentials(self) -> bool:
        """Validate that all required credentials are present."""
        return bool(self.bot_token)

    def _get_platform_name(self) -> str:
        """Get the platform name for this auth manager."""
        return "telegram"

    def _get_token_identifier(self) -> str:
        """Get unique identifier for token storage."""
        # Use bot username if available, otherwise use token hash
        if hasattr(self, "_cached_bot_info") and self._cached_bot_info:
            username = self._cached_bot_info.get("username")
            if username:
                return username
        # Fallback to token hash if bot_token exists
        if self.bot_token:
            return str(hash(self.bot_token))
        return "default"

    def _save_credentials_to_storage(self, bot_token: str, chat_id: Optional[str] = None):
        """
        Save Telegram credentials to secure storage.

        Args:
            bot_token (str): Telegram bot token
            chat_id (str, optional): Telegram chat ID
        """
        platform_name = self._get_platform_name()

        # Use bot username as identifier if available, otherwise use token hash
        identifier = self._get_token_identifier()
        if identifier == "default" and self.bot_token:
            identifier = str(hash(bot_token))

        token_data = {"bot_token": bot_token, "chat_id": chat_id}

        self.token_storage.save_token(platform_name, identifier, token_data)
        # Also save as default so it becomes the primary credential loaded
        self.token_storage.save_token(platform_name, "default", token_data)

    def _load_credentials_from_storage(self) -> bool:
        """
        Load Telegram credentials from secure storage.

        Returns:
            bool: True if credentials were loaded, False otherwise
        """
        platform_name = self._get_platform_name()

        # Try to load with default identifier first
        identifier = "default"
        token_data = self.token_storage.load_token(platform_name, identifier)

        if not token_data:
            # If no default, try to find any stored token
            tokens = self.token_storage.list_tokens(platform_name)
            if tokens:
                # Use the first available token
                identifier = tokens[0][1]
                token_data = self.token_storage.load_token(platform_name, identifier)

        if token_data:
            self.bot_token = token_data.get("bot_token")
            self.chat_id = normalize_chat_id(token_data.get("chat_id"))
            return bool(self.bot_token)

        return False
