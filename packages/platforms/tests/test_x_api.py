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

from agoras.platforms.x.api import XAPI


@pytest.fixture
def x_api():
    """Fixture to create XAPI instance with mocked auth."""
    with patch('agoras.platforms.x.api.XAuthManager') as mock_auth_class:
        mock_auth = MagicMock()
        mock_auth.authenticate = AsyncMock()
        mock_auth.consumer_key = 'consumer_key'
        mock_auth.consumer_secret = 'consumer_secret'
        mock_auth.oauth_token = 'oauth_token'
        mock_auth.oauth_secret = 'oauth_secret'
        mock_auth_class.return_value = mock_auth

        api = XAPI('consumer_key', 'consumer_secret', 'oauth_token', 'oauth_secret')
        api._authenticated = True
        api.client = MagicMock()
        # Make client methods async with proper return values
        mock_tweet_response = MagicMock()
        mock_tweet_response.data = {'id': 'tweet-123'}
        api.client.create_tweet = AsyncMock(return_value=mock_tweet_response)
        api.client.like_tweet = AsyncMock(return_value='tweet-123')
        api.client.retweet = AsyncMock(return_value=MagicMock(data={'id': 'retweet-456'}))
        api.client.delete_tweet = AsyncMock(return_value=MagicMock(data={}))
        api.client.upload_media = AsyncMock(return_value='media-123')
        yield api


# Authentication Tests

@pytest.mark.asyncio
@patch('agoras.platforms.x.api.XAuthManager')
@patch('agoras.platforms.x.client.XAPIClient')
async def test_x_api_authenticate(mock_client_class, mock_auth_class):
    """Test XAPI authenticate method."""
    mock_auth = MagicMock()
    mock_auth.authenticate = AsyncMock()
    mock_auth_class.return_value = mock_auth

    mock_client = MagicMock()
    mock_client.authenticate = AsyncMock()
    mock_client_class.return_value = mock_client

    api = XAPI('key', 'secret', 'token', 'token_secret')
    result = await api.authenticate()

    assert api._authenticated is True
    assert result is api


@pytest.mark.asyncio
async def test_x_api_disconnect(x_api):
    """Test XAPI disconnect method."""
    x_api.client = MagicMock()

    await x_api.disconnect()

    assert x_api._authenticated is False


# Tweet Tests

@pytest.mark.asyncio
async def test_x_api_post(x_api):
    """Test XAPI post method (create tweet)."""
    result = await x_api.post('Hello Twitter')

    # Method returns result.data['id']
    assert result.data['id'] == 'tweet-123'


@pytest.mark.asyncio
async def test_x_api_post_with_media(x_api):
    """Test XAPI post with media."""
    result = await x_api.post('Tweet with image', media_ids=['media-123'])

    # Method returns result.data['id']
    assert result.data['id'] == 'tweet-123'


# Like Tests

@pytest.mark.asyncio
async def test_x_api_like(x_api):
    """Test XAPI like method."""
    result = await x_api.like('tweet-123')

    # Method returns what client.like_tweet returns
    assert result == 'tweet-123'
    x_api.client.like_tweet.assert_called_once()


# Retweet (Share) Tests

@pytest.mark.asyncio
async def test_x_api_share(x_api):
    """Test XAPI share method (retweet)."""
    mock_result = MagicMock()
    mock_result.data = {'id': 'retweet-456'}
    x_api.client.retweet = AsyncMock(return_value=mock_result)

    result = await x_api.share('tweet-123')

    # Method returns the full result object
    assert result.data['id'] == 'retweet-456'


# Delete Tests

@pytest.mark.asyncio
async def test_x_api_delete(x_api):
    """Test XAPI delete method."""
    mock_result = MagicMock()
    mock_result.data = {}
    x_api.client.delete_tweet = AsyncMock(return_value=mock_result)

    result = await x_api.delete('tweet-123')

    # Method returns the full result object
    assert result is not None
    x_api.client.delete_tweet.assert_called_once()


# Error Handling Tests

@pytest.mark.asyncio
@patch('agoras.platforms.x.api.XAuthManager')
async def test_x_api_post_not_authenticated(mock_auth_class):
    """Test XAPI requires authentication."""
    api = XAPI('key', 'secret', 'token', 'token_secret')
    api._authenticated = False

    with pytest.raises(Exception):
        await api.post('Test tweet')


@pytest.mark.asyncio
async def test_x_api_handles_error(x_api):
    """Test XAPI handles Twitter errors."""
    x_api.client.create_tweet = AsyncMock(side_effect=Exception('Twitter API error'))

    with pytest.raises(Exception, match='Twitter API error'):
        await x_api.post('Test')


# Property Tests

@patch('agoras.platforms.x.api.XAuthManager')
def test_x_api_has_auth_manager(mock_auth_class):
    """Test XAPI has auth manager."""
    api = XAPI('consumer_key', 'consumer_secret', 'oauth_token', 'oauth_secret')

    assert api.auth_manager is not None
