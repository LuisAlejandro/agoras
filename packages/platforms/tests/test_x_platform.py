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

import os
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from agoras.platforms.x import X
from agoras.platforms.x.api import XAPI
from agoras.platforms.x.auth import XAuthManager
from agoras.platforms.x.client import XAPIClient

# X (Twitter) Wrapper Tests


@pytest.mark.asyncio
@patch('agoras.platforms.x.wrapper.XAPI')
async def test_x_initialize_client(mock_api_class):
    """Test X _initialize_client extracts config and creates API."""
    mock_api = MagicMock()
    mock_api.authenticate = AsyncMock()
    mock_api_class.return_value = mock_api

    x = X(
        twitter_consumer_key='test_key',
        twitter_consumer_secret='test_secret',
        twitter_oauth_token='access_token',
        twitter_oauth_secret='access_secret'
    )

    await x._initialize_client()

    assert x.twitter_consumer_key == 'test_key'
    assert x.api is mock_api
    mock_api.authenticate.assert_called_once()


@pytest.mark.asyncio
@patch('agoras.platforms.x.auth.XAuthManager._load_credentials_from_storage', return_value=False)
async def test_x_initialize_client_missing_credentials(mock_load):
    """Test X _initialize_client raises exception without credentials."""
    x = X()

    with pytest.raises(Exception):
        await x._initialize_client()


@pytest.mark.asyncio
@patch('agoras.platforms.x.wrapper.XAPI')
async def test_x_post(mock_api_class):
    """Test X post method (create tweet)."""
    mock_api = MagicMock()
    mock_api.authenticate = AsyncMock()
    mock_api.post = AsyncMock(return_value='tweet-123')
    mock_api_class.return_value = mock_api

    x = X(
        twitter_consumer_key='key',
        twitter_consumer_secret='secret',
        twitter_oauth_token='token',
        twitter_oauth_secret='token_secret'
    )

    await x._initialize_client()

    with patch.object(x, '_output_status'):
        result = await x.post('Hello X', 'http://link.com')

    assert result == 'tweet-123'


@pytest.mark.asyncio
@patch('agoras.platforms.x.wrapper.XAPI')
async def test_x_like(mock_api_class):
    """Test X like method."""
    mock_api = MagicMock()
    mock_api.authenticate = AsyncMock()
    mock_api.like = AsyncMock(return_value='tweet-123')
    mock_api_class.return_value = mock_api

    x = X(
        twitter_consumer_key='key',
        twitter_consumer_secret='secret',
        twitter_oauth_token='token',
        twitter_oauth_secret='token_secret'
    )

    await x._initialize_client()

    with patch.object(x, '_output_status'):
        result = await x.like('tweet-123')

    assert result == 'tweet-123'


@pytest.mark.asyncio
@patch('agoras.platforms.x.wrapper.XAPI')
async def test_x_disconnect(mock_api_class):
    """Test X disconnect method."""
    mock_api = MagicMock()
    mock_api.authenticate = AsyncMock()
    mock_api.disconnect = AsyncMock()
    mock_api_class.return_value = mock_api

    x = X(
        twitter_consumer_key='key',
        twitter_consumer_secret='secret',
        twitter_oauth_token='token',
        twitter_oauth_secret='token_secret'
    )

    await x._initialize_client()
    await x.disconnect()

    mock_api.disconnect.assert_called_once()


# X API Tests

def test_x_api_class_exists():
    """Test XAPI class exists."""
    assert XAPI is not None


# X Auth Tests (Abstract - test via concrete usage)

def test_x_auth_class_exists():
    """Test XAuthManager class exists."""
    assert XAuthManager is not None


# X Client Tests

@pytest.mark.asyncio
@patch('agoras.platforms.x.wrapper.XAPI')
async def test_x_initialize_client_loads_from_storage(mock_api_class):
    """Test X _initialize_client loads from storage when auth manager returns True."""
    # Mock auth manager with credentials
    mock_auth_manager = MagicMock()
    mock_auth_manager._load_credentials_from_storage.return_value = True
    mock_auth_manager.consumer_key = 'stored_key'
    mock_auth_manager.consumer_secret = 'stored_secret'
    mock_auth_manager.oauth_token = 'stored_token'
    mock_auth_manager.oauth_secret = 'stored_secret'

    mock_api = MagicMock()
    mock_api.authenticate = AsyncMock()
    mock_api_class.return_value = mock_api

    with patch('agoras.platforms.x.auth.XAuthManager', return_value=mock_auth_manager):
        x = X()  # No initial credentials

        await x._initialize_client()

        assert x.twitter_consumer_key == 'stored_key'  # Should be loaded from storage
        assert x.twitter_consumer_secret == 'stored_secret'
        assert x.twitter_oauth_token == 'stored_token'
        assert x.twitter_oauth_secret == 'stored_secret'


