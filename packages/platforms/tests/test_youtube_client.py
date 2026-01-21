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

from unittest.mock import MagicMock, patch

import pytest
from apiclient import errors

from agoras.platforms.youtube.client import YouTubeAPIClient


def test_youtube_client_init():
    """Test YouTubeAPIClient initialization."""
    client = YouTubeAPIClient('access_token')

    assert client.access_token == 'access_token'
    assert client.youtube_client is None
    assert client._authenticated is False


@pytest.mark.asyncio
@patch('apiclient.discovery.build')
@patch('agoras.platforms.youtube.client.httplib2.Http')
async def test_youtube_client_authenticate_success(mock_http_class, mock_discovery_build):
    """Test YouTubeAPIClient authenticate success."""
    mock_http = MagicMock()
    mock_http_class.return_value = mock_http

    mock_youtube_client = MagicMock()
    mock_discovery_build.return_value = mock_youtube_client

    client = YouTubeAPIClient('access_token')

    # Mock asyncio.to_thread to return the discovery.build result
    with patch('agoras.platforms.youtube.client.asyncio.to_thread', return_value=mock_youtube_client):
        result = await client.authenticate()

    assert result is True
    assert client._authenticated is True
    assert client.youtube_client == mock_youtube_client


@pytest.mark.asyncio
async def test_youtube_client_authenticate_already():
    """Test YouTubeAPIClient authenticate when already authenticated."""
    client = YouTubeAPIClient('access_token')
    client._authenticated = True

    result = await client.authenticate()

    assert result is True


@pytest.mark.asyncio
async def test_youtube_client_authenticate_no_token():
    """Test YouTubeAPIClient authenticate raises error without token."""
    client = YouTubeAPIClient('')

    with pytest.raises(Exception, match='YouTube access token is required'):
        await client.authenticate()


@pytest.mark.asyncio
@patch('apiclient.discovery.build')
@patch('agoras.platforms.youtube.client.httplib2.Http')
async def test_youtube_client_authenticate_failure(mock_http_class, mock_discovery_build):
    """Test YouTubeAPIClient authenticate handles discovery errors."""
    mock_discovery_build.side_effect = Exception('Discovery error')

    client = YouTubeAPIClient('access_token')

    with patch('agoras.platforms.youtube.client.asyncio.to_thread', side_effect=Exception('Discovery error')):
        with pytest.raises(Exception, match='YouTube client authentication failed: Discovery error'):
            await client.authenticate()


def test_youtube_client_disconnect():
    """Test YouTubeAPIClient disconnect method."""
    client = YouTubeAPIClient('access_token')
    mock_client = MagicMock()
    client.youtube_client = mock_client
    client._authenticated = True

    client.disconnect()

    assert client.youtube_client is None
    assert client._authenticated is False


def test_youtube_client_simplify_upload_success():
    """Test _simplify_upload_method with successful response."""
    client = YouTubeAPIClient('access_token')

    mock_request = MagicMock()
    mock_response = {'id': 'vid123'}
    mock_request.next_chunk.return_value = (None, mock_response)

    response, error, retry = client._simplify_upload_method(mock_request, 0, "")

    assert response == mock_response
    assert error is None
    assert retry == 0


def test_youtube_client_simplify_upload_http_error_retriable():
    """Test _simplify_upload_method with retriable HTTP error."""
    client = YouTubeAPIClient('access_token')

    mock_request = MagicMock()
    mock_http_error = errors.HttpError(MagicMock(status=503), b'')
    mock_request.next_chunk.side_effect = mock_http_error

    response, error, retry = client._simplify_upload_method(mock_request, 0, "")

    assert response is None
    assert "A retriable HTTP error 503 occurred" in error
    assert retry == 0


def test_youtube_client_simplify_upload_retriable_exception():
    """Test _simplify_upload_method with retriable exception."""
    client = YouTubeAPIClient('access_token')

    mock_request = MagicMock()
    mock_request.next_chunk.side_effect = IOError('Network error')

    response, error, retry = client._simplify_upload_method(mock_request, 0, "")

    assert response is None
    assert "A retriable error occurred: Network error" in error
    assert retry == 0


