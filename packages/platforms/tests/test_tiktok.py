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

from agoras.platforms.tiktok import TikTok
from agoras.platforms.tiktok.api import TikTokAPI
from agoras.platforms.tiktok.auth import TikTokAuthManager
from agoras.platforms.tiktok.client import TikTokAPIClient

# TikTok Wrapper Tests


@pytest.mark.asyncio
@patch('agoras.platforms.tiktok.wrapper.TikTokAPI')
async def test_tiktok_initialize_client(mock_api_class):
    """Test TikTok _initialize_client extracts config and creates API."""
    mock_api = MagicMock()
    mock_api.authenticate = AsyncMock()
    mock_api_class.return_value = mock_api

    tiktok = TikTok(
        tiktok_client_key='test_key',
        tiktok_client_secret='test_secret',
        tiktok_access_token='test_token',
        tiktok_username='testuser',
        tiktok_refresh_token='refresh'
    )

    await tiktok._initialize_client()

    assert tiktok.tiktok_client_key == 'test_key'
    assert tiktok.api is mock_api
    mock_api.authenticate.assert_called_once()


@pytest.mark.asyncio
async def test_tiktok_initialize_client_missing_credentials():
    """Test TikTok _initialize_client raises exception without credentials."""
    tiktok = TikTok()

    with pytest.raises(Exception, match="Not authenticated"):
        await tiktok._initialize_client()


@pytest.mark.asyncio
@patch('agoras.platforms.tiktok.wrapper.TikTokAPI')
@patch('agoras.platforms.tiktok.auth.TikTokAuthManager')
async def test_tiktok_initialize_client_loads_from_storage(mock_auth_manager_class, mock_api_class):
    """Test TikTok _initialize_client loads credentials from storage when not provided."""
    # Mock auth manager that loads from storage
    mock_auth_manager = MagicMock()
    mock_auth_manager.username = 'stored_username'
    mock_auth_manager.client_key = 'stored_client_key'
    mock_auth_manager.client_secret = 'stored_client_secret'
    mock_auth_manager.refresh_token = 'stored_refresh_token'
    mock_auth_manager._load_credentials_from_storage = MagicMock(return_value=True)
    mock_auth_manager_class.return_value = mock_auth_manager

    # Mock API
    mock_api = MagicMock()
    mock_api.authenticate = AsyncMock()
    mock_api_class.return_value = mock_api

    # Create TikTok instance with NO credentials
    tiktok = TikTok()

    await tiktok._initialize_client()

    # Verify credentials were loaded from storage
    assert tiktok.tiktok_username == 'stored_username'
    assert tiktok.tiktok_client_key == 'stored_client_key'
    assert tiktok.tiktok_client_secret == 'stored_client_secret'
    assert tiktok.tiktok_refresh_token == 'stored_refresh_token'
    assert tiktok.api is mock_api
    mock_api.authenticate.assert_called_once()


@pytest.mark.asyncio
@patch('agoras.platforms.tiktok.auth.TikTokAuthManager')
async def test_tiktok_authorize_credentials(mock_auth_manager_class):
    """Test TikTok authorize_credentials method."""
    mock_auth_manager = MagicMock()
    mock_auth_manager.authorize = AsyncMock(return_value="Authorization successful. Credentials stored securely.")
    mock_auth_manager_class.return_value = mock_auth_manager

    tiktok = TikTok(
        tiktok_username='user123',
        tiktok_client_key='client123',
        tiktok_client_secret='secret123'
    )

    with patch('builtins.print'):
        result = await tiktok.authorize_credentials()

    assert result is True
    mock_auth_manager.authorize.assert_called_once()


@pytest.mark.asyncio
@patch('agoras.platforms.tiktok.auth.TikTokAuthManager')
async def test_tiktok_authorize_credentials_failure(mock_auth_manager_class):
    """Test TikTok authorize_credentials method when authorization fails."""
    mock_auth_manager = MagicMock()
    mock_auth_manager.authorize = AsyncMock(return_value=None)
    mock_auth_manager_class.return_value = mock_auth_manager

    tiktok = TikTok(
        tiktok_username='user123',
        tiktok_client_key='client123',
        tiktok_client_secret='secret123'
    )

    result = await tiktok.authorize_credentials()

    assert result is False
    mock_auth_manager.authorize.assert_called_once()