@pytest.mark.asyncio
@patch('agoras.platforms.x.auth.XAuthManager._load_credentials_from_storage', return_value=False)
@patch('agoras.platforms.x.wrapper.XAPI')
async def test_x_initialize_client_missing_consumer_key(mock_api_class, mock_load_storage):
    """Test X _initialize_client raises when consumer_key missing after storage."""
    mock_api = MagicMock()
    mock_api.authenticate = AsyncMock()
    mock_api_class.return_value = mock_api

    x = X(
        twitter_consumer_secret='secret',
        twitter_oauth_token='token',
        twitter_oauth_secret='secret'
    )  # Missing consumer_key

    with pytest.raises(Exception, match="Not authenticated"):
        await x._initialize_client()


@pytest.mark.asyncio
@patch('agoras.platforms.x.auth.XAuthManager._load_credentials_from_storage', return_value=False)
@patch('agoras.platforms.x.wrapper.XAPI')
async def test_x_initialize_client_missing_consumer_secret(mock_api_class, mock_load_storage):
    """Test X _initialize_client raises when consumer_secret missing after storage."""
    mock_api = MagicMock()
    mock_api.authenticate = AsyncMock()
    mock_api_class.return_value = mock_api

    x = X(
        twitter_consumer_key='key',
        twitter_oauth_token='token',
        twitter_oauth_secret='secret'
    )  # Missing consumer_secret

    with pytest.raises(Exception, match="Not authenticated"):
        await x._initialize_client()


@pytest.mark.asyncio
@patch('agoras.platforms.x.auth.XAuthManager._load_credentials_from_storage', return_value=False)
@patch('agoras.platforms.x.wrapper.XAPI')
async def test_x_initialize_client_missing_oauth_token(mock_api_class, mock_load_storage):
    """Test X _initialize_client raises when oauth_token missing after storage."""
    mock_api = MagicMock()
    mock_api.authenticate = AsyncMock()
    mock_api_class.return_value = mock_api

    x = X(
        twitter_consumer_key='key',
        twitter_consumer_secret='secret',
        twitter_oauth_secret='secret'
    )  # Missing oauth_token

    with pytest.raises(Exception, match="Not authenticated"):
        await x._initialize_client()


@pytest.mark.asyncio
@patch('agoras.platforms.x.auth.XAuthManager._load_credentials_from_storage', return_value=False)
@patch('agoras.platforms.x.wrapper.XAPI')
async def test_x_initialize_client_missing_oauth_secret(mock_api_class, mock_load_storage):
    """Test X _initialize_client raises when oauth_secret missing after storage."""
    mock_api = MagicMock()
    mock_api.authenticate = AsyncMock()
    mock_api_class.return_value = mock_api

    x = X(
        twitter_consumer_key='key',
        twitter_consumer_secret='secret',
        twitter_oauth_token='token'
    )  # Missing oauth_secret

    with pytest.raises(Exception, match="Not authenticated"):
        await x._initialize_client()


@pytest.mark.asyncio
@patch('agoras.platforms.x.auth.XAuthManager')
async def test_x_authorize_credentials_success(mock_auth_manager_class):
    """Test X authorize_credentials success."""
    mock_auth_manager = MagicMock()
    mock_auth_manager.authorize = AsyncMock(return_value='success')
    mock_auth_manager_class.return_value = mock_auth_manager

    x = X()

    with patch('builtins.print'):  # Suppress print output
        result = await x.authorize_credentials()

    assert result is True
    mock_auth_manager.authorize.assert_called_once()


@pytest.mark.asyncio
@patch('agoras.platforms.x.auth.XAuthManager')
async def test_x_authorize_credentials_failure(mock_auth_manager_class):
    """Test X authorize_credentials failure."""
    mock_auth_manager = MagicMock()
    mock_auth_manager.authorize = AsyncMock(return_value=None)
    mock_auth_manager_class.return_value = mock_auth_manager

    x = X()

    result = await x.authorize_credentials()

    assert result is False


@pytest.mark.asyncio
@patch('agoras.platforms.x.wrapper.XAPI')
async def test_x_disconnect_with_api(mock_api_class):
    """Test X disconnect with API instance."""
    mock_api = MagicMock()
    mock_api.authenticate = AsyncMock()
    mock_api.disconnect = AsyncMock()
    mock_api_class.return_value = mock_api

    x = X(
        twitter_consumer_key='key',
        twitter_consumer_secret='secret',
        twitter_oauth_token='token',
        twitter_oauth_secret='secret'
    )

    await x._initialize_client()
    await x.disconnect()

    mock_api.disconnect.assert_called_once()


@pytest.mark.asyncio
async def test_x_disconnect_without_api():
    """Test X disconnect without API instance."""
    x = X()
    # Should not raise
    await x.disconnect()


@pytest.mark.asyncio
@patch('agoras.platforms.x.wrapper.XAPI')
async def test_x_post_no_content_raises(mock_api_class):
    """Test X post raises when no content provided."""
    mock_api = MagicMock()
    mock_api.authenticate = AsyncMock()
    mock_api_class.return_value = mock_api

    x = X(
        twitter_consumer_key='key',
        twitter_consumer_secret='secret',
        twitter_oauth_token='token',
        twitter_oauth_secret='secret'
    )

    await x._initialize_client()

    with pytest.raises(Exception, match="No status text, link, or images provided"):
        await x.post('', '', None, None, None, None)


