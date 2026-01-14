# -*- coding: utf-8 -*-
#
# Please refer to AUTHORS.rst for a complete list of Copyright holders.
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

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from agoras.platforms.discord.client import DiscordAPIClient


# Initialization Tests

def test_discord_client_init():
    """Test DiscordAPIClient initialization."""
    client = DiscordAPIClient('bot_token', 'server_name', 'channel_name')

    assert client.bot_token == 'bot_token'
    assert client.server_name == 'server_name'
    assert client.channel_name == 'channel_name'
    assert client.client is None
    assert client._authenticated is False


# Authentication Tests

@pytest.mark.asyncio
@patch('agoras.platforms.discord.client.discord.Client')
@patch('agoras.platforms.discord.client.discord.Intents')
async def test_discord_client_authenticate(mock_intents_class, mock_client_class):
    """Test DiscordAPIClient authenticate method."""
    mock_client = AsyncMock()
    mock_client.login = AsyncMock()
    mock_client.wait_until_ready = AsyncMock()
    mock_client_class.return_value = mock_client
    mock_intents = MagicMock()
    mock_intents_class.all.return_value = mock_intents

    client = DiscordAPIClient('bot_token', 'server_name', 'channel_name')
    result = await client.authenticate()

    assert result is True
    assert client._authenticated is True
    assert client.client is mock_client
    mock_client_class.assert_called_once_with(intents=mock_intents)
    mock_client.login.assert_called_once_with('bot_token')
    mock_client.wait_until_ready.assert_called_once()


@pytest.mark.asyncio
async def test_discord_client_authenticate_already_authenticated():
    """Test DiscordAPIClient authenticate when already authenticated."""
    client = DiscordAPIClient('bot_token', 'server_name', 'channel_name')
    client._authenticated = True

    result = await client.authenticate()

    assert result is True


@pytest.mark.asyncio
async def test_discord_client_authenticate_missing_token():
    """Test DiscordAPIClient authenticate raises error without token."""
    client = DiscordAPIClient('', 'server_name', 'channel_name')

    with pytest.raises(Exception, match='bot token is required'):
        await client.authenticate()


@pytest.mark.asyncio
@patch('agoras.platforms.discord.client.discord.Client')
@patch('agoras.platforms.discord.client.discord.Intents')
async def test_discord_client_authenticate_failure(mock_intents_class, mock_client_class):
    """Test DiscordAPIClient authenticate handles Discord errors."""
    mock_client = AsyncMock()
    mock_client.login = AsyncMock(side_effect=Exception('Login failed'))
    mock_client_class.return_value = mock_client
    mock_intents = MagicMock()
    mock_intents_class.all.return_value = mock_intents

    client = DiscordAPIClient('bot_token', 'server_name', 'channel_name')

    with pytest.raises(Exception, match='authentication failed'):
        await client.authenticate()


# Disconnect Tests

def test_discord_client_disconnect():
    """Test DiscordAPIClient disconnect method."""
    client = DiscordAPIClient('bot_token', 'server_name', 'channel_name')
    mock_client = MagicMock()
    mock_client.is_closed.return_value = False
    mock_client.close = AsyncMock()
    client.client = mock_client
    client._authenticated = True

    client.disconnect()

    assert client.client is None
    assert client._authenticated is False


def test_discord_client_disconnect_already_closed():
    """Test DiscordAPIClient disconnect when client is already closed."""
    client = DiscordAPIClient('bot_token', 'server_name', 'channel_name')
    mock_client = MagicMock()
    mock_client.is_closed.return_value = True
    client.client = mock_client
    client._authenticated = True

    client.disconnect()

    assert client.client is None
    assert client._authenticated is False


def test_discord_client_disconnect_no_client():
    """Test DiscordAPIClient disconnect when client is None."""
    client = DiscordAPIClient('bot_token', 'server_name', 'channel_name')
    client.client = None
    client._authenticated = True

    client.disconnect()

    assert client.client is None
    assert client._authenticated is False


# Get Guild/Channel Tests

def test_discord_client_get_guild():
    """Test DiscordAPIClient _get_guild method."""
    client = DiscordAPIClient('bot_token', 'server_name', 'channel_name')
    mock_client = MagicMock()
    mock_guild = MagicMock()
    mock_guild.name = 'server_name'
    mock_client.guilds = [mock_guild]
    client.client = mock_client

    result = client._get_guild()

    assert result is mock_guild


def test_discord_client_get_guild_not_found():
    """Test DiscordAPIClient _get_guild raises error when guild not found."""
    client = DiscordAPIClient('bot_token', 'server_name', 'channel_name')
    mock_client = MagicMock()
    mock_guild = MagicMock()
    mock_guild.name = 'other_server'
    mock_client.guilds = [mock_guild]
    client.client = mock_client

    with pytest.raises(Exception, match='Guild server_name not found'):
        client._get_guild()


