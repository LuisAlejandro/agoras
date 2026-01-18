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

from agoras.platforms.facebook.api import FacebookAPI


@pytest.fixture
def facebook_api():
    """Fixture to create FacebookAPI instance."""
    with patch('agoras.platforms.facebook.api.FacebookAuthManager') as mock_auth_class:
        mock_auth = MagicMock()
        mock_auth.access_token = 'mock_token'
        mock_auth.page_id = 'page_id'
        mock_auth.ensure_authenticated = MagicMock()
        mock_auth_class.return_value = mock_auth

        api = FacebookAPI('page_id', 'client_id', 'client_secret')
        api._authenticated = True
        api.client = MagicMock()  # Mock the client
        api.client.create_post = AsyncMock(return_value='post-123')
        api.client.upload_media = AsyncMock(return_value={'id': 'media-123'})
        api.client.like_post = AsyncMock(return_value={'success': True})
        api.client.share_post = AsyncMock(return_value='share-123')
        api.client.delete_post = AsyncMock(return_value={'success': True})
        yield api


# Authentication Tests

@pytest.mark.asyncio
@patch('agoras.platforms.facebook.api.FacebookAuthManager')
async def test_facebook_api_authenticate(mock_auth_class):
    """Test FacebookAPI authenticate method."""
    mock_auth = MagicMock()
    mock_auth.authenticate = AsyncMock()
    mock_auth.access_token = 'token123'
    mock_auth_class.return_value = mock_auth

    api = FacebookAPI('page_id', 'client_id', 'secret')
    result = await api.authenticate()

    assert api._authenticated is True
    assert result is api


@pytest.mark.asyncio
async def test_facebook_api_disconnect(facebook_api):
    """Test FacebookAPI disconnect method."""
    await facebook_api.disconnect()

    assert facebook_api._authenticated is False


# Post Tests

@pytest.mark.asyncio
async def test_facebook_api_post(facebook_api):
    """Test FacebookAPI post method."""
    result = await facebook_api.post('page_id', message='Test post content')

    assert result == 'post-123'
    facebook_api.client.create_post.assert_called_once()


@pytest.mark.asyncio
async def test_facebook_api_post_with_link(facebook_api):
    """Test FacebookAPI post with link."""
    result = await facebook_api.post('page_id', message='Check this out', link='http://link.com')

    assert result == 'post-123'


@pytest.mark.asyncio
async def test_facebook_api_post_photo(facebook_api):
    """Test FacebookAPI post photo."""
    result = await facebook_api.upload_media('page_id', 'http://image.jpg')

    assert result == {'id': 'media-123'}


# Video Tests

@pytest.mark.asyncio
async def test_facebook_api_upload_media(facebook_api):
    """Test FacebookAPI upload_media method."""
    result = await facebook_api.upload_media('page_id', 'http://video.mp4')

    assert result == {'id': 'media-123'}


# Like Tests

@pytest.mark.asyncio
async def test_facebook_api_like(facebook_api):
    """Test FacebookAPI like method."""
    facebook_api.client.like_post = AsyncMock(return_value={'success': True})

    result = await facebook_api.like('page_id', 'post-123')

    # Returns whatever client returns
    assert result is not None


# Share Tests

@pytest.mark.asyncio
async def test_facebook_api_share(facebook_api):
    """Test FacebookAPI share method."""
    facebook_api.client.share_post = AsyncMock(return_value='share-456')

    result = await facebook_api.share('profile_id', 'page_id', 'post-123')

    assert result == 'share-456'


# Delete Tests

@pytest.mark.asyncio
async def test_facebook_api_delete(facebook_api):
    """Test FacebookAPI delete method."""
    facebook_api.client.delete_post = AsyncMock(return_value={'success': True})

    result = await facebook_api.delete('page_id', 'post-123')

    # Returns whatever client returns
    assert result is not None


# Error Handling Tests

@pytest.mark.asyncio
@patch('agoras.platforms.facebook.api.FacebookAuthManager')
async def test_facebook_api_not_authenticated(mock_auth_class):
    """Test FacebookAPI requires authentication."""
    api = FacebookAPI('page_id', 'client_id', 'secret')
    api._authenticated = False

    with pytest.raises(Exception):
        await api.post('Test post')


@pytest.mark.asyncio
async def test_facebook_api_handles_error(facebook_api):
    """Test FacebookAPI handles client errors."""
    facebook_api.client.create_post = AsyncMock(side_effect=Exception('API Error'))

    with pytest.raises(Exception, match='API Error'):
        await facebook_api.post('page_id', message='Test post')


# Property Tests

def test_facebook_api_has_auth_manager():
    """Test FacebookAPI has auth manager."""
    with patch('agoras.platforms.facebook.api.FacebookAuthManager') as mock_auth_class:
        api = FacebookAPI('page_id', 'client_id', 'secret')

        assert api.auth_manager is not None
