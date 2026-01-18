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

from agoras.platforms.telegram.api import TelegramAPI


@pytest.fixture
def telegram_api():
    """Fixture to create TelegramAPI instance with mocked auth."""
    with patch('agoras.platforms.telegram.api.TelegramAuthManager') as mock_auth_class:
        mock_auth = MagicMock()
        mock_auth.authenticate = AsyncMock()
        mock_auth.bot_token = 'bot_token'
        mock_auth.user_info = {'id': 123, 'username': 'testbot'}
        mock_auth_class.return_value = mock_auth

        api = TelegramAPI('bot_token', 'chat_id')
        api._authenticated = True
        api.client = MagicMock()
        api.client.send_message = MagicMock(return_value={'message_id': 123})
        api.client.send_photo = MagicMock(return_value={'message_id': 124})
        api.client.send_video = MagicMock(return_value={'message_id': 125})
        api.client.send_media_group = MagicMock(return_value=[
            {'message_id': 129}, {'message_id': 130}
        ])
        api.client.delete_message = MagicMock()
        api.client.get_me = MagicMock(return_value={'id': 123, 'username': 'testbot'})
        yield api


# Authentication Tests

@pytest.mark.asyncio
@patch('agoras.platforms.telegram.api.TelegramAuthManager')
async def test_telegram_api_authenticate(mock_auth_class):
    """Test TelegramAPI authenticate method."""
    mock_auth = MagicMock()
    mock_auth.authenticate = AsyncMock(return_value=True)
    mock_auth.bot_token = 'bot_token'
    mock_auth.client = MagicMock()
    mock_auth_class.return_value = mock_auth

    api = TelegramAPI('bot_token', 'chat_id')
    result = await api.authenticate()

    assert api._authenticated is True
    assert result is api
    mock_auth.authenticate.assert_called_once()


@pytest.mark.asyncio
async def test_telegram_api_disconnect(telegram_api):
    """Test TelegramAPI disconnect method."""
    await telegram_api.disconnect()

    assert telegram_api._authenticated is False
    assert telegram_api.client is None


@pytest.mark.asyncio
async def test_telegram_api_get_bot_info(telegram_api):
    """Test TelegramAPI get_bot_info method."""
    result = await telegram_api.get_bot_info()

    assert result == {'id': 123, 'username': 'testbot'}
    telegram_api.client.get_me.assert_called_once()


# Messaging Tests

@pytest.mark.asyncio
async def test_telegram_api_send_message(telegram_api):
    """Test TelegramAPI send_message."""
    result = await telegram_api.send_message('chat_id', 'Test message')

    assert result == '123'
    telegram_api.client.send_message.assert_called_once_with(
        chat_id='chat_id',
        text='Test message',
        parse_mode=None
    )


@pytest.mark.asyncio
async def test_telegram_api_send_photo(telegram_api):
    """Test TelegramAPI send_photo."""
    result = await telegram_api.send_photo('chat_id', photo_content=b'image_data', caption='Photo caption')

    assert result == '124'
    telegram_api.client.send_photo.assert_called_once_with(
        chat_id='chat_id',
        photo=b'image_data',
        caption='Photo caption',
        parse_mode=None
    )


@pytest.mark.asyncio
@patch('agoras.media.MediaFactory')
async def test_telegram_api_send_photo_with_url(mock_media_factory, telegram_api):
    """Test TelegramAPI send_photo with URL."""
    mock_image = MagicMock()
    mock_image.content = b'image_content'
    mock_file_type = MagicMock()
    mock_file_type.mime = 'image/jpeg'
    mock_image.file_type = mock_file_type
    mock_image.url = 'http://image.jpg'
    mock_image.cleanup = MagicMock()
    mock_media_factory.download_images = AsyncMock(return_value=[mock_image])

    result = await telegram_api.send_photo('chat_id', photo_url='http://image.jpg')

    assert result == '124'
    mock_image.cleanup.assert_called()