@pytest.mark.asyncio
@patch('agoras.platforms.tiktok.wrapper.TikTokAPI')
async def test_tiktok_post(mock_api_class):
    """Test TikTok post method."""
    mock_api = MagicMock()
    mock_api.authenticate = AsyncMock()
    mock_api.post = AsyncMock(return_value='video-123')
    mock_api_class.return_value = mock_api

    tiktok = TikTok(
        tiktok_client_key='key',
        tiktok_client_secret='secret',
        tiktok_access_token="token", tiktok_username="testuser", tiktok_refresh_token="refresh"
    )

    await tiktok._initialize_client()

    # Ensure allow_duet is False for photo posts
    tiktok.tiktok_allow_duet = False
    tiktok.tiktok_allow_stitch = False

    # Mock upload_photo since post with images calls it
    mock_api.upload_photo = AsyncMock(return_value={'publish_id': 'video-123'})

    # Mock download_images to avoid actual HTTP call
    with patch.object(tiktok, 'download_images', new_callable=AsyncMock) as mock_download:
        mock_image = MagicMock()
        mock_image.content = b'image_content'
        mock_file_type = MagicMock()
        mock_file_type.mime = 'image/jpeg'
        mock_image.file_type = mock_file_type
        mock_image.url = 'img.jpg'
        mock_image.cleanup = MagicMock()
        mock_download.return_value = [mock_image]

        with patch.object(tiktok, '_output_status'):
            result = await tiktok.post('Hello TikTok', 'http://link.com', status_image_url_1='img.jpg')

    assert result == 'video-123'


@pytest.mark.asyncio
@patch('agoras.platforms.tiktok.wrapper.TikTokAPI')
async def test_tiktok_disconnect(mock_api_class):
    """Test TikTok disconnect method."""
    mock_api = MagicMock()
    mock_api.authenticate = AsyncMock()
    mock_api.disconnect = AsyncMock()
    mock_api_class.return_value = mock_api

    tiktok = TikTok(
        tiktok_client_key='key',
        tiktok_client_secret='secret',
        tiktok_access_token='token',
        tiktok_username='testuser',
        tiktok_refresh_token='refresh'
    )

    await tiktok._initialize_client()
    await tiktok.disconnect()

    mock_api.disconnect.assert_called_once()


# TikTok API Tests

def test_tiktok_api_class_exists():
    """Test TikTokAPI class exists."""
    assert TikTokAPI is not None


# TikTok Auth Tests

def test_tiktok_auth_class_exists():
    """Test TikTokAuthManager class exists."""
    assert TikTokAuthManager is not None


# TikTok Client Tests

def test_tiktok_client_class_exists():
    """Test TikTokAPIClient class exists."""
    assert TikTokAPIClient is not None


# Additional Wrapper Tests

@pytest.mark.asyncio
@patch('agoras.platforms.tiktok.wrapper.TikTokAPI')
async def test_tiktok_video(mock_api_class):
    """Test TikTok video method."""
    mock_api = MagicMock()
    mock_api.authenticate = AsyncMock()
    mock_api.upload_video = AsyncMock(return_value={'publish_id': 'video-456'})
    mock_api.creator_info = None  # Skip duration check
    mock_api_class.return_value = mock_api

    tiktok = TikTok(
        tiktok_client_key='key',
        tiktok_client_secret='secret',
        tiktok_access_token='token',
        tiktok_username='testuser',
        tiktok_refresh_token='refresh'
    )

    await tiktok._initialize_client()

    # Mock download_video to avoid actual HTTP call
    with patch.object(tiktok, 'download_video', new_callable=AsyncMock) as mock_download:
        mock_video = MagicMock()
        mock_video.content = b'video_content'
        mock_file_type = MagicMock()
        mock_file_type.mime = 'video/mp4'
        mock_video.file_type = mock_file_type
        mock_video.url = 'http://video.mp4'
        mock_video.cleanup = MagicMock()
        mock_video.get_duration = MagicMock(return_value=None)  # Skip duration check
        mock_download.return_value = mock_video

        with patch.object(tiktok, '_output_status'):
            with patch('builtins.print'):
                result = await tiktok.video('Video description', 'http://video.mp4', 'Video Title')

    assert result == 'video-456'
    mock_api.upload_video.assert_called_once()


