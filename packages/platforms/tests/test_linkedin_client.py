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

from agoras.platforms.linkedin.client import LinkedInAPIClient

# Initialization Tests


def test_linkedin_client_init():
    """Test LinkedInAPIClient initialization."""
    client = LinkedInAPIClient('access_token')

    assert client.access_token == 'access_token'
    assert client.restli_client is None
    assert client.api_version == "202302"
    assert client._authenticated is False


# Authentication Tests

@pytest.mark.asyncio
@patch('agoras.platforms.linkedin.client.RestliClient')
async def test_linkedin_client_authenticate(mock_restli_class):
    """Test LinkedInAPIClient authenticate method."""
    mock_restli = MagicMock()
    mock_restli_class.return_value = mock_restli

    client = LinkedInAPIClient('access_token')
    result = await client.authenticate()

    assert result is True
    assert client._authenticated is True
    assert client.restli_client is mock_restli
    mock_restli_class.assert_called_once()


@pytest.mark.asyncio
async def test_linkedin_client_authenticate_already_authenticated():
    """Test LinkedInAPIClient authenticate when already authenticated."""
    client = LinkedInAPIClient('access_token')
    client._authenticated = True

    result = await client.authenticate()

    assert result is True


@pytest.mark.asyncio
async def test_linkedin_client_authenticate_missing_token():
    """Test LinkedInAPIClient authenticate raises error without token."""
    client = LinkedInAPIClient('')

    with pytest.raises(Exception, match='access token is required'):
        await client.authenticate()


@pytest.mark.asyncio
@patch('agoras.platforms.linkedin.client.RestliClient')
async def test_linkedin_client_authenticate_failure(mock_restli_class):
    """Test LinkedInAPIClient authenticate handles RestliClient errors."""
    mock_restli_class.side_effect = Exception('RestliClient error')

    client = LinkedInAPIClient('access_token')

    with pytest.raises(Exception, match='authentication failed'):
        await client.authenticate()


# Disconnect Tests

def test_linkedin_client_disconnect():
    """Test LinkedInAPIClient disconnect method."""
    client = LinkedInAPIClient('access_token')
    mock_restli = MagicMock()
    client.restli_client = mock_restli
    client._authenticated = True

    client.disconnect()

    assert client.restli_client is None
    assert client._authenticated is False


# Upload Image Tests

@pytest.mark.asyncio
@patch('agoras.platforms.linkedin.client.requests.put')
@patch('agoras.platforms.linkedin.client.asyncio.to_thread')
async def test_linkedin_client_upload_image(mock_to_thread, mock_requests_put):
    """Test LinkedInAPIClient upload_image method."""
    client = LinkedInAPIClient('access_token')
    mock_restli = MagicMock()
    mock_request = MagicMock()
    mock_response = MagicMock()
    mock_response.json.return_value = {
        'value': {
            'uploadUrl': 'http://upload.url',
            'image': 'urn:li:image:123'
        }
    }
    mock_request.response = mock_response
    mock_restli.action.return_value = mock_request
    client.restli_client = mock_restli
    client._authenticated = True

    mock_upload_response = MagicMock()
    mock_upload_response.status_code = 201
    mock_requests_put.return_value = mock_upload_response

    # Mock asyncio.to_thread to execute the sync function
    def execute_sync(func):
        return func()
    mock_to_thread.side_effect = execute_sync

    result = await client.upload_image(b'image_content', 'urn:li:person:123')

    assert result == 'urn:li:image:123'
    mock_restli.action.assert_called_once()
    mock_requests_put.assert_called_once()


@pytest.mark.asyncio
@patch('agoras.platforms.linkedin.client.asyncio.to_thread')
async def test_linkedin_client_upload_image_not_initialized(mock_to_thread):
    """Test LinkedInAPIClient upload_image raises error when not initialized."""
    client = LinkedInAPIClient('access_token')

    def execute_sync(func):
        return func()
    mock_to_thread.side_effect = execute_sync

    with pytest.raises(Exception, match='RestliClient not initialized'):
        await client.upload_image(b'content', 'urn:li:person:123')


