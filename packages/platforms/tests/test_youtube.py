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
@patch('agoras.platforms.youtube.auth.YouTubeAuthManager')
async def test_youtube_initialize_client_missing_credentials(mock_auth_manager_class):
    """Test YouTube _initialize_client raises exception without credentials."""
    # Mock auth manager to not load from storage
    mock_auth_manager = MagicMock()
    mock_auth_manager._load_credentials_from_storage = MagicMock(return_value=False)
    mock_auth_manager_class.return_value = mock_auth_manager

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


# Additional YouTube Wrapper Tests

@pytest.mark.asyncio
@patch('agoras.platforms.youtube.wrapper.YouTubeAPI')
async def test_youtube_post_raises(mock_api_class):
    """Test YouTube post raises exception."""
    mock_api = MagicMock()
    mock_api.authenticate = AsyncMock()
    mock_api_class.return_value = mock_api

    youtube = YouTube(
        youtube_client_id='client_id',
        youtube_client_secret='secret'
    )

    await youtube._initialize_client()

    with pytest.raises(Exception, match="Regular posts not supported for YouTube"):
        await youtube.post('text', 'link')


@pytest.mark.asyncio
@patch('agoras.platforms.youtube.wrapper.YouTubeAPI')
async def test_youtube_like_no_api(mock_api_class):
    """Test YouTube like with no API initialized."""
    youtube = YouTube(
        youtube_client_id='client_id',
        youtube_client_secret='secret'
    )

    with pytest.raises(Exception, match="YouTube API not initialized"):
        await youtube.like('video123')


@pytest.mark.asyncio
@patch('agoras.platforms.youtube.wrapper.YouTubeAPI')
async def test_youtube_like_no_video_id(mock_api_class):
    """Test YouTube like with no video ID."""
    mock_api = MagicMock()
    mock_api.authenticate = AsyncMock()
    mock_api_class.return_value = mock_api

    youtube = YouTube(
        youtube_client_id='client_id',
        youtube_client_secret='secret'
    )

    await youtube._initialize_client()

    with pytest.raises(Exception, match="YouTube video ID is required"):
        await youtube.like()


@pytest.mark.asyncio
@patch('agoras.platforms.youtube.wrapper.YouTubeAPI')
async def test_youtube_like_success(mock_api_class):
    """Test YouTube like success."""
    mock_api = MagicMock()
    mock_api.authenticate = AsyncMock()
    mock_api.like = AsyncMock()
    mock_api_class.return_value = mock_api

    youtube = YouTube(
        youtube_client_id='client_id',
        youtube_client_secret='secret'
    )

    await youtube._initialize_client()

    with patch.object(youtube, '_output_status'):
        result = await youtube.like('video123')

    assert result == 'video123'
    mock_api.like.assert_called_once_with('video123')


@pytest.mark.asyncio
@patch('agoras.platforms.youtube.wrapper.YouTubeAPI')
async def test_youtube_delete_no_api(mock_api_class):
    """Test YouTube delete with no API initialized."""
    youtube = YouTube(
        youtube_client_id='client_id',
        youtube_client_secret='secret'
    )

    with pytest.raises(Exception, match="YouTube API not initialized"):
        await youtube.delete('video123')


@pytest.mark.asyncio
@patch('agoras.platforms.youtube.wrapper.YouTubeAPI')
async def test_youtube_delete_no_video_id(mock_api_class):
    """Test YouTube delete with no video ID."""
    mock_api = MagicMock()
    mock_api.authenticate = AsyncMock()
    mock_api_class.return_value = mock_api

    youtube = YouTube(
        youtube_client_id='client_id',
        youtube_client_secret='secret'
    )

    await youtube._initialize_client()

    with pytest.raises(Exception, match="YouTube video ID is required"):
        await youtube.delete()


