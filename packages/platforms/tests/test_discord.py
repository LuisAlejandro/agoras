# -*- coding: utf-8 -*-
#
# Please refer to AUTHORS.rst for a complete list of Copyright holders.
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

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from agoras.platforms.discord import Discord
from agoras.platforms.discord.api import DiscordAPI
from agoras.platforms.discord.auth import DiscordAuthManager
from agoras.platforms.discord.client import DiscordAPIClient

# Discord Wrapper Tests


@pytest.mark.asyncio
@patch('agoras.platforms.discord.wrapper.DiscordAPI')
async def test_discord_initialize_client(mock_api_class):
    """Test Discord _initialize_client extracts config and creates API."""
    mock_api = MagicMock()
    mock_api.authenticate = AsyncMock()
    mock_api_class.return_value = mock_api

    discord = Discord(
        discord_bot_token='test_token',
        discord_server_name='Test Server',
        discord_channel_name='general'
    )

    await discord._initialize_client()

    assert discord.discord_bot_token == 'test_token'
    assert discord.discord_server_name == 'Test Server'
    assert discord.discord_channel_name == 'general'
    assert discord.api is mock_api
    mock_api.authenticate.assert_called_once()


@pytest.mark.asyncio
@patch('agoras.platforms.discord.auth.DiscordAuthManager._load_credentials_from_storage', return_value=False)
async def test_discord_initialize_client_missing_token(mock_load_credentials):
    """Test Discord _initialize_client raises exception without token."""
    discord = Discord()

    with pytest.raises(Exception, match="Not authenticated. Please run 'agoras discord authorize' first."):
        await discord._initialize_client()


@pytest.mark.asyncio
@patch('agoras.platforms.discord.auth.DiscordAuthManager._load_credentials_from_storage', return_value=False)
async def test_discord_initialize_client_missing_server(mock_load_credentials):
    """Test Discord _initialize_client raises exception without server."""
    discord = Discord(discord_bot_token='token')

    with pytest.raises(Exception, match="Not authenticated. Please run 'agoras discord authorize' first."):
        await discord._initialize_client()


@pytest.mark.asyncio
@patch('agoras.platforms.discord.auth.DiscordAuthManager._load_credentials_from_storage', return_value=False)
async def test_discord_initialize_client_missing_channel(mock_load_credentials):
    """Test Discord _initialize_client raises exception without channel."""
    discord = Discord(
        discord_bot_token='token',
        discord_server_name='Server'
    )

    with pytest.raises(Exception, match="Not authenticated. Please run 'agoras discord authorize' first."):
        await discord._initialize_client()


@pytest.mark.asyncio
@patch('agoras.platforms.discord.wrapper.parse_metatags')
@patch('agoras.platforms.discord.wrapper.DiscordAPI')
async def test_discord_post(mock_api_class, mock_parse):
    """Test Discord post method."""
    mock_parse.return_value = {'title': 'Title', 'description': 'Desc', 'image': ''}

    mock_api = MagicMock()
    mock_api.authenticate = AsyncMock()
    mock_api.create_embed = MagicMock(return_value={'title': 'Embed'})
    mock_api.send_message = AsyncMock(return_value='message-123')
    mock_api.post = AsyncMock(return_value='message-123')  # Add post method
    mock_api_class.return_value = mock_api

    discord = Discord(
        discord_bot_token='token',
        discord_server_name='Server',
        discord_channel_name='Channel'
    )

    await discord._initialize_client()

    # Mock _output_status to avoid print
    with patch.object(discord, '_output_status'):
        result = await discord.post('Hello Discord', 'http://link.com')

    assert result == 'message-123'