@pytest.mark.asyncio
@patch('agoras.platforms.linkedin.client.requests.put')
@patch('agoras.platforms.linkedin.client.asyncio.to_thread')
async def test_linkedin_client_upload_image_upload_failure(mock_to_thread, mock_requests_put):
    """Test LinkedInAPIClient upload_image handles upload failure."""
    client = LinkedInAPIClient('access_token')
    mock_restli = MagicMock()
    mock_request = MagicMock()
    mock_response = MagicMock()
    mock_response.json.return_value = {
        'value': {
            'uploadUrl': 'http://upload.url',
            'image': 'urn:li:image:123'
        }
    }
    mock_request.response = mock_response
    mock_restli.action.return_value = mock_request
    client.restli_client = mock_restli
    client._authenticated = True

    mock_upload_response = MagicMock()
    mock_upload_response.status_code = 400  # Upload failed
    mock_requests_put.return_value = mock_upload_response

    def execute_sync(func):
        return func()
    mock_to_thread.side_effect = execute_sync

    with pytest.raises(Exception, match='Failed to upload image'):
        await client.upload_image(b'content', 'urn:li:person:123')


# Create Post Tests

@pytest.mark.asyncio
@patch('agoras.platforms.linkedin.client.asyncio.to_thread')
async def test_linkedin_client_create_post_text_only(mock_to_thread):
    """Test LinkedInAPIClient create_post with text only."""
    client = LinkedInAPIClient('access_token')
    mock_restli = MagicMock()
    mock_request = MagicMock()
    mock_request.entity_id = 'post-123'
    mock_restli.create.return_value = mock_request
    client.restli_client = mock_restli
    client._authenticated = True

    def execute_sync(func):
        return func()
    mock_to_thread.side_effect = execute_sync

    result = await client.create_post('urn:li:person:123', 'Test post')

    assert result == 'post-123'
    mock_restli.create.assert_called_once()
    call_entity = mock_restli.create.call_args[1]['entity']
    assert call_entity['author'] == 'urn:li:person:123'
    assert call_entity['commentary'] == 'Test post'


@pytest.mark.asyncio
@patch('agoras.platforms.linkedin.client.asyncio.to_thread')
async def test_linkedin_client_create_post_with_link(mock_to_thread):
    """Test LinkedInAPIClient create_post with link."""
    client = LinkedInAPIClient('access_token')
    mock_restli = MagicMock()
    mock_request = MagicMock()
    mock_request.entity_id = 'post-123'
    mock_restli.create.return_value = mock_request
    client.restli_client = mock_restli
    client._authenticated = True

    def execute_sync(func):
        return func()
    mock_to_thread.side_effect = execute_sync

    result = await client.create_post(
        'urn:li:person:123',
        'Test post',
        link='http://link.com',
        link_title='Link Title',
        link_description='Link Description'
    )

    assert result == 'post-123'
    call_entity = mock_restli.create.call_args[1]['entity']
    assert 'content' in call_entity
    assert call_entity['content']['article']['source'] == 'http://link.com'
    assert call_entity['content']['article']['title'] == 'Link Title'
    assert call_entity['content']['article']['description'] == 'Link Description'


@pytest.mark.asyncio
@patch('agoras.platforms.linkedin.client.asyncio.to_thread')
async def test_linkedin_client_create_post_with_single_image(mock_to_thread):
    """Test LinkedInAPIClient create_post with single image."""
    client = LinkedInAPIClient('access_token')
    mock_restli = MagicMock()
    mock_request = MagicMock()
    mock_request.entity_id = 'post-123'
    mock_restli.create.return_value = mock_request
    client.restli_client = mock_restli
    client._authenticated = True

    def execute_sync(func):
        return func()
    mock_to_thread.side_effect = execute_sync

    result = await client.create_post('urn:li:person:123', 'Test post', image_ids=['image-123'])

    assert result == 'post-123'
    call_entity = mock_restli.create.call_args[1]['entity']
    assert call_entity['content']['media']['id'] == 'image-123'