@pytest.mark.asyncio
@patch('agoras.platforms.youtube.wrapper.YouTubeAPI')
async def test_youtube_delete_success(mock_api_class):
    """Test YouTube delete success."""
    mock_api = MagicMock()
    mock_api.authenticate = AsyncMock()
    mock_api.delete = AsyncMock()
    mock_api_class.return_value = mock_api

    youtube = YouTube(
        youtube_client_id='client_id',
        youtube_client_secret='secret'
    )

    await youtube._initialize_client()

    with patch.object(youtube, '_output_status'):
        result = await youtube.delete('video123')

    assert result == 'video123'
    mock_api.delete.assert_called_once_with('video123')


@pytest.mark.asyncio
@patch('agoras.platforms.youtube.wrapper.YouTubeAPI')
async def test_youtube_share_raises(mock_api_class):
    """Test YouTube share raises exception."""
    mock_api = MagicMock()
    mock_api.authenticate = AsyncMock()
    mock_api_class.return_value = mock_api

    youtube = YouTube(
        youtube_client_id='client_id',
        youtube_client_secret='secret'
    )

    await youtube._initialize_client()

    with pytest.raises(Exception, match="Share not supported for YouTube"):
        await youtube.share('video123')


@pytest.mark.asyncio
@patch('agoras.platforms.youtube.wrapper.YouTubeAPI')
async def test_youtube_video_no_api(mock_api_class):
    """Test YouTube video with no API initialized."""
    youtube = YouTube(
        youtube_client_id='client_id',
        youtube_client_secret='secret'
    )

    with pytest.raises(Exception, match="YouTube API not initialized"):
        await youtube.video('text', 'url', 'title')


@pytest.mark.asyncio
@patch('agoras.platforms.youtube.wrapper.YouTubeAPI')
async def test_youtube_video_no_title_or_url(mock_api_class):
    """Test YouTube video with missing title or URL."""
    mock_api = MagicMock()
    mock_api.authenticate = AsyncMock()
    mock_api_class.return_value = mock_api

    youtube = YouTube(
        youtube_client_id='client_id',
        youtube_client_secret='secret'
    )

    await youtube._initialize_client()

    with pytest.raises(Exception, match="Video title and URL are required"):
        await youtube.video('text', '', 'title')

    with pytest.raises(Exception, match="Video title and URL are required"):
        await youtube.video('text', 'url', '')


@pytest.mark.asyncio
@patch('agoras.platforms.youtube.wrapper.YouTubeAPI')
async def test_youtube_video_invalid_mime(mock_api_class):
    """Test YouTube video with invalid MIME type."""
    mock_api = MagicMock()
    mock_api.authenticate = AsyncMock()
    mock_api_class.return_value = mock_api

    youtube = YouTube(
        youtube_client_id='client_id',
        youtube_client_secret='secret'
    )

    await youtube._initialize_client()

    with patch.object(youtube, 'download_video', new_callable=AsyncMock) as mock_download:
        mock_video = MagicMock()
        mock_video.content = b'video_content'
        mock_file_type = MagicMock()
        mock_file_type.mime = 'video/avi'  # Invalid MIME
        mock_video.file_type = mock_file_type
        mock_video.cleanup = MagicMock()
        mock_download.return_value = mock_video

        with pytest.raises(Exception, match="Invalid video type.*YouTube supports"):
            await youtube.video('text', 'url', 'title')


@pytest.mark.asyncio
@patch('agoras.platforms.youtube.wrapper.YouTubeAPI')
async def test_youtube_last_from_feed(mock_api_class):
    """Test YouTube last_from_feed method."""
    mock_api = MagicMock()
    mock_api.authenticate = AsyncMock()
    mock_api_class.return_value = mock_api

    youtube = YouTube(
        youtube_client_id='client_id',
        youtube_client_secret='secret'
    )

    await youtube._initialize_client()

    # Mock feed operations
    with patch.object(youtube, 'download_feed', new_callable=AsyncMock) as mock_download_feed, \
         patch.object(youtube, 'video', new_callable=AsyncMock) as mock_video:

        mock_feed = MagicMock()
        mock_item = MagicMock()
        mock_item.title = 'Test Video'
        mock_item.raw_item.enclosures = [MagicMock()]
        mock_item.raw_item.enclosures[0].url = 'http://video.mp4'
        mock_feed.get_items_since.return_value = [mock_item]
        mock_download_feed.return_value = mock_feed

        await youtube.last_from_feed('http://feed.xml', 5, 3600)

        mock_download_feed.assert_called_once_with('http://feed.xml')
        mock_feed.get_items_since.assert_called_once_with(3600)
        mock_video.assert_called_once_with('', 'http://video.mp4', 'Test Video')


