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

from agoras.common.utils import parse_metatags
from agoras.core.interfaces import SocialNetwork

from .api import DiscordAPI


class Discord(SocialNetwork):
    """
    Discord social network implementation.

    This class provides Discord-specific functionality for posting messages,
    videos, and managing Discord interactions asynchronously.
    """

    def __init__(self, **kwargs):
        """
        Initialize Discord instance.

        Args:
            **kwargs: Configuration parameters including:
                - discord_bot_token: Discord bot token
                - discord_server_name: Discord server name
                - discord_channel_name: Discord channel name
        """
        # Map platform-specific keys to generic keys for core interface compatibility
        if 'discord_post_id' in kwargs:
            kwargs['post_id'] = kwargs['discord_post_id']

        super().__init__(**kwargs)
        self.discord_bot_token = None
        self.discord_server_name = None
        self.discord_channel_name = None
        self.api = None

    async def _initialize_client(self):
        """
        Initialize Discord API client.

        This method sets up the Discord API client with configuration.
        Tries to load credentials from storage if not provided via parameters.
        """
        self.discord_bot_token = self._get_config_value('discord_bot_token', 'DISCORD_BOT_TOKEN')
        self.discord_server_name = self._get_config_value('discord_server_name', 'DISCORD_SERVER_NAME')
        self.discord_channel_name = self._get_config_value('discord_channel_name', 'DISCORD_CHANNEL_NAME')

        # If credentials not provided, try loading from storage
        if not self.discord_bot_token or not self.discord_server_name or not self.discord_channel_name:
            from .auth import DiscordAuthManager
            auth_manager = DiscordAuthManager()
            if auth_manager._load_credentials_from_storage():
                if not self.discord_bot_token:
                    self.discord_bot_token = auth_manager.bot_token
                if not self.discord_server_name:
                    self.discord_server_name = auth_manager.server_name
                if not self.discord_channel_name:
                    self.discord_channel_name = auth_manager.channel_name

        if not self.discord_bot_token:
            raise Exception("Not authenticated. Please run 'agoras discord authorize' first.")
        if not self.discord_server_name:
            raise Exception("Not authenticated. Please run 'agoras discord authorize' first.")
        if not self.discord_channel_name:
            raise Exception("Not authenticated. Please run 'agoras discord authorize' first.")

        # Initialize Discord API
        self.api = DiscordAPI(
            self.discord_bot_token,
            self.discord_server_name,
            self.discord_channel_name
        )
        await self.api.authenticate()

    async def disconnect(self):
        """
        Disconnect from Discord API and clean up resources.
        """
        if self.api:
            await self.api.disconnect()

    def _build_embeds(self, status_link, status_link_title, status_link_description,
                      status_link_image, attached_media):
        """
        Build Discord embeds for a message.

        Args:
            status_link (str): URL to include
            status_link_title (str): Link title
            status_link_description (str): Link description
            status_link_image (str): Link image URL
            attached_media (list): List of attached media info

        Returns:
            list: List of Discord embeds
        """
        if not self.api:
            raise Exception('Discord API not initialized')

        embeds = []

        # Add link embed
        if status_link:
            link_embed = self.api.create_embed(
                title=status_link_title,
                description=status_link_description,
                url=status_link,
                image_url=status_link_image
            )
            embeds.append(link_embed)

        # Add media embeds
        for media in attached_media:
            media_embed = self.api.create_embed(image_url=media['url'])
            embeds.append(media_embed)

        return embeds

    async def post(self, status_text, status_link,
                   status_image_url_1=None, status_image_url_2=None,
                   status_image_url_3=None, status_image_url_4=None):
        """
        Create a post on Discord.

        Args:
            status_text (str): Text content of the post
            status_link (str): URL to include in the post
            status_image_url_1 (str, optional): First image URL
            status_image_url_2 (str, optional): Second image URL
            status_image_url_3 (str, optional): Third image URL
            status_image_url_4 (str, optional): Fourth image URL

        Returns:
            str: Post ID
        """
        if not self.api:
            raise Exception('Discord API not initialized')

        embeds = []
        status_link_title = ''
        status_link_description = ''
        status_link_image = ''
        source_media = list(filter(None, [
            status_image_url_1, status_image_url_2,
            status_image_url_3, status_image_url_4
        ]))

        if not source_media and not status_text and not status_link:
            raise Exception('No status text, link, or images provided.')

        # Parse link metadata
        if status_link:
            scraped_data = parse_metatags(status_link)
            status_link_title = scraped_data.get('title', '')
            status_link_description = scraped_data.get('description', '')
            status_link_image = scraped_data.get('image', '')

            # Create link embed
            link_embed = self.api.create_embed(
                title=status_link_title,
                description=status_link_description,
                url=status_link,
                image_url=status_link_image
            )
            embeds.append(link_embed)

        # Download and validate images using the Media system
        if source_media:
            images = await self.download_images(source_media)
            for image in images:
                try:
                    image_embed = self.api.create_embed(image_url=image.url)
                    embeds.append(image_embed)
                finally:
                    # Clean up temporary files
                    image.cleanup()

        # Post message using Discord API
        message_id = await self.api.post(
            content=status_text or None,
            embeds=embeds if embeds else None
        )

        self._output_status(message_id)
        return message_id

    async def like(self, discord_post_id):
        """
        Like a Discord message by adding a heart reaction.

        Args:
            discord_post_id (str): ID of the Discord message to like

        Returns:
            str: Post ID
        """
        if not self.api:
            raise Exception('Discord API not initialized')

        result = await self.api.like(discord_post_id, '❤️')
        self._output_status(result)
        return result

    async def delete(self, discord_post_id):
        """
        Delete a Discord message.

        Args:
            discord_post_id (str): ID of the Discord message to delete

        Returns:
            str: Post ID
        """
        if not self.api:
            raise Exception('Discord API not initialized')

        result = await self.api.delete(discord_post_id)
        self._output_status(result)
        return result

    async def share(self, discord_post_id):
        """
        Share is not supported for Discord.

        Args:
            discord_post_id (str): ID of the Discord message

        Raises:
            Exception: Share not supported for Discord
        """
        raise Exception('Share not supported for Discord')

    async def video(self, status_text, video_url, video_title):
        """
        Post a video to Discord.

        Args:
            status_text (str): Text content to accompany the video
            video_url (str): URL of the video to post
            video_title (str): Title of the video

        Returns:
            str: Post ID
        """
        if not self.api:
            raise Exception('Discord API not initialized')

        if not video_url:
            raise Exception('No Discord video URL provided.')

        # Download and validate video using the Media system
        video = await self.download_video(video_url)

        if not video.content or not video.file_type:
            video.cleanup()
            raise Exception('Failed to download or validate video')

        # Create embed for video title and description
        embeds = []
        if video_title or status_text:
            embed = self.api.create_embed(
                title=video_title or "Video",
                description=status_text
            )
            embeds.append(embed)

        # Get file-like object directly from video content in memory
        video_file = video.get_file_like_object()
        filename = f"video.{video.file_type.extension}"

        # Upload file using Discord API
        message_id = await self.api.upload_file(
            video_file,
            filename,
            content=None,
            embeds=embeds if embeds else None
        )

        # Clean up
        video.cleanup()

        self._output_status(message_id)
        return message_id

    async def authorize_credentials(self):
        """
        Authorize and store Discord credentials for future use.

        Returns:
            bool: True if authorization successful
        """
        from .auth import DiscordAuthManager

        bot_token = self._get_config_value('discord_bot_token', 'DISCORD_BOT_TOKEN')
        server_name = self._get_config_value('discord_server_name', 'DISCORD_SERVER_NAME')
        channel_name = self._get_config_value('discord_channel_name', 'DISCORD_CHANNEL_NAME')

        auth_manager = DiscordAuthManager(
            bot_token=bot_token,
            server_name=server_name,
            channel_name=channel_name
        )

        result = await auth_manager.authorize()
        if result:
            print(result)
            return True
        return False


async def main_async(kwargs):
    """
    Async main function to execute Discord actions.

    Args:
        kwargs (dict): Configuration arguments
    """
    action = kwargs.get('action', '')

    if action == '':
        raise Exception('Action is a required argument.')

    # Create Discord instance with configuration
    instance = Discord(**kwargs)

    # Handle authorize action separately (doesn't need client initialization)
    if action == 'authorize':
        success = await instance.authorize_credentials()
        return 0 if success else 1

    # Execute other actions using the base class method
    await instance.execute_action(action)
    await instance.disconnect()


def main(kwargs):
    """
    Main function to execute Discord actions.

    Args:
        kwargs (dict): Configuration arguments
    """
    asyncio.run(main_async(kwargs))
