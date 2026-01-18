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

from agoras.platforms.facebook import Facebook
from agoras.platforms.facebook.api import FacebookAPI

# Facebook Wrapper Tests


@pytest.mark.asyncio
@patch('agoras.platforms.facebook.wrapper.FacebookAPI')
async def test_facebook_initialize_client(mock_api_class):
    """Test Facebook _initialize_client extracts config and creates API."""
    mock_api = MagicMock()
    mock_api.authenticate = AsyncMock()
    mock_api_class.return_value = mock_api

    facebook = Facebook(
        facebook_access_token='test_token',
        facebook_object_id='page123'
    )

    await facebook._initialize_client()

    assert facebook.facebook_access_token == 'test_token'
    assert facebook.api is mock_api
    mock_api.authenticate.assert_called_once()


@pytest.mark.asyncio
async def test_facebook_initialize_client_missing_credentials():
    """Test Facebook _initialize_client raises exception without credentials."""
    facebook = Facebook()

    with pytest.raises(Exception, match="Not authenticated"):
        await facebook._initialize_client()


@pytest.mark.asyncio
@patch('agoras.platforms.facebook.wrapper.FacebookAPI')
@patch('agoras.platforms.facebook.auth.FacebookAuthManager')
async def test_facebook_initialize_client_loads_from_storage(mock_auth_manager_class, mock_api_class):
    """Test Facebook _initialize_client loads credentials from storage when not provided."""
    # Mock auth manager that loads from storage
    mock_auth_manager = MagicMock()
    mock_auth_manager.user_id = 'stored_user_id'
    mock_auth_manager.client_id = 'stored_client_id'
    mock_auth_manager.client_secret = 'stored_client_secret'
    mock_auth_manager.refresh_token = 'stored_refresh_token'
    mock_auth_manager.access_token = 'stored_access_token'
    mock_auth_manager._load_credentials_from_storage = MagicMock(return_value=True)
    mock_auth_manager.authenticate = AsyncMock(return_value=True)
    mock_auth_manager_class.return_value = mock_auth_manager

    # Mock API
    mock_api = MagicMock()
    mock_api.authenticate = AsyncMock()
    mock_api_class.return_value = mock_api

    # Create Facebook instance with NO credentials
    facebook = Facebook()

    await facebook._initialize_client()

    # Verify credentials were loaded from storage
    assert facebook.facebook_object_id == 'stored_user_id'
    assert facebook.facebook_client_id == 'stored_client_id'
    assert facebook.facebook_client_secret == 'stored_client_secret'
    assert facebook.facebook_refresh_token == 'stored_refresh_token'
    assert facebook.facebook_access_token == 'stored_access_token'
    assert facebook.api is mock_api
    mock_api.authenticate.assert_called_once()


@pytest.mark.asyncio
@patch('agoras.platforms.facebook.auth.FacebookAuthManager')
async def test_facebook_authorize_credentials(mock_auth_manager_class):
    """Test Facebook authorize_credentials method."""
    mock_auth_manager = MagicMock()
    mock_auth_manager.authorize = AsyncMock(return_value="Authorization successful. Credentials stored securely.")
    mock_auth_manager_class.return_value = mock_auth_manager

    facebook = Facebook(
        facebook_object_id='user123',
        facebook_client_id='client123',
        facebook_client_secret='secret123'
    )

    with patch('builtins.print'):
        result = await facebook.authorize_credentials()

    assert result is True
    mock_auth_manager.authorize.assert_called_once()


@pytest.mark.asyncio
@patch('agoras.platforms.facebook.auth.FacebookAuthManager')
async def test_facebook_authorize_credentials_failure(mock_auth_manager_class):
    """Test Facebook authorize_credentials method when authorization fails."""
    mock_auth_manager = MagicMock()
    mock_auth_manager.authorize = AsyncMock(return_value=None)
    mock_auth_manager_class.return_value = mock_auth_manager

    facebook = Facebook(
        facebook_object_id='user123',
        facebook_client_id='client123',
        facebook_client_secret='secret123'
    )

    result = await facebook.authorize_credentials()

    assert result is False
    mock_auth_manager.authorize.assert_called_once()


@pytest.mark.asyncio
@patch('agoras.platforms.facebook.wrapper.FacebookAPI')
async def test_facebook_post(mock_api_class):
    """Test Facebook post method."""
    mock_api = MagicMock()
    mock_api.authenticate = AsyncMock()
    mock_api.post = AsyncMock(return_value='post-123')
    mock_api_class.return_value = mock_api

    facebook = Facebook(
        facebook_access_token='token',
        facebook_object_id='page123'
    )

    await facebook._initialize_client()

    with patch.object(facebook, '_output_status'):
        result = await facebook.post('Hello Facebook', 'http://link.com')

    assert result == 'post-123'