@pytest.mark.asyncio
@patch('agoras.platforms.linkedin.client.asyncio.to_thread')
async def test_linkedin_client_create_post_with_multiple_images(mock_to_thread):
    """Test LinkedInAPIClient create_post with multiple images."""
    client = LinkedInAPIClient('access_token')
    mock_restli = MagicMock()
    mock_request = MagicMock()
    mock_request.entity_id = 'post-123'
    mock_restli.create.return_value = mock_request
    client.restli_client = mock_restli
    client._authenticated = True

    def execute_sync(func):
        return func()
    mock_to_thread.side_effect = execute_sync

    result = await client.create_post('urn:li:person:123', 'Test post', image_ids=['img1', 'img2', 'img3'])

    assert result == 'post-123'
    call_entity = mock_restli.create.call_args[1]['entity']
    assert 'multiImage' in call_entity['content']
    assert len(call_entity['content']['multiImage']['images']) == 3


@pytest.mark.asyncio
@patch('agoras.platforms.linkedin.client.asyncio.to_thread')
async def test_linkedin_client_create_post_not_initialized(mock_to_thread):
    """Test LinkedInAPIClient create_post raises error when not initialized."""
    client = LinkedInAPIClient('access_token')

    def execute_sync(func):
        return func()
    mock_to_thread.side_effect = execute_sync

    with pytest.raises(Exception, match='RestliClient not initialized'):
        await client.create_post('urn:li:person:123', 'Test')


@pytest.mark.asyncio
@patch('agoras.platforms.linkedin.client.asyncio.to_thread')
async def test_linkedin_client_create_post_invalid_response(mock_to_thread):
    """Test LinkedInAPIClient create_post handles invalid response."""
    client = LinkedInAPIClient('access_token')
    mock_restli = MagicMock()
    mock_request = MagicMock()
    mock_request.entity_id = None  # Invalid response
    mock_restli.create.return_value = mock_request
    client.restli_client = mock_restli
    client._authenticated = True

    def execute_sync(func):
        return func()
    mock_to_thread.side_effect = execute_sync

    with pytest.raises(Exception, match='Invalid response from LinkedIn API'):
        await client.create_post('urn:li:person:123', 'Test')


# Like Post Tests

@pytest.mark.asyncio
@patch('agoras.platforms.linkedin.client.asyncio.to_thread')
async def test_linkedin_client_like_post(mock_to_thread):
    """Test LinkedInAPIClient like_post method."""
    client = LinkedInAPIClient('access_token')
    mock_restli = MagicMock()
    mock_request = MagicMock()
    mock_request.status_code = 201
    mock_restli.create.return_value = mock_request
    client.restli_client = mock_restli
    client._authenticated = True

    def execute_sync(func):
        return func()
    mock_to_thread.side_effect = execute_sync

    result = await client.like_post('post-123', 'urn:li:person:123')

    assert result == 'post-123'
    mock_restli.create.assert_called_once()
    call_entity = mock_restli.create.call_args[1]['entity']
    assert call_entity['actor'] == 'urn:li:person:123'
    assert call_entity['object'] == 'post-123'


@pytest.mark.asyncio
@patch('agoras.platforms.linkedin.client.asyncio.to_thread')
async def test_linkedin_client_like_post_failure(mock_to_thread):
    """Test LinkedInAPIClient like_post handles failure."""
    client = LinkedInAPIClient('access_token')
    mock_restli = MagicMock()
    mock_request = MagicMock()
    mock_request.status_code = 400  # Failure
    mock_restli.create.return_value = mock_request
    client.restli_client = mock_restli
    client._authenticated = True

    def execute_sync(func):
        return func()
    mock_to_thread.side_effect = execute_sync

    with pytest.raises(Exception, match='Unable to like post'):
        await client.like_post('post-123', 'urn:li:person:123')


# Share Post Tests

@pytest.mark.asyncio
@patch('agoras.platforms.linkedin.client.asyncio.to_thread')
async def test_linkedin_client_share_post(mock_to_thread):
    """Test LinkedInAPIClient share_post method."""
    client = LinkedInAPIClient('access_token')
    mock_restli = MagicMock()
    mock_request = MagicMock()
    mock_request.status_code = 201
    mock_request.entity_id = 'share-123'
    mock_restli.create.return_value = mock_request
    client.restli_client = mock_restli
    client._authenticated = True

    def execute_sync(func):
        return func()
    mock_to_thread.side_effect = execute_sync

    result = await client.share_post('post-123', 'urn:li:person:123', commentary='Shared!')

    assert result == 'share-123'
    call_entity = mock_restli.create.call_args[1]['entity']
    assert call_entity['author'] == 'urn:li:person:123'
    assert call_entity['commentary'] == 'Shared!'
    assert call_entity['reshareContext']['parent'] == 'post-123'


