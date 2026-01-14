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

from agoras.platforms.telegram import Telegram
from agoras.platforms.telegram.api import TelegramAPI
from agoras.platforms.telegram.auth import TelegramAuthManager
from agoras.platforms.telegram.client import TelegramAPIClient

# Telegram Wrapper Tests


@pytest.mark.asyncio
@patch('agoras.platforms.telegram.wrapper.TelegramAPI')
async def test_telegram_initialize_client(mock_api_class):
    """Test Telegram _initialize_client extracts config and creates API."""
    mock_api = MagicMock()
    mock_api.authenticate = AsyncMock()
    mock_api_class.return_value = mock_api

    telegram = Telegram(
        telegram_bot_token='test_token',
        telegram_chat_id='123456'
    )

    await telegram._initialize_client()

    assert telegram.telegram_bot_token == 'test_token'
    assert telegram.telegram_chat_id == '123456'
    assert telegram.api is mock_api
    mock_api.authenticate.assert_called_once()


@pytest.mark.asyncio
async def test_telegram_initialize_client_missing_token():
    """Test Telegram _initialize_client raises exception without token."""
    telegram = Telegram()

    with pytest.raises(Exception, match="Not authenticated. Please run 'agoras telegram authorize' first."):
        await telegram._initialize_client()


@pytest.mark.asyncio
async def test_telegram_initialize_client_missing_chat_id():
    """Test Telegram _initialize_client raises exception without chat ID."""
    telegram = Telegram(telegram_bot_token='token')

    with pytest.raises(Exception, match="Not authenticated. Please run 'agoras telegram authorize' first."):
        await telegram._initialize_client()


@pytest.mark.asyncio
@patch('agoras.platforms.telegram.wrapper.TelegramAPI')
async def test_telegram_post(mock_api_class):
    """Test Telegram post method."""
    mock_api = MagicMock()
    mock_api.authenticate = AsyncMock()
    mock_api.send_message = AsyncMock(return_value='message-456')
    mock_api_class.return_value = mock_api

    telegram = Telegram(
        telegram_bot_token='token',
        telegram_chat_id='123'
    )

    await telegram._initialize_client()

    # Mock _output_status to avoid print
    with patch.object(telegram, '_output_status'):
        result = await telegram.post('Hello Telegram', 'http://link.com')

    assert result == 'message-456'
    mock_api.send_message.assert_called_once()


@pytest.mark.asyncio
@patch('agoras.platforms.telegram.wrapper.TelegramAPI')
async def test_telegram_disconnect(mock_api_class):
    """Test Telegram disconnect method."""
    mock_api = MagicMock()
    mock_api.authenticate = AsyncMock()
    mock_api.disconnect = AsyncMock()
    mock_api_class.return_value = mock_api

    telegram = Telegram(
        telegram_bot_token='token',
        telegram_chat_id='123'
    )

    await telegram._initialize_client()
    await telegram.disconnect()

    mock_api.disconnect.assert_called_once()


# Telegram API Tests

def test_telegram_api_instantiation():
    """Test TelegramAPI can be instantiated."""
    api = TelegramAPI('token', 'chat_id')
    assert api is not None
    assert api.bot_token == 'token'


# Telegram Auth Tests (Abstract - test via concrete usage)

def test_telegram_auth_class_exists():
    """Test TelegramAuthManager class exists."""
    assert TelegramAuthManager is not None


# Telegram Client Tests

def test_telegram_client_class_exists():
    """Test TelegramAPIClient class exists."""
    assert TelegramAPIClient is not None