@pytest.mark.asyncio
@patch('agoras.platforms.facebook.wrapper.FacebookAPI')
async def test_facebook_like(mock_api_class):
    """Test Facebook like method."""
    mock_api = MagicMock()
    mock_api.authenticate = AsyncMock()
    mock_api.like = AsyncMock(return_value='post-123')
    mock_api_class.return_value = mock_api

    facebook = Facebook(
        facebook_access_token='token',
        facebook_object_id='page123'
    )

    await facebook._initialize_client()

    with patch.object(facebook, '_output_status'):
        result = await facebook.like('post-123')

    assert result == 'post-123'


@pytest.mark.asyncio
@patch('agoras.platforms.facebook.wrapper.FacebookAPI')
async def test_facebook_share(mock_api_class):
    """Test Facebook share method."""
    mock_api = MagicMock()
    mock_api.authenticate = AsyncMock()
    mock_api.share = AsyncMock(return_value='share-456')
    mock_api_class.return_value = mock_api

    facebook = Facebook(
        facebook_access_token='token',
        facebook_object_id='page123',
        facebook_profile_id='profile123'
    )

    await facebook._initialize_client()

    with patch.object(facebook, '_output_status'):
        result = await facebook.share('post-123')

    assert result == 'share-456'


@pytest.mark.asyncio
@patch('agoras.platforms.facebook.wrapper.FacebookAPI')
async def test_facebook_delete(mock_api_class):
    """Test Facebook delete method."""
    mock_api = MagicMock()
    mock_api.authenticate = AsyncMock()
    mock_api.delete = AsyncMock(return_value='post-123')
    mock_api_class.return_value = mock_api

    facebook = Facebook(
        facebook_access_token='token',
        facebook_object_id='page123'
    )

    await facebook._initialize_client()

    with patch.object(facebook, '_output_status'):
        result = await facebook.delete('post-123')

    assert result == 'post-123'


@pytest.mark.asyncio
@patch('agoras.platforms.facebook.wrapper.FacebookAPI')
async def test_facebook_video(mock_api_class):
    """Test Facebook video posting."""
    mock_api = MagicMock()
    mock_api.authenticate = AsyncMock()
    mock_api.upload_video = AsyncMock(return_value='video-789')
    mock_api.upload_regular_video = AsyncMock(return_value='video-789')
    mock_api_class.return_value = mock_api

    facebook = Facebook(
        facebook_access_token='token',
        facebook_object_id='page123',
        facebook_app_id='app123'
    )

    await facebook._initialize_client()

    # Mock download_video to avoid actual HTTP call
    with patch.object(facebook, 'download_video', new_callable=AsyncMock) as mock_download:
        mock_video = MagicMock()
        mock_video.content = b'video_content'
        mock_file_type = MagicMock()
        mock_file_type.mime = 'video/mp4'
        mock_video.file_type = mock_file_type
        mock_video.cleanup = MagicMock()
        mock_download.return_value = mock_video

        with patch.object(facebook, '_output_status'):
            result = await facebook.video('Video description', 'http://video.mp4', 'Video Title')

    assert result == 'video-789'


@pytest.mark.asyncio
@patch('agoras.platforms.facebook.wrapper.FacebookAPI')
async def test_facebook_disconnect(mock_api_class):
    """Test Facebook disconnect method."""
    mock_api = MagicMock()
    mock_api.authenticate = AsyncMock()
    mock_api.disconnect = AsyncMock()
    mock_api_class.return_value = mock_api

    facebook = Facebook(
        facebook_access_token='token',
        facebook_object_id='page123'
    )

    await facebook._initialize_client()
    await facebook.disconnect()

    mock_api.disconnect.assert_called_once()


# Additional Wrapper Tests

@pytest.mark.asyncio
@patch('agoras.platforms.facebook.wrapper.FacebookAPI')
async def test_facebook_upload_reel(mock_api_class):
    """Test Facebook _upload_reel_or_story with reel type."""
    mock_api = MagicMock()
    mock_api.authenticate = AsyncMock()
    mock_api.upload_reel_or_story = AsyncMock(return_value='reel-123')
    mock_api_class.return_value = mock_api

    facebook = Facebook(
        facebook_access_token='token',
        facebook_object_id='page123',
        facebook_app_id='app123'
    )

    await facebook._initialize_client()

    with patch.object(facebook, '_output_status'):
        result = await facebook._upload_reel_or_story('reel', 'Reel description', 'http://video.mp4')

    assert result == 'reel-123'
    mock_api.upload_reel_or_story.assert_called_once()


