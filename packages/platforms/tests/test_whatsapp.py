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

from agoras.platforms.whatsapp import WhatsApp
from agoras.platforms.whatsapp.api import WhatsAppAPI
from agoras.platforms.whatsapp.auth import WhatsAppAuthManager
from agoras.platforms.whatsapp.client import WhatsAppAPIClient

# WhatsApp Wrapper Tests


@pytest.mark.asyncio
@patch('agoras.platforms.whatsapp.wrapper.WhatsAppAPI')
async def test_whatsapp_initialize_client(mock_api_class):
    """Test WhatsApp _initialize_client extracts config and creates API."""
    mock_api = MagicMock()
    mock_api.authenticate = AsyncMock()
    mock_api_class.return_value = mock_api

    whatsapp = WhatsApp(
        whatsapp_access_token='test_token',
        whatsapp_phone_number_id='123456',
        whatsapp_recipient='1234567890'
    )

    await whatsapp._initialize_client()

    assert whatsapp.whatsapp_access_token == 'test_token'
    assert whatsapp.whatsapp_phone_number_id == '123456'
    assert whatsapp.api is mock_api
    mock_api.authenticate.assert_called_once()


@pytest.mark.asyncio
@patch('agoras.platforms.whatsapp.wrapper.WhatsAppAPI')
@patch('agoras.platforms.whatsapp.auth.WhatsAppAuthManager')
async def test_whatsapp_initialize_client_from_storage_without_business_account(
    mock_auth_class, mock_api_class,
):
    """Stored credentials need only access token and phone number ID."""
    mock_auth = MagicMock()
    mock_auth._load_credentials_from_storage.return_value = True
    mock_auth.access_token = 'stored_token'
    mock_auth.phone_number_id = 'phone123'
    mock_auth.business_account_id = None
    mock_auth_class.return_value = mock_auth

    mock_api = MagicMock()
    mock_api.authenticate = AsyncMock()
    mock_api_class.return_value = mock_api

    whatsapp = WhatsApp(whatsapp_recipient='+1234567890')
    await whatsapp._initialize_client()

    assert whatsapp.whatsapp_access_token == 'stored_token'
    assert whatsapp.whatsapp_phone_number_id == 'phone123'
    mock_api.authenticate.assert_called_once()


@pytest.mark.asyncio
@patch('agoras.platforms.whatsapp.wrapper.WhatsAppAPI')
@patch('agoras.platforms.whatsapp.auth.WhatsAppAuthManager._load_credentials_from_storage', return_value=False)
async def test_whatsapp_initialize_client_missing_credentials(mock_load_credentials, mock_api_class):
    """Test WhatsApp _initialize_client raises exception without credentials."""
    mock_api = MagicMock()
    mock_api.authenticate = AsyncMock()
    mock_api_class.return_value = mock_api

    whatsapp = WhatsApp(whatsapp_recipient='+1234567890')  # Provide recipient but not credentials

    with pytest.raises(Exception, match="Not authenticated. Please run 'agoras whatsapp authorize' first."):
        await whatsapp._initialize_client()


@pytest.mark.asyncio
@patch('agoras.platforms.whatsapp.wrapper.WhatsAppAPI')
async def test_whatsapp_post(mock_api_class):
    """Test WhatsApp post method."""
    mock_api = MagicMock()
    mock_api.authenticate = AsyncMock()
    mock_api.send_message = AsyncMock(return_value='message-789')
    mock_api_class.return_value = mock_api

    whatsapp = WhatsApp(
        whatsapp_access_token='token',
        whatsapp_phone_number_id='123',
        whatsapp_recipient='1234567890'
    )

    await whatsapp._initialize_client()

    with patch.object(whatsapp, '_output_status'):
        result = await whatsapp.post('Hello WhatsApp', 'http://link.com')

    assert result == 'message-789'
    mock_api.send_message.assert_called_once()