@pytest.mark.asyncio
@patch('agoras.platforms.x.wrapper.XAPI')
async def test_x_post_with_image_urls(mock_api_class):
    """Test X post with image URLs."""
    mock_api = MagicMock()
    mock_api.authenticate = AsyncMock()
    mock_api.upload_media = AsyncMock(return_value='media123')
    mock_api.post = AsyncMock(return_value='tweet-456')
    mock_api_class.return_value = mock_api

    # Mock media download
    mock_media = MagicMock()
    mock_media.content = b'fake_image_data'
    mock_media.file_type.mime = 'image/jpeg'
    mock_media.cleanup = MagicMock()

    x = X(
        twitter_consumer_key='key',
        twitter_consumer_secret='secret',
        twitter_oauth_token='token',
        twitter_oauth_secret='secret'
    )

    await x._initialize_client()

    with patch.object(x, 'download_images', return_value=[mock_media]), \
         patch.object(x, '_output_status'):
        result = await x.post('Hello', 'http://link.com', 'http://image1.jpg')

    assert result == 'tweet-456'
    mock_api.upload_media.assert_called_once()
    mock_api.post.assert_called_once()
    mock_media.cleanup.assert_called_once()


@pytest.mark.asyncio
@patch('agoras.platforms.x.wrapper.XAPI')
async def test_x_post_with_local_image_path(mock_api_class):
    """X post uploads bytes from a local image path."""
    mock_api = MagicMock()
    mock_api.authenticate = AsyncMock()
    mock_api.upload_media = AsyncMock(return_value='media-local')
    mock_api.post = AsyncMock(return_value='tweet-local')
    mock_api_class.return_value = mock_api

    mock_media = MagicMock()
    mock_media.content = b'local_jpeg'
    mock_media.file_type.mime = 'image/jpeg'
    mock_media.cleanup = MagicMock()

    x = X(
        twitter_consumer_key='key',
        twitter_consumer_secret='secret',
        twitter_oauth_token='token',
        twitter_oauth_secret='secret'
    )

    await x._initialize_client()

    with patch.object(x, 'download_images', return_value=[mock_media]), \
         patch.object(x, '_output_status'):
        result = await x.post('Hello', '', '/tmp/local.jpg')

    assert result == 'tweet-local'
    mock_api.upload_media.assert_called_once_with(b'local_jpeg', 'image/jpeg')
    mock_api.post.assert_called_once()


@pytest.mark.asyncio
@patch('agoras.platforms.x.wrapper.XAPI')
async def test_x_post_media_upload_exception_continues(mock_api_class):
    """Test X post continues when media upload fails."""
    mock_api = MagicMock()
    mock_api.authenticate = AsyncMock()
    mock_api.upload_media = AsyncMock(side_effect=Exception('Upload failed'))
    mock_api.post = AsyncMock(return_value='tweet-456')
    mock_api_class.return_value = mock_api

    # Mock media download
    mock_media = MagicMock()
    mock_media.content = b'fake_image_data'
    mock_media.file_type.mime = 'image/jpeg'
    mock_media.cleanup = MagicMock()

    x = X(
        twitter_consumer_key='key',
        twitter_consumer_secret='secret',
        twitter_oauth_token='token',
        twitter_oauth_secret='secret'
    )

    await x._initialize_client()

    with patch.object(x, 'download_images', return_value=[mock_media]), \
         patch.object(x, '_output_status'):
        result = await x.post('Hello', 'http://link.com', 'http://image1.jpg')

    assert result == 'tweet-456'
    # Should still call post even though upload failed
    mock_api.post.assert_called_once()


@pytest.mark.asyncio
@patch('agoras.platforms.x.wrapper.XAPI')
async def test_x_reply_text_only(mock_api_class):
    """Test X reply with text only posts a reply tweet."""
    mock_api = MagicMock()
    mock_api.authenticate = AsyncMock()
    mock_api.reply = AsyncMock(return_value='reply-789')
    mock_api_class.return_value = mock_api

    x = X(
        twitter_consumer_key='key',
        twitter_consumer_secret='secret',
        twitter_oauth_token='token',
        twitter_oauth_secret='secret'
    )

    await x._initialize_client()

    with patch.object(x, '_output_status'):
        result = await x.reply('tweet-123', 'A reply')

    assert result == 'reply-789'
    mock_api.reply.assert_called_once_with('A reply', [], 'tweet-123')


