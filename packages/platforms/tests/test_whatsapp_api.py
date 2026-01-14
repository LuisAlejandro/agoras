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

from agoras.platforms.whatsapp.api import WhatsAppAPI


@pytest.fixture
def whatsapp_api():
    """Fixture to create WhatsAppAPI instance with mocked auth."""
    with patch('agoras.platforms.whatsapp.api.WhatsAppAuthManager') as mock_auth_class:
        mock_auth = MagicMock()
        mock_auth.authenticate = AsyncMock()
        mock_auth.access_token = 'token'
        mock_auth.ensure_authenticated = MagicMock()  # Don't raise
        mock_auth.client = MagicMock()
        mock_auth_class.return_value = mock_auth

        api = WhatsAppAPI('access_token', 'phone_number_id', 'business_account_id')
        api._authenticated = True
        api.client = MagicMock()
        api.client.send_message = MagicMock(return_value={'message_id': 'msg-123'})
        api.client.send_image = MagicMock(return_value={'message_id': 'msg-124'})
        api.client.send_video = MagicMock(return_value={'message_id': 'msg-125'})
        api.client.send_template = MagicMock(return_value={'message_id': 'msg-130'})
        api.client.get_object = MagicMock(return_value={
            'data': [{'id': 'profile-123', 'name': 'Business Name'}]
        })
        api.client.phone_number_id = 'phone_number_id'
        yield api


# Authentication Tests

@pytest.mark.asyncio
@patch('agoras.platforms.whatsapp.api.WhatsAppAuthManager')
async def test_whatsapp_api_authenticate(mock_auth_class):
    """Test WhatsAppAPI authenticate method."""
    mock_auth = MagicMock()
    mock_auth.authenticate = AsyncMock(return_value=True)
    mock_auth.access_token = 'token123'
    mock_auth.client = MagicMock()
    mock_auth_class.return_value = mock_auth

    api = WhatsAppAPI('access_token', 'phone_number_id')
    result = await api.authenticate()

    assert api._authenticated is True
    assert result is api
    mock_auth.authenticate.assert_called_once()


@pytest.mark.asyncio
async def test_whatsapp_api_disconnect(whatsapp_api):
    """Test WhatsAppAPI disconnect method."""
    whatsapp_api.client.disconnect = MagicMock()

    await whatsapp_api.disconnect()

    assert whatsapp_api._authenticated is False
    assert whatsapp_api.client is None


# Messaging Tests

@pytest.mark.asyncio
async def test_whatsapp_api_send_message(whatsapp_api):
    """Test WhatsAppAPI send_message."""
    result = await whatsapp_api.send_message('+1234567890', 'Test message')

    assert result == 'msg-123'
    whatsapp_api.client.send_message.assert_called_once_with('+1234567890', 'Test message', buttons=None)


@pytest.mark.asyncio
async def test_whatsapp_api_send_image(whatsapp_api):
    """Test WhatsAppAPI send_image."""
    result = await whatsapp_api.send_image('+1234567890', 'http://image.jpg', caption='Image caption')

    assert result == 'msg-124'
    whatsapp_api.client.send_image.assert_called_once_with('+1234567890', 'http://image.jpg', caption='Image caption')


@pytest.mark.asyncio
async def test_whatsapp_api_send_video(whatsapp_api):
    """Test WhatsAppAPI send_video."""
    result = await whatsapp_api.send_video('+1234567890', 'http://video.mp4', caption='Video caption')

    assert result == 'msg-125'
    whatsapp_api.client.send_video.assert_called_once_with('+1234567890', 'http://video.mp4', caption='Video caption')


@pytest.mark.asyncio
async def test_whatsapp_api_send_template(whatsapp_api):
    """Test WhatsAppAPI send_template."""
    result = await whatsapp_api.send_template('+1234567890', 'welcome_template', language_code='en')

    assert result == 'msg-130'
    whatsapp_api.client.send_template.assert_called_once_with(
        '+1234567890', 'welcome_template', language_code='en', components=None
    )


