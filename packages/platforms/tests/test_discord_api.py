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

from agoras.platforms.discord.api import DiscordAPI


@pytest.fixture
def discord_api():
    """Fixture to create DiscordAPI instance with mocked auth."""
    with patch('agoras.platforms.discord.api.DiscordAuthManager'):
        api = DiscordAPI('bot_token', 'Server Name', 'channel-name')
        api._authenticated = True
        api.auth_manager = MagicMock()
        api.channel = MagicMock()
        yield api


# Authentication Tests

@pytest.mark.asyncio
@patch('agoras.platforms.discord.api.DiscordAuthManager')
@patch('agoras.platforms.discord.client.DiscordAPIClient')
async def test_discord_api_authenticate(mock_client_class, mock_auth_class):
    """Test DiscordAPI authenticate method."""
    mock_auth = MagicMock()
    mock_auth.authenticate = AsyncMock()
    mock_auth_class.return_value = mock_auth

    mock_client = MagicMock()
    mock_client.connect = AsyncMock()
    mock_client.get_channel = AsyncMock(return_value='channel_obj')
    mock_client_class.return_value = mock_client

    api = DiscordAPI('token', 'Server', 'channel')
    result = await api.authenticate()

    assert api._authenticated is True
    assert result is api


@pytest.mark.asyncio
async def test_discord_api_disconnect(discord_api):
    """Test DiscordAPI disconnect method."""
    discord_api.client = MagicMock()
    discord_api.client.close = AsyncMock()

    await discord_api.disconnect()

    assert discord_api._authenticated is False


# Post Tests

@pytest.mark.asyncio
async def test_discord_api_post(discord_api):
    """Test DiscordAPI post method."""
    discord_api.client = MagicMock()
    discord_api.client.send_message = AsyncMock(return_value='msg-789')

    result = await discord_api.post(content='Post text', embeds=None, file=None)

    assert result == 'msg-789'


# Like Tests

@pytest.mark.asyncio
async def test_discord_api_like(discord_api):
    """Test DiscordAPI like method."""
    discord_api.client = MagicMock()
    discord_api.client.add_reaction = AsyncMock(return_value='msg-123')

    result = await discord_api.like('msg-123')

    # Method returns what client.add_reaction returns
    assert result == 'msg-123'
    discord_api.client.add_reaction.assert_called_once()


# Delete Tests

@pytest.mark.asyncio
async def test_discord_api_delete(discord_api):
    """Test DiscordAPI delete method."""
    discord_api.client = MagicMock()
    discord_api.client.delete_message = AsyncMock(return_value='msg-123')

    result = await discord_api.delete('msg-123')

    # Method returns what client.delete_message returns
    assert result == 'msg-123'
    discord_api.client.delete_message.assert_called_once()


# Share Tests

@pytest.mark.asyncio
async def test_discord_api_share_not_supported(discord_api):
    """Test DiscordAPI share is not supported."""
    with pytest.raises(Exception, match='not supported'):
        await discord_api.share('msg-123')


# Error Handling Tests

@pytest.mark.asyncio
@patch('agoras.platforms.discord.api.DiscordAuthManager')
async def test_discord_api_not_authenticated(mock_auth_class):
    """Test DiscordAPI requires authentication."""
    api = DiscordAPI('token', 'Server', 'channel')
    api._authenticated = False

    with pytest.raises(Exception):
        await api.post('Test')


@pytest.mark.asyncio
async def test_discord_api_handles_error(discord_api):
    """Test DiscordAPI handles errors gracefully."""
    discord_api.client = MagicMock()
    discord_api.client.send_message = AsyncMock(side_effect=Exception('Discord API error'))

    with pytest.raises(Exception, match='Discord API error'):
        await discord_api.post('Test')
