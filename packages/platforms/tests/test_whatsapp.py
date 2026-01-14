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

from agoras.platforms.whatsapp import WhatsApp
from agoras.platforms.whatsapp.api import WhatsAppAPI
from agoras.platforms.whatsapp.auth import WhatsAppAuthManager
from agoras.platforms.whatsapp.client import WhatsAppAPIClient

# WhatsApp Wrapper Tests


@pytest.mark.asyncio
@patch('agoras.platforms.whatsapp.wrapper.WhatsAppAPI')
async def test_whatsapp_initialize_client(mock_api_class):
    """Test WhatsApp _initialize_client extracts config and creates API."""
    mock_api = MagicMock()
    mock_api.authenticate = AsyncMock()
    mock_api_class.return_value = mock_api

    whatsapp = WhatsApp(
        whatsapp_access_token='test_token',
        whatsapp_phone_number_id='123456',
        whatsapp_recipient='1234567890'
    )

    await whatsapp._initialize_client()

    assert whatsapp.whatsapp_access_token == 'test_token'
    assert whatsapp.whatsapp_phone_number_id == '123456'
    assert whatsapp.api is mock_api
    mock_api.authenticate.assert_called_once()


@pytest.mark.asyncio
async def test_whatsapp_initialize_client_missing_credentials():
    """Test WhatsApp _initialize_client raises exception without credentials."""
    whatsapp = WhatsApp()

    with pytest.raises(Exception, match="Not authenticated. Please run 'agoras whatsapp authorize' first."):
        await whatsapp._initialize_client()


@pytest.mark.asyncio
@patch('agoras.platforms.whatsapp.wrapper.WhatsAppAPI')
async def test_whatsapp_post(mock_api_class):
    """Test WhatsApp post method."""
    mock_api = MagicMock()
    mock_api.authenticate = AsyncMock()
    mock_api.send_message = AsyncMock(return_value='message-789')
    mock_api_class.return_value = mock_api

    whatsapp = WhatsApp(
        whatsapp_access_token='token',
        whatsapp_phone_number_id='123',
        whatsapp_recipient='1234567890'
    )

    await whatsapp._initialize_client()

    with patch.object(whatsapp, '_output_status'):
        result = await whatsapp.post('Hello WhatsApp', 'http://link.com')

    assert result == 'message-789'
    mock_api.send_message.assert_called_once()


@pytest.mark.asyncio
@patch('agoras.platforms.whatsapp.wrapper.WhatsAppAPI')
async def test_whatsapp_disconnect(mock_api_class):
    """Test WhatsApp disconnect method."""
    mock_api = MagicMock()
    mock_api.authenticate = AsyncMock()
    mock_api.disconnect = AsyncMock()
    mock_api_class.return_value = mock_api

    whatsapp = WhatsApp(
        whatsapp_access_token='token',
        whatsapp_phone_number_id='123',
        whatsapp_recipient='1234567890'
    )

    await whatsapp._initialize_client()
    await whatsapp.disconnect()

    mock_api.disconnect.assert_called_once()


# WhatsApp API Tests

def test_whatsapp_api_instantiation():
    """Test WhatsAppAPI can be instantiated."""
    api = WhatsAppAPI('token', 'phone_id')
    assert api is not None


# WhatsApp Auth Tests (Abstract - test via concrete usage)

def test_whatsapp_auth_class_exists():
    """Test WhatsAppAuthManager class exists."""
    assert WhatsAppAuthManager is not None


# WhatsApp Client Tests

def test_whatsapp_client_class_exists():
    """Test WhatsAppAPIClient class exists."""
    assert WhatsAppAPIClient is not None