@pytest.mark.asyncio
@patch('agoras.platforms.x.wrapper.XAPI')
async def test_x_reply_via_base_handler_uses_converter_key(mock_api_class):
    """End-to-end: CLI converter emits tweet_id, base _handle_reply_action must reach X.reply.

    Regression for the P1 where the base handler read config key ``post_id`` but the
    converter maps ``--post-id`` to ``tweet_id`` for X. The wrapper __init__ remaps
    ``tweet_id`` -> ``post_id`` so the shared handler can drive the reply.
    """
    mock_api = MagicMock()
    mock_api.authenticate = AsyncMock()
    mock_api.reply = AsyncMock(return_value='reply-789')
    mock_api_class.return_value = mock_api

    # Simulate the CLI converter output for `agoras x reply --post-id tweet-123 --text "A reply"`
    x = X(
        twitter_consumer_key='key',
        twitter_consumer_secret='secret',
        twitter_oauth_token='token',
        twitter_oauth_secret='secret',
        action='reply',
        tweet_id='tweet-123',
        status_text='A reply',
    )

    await x._initialize_client()

    with patch.object(x, '_output_status'):
        await x._handle_reply_action()

    mock_api.reply.assert_called_once_with('A reply', [], 'tweet-123')


@pytest.mark.asyncio
@patch('agoras.platforms.x.wrapper.XAPI')
async def test_x_reply_with_image(mock_api_class):
    """Test X reply with an image posts a reply tweet with media."""
    mock_api = MagicMock()
    mock_api.authenticate = AsyncMock()
    mock_api.upload_media = AsyncMock(return_value='media123')
    mock_api.reply = AsyncMock(return_value='reply-789')
    mock_api_class.return_value = mock_api

    mock_media = MagicMock()
    mock_media.content = b'fake_image_data'
    mock_media.file_type.mime = 'image/jpeg'
    mock_media.cleanup = MagicMock()

    x = X(
        twitter_consumer_key='key',
        twitter_consumer_secret='secret',
        twitter_oauth_token='token',
        twitter_oauth_secret='secret'
    )

    await x._initialize_client()

    with patch.object(x, 'download_images', return_value=[mock_media]), \
         patch.object(x, '_output_status'):
        result = await x.reply('tweet-123', 'A reply', 'http://image1.jpg')

    assert result == 'reply-789'
    mock_api.upload_media.assert_called_once()
    mock_api.reply.assert_called_once_with('A reply', ['media123'], 'tweet-123')


@pytest.mark.asyncio
@patch('agoras.platforms.x.wrapper.XAPI')
async def test_x_reply_media_only_fails_when_upload_fails(mock_api_class):
    """Test X reply with only media raises instead of publishing an empty reply when uploads fail."""
    mock_api = MagicMock()
    mock_api.authenticate = AsyncMock()
    mock_api.upload_media = AsyncMock(return_value=None)
    mock_api.reply = AsyncMock(return_value='reply-789')
    mock_api_class.return_value = mock_api

    mock_media = MagicMock()
    mock_media.content = b'fake_image_data'
    mock_media.file_type.mime = 'image/jpeg'
    mock_media.cleanup = MagicMock()

    x = X(
        twitter_consumer_key='key',
        twitter_consumer_secret='secret',
        twitter_oauth_token='token',
        twitter_oauth_secret='secret'
    )

    await x._initialize_client()

    with patch.object(x, 'download_images', return_value=[mock_media]):
        with pytest.raises(Exception, match="Failed to upload reply media"):
            await x.reply('tweet-123', None, 'http://image1.jpg')

    mock_api.reply.assert_not_called()


@pytest.mark.asyncio
@patch('agoras.platforms.x.wrapper.XAPI')
async def test_x_reply_no_post_id(mock_api_class):
    """Test X reply raises when no post_id provided."""
    mock_api = MagicMock()
    mock_api.authenticate = AsyncMock()
    mock_api_class.return_value = mock_api

    x = X(
        twitter_consumer_key='key',
        twitter_consumer_secret='secret',
        twitter_oauth_token='token',
        twitter_oauth_secret='secret'
    )

    await x._initialize_client()

    with pytest.raises(Exception, match="Tweet ID is required for reply action."):
        await x.reply(None, 'A reply')


@pytest.mark.asyncio
@patch('agoras.platforms.x.wrapper.XAPI')
async def test_x_reply_no_content(mock_api_class):
    """Test X reply raises when no text or media provided."""
    mock_api = MagicMock()
    mock_api.authenticate = AsyncMock()
    mock_api_class.return_value = mock_api

    x = X(
        twitter_consumer_key='key',
        twitter_consumer_secret='secret',
        twitter_oauth_token='token',
        twitter_oauth_secret='secret'
    )

    await x._initialize_client()

    with pytest.raises(Exception, match="No reply text or media provided."):
        await x.reply('tweet-123', None)


@pytest.mark.asyncio
@patch('agoras.platforms.x.wrapper.XAPI')
async def test_x_like_no_api(mock_api_class):
    """Test X like raises when no API initialized."""
    mock_api = MagicMock()
    mock_api.authenticate = AsyncMock()
    mock_api_class.return_value = mock_api

    x = X()  # No initialization

    with pytest.raises(Exception, match="X API not initialized"):
        await x.like('tweet123')


