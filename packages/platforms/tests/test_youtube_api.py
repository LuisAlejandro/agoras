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

from agoras.platforms.youtube.api import YouTubeAPI


@pytest.fixture
def youtube_api():
    """Fixture to create YouTubeAPI instance with mocked auth."""
    with patch('agoras.platforms.youtube.api.YouTubeAuthManager') as mock_auth_class:
        mock_auth = MagicMock()
        mock_auth.authenticate = AsyncMock()
        mock_auth.access_token = 'token'
        mock_auth.ensure_authenticated = MagicMock()  # Don't raise
        mock_auth.client = MagicMock()
        mock_auth_class.return_value = mock_auth

        api = YouTubeAPI('client_id', 'client_secret')
        api._authenticated = True
        api.client = MagicMock()
        api.client.upload_video = AsyncMock(return_value={'id': 'video-123'})
        api.client.like_video = AsyncMock()
        api.client.delete_video = AsyncMock()
        yield api


# Authentication Tests

@pytest.mark.asyncio
@patch('agoras.platforms.youtube.api.YouTubeAuthManager')
async def test_youtube_api_authenticate(mock_auth_class):
    """Test YouTubeAPI authenticate method."""
    mock_auth = MagicMock()
    mock_auth.authenticate = AsyncMock(return_value=True)
    mock_auth.access_token = 'token123'
    mock_auth.client = MagicMock()
    mock_auth_class.return_value = mock_auth

    api = YouTubeAPI('client_id', 'client_secret')
    result = await api.authenticate()

    assert api._authenticated is True
    assert result is api
    mock_auth.authenticate.assert_called_once()


@pytest.mark.asyncio
async def test_youtube_api_disconnect(youtube_api):
    """Test YouTubeAPI disconnect method."""
    youtube_api.client.disconnect = MagicMock()

    await youtube_api.disconnect()

    assert youtube_api._authenticated is False
    assert youtube_api.client is None


# Upload Tests

@pytest.mark.asyncio
async def test_youtube_api_upload_video(youtube_api):
    """Test YouTubeAPI upload_video with file."""
    result = await youtube_api.upload_video(
        video_file_path='/path/to/video.mp4',
        title='Test Video',
        description='Test Description',
        category_id='22',
        privacy_status='public'
    )

    assert result == {'id': 'video-123'}
    youtube_api.client.upload_video.assert_called_once()


@pytest.mark.asyncio
async def test_youtube_api_upload_video_with_metadata(youtube_api):
    """Test YouTubeAPI upload_video with metadata."""
    result = await youtube_api.upload_video(
        video_file_path='/path/to/video.mp4',
        title='Test Video',
        description='Test Description',
        category_id='22',
        privacy_status='public',
        keywords='test, video, youtube'
    )

    assert result == {'id': 'video-123'}
    youtube_api.client.upload_video.assert_called_once_with(
        video_file_path='/path/to/video.mp4',
        title='Test Video',
        description='Test Description',
        category_id='22',
        privacy_status='public',
        keywords='test, video, youtube'
    )


# Post Tests

@pytest.mark.asyncio
async def test_youtube_api_post_not_supported(youtube_api):
    """Test YouTubeAPI post method raises exception."""
    with pytest.raises(Exception, match='Regular posts not supported'):
        await youtube_api.post('Test post')


@pytest.mark.asyncio
async def test_youtube_api_post_with_description(youtube_api):
    """Test YouTubeAPI post method raises exception even with description."""
    with pytest.raises(Exception, match='Regular posts not supported'):
        await youtube_api.post('Test post', description='Description')


# Interaction Tests

@pytest.mark.asyncio
async def test_youtube_api_like(youtube_api):
    """Test YouTubeAPI like video."""
    await youtube_api.like('video-123')

    youtube_api.client.like_video.assert_called_once_with('video-123')


@pytest.mark.asyncio
async def test_youtube_api_delete(youtube_api):
    """Test YouTubeAPI delete video."""
    await youtube_api.delete('video-123')

    youtube_api.client.delete_video.assert_called_once_with('video-123')


@pytest.mark.asyncio
async def test_youtube_api_share_not_supported(youtube_api):
    """Test YouTubeAPI share is not supported."""
    with pytest.raises(Exception, match='Share not supported'):
        await youtube_api.share('video-123')


# Error Handling Tests

@pytest.mark.asyncio
async def test_youtube_api_not_authenticated(youtube_api):
    """Test YouTubeAPI methods require authentication."""
    youtube_api._authenticated = False
    youtube_api.auth_manager.ensure_authenticated = MagicMock(side_effect=Exception('Not authenticated'))

    with pytest.raises(Exception, match='Not authenticated'):
        await youtube_api.upload_video(
            video_file_path='/path/to/video.mp4',
            title='Test',
            description='Test',
            category_id='22',
            privacy_status='public'
        )


@pytest.mark.asyncio
async def test_youtube_api_upload_error(youtube_api):
    """Test YouTubeAPI handles upload errors."""
    youtube_api.client.upload_video = AsyncMock(side_effect=Exception('Upload failed'))

    with pytest.raises(Exception, match='Upload failed'):
        await youtube_api.upload_video(
            video_file_path='/path/to/video.mp4',
            title='Test',
            description='Test',
            category_id='22',
            privacy_status='public'
        )


@pytest.mark.asyncio
async def test_youtube_api_error_handling(youtube_api):
    """Test YouTubeAPI handles API errors."""
    youtube_api.client.like_video = AsyncMock(side_effect=Exception('API error'))

    with pytest.raises(Exception, match='API error'):
        await youtube_api.like('video-123')


# Property Tests

def test_youtube_api_properties():
    """Test YouTubeAPI property accessors."""
    with patch('agoras.platforms.youtube.api.YouTubeAuthManager') as mock_auth_class:
        mock_auth = MagicMock()
        mock_auth.client_id = 'client123'
        mock_auth.client_secret = 'secret123'
        mock_auth.access_token = 'token123'
        mock_auth.user_info = {'id': 'user123'}
        mock_auth_class.return_value = mock_auth

        api = YouTubeAPI('client_id', 'client_secret')

        assert api.client_id == 'client123'
        assert api.client_secret == 'secret123'
        assert api.access_token == 'token123'
        assert api.user_info == {'id': 'user123'}
