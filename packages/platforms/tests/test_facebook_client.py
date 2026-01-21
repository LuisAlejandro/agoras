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

from agoras.platforms.facebook.client import FacebookAPIClient


def test_facebook_client_init():
    """Test FacebookAPIClient initialization."""
    client = FacebookAPIClient('access_token')

    assert client.access_token == 'access_token'
    assert client.graph_api is None
    assert client._authenticated is False


@pytest.mark.asyncio
@patch('agoras.platforms.facebook.client.GraphAPI')
async def test_facebook_client_authenticate_success(mock_graph_api_class):
    """Test FacebookAPIClient authenticate success."""
    mock_graph_api = MagicMock()
    mock_graph_api_class.return_value = mock_graph_api

    client = FacebookAPIClient('access_token')
    result = await client.authenticate()

    assert result is True
    assert client._authenticated is True
    assert client.graph_api == mock_graph_api
    mock_graph_api_class.assert_called_once_with(access_token='access_token', version="21.0")


@pytest.mark.asyncio
async def test_facebook_client_authenticate_already():
    """Test FacebookAPIClient authenticate when already authenticated."""
    client = FacebookAPIClient('access_token')
    client._authenticated = True

    result = await client.authenticate()

    assert result is True


@pytest.mark.asyncio
async def test_facebook_client_authenticate_no_token():
    """Test FacebookAPIClient authenticate raises error without token."""
    client = FacebookAPIClient('')

    with pytest.raises(Exception, match='Facebook access token is required'):
        await client.authenticate()


@pytest.mark.asyncio
@patch('agoras.platforms.facebook.client.GraphAPI')
async def test_facebook_client_authenticate_failure(mock_graph_api_class):
    """Test FacebookAPIClient authenticate handles GraphAPI errors."""
    mock_graph_api_class.side_effect = Exception('GraphAPI error')

    client = FacebookAPIClient('access_token')

    with pytest.raises(Exception, match='Facebook client authentication failed: GraphAPI error'):
        await client.authenticate()


def test_facebook_client_disconnect():
    """Test FacebookAPIClient disconnect method."""
    client = FacebookAPIClient('access_token')
    mock_graph_api = MagicMock()
    client.graph_api = mock_graph_api
    client._authenticated = True

    client.disconnect()

    assert client.graph_api is None
    assert client._authenticated is False


@patch('agoras.platforms.facebook.client.GraphAPI')
def test_facebook_client_post_object_success(mock_graph_api_class):
    """Test FacebookAPIClient post_object success."""
    mock_graph_api = MagicMock()
    mock_graph_api.post_object.return_value = {'id': 'post123'}
    mock_graph_api_class.return_value = mock_graph_api

    client = FacebookAPIClient('access_token')
    client.graph_api = mock_graph_api
    client._authenticated = True

    result = client.post_object('user_id', 'feed', {'message': 'test'})

    assert result == {'id': 'post123'}
    mock_graph_api.post_object.assert_called_once_with(
        object_id='user_id',
        connection='feed',
        data={'message': 'test'}
    )


def test_facebook_client_post_object_not_initialized():
    """Test FacebookAPIClient post_object raises error when not initialized."""
    client = FacebookAPIClient('access_token')

    with pytest.raises(Exception, match='Facebook GraphAPI not initialized'):
        client.post_object('user_id', 'feed', {})


@patch('agoras.platforms.facebook.client.GraphAPI')
def test_facebook_client_post_object_exception(mock_graph_api_class):
    """Test FacebookAPIClient post_object handles GraphAPI errors."""
    mock_graph_api = MagicMock()
    mock_graph_api.post_object.side_effect = Exception('API error')
    mock_graph_api_class.return_value = mock_graph_api

    client = FacebookAPIClient('access_token')
    client.graph_api = mock_graph_api
    client._authenticated = True

    with pytest.raises(Exception, match='Facebook post_object failed: API error'):
        client.post_object('user_id', 'feed', {})


@patch('agoras.platforms.facebook.client.GraphAPI')
def test_facebook_client_delete_object_success(mock_graph_api_class):
    """Test FacebookAPIClient delete_object success."""
    mock_graph_api = MagicMock()
    mock_graph_api_class.return_value = mock_graph_api

    client = FacebookAPIClient('access_token')
    client.graph_api = mock_graph_api
    client._authenticated = True

    client.delete_object('object_id')

    mock_graph_api.delete_object.assert_called_once_with(object_id='object_id')