@pytest.mark.asyncio
@patch('agoras.platforms.x.wrapper.XAPI')
async def test_x_like_no_tweet_id(mock_api_class):
    """Test X like raises when no tweet ID provided."""
    mock_api = MagicMock()
    mock_api.authenticate = AsyncMock()
    mock_api_class.return_value = mock_api

    x = X(
        twitter_consumer_key='key',
        twitter_consumer_secret='secret',
        twitter_oauth_token='token',
        twitter_oauth_secret='secret'
    )

    await x._initialize_client()

    with pytest.raises(Exception, match="Tweet ID is required"):
        await x.like()


@pytest.mark.asyncio
@patch('agoras.platforms.x.wrapper.XAPI')
async def test_x_delete_no_api(mock_api_class):
    """Test X delete raises when no API initialized."""
    mock_api = MagicMock()
    mock_api.authenticate = AsyncMock()
    mock_api_class.return_value = mock_api

    x = X()  # No initialization

    with pytest.raises(Exception, match="X API not initialized"):
        await x.delete('tweet123')


@pytest.mark.asyncio
@patch('agoras.platforms.x.wrapper.XAPI')
async def test_x_delete_no_tweet_id(mock_api_class):
    """Test X delete raises when no tweet ID provided."""
    mock_api = MagicMock()
    mock_api.authenticate = AsyncMock()
    mock_api_class.return_value = mock_api

    x = X(
        twitter_consumer_key='key',
        twitter_consumer_secret='secret',
        twitter_oauth_token='token',
        twitter_oauth_secret='secret'
    )

    await x._initialize_client()

    with pytest.raises(Exception, match="Tweet ID is required"):
        await x.delete()


@pytest.mark.asyncio
@patch('agoras.platforms.x.wrapper.XAPI')
async def test_x_share_no_api(mock_api_class):
    """Test X share raises when no API initialized."""
    mock_api = MagicMock()
    mock_api.authenticate = AsyncMock()
    mock_api_class.return_value = mock_api

    x = X()  # No initialization

    with pytest.raises(Exception, match="X API not initialized"):
        await x.share('tweet123')


@pytest.mark.asyncio
@patch('agoras.platforms.x.wrapper.XAPI')
async def test_x_share_no_tweet_id(mock_api_class):
    """Test X share raises when no tweet ID provided."""
    mock_api = MagicMock()
    mock_api.authenticate = AsyncMock()
    mock_api_class.return_value = mock_api

    x = X(
        twitter_consumer_key='key',
        twitter_consumer_secret='secret',
        twitter_oauth_token='token',
        twitter_oauth_secret='secret'
    )

    await x._initialize_client()

    with pytest.raises(Exception, match="Tweet ID is required"):
        await x.share()


@pytest.mark.asyncio
@patch('agoras.platforms.x.wrapper.XAPI')
async def test_x_video_no_api(mock_api_class):
    """Test X video raises when no API initialized."""
    mock_api = MagicMock()
    mock_api.authenticate = AsyncMock()
    mock_api_class.return_value = mock_api

    x = X()  # No initialization

    with pytest.raises(Exception, match="X API not initialized"):
        await x.video('Test', 'video.mp4', 'Title')


@pytest.mark.asyncio
@patch('agoras.platforms.x.wrapper.XAPI')
async def test_x_video_no_video_url(mock_api_class):
    """Test X video raises when no video URL provided."""
    mock_api = MagicMock()
    mock_api.authenticate = AsyncMock()
    mock_api_class.return_value = mock_api

    x = X(
        twitter_consumer_key='key',
        twitter_consumer_secret='secret',
        twitter_oauth_token='token',
        twitter_oauth_secret='secret'
    )

    await x._initialize_client()

    with pytest.raises(Exception, match="Video URL is required"):
        await x.video('Test', '', 'Title')


@pytest.mark.asyncio
@patch('agoras.platforms.x.wrapper.XAPI')
async def test_x_video_success(mock_api_class):
    """Test X video success."""
    mock_api = MagicMock()
    mock_api.authenticate = AsyncMock()
    mock_api.upload_media = AsyncMock(return_value='media123')
    mock_api.post = AsyncMock(return_value='tweet-456')
    mock_api_class.return_value = mock_api

    # Mock video download
    mock_video = MagicMock()
    mock_video.content = b'fake_video_data'
    mock_video.file_type.mime = 'video/mp4'
    mock_video.get_duration = MagicMock(return_value=60)
    mock_video.cleanup = MagicMock()

    x = X(
        twitter_consumer_key='key',
        twitter_consumer_secret='secret',
        twitter_oauth_token='token',
        twitter_oauth_secret='secret'
    )

    await x._initialize_client()

    with patch.object(x, 'download_video', return_value=mock_video), \
         patch.object(x, '_output_status'):
        result = await x.video('Test content', 'video.mp4', 'Video Title')

    assert result == 'tweet-456'
    mock_api.upload_media.assert_called_once()
    mock_api.post.assert_called_once()
    mock_video.cleanup.assert_called_once()