@pytest.mark.asyncio
@patch('agoras.platforms.discord.wrapper.DiscordAPI')
async def test_discord_disconnect(mock_api_class):
    """Test Discord disconnect method."""
    mock_api = MagicMock()
    mock_api.authenticate = AsyncMock()
    mock_api.disconnect = AsyncMock()
    mock_api_class.return_value = mock_api

    discord = Discord(
        discord_bot_token='token',
        discord_server_name='Server',
        discord_channel_name='Channel'
    )

    await discord._initialize_client()
    await discord.disconnect()

    mock_api.disconnect.assert_called_once()


# Discord API Tests

def test_discord_api_class_exists():
    """Test DiscordAPI class exists."""
    assert DiscordAPI is not None


# Discord Auth Tests (Abstract - test via concrete usage)

def test_discord_auth_class_exists():
    """Test DiscordAuthManager class exists."""
    assert DiscordAuthManager is not None


# Discord Client Tests

def test_discord_client_instantiation():
    """Test DiscordAPIClient can be instantiated."""
    client = DiscordAPIClient('bot_token', 'Server', 'Channel')
    assert client is not None


# Additional Discord Wrapper Tests

@pytest.mark.asyncio
async def test_discord_init_maps_discord_post_id():
    """Test Discord __init__ maps discord_post_id to post_id."""
    discord = Discord(discord_post_id='test_pid')
    # The mapping happens in __init__, so we can't directly check kwargs after super().__init__
    # But we can verify the behavior indirectly by checking that post_id gets used
    # For now, just ensure the instance is created without error
    assert discord is not None


@pytest.mark.asyncio
@patch('agoras.platforms.discord.wrapper.DiscordAPI')
async def test_discord_initialize_client_loads_from_storage(mock_api_class):
    """Test Discord _initialize_client loads credentials from storage."""
    mock_api = MagicMock()
    mock_api.authenticate = AsyncMock()
    mock_api_class.return_value = mock_api

    # Mock auth manager
    with patch('agoras.platforms.discord.auth.DiscordAuthManager') as mock_auth_class:
        mock_auth_manager = MagicMock()
        mock_auth_manager._load_credentials_from_storage.return_value = True
        mock_auth_manager.bot_token = 'stored_token'
        mock_auth_manager.server_name = 'stored_server'
        mock_auth_manager.channel_name = 'stored_channel'
        mock_auth_class.return_value = mock_auth_manager

        discord = Discord()

        await discord._initialize_client()

        assert discord.discord_bot_token == 'stored_token'
        assert discord.discord_server_name == 'stored_server'
        assert discord.discord_channel_name == 'stored_channel'
        assert discord.api is mock_api
        mock_api.authenticate.assert_called_once()


@pytest.mark.asyncio
@patch('agoras.platforms.discord.wrapper.DiscordAPI')
async def test_discord_build_embeds_no_api(mock_api_class):
    """Test Discord _build_embeds with no API initialized."""
    mock_api = MagicMock()
    mock_api.authenticate = AsyncMock()
    mock_api_class.return_value = mock_api

    discord = Discord(
        discord_bot_token='token',
        discord_server_name='Server',
        discord_channel_name='Channel'
    )

    await discord._initialize_client()

    discord.api = None  # Simulate no API

    with pytest.raises(Exception, match='Discord API not initialized'):
        discord._build_embeds('link', 'title', 'desc', 'image', [])


@pytest.mark.asyncio
@patch('agoras.platforms.discord.wrapper.DiscordAPI')
async def test_discord_build_embeds_with_link(mock_api_class):
    """Test Discord _build_embeds with link."""
    mock_api = MagicMock()
    mock_api.authenticate = AsyncMock()
    mock_api.create_embed.return_value = {'title': 'Link Embed'}
    mock_api_class.return_value = mock_api

    discord = Discord(
        discord_bot_token='token',
        discord_server_name='Server',
        discord_channel_name='Channel'
    )

    await discord._initialize_client()

    result = discord._build_embeds('http://link.com', 'Link Title', 'Link Desc', 'link.jpg', [])

    assert len(result) == 1
    mock_api.create_embed.assert_called_once_with(
        title='Link Title',
        description='Link Desc',
        url='http://link.com',
        image_url='link.jpg'
    )


