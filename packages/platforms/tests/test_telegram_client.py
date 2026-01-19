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

from agoras.platforms.telegram.client import TelegramAPIClient


def test_telegram_client_init():
    """Test TelegramAPIClient initialization."""
    client = TelegramAPIClient('bot_token')

    assert client.bot_token == 'bot_token'
    assert client.default_parse_mode == 'HTML'


@pytest.mark.asyncio
@patch('agoras.platforms.telegram.client.Bot')
async def test_telegram_client_get_me_success(mock_bot_class):
    """Test TelegramAPIClient get_me success."""
    mock_bot = MagicMock()
    mock_user = MagicMock()
    mock_user.id = 123
    mock_user.username = 'testbot'
    mock_user.first_name = 'Test Bot'
    mock_user.is_bot = True
    mock_user.can_join_groups = True
    mock_user.can_read_all_group_messages = False
    mock_user.supports_inline_queries = True
    mock_bot.get_me = AsyncMock(return_value=mock_user)
    mock_bot_class.return_value = mock_bot

    client = TelegramAPIClient('bot_token')
    result = await client.get_me()

    assert result == {
        'id': 123,
        'username': 'testbot',
        'first_name': 'Test Bot',
        'is_bot': True,
        'can_join_groups': True,
        'can_read_all_group_messages': False,
        'supports_inline_queries': True
    }
    mock_bot.get_me.assert_called_once()


@pytest.mark.asyncio
@patch('agoras.platforms.telegram.client.Bot')
async def test_telegram_client_get_me_no_token(mock_bot_class):
    """Test TelegramAPIClient get_me with no token."""
    mock_bot = MagicMock()
    mock_bot_class.return_value = mock_bot

    with patch.object(TelegramAPIClient, '__init__', lambda self, bot_token: None):
        client = TelegramAPIClient.__new__(TelegramAPIClient)
        client.bot_token = ''
        client.bot = mock_bot
        client.default_parse_mode = 'HTML'

        with pytest.raises(Exception, match='No bot token available'):
            await client.get_me()


@pytest.mark.asyncio
@patch('agoras.platforms.telegram.client.Bot')
async def test_telegram_client_get_me_telegram_error(mock_bot_class):
    """Test TelegramAPIClient get_me with TelegramError."""
    from telegram.error import TelegramError

    mock_bot = MagicMock()
    mock_bot.get_me = AsyncMock(side_effect=TelegramError('API Error'))
    mock_bot_class.return_value = mock_bot

    client = TelegramAPIClient('bot_token')
    client.bot = mock_bot  # Override with our mock

    with pytest.raises(Exception, match='Failed to get bot info: API Error'):
        await client.get_me()


@pytest.mark.asyncio
@patch('agoras.platforms.telegram.client.Bot')
async def test_telegram_client_send_message_success(mock_bot_class):
    """Test TelegramAPIClient send_message success."""
    mock_bot = MagicMock()
    mock_message = MagicMock()
    mock_message.to_dict.return_value = {'message_id': 123, 'text': 'test'}
    mock_bot.send_message = AsyncMock(return_value=mock_message)
    mock_bot_class.return_value = mock_bot

    client = TelegramAPIClient('bot_token')
    client.bot = mock_bot  # Override with our mock
    result = await client.send_message('chat_id', 'Test message')

    assert result == {'message_id': 123, 'text': 'test'}
    mock_bot.send_message.assert_called_once_with(
        chat_id='chat_id',
        text='Test message',
        parse_mode='HTML',
        reply_markup=None
    )


@pytest.mark.asyncio
@patch('agoras.platforms.telegram.client.Bot')
async def test_telegram_client_send_message_with_parse_mode_none(mock_bot_class):
    """Test TelegramAPIClient send_message with parse_mode=None (should use default)."""
    mock_bot = MagicMock()
    mock_message = MagicMock()
    mock_message.to_dict.return_value = {'message_id': 123, 'text': 'test'}
    mock_bot.send_message = AsyncMock(return_value=mock_message)
    mock_bot_class.return_value = mock_bot

    client = TelegramAPIClient('bot_token')
    client.bot = mock_bot  # Override with our mock
    result = await client.send_message('chat_id', 'Test message', parse_mode=None)

    assert result == {'message_id': 123, 'text': 'test'}
    mock_bot.send_message.assert_called_once_with(
        chat_id='chat_id',
        text='Test message',
        parse_mode='HTML',  # Should use default
        reply_markup=None
    )


