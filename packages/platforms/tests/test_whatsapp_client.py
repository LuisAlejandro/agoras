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

from agoras.platforms.whatsapp.client import WhatsAppAPIClient

# Initialization Tests


def test_whatsapp_client_init():
    """Test WhatsAppAPIClient initialization."""
    client = WhatsAppAPIClient('access_token', 'phone_number_id')

    assert client.access_token == 'access_token'
    assert client.phone_number_id == 'phone_number_id'
    assert client.graph_api is None
    assert client.api_version == "v23.0"
    assert client._authenticated is False


# Authentication Tests

@pytest.mark.asyncio
@patch('agoras.platforms.whatsapp.client.GraphAPI')
async def test_whatsapp_client_authenticate(mock_graph_api_class):
    """Test WhatsAppAPIClient authenticate method."""
    mock_graph_api = MagicMock()
    mock_graph_api_class.return_value = mock_graph_api

    client = WhatsAppAPIClient('access_token', 'phone_number_id')
    result = await client.authenticate()

    assert result is True
    assert client._authenticated is True
    assert client.graph_api is mock_graph_api
    mock_graph_api_class.assert_called_once_with(access_token='access_token', version="v23.0")


@pytest.mark.asyncio
async def test_whatsapp_client_authenticate_already_authenticated():
    """Test WhatsAppAPIClient authenticate when already authenticated."""
    client = WhatsAppAPIClient('access_token', 'phone_number_id')
    client._authenticated = True

    result = await client.authenticate()

    assert result is True


@pytest.mark.asyncio
async def test_whatsapp_client_authenticate_missing_token():
    """Test WhatsAppAPIClient authenticate raises error without token."""
    client = WhatsAppAPIClient('', 'phone_number_id')

    with pytest.raises(Exception, match='access token is required'):
        await client.authenticate()


@pytest.mark.asyncio
@patch('agoras.platforms.whatsapp.client.GraphAPI')
async def test_whatsapp_client_authenticate_failure(mock_graph_api_class):
    """Test WhatsAppAPIClient authenticate handles GraphAPI errors."""
    mock_graph_api_class.side_effect = Exception('GraphAPI error')

    client = WhatsAppAPIClient('access_token', 'phone_number_id')

    with pytest.raises(Exception, match='authentication failed'):
        await client.authenticate()


# Disconnect Tests

def test_whatsapp_client_disconnect():
    """Test WhatsAppAPIClient disconnect method."""
    client = WhatsAppAPIClient('access_token', 'phone_number_id')
    client.graph_api = MagicMock()
    client._authenticated = True

    client.disconnect()

    assert client.graph_api is None
    assert client._authenticated is False


# Get Object Tests

def test_whatsapp_client_get_object():
    """Test WhatsAppAPIClient get_object method."""
    client = WhatsAppAPIClient('access_token', 'phone_number_id')
    mock_graph_api = MagicMock()
    mock_graph_api.get_object.return_value = {'id': 'obj123', 'name': 'Test'}
    client.graph_api = mock_graph_api
    client._authenticated = True

    result = client.get_object('obj123')

    assert result == {'id': 'obj123', 'name': 'Test'}
    mock_graph_api.get_object.assert_called_once_with(object_id='obj123')


def test_whatsapp_client_get_object_with_fields():
    """Test WhatsAppAPIClient get_object with fields parameter."""
    client = WhatsAppAPIClient('access_token', 'phone_number_id')
    mock_graph_api = MagicMock()
    mock_graph_api.get_object.return_value = {'id': 'obj123'}
    client.graph_api = mock_graph_api
    client._authenticated = True

    result = client.get_object('obj123', fields='id,name')

    assert result == {'id': 'obj123'}
    mock_graph_api.get_object.assert_called_once_with(object_id='obj123', fields='id,name')


def test_whatsapp_client_get_object_not_initialized():
    """Test WhatsAppAPIClient get_object raises error when not initialized."""
    client = WhatsAppAPIClient('access_token', 'phone_number_id')

    with pytest.raises(Exception, match='GraphAPI not initialized'):
        client.get_object('obj123')


def test_whatsapp_client_get_object_error_handling():
    """Test WhatsAppAPIClient get_object handles GraphAPI errors."""
    client = WhatsAppAPIClient('access_token', 'phone_number_id')
    mock_graph_api = MagicMock()
    mock_graph_api.get_object.side_effect = Exception('API error')
    client.graph_api = mock_graph_api
    client._authenticated = True

    with pytest.raises(Exception, match='get_object failed'):
        client.get_object('obj123')


