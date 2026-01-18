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
from typing import Any, List, Optional

import discord


class DiscordAPIClient:
    """
    Discord API client that centralizes Discord operations.

    Handles all Discord API interactions including authentication, guild/channel management,
    message operations, and file uploads.
    """

    def __init__(self, bot_token: str, server_name: str, channel_name: str):
        """
        Initialize Discord API client.

        Args:
            bot_token (str): Discord bot token
            server_name (str): Discord server name
            channel_name (str): Discord channel name
        """
        self.bot_token = bot_token
        self.server_name = server_name
        self.channel_name = channel_name
        self.client: Optional[discord.Client] = None
        self._authenticated = False
        self._fetched_channels = {}  # Store fetched channels by guild name

    async def authenticate(self) -> bool:
        """
        Authenticate with Discord API.

        Returns:
            bool: True if authentication successful

        Raises:
            Exception: If authentication fails
        """
        if self._authenticated:
            return True

        if not self.bot_token:
            raise Exception('Discord bot token is required')

        try:
            # Create Discord client instance
            self.client = discord.Client(intents=discord.Intents.all())

            # Login to Discord with timeout
            try:
                await asyncio.wait_for(self.client.login(self.bot_token), timeout=10.0)
            except asyncio.TimeoutError:
                raise Exception(
                    'Discord login timed out. The bot token appears to be invalid or Discord servers are unreachable.')

            # Wait until client is ready with timeout
            try:
                await asyncio.wait_for(self.client.wait_until_ready(), timeout=30.0)
            except asyncio.TimeoutError:
                # Check if we can fetch guilds directly
                try:

                    # Try to fetch guilds manually if not loaded
                    if len(self.client.guilds) == 0 and self.client.user:
                        try:
                            # fetch_guilds() returns an async iterator, convert to list
                            fetched_guilds = [guild async for guild in self.client.fetch_guilds()]

                            if len(fetched_guilds) > 0:

                                # Fetch full guild details including channels
                                self._fetched_guilds = []
                                for guild in fetched_guilds:
                                    try:
                                        full_guild = await self.client.fetch_guild(guild.id)

                                        # If no channels, try to fetch them separately
                                        if len(full_guild.text_channels) == 0:
                                            try:
                                                channels = await full_guild.fetch_channels()
                                                text_channels = [
                                                    c for c in channels if isinstance(
                                                        c, discord.TextChannel)]
                                                # Store the fetched channels for later use
                                                self._fetched_channels[full_guild.name] = text_channels
                                            except Exception:
                                                pass

                                        self._fetched_guilds.append(full_guild)
                                    except Exception:
                                        # Use the basic guild if full fetch fails
                                        self._fetched_guilds.append(guild)

                                # Mark as ready since we have guilds
                                self.client._ready.set()
                            else:
                                raise Exception(
                                    'Discord bot is not added to any servers. Please invite the bot to your Discord server using the OAuth2 URL from the Developer Portal.')
                        except Exception:
                            raise Exception(
                                'Discord authentication failed. Please check your bot token and ensure the bot is invited to your server.')
                    else:
                        raise Exception(
                            'Discord authentication timed out after login. The bot may not have proper permissions or the server/channel may not exist.')
                except Exception:
                    raise Exception(
                        'Discord authentication failed. Please check your bot token and ensure the bot is invited to your server.')

            self._authenticated = True
            return True
        except Exception as e:
            raise Exception(f'Discord authentication failed: {str(e)}') from e

    def disconnect(self):
        """
        Disconnect and clean up client resources.
        """
        if self.client:
            try:
                # Use asyncio to close the client if it's still running
                if not self.client.is_closed():
                    asyncio.create_task(self.client.close())
            except Exception:
                pass

        self.client = None
        self._authenticated = False

    def _get_guild(self) -> discord.Guild:
        """
        Get Discord guild by name.

        Args:
            client: Discord client instance

        Returns:
            Guild: Discord guild object

        Raises:
            Exception: If guild not found
        """
        if not self.client:
            raise Exception('Discord client not available')

        # First try the client's guilds list
        for guild in self.client.guilds:
            if guild.name == self.server_name:
                return guild

        # If not found, try the fetched guilds (for when wait_until_ready timed out)
        if hasattr(self, '_fetched_guilds'):
            for guild in self._fetched_guilds:
                if guild.name == self.server_name:
                    return guild

        raise Exception(f'Guild {self.server_name} not found.')

    def _get_channel(self) -> discord.TextChannel:
        """
        Get Discord text channel by name.

        Args:
            client: Discord client instance

        Returns:
            TextChannel: Discord text channel object

        Raises:
            Exception: If channel not found
        """
        guild = self._get_guild()

        # First try the normal text_channels
        for channel in guild.text_channels:
            if channel.name == self.channel_name:
                return channel

        # If not found, try the fetched text channels (for manually populated guilds)
        if guild.name in self._fetched_channels:
            for channel in self._fetched_channels[guild.name]:
                if channel.name == self.channel_name:
                    return channel

        raise Exception(f'Text channel {self.channel_name} not found.')

    async def send_message(self, content: Optional[str] = None,
                           embeds: Optional[List[discord.Embed]] = None,
                           file: Optional[discord.File] = None) -> str:
        """
        Send a message to the configured Discord channel.

        Args:
            content (str, optional): Text content of the message
            embeds (list, optional): List of Discord embeds
            file (discord.File, optional): File to attach

        Returns:
            str: Message ID

        Raises:
            Exception: If message sending fails
        """
        if not self._authenticated:
            raise Exception('Discord client not authenticated')

        if not self.client:
            raise Exception('Discord client not available')

        try:
            channel = self._get_channel()
            # Build kwargs dict with only non-None values
            kwargs = {}
            if content is not None:
                kwargs['content'] = content
            if embeds is not None:
                kwargs['embeds'] = embeds
            if file is not None:
                kwargs['file'] = file

            # Send message with appropriate parameters
            if kwargs:
                message = await channel.send(**kwargs)
            else:
                message = await channel.send()

            return str(message.id)
        except Exception as e:
            error_msg = f'Discord send message failed: {str(e)}'
            raise Exception(error_msg) from e

    async def add_reaction(self, message_id: str, emoji: str = '❤️') -> str:
        """
        Add a reaction to a Discord message.

        Args:
            message_id (str): ID of the message to react to
            emoji (str): Emoji to react with

        Returns:
            str: Message ID

        Raises:
            Exception: If reaction fails
        """
        if not self._authenticated:
            raise Exception('Discord client not authenticated')

        if not self.client:
            raise Exception('Discord client not available')

        try:
            channel = self._get_channel()
            message = await channel.fetch_message(int(message_id))
            await message.add_reaction(emoji)
            return message_id
        except Exception as e:
            error_msg = f'Discord add reaction failed: {str(e)}'
            raise Exception(error_msg) from e

    async def delete_message(self, message_id: str) -> str:
        """
        Delete a Discord message.

        Args:
            message_id (str): ID of the message to delete

        Returns:
            str: Message ID

        Raises:
            Exception: If deletion fails
        """
        if not self._authenticated:
            raise Exception('Discord client not authenticated')

        if not self.client:
            raise Exception('Discord client not available')

        try:
            channel = self._get_channel()
            message = await channel.fetch_message(int(message_id))
            await message.delete()
            return message_id
        except Exception as e:
            error_msg = f'Discord delete message failed: {str(e)}'
            raise Exception(error_msg) from e

    async def upload_file(self, file_content: Any, filename: str,
                          content: Optional[str] = None,
                          embeds: Optional[List[discord.Embed]] = None) -> str:
        """
        Upload a file to Discord.

        Args:
            file_content: File-like object or bytes
            filename (str): Name of the file
            content (str, optional): Message content to accompany file
            embeds (list, optional): Embeds to include with file

        Returns:
            str: Message ID

        Raises:
            Exception: If file upload fails
        """
        if not self._authenticated:
            raise Exception('Discord client not authenticated')

        if not self.client:
            raise Exception('Discord client not available')

        try:
            channel = self._get_channel()

            kwargs = {}
            kwargs['file'] = discord.File(file_content, filename=filename)

            if content is not None:
                kwargs['content'] = content
            if embeds is not None:
                kwargs['embeds'] = embeds

            message = await channel.send(**kwargs)
            return str(message.id)
        except Exception as e:
            error_msg = f'Discord file upload failed: {str(e)}'
            raise Exception(error_msg) from e

    def create_embed(self, title: Optional[str] = None,
                     description: Optional[str] = None,
                     url: Optional[str] = None, embed_type: str = 'rich',
                     image_url: Optional[str] = None) -> discord.Embed:
        """
        Create a Discord embed object.

        Args:
            title (str, optional): Embed title
            description (str, optional): Embed description
            url (str, optional): Embed URL
            embed_type (str): Embed type (default: 'rich')
            image_url (str, optional): Image URL for embed

        Returns:
            discord.Embed: Discord embed object
        """
        # Create embed without type parameter to avoid linter issues
        embed = discord.Embed()

        if title:
            embed.title = title
        if description:
            embed.description = description
        if url:
            embed.url = url
        if image_url:
            embed.set_image(url=image_url)

        return embed