@pytest.mark.asyncio
@patch('agoras.platforms.youtube.wrapper.YouTubeAPI')
async def test_youtube_random_from_feed(mock_api_class):
    """Test YouTube random_from_feed method."""
    mock_api = MagicMock()
    mock_api.authenticate = AsyncMock()
    mock_api_class.return_value = mock_api

    youtube = YouTube(
        youtube_client_id='client_id',
        youtube_client_secret='secret'
    )

    await youtube._initialize_client()

    # Mock feed operations
    with patch.object(youtube, 'download_feed', new_callable=AsyncMock) as mock_download_feed, \
         patch.object(youtube, 'video', new_callable=AsyncMock) as mock_video:

        mock_feed = MagicMock()
        mock_item = MagicMock()
        mock_item.title = 'Random Video'
        mock_item.raw_item.enclosures = [MagicMock()]
        mock_item.raw_item.enclosures[0].url = 'http://random.mp4'
        mock_feed.get_random_item.return_value = mock_item
        mock_download_feed.return_value = mock_feed

        await youtube.random_from_feed('http://feed.xml', 30)

        mock_download_feed.assert_called_once_with('http://feed.xml')
        mock_feed.get_random_item.assert_called_once_with(30)
        mock_video.assert_called_once_with('', 'http://random.mp4', 'Random Video')


@pytest.mark.asyncio
@patch('agoras.platforms.youtube.wrapper.YouTubeAPI')
async def test_youtube_schedule(mock_api_class):
    """Test YouTube schedule method."""
    mock_api = MagicMock()
    mock_api.authenticate = AsyncMock()
    mock_api_class.return_value = mock_api

    youtube = YouTube(
        youtube_client_id='client_id',
        youtube_client_secret='secret'
    )

    await youtube._initialize_client()

    # Mock schedule operations
    with patch.object(youtube, 'create_schedule_sheet', new_callable=AsyncMock) as mock_create_sheet, \
         patch.object(youtube, 'video', new_callable=AsyncMock) as mock_video:

        mock_sheet = MagicMock()
        mock_videos = [{
            'youtube_title': 'Scheduled Video',
            'youtube_description': 'Desc',
            'youtube_video_url': 'http://scheduled.mp4',
            'youtube_category_id': '22',
            'youtube_privacy_status': 'unlisted',
            'youtube_keywords': 'test'
        }]
        mock_sheet.process_scheduled_posts = AsyncMock(return_value=mock_videos)
        mock_create_sheet.return_value = mock_sheet

        await youtube.schedule('sheet_id', 'sheet_name', 'email', 'key', 10)

        mock_create_sheet.assert_called_once_with('sheet_id', 'sheet_name', 'email', 'key')
        mock_sheet.process_scheduled_posts.assert_called_once_with(10)
        mock_video.assert_called_once_with('Desc', 'http://scheduled.mp4', 'Scheduled Video')


@pytest.mark.asyncio
@patch('agoras.platforms.youtube.wrapper.YouTubeAPI')
async def test_youtube_handle_like_action_missing_id(mock_api_class):
    """Test YouTube _handle_like_action with missing video ID."""
    mock_api = MagicMock()
    mock_api.authenticate = AsyncMock()
    mock_api_class.return_value = mock_api

    youtube = YouTube(
        youtube_client_id='client_id',
        youtube_client_secret='secret'
    )

    await youtube._initialize_client()

    with patch.object(youtube, '_get_config_value', return_value=''):
        with pytest.raises(Exception, match="YouTube video ID is required for like action"):
            await youtube._handle_like_action()