def test_discord_client_get_guild_no_client():
    """Test DiscordAPIClient _get_guild raises error when client not available."""
    client = DiscordAPIClient('bot_token', 'server_name', 'channel_name')

    with pytest.raises(Exception, match='client not available'):
        client._get_guild()


def test_discord_client_get_channel():
    """Test DiscordAPIClient _get_channel method."""
    client = DiscordAPIClient('bot_token', 'server_name', 'channel_name')
    mock_client = MagicMock()
    mock_guild = MagicMock()
    mock_guild.name = 'server_name'
    mock_channel = MagicMock()
    mock_channel.name = 'channel_name'
    mock_guild.text_channels = [mock_channel]
    mock_client.guilds = [mock_guild]
    client.client = mock_client

    result = client._get_channel()

    assert result is mock_channel


def test_discord_client_get_channel_not_found():
    """Test DiscordAPIClient _get_channel raises error when channel not found."""
    client = DiscordAPIClient('bot_token', 'server_name', 'channel_name')
    mock_client = MagicMock()
    mock_guild = MagicMock()
    mock_guild.name = 'server_name'
    mock_channel = MagicMock()
    mock_channel.name = 'other_channel'
    mock_guild.text_channels = [mock_channel]
    mock_client.guilds = [mock_guild]
    client.client = mock_client

    with pytest.raises(Exception, match='Text channel channel_name not found'):
        client._get_channel()


# Send Message Tests

@pytest.mark.asyncio
async def test_discord_client_send_message():
    """Test DiscordAPIClient send_message method."""
    client = DiscordAPIClient('bot_token', 'server_name', 'channel_name')
    mock_client = MagicMock()
    mock_guild = MagicMock()
    mock_guild.name = 'server_name'
    mock_channel = AsyncMock()
    mock_channel.name = 'channel_name'
    mock_message = MagicMock()
    mock_message.id = 123456789
    mock_channel.send = AsyncMock(return_value=mock_message)
    mock_guild.text_channels = [mock_channel]
    mock_client.guilds = [mock_guild]
    client.client = mock_client
    client._authenticated = True

    result = await client.send_message('Test message')

    assert result == '123456789'
    mock_channel.send.assert_called_once_with(content='Test message')


@pytest.mark.asyncio
async def test_discord_client_send_message_with_embeds():
    """Test DiscordAPIClient send_message with embeds."""
    client = DiscordAPIClient('bot_token', 'server_name', 'channel_name')
    mock_client = MagicMock()
    mock_guild = MagicMock()
    mock_guild.name = 'server_name'
    mock_channel = AsyncMock()
    mock_channel.name = 'channel_name'
    mock_message = MagicMock()
    mock_message.id = 123456789
    mock_channel.send = AsyncMock(return_value=mock_message)
    mock_guild.text_channels = [mock_channel]
    mock_client.guilds = [mock_guild]
    client.client = mock_client
    client._authenticated = True

    mock_embed = MagicMock()
    result = await client.send_message(embeds=[mock_embed])

    assert result == '123456789'
    mock_channel.send.assert_called_once_with(embeds=[mock_embed])


@pytest.mark.asyncio
async def test_discord_client_send_message_with_file():
    """Test DiscordAPIClient send_message with file."""
    client = DiscordAPIClient('bot_token', 'server_name', 'channel_name')
    mock_client = MagicMock()
    mock_guild = MagicMock()
    mock_guild.name = 'server_name'
    mock_channel = AsyncMock()
    mock_channel.name = 'channel_name'
    mock_message = MagicMock()
    mock_message.id = 123456789
    mock_channel.send = AsyncMock(return_value=mock_message)
    mock_guild.text_channels = [mock_channel]
    mock_client.guilds = [mock_guild]
    client.client = mock_client
    client._authenticated = True

    mock_file = MagicMock()
    result = await client.send_message(file=mock_file)

    assert result == '123456789'
    mock_channel.send.assert_called_once_with(file=mock_file)


@pytest.mark.asyncio
async def test_discord_client_send_message_empty():
    """Test DiscordAPIClient send_message with no parameters."""
    client = DiscordAPIClient('bot_token', 'server_name', 'channel_name')
    mock_client = MagicMock()
    mock_guild = MagicMock()
    mock_guild.name = 'server_name'
    mock_channel = AsyncMock()
    mock_channel.name = 'channel_name'
    mock_message = MagicMock()
    mock_message.id = 123456789
    mock_channel.send = AsyncMock(return_value=mock_message)
    mock_guild.text_channels = [mock_channel]
    mock_client.guilds = [mock_guild]
    client.client = mock_client
    client._authenticated = True

    result = await client.send_message()

    assert result == '123456789'
    mock_channel.send.assert_called_once_with()