@pytest.mark.asyncio
async def test_telegram_client_send_message_no_token():
    """Test TelegramAPIClient send_message with no token."""
    with patch.object(TelegramAPIClient, '__init__', lambda self, bot_token: None):
        client = TelegramAPIClient.__new__(TelegramAPIClient)
        client.bot_token = ''
        mock_bot = MagicMock()
        client.bot = mock_bot

        with pytest.raises(Exception, match='No bot token available'):
            await client.send_message('chat_id', 'Test')


@pytest.mark.asyncio
@patch('agoras.platforms.telegram.client.Bot')
async def test_telegram_client_send_message_with_parse_mode_none(mock_bot_class):
    """Test TelegramAPIClient send_message with parse_mode=None (should use default)."""
    mock_bot = MagicMock()
    mock_message = MagicMock()
    mock_message.to_dict.return_value = {'message_id': 123, 'text': 'test'}
    mock_bot.send_message = AsyncMock(return_value=mock_message)
    mock_bot_class.return_value = mock_bot

    client = TelegramAPIClient('bot_token')
    client.bot = mock_bot  # Override with our mock
    result = await client.send_message('chat_id', 'Test message', parse_mode=None)

    assert result == {'message_id': 123, 'text': 'test'}
    mock_bot.send_message.assert_called_once_with(
        chat_id='chat_id',
        text='Test message',
        parse_mode='HTML',  # Should use default
        reply_markup=None
    )


@pytest.mark.asyncio
@patch('agoras.platforms.telegram.client.Bot')
async def test_telegram_client_send_message_telegram_error(mock_bot_class):
    """Test TelegramAPIClient send_message with TelegramError."""
    from telegram.error import TelegramError

    mock_bot = MagicMock()
    mock_bot.send_message = AsyncMock(side_effect=TelegramError('Send failed'))
    mock_bot_class.return_value = mock_bot

    client = TelegramAPIClient('bot_token')
    client.bot = mock_bot  # Override with our mock

    with pytest.raises(Exception, match='Failed to send message: Send failed'):
        await client.send_message('chat_id', 'Test')


@pytest.mark.asyncio
@patch('agoras.platforms.telegram.client.Bot')
async def test_telegram_client_send_photo_success(mock_bot_class):
    """Test TelegramAPIClient send_photo success."""
    mock_bot = MagicMock()
    mock_message = MagicMock()
    mock_message.to_dict.return_value = {'message_id': 124, 'photo': []}
    mock_bot.send_photo = AsyncMock(return_value=mock_message)
    mock_bot_class.return_value = mock_bot

    client = TelegramAPIClient('bot_token')
    client.bot = mock_bot  # Override with our mock
    result = await client.send_photo('chat_id', 'photo_data', caption='Test caption')

    assert result == {'message_id': 124, 'photo': []}
    mock_bot.send_photo.assert_called_once_with(
        chat_id='chat_id',
        photo='photo_data',
        caption='Test caption',
        parse_mode='HTML'
    )


@pytest.mark.asyncio
async def test_telegram_client_send_photo_no_token():
    """Test TelegramAPIClient send_photo with no token."""
    with patch.object(TelegramAPIClient, '__init__', lambda self, bot_token: None):
        client = TelegramAPIClient.__new__(TelegramAPIClient)
        client.bot_token = ''
        mock_bot = MagicMock()
        client.bot = mock_bot

        with pytest.raises(Exception, match='No bot token available'):
            await client.send_photo('chat_id', 'photo_data')


@pytest.mark.asyncio
@patch('agoras.platforms.telegram.client.Bot')
async def test_telegram_client_send_photo_telegram_error(mock_bot_class):
    """Test TelegramAPIClient send_photo with TelegramError."""
    from telegram.error import TelegramError

    mock_bot = MagicMock()
    mock_bot.send_photo = AsyncMock(side_effect=TelegramError('Photo failed'))
    mock_bot_class.return_value = mock_bot

    client = TelegramAPIClient('bot_token')
    client.bot = mock_bot  # Override with our mock

    with pytest.raises(Exception, match='Failed to send photo: Photo failed'):
        await client.send_photo('chat_id', 'photo_data')