@pytest.mark.asyncio
async def test_telegram_api_send_video(telegram_api):
    """Test TelegramAPI send_video."""
    result = await telegram_api.send_video('chat_id', video_content=b'video_data', caption='Video caption')

    assert result == '125'
    telegram_api.client.send_video.assert_called_once_with(
        chat_id='chat_id',
        video=b'video_data',
        caption='Video caption',
        parse_mode=None
    )


@pytest.mark.asyncio
@patch('agoras.media.MediaFactory')
async def test_telegram_api_send_video_with_url(mock_media_factory, telegram_api):
    """Test TelegramAPI send_video with URL."""
    mock_video = MagicMock()
    mock_video.content = b'video_content'
    mock_file_type = MagicMock()
    mock_file_type.mime = 'video/mp4'
    mock_video.file_type = mock_file_type
    mock_video.url = 'http://video.mp4'
    mock_video.cleanup = MagicMock()
    mock_video.download = AsyncMock()  # Mock download to avoid actual HTTP call
    mock_media_factory.create_video = MagicMock(return_value=mock_video)

    result = await telegram_api.send_video('chat_id', video_url='http://video.mp4')

    assert result == '125'
    mock_video.download.assert_called_once()
    mock_video.cleanup.assert_called()


@pytest.mark.asyncio
async def test_telegram_api_send_media_group(telegram_api):
    """Test TelegramAPI send_media_group."""
    media = [
        {'type': 'photo', 'media': 'http://image1.jpg'},
        {'type': 'photo', 'media': 'http://image2.jpg'}
    ]
    result = await telegram_api.send_media_group('chat_id', media)

    assert result == ['129', '130']
    telegram_api.client.send_media_group.assert_called_once_with(
        chat_id='chat_id',
        media=media
    )


@pytest.mark.asyncio
async def test_telegram_api_send_message_with_reply_markup(telegram_api):
    """Test TelegramAPI send_message with parse mode."""
    result = await telegram_api.send_message('chat_id', 'Test message', parse_mode='HTML')

    assert result == '123'
    telegram_api.client.send_message.assert_called_once_with(
        chat_id='chat_id',
        text='Test message',
        parse_mode='HTML'
    )


# Operation Tests

@pytest.mark.asyncio
async def test_telegram_api_delete_message(telegram_api):
    """Test TelegramAPI delete_message."""
    result = await telegram_api.delete_message('chat_id', 123)

    assert result == '123'
    telegram_api.client.delete_message.assert_called_once_with(chat_id='chat_id', message_id=123)


@pytest.mark.asyncio
async def test_telegram_api_post_wrapper(telegram_api):
    """Test TelegramAPI post wrapper method."""
    result = await telegram_api.post(chat_id='chat_id', text='Test post')

    assert result == '123'
    telegram_api.client.send_message.assert_called_once()


@pytest.mark.asyncio
async def test_telegram_api_share_not_supported(telegram_api):
    """Test TelegramAPI share is not supported."""
    with pytest.raises(Exception, match='Share not supported'):
        await telegram_api.share('msg-123')


# Not Supported Tests

@pytest.mark.asyncio
async def test_telegram_api_like_raises_exception(telegram_api):
    """Test TelegramAPI like raises exception."""
    with pytest.raises(Exception, match='Like not supported'):
        await telegram_api.like('msg-123')


# Error Handling Tests

@pytest.mark.asyncio
async def test_telegram_api_send_error(telegram_api):
    """Test TelegramAPI handles send errors."""
    telegram_api.client.send_message = MagicMock(side_effect=Exception('Send failed'))

    with pytest.raises(Exception, match='Send failed'):
        await telegram_api.send_message('chat_id', 'Test')


@pytest.mark.asyncio
async def test_telegram_api_not_authenticated(telegram_api):
    """Test TelegramAPI methods require authentication."""
    telegram_api._authenticated = False
    telegram_api.client = None
    telegram_api.authenticate = AsyncMock(side_effect=Exception('Authentication failed'))

    with pytest.raises(Exception, match='Authentication failed'):
        await telegram_api.send_message('chat_id', 'Test')