@pytest.mark.asyncio
@patch('agoras.platforms.whatsapp.wrapper.WhatsAppAPI')
async def test_whatsapp_disconnect(mock_api_class):
    """Test WhatsApp disconnect method."""
    mock_api = MagicMock()
    mock_api.authenticate = AsyncMock()
    mock_api.disconnect = AsyncMock()
    mock_api_class.return_value = mock_api

    whatsapp = WhatsApp(
        whatsapp_access_token='token',
        whatsapp_phone_number_id='123',
        whatsapp_recipient='1234567890'
    )

    await whatsapp._initialize_client()
    await whatsapp.disconnect()

    mock_api.disconnect.assert_called_once()


# WhatsApp API Tests

def test_whatsapp_api_instantiation():
    """Test WhatsAppAPI can be instantiated."""
    api = WhatsAppAPI('token', 'phone_id')
    assert api is not None


# WhatsApp Auth Tests (Abstract - test via concrete usage)

def test_whatsapp_auth_class_exists():
    """Test WhatsAppAuthManager class exists."""
    assert WhatsAppAuthManager is not None


# WhatsApp Client Tests

def test_whatsapp_client_class_exists():
    """Test WhatsAppAPIClient class exists."""
    assert WhatsAppAPIClient is not None


@pytest.mark.asyncio
@patch("agoras.platforms.whatsapp.wrapper.WhatsAppAPI")
async def test_whatsapp_post_local_image_uploads_media_id(mock_api_class):
    """Local image post uploads bytes and sends image id payload."""
    mock_api = MagicMock()
    mock_api.authenticate = AsyncMock()
    mock_api.upload_media = AsyncMock(return_value="media-123")
    mock_api.send_image = AsyncMock(return_value="message-456")
    mock_api_class.return_value = mock_api

    whatsapp = WhatsApp(
        whatsapp_access_token="token",
        whatsapp_phone_number_id="123",
        whatsapp_recipient="1234567890",
    )
    await whatsapp._initialize_client()

    mock_image = MagicMock()
    mock_image.url = "/tmp/pic.png"
    mock_image.content = b"png-bytes"
    mock_image.file_type = MagicMock(mime="image/png", extension="png")
    mock_image._is_local = True
    mock_image.cleanup = MagicMock()

    with patch.object(whatsapp, "download_images", new_callable=AsyncMock, return_value=[mock_image]):
        with patch.object(whatsapp, "_output_status"):
            result = await whatsapp.post("Caption", "", status_image_url_1="/tmp/pic.png")

    assert result == "message-456"
    mock_api.upload_media.assert_called_once_with(b"png-bytes", "image/png", filename="image.png")
    mock_api.send_image.assert_called_once_with(
        to="1234567890",
        image_id="media-123",
        caption="Caption",
    )


@pytest.mark.asyncio
@patch("agoras.platforms.whatsapp.wrapper.WhatsAppAPI")
async def test_whatsapp_video_local_uploads_media_id(mock_api_class):
    """Local video upload sends video id payload instead of link."""
    mock_api = MagicMock()
    mock_api.authenticate = AsyncMock()
    mock_api.upload_media = AsyncMock(return_value="media-789")
    mock_api.send_video = AsyncMock(return_value="message-999")
    mock_api_class.return_value = mock_api

    whatsapp = WhatsApp(
        whatsapp_access_token="token",
        whatsapp_phone_number_id="123",
        whatsapp_recipient="1234567890",
    )
    await whatsapp._initialize_client()

    mock_video = MagicMock()
    mock_video.url = "/tmp/clip.mp4"
    mock_video.content = b"mp4-bytes"
    mock_video.file_type = MagicMock(mime="video/mp4", extension="mp4")
    mock_video._is_local = True
    mock_video.cleanup = MagicMock()

    with patch.object(whatsapp, "download_video", new_callable=AsyncMock, return_value=mock_video):
        with patch.object(whatsapp, "_output_status"):
            result = await whatsapp.video("Video caption", "/tmp/clip.mp4", "Title")

    assert result == "message-999"
    mock_api.upload_media.assert_called_once_with(b"mp4-bytes", "video/mp4", filename="video.mp4")
    mock_api.send_video.assert_called_once_with(
        to="1234567890",
        video_id="media-789",
        caption="Video caption",
    )


