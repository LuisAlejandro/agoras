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

from agoras.platforms.telegram import Telegram
from agoras.platforms.telegram.api import TelegramAPI
from agoras.platforms.telegram.auth import TelegramAuthManager, normalize_chat_id
from agoras.platforms.telegram.client import TelegramAPIClient

# Telegram Wrapper Tests


@pytest.mark.asyncio
@patch("agoras.platforms.telegram.wrapper.TelegramAPI")
async def test_telegram_initialize_client(mock_api_class):
    """Test Telegram _initialize_client extracts config and creates API."""
    mock_api = MagicMock()
    mock_api.authenticate = AsyncMock()
    mock_api_class.return_value = mock_api

    telegram = Telegram(telegram_bot_token="test_token", telegram_chat_id="123456")

    await telegram._initialize_client()

    assert telegram.telegram_bot_token == "test_token"
    assert telegram.telegram_chat_id == "123456"
    assert telegram.api is mock_api
    mock_api.authenticate.assert_called_once()


@pytest.mark.asyncio
@patch.dict("os.environ", {}, clear=True)
@patch("agoras.platforms.telegram.auth.TelegramAuthManager._load_credentials_from_storage", return_value=False)
async def test_telegram_initialize_client_missing_token(mock_load_credentials):
    """Test Telegram _initialize_client raises exception without token."""
    telegram = Telegram()

    with pytest.raises(Exception, match="Not authenticated. Please run 'agoras telegram authorize' first."):
        await telegram._initialize_client()


@pytest.mark.asyncio
@patch.dict("os.environ", {}, clear=True)
@patch("agoras.platforms.telegram.auth.TelegramAuthManager._load_credentials_from_storage", return_value=False)
async def test_telegram_initialize_client_missing_chat_id(mock_load_credentials):
    """Test Telegram _initialize_client raises exception without chat ID."""
    telegram = Telegram(telegram_bot_token="token")

    with pytest.raises(Exception, match="Not authenticated. Please run 'agoras telegram authorize' first."):
        await telegram._initialize_client()


@pytest.mark.asyncio
@patch("agoras.platforms.telegram.wrapper.TelegramAPI")
async def test_telegram_post(mock_api_class):
    """Test Telegram post method."""
    mock_api = MagicMock()
    mock_api.authenticate = AsyncMock()
    mock_api.send_message = AsyncMock(return_value="message-456")
    mock_api_class.return_value = mock_api

    telegram = Telegram(telegram_bot_token="token", telegram_chat_id="123")

    await telegram._initialize_client()

    # Mock _output_status to avoid print
    with patch.object(telegram, "_output_status"):
        result = await telegram.post("Hello Telegram", "http://link.com")

    assert result == "message-456"
    mock_api.send_message.assert_called_once()


@pytest.mark.asyncio
@patch("agoras.platforms.telegram.wrapper.TelegramAPI")
async def test_telegram_post_with_local_image_path(mock_api_class):
    """Telegram image posts download a local path before send_photo."""
    mock_api = MagicMock()
    mock_api.authenticate = AsyncMock()
    mock_api.send_photo = AsyncMock(return_value="photo-local")
    mock_api_class.return_value = mock_api

    mock_image = MagicMock()
    mock_image.content = b"local_jpeg"
    mock_image.file_type = MagicMock()
    mock_image.url = "/tmp/local.jpg"
    mock_image.cleanup = MagicMock()

    telegram = Telegram(telegram_bot_token="token", telegram_chat_id="123")

    await telegram._initialize_client()

    with patch.object(telegram, "download_images", new_callable=AsyncMock, return_value=[mock_image]):
        with patch.object(telegram, "_output_status"):
            result = await telegram.post("Hello", "", status_image_url_1="/tmp/local.jpg")

    assert result == "photo-local"
    mock_api.send_photo.assert_called_once()
    assert mock_api.send_photo.call_args.kwargs["photo_url"] == "/tmp/local.jpg"