def test_youtube_client_handle_upload_retry_increments():
    """Test _handle_upload_retry increments retry counter."""
    client = YouTubeAPIClient('access_token')

    with patch('agoras.platforms.youtube.client.time.sleep'):
        retry = client._handle_upload_retry(0, "Test error")

    assert retry == 1


def test_youtube_client_handle_upload_retry_max_raises():
    """Test _handle_upload_retry raises when max retries exceeded."""
    client = YouTubeAPIClient('access_token')

    with pytest.raises(Exception, match='No longer attempting to retry'):
        client._handle_upload_retry(client.MAX_RETRIES, "Test error")


@pytest.mark.asyncio
@patch('agoras.platforms.youtube.client.http.MediaFileUpload')
async def test_youtube_client_upload_video_success(mock_media_upload_class):
    """Test YouTubeAPIClient upload_video success."""
    mock_media_upload = MagicMock()
    mock_media_upload_class.return_value = mock_media_upload

    # Mock YouTube client structure
    mock_videos_insert = MagicMock()
    mock_videos_insert.next_chunk.return_value = (None, {'id': 'vid123'})
    mock_videos = MagicMock()
    mock_videos.insert.return_value = mock_videos_insert
    mock_youtube_client = MagicMock()
    mock_youtube_client.videos.return_value = mock_videos

    client = YouTubeAPIClient('access_token')
    client.youtube_client = mock_youtube_client
    client._authenticated = True

    result = await client.upload_video('video.mp4', 'Title', 'Description', '22', 'public')

    assert result == {'id': 'vid123'}
    mock_videos.insert.assert_called_once()


@pytest.mark.asyncio
async def test_youtube_client_upload_video_not_initialized():
    """Test YouTubeAPIClient upload_video raises when not initialized."""
    client = YouTubeAPIClient('access_token')

    with pytest.raises(Exception, match='YouTube client not initialized'):
        await client.upload_video('video.mp4', 'Title', 'Description', '22', 'public')


@pytest.mark.asyncio
async def test_youtube_client_like_video_success():
    """Test YouTubeAPIClient like_video success."""
    mock_videos_rate = MagicMock()
    mock_videos_rate.execute.return_value = None
    mock_videos = MagicMock()
    mock_videos.rate.return_value = mock_videos_rate
    mock_youtube_client = MagicMock()
    mock_youtube_client.videos.return_value = mock_videos

    client = YouTubeAPIClient('access_token')
    client.youtube_client = mock_youtube_client
    client._authenticated = True

    await client.like_video('vid123')

    mock_videos.rate.assert_called_once_with(id='vid123', rating='like')


@pytest.mark.asyncio
async def test_youtube_client_like_video_not_initialized():
    """Test YouTubeAPIClient like_video raises when not initialized."""
    client = YouTubeAPIClient('access_token')

    with pytest.raises(Exception, match='YouTube client not initialized'):
        await client.like_video('vid123')


@pytest.mark.asyncio
async def test_youtube_client_delete_video_success():
    """Test YouTubeAPIClient delete_video success."""
    mock_videos_delete = MagicMock()
    mock_videos_delete.execute.return_value = None
    mock_videos = MagicMock()
    mock_videos.delete.return_value = mock_videos_delete
    mock_youtube_client = MagicMock()
    mock_youtube_client.videos.return_value = mock_videos

    client = YouTubeAPIClient('access_token')
    client.youtube_client = mock_youtube_client
    client._authenticated = True

    await client.delete_video('vid123')

    mock_videos.delete.assert_called_once_with(id='vid123')


@pytest.mark.asyncio
async def test_youtube_client_delete_video_not_initialized():
    """Test YouTubeAPIClient delete_video raises when not initialized."""
    client = YouTubeAPIClient('access_token')

    with pytest.raises(Exception, match='YouTube client not initialized'):
        await client.delete_video('vid123')


