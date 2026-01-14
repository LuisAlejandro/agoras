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

from agoras.platforms.linkedin.api import LinkedInAPI


@pytest.fixture
def linkedin_api():
    """Fixture to create LinkedInAPI instance with mocked auth."""
    with patch('agoras.platforms.linkedin.api.LinkedInAuthManager') as mock_auth_class:
        mock_auth = MagicMock()
        mock_auth.access_token = 'mock_access_token'
        mock_auth.user_id = 'user_id'
        mock_auth.client_id = 'client_id'
        mock_auth.client_secret = 'client_secret'
        mock_auth.user_info = {'object_id': 'user_id'}
        mock_auth.ensure_authenticated = MagicMock()  # Don't raise
        mock_auth_class.return_value = mock_auth

        api = LinkedInAPI('user_id', 'client_id', 'client_secret', 'refresh_token')
        api._authenticated = True
        api.client = MagicMock()  # Mock the client
        api.client.create_post = AsyncMock(return_value='post-123')
        api.client.like_post = AsyncMock(return_value={'id': 'like-123'})
        api.client.share_post = AsyncMock(return_value='share-123')
        api.client.delete_post = AsyncMock(return_value={'success': True})
        yield api


# Authentication Tests

@pytest.mark.asyncio
@patch('agoras.platforms.linkedin.api.LinkedInAuthManager')
async def test_linkedin_api_authenticate(mock_auth_class):
    """Test LinkedInAPI authenticate method."""
    mock_auth = MagicMock()
    mock_auth.authenticate = AsyncMock()
    mock_auth.access_token = 'token123'
    mock_auth_class.return_value = mock_auth

    api = LinkedInAPI('user_id', 'client_id', 'secret')
    result = await api.authenticate()

    assert api._authenticated is True
    assert result is api
    mock_auth.authenticate.assert_called_once()


@pytest.mark.asyncio
@patch('agoras.platforms.linkedin.api.LinkedInAuthManager')
async def test_linkedin_api_disconnect(mock_auth_class):
    """Test LinkedInAPI disconnect method."""
    mock_auth = MagicMock()
    mock_auth.disconnect = AsyncMock()
    mock_auth_class.return_value = mock_auth

    api = LinkedInAPI('user_id', 'client_id', 'secret')
    api._authenticated = True

    await api.disconnect()

    assert api._authenticated is False


# Post Tests

@pytest.mark.asyncio
async def test_linkedin_api_post(linkedin_api):
    """Test LinkedInAPI post method."""
    result = await linkedin_api.post('Test post content')

    assert result == 'post-123'
    linkedin_api.client.create_post.assert_called_once()


@pytest.mark.asyncio
async def test_linkedin_api_post_with_link(linkedin_api):
    """Test LinkedInAPI post with link."""
    result = await linkedin_api.post('Post with link', link='http://link.com')

    assert result == 'post-123'
    linkedin_api.client.create_post.assert_called_once()


# Like Tests

@pytest.mark.asyncio
async def test_linkedin_api_like(linkedin_api):
    """Test LinkedInAPI like method."""
    result = await linkedin_api.like('post-123')

    # Returns the result from client.like_post
    assert result == {'id': 'like-123'}
    linkedin_api.client.like_post.assert_called_once()


# Share Tests

@pytest.mark.asyncio
async def test_linkedin_api_share(linkedin_api):
    """Test LinkedInAPI share method."""
    result = await linkedin_api.share('post-123')

    assert result == 'share-123'
    linkedin_api.client.share_post.assert_called_once()


# Delete Tests

@pytest.mark.asyncio
async def test_linkedin_api_delete(linkedin_api):
    """Test LinkedInAPI delete method."""
    result = await linkedin_api.delete('post-123')

    # Returns the result from client.delete_post
    assert result == {'success': True}
    linkedin_api.client.delete_post.assert_called_once()


# Error Handling Tests

@pytest.mark.asyncio
async def test_linkedin_api_post_error_handling(linkedin_api):
    """Test LinkedInAPI handles client errors."""
    linkedin_api.client.create_post = AsyncMock(side_effect=Exception('Post failed'))

    with pytest.raises(Exception, match='Post failed'):
        await linkedin_api.post('Test post')


@pytest.mark.asyncio
async def test_linkedin_api_not_authenticated(linkedin_api):
    """Test LinkedInAPI methods require authentication."""
    linkedin_api._authenticated = False
    linkedin_api.auth_manager.ensure_authenticated = MagicMock(side_effect=Exception('Not authenticated'))

    with pytest.raises(Exception, match='Not authenticated'):
        await linkedin_api.post('Test post')


# Property Tests

def test_linkedin_api_properties():
    """Test LinkedInAPI property accessors."""
    with patch('agoras.platforms.linkedin.api.LinkedInAuthManager') as mock_auth_class:
        mock_auth = MagicMock()
        mock_auth.user_id = 'user123'
        mock_auth.client_id = 'client123'
        mock_auth.access_token = 'token123'
        mock_auth_class.return_value = mock_auth

        api = LinkedInAPI('user_id', 'client_id', 'secret')

        assert api.user_id == 'user123'
        assert api.client_id == 'client123'
        assert api.access_token == 'token123'