# Post Object Tests

@patch('requests.post')
def test_whatsapp_client_post_object(mock_requests_post):
    """Test WhatsAppAPIClient post_object method."""
    mock_response = MagicMock()
    mock_response.json.return_value = {'id': 'post123'}
    mock_response.raise_for_status.return_value = None
    mock_requests_post.return_value = mock_response

    client = WhatsAppAPIClient('access_token', 'phone_number_id')
    client._authenticated = True  # Set authenticated to avoid graph_api check

    result = client.post_object('obj123', 'messages', {'data': 'test'})

    assert result == {'id': 'post123'}
    mock_requests_post.assert_called_once()
    call_args = mock_requests_post.call_args
    assert 'https://graph.facebook.com/v23.0/obj123/messages' in call_args[0][0]
    assert call_args[1]['json'] == {'data': 'test'}


@patch('requests.post')
def test_whatsapp_client_post_object_with_empty_data(mock_requests_post):
    """Test WhatsAppAPIClient post_object with None data (uses empty dict)."""
    mock_response = MagicMock()
    mock_response.json.return_value = {'id': 'post123'}
    mock_response.raise_for_status.return_value = None
    mock_requests_post.return_value = mock_response

    client = WhatsAppAPIClient('access_token', 'phone_number_id')
    client._authenticated = True

    result = client.post_object('obj123', 'messages', None)

    assert result == {'id': 'post123'}
    mock_requests_post.assert_called_once()
    call_args = mock_requests_post.call_args
    assert 'https://graph.facebook.com/v23.0/obj123/messages' in call_args[0][0]
    assert call_args[1]['json'] == {}


@patch('requests.post')
def test_whatsapp_client_post_object_not_initialized(mock_requests_post):
    """Test WhatsAppAPIClient post_object raises error when not initialized."""
    mock_requests_post.side_effect = RuntimeError(
        "Real HTTP call blocked! Use @pytest.mark.integration for tests that need real network access, or mock the HTTP call in your test.")

    client = WhatsAppAPIClient('access_token', 'phone_number_id')

    with pytest.raises(RuntimeError, match='Real HTTP call blocked'):
        client.post_object('obj123', 'messages', {})


@patch('requests.post')
def test_whatsapp_client_post_object_error_handling(mock_requests_post):
    """Test WhatsAppAPIClient post_object handles HTTP errors."""
    import requests
    mock_requests_post.side_effect = requests.exceptions.RequestException('API error')

    client = WhatsAppAPIClient('access_token', 'phone_number_id')
    client._authenticated = True

    with pytest.raises(Exception, match='WhatsApp post_object failed: API error'):
        client.post_object('obj123', 'messages', {})


# Send Message Tests

@patch('requests.post')
def test_whatsapp_client_send_message(mock_requests_post):
    """Test WhatsAppAPIClient send_message method."""
    mock_response = MagicMock()
    mock_response.json.return_value = {'messages': [{'id': 'msg-123'}]}
    mock_response.raise_for_status.return_value = None
    mock_requests_post.return_value = mock_response

    client = WhatsAppAPIClient('access_token', 'phone_number_id')
    client.graph_api = MagicMock()  # Mock graph_api to avoid initialization check
    client._authenticated = True

    result = client.send_message('+1234567890', 'Test message')

    assert result == {'message_id': 'msg-123', 'status': 'sent'}
    mock_requests_post.assert_called_once()
    call_args = mock_requests_post.call_args
    assert 'https://graph.facebook.com/v23.0/phone_number_id/messages' in call_args[0][0]
    call_data = call_args[1]['json']
    assert call_data['messaging_product'] == 'whatsapp'
    assert call_data['to'] == '+1234567890'
    assert call_data['type'] == 'text'
    assert call_data['text']['body'] == 'Test message'