@pytest.mark.asyncio
async def test_youtube_client_get_channel_info_success():
    """Test YouTubeAPIClient get_channel_info success."""
    mock_channels_list = MagicMock()
    mock_channels_list.execute.return_value = {
        'items': [{
            'id': 'UC123',
            'snippet': {'title': 'Test Channel'},
            'statistics': {
                'subscriberCount': '1000',
                'videoCount': '50',
                'viewCount': '10000'
            }
        }]
    }
    mock_channels = MagicMock()
    mock_channels.list.return_value = mock_channels_list
    mock_youtube_client = MagicMock()
    mock_youtube_client.channels.return_value = mock_channels

    client = YouTubeAPIClient('access_token')
    client.youtube_client = mock_youtube_client
    client._authenticated = True

    result = await client.get_channel_info()

    assert result == {
        'channel_id': 'UC123',
        'channel_title': 'Test Channel',
        'description': '',
        'subscriber_count': '1000',
        'video_count': '50',
        'view_count': '10000'
    }


@pytest.mark.asyncio
async def test_youtube_client_get_channel_info_no_items():
    """Test YouTubeAPIClient get_channel_info raises when no channel found."""
    mock_channels_list = MagicMock()
    mock_channels_list.execute.return_value = {'items': []}
    mock_channels = MagicMock()
    mock_channels.list.return_value = mock_channels_list
    mock_youtube_client = MagicMock()
    mock_youtube_client.channels.return_value = mock_channels

    client = YouTubeAPIClient('access_token')
    client.youtube_client = mock_youtube_client
    client._authenticated = True

    with pytest.raises(Exception, match='No YouTube channel found for authenticated user'):
        await client.get_channel_info()


@pytest.mark.asyncio
async def test_youtube_client_get_video_info_success():
    """Test YouTubeAPIClient get_video_info success."""
    mock_videos_list = MagicMock()
    mock_videos_list.execute.return_value = {
        'items': [{
            'id': 'vid123',
            'snippet': {
                'title': 'Test Video',
                'description': 'Test Description',
                'channelId': 'UC123',
                'channelTitle': 'Test Channel'
            },
            'status': {'privacyStatus': 'public'},
            'statistics': {
                'viewCount': '1000',
                'likeCount': '50',
                'commentCount': '10'
            }
        }]
    }
    mock_videos = MagicMock()
    mock_videos.list.return_value = mock_videos_list
    mock_youtube_client = MagicMock()
    mock_youtube_client.videos.return_value = mock_videos

    client = YouTubeAPIClient('access_token')
    client.youtube_client = mock_youtube_client
    client._authenticated = True

    result = await client.get_video_info('vid123')

    assert result == {
        'video_id': 'vid123',
        'title': 'Test Video',
        'description': 'Test Description',
        'channel_id': 'UC123',
        'channel_title': 'Test Channel',
        'privacy_status': 'public',
        'view_count': '1000',
        'like_count': '50',
        'comment_count': '10'
    }


@pytest.mark.asyncio
async def test_youtube_client_get_video_info_no_items():
    """Test YouTubeAPIClient get_video_info raises when video not found."""
    mock_videos_list = MagicMock()
    mock_videos_list.execute.return_value = {'items': []}
    mock_videos = MagicMock()
    mock_videos.list.return_value = mock_videos_list
    mock_youtube_client = MagicMock()
    mock_youtube_client.videos.return_value = mock_videos

    client = YouTubeAPIClient('access_token')
    client.youtube_client = mock_youtube_client
    client._authenticated = True

    with pytest.raises(Exception, match='Video vid123 not found'):
        await client.get_video_info('vid123')


@pytest.mark.asyncio
async def test_youtube_client_search_videos_success():
    """Test YouTubeAPIClient search_videos success."""
    mock_search_list = MagicMock()
    mock_search_list.execute.return_value = {'items': [], 'pageInfo': {}}
    mock_search = MagicMock()
    mock_search.list.return_value = mock_search_list
    mock_youtube_client = MagicMock()
    mock_youtube_client.search.return_value = mock_search

    client = YouTubeAPIClient('access_token')
    client.youtube_client = mock_youtube_client
    client._authenticated = True

    result = await client.search_videos('test query')

    assert 'items' in result
    assert 'pageInfo' in result


@pytest.mark.asyncio
async def test_youtube_client_search_videos_not_initialized():
    """Test YouTubeAPIClient search_videos raises when not initialized."""
    client = YouTubeAPIClient('access_token')

    with pytest.raises(Exception, match='YouTube client not initialized'):
        await client.search_videos('test query')