@pytest.mark.asyncio
@patch('agoras.platforms.x.wrapper.XAPI')
async def test_x_video_invalid_mime(mock_api_class):
    """Test X video raises for invalid MIME type."""
    mock_api = MagicMock()
    mock_api.authenticate = AsyncMock()
    mock_api_class.return_value = mock_api

    # Mock video download with invalid MIME
    mock_video = MagicMock()
    mock_video.content = b'fake_video_data'
    mock_video.file_type.mime = 'video/avi'  # Invalid for X
    mock_video.cleanup = MagicMock()

    x = X(
        twitter_consumer_key='key',
        twitter_consumer_secret='secret',
        twitter_oauth_token='token',
        twitter_oauth_secret='secret'
    )

    await x._initialize_client()

    with patch.object(x, 'download_video', return_value=mock_video):
        from agoras.media.errors import MediaValidationError

        with pytest.raises(MediaValidationError, match='twitter'):
            await x.video('Test', 'video.avi', 'Title')

    mock_video.cleanup.assert_called_once()


@pytest.mark.asyncio
@patch('agoras.platforms.x.wrapper.XAPI')
async def test_x_video_rejects_over_280(mock_api_class):
    """Test X video rejects text over free-tier 280 weighted characters."""
    from agoras.core.text_limits import TextValidationError

    mock_api = MagicMock()
    mock_api.authenticate = AsyncMock()
    mock_api.user_info = None
    mock_api.upload_media = AsyncMock(return_value='media123')
    mock_api.post = AsyncMock(side_effect=TextValidationError('twitter', 'text', 400, 280, 'weighted_x'))
    mock_api_class.return_value = mock_api

    mock_video = MagicMock()
    mock_video.content = b'fake_video_data'
    mock_video.file_type.mime = 'video/mp4'
    mock_video.get_duration = MagicMock(return_value=60)
    mock_video.cleanup = MagicMock()

    x = X(
        twitter_consumer_key='key',
        twitter_consumer_secret='secret',
        twitter_oauth_token='token',
        twitter_oauth_secret='secret'
    )
    x._subscription_type = None  # fail closed to free

    await x._initialize_client()

    long_text = 'A' * 300
    long_title = 'B' * 50

    from agoras.core.text_limits import TextValidationError

    with patch.object(x, 'download_video', return_value=mock_video), \
         patch.object(x, '_output_status'), \
         patch.object(x, '_load_subscription_type', return_value=None):
        x._subscription_type = None
        with pytest.raises(TextValidationError):
            await x.video(long_text, 'video.mp4', long_title)

    mock_api.upload_media.assert_not_called()
    mock_api.post.assert_not_called()
    mock_video.cleanup.assert_not_called()


@pytest.mark.asyncio
@patch('agoras.platforms.x.wrapper.XAPI')
async def test_x_thread_reply_chain(mock_api_class):
    """Test X.thread publishes ordered reply chain and returns ThreadResult."""
    mock_api = MagicMock()
    mock_api.authenticate = AsyncMock()
    mock_api.user_info = None
    mock_api.post = AsyncMock(side_effect=['id1', 'id2', 'id3'])
    mock_api_class.return_value = mock_api

    x = X(
        twitter_consumer_key='key',
        twitter_consumer_secret='secret',
        twitter_oauth_token='token',
        twitter_oauth_secret='secret'
    )
    await x._initialize_client()

    entries = [
        {'text': 'one'},
        {'text': 'two'},
        {'text': 'three'},
    ]
    result = await x.thread(entries)

    assert result.complete is True
    assert result.ids == ['id1', 'id2', 'id3']
    assert mock_api.post.call_count == 3
    assert mock_api.post.call_args_list[0].kwargs.get('in_reply_to_tweet_id') is None
    assert mock_api.post.call_args_list[1].kwargs.get('in_reply_to_tweet_id') == 'id1'
    assert mock_api.post.call_args_list[2].kwargs.get('in_reply_to_tweet_id') == 'id2'


@pytest.mark.asyncio
@patch('agoras.platforms.x.wrapper.XAPI')
async def test_x_thread_partial_on_api_failure(mock_api_class):
    """Test X.thread stops on failure and raises ThreadPublishError."""
    from agoras.core.threading import ThreadPublishError

    mock_api = MagicMock()
    mock_api.authenticate = AsyncMock()
    mock_api.user_info = None
    mock_api.post = AsyncMock(side_effect=['id1', Exception('API rejected')])
    mock_api_class.return_value = mock_api

    x = X(
        twitter_consumer_key='key',
        twitter_consumer_secret='secret',
        twitter_oauth_token='token',
        twitter_oauth_secret='secret'
    )
    await x._initialize_client()

    with pytest.raises(ThreadPublishError) as exc_info:
        await x.thread([{'text': 'one'}, {'text': 'two'}, {'text': 'three'}])

    assert exc_info.value.result.complete is False
    assert exc_info.value.result.ids == ['id1']
    assert exc_info.value.result.failed_index == 1
    assert exc_info.value.result.outcome == 'failed'
    assert mock_api.post.call_count == 2


