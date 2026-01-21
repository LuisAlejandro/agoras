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

from agoras.core.api_base import BaseAPI

from .auth import DiscordAuthManager


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

        # Initialize the authentication manager
        self.auth_manager = DiscordAuthManager(
            bot_token=bot_token,
            server_name=server_name,
            channel_name=channel_name
        )

    @property
    def bot_token(self):
        """Get the Discord bot token from the auth manager."""
        return self.auth_manager.bot_token if self.auth_manager else None

    @property
    def server_name(self):
        """Get the Discord server name from the auth manager."""
        return self.auth_manager.server_name if self.auth_manager else None

    @property
    def channel_name(self):
        """Get the Discord channel name from the auth manager."""
        return self.auth_manager.channel_name if self.auth_manager else None

    @property
    def user_info(self):
        """Get the Discord user info from the auth manager."""
        return self.auth_manager.user_info if self.auth_manager else None

    async def authenticate(self):
        """
        Authenticate with Discord API using the auth manager and client.

        Returns:
            DiscordAPI: Self for method chaining

        Raises:
            Exception: If authentication fails
        """
        if self._authenticated:
            return self

        # Authenticate with auth manager (this creates and sets up the client)
        auth_success = await self.auth_manager.authenticate()
        if not auth_success:
            error_msg = 'Discord authentication failed'
            if hasattr(self.auth_manager, '_last_error') and self.auth_manager._last_error:
                error_msg += f': {self.auth_manager._last_error}'
            raise Exception(error_msg)

        # Ensure client was created during authentication
        if not self.auth_manager.client:
            raise Exception('Discord client not available after authentication')

        self.client = self.auth_manager.client
        self._authenticated = True
        return self

    async def disconnect(self):
        """
        Disconnect from Discord API and clean up resources.
        """
        # Disconnect the client first
        if self.client:
            self.client.disconnect()

        # Clear auth manager data
        if self.auth_manager:
            self.auth_manager.access_token = None

        # Clear BaseAPI client
        self.client = None
        self._authenticated = False

    async def post(self, content=None, embeds=None, file=None):
        """
        Post a message to the configured Discord channel.

        Args:
            content (str, optional): Text content of the message
            embeds (list, optional): List of Discord embeds
            file (discord.File, optional): File to attach

        Returns:
            str: Message ID

        Raises:
            Exception: If message posting fails
        """
        if not self._authenticated:
            await self.authenticate()

        if not self.client:
            raise Exception('Discord client not available')

        await self._rate_limit_check('post', 1.0)
        return await self.client.send_message(content=content, embeds=embeds, file=file)

    async def like(self, message_id, emoji='❤️'):
        """
        Add a reaction (like) to a Discord message.

        Args:
            message_id (str): ID of the message to react to
            emoji (str): Emoji to react with

        Returns:
            str: Message ID

        Raises:
            Exception: If reaction fails
        """
        if not self._authenticated:
            await self.authenticate()

        if not self.client:
            raise Exception('Discord client not available')

        await self._rate_limit_check('like', 0.5)
        return await self.client.add_reaction(message_id, emoji)

    async def delete(self, message_id):
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
            await self.authenticate()

        if not self.client:
            raise Exception('Discord client not available')

        await self._rate_limit_check('delete', 0.5)
        return await self.client.delete_message(message_id)

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
        if not self._authenticated:
            await self.authenticate()

        if not self.client:
            raise Exception('Discord client not available')

        await self._rate_limit_check('upload_file', 1.0)
        return await self.client.upload_file(file_content, filename, content, embeds)

    async def share(self, message_id):
        """
        Share is not supported for Discord.

        Args:
            message_id (str): ID of the message

        Raises:
            Exception: Share not supported for Discord
        """
        raise Exception('Share not supported for Discord')

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
        if not self.client:
            raise Exception('Discord client not available')

        return self.client.create_embed(
            title=title,
            description=description,
            url=url,
            embed_type=embed_type,
            image_url=image_url
        )