@pytest.mark.asyncio
@patch('agoras.platforms.telegram.client.Bot')
async def test_telegram_client_send_video_success(mock_bot_class):
    """Test TelegramAPIClient send_video success."""
    mock_bot = MagicMock()
    mock_message = MagicMock()
    mock_message.to_dict.return_value = {'message_id': 125, 'video': {}}
    mock_bot.send_video = AsyncMock(return_value=mock_message)
    mock_bot_class.return_value = mock_bot

    client = TelegramAPIClient('bot_token')
    client.bot = mock_bot  # Override with our mock
    result = await client.send_video('chat_id', 'video_data', caption='Test caption')

    assert result == {'message_id': 125, 'video': {}}
    mock_bot.send_video.assert_called_once_with(
        chat_id='chat_id',
        video='video_data',
        caption='Test caption',
        parse_mode='HTML',
        duration=None,
        width=None,
        height=None
    )


@pytest.mark.asyncio
async def test_telegram_client_send_video_no_token():
    """Test TelegramAPIClient send_video with no token."""
    with patch.object(TelegramAPIClient, '__init__', lambda self, bot_token: None):
        client = TelegramAPIClient.__new__(TelegramAPIClient)
        client.bot_token = ''
        mock_bot = MagicMock()
        client.bot = mock_bot

        with pytest.raises(Exception, match='No bot token available'):
            await client.send_video('chat_id', 'video_data')


@pytest.mark.asyncio
@patch('agoras.platforms.telegram.client.Bot')
async def test_telegram_client_send_video_telegram_error(mock_bot_class):
    """Test TelegramAPIClient send_video with TelegramError."""
    from telegram.error import TelegramError

    mock_bot = MagicMock()
    mock_bot.send_video = AsyncMock(side_effect=TelegramError('Video failed'))
    mock_bot_class.return_value = mock_bot

    client = TelegramAPIClient('bot_token')

    with pytest.raises(Exception, match='Failed to send video'):
        await client.send_video('chat_id', 'video_data')


@pytest.mark.asyncio
@patch('agoras.platforms.telegram.client.Bot')
async def test_telegram_client_delete_message_success(mock_bot_class):
    """Test TelegramAPIClient delete_message success."""
    mock_bot = MagicMock()
    mock_bot.delete_message = AsyncMock(return_value=True)
    mock_bot_class.return_value = mock_bot

    client = TelegramAPIClient('bot_token')
    result = await client.delete_message('chat_id', 123)

    assert result is True
    mock_bot.delete_message.assert_called_once_with(chat_id='chat_id', message_id=123)


@pytest.mark.asyncio
async def test_telegram_client_delete_message_no_token():
    """Test TelegramAPIClient delete_message with no token."""
    with patch.object(TelegramAPIClient, '__init__', lambda self, bot_token: None):
        client = TelegramAPIClient.__new__(TelegramAPIClient)
        client.bot_token = ''
        mock_bot = MagicMock()
        client.bot = mock_bot

        with pytest.raises(Exception, match='No bot token available'):
            await client.delete_message('chat_id', 123)


@pytest.mark.asyncio
@patch('agoras.platforms.telegram.client.Bot')
async def test_telegram_client_delete_message_telegram_error(mock_bot_class):
    """Test TelegramAPIClient delete_message with TelegramError."""
    from telegram.error import TelegramError

    mock_bot = MagicMock()
    mock_bot.delete_message = AsyncMock(side_effect=TelegramError('Delete failed'))
    mock_bot_class.return_value = mock_bot

    client = TelegramAPIClient('bot_token')

    with pytest.raises(Exception, match='Failed to delete message'):
        await client.delete_message('chat_id', 123)


@pytest.mark.asyncio
@patch('agoras.platforms.telegram.client.Bot')
async def test_telegram_client_send_media_group_photos(mock_bot_class):
    """Test TelegramAPIClient send_media_group with photos."""
    from telegram import InputMediaPhoto

    mock_bot = MagicMock()
    mock_message1 = MagicMock()
    mock_message1.to_dict.return_value = {'message_id': 126}
    mock_message2 = MagicMock()
    mock_message2.to_dict.return_value = {'message_id': 127}
    mock_bot.send_media_group = AsyncMock(return_value=[mock_message1, mock_message2])
    mock_bot_class.return_value = mock_bot

    client = TelegramAPIClient('bot_token')
    media = [
        {'type': 'photo', 'media': 'photo1.jpg', 'caption': 'First'},
        {'type': 'photo', 'media': 'photo2.jpg'}
    ]
    result = await client.send_media_group('chat_id', media)

    assert len(result) == 2
    assert result[0]['message_id'] == 126
    assert result[1]['message_id'] == 127
    mock_bot.send_media_group.assert_called_once()
    call_args = mock_bot.send_media_group.call_args
    assert call_args[1]['chat_id'] == 'chat_id'
    assert len(call_args[1]['media']) == 2
    assert isinstance(call_args[1]['media'][0], InputMediaPhoto)