@pytest.mark.asyncio
@patch('agoras.platforms.x.wrapper.XAPI')
async def test_x_post_rejects_over_limit_before_api(mock_api_class):
    """Test X post rejects oversized text before create_tweet."""
    mock_api = MagicMock()
    mock_api.authenticate = AsyncMock()
    mock_api.post = AsyncMock(return_value='tweet-1')
    mock_api_class.return_value = mock_api

    x = X(
        twitter_consumer_key='key',
        twitter_consumer_secret='secret',
        twitter_oauth_token='token',
        twitter_oauth_secret='secret',
    )
    await x._initialize_client()
    x._subscription_type = None

    from agoras.core.text_limits import TextValidationError

    with patch.object(x, '_output_status'), patch.object(x, '_load_subscription_type', return_value=None):
        x._subscription_type = None
        with pytest.raises(TextValidationError):
            await x.post('A' * 281, '')

    mock_api.post.assert_not_called()


@pytest.mark.asyncio
@patch('agoras.platforms.x.wrapper.XAPI')
async def test_x_post_allows_premium_long_text(mock_api_class):
    """Premium stored tier allows long posts through validation."""
    mock_api = MagicMock()
    mock_api.authenticate = AsyncMock()
    mock_api.post = AsyncMock(return_value='tweet-1')
    mock_api_class.return_value = mock_api

    x = X(
        twitter_consumer_key='key',
        twitter_consumer_secret='secret',
        twitter_oauth_token='token',
        twitter_oauth_secret='secret',
    )
    await x._initialize_client()
    x._subscription_type = 'Premium'

    with patch.object(x, '_output_status'):
        result = await x.post('A' * 1000, '')

    assert result == 'tweet-1'
    mock_api.post.assert_called_once()
    assert len(mock_api.post.call_args[0][0]) == 1000


_X_CREDS = {
    'twitter_consumer_key': 'key',
    'twitter_consumer_secret': 'secret',
    'twitter_oauth_token': 'token',
    'twitter_oauth_secret': 'secret',
}


def _x_api_with_live_subscription(mock_api_class, subscription_type=None, *, error=None):
    """Build a mocked XAPI whose client.get_subscription_type is awaitable."""
    mock_api = MagicMock()
    mock_api.authenticate = AsyncMock()
    mock_api.post = AsyncMock(return_value='tweet-1')
    mock_client = MagicMock()
    if error is not None:
        mock_client.get_subscription_type = AsyncMock(side_effect=error)
    else:
        mock_client.get_subscription_type = AsyncMock(return_value=subscription_type)
    mock_api.client = mock_client
    mock_api_class.return_value = mock_api
    return mock_api


@pytest.mark.asyncio
@pytest.mark.parametrize('tier', ['Premium', 'Basic', 'PremiumPlus'])
@patch('agoras.platforms.x.wrapper.XAPI')
async def test_x_post_live_premium_family_allows_long_text(mock_api_class, tier):
    """Live get_me Premium-family tiers allow 1000-char posts and do not write storage."""
    mock_api = _x_api_with_live_subscription(mock_api_class, tier)
    x = X(**_X_CREDS)

    with patch.object(XAuthManager, '_save_credentials_to_storage') as mock_save:
        await x._initialize_client()
        with patch.object(x, '_output_status'):
            result = await x.post('A' * 1000, '')

    assert result == 'tweet-1'
    assert x._subscription_type == tier
    mock_api.client.get_subscription_type.assert_awaited_once()
    mock_save.assert_not_called()
    mock_api.post.assert_called_once()


@pytest.mark.asyncio
@patch('agoras.platforms.x.wrapper.XAPI')
async def test_x_post_live_lookup_error_fail_closed(mock_api_class):
    """get_me raise fail-closes to 280; auth already succeeded; short posts still work."""
    from agoras.core.text_limits import TextValidationError

    mock_api = _x_api_with_live_subscription(mock_api_class, error=Exception('403'))
    x = X(**_X_CREDS)
    await x._initialize_client()

    mock_api.authenticate.assert_awaited_once()
    assert x._subscription_type is None

    with pytest.raises(TextValidationError, match='280'):
        await x.post('A' * 281, '')
    mock_api.post.assert_not_called()

    with patch.object(x, '_output_status'):
        result = await x.post('A' * 100, '')
    assert result == 'tweet-1'


@pytest.mark.asyncio
@pytest.mark.parametrize('tier', [None, 'premium', 'Free'])
@patch('agoras.platforms.x.wrapper.XAPI')
async def test_x_post_live_non_premium_fail_closed_to_280(mock_api_class, tier):
    """None, lowercase premium, and Free fail-closed to 280."""
    from agoras.core.text_limits import TextValidationError

    mock_api = _x_api_with_live_subscription(mock_api_class, tier)
    x = X(**_X_CREDS)
    await x._initialize_client()

    with pytest.raises(TextValidationError, match='280'):
        await x.post('A' * 281, '')
    mock_api.post.assert_not_called()