@pytest.mark.asyncio
@patch('agoras.platforms.youtube.wrapper.YouTubeAPI')
async def test_youtube_handle_delete_action_missing_id(mock_api_class):
    """Test YouTube _handle_delete_action with missing video ID."""
    mock_api = MagicMock()
    mock_api.authenticate = AsyncMock()
    mock_api_class.return_value = mock_api

    youtube = YouTube(
        youtube_client_id='client_id',
        youtube_client_secret='secret'
    )

    await youtube._initialize_client()

    with patch.object(youtube, '_get_config_value', return_value=''):
        with pytest.raises(Exception, match="YouTube video ID is required for delete action"):
            await youtube._handle_delete_action()


@pytest.mark.asyncio
@patch('agoras.platforms.youtube.wrapper.YouTubeAPI')
async def test_youtube_handle_video_action_missing_url(mock_api_class):
    """Test YouTube _handle_video_action with missing URL."""
    mock_api = MagicMock()
    mock_api.authenticate = AsyncMock()
    mock_api_class.return_value = mock_api

    youtube = YouTube(
        youtube_client_id='client_id',
        youtube_client_secret='secret'
    )

    await youtube._initialize_client()

    with patch.object(youtube, '_get_config_value', side_effect=['', '', 'title']):
        with pytest.raises(Exception, match="YouTube video URL is required for video action"):
            await youtube._handle_video_action()


@pytest.mark.asyncio
@patch('agoras.platforms.youtube.wrapper.YouTubeAPI')
async def test_youtube_handle_video_action_missing_title(mock_api_class):
    """Test YouTube _handle_video_action with missing title."""
    mock_api = MagicMock()
    mock_api.authenticate = AsyncMock()
    mock_api_class.return_value = mock_api

    youtube = YouTube(
        youtube_client_id='client_id',
        youtube_client_secret='secret'
    )

    await youtube._initialize_client()

    with patch.object(youtube, '_get_config_value', side_effect=['desc', 'url', '']):
        with pytest.raises(Exception, match="YouTube video title is required for video action"):
            await youtube._handle_video_action()


@pytest.mark.asyncio
@patch('agoras.platforms.youtube.wrapper.YouTubeAPI')
async def test_youtube_handle_share_action(mock_api_class):
    """Test YouTube _handle_share_action calls share (which raises)."""
    mock_api = MagicMock()
    mock_api.authenticate = AsyncMock()
    mock_api_class.return_value = mock_api

    youtube = YouTube(
        youtube_client_id='client_id',
        youtube_client_secret='secret'
    )

    await youtube._initialize_client()

    with pytest.raises(Exception, match="Share not supported for YouTube"):
        await youtube._handle_share_action()


@pytest.mark.asyncio
async def test_youtube_main_async_empty_action():
    """Test YouTube main_async with empty action."""
    from agoras.platforms.youtube.wrapper import main_async

    with pytest.raises(Exception, match="Action is a required argument"):
        await main_async({})


@pytest.mark.asyncio
@patch('agoras.platforms.youtube.wrapper.YouTube')
async def test_youtube_main_async_authorize(mock_youtube_class):
    """Test YouTube main_async with authorize action."""
    from agoras.platforms.youtube.wrapper import main_async

    mock_youtube = MagicMock()
    mock_youtube.authorize_credentials = AsyncMock(return_value=True)
    mock_youtube_class.return_value = mock_youtube

    result = await main_async({'action': 'authorize'})

    assert result == 0
    mock_youtube.authorize_credentials.assert_called_once()


@pytest.mark.asyncio
@patch('agoras.platforms.youtube.wrapper.YouTube')
async def test_youtube_main_async_execute_action(mock_youtube_class):
    """Test YouTube main_async with other actions."""
    from agoras.platforms.youtube.wrapper import main_async

    mock_youtube = MagicMock()
    mock_youtube.execute_action = AsyncMock()
    mock_youtube.disconnect = AsyncMock()
    mock_youtube_class.return_value = mock_youtube

    result = await main_async({'action': 'video'})

    assert result is None
    mock_youtube.execute_action.assert_called_once_with('video')
    mock_youtube.disconnect.assert_called_once()