@pytest.mark.asyncio
@patch('agoras.platforms.whatsapp.api.MediaFactory')
async def test_whatsapp_api_post_wrapper_text(mock_media_factory, whatsapp_api):
    """Test WhatsAppAPI post wrapper with text."""
    result = await whatsapp_api.post(to='+1234567890', text='Test message')

    assert result == 'msg-123'
    whatsapp_api.client.send_message.assert_called_once()


@pytest.mark.asyncio
@patch('agoras.platforms.whatsapp.api.MediaFactory')
async def test_whatsapp_api_post_wrapper_image(mock_media_factory, whatsapp_api):
    """Test WhatsAppAPI post wrapper with image."""
    mock_image = MagicMock()
    mock_image.content = b'image_content'
    mock_image.file_type = MagicMock()
    mock_image.url = 'http://image.jpg'
    mock_image.cleanup = MagicMock()
    mock_media_factory.download_images = AsyncMock(return_value=[mock_image])

    result = await whatsapp_api.post(to='+1234567890', image_url='http://image.jpg', text='Caption')

    assert result == 'msg-124'
    mock_image.cleanup.assert_called()


@pytest.mark.asyncio
@patch('agoras.platforms.whatsapp.api.MediaFactory')
async def test_whatsapp_api_post_wrapper_video(mock_media_factory, whatsapp_api):
    """Test WhatsAppAPI post wrapper with video."""
    mock_video = MagicMock()
    mock_video.content = b'video_content'
    mock_video.file_type = MagicMock()
    mock_video.url = 'http://video.mp4'
    mock_video.cleanup = MagicMock()
    mock_media_factory.create_video = MagicMock(return_value=mock_video)
    mock_video.download = AsyncMock()

    result = await whatsapp_api.post(to='+1234567890', video_url='http://video.mp4', text='Caption')

    assert result == 'msg-125'
    mock_video.cleanup.assert_called()


# Profile Tests

@pytest.mark.asyncio
async def test_whatsapp_api_get_business_profile(whatsapp_api):
    """Test WhatsAppAPI get_business_profile."""
    result = await whatsapp_api.get_business_profile()

    assert result == {'id': 'profile-123', 'name': 'Business Name'}
    whatsapp_api.client.get_object.assert_called_once()


# Not Supported Tests

@pytest.mark.asyncio
async def test_whatsapp_api_like_raises_exception(whatsapp_api):
    """Test WhatsAppAPI like raises exception."""
    with pytest.raises(Exception, match='Like not supported'):
        await whatsapp_api.like('msg-123')


@pytest.mark.asyncio
async def test_whatsapp_api_delete_raises_exception(whatsapp_api):
    """Test WhatsAppAPI delete raises exception."""
    with pytest.raises(Exception, match='Delete not supported'):
        await whatsapp_api.delete('msg-123')


@pytest.mark.asyncio
async def test_whatsapp_api_share_raises_exception(whatsapp_api):
    """Test WhatsAppAPI share raises exception."""
    with pytest.raises(Exception, match='Share not supported'):
        await whatsapp_api.share('msg-123')


# Error Handling Tests

@pytest.mark.asyncio
async def test_whatsapp_api_send_error(whatsapp_api):
    """Test WhatsAppAPI handles send errors."""
    whatsapp_api.client.send_message = MagicMock(side_effect=Exception('Send failed'))

    with pytest.raises(Exception, match='Send failed'):
        await whatsapp_api.send_message('+1234567890', 'Test')


@pytest.mark.asyncio
async def test_whatsapp_api_not_authenticated(whatsapp_api):
    """Test WhatsAppAPI methods require authentication."""
    whatsapp_api._authenticated = False
    whatsapp_api.auth_manager.ensure_authenticated = MagicMock(side_effect=Exception('Not authenticated'))

    with pytest.raises(Exception, match='Not authenticated'):
        await whatsapp_api.send_message('+1234567890', 'Test')


@pytest.mark.asyncio
async def test_whatsapp_api_template_name_required(whatsapp_api):
    """Test WhatsAppAPI requires template name."""
    with pytest.raises(Exception, match='Template name is required'):
        await whatsapp_api.send_template('+1234567890', '')


# Additional Edge Cases and Error Handling