@pytest.mark.asyncio
async def test_telegram_client_send_media_group_unsupported_type():
    """Test TelegramAPIClient send_media_group with unsupported media type."""
    client = TelegramAPIClient('bot_token')
    media = [{'type': 'document', 'media': 'doc.pdf'}]

    with pytest.raises(Exception, match='Unsupported media type: document'):
        await client.send_media_group('chat_id', media)


@pytest.mark.asyncio
async def test_telegram_client_send_media_group_no_token():
    """Test TelegramAPIClient send_media_group with no token."""
    with patch.object(TelegramAPIClient, '__init__', lambda self, bot_token: None):
        client = TelegramAPIClient.__new__(TelegramAPIClient)
        client.bot_token = ''
        mock_bot = MagicMock()
        client.bot = mock_bot
        media = [{'type': 'photo', 'media': 'photo.jpg'}]

        with pytest.raises(Exception, match='No bot token available'):
            await client.send_media_group('chat_id', media)


@pytest.mark.asyncio
@patch('agoras.platforms.telegram.client.Bot')
async def test_telegram_client_get_me_generic_exception(mock_bot_class):
    """Test TelegramAPIClient get_me with generic exception."""
    mock_bot = MagicMock()
    mock_bot.get_me = AsyncMock(side_effect=Exception('Network error'))
    mock_bot_class.return_value = mock_bot

    client = TelegramAPIClient('bot_token')
    client.bot = mock_bot  # Override with our mock

    with pytest.raises(Exception, match='Unexpected error getting bot info: Network error'):
        await client.get_me()


@pytest.mark.asyncio
@patch('agoras.platforms.telegram.client.Bot')
async def test_telegram_client_send_message_generic_exception(mock_bot_class):
    """Test TelegramAPIClient send_message with generic exception."""
    mock_bot = MagicMock()
    mock_bot.send_message = AsyncMock(side_effect=Exception('Network error'))
    mock_bot_class.return_value = mock_bot

    client = TelegramAPIClient('bot_token')

    with pytest.raises(Exception, match='Unexpected error sending message: Network error'):
        await client.send_message('chat_id', 'Test message')


@pytest.mark.asyncio
@patch('agoras.platforms.telegram.client.Bot')
async def test_telegram_client_send_photo_generic_exception(mock_bot_class):
    """Test TelegramAPIClient send_photo with generic exception."""
    mock_bot = MagicMock()
    mock_bot.send_photo = AsyncMock(side_effect=Exception('Network error'))
    mock_bot_class.return_value = mock_bot

    client = TelegramAPIClient('bot_token')

    with pytest.raises(Exception, match='Unexpected error sending photo: Network error'):
        await client.send_photo('chat_id', 'photo_data')


@pytest.mark.asyncio
@patch('agoras.platforms.telegram.client.Bot')
async def test_telegram_client_send_video_generic_exception(mock_bot_class):
    """Test TelegramAPIClient send_video with generic exception."""
    mock_bot = MagicMock()
    mock_bot.send_video = AsyncMock(side_effect=Exception('Network error'))
    mock_bot_class.return_value = mock_bot

    client = TelegramAPIClient('bot_token')

    with pytest.raises(Exception, match='Unexpected error sending video: Network error'):
        await client.send_video('chat_id', 'video_data')


@pytest.mark.asyncio
@patch('agoras.platforms.telegram.client.Bot')
async def test_telegram_client_delete_message_generic_exception(mock_bot_class):
    """Test TelegramAPIClient delete_message with generic exception."""
    mock_bot = MagicMock()
    mock_bot.delete_message = AsyncMock(side_effect=Exception('Network error'))
    mock_bot_class.return_value = mock_bot

    client = TelegramAPIClient('bot_token')

    with pytest.raises(Exception, match='Unexpected error deleting message: Network error'):
        await client.delete_message('chat_id', 123)