def test_facebook_client_delete_object_not_initialized():
    """Test FacebookAPIClient delete_object raises error when not initialized."""
    client = FacebookAPIClient('access_token')

    with pytest.raises(Exception, match='Facebook GraphAPI not initialized'):
        client.delete_object('object_id')


@patch('agoras.platforms.facebook.client.GraphAPI')
def test_facebook_client_delete_object_exception(mock_graph_api_class):
    """Test FacebookAPIClient delete_object handles GraphAPI errors."""
    mock_graph_api = MagicMock()
    mock_graph_api.delete_object.side_effect = Exception('Delete error')
    mock_graph_api_class.return_value = mock_graph_api

    client = FacebookAPIClient('access_token')
    client.graph_api = mock_graph_api
    client._authenticated = True

    with pytest.raises(Exception, match='Facebook delete_object failed: Delete error'):
        client.delete_object('object_id')


@patch('agoras.platforms.facebook.client.GraphAPI')
def test_facebook_client_get_object_success(mock_graph_api_class):
    """Test FacebookAPIClient get_object success."""
    mock_graph_api = MagicMock()
    mock_graph_api.get_object.return_value = {'id': 'obj123', 'name': 'Test'}
    mock_graph_api_class.return_value = mock_graph_api

    client = FacebookAPIClient('access_token')
    client.graph_api = mock_graph_api
    client._authenticated = True

    result = client.get_object('obj123')

    assert result == {'id': 'obj123', 'name': 'Test'}
    mock_graph_api.get_object.assert_called_once_with(object_id='obj123')


@patch('agoras.platforms.facebook.client.GraphAPI')
def test_facebook_client_get_object_with_fields(mock_graph_api_class):
    """Test FacebookAPIClient get_object with fields parameter."""
    mock_graph_api = MagicMock()
    mock_graph_api.get_object.return_value = {'id': 'obj123', 'name': 'Test'}
    mock_graph_api_class.return_value = mock_graph_api

    client = FacebookAPIClient('access_token')
    client.graph_api = mock_graph_api
    client._authenticated = True

    result = client.get_object('obj123', fields='id,name')

    assert result == {'id': 'obj123', 'name': 'Test'}
    mock_graph_api.get_object.assert_called_once_with(object_id='obj123', fields='id,name')


def test_facebook_client_get_object_not_initialized():
    """Test FacebookAPIClient get_object raises error when not initialized."""
    client = FacebookAPIClient('access_token')

    with pytest.raises(Exception, match='Facebook GraphAPI not initialized'):
        client.get_object('obj123')


@patch('agoras.platforms.facebook.client.GraphAPI')
def test_facebook_client_get_object_exception(mock_graph_api_class):
    """Test FacebookAPIClient get_object handles GraphAPI errors."""
    mock_graph_api = MagicMock()
    mock_graph_api.get_object.side_effect = Exception('Get error')
    mock_graph_api_class.return_value = mock_graph_api

    client = FacebookAPIClient('access_token')
    client.graph_api = mock_graph_api
    client._authenticated = True

    with pytest.raises(Exception, match='Facebook get_object failed: Get error'):
        client.get_object('obj123')


@pytest.mark.asyncio
@patch('agoras.platforms.facebook.client.GraphAPI')
async def test_facebook_client_is_page_true(mock_graph_api_class):
    """Test FacebookAPIClient is_page returns True for pages."""
    mock_graph_api = MagicMock()
    mock_graph_api.get_object.return_value = {'category': 'Business', 'about': 'About us'}
    mock_graph_api_class.return_value = mock_graph_api

    client = FacebookAPIClient('access_token')
    client.graph_api = mock_graph_api
    client._authenticated = True

    result = await client.is_page('page_id')

    assert result is True
    mock_graph_api.get_object.assert_called_once_with(
        object_id='page_id',
        fields='category,category_list,about'
    )