@pytest.mark.asyncio
@patch('agoras.platforms.facebook.wrapper.FacebookAPI')
async def test_facebook_upload_story(mock_api_class):
    """Test Facebook _upload_reel_or_story with story type."""
    mock_api = MagicMock()
    mock_api.authenticate = AsyncMock()
    mock_api.upload_reel_or_story = AsyncMock(return_value='story-123')
    mock_api_class.return_value = mock_api

    facebook = Facebook(
        facebook_access_token='token',
        facebook_object_id='page123',
        facebook_app_id='app123'
    )

    await facebook._initialize_client()

    with patch.object(facebook, '_output_status'):
        result = await facebook._upload_reel_or_story('story', 'Story description', 'http://video.mp4')

    assert result == 'story-123'
    mock_api.upload_reel_or_story.assert_called_once()


@pytest.mark.asyncio
@patch('agoras.platforms.facebook.wrapper.FacebookAPI')
async def test_facebook_upload_regular_video(mock_api_class):
    """Test Facebook _upload_regular_video method."""
    mock_api = MagicMock()
    mock_api.authenticate = AsyncMock()
    mock_api.upload_regular_video = AsyncMock(return_value='video-123')
    mock_api_class.return_value = mock_api

    facebook = Facebook(
        facebook_access_token='token',
        facebook_object_id='page123',
        facebook_app_id='app123'
    )

    await facebook._initialize_client()

    mock_video = MagicMock()
    mock_video.content = b'video_content'
    mock_file_type = MagicMock()
    mock_file_type.mime = 'video/mp4'
    mock_video.file_type = mock_file_type
    mock_video.cleanup = MagicMock()

    with patch.object(facebook, '_output_status'):
        result = await facebook._upload_regular_video(mock_video, 'Video description', 'Video Title')

    assert result == 'video-123'
    mock_api.upload_regular_video.assert_called_once()


@pytest.mark.asyncio
@patch('agoras.platforms.facebook.wrapper.FacebookAPI')
async def test_facebook_handle_like_action(mock_api_class):
    """Test Facebook _handle_like_action method."""
    mock_api = MagicMock()
    mock_api.authenticate = AsyncMock()
    mock_api.like = AsyncMock(return_value='post-123')
    mock_api_class.return_value = mock_api

    facebook = Facebook(
        facebook_access_token='token',
        facebook_object_id='page123'
    )

    await facebook._initialize_client()

    with patch.object(facebook, '_get_config_value', return_value='post-123'):
        with patch.object(facebook, 'like', new_callable=AsyncMock) as mock_like:
            mock_like.return_value = 'post-123'
            with patch.object(facebook, '_output_status'):
                await facebook._handle_like_action()

            mock_like.assert_called_once_with('post-123')


@pytest.mark.asyncio
@patch('agoras.platforms.facebook.wrapper.FacebookAPI')
async def test_facebook_handle_share_action(mock_api_class):
    """Test Facebook _handle_share_action method."""
    mock_api = MagicMock()
    mock_api.authenticate = AsyncMock()
    mock_api.share = AsyncMock(return_value='share-123')
    mock_api_class.return_value = mock_api

    facebook = Facebook(
        facebook_access_token='token',
        facebook_object_id='page123',
        facebook_profile_id='profile123'
    )

    await facebook._initialize_client()

    with patch.object(facebook, '_get_config_value', return_value='post-123'):
        with patch.object(facebook, 'share', new_callable=AsyncMock) as mock_share:
            mock_share.return_value = 'share-123'
            with patch.object(facebook, '_output_status'):
                await facebook._handle_share_action()

            mock_share.assert_called_once_with('post-123')


@pytest.mark.asyncio
@patch('agoras.platforms.facebook.wrapper.FacebookAPI')
async def test_facebook_handle_delete_action(mock_api_class):
    """Test Facebook _handle_delete_action method."""
    mock_api = MagicMock()
    mock_api.authenticate = AsyncMock()
    mock_api.delete = AsyncMock(return_value='post-123')
    mock_api_class.return_value = mock_api

    facebook = Facebook(
        facebook_access_token='token',
        facebook_object_id='page123'
    )

    await facebook._initialize_client()

    with patch.object(facebook, '_get_config_value', return_value='post-123'):
        with patch.object(facebook, 'delete', new_callable=AsyncMock) as mock_delete:
            mock_delete.return_value = 'post-123'
            with patch.object(facebook, '_output_status'):
                await facebook._handle_delete_action()

            mock_delete.assert_called_once_with('post-123')