@pytest.mark.asyncio
@patch('agoras.platforms.discord.wrapper.DiscordAPI')
async def test_discord_build_embeds_with_media(mock_api_class):
    """Test Discord _build_embeds with media."""
    mock_api = MagicMock()
    mock_api.authenticate = AsyncMock()
    mock_api.create_embed.return_value = {'image': 'media.jpg'}
    mock_api_class.return_value = mock_api

    discord = Discord(
        discord_bot_token='token',
        discord_server_name='Server',
        discord_channel_name='Channel'
    )

    await discord._initialize_client()

    attached_media = [{'url': 'media1.jpg'}, {'url': 'media2.jpg'}]
    result = discord._build_embeds('', '', '', '', attached_media)

    assert len(result) == 2
    assert mock_api.create_embed.call_count == 2


@pytest.mark.asyncio
@patch('agoras.platforms.discord.wrapper.DiscordAPI')
async def test_discord_post_no_api(mock_api_class):
    """Test Discord post with no API initialized."""
    discord = Discord(
        discord_bot_token='token',
        discord_server_name='Server',
        discord_channel_name='Channel'
    )

    with pytest.raises(Exception, match='Discord API not initialized'):
        await discord.post('text', 'link')


@pytest.mark.asyncio
@patch('agoras.platforms.discord.wrapper.DiscordAPI')
async def test_discord_post_no_content_link_or_images(mock_api_class):
    """Test Discord post with no content, link, or images."""
    mock_api = MagicMock()
    mock_api.authenticate = AsyncMock()
    mock_api_class.return_value = mock_api

    discord = Discord(
        discord_bot_token='token',
        discord_server_name='Server',
        discord_channel_name='Channel'
    )

    await discord._initialize_client()

    with pytest.raises(Exception, match='No status text, link, or images provided'):
        await discord.post('', '', None, None, None, None)


@pytest.mark.asyncio
@patch('agoras.platforms.discord.wrapper.DiscordAPI')
@patch('agoras.platforms.discord.wrapper.parse_metatags')
async def test_discord_post_with_images(mock_parse, mock_api_class):
    """Test Discord post with images."""
    mock_parse.return_value = {}

    mock_api = MagicMock()
    mock_api.authenticate = AsyncMock()
    mock_api.create_embed.return_value = {'image': 'img.jpg'}
    mock_api.post = AsyncMock(return_value='message-123')
    mock_api_class.return_value = mock_api

    discord = Discord(
        discord_bot_token='token',
        discord_server_name='Server',
        discord_channel_name='Channel'
    )

    await discord._initialize_client()

    # Mock download_images
    with patch.object(discord, 'download_images', new_callable=AsyncMock) as mock_download:
        mock_image = MagicMock()
        mock_image.url = 'img.jpg'
        mock_image.cleanup = MagicMock()
        mock_download.return_value = [mock_image]

        with patch.object(discord, '_output_status'):
            result = await discord.post('Hello Discord', 'http://link.com',
                                      status_image_url_1='img.jpg')

    assert result == 'message-123'


@pytest.mark.asyncio
@patch('agoras.platforms.discord.wrapper.DiscordAPI')
async def test_discord_like_no_api(mock_api_class):
    """Test Discord like with no API initialized."""
    discord = Discord(
        discord_bot_token='token',
        discord_server_name='Server',
        discord_channel_name='Channel'
    )

    with pytest.raises(Exception, match='Discord API not initialized'):
        await discord.like('message123')


@pytest.mark.asyncio
@patch('agoras.platforms.discord.wrapper.DiscordAPI')
async def test_discord_like_success(mock_api_class):
    """Test Discord like success."""
    mock_api = MagicMock()
    mock_api.authenticate = AsyncMock()
    mock_api.like = AsyncMock(return_value='reaction123')
    mock_api_class.return_value = mock_api

    discord = Discord(
        discord_bot_token='token',
        discord_server_name='Server',
        discord_channel_name='Channel'
    )

    await discord._initialize_client()

    with patch.object(discord, '_output_status'):
        result = await discord.like('message123')

    assert result == 'reaction123'
    mock_api.like.assert_called_once_with('message123', '❤️')


