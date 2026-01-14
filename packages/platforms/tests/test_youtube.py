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

from agoras.platforms.youtube import YouTube
from agoras.platforms.youtube.api import YouTubeAPI
from agoras.platforms.youtube.auth import YouTubeAuthManager
from agoras.platforms.youtube.client import YouTubeAPIClient

# YouTube Wrapper Tests


@pytest.mark.asyncio
@patch('agoras.platforms.youtube.wrapper.YouTubeAPI')
async def test_youtube_initialize_client(mock_api_class):
    """Test YouTube _initialize_client extracts config and creates API."""
    mock_api = MagicMock()
    mock_api.authenticate = AsyncMock()
    mock_api_class.return_value = mock_api

    youtube = YouTube(
        youtube_client_id='test_client_id',
        youtube_client_secret='test_secret'
    )

    await youtube._initialize_client()

    assert youtube.youtube_client_id == 'test_client_id'
    assert youtube.api is mock_api
    mock_api.authenticate.assert_called_once()


@pytest.mark.asyncio
async def test_youtube_initialize_client_missing_credentials():
    """Test YouTube _initialize_client raises exception without credentials."""
    youtube = YouTube()

    with pytest.raises(Exception, match="Not authenticated"):
        await youtube._initialize_client()


@pytest.mark.asyncio
@patch('agoras.platforms.youtube.wrapper.YouTubeAPI')
@patch('agoras.platforms.youtube.auth.YouTubeAuthManager')
async def test_youtube_initialize_client_loads_from_storage(mock_auth_manager_class, mock_api_class):
    """Test YouTube _initialize_client loads credentials from storage when not provided."""
    # Mock auth manager that loads from storage
    mock_auth_manager = MagicMock()
    mock_auth_manager.client_id = 'stored_client_id'
    mock_auth_manager.client_secret = 'stored_client_secret'
    mock_auth_manager.refresh_token = 'stored_refresh_token'
    mock_auth_manager._load_credentials_from_storage = MagicMock(return_value=True)
    mock_auth_manager_class.return_value = mock_auth_manager

    # Mock API
    mock_api = MagicMock()
    mock_api.authenticate = AsyncMock()
    mock_api_class.return_value = mock_api

    # Create YouTube instance with NO credentials
    youtube = YouTube()

    await youtube._initialize_client()

    # Verify credentials were loaded from storage
    assert youtube.youtube_client_id == 'stored_client_id'
    assert youtube.youtube_client_secret == 'stored_client_secret'
    assert youtube.api is mock_api
    mock_api.authenticate.assert_called_once()


@pytest.mark.asyncio
@patch('agoras.platforms.youtube.auth.YouTubeAuthManager')
async def test_youtube_authorize_credentials(mock_auth_manager_class):
    """Test YouTube authorize_credentials method."""
    mock_auth_manager = MagicMock()
    mock_auth_manager.authorize = AsyncMock(return_value="Authorization successful. Credentials stored securely.")
    mock_auth_manager_class.return_value = mock_auth_manager

    youtube = YouTube(
        youtube_client_id='client123',
        youtube_client_secret='secret123'
    )

    with patch('builtins.print'):
        result = await youtube.authorize_credentials()

    assert result is True
    mock_auth_manager.authorize.assert_called_once()


@pytest.mark.asyncio
@patch('agoras.platforms.youtube.auth.YouTubeAuthManager')
async def test_youtube_authorize_credentials_failure(mock_auth_manager_class):
    """Test YouTube authorize_credentials method when authorization fails."""
    mock_auth_manager = MagicMock()
    mock_auth_manager.authorize = AsyncMock(return_value=None)
    mock_auth_manager_class.return_value = mock_auth_manager

    youtube = YouTube(
        youtube_client_id='client123',
        youtube_client_secret='secret123'
    )

    result = await youtube.authorize_credentials()

    assert result is False
    mock_auth_manager.authorize.assert_called_once()


@pytest.mark.asyncio
@patch('agoras.platforms.youtube.wrapper.YouTubeAPI')
async def test_youtube_video(mock_api_class):
    """Test YouTube video method."""
    mock_api = MagicMock()
    mock_api.authenticate = AsyncMock()
    mock_api.upload_video = AsyncMock(return_value={'id': 'video-456'})
    mock_api_class.return_value = mock_api

    youtube = YouTube(
        youtube_client_id='client_id',
        youtube_client_secret='secret'
    )

    await youtube._initialize_client()

    # Mock download_video to avoid actual HTTP call
    with patch.object(youtube, 'download_video', new_callable=AsyncMock) as mock_download:
        mock_video = MagicMock()
        mock_video.content = b'video_content'
        mock_video.temp_file = '/tmp/video.mp4'
        mock_file_handle = MagicMock()
        mock_video.get_file_handle = MagicMock(return_value=mock_file_handle)
        mock_file_type = MagicMock()
        mock_file_type.mime = 'video/mp4'
        mock_video.file_type = mock_file_type
        mock_video.get_file_size = MagicMock(return_value=1024)
        mock_video.cleanup = MagicMock()
        mock_download.return_value = mock_video

        with patch.object(youtube, '_output_status'):
            result = await youtube.video('Video text', 'http://video.mp4', 'Video Title')

    assert result == 'video-456'


@pytest.mark.asyncio
@patch('agoras.platforms.youtube.wrapper.YouTubeAPI')
async def test_youtube_disconnect(mock_api_class):
    """Test YouTube disconnect method."""
    mock_api = MagicMock()
    mock_api.authenticate = AsyncMock()
    mock_api.disconnect = AsyncMock()
    mock_api_class.return_value = mock_api

    youtube = YouTube(
        youtube_client_id='client_id',
        youtube_client_secret='secret'
    )

    await youtube._initialize_client()
    await youtube.disconnect()

    mock_api.disconnect.assert_called_once()


# YouTube API Tests

def test_youtube_api_class_exists():
    """Test YouTubeAPI class exists."""
    assert YouTubeAPI is not None


# YouTube Auth Tests

def test_youtube_auth_class_exists():
    """Test YouTubeAuthManager class exists."""
    assert YouTubeAuthManager is not None


# YouTube Client Tests

def test_youtube_client_class_exists():
    """Test YouTubeAPIClient class exists."""
    assert YouTubeAPIClient is not None