@pytest.mark.asyncio
@patch('agoras.platforms.tiktok.wrapper.TikTokAPI')
async def test_tiktok_video_with_privacy_settings(mock_api_class):
    """Test TikTok video with privacy settings."""
    mock_api = MagicMock()
    mock_api.authenticate = AsyncMock()
    mock_api.upload_video = AsyncMock(return_value={'publish_id': 'video-456'})
    mock_api.creator_info = None  # Skip duration check
    mock_api_class.return_value = mock_api

    tiktok = TikTok(
        tiktok_client_key='key',
        tiktok_client_secret='secret',
        tiktok_access_token='token',
        tiktok_username='testuser',
        tiktok_refresh_token='refresh',
        tiktok_privacy_status='PUBLIC_TO_EVERYONE',
        tiktok_allow_duet=True,
        tiktok_allow_stitch=True
    )

    await tiktok._initialize_client()

    with patch.object(tiktok, 'download_video', new_callable=AsyncMock) as mock_download:
        mock_video = MagicMock()
        mock_video.content = b'video_content'
        mock_file_type = MagicMock()
        mock_file_type.mime = 'video/mp4'
        mock_video.file_type = mock_file_type
        mock_video.url = 'http://video.mp4'
        mock_video.cleanup = MagicMock()
        mock_video.get_duration = MagicMock(return_value=None)
        mock_download.return_value = mock_video

        with patch.object(tiktok, '_output_status'):
            with patch('builtins.print'):
                result = await tiktok.video('Description', 'http://video.mp4', 'Title')

    assert result == 'video-456'
    # Verify upload_video was called with privacy settings
    call_args = mock_api.upload_video.call_args
    assert call_args[0][1] == 'Title'  # title parameter
    assert call_args[0][2] == 'PUBLIC_TO_EVERYONE'  # privacy_status
    assert call_args[0][4] is True  # allow_duet
    assert call_args[0][5] is True  # allow_stitch


@pytest.mark.asyncio
@patch('agoras.platforms.tiktok.wrapper.TikTokAPI')
async def test_tiktok_like_not_supported(mock_api_class):
    """Test TikTok like raises exception."""
    mock_api = MagicMock()
    mock_api.authenticate = AsyncMock()
    mock_api.like = AsyncMock(side_effect=Exception('Like not supported'))
    mock_api_class.return_value = mock_api

    tiktok = TikTok(
        tiktok_client_key='key',
        tiktok_client_secret='secret',
        tiktok_access_token='token',
        tiktok_username='testuser',
        tiktok_refresh_token='refresh'
    )

    await tiktok._initialize_client()

    with pytest.raises(Exception, match='not supported'):
        await tiktok.like('post-123')


@pytest.mark.asyncio
@patch('agoras.platforms.tiktok.wrapper.TikTokAPI')
async def test_tiktok_delete_not_supported(mock_api_class):
    """Test TikTok delete raises exception."""
    mock_api = MagicMock()
    mock_api.authenticate = AsyncMock()
    mock_api.delete = AsyncMock(side_effect=Exception('Delete not supported'))
    mock_api_class.return_value = mock_api

    tiktok = TikTok(
        tiktok_client_key='key',
        tiktok_client_secret='secret',
        tiktok_access_token='token',
        tiktok_username='testuser',
        tiktok_refresh_token='refresh'
    )

    await tiktok._initialize_client()

    with pytest.raises(Exception, match='not supported'):
        await tiktok.delete('post-123')


@pytest.mark.asyncio
@patch('agoras.platforms.tiktok.wrapper.TikTokAPI')
async def test_tiktok_share_not_supported(mock_api_class):
    """Test TikTok share raises exception."""
    mock_api = MagicMock()
    mock_api.authenticate = AsyncMock()
    mock_api.share = AsyncMock(side_effect=Exception('Share not supported'))
    mock_api_class.return_value = mock_api

    tiktok = TikTok(
        tiktok_client_key='key',
        tiktok_client_secret='secret',
        tiktok_access_token='token',
        tiktok_username='testuser',
        tiktok_refresh_token='refresh'
    )

    await tiktok._initialize_client()

    with pytest.raises(Exception, match='not supported'):
        await tiktok.share('post-123')