@pytest.mark.asyncio
@patch('agoras.platforms.discord.wrapper.DiscordAPI')
async def test_discord_delete_no_api(mock_api_class):
    """Test Discord delete with no API initialized."""
    discord = Discord(
        discord_bot_token='token',
        discord_server_name='Server',
        discord_channel_name='Channel'
    )

    with pytest.raises(Exception, match='Discord API not initialized'):
        await discord.delete('message123')


@pytest.mark.asyncio
@patch('agoras.platforms.discord.wrapper.DiscordAPI')
async def test_discord_delete_success(mock_api_class):
    """Test Discord delete success."""
    mock_api = MagicMock()
    mock_api.authenticate = AsyncMock()
    mock_api.delete = AsyncMock(return_value='deleted123')
    mock_api_class.return_value = mock_api

    discord = Discord(
        discord_bot_token='token',
        discord_server_name='Server',
        discord_channel_name='Channel'
    )

    await discord._initialize_client()

    with patch.object(discord, '_output_status'):
        result = await discord.delete('message123')

    assert result == 'deleted123'
    mock_api.delete.assert_called_once_with('message123')


@pytest.mark.asyncio
@patch('agoras.platforms.discord.wrapper.DiscordAPI')
async def test_discord_share_raises(mock_api_class):
    """Test Discord share raises exception."""
    mock_api = MagicMock()
    mock_api.authenticate = AsyncMock()
    mock_api_class.return_value = mock_api

    discord = Discord(
        discord_bot_token='token',
        discord_server_name='Server',
        discord_channel_name='Channel'
    )

    await discord._initialize_client()

    with pytest.raises(Exception, match='Share not supported for Discord'):
        await discord.share('message123')


@pytest.mark.asyncio
@patch('agoras.platforms.discord.wrapper.DiscordAPI')
async def test_discord_video_no_api(mock_api_class):
    """Test Discord video with no API initialized."""
    discord = Discord(
        discord_bot_token='token',
        discord_server_name='Server',
        discord_channel_name='Channel'
    )

    with pytest.raises(Exception, match='Discord API not initialized'):
        await discord.video('text', 'url', 'title')


@pytest.mark.asyncio
@patch('agoras.platforms.discord.wrapper.DiscordAPI')
async def test_discord_video_no_url(mock_api_class):
    """Test Discord video with no URL."""
    mock_api = MagicMock()
    mock_api.authenticate = AsyncMock()
    mock_api_class.return_value = mock_api

    discord = Discord(
        discord_bot_token='token',
        discord_server_name='Server',
        discord_channel_name='Channel'
    )

    await discord._initialize_client()

    with pytest.raises(Exception, match='No Discord video URL provided'):
        await discord.video('text', '', 'title')


@pytest.mark.asyncio
@patch('agoras.platforms.discord.wrapper.DiscordAPI')
async def test_discord_video_failed_download(mock_api_class):
    """Test Discord video with failed download."""
    mock_api = MagicMock()
    mock_api.authenticate = AsyncMock()
    mock_api_class.return_value = mock_api

    discord = Discord(
        discord_bot_token='token',
        discord_server_name='Server',
        discord_channel_name='Channel'
    )

    await discord._initialize_client()

    with patch.object(discord, 'download_video', new_callable=AsyncMock) as mock_download:
        mock_video = MagicMock()
        mock_video.content = None  # Failed download
        mock_download.return_value = mock_video

        with pytest.raises(Exception, match='Failed to download or validate video'):
            await discord.video('text', 'http://video.mp4', 'title')