@pytest.mark.asyncio
@patch("agoras.platforms.whatsapp.wrapper.WhatsAppAPI")
async def test_whatsapp_reply_text_only(mock_api_class):
    """Test WhatsApp reply with text only posts a reply message."""
    mock_api = MagicMock()
    mock_api.authenticate = AsyncMock()
    mock_api.reply = AsyncMock(return_value="reply-789")
    mock_api_class.return_value = mock_api

    whatsapp = WhatsApp(
        whatsapp_access_token="token",
        whatsapp_phone_number_id="123",
        whatsapp_recipient="1234567890",
    )
    await whatsapp._initialize_client()

    with patch.object(whatsapp, "_output_status"):
        result = await whatsapp.reply("wa-msg-1", "A reply")

    assert result == "reply-789"
    mock_api.reply.assert_called_once_with("1234567890", "wa-msg-1", text="A reply")


@pytest.mark.asyncio
@patch("agoras.platforms.whatsapp.wrapper.WhatsAppAPI")
async def test_whatsapp_reply_via_base_handler_uses_converter_key(mock_api_class):
    """End-to-end: CLI converter emits whatsapp_message_id, base handler must reach WhatsApp.reply.

    Regression for the P1 where the base handler read config key ``post_id`` but the
    converter maps ``--post-id`` to ``whatsapp_message_id`` for WhatsApp. The wrapper
    __init__ remaps ``whatsapp_message_id`` -> ``post_id`` so the shared handler works.
    """
    mock_api = MagicMock()
    mock_api.authenticate = AsyncMock()
    mock_api.reply = AsyncMock(return_value="reply-789")
    mock_api_class.return_value = mock_api

    whatsapp = WhatsApp(
        whatsapp_access_token="token",
        whatsapp_phone_number_id="123",
        whatsapp_recipient="1234567890",
        action="reply",
        whatsapp_message_id="wa-msg-1",
        status_text="A reply",
    )
    await whatsapp._initialize_client()

    with patch.object(whatsapp, "_output_status"):
        await whatsapp._handle_reply_action()

    mock_api.reply.assert_called_once_with("1234567890", "wa-msg-1", text="A reply")


@pytest.mark.asyncio
@patch("agoras.platforms.whatsapp.wrapper.WhatsAppAPI")
async def test_whatsapp_reply_with_image(mock_api_class):
    """Test WhatsApp reply with an image posts a reply image."""
    mock_api = MagicMock()
    mock_api.authenticate = AsyncMock()
    mock_api.reply = AsyncMock(return_value="reply-789")
    mock_api_class.return_value = mock_api

    mock_image = MagicMock()
    mock_image.url = "http://example.com/img.jpg"
    mock_image.content = b"image_data"
    mock_image.file_type = MagicMock(mime="image/jpeg", extension="jpg")
    mock_image._is_local = False
    mock_image.cleanup = MagicMock()

    whatsapp = WhatsApp(
        whatsapp_access_token="token",
        whatsapp_phone_number_id="123",
        whatsapp_recipient="1234567890",
    )
    await whatsapp._initialize_client()

    with patch.object(whatsapp, "download_images", new_callable=AsyncMock, return_value=[mock_image]):
        with patch.object(whatsapp, "_output_status"):
            result = await whatsapp.reply("wa-msg-1", "A reply", "http://example.com/img.jpg")

    assert result == "reply-789"
    mock_api.reply.assert_called_once_with(
        "1234567890", "wa-msg-1", text="A reply", image_url="http://example.com/img.jpg"
    )


