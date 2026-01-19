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

import os
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from agoras.platforms.x import X
from agoras.platforms.x.api import XAPI
from agoras.platforms.x.auth import XAuthManager
from agoras.platforms.x.client import XAPIClient

# X (Twitter) Wrapper Tests


@pytest.mark.asyncio
@patch('agoras.platforms.x.wrapper.XAPI')
async def test_x_initialize_client(mock_api_class):
    """Test X _initialize_client extracts config and creates API."""
    mock_api = MagicMock()
    mock_api.authenticate = AsyncMock()
    mock_api_class.return_value = mock_api

    x = X(
        twitter_consumer_key='test_key',
        twitter_consumer_secret='test_secret',
        twitter_oauth_token='access_token',
        twitter_oauth_secret='access_secret'
    )

    await x._initialize_client()

    assert x.twitter_consumer_key == 'test_key'
    assert x.api is mock_api
    mock_api.authenticate.assert_called_once()


@pytest.mark.asyncio
@patch('agoras.platforms.x.auth.XAuthManager._load_credentials_from_storage', return_value=False)
async def test_x_initialize_client_missing_credentials(mock_load):
    """Test X _initialize_client raises exception without credentials."""
    x = X()

    with pytest.raises(Exception):
        await x._initialize_client()


@pytest.mark.asyncio
@patch('agoras.platforms.x.wrapper.XAPI')
async def test_x_post(mock_api_class):
    """Test X post method (create tweet)."""
    mock_api = MagicMock()
    mock_api.authenticate = AsyncMock()
    mock_api.post = AsyncMock(return_value='tweet-123')
    mock_api_class.return_value = mock_api

    x = X(
        twitter_consumer_key='key',
        twitter_consumer_secret='secret',
        twitter_oauth_token='token',
        twitter_oauth_secret='token_secret'
    )

    await x._initialize_client()

    with patch.object(x, '_output_status'):
        result = await x.post('Hello X', 'http://link.com')

    assert result == 'tweet-123'


@pytest.mark.asyncio
@patch('agoras.platforms.x.wrapper.XAPI')
async def test_x_like(mock_api_class):
    """Test X like method."""
    mock_api = MagicMock()
    mock_api.authenticate = AsyncMock()
    mock_api.like = AsyncMock(return_value='tweet-123')
    mock_api_class.return_value = mock_api

    x = X(
        twitter_consumer_key='key',
        twitter_consumer_secret='secret',
        twitter_oauth_token='token',
        twitter_oauth_secret='token_secret'
    )

    await x._initialize_client()

    with patch.object(x, '_output_status'):
        result = await x.like('tweet-123')

    assert result == 'tweet-123'


@pytest.mark.asyncio
@patch('agoras.platforms.x.wrapper.XAPI')
async def test_x_disconnect(mock_api_class):
    """Test X disconnect method."""
    mock_api = MagicMock()
    mock_api.authenticate = AsyncMock()
    mock_api.disconnect = AsyncMock()
    mock_api_class.return_value = mock_api

    x = X(
        twitter_consumer_key='key',
        twitter_consumer_secret='secret',
        twitter_oauth_token='token',
        twitter_oauth_secret='token_secret'
    )

    await x._initialize_client()
    await x.disconnect()

    mock_api.disconnect.assert_called_once()


# X API Tests

def test_x_api_class_exists():
    """Test XAPI class exists."""
    assert XAPI is not None


# X Auth Tests (Abstract - test via concrete usage)

def test_x_auth_class_exists():
    """Test XAuthManager class exists."""
    assert XAuthManager is not None


# X Client Tests

def test_x_client_instantiation():
    """Test XAPIClient can be instantiated."""
    client = XAPIClient('api_key', 'api_secret', 'token', 'token_secret')
    assert client is not None