@patch('requests.post')
def test_whatsapp_client_send_message_with_buttons(mock_requests_post):
    """Test WhatsAppAPIClient send_message with buttons."""
    mock_response = MagicMock()
    mock_response.json.return_value = {'messages': [{'id': 'msg-123'}]}
    mock_response.raise_for_status.return_value = None
    mock_requests_post.return_value = mock_response

    client = WhatsAppAPIClient('access_token', 'phone_number_id')
    client.graph_api = MagicMock()  # Mock graph_api to avoid initialization check
    client._authenticated = True

    buttons = [{'type': 'reply', 'reply': {'id': '1', 'title': 'Yes'}}]
    result = client.send_message('+1234567890', 'Test message', buttons=buttons)

    assert result == {'message_id': 'msg-123', 'status': 'sent'}
    mock_requests_post.assert_called_once()
    call_args = mock_requests_post.call_args
    call_data = call_args[1]['json']
    assert call_data['type'] == 'interactive'
    assert 'interactive' in call_data
    assert call_data['interactive']['action']['buttons'] == buttons


def test_whatsapp_client_send_message_not_initialized():
    """Test WhatsAppAPIClient send_message raises error when not initialized."""
    client = WhatsAppAPIClient('access_token', 'phone_number_id')

    with pytest.raises(Exception, match='GraphAPI not initialized'):
        client.send_message('+1234567890', 'Test')


@patch('requests.post')
def test_whatsapp_client_send_message_api_error(mock_requests_post):
    """Test WhatsAppAPIClient send_message handles API errors."""
    mock_response = MagicMock()
    mock_response.json.return_value = {}  # No messages in response
    mock_response.raise_for_status.return_value = None
    mock_requests_post.return_value = mock_response

    client = WhatsAppAPIClient('access_token', 'phone_number_id')
    client.graph_api = MagicMock()  # Mock graph_api to avoid initialization check
    client._authenticated = True

    with pytest.raises(Exception, match='WhatsApp API error'):
        client.send_message('+1234567890', 'Test')


@patch('requests.post')
def test_whatsapp_client_send_message_post_error(mock_requests_post):
    """Test WhatsAppAPIClient send_message handles post_object errors."""
    mock_requests_post.side_effect = Exception('Post failed')

    client = WhatsAppAPIClient('access_token', 'phone_number_id')
    client.graph_api = MagicMock()  # Mock graph_api to avoid initialization check
    client._authenticated = True

    with pytest.raises(Exception, match='send_message failed'):
        client.send_message('+1234567890', 'Test')


# Send Image Tests

@patch('requests.post')
def test_whatsapp_client_send_image(mock_requests_post):
    """Test WhatsAppAPIClient send_image method."""
    mock_response = MagicMock()
    mock_response.json.return_value = {'messages': [{'id': 'msg-124'}]}
    mock_response.raise_for_status.return_value = None
    mock_requests_post.return_value = mock_response

    client = WhatsAppAPIClient('access_token', 'phone_number_id')
    client.graph_api = MagicMock()  # Mock graph_api to avoid initialization check
    client._authenticated = True

    result = client.send_image('+1234567890', 'http://image.jpg', caption='Image caption')

    assert result == {'message_id': 'msg-124', 'status': 'sent'}
    mock_requests_post.assert_called_once()
    call_args = mock_requests_post.call_args
    call_data = call_args[1]['json']
    assert call_data['type'] == 'image'
    assert call_data['image']['link'] == 'http://image.jpg'
    assert call_data['image']['caption'] == 'Image caption'


@patch('requests.post')
def test_whatsapp_client_send_image_without_caption(mock_requests_post):
    """Test WhatsAppAPIClient send_image without caption."""
    mock_response = MagicMock()
    mock_response.json.return_value = {'messages': [{'id': 'msg-124'}]}
    mock_response.raise_for_status.return_value = None
    mock_requests_post.return_value = mock_response

    client = WhatsAppAPIClient('access_token', 'phone_number_id')
    client.graph_api = MagicMock()  # Mock graph_api to avoid initialization check
    client._authenticated = True

    result = client.send_image('+1234567890', 'http://image.jpg')

    assert result == {'message_id': 'msg-124', 'status': 'sent'}
    mock_requests_post.assert_called_once()
    call_args = mock_requests_post.call_args
    call_data = call_args[1]['json']
    assert 'caption' not in call_data['image']


# Send Video Tests

