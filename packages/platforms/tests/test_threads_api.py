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

from agoras.platforms.threads.api import ThreadsAPI


@pytest.fixture
def threads_api():
    """Fixture to create ThreadsAPI instance with mocked auth."""
    with patch('agoras.platforms.threads.api.ThreadsAuthManager') as mock_auth_class:
        mock_auth = MagicMock()
        mock_auth.authenticate = AsyncMock()
        mock_auth.access_token = 'token'
        mock_auth.user_id = 'user123'
        mock_auth.ensure_authenticated = MagicMock()  # Don't raise
        mock_auth_class.return_value = mock_auth

        api = ThreadsAPI('app_id', 'app_secret', 'redirect_uri', 'refresh_token')
        api._authenticated = True
        api.client = MagicMock()
        api.client.create_post = MagicMock(return_value={'id': 'thread-123'})
        api.client.repost_post = MagicMock(return_value={'id': 'repost-123'})
        api.client.get_profile = MagicMock(return_value={'id': 'user123', 'username': 'testuser'})
        yield api


# Authentication Tests

@pytest.mark.asyncio
@patch('agoras.platforms.threads.api.ThreadsAuthManager')
async def test_threads_api_authenticate(mock_auth_class):
    """Test ThreadsAPI authenticate method."""
    mock_auth = MagicMock()
    mock_auth.authenticate = AsyncMock(return_value=True)
    mock_auth.access_token = 'token123'
    mock_auth.client = MagicMock()
    mock_auth_class.return_value = mock_auth

    api = ThreadsAPI('app_id', 'app_secret', 'redirect_uri')
    result = await api.authenticate()

    assert api._authenticated is True
    assert result is api
    mock_auth.authenticate.assert_called_once()


@pytest.mark.asyncio
async def test_threads_api_disconnect(threads_api):
    """Test ThreadsAPI disconnect method."""
    await threads_api.disconnect()

    assert threads_api._authenticated is False
    assert threads_api.client is None


# Post Tests

@pytest.mark.asyncio
@patch('agoras.platforms.threads.api.MediaFactory')
async def test_threads_api_create_post_with_text(mock_media_factory, threads_api):
    """Test ThreadsAPI create_post with text."""
    result = await threads_api.create_post('Test post text')

    assert result == 'thread-123'
    threads_api.client.create_post.assert_called_once()


@pytest.mark.asyncio
@patch('agoras.platforms.threads.api.MediaFactory')
async def test_threads_api_create_post_with_images(mock_media_factory, threads_api):
    """Test ThreadsAPI create_post with images."""
    # Mock MediaFactory.download_images
    mock_image = MagicMock()
    mock_image.content = b'image_content'
    mock_image.file_type = MagicMock()
    mock_image.file_type.mime = 'image/jpeg'
    mock_image.url = 'http://image.jpg'
    mock_image.cleanup = MagicMock()
    mock_media_factory.download_images = AsyncMock(return_value=[mock_image])

    result = await threads_api.create_post('Test post', files=['http://image.jpg'])

    assert result == 'thread-123'
    threads_api.client.create_post.assert_called_once()
    mock_image.cleanup.assert_called()


@pytest.mark.asyncio
@patch('agoras.platforms.threads.api.MediaFactory')
async def test_threads_api_post_wrapper(mock_media_factory, threads_api):
    """Test ThreadsAPI post wrapper method."""
    result = await threads_api.post('Test post text')

    assert result == 'thread-123'
    threads_api.client.create_post.assert_called_once()


@pytest.mark.asyncio
@patch('agoras.platforms.threads.api.MediaFactory')
async def test_threads_api_create_post_with_hashtags(mock_media_factory, threads_api):
    """Test ThreadsAPI create_post with hashtags."""
    result = await threads_api.create_post('Test post #hashtag #test')

    assert result == 'thread-123'
    threads_api.client.create_post.assert_called_once()


# Interaction Tests