@pytest.mark.asyncio
@patch('agoras.platforms.telegram.api.TelegramAuthManager')
async def test_telegram_api_bot_token_invalid(mock_auth_class):
    """Test TelegramAPI handles invalid bot token."""
    mock_auth = MagicMock()
    mock_auth.authenticate = AsyncMock(return_value=False)
    mock_auth_class.return_value = mock_auth

    api = TelegramAPI('invalid_token', 'chat_id')

    with pytest.raises(Exception, match='Telegram authentication failed'):
        await api.authenticate()


# Additional Tests for Coverage

@pytest.mark.asyncio
async def test_telegram_api_send_media_group_single_item(telegram_api):
    """Test TelegramAPI send_media_group with single media item."""
    media = [{'type': 'photo', 'media': 'http://image1.jpg'}]
    telegram_api.client.send_media_group = MagicMock(return_value=[{'message_id': 129}])

    result = await telegram_api.send_media_group('chat_id', media)

    assert result == ['129']
    telegram_api.client.send_media_group.assert_called_once_with(chat_id='chat_id', media=media)


@pytest.mark.asyncio
async def test_telegram_api_send_media_group_mixed_types(telegram_api):
    """Test TelegramAPI send_media_group with mixed media types."""
    media = [
        {'type': 'photo', 'media': 'http://image1.jpg'},
        {'type': 'video', 'media': 'http://video1.mp4'},
        {'type': 'document', 'media': 'http://doc1.pdf'}
    ]
    telegram_api.client.send_media_group = MagicMock(return_value=[
        {'message_id': 129}, {'message_id': 130}, {'message_id': 131}
    ])

    result = await telegram_api.send_media_group('chat_id', media)

    assert len(result) == 3
    assert result == ['129', '130', '131']


@pytest.mark.asyncio
@patch('agoras.media.MediaFactory')
async def test_telegram_api_send_photo_with_parse_mode(mock_media_factory, telegram_api):
    """Test TelegramAPI send_photo with parse mode in caption."""
    mock_image = MagicMock()
    mock_image.content = b'image_content'
    mock_file_type = MagicMock()
    mock_file_type.mime = 'image/jpeg'
    mock_image.file_type = mock_file_type
    mock_image.url = 'http://image.jpg'
    mock_image.cleanup = MagicMock()
    mock_media_factory.download_images = AsyncMock(return_value=[mock_image])

    result = await telegram_api.send_photo('chat_id', photo_url='http://image.jpg', caption='<b>Caption</b>', parse_mode='HTML')

    assert result == '124'
    telegram_api.client.send_photo.assert_called_once()
    call_kwargs = telegram_api.client.send_photo.call_args[1]
    assert call_kwargs['parse_mode'] == 'HTML'


@pytest.mark.asyncio
@patch('agoras.media.MediaFactory')
async def test_telegram_api_send_video_with_parse_mode(mock_media_factory, telegram_api):
    """Test TelegramAPI send_video with parse mode in caption."""
    mock_video = MagicMock()
    mock_video.content = b'video_content'
    mock_file_type = MagicMock()
    mock_file_type.mime = 'video/mp4'
    mock_video.file_type = mock_file_type
    mock_video.url = 'http://video.mp4'
    mock_video.cleanup = MagicMock()
    mock_video.download = AsyncMock()
    mock_media_factory.create_video = MagicMock(return_value=mock_video)

    result = await telegram_api.send_video('chat_id', video_url='http://video.mp4', caption='*Bold* caption', parse_mode='Markdown')

    assert result == '125'
    telegram_api.client.send_video.assert_called_once()
    call_kwargs = telegram_api.client.send_video.call_args[1]
    assert call_kwargs['parse_mode'] == 'Markdown'