@pytest.mark.asyncio
@patch('agoras.platforms.facebook.client.GraphAPI')
async def test_facebook_client_is_page_false(mock_graph_api_class):
    """Test FacebookAPIClient is_page returns False for non-pages."""
    mock_graph_api = MagicMock()
    mock_graph_api.get_object.return_value = {'name': 'John Doe', 'about': 'About me'}
    mock_graph_api_class.return_value = mock_graph_api

    client = FacebookAPIClient('access_token')
    client.graph_api = mock_graph_api
    client._authenticated = True

    result = await client.is_page('user_id')

    assert result is False


@pytest.mark.asyncio
@patch('agoras.platforms.facebook.client.GraphAPI')
async def test_facebook_client_is_page_exception(mock_graph_api_class):
    """Test FacebookAPIClient is_page returns False on exception."""
    mock_graph_api = MagicMock()
    mock_graph_api.get_object.side_effect = Exception('Privacy error')
    mock_graph_api_class.return_value = mock_graph_api

    client = FacebookAPIClient('access_token')
    client.graph_api = mock_graph_api
    client._authenticated = True

    result = await client.is_page('private_id')

    assert result is False


@pytest.mark.asyncio
@patch('agoras.platforms.facebook.client.requests.get')
@patch('agoras.platforms.facebook.client.GraphAPI')
async def test_facebook_client_get_page_token_success(mock_graph_api_class, mock_requests_get):
    """Test FacebookAPIClient get_page_access_token success."""
    mock_graph_api = MagicMock()
    mock_graph_api_class.return_value = mock_graph_api

    mock_response = MagicMock()
    mock_response.json.return_value = {
        'data': [
            {'id': 'page123', 'access_token': 'page_token_123'},
            {'id': 'page456', 'access_token': 'page_token_456'}
        ]
    }
    mock_response.raise_for_status.return_value = None
    mock_requests_get.return_value = mock_response

    client = FacebookAPIClient('access_token')
    client.graph_api = mock_graph_api
    client._authenticated = True

    result = await client.get_page_access_token('page123', 'user_token')

    assert result == 'page_token_123'


@pytest.mark.asyncio
@patch('agoras.platforms.facebook.client.GraphAPI')
async def test_facebook_client_get_page_token_not_found(mock_graph_api_class):
    """Test FacebookAPIClient get_page_access_token raises when page not found."""
    mock_graph_api = MagicMock()
    mock_graph_api_class.return_value = mock_graph_api

    mock_response = MagicMock()
    mock_response.json.return_value = {'data': []}  # No pages
    mock_response.raise_for_status.return_value = None

    with patch('agoras.platforms.facebook.client.requests.get', return_value=mock_response):
        client = FacebookAPIClient('access_token')
        client.graph_api = mock_graph_api
        client._authenticated = True

        with pytest.raises(Exception, match="Page page123 not found in user accounts"):
            await client.get_page_access_token('page123', 'user_token')


@pytest.mark.asyncio
@patch('agoras.platforms.facebook.client.GraphAPI')
async def test_facebook_client_create_post(mock_graph_api_class):
    """Test FacebookAPIClient create_post success."""
    mock_graph_api = MagicMock()
    mock_graph_api.post_object.return_value = {'id': 'user_123'}
    mock_graph_api_class.return_value = mock_graph_api

    client = FacebookAPIClient('access_token')
    client.graph_api = mock_graph_api
    client._authenticated = True

    result = await client.create_post('user_id', message='Test post')

    assert result == '123'
    mock_graph_api.post_object.assert_called_once()
    call_args = mock_graph_api.post_object.call_args
    assert call_args[1]['object_id'] == 'user_id'
    assert call_args[1]['connection'] == 'feed'
    assert call_args[1]['data']['message'] == 'Test post'
    assert call_args[1]['data']['published'] is True


@pytest.mark.asyncio
@patch('agoras.platforms.facebook.client.GraphAPI')
async def test_facebook_client_upload_media(mock_graph_api_class):
    """Test FacebookAPIClient upload_media success."""
    mock_graph_api = MagicMock()
    mock_graph_api.post_object.return_value = {'id': 'media123', 'post_id': 'post123'}
    mock_graph_api_class.return_value = mock_graph_api

    client = FacebookAPIClient('access_token')
    client.graph_api = mock_graph_api
    client._authenticated = True

    result = await client.upload_media('page_id', 'http://image.jpg')

    assert result == {'id': 'media123', 'post_id': 'post123'}
    mock_graph_api.post_object.assert_called_once_with(
        object_id='page_id',
        connection='photos',
        data={'url': 'http://image.jpg', 'published': False}
    )