@patch('requests.post')
def test_whatsapp_client_send_video(mock_requests_post):
    """Test WhatsAppAPIClient send_video method."""
    mock_response = MagicMock()
    mock_response.json.return_value = {'messages': [{'id': 'msg-125'}]}
    mock_response.raise_for_status.return_value = None
    mock_requests_post.return_value = mock_response

    client = WhatsAppAPIClient('access_token', 'phone_number_id')
    client.graph_api = MagicMock()  # Mock graph_api to avoid initialization check
    client._authenticated = True

    result = client.send_video('+1234567890', 'http://video.mp4', caption='Video caption')

    assert result == {'message_id': 'msg-125', 'status': 'sent'}
    mock_requests_post.assert_called_once()
    call_args = mock_requests_post.call_args
    call_data = call_args[1]['json']
    assert call_data['type'] == 'video'
    assert call_data['video']['link'] == 'http://video.mp4'
    assert call_data['video']['caption'] == 'Video caption'


# Send Template Tests

@patch('requests.post')
def test_whatsapp_client_send_template(mock_requests_post):
    """Test WhatsAppAPIClient send_template method."""
    mock_response = MagicMock()
    mock_response.json.return_value = {'messages': [{'id': 'msg-130'}]}
    mock_response.raise_for_status.return_value = None
    mock_requests_post.return_value = mock_response

    client = WhatsAppAPIClient('access_token', 'phone_number_id')
    client.graph_api = MagicMock()  # Mock graph_api to avoid initialization check
    client._authenticated = True

    result = client.send_template('+1234567890', 'welcome_template', language_code='en')

    assert result == {'message_id': 'msg-130', 'status': 'sent'}
    mock_requests_post.assert_called_once()
    call_args = mock_requests_post.call_args
    call_data = call_args[1]['json']
    assert call_data['type'] == 'template'
    assert call_data['template']['name'] == 'welcome_template'
    assert call_data['template']['language']['code'] == 'en'


@patch('requests.post')
def test_whatsapp_client_send_template_with_components(mock_requests_post):
    """Test WhatsAppAPIClient send_template with components."""
    mock_response = MagicMock()
    mock_response.json.return_value = {'messages': [{'id': 'msg-130'}]}
    mock_response.raise_for_status.return_value = None
    mock_requests_post.return_value = mock_response

    client = WhatsAppAPIClient('access_token', 'phone_number_id')
    client.graph_api = MagicMock()  # Mock graph_api to avoid initialization check
    client._authenticated = True

    components = [{'type': 'body', 'parameters': [{'type': 'text', 'text': 'John'}]}]
    result = client.send_template('+1234567890', 'welcome_template', language_code='es', components=components)

    assert result == {'message_id': 'msg-130', 'status': 'sent'}
    mock_requests_post.assert_called_once()
    call_args = mock_requests_post.call_args
    call_data = call_args[1]['json']
    assert call_data['template']['components'] == components
    assert call_data['template']['language']['code'] == 'es'


# Error Handling for All Send Methods

def test_whatsapp_client_send_image_not_initialized():
    """Test WhatsAppAPIClient send_image raises error when not initialized."""
    client = WhatsAppAPIClient('access_token', 'phone_number_id')

    with pytest.raises(Exception, match='GraphAPI not initialized'):
        client.send_image('+1234567890', 'http://image.jpg')


def test_whatsapp_client_send_video_not_initialized():
    """Test WhatsAppAPIClient send_video raises error when not initialized."""
    client = WhatsAppAPIClient('access_token', 'phone_number_id')

    with pytest.raises(Exception, match='GraphAPI not initialized'):
        client.send_video('+1234567890', 'http://video.mp4')


def test_whatsapp_client_send_template_not_initialized():
    """Test WhatsAppAPIClient send_template raises error when not initialized."""
    client = WhatsAppAPIClient('access_token', 'phone_number_id')

    with pytest.raises(Exception, match='GraphAPI not initialized'):
        client.send_template('+1234567890', 'template')


@patch('requests.post')
def test_whatsapp_client_send_image_api_error(mock_requests_post):
    """Test WhatsAppAPIClient send_image handles API errors."""
    mock_response = MagicMock()
    mock_response.json.return_value = {}  # No messages
    mock_response.raise_for_status.return_value = None
    mock_requests_post.return_value = mock_response

    client = WhatsAppAPIClient('access_token', 'phone_number_id')
    client.graph_api = MagicMock()  # Mock graph_api to avoid initialization check
    client._authenticated = True

    with pytest.raises(Exception, match='WhatsApp API error'):
        client.send_image('+1234567890', 'http://image.jpg')
