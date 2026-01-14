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
import os
from typing import Optional

import discord

from agoras.core.auth import BaseAuthManager
from agoras.core.auth.exceptions import AuthenticationError

from .client import DiscordAPIClient


class DiscordAuthManager(BaseAuthManager):
    """Discord authentication manager using bot token authentication."""

    def __init__(
            self,
            bot_token: Optional[str] = None,
            server_name: Optional[str] = None,
            channel_name: Optional[str] = None):
        """
        Initialize Discord authentication manager.

        Args:
            bot_token (str, optional): Discord bot token
            server_name (str, optional): Discord server/guild name
            channel_name (str, optional): Discord channel name
        """
        super().__init__()
        # Try loading from storage first if credentials not provided
        if not bot_token or not server_name or not channel_name:
            loaded = self._load_credentials_from_storage()
            if loaded:
                # Use loaded credentials if available
                if not bot_token:
                    bot_token = getattr(self, 'bot_token', None)
                if not server_name:
                    server_name = getattr(self, 'server_name', None)
                if not channel_name:
                    channel_name = getattr(self, 'channel_name', None)

        self.bot_token = bot_token
        self.server_name = server_name
        self.channel_name = channel_name

        # Load cached bot token validation if available
        self._load_cached_validation()

    async def authenticate(self) -> bool:
        """
        Authenticate with Discord API using bot token.

        Validates bot token and verifies access to specified server and channel.

        Returns:
            bool: True if authentication successful, False otherwise
        """
        if not self._validate_credentials():
            return False

        # For Discord, we need to validate the bot token by connecting
        try:
            success = await self._validate_bot_token()
            if success:
                # Set access token to bot token for consistency with other auth managers
                self.access_token = self.bot_token

                # Create Discord client
                self.client = self._create_client(self.access_token)

                # Get user info (including bot, guild, and channel details)
                self.user_info = await self._get_user_info()

                # Cache successful validation
                self._save_validation_cache()

                return True
            return False
        except Exception:
            return False

    async def authorize(self) -> Optional[str]:
        """
        Authorize Discord by validating and storing bot token credentials.

        Accepts credentials from parameters or environment variables, validates them,
        and stores them securely for future use.

        Returns:
            str: Success message if authorization successful, None otherwise
        """
        # Get credentials from parameters or environment variables
        bot_token = self.bot_token or os.environ.get('DISCORD_BOT_TOKEN')
        server_name = self.server_name or os.environ.get('DISCORD_SERVER_NAME')
        channel_name = self.channel_name or os.environ.get('DISCORD_CHANNEL_NAME')

        if not bot_token or not server_name or not channel_name:
            raise Exception('Discord bot token, server name, and channel name are required. '
                            'Provide via parameters or environment variables (DISCORD_BOT_TOKEN, '
                            'DISCORD_SERVER_NAME, DISCORD_CHANNEL_NAME).')

        # Set credentials for validation
        self.bot_token = bot_token
        self.server_name = server_name
        self.channel_name = channel_name

        # Validate credentials
        if not await self._validate_bot_token():
            raise Exception('Discord bot token validation failed. Please check your credentials.')

        # Save credentials to secure storage
        self._save_credentials_to_storage(bot_token, server_name, channel_name)
        self._save_validation_cache()

        return "Authorization successful. Credentials stored securely."

    async def _validate_bot_token(self) -> bool:
        """
        Validate Discord bot token by attempting to connect and find server/channel.

        Returns:
            bool: True if token is valid and server/channel accessible
        """
        def _sync_validate():
            client = discord.Client(intents=discord.Intents.default())
            validation_result = {'success': False, 'user_info': None}

            @client.event
            async def on_ready():
                try:
                    # Find the guild (server)
                    guild = self._find_guild(client)

                    # Find the channel within the guild
                    channel = self._find_channel(guild)

                    # Collect validation info
                    bot_user_info = None
                    if client.user:
                        bot_user_info = {
                            'id': str(client.user.id),
                            'name': client.user.name,
                            'discriminator': (client.user.discriminator
                                              if hasattr(client.user, 'discriminator')
                                              else None)
                        }

                    validation_result['user_info'] = {
                        'bot_token': self.bot_token[:20] + '...',  # Partial token for security
                        'server_name': self.server_name,
                        'channel_name': self.channel_name,
                        'bot_user': bot_user_info,
                        'guild': {
                            'id': str(guild.id),
                            'name': guild.name,
                            'member_count': guild.member_count
                        },
                        'channel': {
                            'id': str(channel.id),
                            'name': channel.name,
                            'type': str(channel.type)
                        }
                    }
                    validation_result['success'] = True
                except Exception as e:
                    print(f"Discord validation failed: {e}")
                    validation_result['success'] = False
                finally:
                    await client.close()

            # Run the Discord client
            asyncio.create_task(client.start(self.bot_token))
            return validation_result

        try:
            result = await asyncio.to_thread(_sync_validate)
            if result['success']:
                # Store the user info for later use
                self._cached_user_info = result['user_info']
                return True
            return False
        except Exception as e:
            print(f"Discord connection failed: {e}")
            return False

    def _find_guild(self, client: discord.Client) -> discord.Guild:
        """Find guild by name."""
        for guild in client.guilds:
            if guild.name == self.server_name:
                return guild
        raise Exception(f'Guild "{self.server_name}" not found')

    def _find_channel(self, guild: discord.Guild) -> discord.TextChannel:
        """Find text channel by name in guild."""
        for channel in guild.text_channels:
            if channel.name == self.channel_name:
                return channel
        raise Exception(f'Channel "{self.channel_name}" not found in guild "{self.server_name}"')

    def _create_client(self, access_token: str) -> DiscordAPIClient:
        """Create Discord API client instance."""
        return DiscordAPIClient(
            bot_token=access_token,
            server_name=self.server_name,
            channel_name=self.channel_name
        )

    async def _get_user_info(self) -> dict:
        """Get bot and server information from Discord API."""
        def _sync_get_info():
            # Return cached user info from validation if available
            if hasattr(self, '_cached_user_info') and self._cached_user_info:
                return self._cached_user_info

            # Fallback to basic info if no cached validation
            return {
                'bot_token': self.bot_token[:20] + '...',  # Partial token for security
                'server_name': self.server_name,
                'channel_name': self.channel_name,
                'bot_user': None,
                'guild': None,
                'channel': None
            }

        return await asyncio.to_thread(_sync_get_info)

    def _validate_credentials(self) -> bool:
        """Validate that all required credentials are present."""
        return all([self.bot_token, self.server_name, self.channel_name])

    def _get_cache_filename(self) -> str:
        """Get cache filename for storing validation results."""
        if self.server_name and self.channel_name:
            return f'discord-{self.server_name}-{self.channel_name}.json'
        return 'discord-bot.json'

    def _get_platform_name(self) -> str:
        """Get the platform name for this auth manager."""
        return 'discord'

    def _get_token_identifier(self) -> str:
        """Get unique identifier for token storage."""
        if self.server_name and self.channel_name:
            return f"{self.server_name}-{self.channel_name}"
        return "default"

    def _save_credentials_to_storage(self, bot_token: str, server_name: str, channel_name: str):
        """
        Save Discord credentials to secure storage.

        Args:
            bot_token (str): Discord bot token
            server_name (str): Discord server name
            channel_name (str): Discord channel name
        """
        platform_name = self._get_platform_name()
        identifier = f"{server_name}-{channel_name}"

        token_data = {
            'bot_token': bot_token,
            'server_name': server_name,
            'channel_name': channel_name
        }

        self.token_storage.save_token(platform_name, identifier, token_data)

    def _load_credentials_from_storage(self) -> bool:
        """
        Load Discord credentials from secure storage.

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
            self.bot_token = token_data.get('bot_token')
            self.server_name = token_data.get('server_name')
            self.channel_name = token_data.get('channel_name')
            return bool(self.bot_token and self.server_name and self.channel_name)

        return False

    def _load_cached_validation(self):
        """Load cached validation data if available."""
        cache_file = self._get_cache_filename()
        cache_data = self._load_cache_data(cache_file)
        # Only load if the bot token matches (for security)
        if cache_data.get('bot_token_hash') == hash(self.bot_token):
            self._cached_user_info = cache_data.get('user_info')

    def _save_validation_cache(self):
        """Save validation results to cache."""
        if hasattr(self, '_cached_user_info') and self._cached_user_info:
            cache_file = self._get_cache_filename()
            data = {
                'bot_token_hash': hash(self.bot_token),  # For validation without storing actual token
                'user_info': self._cached_user_info
            }
            self._save_cache_data(cache_file, data)