@pytest.mark.asyncio
@patch('agoras.platforms.facebook.wrapper.FacebookAPI')
async def test_facebook_handle_video_action(mock_api_class):
    """Test Facebook _handle_video_action method."""
    mock_api = MagicMock()
    mock_api.authenticate = AsyncMock()
    mock_api.upload_regular_video = AsyncMock(return_value='video-123')
    mock_api_class.return_value = mock_api

    facebook = Facebook(
        facebook_access_token='token',
        facebook_object_id='page123',
        facebook_app_id='app123'
    )

    await facebook._initialize_client()

    with patch.object(facebook, '_get_config_value') as mock_get_config:
        mock_get_config.side_effect = lambda key, env_key, default=None: {
            'facebook_video_url': 'http://video.mp4',
            'facebook_video_title': 'Video Title',
            'facebook_video_type': 'regular'
        }.get(key, default)

        with patch.object(facebook, 'video', new_callable=AsyncMock) as mock_video:
            mock_video.return_value = 'video-123'
            with patch.object(facebook, '_output_status'):
                with patch.object(facebook, 'download_video', new_callable=AsyncMock) as mock_download:
                    mock_video_obj = MagicMock()
                    mock_video_obj.content = b'content'
                    mock_video_obj.file_type = MagicMock(mime='video/mp4')
                    mock_video_obj.cleanup = MagicMock()
                    mock_download.return_value = mock_video_obj
                    await facebook._handle_video_action()

            mock_video.assert_called_once()


@pytest.mark.asyncio
@patch('agoras.platforms.facebook.wrapper.FacebookAPI')
async def test_facebook_video_type_validation(mock_api_class):
    """Test Facebook video validates video type."""
    mock_api = MagicMock()
    mock_api.authenticate = AsyncMock()
    mock_api_class.return_value = mock_api

    facebook = Facebook(
        facebook_access_token='token',
        facebook_object_id='page123',
        facebook_app_id='app123'
    )

    await facebook._initialize_client()

    with patch.object(facebook, 'download_video', new_callable=AsyncMock) as mock_download:
        mock_video = MagicMock()
        mock_video.content = b'video_content'
        mock_file_type = MagicMock()
        mock_file_type.mime = 'video/avi'  # Invalid format
        mock_video.file_type = mock_file_type
        mock_video.cleanup = MagicMock()
        mock_download.return_value = mock_video

        with pytest.raises(Exception, match='Invalid video type'):
            await facebook.video('Description', 'http://video.avi', 'Title')


@pytest.mark.asyncio
@patch('agoras.platforms.facebook.wrapper.FacebookAPI')
async def test_facebook_video_with_reel_type(mock_api_class):
    """Test Facebook video with reel type."""
    mock_api = MagicMock()
    mock_api.authenticate = AsyncMock()
    mock_api.upload_reel_or_story = AsyncMock(return_value='reel-123')
    mock_api_class.return_value = mock_api

    facebook = Facebook(
        facebook_access_token='token',
        facebook_object_id='page123',
        facebook_app_id='app123',
        facebook_video_type='reel'
    )

    await facebook._initialize_client()

    with patch.object(facebook, 'download_video', new_callable=AsyncMock) as mock_download:
        mock_video = MagicMock()
        mock_video.content = b'video_content'
        mock_file_type = MagicMock()
        mock_file_type.mime = 'video/mp4'
        mock_video.file_type = mock_file_type
        mock_video.cleanup = MagicMock()
        mock_download.return_value = mock_video

        with patch.object(facebook, '_output_status'):
            result = await facebook.video('Reel description', 'http://video.mp4', 'Reel Title')

    assert result == 'reel-123'
    mock_api.upload_reel_or_story.assert_called_once()


@pytest.mark.asyncio
@patch('agoras.platforms.facebook.wrapper.FacebookAPI')
async def test_facebook_video_with_story_type(mock_api_class):
    """Test Facebook video with story type."""
    mock_api = MagicMock()
    mock_api.authenticate = AsyncMock()
    mock_api.upload_reel_or_story = AsyncMock(return_value='story-123')
    mock_api_class.return_value = mock_api

    facebook = Facebook(
        facebook_access_token='token',
        facebook_object_id='page123',
        facebook_app_id='app123',
        facebook_video_type='story'
    )

    await facebook._initialize_client()

    with patch.object(facebook, 'download_video', new_callable=AsyncMock) as mock_download:
        mock_video = MagicMock()
        mock_video.content = b'video_content'
        mock_file_type = MagicMock()
        mock_file_type.mime = 'video/mp4'
        mock_video.file_type = mock_file_type
        mock_video.cleanup = MagicMock()
        mock_download.return_value = mock_video

        with patch.object(facebook, '_output_status'):
            result = await facebook.video('Story description', 'http://video.mp4', 'Story Title')

    assert result == 'story-123'
    mock_api.upload_reel_or_story.assert_called_once()


# Facebook API Tests

def test_facebook_api_class_exists():
    """Test FacebookAPI class exists."""
    assert FacebookAPI is not None