@pytest.mark.asyncio
@patch('agoras.platforms.x.wrapper.XAPI')
async def test_x_post_live_premium_wins_over_empty_storage(mock_api_class):
    """Empty storage must not clobber a live Premium fetch back to 280."""
    mock_api = _x_api_with_live_subscription(mock_api_class, 'Premium')
    x = X(**_X_CREDS)

    def clobber_from_storage():
        x._subscription_type = None
        return None

    with patch.object(x, '_load_subscription_type', side_effect=clobber_from_storage) as mock_load:
        await x._initialize_client()
        with patch.object(x, '_output_status'):
            result = await x.post('A' * 1000, '')

    assert result == 'tweet-1'
    assert x._subscription_type == 'Premium'
    mock_load.assert_not_called()


@pytest.mark.asyncio
@patch('agoras.platforms.x.wrapper.XAPI')
async def test_x_thread_lookup_failed_rejects_over_280_before_create(mock_api_class):
    """Thread entry over 280 with failed lookup rejects before any create_tweet."""
    from agoras.core.text_limits import TextValidationError

    mock_api = _x_api_with_live_subscription(mock_api_class, error=Exception('429'))
    x = X(**_X_CREDS)
    await x._initialize_client()

    with pytest.raises(TextValidationError, match='280'):
        await x.thread([{'text': 'A' * 281}, {'text': 'ok'}])
    mock_api.post.assert_not_called()


@pytest.mark.asyncio
@patch('agoras.platforms.x.wrapper.XAPI')
async def test_x_initialize_fetches_subscription_on_existing_client(mock_api_class):
    """Post-time fetch uses the authenticated client, not a second _create_client."""
    mock_api = _x_api_with_live_subscription(mock_api_class, 'Premium')
    x = X(**_X_CREDS)

    with patch.object(XAuthManager, '_create_client') as mock_create:
        await x._initialize_client()

    mock_create.assert_not_called()
    mock_api.client.get_subscription_type.assert_awaited_once()
    assert x._subscription_type == 'Premium'


@pytest.mark.asyncio
async def test_x_handle_like_action_no_tweet_id():
    """Test X _handle_like_action raises when no tweet ID."""
    x = X()

    with patch.object(x, '_get_config_value', return_value=None):
        with pytest.raises(Exception, match="Tweet ID is required for like action"):
            await x._handle_like_action()


@pytest.mark.asyncio
async def test_x_handle_share_action_no_tweet_id():
    """Test X _handle_share_action raises when no tweet ID."""
    x = X()

    with patch.object(x, '_get_config_value', return_value=None):
        with pytest.raises(Exception, match="Tweet ID is required for share action"):
            await x._handle_share_action()


@pytest.mark.asyncio
async def test_x_handle_delete_action_no_tweet_id():
    """Test X _handle_delete_action raises when no tweet ID."""
    x = X()

    with patch.object(x, '_get_config_value', return_value=None):
        with pytest.raises(Exception, match="Tweet ID is required for delete action"):
            await x._handle_delete_action()


@pytest.mark.asyncio
async def test_x_handle_video_action_no_url():
    """Test X _handle_video_action raises when no video URL."""
    x = X()

    with patch.object(x, '_get_config_value') as mock_get_config:
        mock_get_config.side_effect = ['', None, 'title']  # status_text, video_url, video_title
        with pytest.raises(Exception, match="X video URL is required for video action"):
            await x._handle_video_action()


def test_x_auth_class_exists():
    """Test X auth class exists."""
    from agoras.platforms.x.auth import XAuthManager
    assert XAuthManager


@pytest.mark.asyncio
async def test_x_main_async_no_action():
    """Test main_async raises when no action provided."""
    from agoras.platforms.x.wrapper import main_async
    with pytest.raises(Exception, match="Action is a required argument"):
        await main_async({})


@pytest.mark.asyncio
@patch('agoras.platforms.x.wrapper.X')
async def test_x_main_async_authorize_action(mock_x_class):
    """Test main_async with authorize action."""
    from agoras.platforms.x.wrapper import main_async
    mock_instance = MagicMock()
    mock_instance.authorize_credentials = AsyncMock(return_value=True)
    mock_x_class.return_value = mock_instance

    result = await main_async({'action': 'authorize'})

    assert result == 0
    mock_instance.authorize_credentials.assert_called_once()


@pytest.mark.asyncio
@patch('agoras.platforms.x.wrapper.X')
async def test_x_main_async_other_action(mock_x_class):
    """Test main_async with other action."""
    from agoras.platforms.x.wrapper import main_async
    mock_instance = MagicMock()
    mock_instance.execute_action = AsyncMock()
    mock_instance.disconnect = AsyncMock()
    mock_x_class.return_value = mock_instance

    await main_async({'action': 'post'})

    mock_instance.execute_action.assert_called_once_with('post')
    mock_instance.disconnect.assert_called_once()


def test_x_client_instantiation():
    """Test X client can be instantiated."""
    from agoras.platforms.x.client import XAPIClient
    assert XAPIClient