@pytest.mark.asyncio
@patch("agoras.platforms.telegram.wrapper.TelegramAPI")
async def test_telegram_video_with_local_path(mock_api_class):
    """Telegram video uploads local file bytes."""
    mock_api = MagicMock()
    mock_api.authenticate = AsyncMock()
    mock_api.send_video = AsyncMock(return_value="video-local")
    mock_api_class.return_value = mock_api

    mock_video = MagicMock()
    mock_video.content = b"video-bytes"
    mock_video.file_type = MagicMock()
    mock_video.cleanup = MagicMock()

    telegram = Telegram(telegram_bot_token="token", telegram_chat_id="123")

    await telegram._initialize_client()

    with patch.object(telegram, "download_video", new_callable=AsyncMock, return_value=mock_video):
        with patch.object(telegram, "_output_status"):
            result = await telegram.video("Caption", "/tmp/local.mp4", "Title")

    assert result == "video-local"
    mock_api.send_video.assert_called_once()
    assert mock_api.send_video.call_args.kwargs["video_content"] == b"video-bytes"


@pytest.mark.asyncio
@patch("agoras.platforms.telegram.wrapper.TelegramAPI")
async def test_telegram_disconnect(mock_api_class):
    """Test Telegram disconnect method."""
    mock_api = MagicMock()
    mock_api.authenticate = AsyncMock()
    mock_api.disconnect = AsyncMock()
    mock_api_class.return_value = mock_api

    telegram = Telegram(telegram_bot_token="token", telegram_chat_id="123")

    await telegram._initialize_client()
    await telegram.disconnect()

    mock_api.disconnect.assert_called_once()


# Telegram API Tests


def test_telegram_api_instantiation():
    """Test TelegramAPI can be instantiated."""
    api = TelegramAPI("token", "chat_id")
    assert api is not None
    assert api.bot_token == "token"


# Telegram Auth Tests (Abstract - test via concrete usage)


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        (None, None),
        ("  12345  ", "12345"),
        ("-1001234567890", "-1001234567890"),
        ("mychannel", "@mychannel"),
        ("@mychannel", "@mychannel"),
    ],
)
def test_normalize_chat_id(raw, expected):
    """Test Telegram chat ID normalization."""
    assert normalize_chat_id(raw) == expected


@pytest.mark.asyncio
@patch("agoras.core.auth.base.SecureTokenStorage")
@patch("agoras.platforms.telegram.auth.Bot")
async def test_telegram_authorize_validates_chat_access(mock_bot_class, mock_storage_class):
    """Test authorize validates chat ID with get_chat."""
    mock_bot = MagicMock()
    mock_bot.get_me = AsyncMock()
    mock_bot.get_chat = AsyncMock()
    mock_bot_class.return_value = mock_bot

    auth_manager = TelegramAuthManager(bot_token="token", chat_id="12345")
    result = await auth_manager.authorize()

    assert result is not None
    mock_bot.get_chat.assert_called_once_with("12345")


@pytest.mark.asyncio
@patch.dict("os.environ", {}, clear=True)
async def test_telegram_authorize_requires_chat_id():
    """Test authorize fails when chat ID is missing."""
    auth_manager = TelegramAuthManager(bot_token="token")

    with pytest.raises(Exception, match="Telegram chat ID is required"):
        await auth_manager.authorize()


def test_telegram_auth_class_exists():
    """Test TelegramAuthManager class exists."""
    assert TelegramAuthManager is not None


# Telegram Client Tests


def test_telegram_client_class_exists():
    """Test TelegramAPIClient class exists."""
    assert TelegramAPIClient is not None


@pytest.mark.asyncio
@patch("agoras.platforms.telegram.wrapper.TelegramAPI")
async def test_telegram_text_vs_caption_limits(mock_api_class):
    """AE4: length 2000 text-only allowed; same string as photo caption rejected."""
    from agoras.core.text_limits import TextValidationError

    mock_api = MagicMock()
    mock_api.authenticate = AsyncMock()
    mock_api.send_message = AsyncMock(return_value="message-ok")
    mock_api.send_photo = AsyncMock(return_value="photo-ok")
    mock_api_class.return_value = mock_api

    telegram = Telegram(telegram_bot_token="token", telegram_chat_id="123")
    await telegram._initialize_client()

    body = "A" * 2000

    with patch.object(telegram, "_output_status"):
        result = await telegram.post(body, "")
    assert result == "message-ok"
    mock_api.send_message.assert_called_once()

    with patch.object(telegram, "download_images", new_callable=AsyncMock) as mock_download:
        with pytest.raises(TextValidationError) as exc_info:
            await telegram.post(body, "", status_image_url_1="http://example.com/img.jpg")

    assert exc_info.value.platform == "telegram"
    assert exc_info.value.field == "caption"
    mock_download.assert_not_called()
    mock_api.send_photo.assert_not_called()