@pytest.mark.asyncio
async def test_threads_api_like_not_supported(threads_api):
    """Test ThreadsAPI like is not supported."""
    with pytest.raises(Exception, match='Like not supported'):
        await threads_api.like('thread-123')


@pytest.mark.asyncio
async def test_threads_api_delete_not_supported(threads_api):
    """Test ThreadsAPI delete is not supported."""
    with pytest.raises(Exception, match='Delete not supported'):
        await threads_api.delete('thread-123')


@pytest.mark.asyncio
async def test_threads_api_share_repost(threads_api):
    """Test ThreadsAPI share/repost thread."""
    result = await threads_api.share('thread-123')

    assert result == 'repost-123'
    threads_api.client.repost_post.assert_called_once_with(post_id='thread-123')


@pytest.mark.asyncio
async def test_threads_api_repost_post(threads_api):
    """Test ThreadsAPI repost_post method."""
    result = await threads_api.repost_post('thread-123')

    assert result == 'repost-123'
    threads_api.client.repost_post.assert_called_once_with(post_id='thread-123')


# Utility Tests

@pytest.mark.asyncio
async def test_threads_api_get_profile(threads_api):
    """Test ThreadsAPI get_profile method."""
    result = await threads_api.get_profile()

    assert result == {'id': 'user123', 'username': 'testuser'}
    threads_api.client.get_profile.assert_called_once()


@pytest.mark.asyncio
@patch('agoras.platforms.threads.api.MediaFactory')
async def test_threads_api_validate_and_download_images(mock_media_factory, threads_api):
    """Test ThreadsAPI _validate_and_download_images method."""
    # Mock MediaFactory.download_images
    mock_image = MagicMock()
    mock_image.content = b'image_content'
    mock_image.file_type = MagicMock()
    mock_image.file_type.mime = 'image/jpeg'
    mock_image.url = 'http://image.jpg'
    mock_image.cleanup = MagicMock()
    mock_media_factory.download_images = AsyncMock(return_value=[mock_image])

    validated_files, validated_captions, images = await threads_api._validate_and_download_images(
        ['http://image.jpg'], ['Caption']
    )

    assert len(validated_files) == 1
    assert validated_files[0] == 'http://image.jpg'
    assert len(validated_captions) == 1
    assert validated_captions[0] == 'Caption'
    assert len(images) == 1


# Error Handling Tests

@pytest.mark.asyncio
async def test_threads_api_not_authenticated(threads_api):
    """Test ThreadsAPI methods require authentication."""
    threads_api._authenticated = False
    threads_api.auth_manager.ensure_authenticated = MagicMock(side_effect=Exception('Not authenticated'))

    with pytest.raises(Exception, match='Not authenticated'):
        await threads_api.create_post('Test post')


@pytest.mark.asyncio
@patch('agoras.platforms.threads.api.MediaFactory')
async def test_threads_api_post_error(mock_media_factory, threads_api):
    """Test ThreadsAPI handles post errors."""
    threads_api.client.create_post = MagicMock(side_effect=Exception('Post failed'))

    with pytest.raises(Exception, match='Post failed'):
        await threads_api.create_post('Test post')


@pytest.mark.asyncio
async def test_threads_api_error_handling(threads_api):
    """Test ThreadsAPI handles API errors."""
    threads_api.client.get_profile = MagicMock(side_effect=Exception('API error'))

    with pytest.raises(Exception, match='API error'):
        await threads_api.get_profile()


# Property Tests

def test_threads_api_properties():
    """Test ThreadsAPI property accessors."""
    with patch('agoras.platforms.threads.api.ThreadsAuthManager') as mock_auth_class:
        mock_auth = MagicMock()
        mock_auth.access_token = 'token123'
        mock_auth.user_id = 'user123'
        mock_auth.user_info = {'id': 'user123', 'username': 'testuser'}
        mock_auth_class.return_value = mock_auth

        api = ThreadsAPI('app_id', 'app_secret', 'redirect_uri')

        assert api.access_token == 'token123'
        assert api.user_id == 'user123'
        assert api.user_info == {'id': 'user123', 'username': 'testuser'}
