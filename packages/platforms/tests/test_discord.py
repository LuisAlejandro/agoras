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