@pytest.mark.asyncio
async def test_discord_client_send_message_not_authenticated():
    """Test DiscordAPIClient send_message raises error when not authenticated."""
    client = DiscordAPIClient('bot_token', 'server_name', 'channel_name')

    with pytest.raises(Exception, match='not authenticated'):
        await client.send_message('Test')


@pytest.mark.asyncio
async def test_discord_client_send_message_error_handling():
    """Test DiscordAPIClient send_message handles errors."""
    client = DiscordAPIClient('bot_token', 'server_name', 'channel_name')
    mock_client = MagicMock()
    mock_guild = MagicMock()
    mock_guild.name = 'server_name'
    mock_channel = AsyncMock()
    mock_channel.name = 'channel_name'
    mock_channel.send = AsyncMock(side_effect=Exception('Send failed'))
    mock_guild.text_channels = [mock_channel]
    mock_client.guilds = [mock_guild]
    client.client = mock_client
    client._authenticated = True

    with pytest.raises(Exception, match='send message failed'):
        await client.send_message('Test')


# Add Reaction Tests

@pytest.mark.asyncio
async def test_discord_client_add_reaction():
    """Test DiscordAPIClient add_reaction method."""
    client = DiscordAPIClient('bot_token', 'server_name', 'channel_name')
    mock_client = MagicMock()
    mock_guild = MagicMock()
    mock_guild.name = 'server_name'
    mock_channel = AsyncMock()
    mock_channel.name = 'channel_name'
    mock_message = AsyncMock()
    mock_message.add_reaction = AsyncMock()
    mock_channel.fetch_message = AsyncMock(return_value=mock_message)
    mock_guild.text_channels = [mock_channel]
    mock_client.guilds = [mock_guild]
    client.client = mock_client
    client._authenticated = True

    result = await client.add_reaction('123456789', '👍')

    assert result == '123456789'
    mock_channel.fetch_message.assert_called_once_with(123456789)
    mock_message.add_reaction.assert_called_once_with('👍')


@pytest.mark.asyncio
async def test_discord_client_add_reaction_default_emoji():
    """Test DiscordAPIClient add_reaction with default emoji."""
    client = DiscordAPIClient('bot_token', 'server_name', 'channel_name')
    mock_client = MagicMock()
    mock_guild = MagicMock()
    mock_guild.name = 'server_name'
    mock_channel = AsyncMock()
    mock_channel.name = 'channel_name'
    mock_message = AsyncMock()
    mock_message.add_reaction = AsyncMock()
    mock_channel.fetch_message = AsyncMock(return_value=mock_message)
    mock_guild.text_channels = [mock_channel]
    mock_client.guilds = [mock_guild]
    client.client = mock_client
    client._authenticated = True

    result = await client.add_reaction('123456789')

    assert result == '123456789'
    mock_message.add_reaction.assert_called_once_with('❤️')


@pytest.mark.asyncio
async def test_discord_client_add_reaction_error_handling():
    """Test DiscordAPIClient add_reaction handles errors."""
    client = DiscordAPIClient('bot_token', 'server_name', 'channel_name')
    mock_client = MagicMock()
    mock_guild = MagicMock()
    mock_guild.name = 'server_name'
    mock_channel = AsyncMock()
    mock_channel.name = 'channel_name'
    mock_channel.fetch_message = AsyncMock(side_effect=Exception('Fetch failed'))
    mock_guild.text_channels = [mock_channel]
    mock_client.guilds = [mock_guild]
    client.client = mock_client
    client._authenticated = True

    with pytest.raises(Exception, match='add reaction failed'):
        await client.add_reaction('123456789')


# Delete Message Tests

@pytest.mark.asyncio
async def test_discord_client_delete_message():
    """Test DiscordAPIClient delete_message method."""
    client = DiscordAPIClient('bot_token', 'server_name', 'channel_name')
    mock_client = MagicMock()
    mock_guild = MagicMock()
    mock_guild.name = 'server_name'
    mock_channel = AsyncMock()
    mock_channel.name = 'channel_name'
    mock_message = AsyncMock()
    mock_message.delete = AsyncMock()
    mock_channel.fetch_message = AsyncMock(return_value=mock_message)
    mock_guild.text_channels = [mock_channel]
    mock_client.guilds = [mock_guild]
    client.client = mock_client
    client._authenticated = True

    result = await client.delete_message('123456789')

    assert result == '123456789'
    mock_channel.fetch_message.assert_called_once_with(123456789)
    mock_message.delete.assert_called_once()