@pytest.mark.asyncio
@patch("agoras.platforms.whatsapp.wrapper.WhatsAppAPI")
async def test_whatsapp_reply_with_multiple_images(mock_api_class):
    """Test WhatsApp reply sends every image (parity with post), not just the first."""
    mock_api = MagicMock()
    mock_api.authenticate = AsyncMock()
    mock_api.reply = AsyncMock(return_value="reply-789")
    mock_api_class.return_value = mock_api

    def _img(url):
        img = MagicMock()
        img.url = url
        img.content = b"image_data"
        img.file_type = MagicMock(mime="image/jpeg", extension="jpg")
        img._is_local = False
        img.cleanup = MagicMock()
        return img

    images = [_img("http://example.com/1.jpg"), _img("http://example.com/2.jpg")]
    whatsapp = WhatsApp(
        whatsapp_access_token="token",
        whatsapp_phone_number_id="123",
        whatsapp_recipient="1234567890",
    )
    await whatsapp._initialize_client()

    with patch.object(whatsapp, "download_images", new_callable=AsyncMock, return_value=images):
        with patch.object(whatsapp, "_output_status"):
            result = await whatsapp.reply(
                "wa-msg-1", "A reply", "http://example.com/1.jpg", "http://example.com/2.jpg"
            )

    assert result == "reply-789"
    assert mock_api.reply.call_count == 2
    mock_api.reply.assert_any_call(
        "1234567890", "wa-msg-1", text="A reply", image_url="http://example.com/1.jpg"
    )
    mock_api.reply.assert_any_call(
        "1234567890", "wa-msg-1", text="A reply", image_url="http://example.com/2.jpg"
    )


@pytest.mark.asyncio
@patch("agoras.platforms.whatsapp.wrapper.WhatsAppAPI")
async def test_whatsapp_reply_no_post_id(mock_api_class):
    """Test WhatsApp reply raises when no post_id provided."""
    mock_api = MagicMock()
    mock_api.authenticate = AsyncMock()
    mock_api_class.return_value = mock_api

    whatsapp = WhatsApp(
        whatsapp_access_token="token",
        whatsapp_phone_number_id="123",
        whatsapp_recipient="1234567890",
    )
    await whatsapp._initialize_client()

    with pytest.raises(Exception, match="WhatsApp message ID is required for reply action."):
        await whatsapp.reply(None, "A reply")


@pytest.mark.asyncio
@patch("agoras.platforms.whatsapp.wrapper.WhatsAppAPI")
async def test_whatsapp_reply_no_content(mock_api_class):
    """Test WhatsApp reply raises when no text or media provided."""
    mock_api = MagicMock()
    mock_api.authenticate = AsyncMock()
    mock_api_class.return_value = mock_api

    whatsapp = WhatsApp(
        whatsapp_access_token="token",
        whatsapp_phone_number_id="123",
        whatsapp_recipient="1234567890",
    )
    await whatsapp._initialize_client()

    with pytest.raises(Exception, match="No reply text or media provided."):
        await whatsapp.reply("wa-msg-1", None)


@pytest.mark.asyncio
@patch("agoras.platforms.whatsapp.wrapper.WhatsAppAPI")
async def test_whatsapp_execute_action_reply(mock_api_class):
    """Test WhatsApp execute_action dispatches reply to wrapper reply."""
    mock_api = MagicMock()
    mock_api.authenticate = AsyncMock()
    mock_api_class.return_value = mock_api

    whatsapp = WhatsApp(
        whatsapp_access_token="token",
        whatsapp_phone_number_id="123",
        whatsapp_recipient="1234567890",
        post_id="wa-msg-1",
        status_text="A reply",
    )
    await whatsapp._initialize_client()

    with patch.object(whatsapp, "reply", new_callable=AsyncMock) as mock_reply:
        await whatsapp.execute_action("reply")
        mock_reply.assert_called_once_with(
            "wa-msg-1", "A reply",
            status_image_url_1=None, status_image_url_2=None,
            status_image_url_3=None, status_image_url_4=None, video_url=None,
        )