@pytest.mark.asyncio
@patch('agoras.platforms.tiktok.wrapper.TikTokAPI')
async def test_tiktok_post_with_duet_enabled_raises_error(mock_api_class):
    """Test TikTok post raises error when allow_duet is enabled for photos."""
    mock_api = MagicMock()
    mock_api.authenticate = AsyncMock()
    mock_api_class.return_value = mock_api

    tiktok = TikTok(
        tiktok_client_key='key',
        tiktok_client_secret='secret',
        tiktok_access_token='token',
        tiktok_username='testuser',
        tiktok_refresh_token='refresh',
        tiktok_allow_duet=True
    )

    await tiktok._initialize_client()

    with pytest.raises(Exception, match='allow-duet is not supported for photo posts'):
        await tiktok.post('Hello', 'http://link.com', status_image_url_1='img.jpg')


@pytest.mark.asyncio
@patch('agoras.platforms.tiktok.wrapper.TikTokAPI')
async def test_tiktok_post_with_stitch_enabled_raises_error(mock_api_class):
    """Test TikTok post raises error when allow_stitch is enabled for photos."""
    mock_api = MagicMock()
    mock_api.authenticate = AsyncMock()
    mock_api_class.return_value = mock_api

    tiktok = TikTok(
        tiktok_client_key='key',
        tiktok_client_secret='secret',
        tiktok_access_token='token',
        tiktok_username='testuser',
        tiktok_refresh_token='refresh',
        tiktok_allow_stitch=True
    )

    await tiktok._initialize_client()

    with pytest.raises(Exception, match='not supported for photo posts'):
        await tiktok.post('Hello', 'http://link.com', status_image_url_1='img.jpg')


def test_tiktok_convert_bool():
    """Test TikTok _convert_bool utility method."""
    tiktok = TikTok(tiktok_client_key='key', tiktok_client_secret='secret', tiktok_username='testuser')

    # Test various truthy values
    assert tiktok._convert_bool('true', False) is True
    assert tiktok._convert_bool('True', False) is True
    assert tiktok._convert_bool('1', False) is True
    assert tiktok._convert_bool(1, False) is True
    assert tiktok._convert_bool(True, False) is True

    # Test falsy values
    assert tiktok._convert_bool('false', True) is False
    assert tiktok._convert_bool('False', True) is False
    assert tiktok._convert_bool('0', True) is False
    assert tiktok._convert_bool(0, True) is False
    assert tiktok._convert_bool(False, True) is False

    # Test default
    assert tiktok._convert_bool(None, True) is True
    assert tiktok._convert_bool(None, False) is False


@pytest.mark.asyncio
@patch('agoras.platforms.tiktok.wrapper.TikTokAPI')
async def test_tiktok_handle_post_action(mock_api_class):
    """Test TikTok _handle_post_action method."""
    mock_api = MagicMock()
    mock_api.authenticate = AsyncMock()
    mock_api.upload_photo = AsyncMock(return_value={'publish_id': 'post-123'})
    mock_api_class.return_value = mock_api

    tiktok = TikTok(
        tiktok_client_key='key',
        tiktok_client_secret='secret',
        tiktok_access_token='token',
        tiktok_username='testuser',
        tiktok_refresh_token='refresh'
    )

    await tiktok._initialize_client()
    tiktok.tiktok_allow_duet = False
    tiktok.tiktok_allow_stitch = False

    # Set config values
    with patch.object(tiktok, '_get_config_value') as mock_get_config:
        mock_get_config.side_effect = lambda key, env_key, default=None: {
            'status_image_url_1': 'http://image.jpg',
            'status_image_url_2': None,
            'status_image_url_3': None,
            'status_image_url_4': None
        }.get(key, default)

        with patch.object(tiktok, 'post', new_callable=AsyncMock) as mock_post:
            mock_post.return_value = 'post-123'
            with patch.object(tiktok, '_output_status'):
                await tiktok._handle_post_action()

            # Action handler calls post but doesn't return value
            mock_post.assert_called_once()