@pytest.mark.asyncio
@patch('agoras.platforms.telegram.client.Bot')
async def test_telegram_client_send_media_group_generic_exception(mock_bot_class):
    """Test TelegramAPIClient send_media_group with generic exception."""
    mock_bot = MagicMock()
    mock_bot.send_media_group = AsyncMock(side_effect=Exception('Network error'))
    mock_bot_class.return_value = mock_bot

    client = TelegramAPIClient('bot_token')
    media = [{'type': 'photo', 'media': 'photo.jpg'}]

    with pytest.raises(Exception, match='Unexpected error sending media group: Network error'):
        await client.send_media_group('chat_id', media)


@pytest.mark.asyncio
@patch('agoras.platforms.telegram.client.Bot')
async def test_telegram_client_send_photo_without_caption(mock_bot_class):
    """Test TelegramAPIClient send_photo without caption."""
    mock_bot = MagicMock()
    mock_message = MagicMock()
    mock_message.to_dict.return_value = {'message_id': 124, 'photo': []}
    mock_bot.send_photo = AsyncMock(return_value=mock_message)
    mock_bot_class.return_value = mock_bot

    client = TelegramAPIClient('bot_token')
    result = await client.send_photo('chat_id', 'photo_data')

    assert result == {'message_id': 124, 'photo': []}
    mock_bot.send_photo.assert_called_once_with(
        chat_id='chat_id',
        photo='photo_data',
        caption=None,
        parse_mode='HTML'
    )


@pytest.mark.asyncio
@patch('agoras.platforms.telegram.client.Bot')
async def test_telegram_client_send_video_without_caption(mock_bot_class):
    """Test TelegramAPIClient send_video without caption."""
    mock_bot = MagicMock()
    mock_message = MagicMock()
    mock_message.to_dict.return_value = {'message_id': 125, 'video': {}}
    mock_bot.send_video = AsyncMock(return_value=mock_message)
    mock_bot_class.return_value = mock_bot

    client = TelegramAPIClient('bot_token')
    result = await client.send_video('chat_id', 'video_data')

    assert result == {'message_id': 125, 'video': {}}
    mock_bot.send_video.assert_called_once_with(
        chat_id='chat_id',
        video='video_data',
        caption=None,
        parse_mode='HTML',
        duration=None,
        width=None,
        height=None
    )


@pytest.mark.asyncio
@patch('agoras.platforms.telegram.client.Bot')
async def test_telegram_client_send_video_with_dimensions(mock_bot_class):
    """Test TelegramAPIClient send_video with dimensions and duration."""
    mock_bot = MagicMock()
    mock_message = MagicMock()
    mock_message.to_dict.return_value = {'message_id': 125, 'video': {}}
    mock_bot.send_video = AsyncMock(return_value=mock_message)
    mock_bot_class.return_value = mock_bot

    client = TelegramAPIClient('bot_token')
    result = await client.send_video('chat_id', 'video_data', duration=60, width=1920, height=1080)

    assert result == {'message_id': 125, 'video': {}}
    mock_bot.send_video.assert_called_once_with(
        chat_id='chat_id',
        video='video_data',
        caption=None,
        parse_mode='HTML',
        duration=60,
        width=1920,
        height=1080
    )


@pytest.mark.asyncio
@patch('agoras.platforms.telegram.client.Bot')
async def test_telegram_client_send_photo_with_parse_mode(mock_bot_class):
    """Test TelegramAPIClient send_photo with parse mode."""
    mock_bot = MagicMock()
    mock_message = MagicMock()
    mock_message.to_dict.return_value = {'message_id': 124, 'photo': []}
    mock_bot.send_photo = AsyncMock(return_value=mock_message)
    mock_bot_class.return_value = mock_bot

    client = TelegramAPIClient('bot_token')
    result = await client.send_photo('chat_id', 'photo_data', caption='Test **caption**', parse_mode='Markdown')

    assert result == {'message_id': 124, 'photo': []}
    mock_bot.send_photo.assert_called_once_with(
        chat_id='chat_id',
        photo='photo_data',
        caption='Test **caption**',
        parse_mode='Markdown'
    )


@pytest.mark.asyncio
@patch('agoras.platforms.telegram.client.Bot')
async def test_telegram_client_send_video_with_parse_mode(mock_bot_class):
    """Test TelegramAPIClient send_video with parse mode."""
    mock_bot = MagicMock()
    mock_message = MagicMock()
    mock_message.to_dict.return_value = {'message_id': 125, 'video': {}}
    mock_bot.send_video = AsyncMock(return_value=mock_message)
    mock_bot_class.return_value = mock_bot

    client = TelegramAPIClient('bot_token')
    result = await client.send_video('chat_id', 'video_data', caption='Test *caption*', parse_mode='Markdown')

    assert result == {'message_id': 125, 'video': {}}
    mock_bot.send_video.assert_called_once_with(
        chat_id='chat_id',
        video='video_data',
        caption='Test *caption*',
        parse_mode='Markdown',
        duration=None,
        width=None,
        height=None
    )


