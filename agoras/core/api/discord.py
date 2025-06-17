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

import discord

from .base import BaseAPI


class DiscordAPI(BaseAPI):
    """
    Discord API handler that centralizes Discord operations.

    Provides methods for Discord authentication, server/channel management,
    message operations, and file uploads.
    """

    def __init__(self, bot_token, server_name, channel_name):
        """
        Initialize Discord API instance.

        Args:
            bot_token (str): Discord bot token
            server_name (str): Discord server name
            channel_name (str): Discord channel name
        """
        super().__init__(
            bot_token=bot_token,
            server_name=server_name,
            channel_name=channel_name
        )
        self.bot_token = bot_token
        self.server_name = server_name
        self.channel_name = channel_name
        self._guild = None
        self._channel = None

    async def authenticate(self):
        """
        Authenticate with Discord API asynchronously.

        Returns:
            DiscordAPI: Self for method chaining

        Raises:
            Exception: If authentication fails
        """
        if self._authenticated:
            return self

        if not self.bot_token:
            raise Exception('Discord bot token is required.')
        if not self.server_name:
            raise Exception('Discord server name is required.')
        if not self.channel_name:
            raise Exception('Discord channel name is required.')

        # Authentication is handled during client operations
        self._authenticated = True
        return self

    async def disconnect(self):
        """
        Disconnect from Discord API and clean up resources.
        """
        # DiscordAPI doesn't maintain a persistent client - clients are created per operation
        # So we only need to reset the authentication state
        self._authenticated = False
        self._guild = None
        self._channel = None

    def _get_guild(self, client):
        """
        Get Discord guild by name.

        Args:
            client: Discord client instance

        Returns:
            Guild: Discord guild object

        Raises:
            Exception: If guild not found
        """
        for guild in client.guilds:
            if guild.name == self.server_name:
                return guild
        raise Exception(f'Guild {self.server_name} not found.')

    def _get_channel(self, client):
        """
        Get Discord text channel by name.

        Args:
            client: Discord client instance

        Returns:
            TextChannel: Discord text channel object

        Raises:
            Exception: If channel not found
        """
        guild = self._get_guild(client)
        for channel in guild.text_channels:
            if channel.name == self.channel_name:
                return channel
        raise Exception(f'Text channel {self.channel_name} not found.')

    async def _run_with_client(self, operation):
        """
        Run an operation with a Discord client instance.

        Args:
            operation (callable): Async operation to run with client

        Returns:
            Result of the operation

        Raises:
            Exception: If operation fails
        """
        if not self._authenticated:
            await self.authenticate()

        client = discord.Client(intents=discord.Intents.all())
        result = None

        @client.event
        async def on_ready():
            nonlocal result
            try:
                result = await operation(client)
            finally:
                await client.close()

        try:
            await client.start(str(self.bot_token))
            return result
        except Exception as e:
            try:
                await client.close()
            except Exception:
                pass
            error_msg = f'Discord client operation failed: {str(e)}'
            raise Exception(error_msg) from e

    async def send_message(self, content=None, embeds=None, file=None):
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
        async def _send_operation(client):
            await self._rate_limit_check('send_message', 1.0)

            channel = self._get_channel(client)

            # Determine what to send based on available parameters
            kwargs = {}
            if content:
                kwargs['content'] = content
            if embeds:
                kwargs['embeds'] = embeds
            if file:
                kwargs['file'] = file

            # Send message with appropriate parameters
            if kwargs:
                message = await channel.send(**kwargs)
            else:
                message = await channel.send("")

            return str(message.id)

        return await self._run_with_client(_send_operation)

    async def add_reaction(self, message_id, emoji='❤️'):
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
        async def _reaction_operation(client):
            await self._rate_limit_check('add_reaction', 0.5)

            channel = self._get_channel(client)
            message = await channel.fetch_message(message_id)
            await message.add_reaction(emoji)

            return message_id

        return await self._run_with_client(_reaction_operation)

    async def delete_message(self, message_id):
        """
        Delete a Discord message.

        Args:
            message_id (str): ID of the message to delete

        Returns:
            str: Message ID

        Raises:
            Exception: If deletion fails
        """
        async def _delete_operation(client):
            await self._rate_limit_check('delete_message', 0.5)

            channel = self._get_channel(client)
            message = await channel.fetch_message(message_id)
            await message.delete()

            return message_id

        return await self._run_with_client(_delete_operation)

    async def edit_message(self, message_id, content=None, embeds=None):
        """
        Edit a Discord message.

        Args:
            message_id (str): ID of the message to edit
            content (str, optional): New text content
            embeds (list, optional): New embeds

        Returns:
            str: Message ID

        Raises:
            Exception: If editing fails
        """
        async def _edit_operation(client):
            await self._rate_limit_check('edit_message', 0.5)

            channel = self._get_channel(client)
            message = await channel.fetch_message(message_id)

            kwargs = {}
            if content is not None:
                kwargs['content'] = content
            if embeds is not None:
                kwargs['embeds'] = embeds

            await message.edit(**kwargs)
            return message_id

        return await self._run_with_client(_edit_operation)

    async def get_message(self, message_id):
        """
        Get a Discord message by ID.

        Args:
            message_id (str): ID of the message to retrieve

        Returns:
            dict: Message data

        Raises:
            Exception: If message retrieval fails
        """
        async def _get_operation(client):
            await self._rate_limit_check('get_message', 0.2)

            channel = self._get_channel(client)
            message = await channel.fetch_message(message_id)

            return {
                'id': str(message.id),
                'content': message.content,
                'author': str(message.author),
                'timestamp': message.created_at.isoformat(),
                'embeds': len(message.embeds),
                'attachments': len(message.attachments)
            }

        return await self._run_with_client(_get_operation)

    async def upload_file(self, file_content, filename, content=None, embeds=None):
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
        async def _upload_operation(client):
            await self._rate_limit_check('upload_file', 1.0)

            discord_file = discord.File(file_content, filename=filename)

            kwargs = {'file': discord_file}
            if content:
                kwargs['content'] = content
            if embeds:
                kwargs['embeds'] = embeds

            channel = self._get_channel(client)
            message = await channel.send(**kwargs)

            return str(message.id)

        return await self._run_with_client(_upload_operation)

    def create_embed(self, title=None, description=None, url=None,
                     embed_type='rich', image_url=None):
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

    def get_api_info(self):
        """
        Get Discord API configuration information.

        Returns:
            dict: API configuration details
        """
        return {
            'platform': 'Discord',
            'server_name': self.server_name,
            'channel_name': self.channel_name,
            'authenticated': self._authenticated,
            'rate_limits': list(self._rate_limit_cache.keys())
        }
