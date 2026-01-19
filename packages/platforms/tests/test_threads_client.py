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

from agoras.platforms.threads.client import ThreadsAPIClient

# Initialization Tests


def test_threads_client_init():
    """Test ThreadsAPIClient initialization."""
    client = ThreadsAPIClient('access_token', 'user_id')

    assert client.access_token == 'access_token'
    assert client.user_id == 'user_id'
    assert client.base_url == "https://graph.threads.net/v1.0"


# Get Profile Tests


def test_threads_client_get_profile_success():
    """Test ThreadsAPIClient get_profile success."""
    client = ThreadsAPIClient('access_token', 'user_id')

    result = client.get_profile()

    assert result == {'user_id': 'user_id', 'access_token_valid': True}


def test_threads_client_get_profile_no_token():
    """Test ThreadsAPIClient get_profile with no token."""
    client = ThreadsAPIClient('', 'user_id')

    with pytest.raises(Exception, match='No access token available'):
        client.get_profile()


def test_threads_client_get_profile_no_user_id():
    """Test ThreadsAPIClient get_profile with no user_id."""
    client = ThreadsAPIClient('access_token', '')

    with pytest.raises(Exception, match='No user ID available'):
        client.get_profile()


# Create Post Tests


@patch('agoras.platforms.threads.client.time.sleep')
@patch('agoras.platforms.threads.client.requests.post')
def test_threads_client_create_post_text_only(mock_requests_post, mock_sleep):
    """Test ThreadsAPIClient create_post with text-only."""
    # Mock the container creation response
    mock_container_response = MagicMock()
    mock_container_response.status_code = 200
    mock_container_response.json.return_value = {'id': 'c1'}
    mock_container_response.raise_for_status.return_value = None
    mock_container_response.text = '{"id": "c1"}'

    # Mock the publish response
    mock_publish_response = MagicMock()
    mock_publish_response.status_code = 200
    mock_publish_response.json.return_value = {'id': 'p1'}
    mock_publish_response.raise_for_status.return_value = None
    mock_publish_response.text = '{"id": "p1"}'

    # Return different responses for different calls
    mock_requests_post.side_effect = [mock_container_response, mock_publish_response]

    client = ThreadsAPIClient('access_token', 'user_id')
    result = client.create_post('Test post text')

    assert result == {'id': 'p1'}
    # Verify container creation call
    container_call = mock_requests_post.call_args_list[0]
    assert 'https://graph.threads.net/v1.0/me/threads' in container_call[0][0]
    container_data = container_call[1]['data']
    assert container_data['access_token'] == 'access_token'
    assert container_data['text'] == 'Test post text'
    assert container_data['media_type'] == 'TEXT'

    # Verify publish call
    publish_call = mock_requests_post.call_args_list[1]
    assert 'https://graph.threads.net/v1.0/user_id/threads_publish' in publish_call[0][0]
    publish_data = publish_call[1]['data']
    assert publish_data['access_token'] == 'access_token'
    assert publish_data['creation_id'] == 'c1'


def test_threads_client_create_post_no_token():
    """Test ThreadsAPIClient create_post with no token."""
    client = ThreadsAPIClient('', 'user_id')

    with pytest.raises(Exception, match='No access token available'):
        client.create_post('Test post')


def test_threads_client_create_post_no_user_id():
    """Test ThreadsAPIClient create_post with no user_id."""
    client = ThreadsAPIClient('access_token', '')

    with pytest.raises(Exception, match='No user ID available'):
        client.create_post('Test post')


@patch('agoras.platforms.threads.client.time.sleep')
@patch('agoras.platforms.threads.client.requests.post')
def test_threads_client_create_post_single_image(mock_requests_post, mock_sleep):
    """Test ThreadsAPIClient create_post with single image."""
    # Mock the container creation response
    mock_container_response = MagicMock()
    mock_container_response.status_code = 200
    mock_container_response.json.return_value = {'id': 'c1'}
    mock_container_response.raise_for_status.return_value = None
    mock_container_response.text = '{"id": "c1"}'

    # Mock the publish response
    mock_publish_response = MagicMock()
    mock_publish_response.status_code = 200
    mock_publish_response.json.return_value = {'id': 'p1'}
    mock_publish_response.raise_for_status.return_value = None
    mock_publish_response.text = '{"id": "p1"}'

    mock_requests_post.side_effect = [mock_container_response, mock_publish_response]

    client = ThreadsAPIClient('access_token', 'user_id')
    result = client.create_post('Test post', files=['http://image1.jpg'])

    assert result == {'id': 'p1'}
    # Verify container creation has image_url and media_type IMAGE
    container_call = mock_requests_post.call_args_list[0]
    container_data = container_call[1]['data']
    assert container_data['media_type'] == 'IMAGE'
    assert container_data['image_url'] == 'http://image1.jpg'