@pytest.mark.asyncio
@patch('agoras.platforms.telegram.client.Bot')
async def test_telegram_client_send_message_with_reply_markup(mock_bot_class):
    """Test TelegramAPIClient send_message with reply markup."""
    mock_bot = MagicMock()
    mock_message = MagicMock()
    mock_message.to_dict.return_value = {'message_id': 123, 'text': 'test'}
    mock_bot.send_message = AsyncMock(return_value=mock_message)
    mock_bot_class.return_value = mock_bot

    reply_markup = {'inline_keyboard': [[{'text': 'Button', 'callback_data': 'data'}]]}
    client = TelegramAPIClient('bot_token')
    result = await client.send_message('chat_id', 'Test message', reply_markup=reply_markup)

    assert result == {'message_id': 123, 'text': 'test'}
    mock_bot.send_message.assert_called_once_with(
        chat_id='chat_id',
        text='Test message',
        parse_mode='HTML',
        reply_markup=reply_markup
    )


@pytest.mark.asyncio
@patch('agoras.platforms.telegram.client.Bot')
async def test_telegram_client_delete_message_converts_to_int(mock_bot_class):
    """Test TelegramAPIClient delete_message converts string ID to int."""
    mock_bot = MagicMock()
    mock_bot.delete_message = AsyncMock(return_value=True)
    mock_bot_class.return_value = mock_bot

    client = TelegramAPIClient('bot_token')
    result = await client.delete_message('chat_id', 123)  # Int ID

    assert result is True
    mock_bot.delete_message.assert_called_once_with(chat_id='chat_id', message_id=123)


@pytest.mark.asyncio
@patch('agoras.platforms.telegram.client.Bot')
async def test_telegram_client_send_media_group_single_item(mock_bot_class):
    """Test TelegramAPIClient send_media_group with single item."""
    from telegram import InputMediaPhoto

    mock_bot = MagicMock()
    mock_message = MagicMock()
    mock_message.to_dict.return_value = {'message_id': 126}
    mock_bot.send_media_group = AsyncMock(return_value=[mock_message])
    mock_bot_class.return_value = mock_bot

    client = TelegramAPIClient('bot_token')
    media = [{'type': 'photo', 'media': 'photo1.jpg'}]
    result = await client.send_media_group('chat_id', media)

    assert len(result) == 1
    assert result[0]['message_id'] == 126
    mock_bot.send_media_group.assert_called_once()
    call_args = mock_bot.send_media_group.call_args
    assert call_args[1]['chat_id'] == 'chat_id'
    assert len(call_args[1]['media']) == 1


@pytest.mark.asyncio
@patch('agoras.platforms.telegram.client.Bot')
async def test_telegram_client_send_media_group_videos(mock_bot_class):
    """Test TelegramAPIClient send_media_group with videos."""
    from telegram import InputMediaVideo

    mock_bot = MagicMock()
    mock_message1 = MagicMock()
    mock_message1.to_dict.return_value = {'message_id': 126}
    mock_message2 = MagicMock()
    mock_message2.to_dict.return_value = {'message_id': 127}
    mock_bot.send_media_group = AsyncMock(return_value=[mock_message1, mock_message2])
    mock_bot_class.return_value = mock_bot

    client = TelegramAPIClient('bot_token')
    media = [
        {'type': 'video', 'media': 'video1.mp4', 'caption': 'First video'},
        {'type': 'video', 'media': 'video2.mp4'}
    ]
    result = await client.send_media_group('chat_id', media)

    assert len(result) == 2
    assert result[0]['message_id'] == 126
    assert result[1]['message_id'] == 127
    mock_bot.send_media_group.assert_called_once()
    call_args = mock_bot.send_media_group.call_args
    assert call_args[1]['chat_id'] == 'chat_id'
    assert len(call_args[1]['media']) == 2
    # Check that InputMediaVideo objects are created correctly
    assert isinstance(call_args[1]['media'][0], InputMediaVideo)
    assert call_args[1]['media'][0].caption == 'First video'
    assert call_args[1]['media'][1].caption is None