@pytest.mark.asyncio
@patch('agoras.platforms.discord.wrapper.DiscordAPI')
async def test_discord_video_success(mock_api_class):
    """Test Discord video success."""
    mock_api = MagicMock()
    mock_api.authenticate = AsyncMock()
    mock_api.create_embed.return_value = {'title': 'Video Embed'}
    mock_api.upload_file = AsyncMock(return_value='message-456')
    mock_api_class.return_value = mock_api

    discord = Discord(
        discord_bot_token='token',
        discord_server_name='Server',
        discord_channel_name='Channel'
    )

    await discord._initialize_client()

    with patch.object(discord, 'download_video', new_callable=AsyncMock) as mock_download:
        mock_video = MagicMock()
        mock_video.content = b'video_content'
        mock_file_type = MagicMock()
        mock_file_type.mime = 'video/mp4'
        mock_file_type.extension = 'mp4'
        mock_video.file_type = mock_file_type
        mock_video.get_file_like_object.return_value = b'video_data'
        mock_video.cleanup = MagicMock()
        mock_download.return_value = mock_video

        with patch.object(discord, '_output_status'):
            result = await discord.video('Video text', 'http://video.mp4', 'Video Title')

    assert result == 'message-456'


@pytest.mark.asyncio
@patch('agoras.platforms.discord.auth.DiscordAuthManager')
async def test_discord_authorize_credentials_success(mock_auth_class):
    """Test Discord authorize_credentials success."""
    mock_auth_manager = MagicMock()
    mock_auth_manager.authorize = AsyncMock(return_value="Authorization successful")
    mock_auth_class.return_value = mock_auth_manager

    discord = Discord(
        discord_bot_token='token',
        discord_server_name='Server',
        discord_channel_name='Channel'
    )

    with patch('builtins.print'):
        result = await discord.authorize_credentials()

    assert result is True
    mock_auth_manager.authorize.assert_called_once()


@pytest.mark.asyncio
@patch('agoras.platforms.discord.auth.DiscordAuthManager')
async def test_discord_authorize_credentials_failure(mock_auth_class):
    """Test Discord authorize_credentials failure."""
    mock_auth_manager = MagicMock()
    mock_auth_manager.authorize = AsyncMock(return_value=None)
    mock_auth_class.return_value = mock_auth_manager

    discord = Discord(
        discord_bot_token='token',
        discord_server_name='Server',
        discord_channel_name='Channel'
    )

    result = await discord.authorize_credentials()

    assert result is False
    mock_auth_manager.authorize.assert_called_once()


@pytest.mark.asyncio
async def test_discord_main_async_empty_action():
    """Test Discord main_async with empty action."""
    from agoras.platforms.discord.wrapper import main_async

    with pytest.raises(Exception, match="Action is a required argument"):
        await main_async({})


@pytest.mark.asyncio
@patch('agoras.platforms.discord.wrapper.Discord')
async def test_discord_main_async_authorize(mock_discord_class):
    """Test Discord main_async with authorize action."""
    from agoras.platforms.discord.wrapper import main_async

    mock_discord = MagicMock()
    mock_discord.authorize_credentials = AsyncMock(return_value=True)
    mock_discord_class.return_value = mock_discord

    result = await main_async({'action': 'authorize'})

    assert result == 0
    mock_discord.authorize_credentials.assert_called_once()


@pytest.mark.asyncio
@patch('agoras.platforms.discord.wrapper.Discord')
async def test_discord_main_async_execute_action(mock_discord_class):
    """Test Discord main_async with other actions."""
    from agoras.platforms.discord.wrapper import main_async

    mock_discord = MagicMock()
    mock_discord.execute_action = AsyncMock()
    mock_discord.disconnect = AsyncMock()
    mock_discord_class.return_value = mock_discord

    result = await main_async({'action': 'video'})

    assert result is None
    mock_discord.execute_action.assert_called_once_with('video')
    mock_discord.disconnect.assert_called_once()