@patch('agoras.platforms.threads.client.time.sleep')
@patch('agoras.platforms.threads.client.requests.post')
def test_threads_client_create_post_carousel(mock_requests_post, mock_sleep):
    """Test ThreadsAPIClient create_post with carousel (multiple images)."""
    # Mock item container responses
    mock_item1_response = MagicMock()
    mock_item1_response.status_code = 200
    mock_item1_response.json.return_value = {'id': 'i1'}
    mock_item1_response.raise_for_status.return_value = None
    mock_item1_response.text = '{"id": "i1"}'

    mock_item2_response = MagicMock()
    mock_item2_response.status_code = 200
    mock_item2_response.json.return_value = {'id': 'i2'}
    mock_item2_response.raise_for_status.return_value = None
    mock_item2_response.text = '{"id": "i2"}'

    # Mock carousel container response
    mock_carousel_response = MagicMock()
    mock_carousel_response.status_code = 200
    mock_carousel_response.json.return_value = {'id': 'c1'}
    mock_carousel_response.raise_for_status.return_value = None
    mock_carousel_response.text = '{"id": "c1"}'

    # Mock publish response
    mock_publish_response = MagicMock()
    mock_publish_response.status_code = 200
    mock_publish_response.json.return_value = {'id': 'p1'}
    mock_publish_response.raise_for_status.return_value = None
    mock_publish_response.text = '{"id": "p1"}'

    mock_requests_post.side_effect = [
        mock_item1_response, mock_item2_response,  # Item containers
        mock_carousel_response,  # Carousel container
        mock_publish_response    # Publish
    ]

    client = ThreadsAPIClient('access_token', 'user_id')
    result = client.create_post('Test post', files=['http://image1.jpg', 'http://image2.jpg'])

    assert result == {'id': 'p1'}

    # Verify carousel container has children
    carousel_call = mock_requests_post.call_args_list[2]
    carousel_data = carousel_call[1]['data']
    assert carousel_data['media_type'] == 'CAROUSEL'
    assert carousel_data['children'] == 'i1,i2'


# Check Response Tests


def test_threads_client_check_response_200():
    """Test ThreadsAPIClient _check_response with 200 status."""
    client = ThreadsAPIClient('access_token', 'user_id')

    mock_response = MagicMock()
    mock_response.status_code = 200

    # Should not raise
    client._check_response(mock_response)


def test_threads_client_check_response_error_json():
    """Test ThreadsAPIClient _check_response with error JSON."""
    client = ThreadsAPIClient('access_token', 'user_id')

    mock_response = MagicMock()
    mock_response.status_code = 400
    mock_response.json.return_value = {'error': {'message': 'Bad Request Error'}}
    mock_response.text = 'Bad Request'

    with pytest.raises(Exception, match='API error: Bad Request Error'):
        client._check_response(mock_response)


def test_threads_client_check_response_error_no_json():
    """Test ThreadsAPIClient _check_response with error but no JSON."""
    client = ThreadsAPIClient('access_token', 'user_id')

    mock_response = MagicMock()
    mock_response.status_code = 500
    mock_response.json.side_effect = ValueError('No JSON')
    mock_response.text = 'Internal Server Error'

    with pytest.raises(Exception, match='HTTP 500: Internal Server Error'):
        client._check_response(mock_response)


# Repost Post Tests


@patch('agoras.platforms.threads.client.requests.post')
def test_threads_client_repost_post_success(mock_requests_post):
    """Test ThreadsAPIClient repost_post success."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {'id': 'r1'}
    mock_response.raise_for_status.return_value = None
    mock_response.text = '{"id": "r1"}'
    mock_requests_post.return_value = mock_response

    client = ThreadsAPIClient('access_token', 'user_id')
    result = client.repost_post('post123')

    assert result == {'id': 'r1'}
    mock_requests_post.assert_called_once()
    call_args = mock_requests_post.call_args
    assert 'https://graph.threads.net/v1.0/post123/repost' in call_args[0][0]
    assert call_args[1]['data']['access_token'] == 'access_token'


def test_threads_client_repost_post_no_token():
    """Test ThreadsAPIClient repost_post with no token."""
    client = ThreadsAPIClient('', 'user_id')

    with pytest.raises(Exception, match='No access token available'):
        client.repost_post('post123')


def test_threads_client_repost_post_no_user_id():
    """Test ThreadsAPIClient repost_post with no user_id."""
    client = ThreadsAPIClient('access_token', '')

    with pytest.raises(Exception, match='No user ID available'):
        client.repost_post('post123')