@pytest.mark.asyncio
@patch('agoras.platforms.facebook.client.GraphAPI')
async def test_facebook_client_like_post(mock_graph_api_class):
    """Test FacebookAPIClient like_post success."""
    mock_graph_api = MagicMock()
    mock_graph_api.post_object.return_value = {'success': True}
    mock_graph_api_class.return_value = mock_graph_api

    client = FacebookAPIClient('access_token')
    client.graph_api = mock_graph_api
    client._authenticated = True

    result = await client.like_post('user_id', 'post123')

    assert result == 'post123'
    mock_graph_api.post_object.assert_called_once_with(
        object_id='user_id_post123',
        connection='likes',
        data={}
    )


@pytest.mark.asyncio
@patch('agoras.platforms.facebook.client.GraphAPI')
async def test_facebook_client_delete_post(mock_graph_api_class):
    """Test FacebookAPIClient delete_post success."""
    mock_graph_api = MagicMock()
    mock_graph_api_class.return_value = mock_graph_api

    client = FacebookAPIClient('access_token')
    client.graph_api = mock_graph_api
    client._authenticated = True

    result = await client.delete_post('user_id', 'post123')

    assert result == 'post123'
    mock_graph_api.delete_object.assert_called_once_with(object_id='user_id_post123')


@pytest.mark.asyncio
@patch('agoras.platforms.facebook.client.GraphAPI')
async def test_facebook_client_share_post(mock_graph_api_class):
    """Test FacebookAPIClient share_post success."""
    mock_graph_api = MagicMock()
    mock_graph_api.post_object.return_value = {'id': 'user_456'}
    mock_graph_api_class.return_value = mock_graph_api

    client = FacebookAPIClient('access_token')
    client.graph_api = mock_graph_api
    client._authenticated = True

    result = await client.share_post('profile_id', 'original_user', 'post123')

    assert result == '456'
    mock_graph_api.post_object.assert_called_once()
    call_args = mock_graph_api.post_object.call_args
    assert call_args[1]['object_id'] == 'profile_id'
    assert call_args[1]['connection'] == 'feed'
    assert 'facebook.com/original_user/posts/post123' in call_args[1]['data']['link']


@pytest.mark.asyncio
@patch('agoras.platforms.facebook.client.requests.post')
@patch('agoras.platforms.facebook.client.GraphAPI')
async def test_facebook_client_upload_reel_or_story(mock_graph_api_class, mock_requests_post):
    """Test FacebookAPIClient upload_reel_or_story success."""
    # Mock GraphAPI for start request
    mock_graph_api = MagicMock()
    mock_graph_api.post_object.side_effect = [
        {'video_id': 'vid123', 'upload_url': 'https://upload.example.com'},  # start response
        None  # finish response
    ]
    mock_graph_api_class.return_value = mock_graph_api

    # Mock requests.post for upload
    mock_upload_response = MagicMock()
    mock_upload_response.raise_for_status.return_value = None
    mock_requests_post.return_value = mock_upload_response

    client = FacebookAPIClient('access_token')
    client.graph_api = mock_graph_api
    client._authenticated = True

    result = await client.upload_reel_or_story('page_id', 'reel', 'Test caption', 'http://video.mp4')

    assert result == 'vid123'
    # Verify start request
    start_call = mock_graph_api.post_object.call_args_list[0]
    assert start_call[1]['object_id'] == 'page_id'
    assert start_call[1]['connection'] == 'video_reels'
    assert start_call[1]['data']['upload_phase'] == 'start'

    # Verify upload request
    mock_requests_post.assert_called_once()
    upload_call = mock_requests_post.call_args
    assert upload_call[0][0] == 'https://upload.example.com'

    # Verify finish request
    finish_call = mock_graph_api.post_object.call_args_list[1]
    assert finish_call[1]['data']['upload_phase'] == 'finish'
    assert finish_call[1]['data']['video_id'] == 'vid123'
    assert finish_call[1]['data']['description'] == 'Test caption'