@pytest.mark.asyncio
async def test_whatsapp_api_send_template_with_components(whatsapp_api):
    """Test WhatsAppAPI send_template with components."""
    components = [{'type': 'body', 'parameters': [{'type': 'text', 'text': 'John'}]}]
    result = await whatsapp_api.send_template('+1234567890', 'welcome_template', language_code='es', components=components)

    assert result == 'msg-130'
    whatsapp_api.client.send_template.assert_called_once_with(
        '+1234567890', 'welcome_template', language_code='es', components=components
    )


@pytest.mark.asyncio
async def test_whatsapp_api_send_message_with_buttons(whatsapp_api):
    """Test WhatsAppAPI send_message with buttons."""
    buttons = [{'type': 'reply', 'reply': {'id': '1', 'title': 'Yes'}}]
    result = await whatsapp_api.send_message('+1234567890', 'Test message', buttons=buttons)

    assert result == 'msg-123'
    whatsapp_api.client.send_message.assert_called_once_with('+1234567890', 'Test message', buttons=buttons)


@pytest.mark.asyncio
@patch('agoras.platforms.whatsapp.api.MediaFactory')
async def test_whatsapp_api_post_no_content_error(mock_media_factory, whatsapp_api):
    """Test WhatsAppAPI post raises error when no text/image/video provided."""
    with pytest.raises(Exception, match='No text, image, or video provided'):
        await whatsapp_api.post(to='+1234567890')


@pytest.mark.asyncio
@patch('agoras.platforms.whatsapp.api.MediaFactory')
async def test_whatsapp_api_post_image_validation_failure(mock_media_factory, whatsapp_api):
    """Test WhatsAppAPI post handles image validation failure."""
    mock_image = MagicMock()
    mock_image.content = None  # Validation fails
    mock_image.file_type = None
    mock_image.url = 'http://image.jpg'
    mock_image.cleanup = MagicMock()
    mock_media_factory.download_images = AsyncMock(return_value=[mock_image])

    with pytest.raises(Exception, match='Failed to validate image'):
        await whatsapp_api.post(to='+1234567890', image_url='http://image.jpg')


@pytest.mark.asyncio
@patch('agoras.platforms.whatsapp.api.MediaFactory')
async def test_whatsapp_api_post_video_validation_failure(mock_media_factory, whatsapp_api):
    """Test WhatsAppAPI post handles video validation failure."""
    mock_video = MagicMock()
    mock_video.content = None  # Validation fails
    mock_video.file_type = None
    mock_video.url = 'http://video.mp4'
    mock_video.cleanup = MagicMock()
    mock_media_factory.create_video = MagicMock(return_value=mock_video)
    mock_video.download = AsyncMock()

    with pytest.raises(Exception, match='Failed to validate video'):
        await whatsapp_api.post(to='+1234567890', video_url='http://video.mp4')


@pytest.mark.asyncio
async def test_whatsapp_api_get_business_profile_error_handling(whatsapp_api):
    """Test WhatsAppAPI get_business_profile handles API errors."""
    whatsapp_api.client.get_object = MagicMock(return_value={})  # No data

    with pytest.raises(Exception, match='Failed to get business profile'):
        await whatsapp_api.get_business_profile()


@pytest.mark.asyncio
async def test_whatsapp_api_disconnect_handles_none_client(whatsapp_api):
    """Test WhatsAppAPI disconnect handles None client gracefully."""
    whatsapp_api.client = None
    whatsapp_api._authenticated = True

    await whatsapp_api.disconnect()

    assert whatsapp_api._authenticated is False
    assert whatsapp_api.client is None


@pytest.mark.asyncio
async def test_whatsapp_api_all_send_methods_use_rate_limiting(whatsapp_api):
    """Test all WhatsAppAPI send methods use rate limiting."""
    whatsapp_api._rate_limit_check = AsyncMock()

    await whatsapp_api.send_message('+1234567890', 'Test')
    await whatsapp_api.send_image('+1234567890', 'http://image.jpg')
    await whatsapp_api.send_video('+1234567890', 'http://video.mp4')
    await whatsapp_api.send_template('+1234567890', 'template')
    await whatsapp_api.get_business_profile()

    # Rate limit should be called for each method
    assert whatsapp_api._rate_limit_check.call_count == 5