@pytest.mark.asyncio
@patch('agoras.platforms.tiktok.wrapper.TikTokAPI')
async def test_tiktok_handle_video_action(mock_api_class):
    """Test TikTok _handle_video_action method."""
    mock_api = MagicMock()
    mock_api.authenticate = AsyncMock()
    mock_api.upload_video = AsyncMock(return_value={'publish_id': 'video-123'})
    mock_api.creator_info = None
    mock_api_class.return_value = mock_api

    tiktok = TikTok(
        tiktok_client_key='key',
        tiktok_client_secret='secret',
        tiktok_access_token='token',
        tiktok_username='testuser',
        tiktok_refresh_token='refresh',
        tiktok_title='Video Title'
    )

    await tiktok._initialize_client()

    with patch.object(tiktok, '_get_config_value', return_value='http://video.mp4'):
        with patch.object(tiktok, 'video', new_callable=AsyncMock) as mock_video:
            mock_video.return_value = 'video-123'
            with patch.object(tiktok, '_output_status'):
                with patch.object(tiktok, 'download_video', new_callable=AsyncMock) as mock_download:
                    mock_video_obj = MagicMock()
                    mock_video_obj.content = b'content'
                    mock_video_obj.file_type = MagicMock(mime='video/mp4')
                    mock_video_obj.get_duration = MagicMock(return_value=None)
                    mock_video_obj.cleanup = MagicMock()
                    mock_download.return_value = mock_video_obj
                    with patch('builtins.print'):
                        await tiktok._handle_video_action()

            # Action handler calls video but doesn't return value
            mock_video.assert_called_once()


@pytest.mark.asyncio
@patch('agoras.platforms.tiktok.wrapper.TikTokAPI')
async def test_tiktok_handle_like_action(mock_api_class):
    """Test TikTok _handle_like_action method."""
    mock_api = MagicMock()
    mock_api.authenticate = AsyncMock()
    mock_api.like = AsyncMock(side_effect=Exception('Like not supported'))
    mock_api_class.return_value = mock_api

    tiktok = TikTok(
        tiktok_client_key='key',
        tiktok_client_secret='secret',
        tiktok_access_token='token',
        tiktok_username='testuser',
        tiktok_refresh_token='refresh'
    )

    await tiktok._initialize_client()

    with patch.object(tiktok, '_get_config_value', return_value='post-123'):
        with pytest.raises(Exception, match='not supported'):
            await tiktok._handle_like_action()


@pytest.mark.asyncio
@patch('agoras.platforms.tiktok.wrapper.TikTokAPI')
async def test_tiktok_handle_share_action(mock_api_class):
    """Test TikTok _handle_share_action method."""
    mock_api = MagicMock()
    mock_api.authenticate = AsyncMock()
    mock_api.share = AsyncMock(side_effect=Exception('Share not supported'))
    mock_api_class.return_value = mock_api

    tiktok = TikTok(
        tiktok_client_key='key',
        tiktok_client_secret='secret',
        tiktok_access_token='token',
        tiktok_username='testuser',
        tiktok_refresh_token='refresh'
    )

    await tiktok._initialize_client()

    with patch.object(tiktok, '_get_config_value', return_value='post-123'):
        with pytest.raises(Exception, match='not supported'):
            await tiktok._handle_share_action()


@pytest.mark.asyncio
@patch('agoras.platforms.tiktok.wrapper.TikTokAPI')
async def test_tiktok_handle_delete_action(mock_api_class):
    """Test TikTok _handle_delete_action method."""
    mock_api = MagicMock()
    mock_api.authenticate = AsyncMock()
    mock_api.delete = AsyncMock(side_effect=Exception('Delete not supported'))
    mock_api_class.return_value = mock_api

    tiktok = TikTok(
        tiktok_client_key='key',
        tiktok_client_secret='secret',
        tiktok_access_token='token',
        tiktok_username='testuser',
        tiktok_refresh_token='refresh'
    )

    await tiktok._initialize_client()

    with patch.object(tiktok, '_get_config_value', return_value='post-123'):
        with pytest.raises(Exception, match='not supported'):
            await tiktok._handle_delete_action()


@pytest.mark.asyncio
@patch('agoras.platforms.tiktok.wrapper.TikTokAPI')
@patch('builtins.print')
async def test_tiktok_print_brand_content_notices(mock_print, mock_api_class):
    """Test TikTok _print_brand_content_notices method."""
    mock_api = MagicMock()
    mock_api.authenticate = AsyncMock()
    mock_api_class.return_value = mock_api

    tiktok = TikTok(
        tiktok_client_key='key',
        tiktok_client_secret='secret',
        tiktok_access_token='token',
        tiktok_username='testuser',
        tiktok_refresh_token='refresh'
    )

    await tiktok._initialize_client()
    tiktok.brand_organic = True
    tiktok.brand_content = True

    tiktok._print_brand_content_notices()

    # Should print notices when brand content flags are set
    assert mock_print.called