@pytest.mark.asyncio
async def test_telegram_api_send_message_markdown_v2(telegram_api):
    """Test TelegramAPI send_message with MarkdownV2 parse mode."""
    result = await telegram_api.send_message('chat_id', 'Test *message*', parse_mode='MarkdownV2')

    assert result == '123'
    telegram_api.client.send_message.assert_called_once_with(
        chat_id='chat_id',
        text='Test *message*',
        parse_mode='MarkdownV2'
    )


@pytest.mark.asyncio
@patch('agoras.media.MediaFactory')
async def test_telegram_api_send_photo_download_failure(mock_media_factory, telegram_api):
    """Test TelegramAPI send_photo handles download failure."""
    mock_media_factory.download_images = AsyncMock(return_value=[])  # Empty list

    with pytest.raises(Exception, match='Failed to download image'):
        await telegram_api.send_photo('chat_id', photo_url='http://image.jpg')


@pytest.mark.asyncio
@patch('agoras.media.MediaFactory')
async def test_telegram_api_send_video_download_failure(mock_media_factory, telegram_api):
    """Test TelegramAPI send_video handles download failure."""
    mock_video = MagicMock()
    mock_video.content = None  # Download failed
    mock_video.file_type = None
    mock_video.url = 'http://video.mp4'
    mock_video.cleanup = MagicMock()
    mock_video.download = AsyncMock()
    mock_media_factory.create_video = MagicMock(return_value=mock_video)

    with pytest.raises(Exception, match='Failed to validate video'):
        await telegram_api.send_video('chat_id', video_url='http://video.mp4')


@pytest.mark.asyncio
async def test_telegram_api_send_photo_no_content_error(telegram_api):
    """Test TelegramAPI send_photo raises error when no content available."""
    with pytest.raises(Exception, match='No photo content available'):
        await telegram_api.send_photo('chat_id', photo_url=None, photo_content=None)


@pytest.mark.asyncio
async def test_telegram_api_send_video_no_content_error(telegram_api):
    """Test TelegramAPI send_video raises error when no content available."""
    with pytest.raises(Exception, match='No video content available'):
        await telegram_api.send_video('chat_id', video_url=None, video_content=None)


@pytest.mark.asyncio
async def test_telegram_api_delete_message_converts_to_int(telegram_api):
    """Test TelegramAPI delete_message converts message_id to int."""
    result = await telegram_api.delete_message('chat_id', '123')  # String ID

    assert result == '123'
    telegram_api.client.delete_message.assert_called_once_with(chat_id='chat_id', message_id=123)


@pytest.mark.asyncio
async def test_telegram_api_all_methods_use_rate_limiting(telegram_api):
    """Test all TelegramAPI methods use rate limiting."""
    telegram_api._rate_limit_check = AsyncMock()

    await telegram_api.send_message('chat_id', 'Test')
    await telegram_api.send_photo('chat_id', photo_content=b'data')
    await telegram_api.send_video('chat_id', video_content=b'data')
    await telegram_api.send_media_group('chat_id', [{'type': 'photo', 'media': 'http://img.jpg'}])
    await telegram_api.delete_message('chat_id', 123)
    # get_bot_info doesn't use rate limiting, so we expect 5 calls

    # Rate limit should be called for methods that use it
    assert telegram_api._rate_limit_check.call_count == 5


# Property Tests

def test_telegram_api_properties():
    """Test TelegramAPI property accessors."""
    with patch('agoras.platforms.telegram.api.TelegramAuthManager') as mock_auth_class:
        mock_auth = MagicMock()
        mock_auth.bot_token = 'bot_token123'
        mock_auth.user_info = {'id': 123, 'username': 'testbot'}
        mock_auth_class.return_value = mock_auth

        api = TelegramAPI('bot_token', 'chat_id')

        assert api.bot_token == 'bot_token123'
        assert api.user_info == {'id': 123, 'username': 'testbot'}
