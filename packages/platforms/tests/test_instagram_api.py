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

from agoras.platforms.instagram.api import InstagramAPI


@pytest.fixture
def instagram_api():
    """Fixture to create InstagramAPI instance."""
    with patch('agoras.platforms.instagram.api.InstagramAuthManager') as mock_auth_class:
        mock_auth = MagicMock()
        mock_auth.access_token = 'mock_token'
        mock_auth.user_id = 'user_id'
        mock_auth.ensure_authenticated = MagicMock()
        mock_auth_class.return_value = mock_auth

        api = InstagramAPI('user_id', 'client_id', 'client_secret')
        api._authenticated = True
        api.client = MagicMock()  # Mock the client
        api.client.create_media = AsyncMock(return_value='container-123')
        api.client.publish_media = AsyncMock(return_value='media-123')
        api.client.like_media = AsyncMock(return_value=True)
        api.client.delete_media = AsyncMock(return_value=True)
        yield api


# Authentication Tests

@pytest.mark.asyncio
@patch('agoras.platforms.instagram.api.InstagramAuthManager')
async def test_instagram_api_authenticate(mock_auth_class):
    """Test InstagramAPI authenticate method."""
    mock_auth = MagicMock()
    mock_auth.authenticate = AsyncMock()
    mock_auth.access_token = 'token123'
    mock_auth_class.return_value = mock_auth

    api = InstagramAPI('user_id', 'client_id', 'secret')
    result = await api.authenticate()

    assert api._authenticated is True
    assert result is api


@pytest.mark.asyncio
async def test_instagram_api_disconnect(instagram_api):
    """Test InstagramAPI disconnect method."""
    await instagram_api.disconnect()

    assert instagram_api._authenticated is False


# Container Tests

@pytest.mark.asyncio
async def test_instagram_api_create_media(instagram_api):
    """Test InstagramAPI create_media method."""
    result = await instagram_api.create_media('user_id', image_url='http://image.jpg', caption='Caption')

    assert result == 'container-123'
    instagram_api.client.create_media.assert_called_once()


@pytest.mark.asyncio
async def test_instagram_api_publish_media(instagram_api):
    """Test InstagramAPI publish_media method."""
    result = await instagram_api.publish_media('user_id', 'container-123')

    assert result == 'media-123'
    instagram_api.client.publish_media.assert_called_once()


# Post Tests

@pytest.mark.asyncio
async def test_instagram_api_post(instagram_api):
    """Test InstagramAPI post method."""
    # post() calls client.create_post
    instagram_api.client.create_post = AsyncMock(return_value='media-123')

    result = await instagram_api.post('user_id', image_url='http://image.jpg', caption='Caption')

    assert result == 'media-123'


# Like Tests - Not Supported

@pytest.mark.asyncio
async def test_instagram_api_like_not_supported(instagram_api):
    """Test InstagramAPI like raises not supported exception."""
    with pytest.raises(Exception, match='not supported'):
        await instagram_api.like('media-123')


# Share Tests - Not Supported

@pytest.mark.asyncio
async def test_instagram_api_share_not_supported(instagram_api):
    """Test InstagramAPI share raises not supported exception."""
    with pytest.raises(Exception, match='not supported'):
        await instagram_api.share('media-123')


# Delete Tests - Not Supported

@pytest.mark.asyncio
async def test_instagram_api_delete_not_supported(instagram_api):
    """Test InstagramAPI delete raises not supported exception."""
    with pytest.raises(Exception, match='not supported'):
        await instagram_api.delete('media-123')


# Error Handling Tests

@pytest.mark.asyncio
@patch('agoras.platforms.instagram.api.InstagramAuthManager')
async def test_instagram_api_not_authenticated(mock_auth_class):
    """Test InstagramAPI requires authentication."""
    api = InstagramAPI('user_id', 'client_id', 'secret')
    api._authenticated = False

    with pytest.raises(Exception):
        await api.post('Test', 'http://image.jpg')


@pytest.mark.asyncio
async def test_instagram_api_handles_error(instagram_api):
    """Test InstagramAPI handles API errors."""
    # Make the client.create_media raise an exception to test error handling
    instagram_api.client.create_media.side_effect = Exception('API Error')

    with pytest.raises(Exception, match='Instagram media creation'):
        await instagram_api.create_media('user_id', image_url='http://image.jpg', caption='Caption')