@pytest.mark.asyncio
@patch('agoras.platforms.linkedin.client.asyncio.to_thread')
async def test_linkedin_client_share_post_failure(mock_to_thread):
    """Test LinkedInAPIClient share_post handles failure."""
    client = LinkedInAPIClient('access_token')
    mock_restli = MagicMock()
    mock_request = MagicMock()
    mock_request.status_code = 400
    mock_restli.create.return_value = mock_request
    client.restli_client = mock_restli
    client._authenticated = True

    def execute_sync(func):
        return func()
    mock_to_thread.side_effect = execute_sync

    with pytest.raises(Exception, match='Unable to share post'):
        await client.share_post('post-123', 'urn:li:person:123')


# Delete Post Tests

@pytest.mark.asyncio
@patch('agoras.platforms.linkedin.client.asyncio.to_thread')
async def test_linkedin_client_delete_post(mock_to_thread):
    """Test LinkedInAPIClient delete_post method."""
    client = LinkedInAPIClient('access_token')
    mock_restli = MagicMock()
    mock_request = MagicMock()
    mock_request.status_code = 204
    mock_restli.delete.return_value = mock_request
    client.restli_client = mock_restli
    client._authenticated = True

    def execute_sync(func):
        return func()
    mock_to_thread.side_effect = execute_sync

    result = await client.delete_post('post-123')

    assert result == 'post-123'
    mock_restli.delete.assert_called_once()
    call_path_keys = mock_restli.delete.call_args[1]['path_keys']
    assert call_path_keys['id'] == 'post-123'


@pytest.mark.asyncio
@patch('agoras.platforms.linkedin.client.asyncio.to_thread')
async def test_linkedin_client_delete_post_failure(mock_to_thread):
    """Test LinkedInAPIClient delete_post handles failure."""
    client = LinkedInAPIClient('access_token')
    mock_restli = MagicMock()
    mock_request = MagicMock()
    mock_request.status_code = 404
    mock_restli.delete.return_value = mock_request
    client.restli_client = mock_restli
    client._authenticated = True

    def execute_sync(func):
        return func()
    mock_to_thread.side_effect = execute_sync

    with pytest.raises(Exception, match='Unable to delete post'):
        await client.delete_post('post-123')


# Get User Info Tests

@pytest.mark.asyncio
@patch('agoras.platforms.linkedin.client.asyncio.to_thread')
async def test_linkedin_client_get_user_info(mock_to_thread):
    """Test LinkedInAPIClient get_user_info method."""
    client = LinkedInAPIClient('access_token')
    mock_restli = MagicMock()
    mock_request = MagicMock()
    mock_response = MagicMock()
    mock_response.json.return_value = {'sub': 'user123', 'name': 'Test User'}
    mock_request.response = mock_response
    mock_restli.get.return_value = mock_request
    client.restli_client = mock_restli
    client._authenticated = True

    def execute_sync(func):
        return func()
    mock_to_thread.side_effect = execute_sync

    result = await client.get_user_info()

    assert result == {'sub': 'user123', 'name': 'Test User'}
    mock_restli.get.assert_called_once_with(resource_path='/userinfo', access_token='access_token')


@pytest.mark.asyncio
@patch('agoras.platforms.linkedin.client.asyncio.to_thread')
async def test_linkedin_client_get_user_info_expired_token(mock_to_thread):
    """Test LinkedInAPIClient get_user_info handles expired token."""
    client = LinkedInAPIClient('access_token')
    mock_restli = MagicMock()
    mock_request = MagicMock()
    mock_response = MagicMock()
    mock_response.json.return_value = {'code': 'EXPIRED_ACCESS_TOKEN'}
    mock_request.response = mock_response
    mock_restli.get.return_value = mock_request
    client.restli_client = mock_restli
    client._authenticated = True

    def execute_sync(func):
        return func()
    mock_to_thread.side_effect = execute_sync

    with pytest.raises(Exception, match='access token has expired'):
        await client.get_user_info()