@pytest.mark.asyncio
async def test_discord_client_delete_message_error_handling():
    """Test DiscordAPIClient delete_message handles errors."""
    client = DiscordAPIClient('bot_token', 'server_name', 'channel_name')
    mock_client = MagicMock()
    mock_guild = MagicMock()
    mock_guild.name = 'server_name'
    mock_channel = AsyncMock()
    mock_channel.name = 'channel_name'
    mock_channel.fetch_message = AsyncMock(side_effect=Exception('Fetch failed'))
    mock_guild.text_channels = [mock_channel]
    mock_client.guilds = [mock_guild]
    client.client = mock_client
    client._authenticated = True

    with pytest.raises(Exception, match='delete message failed'):
        await client.delete_message('123456789')


# Upload File Tests

@pytest.mark.asyncio
@patch('agoras.platforms.discord.client.discord.File')
async def test_discord_client_upload_file(mock_file_class):
    """Test DiscordAPIClient upload_file method."""
    client = DiscordAPIClient('bot_token', 'server_name', 'channel_name')
    mock_client = MagicMock()
    mock_guild = MagicMock()
    mock_guild.name = 'server_name'
    mock_channel = AsyncMock()
    mock_channel.name = 'channel_name'
    mock_message = MagicMock()
    mock_message.id = 123456789
    mock_channel.send = AsyncMock(return_value=mock_message)
    mock_guild.text_channels = [mock_channel]
    mock_client.guilds = [mock_guild]
    client.client = mock_client
    client._authenticated = True

    mock_file = MagicMock()
    mock_file_class.return_value = mock_file

    result = await client.upload_file(b'file_content', 'file.txt', content='File attached')

    assert result == '123456789'
    mock_file_class.assert_called_once_with(b'file_content', filename='file.txt')
    mock_channel.send.assert_called_once_with(file=mock_file, content='File attached')


@pytest.mark.asyncio
@patch('agoras.platforms.discord.client.discord.File')
async def test_discord_client_upload_file_with_embeds(mock_file_class):
    """Test DiscordAPIClient upload_file with embeds."""
    client = DiscordAPIClient('bot_token', 'server_name', 'channel_name')
    mock_client = MagicMock()
    mock_guild = MagicMock()
    mock_guild.name = 'server_name'
    mock_channel = AsyncMock()
    mock_channel.name = 'channel_name'
    mock_message = MagicMock()
    mock_message.id = 123456789
    mock_channel.send = AsyncMock(return_value=mock_message)
    mock_guild.text_channels = [mock_channel]
    mock_client.guilds = [mock_guild]
    client.client = mock_client
    client._authenticated = True

    mock_file = MagicMock()
    mock_file_class.return_value = mock_file
    mock_embed = MagicMock()

    result = await client.upload_file(b'file_content', 'file.txt', embeds=[mock_embed])

    assert result == '123456789'
    mock_channel.send.assert_called_once_with(file=mock_file, embeds=[mock_embed])


@pytest.mark.asyncio
async def test_discord_client_upload_file_error_handling():
    """Test DiscordAPIClient upload_file handles errors."""
    client = DiscordAPIClient('bot_token', 'server_name', 'channel_name')
    mock_client = MagicMock()
    mock_guild = MagicMock()
    mock_guild.name = 'server_name'
    mock_channel = AsyncMock()
    mock_channel.name = 'channel_name'
    mock_channel.send = AsyncMock(side_effect=Exception('Upload failed'))
    mock_guild.text_channels = [mock_channel]
    mock_client.guilds = [mock_guild]
    client.client = mock_client
    client._authenticated = True

    with patch('agoras.platforms.discord.client.discord.File'):
        with pytest.raises(Exception, match='file upload failed'):
            await client.upload_file(b'content', 'file.txt')


# Create Embed Tests

def test_discord_client_create_embed():
    """Test DiscordAPIClient create_embed method."""
    client = DiscordAPIClient('bot_token', 'server_name', 'channel_name')

    with patch('agoras.platforms.discord.client.discord.Embed') as mock_embed_class:
        mock_embed = MagicMock()
        mock_embed_class.return_value = mock_embed

        result = client.create_embed(title='Title', description='Description', url='http://url.com', image_url='http://image.jpg')

        assert result is mock_embed
        assert mock_embed.title == 'Title'
        assert mock_embed.description == 'Description'
        assert mock_embed.url == 'http://url.com'
        mock_embed.set_image.assert_called_once_with(url='http://image.jpg')


def test_discord_client_create_embed_minimal():
    """Test DiscordAPIClient create_embed with minimal parameters."""
    client = DiscordAPIClient('bot_token', 'server_name', 'channel_name')

    with patch('agoras.platforms.discord.client.discord.Embed') as mock_embed_class:
        mock_embed = MagicMock()
        mock_embed_class.return_value = mock_embed

        result = client.create_embed()

        assert result is mock_embed
        # Verify embed was created (no title/description set when not provided)
        mock_embed_class.assert_called_once()