@pytest.mark.asyncio
@patch("agoras.platforms.telegram.wrapper.TelegramAPI")
async def test_telegram_reply_text_only(mock_api_class):
    """Test Telegram reply with text only posts a reply message."""
    mock_api = MagicMock()
    mock_api.authenticate = AsyncMock()
    mock_api.send_message = AsyncMock(return_value="reply-789")
    mock_api_class.return_value = mock_api

    telegram = Telegram(telegram_bot_token="token", telegram_chat_id="123")
    await telegram._initialize_client()

    with patch.object(telegram, "_output_status"):
        result = await telegram.reply("456", "A reply")

    assert result == "reply-789"
    mock_api.send_message.assert_called_once()
    assert mock_api.send_message.call_args.kwargs["reply_to_message_id"] == 456


@pytest.mark.asyncio
@patch("agoras.platforms.telegram.wrapper.TelegramAPI")
async def test_telegram_reply_via_base_handler_uses_converter_key(mock_api_class):
    """End-to-end: CLI converter emits telegram_message_id, base handler must reach Telegram.reply.

    Regression for the P1 where the base handler read config key ``post_id`` but the
    converter maps ``--post-id`` to ``telegram_message_id`` for Telegram. The wrapper
    __init__ remaps ``telegram_message_id`` -> ``post_id`` so the shared handler works.
    """
    mock_api = MagicMock()
    mock_api.authenticate = AsyncMock()
    mock_api.send_message = AsyncMock(return_value="reply-789")
    mock_api_class.return_value = mock_api

    telegram = Telegram(
        telegram_bot_token="token",
        telegram_chat_id="123",
        action="reply",
        telegram_message_id="456",
        status_text="A reply",
    )
    await telegram._initialize_client()

    with patch.object(telegram, "_output_status"):
        await telegram._handle_reply_action()

    mock_api.send_message.assert_called_once()
    assert mock_api.send_message.call_args.kwargs["reply_to_message_id"] == 456


@pytest.mark.asyncio
@patch("agoras.platforms.telegram.wrapper.TelegramAPI")
async def test_telegram_reply_with_image(mock_api_class):
    """Test Telegram reply with an image posts a reply photo."""
    mock_api = MagicMock()
    mock_api.authenticate = AsyncMock()
    mock_api.send_photo = AsyncMock(return_value="reply-789")
    mock_api_class.return_value = mock_api

    mock_image = MagicMock()
    mock_image.content = b"image_data"
    mock_image.file_type = MagicMock()
    mock_image.url = "http://example.com/img.jpg"
    mock_image.cleanup = MagicMock()

    telegram = Telegram(telegram_bot_token="token", telegram_chat_id="123")
    await telegram._initialize_client()

    with patch.object(telegram, "download_images", new_callable=AsyncMock, return_value=[mock_image]):
        with patch.object(telegram, "_output_status"):
            result = await telegram.reply("456", "A reply", "http://example.com/img.jpg")

    assert result == "reply-789"
    mock_api.send_photo.assert_called_once()
    assert mock_api.send_photo.call_args.kwargs["reply_to_message_id"] == 456


@pytest.mark.asyncio
@patch("agoras.platforms.telegram.wrapper.TelegramAPI")
async def test_telegram_reply_no_post_id(mock_api_class):
    """Test Telegram reply raises when no post_id provided."""
    mock_api = MagicMock()
    mock_api.authenticate = AsyncMock()
    mock_api_class.return_value = mock_api

    telegram = Telegram(telegram_bot_token="token", telegram_chat_id="123")
    await telegram._initialize_client()

    with pytest.raises(Exception, match="Message ID is required for reply action."):
        await telegram.reply(None, "A reply")


@pytest.mark.asyncio
@patch("agoras.platforms.telegram.wrapper.TelegramAPI")
async def test_telegram_reply_no_content(mock_api_class):
    """Test Telegram reply raises when no text or media provided."""
    mock_api = MagicMock()
    mock_api.authenticate = AsyncMock()
    mock_api_class.return_value = mock_api

    telegram = Telegram(telegram_bot_token="token", telegram_chat_id="123")
    await telegram._initialize_client()

    with pytest.raises(Exception, match="No reply text or media provided."):
        await telegram.reply("456", None)
