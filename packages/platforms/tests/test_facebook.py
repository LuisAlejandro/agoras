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
    mock_api.check_if_page = AsyncMock(return_value=False)  # Mock to not detect as page
    mock_api_class.return_value = mock_api

    facebook = Facebook(
        facebook_access_token='test_token',
        facebook_object_id='page123'
    )

    await facebook._initialize_client()

    assert facebook.facebook_access_token == 'test_token'
    assert facebook.api is mock_api
    # authenticate is called twice: once for auth, once for page detection
    assert mock_api.authenticate.call_count == 2


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
    mock_api.check_if_page = AsyncMock(return_value=False)  # Mock to not detect as page
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
    # authenticate is called twice: once for auth, once for page detection
    assert mock_api.authenticate.call_count == 2


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


# Additional Facebook Wrapper Tests

@pytest.mark.asyncio
@patch('agoras.platforms.facebook.wrapper.FacebookAPI')
async def test_facebook_load_config_values(mock_api_class):
    """Test Facebook _load_config_values method."""
    mock_api = MagicMock()
    mock_api.authenticate = AsyncMock()
    mock_api.check_if_page = AsyncMock(return_value=False)
    mock_api_class.return_value = mock_api

    facebook = Facebook(
        facebook_access_token='test_token',
        facebook_client_id='client123',
        facebook_client_secret='secret123',
        facebook_refresh_token='refresh123',
        facebook_object_id='obj123',
        facebook_post_id='post123',
        facebook_profile_id='profile123',
        facebook_app_id='app123'
    )

    await facebook._load_config_values()

    assert facebook.facebook_access_token == 'test_token'
    assert facebook.facebook_client_id == 'client123'
    assert facebook.facebook_client_secret == 'secret123'
    assert facebook.facebook_refresh_token == 'refresh123'
    assert facebook.facebook_object_id == 'obj123'
    assert facebook.facebook_post_id == 'post123'
    assert facebook.facebook_profile_id == 'profile123'
    assert facebook.facebook_app_id == 'app123'


@pytest.mark.asyncio
@patch('agoras.platforms.facebook.wrapper.FacebookAPI')
async def test_facebook_load_credentials_from_storage_fills(mock_api_class):
    """Test Facebook _load_credentials_from_storage fills missing credentials."""
    mock_api = MagicMock()
    mock_api.authenticate = AsyncMock()
    mock_api.check_if_page = AsyncMock(return_value=False)
    mock_api_class.return_value = mock_api

    facebook = Facebook(
        facebook_access_token='test_token',
        # Missing some credentials, object_id is also missing
    )

    # Mock auth manager
    with patch('agoras.platforms.facebook.auth.FacebookAuthManager') as mock_auth_class:
        mock_auth_manager = MagicMock()
        mock_auth_manager.client_id = 'stored_client_id'
        mock_auth_manager.client_secret = 'stored_client_secret'
        mock_auth_manager.refresh_token = 'stored_refresh_token'
        mock_auth_manager.user_id = 'stored_user_id'
        mock_auth_manager._load_credentials_from_storage = MagicMock(return_value=True)
        mock_auth_class.return_value = mock_auth_manager

        await facebook._load_credentials_from_storage()

        # Should fill missing credentials including object_id
        assert facebook.facebook_client_id == 'stored_client_id'
        assert facebook.facebook_client_secret == 'stored_client_secret'
        assert facebook.facebook_refresh_token == 'stored_refresh_token'
        assert facebook.facebook_object_id == 'stored_user_id'


@pytest.mark.asyncio
@patch('agoras.platforms.facebook.wrapper.FacebookAPI')
async def test_facebook_fill_missing_credentials_from_storage(mock_api_class):
    """Test Facebook _fill_missing_credentials_from_storage method."""
    mock_api = MagicMock()
    mock_api.authenticate = AsyncMock()
    mock_api.check_if_page = AsyncMock(return_value=False)
    mock_api_class.return_value = mock_api

    facebook = Facebook()
    facebook.facebook_client_id = None
    facebook.facebook_client_secret = None
    facebook.facebook_refresh_token = None
    facebook.facebook_object_id = None

    # Mock auth manager with stored values
    mock_auth_manager = MagicMock()
    mock_auth_manager.client_id = 'stored_client_id'
    mock_auth_manager.client_secret = 'stored_client_secret'
    mock_auth_manager.refresh_token = 'stored_refresh_token'
    mock_auth_manager.user_id = 'stored_user_id'

    facebook._fill_missing_credentials_from_storage(mock_auth_manager)

    assert facebook.facebook_client_id == 'stored_client_id'
    assert facebook.facebook_client_secret == 'stored_client_secret'
    assert facebook.facebook_refresh_token == 'stored_refresh_token'
    assert facebook.facebook_object_id == 'stored_user_id'


@pytest.mark.asyncio
@patch('agoras.platforms.facebook.wrapper.FacebookAPI')
async def test_facebook_authenticate_with_credentials(mock_api_class):
    """Test Facebook _authenticate_with_credentials method."""
    mock_api = MagicMock()
    mock_api.authenticate = AsyncMock()
    mock_api.check_if_page = AsyncMock(return_value=False)
    mock_api_class.return_value = mock_api

    facebook = Facebook()
    facebook.facebook_client_id = 'client123'
    facebook.facebook_client_secret = 'secret123'
    facebook.facebook_refresh_token = 'refresh123'

    # Mock auth manager
    with patch('agoras.platforms.facebook.auth.FacebookAuthManager') as mock_auth_class:
        mock_auth_manager = MagicMock()
        mock_auth_manager.authenticate = AsyncMock(return_value=True)
        mock_auth_manager.access_token = 'new_access_token'
        mock_auth_class.return_value = mock_auth_manager

        await facebook._authenticate_with_credentials()

        assert facebook.facebook_access_token == 'new_access_token'


@pytest.mark.asyncio
@patch('agoras.platforms.facebook.wrapper.FacebookAPI')
async def test_facebook_handle_page_token_exchange_no_token(mock_api_class):
    """Test Facebook _handle_page_token_exchange with no access token."""
    facebook = Facebook()
    facebook.facebook_access_token = None

    await facebook._handle_page_token_exchange()

    assert facebook._is_page_target is False


@pytest.mark.asyncio
@patch('agoras.platforms.facebook.wrapper.FacebookAPI')
async def test_facebook_handle_page_token_exchange_user_target(mock_api_class):
    """Test Facebook _handle_page_token_exchange detects user target."""
    mock_api = MagicMock()
    mock_api.authenticate = AsyncMock()
    mock_api.check_if_page = AsyncMock(return_value=False)  # Not a page
    mock_api_class.return_value = mock_api

    facebook = Facebook()
    facebook.facebook_access_token = 'user_token'
    facebook.facebook_object_id = 'user123'

    await facebook._handle_page_token_exchange()

    assert facebook._is_page_target is False


@pytest.mark.asyncio
@patch('agoras.platforms.facebook.wrapper.FacebookAPI')
async def test_facebook_handle_page_token_exchange_page_target(mock_api_class):
    """Test Facebook _handle_page_token_exchange detects page target."""
    mock_api = MagicMock()
    mock_api.authenticate = AsyncMock()
    mock_api.check_if_page = AsyncMock(return_value=True)  # Is a page
    mock_api.get_page_token = AsyncMock(return_value='page_token')
    mock_api_class.return_value = mock_api

    facebook = Facebook()
    facebook.facebook_access_token = 'user_token'
    facebook.facebook_object_id = 'page123'

    await facebook._handle_page_token_exchange()

    assert facebook._is_page_target is True
    assert facebook.facebook_access_token == 'page_token'


@pytest.mark.asyncio
@patch('agoras.platforms.facebook.wrapper.FacebookAPI')
async def test_facebook_validate_credentials_missing_token(mock_api_class):
    """Test Facebook _validate_credentials with missing token."""
    facebook = Facebook()
    facebook.facebook_access_token = None

    with pytest.raises(Exception, match="Not authenticated"):
        facebook._validate_credentials()


@pytest.mark.asyncio
@patch('agoras.platforms.facebook.wrapper.FacebookAPI')
async def test_facebook_initialize_api_client_user(mock_api_class):
    """Test Facebook _initialize_api_client for user token."""
    mock_api = MagicMock()
    mock_api.authenticate = AsyncMock()
    mock_api_class.return_value = mock_api

    facebook = Facebook()
    facebook.facebook_access_token = 'user_token'
    facebook.facebook_client_id = 'client123'
    facebook.facebook_client_secret = 'secret123'
    facebook.facebook_refresh_token = 'refresh123'
    facebook.facebook_app_id = 'app123'
    facebook._is_page_target = False

    await facebook._initialize_api_client()

    assert facebook.api is mock_api


@pytest.mark.asyncio
@patch('agoras.platforms.facebook.wrapper.FacebookAPI')
async def test_facebook_initialize_api_client_page(mock_api_class):
    """Test Facebook _initialize_api_client for page token."""
    mock_api = MagicMock()
    mock_api.authenticate = AsyncMock()
    mock_api_class.return_value = mock_api

    facebook = Facebook()
    facebook.facebook_access_token = 'page_token'
    facebook.facebook_client_id = 'client123'
    facebook.facebook_client_secret = 'secret123'
    facebook.facebook_refresh_token = 'refresh123'
    facebook.facebook_app_id = 'app123'
    facebook.facebook_object_id = 'page123'
    facebook._is_page_target = True

    with patch('agoras.platforms.facebook.client.FacebookAPIClient') as mock_client_class:
        mock_client = MagicMock()
        mock_client.authenticate = AsyncMock()
        mock_client_class.return_value = mock_client

        await facebook._initialize_api_client()

        assert facebook.api.client is mock_client
        assert facebook.api.auth_manager.access_token == 'page_token'


@pytest.mark.asyncio
@patch('agoras.platforms.facebook.wrapper.FacebookAPI')
async def test_facebook_post_no_api(mock_api_class):
    """Test Facebook post with no API initialized."""
    facebook = Facebook()

    with pytest.raises(Exception, match='Facebook API not initialized'):
        await facebook.post('text', 'link')


@pytest.mark.asyncio
@patch('agoras.platforms.facebook.wrapper.FacebookAPI')
async def test_facebook_post_no_object_id(mock_api_class):
    """Test Facebook post with no object ID."""
    mock_api = MagicMock()
    mock_api.authenticate = AsyncMock()
    mock_api_class.return_value = mock_api

    facebook = Facebook()
    facebook.api = mock_api
    # object_id is None

    with pytest.raises(Exception, match='Facebook object ID is required'):
        await facebook.post('text', 'link')


@pytest.mark.asyncio
@patch('agoras.platforms.facebook.wrapper.FacebookAPI')
async def test_facebook_post_no_content(mock_api_class):
    """Test Facebook post with no content."""
    mock_api = MagicMock()
    mock_api.authenticate = AsyncMock()
    mock_api_class.return_value = mock_api

    facebook = Facebook()
    facebook.api = mock_api
    facebook.facebook_object_id = 'page123'

    with pytest.raises(Exception, match='No status text, link, or images provided'):
        await facebook.post('', '', None, None, None, None)


@pytest.mark.asyncio
@patch('agoras.platforms.facebook.wrapper.FacebookAPI')
async def test_facebook_post_page_target_with_media(mock_api_class):
    """Test Facebook post to page with media."""
    mock_api = MagicMock()
    mock_api.authenticate = AsyncMock()
    mock_api.check_if_page = AsyncMock(return_value=True)
    mock_api.get_page_token = AsyncMock(return_value='page_token')
    mock_api.post = AsyncMock(return_value='post-123')
    mock_api_class.return_value = mock_api

    facebook = Facebook()
    facebook.api = mock_api
    facebook.facebook_access_token = 'user_token'
    facebook.facebook_object_id = 'page123'
    facebook._is_page_target = True

    with patch.object(facebook, '_output_status'):
        result = await facebook.post('Page post', 'http://link.com', status_image_url_1='img.jpg')

    assert result == 'post-123'


@pytest.mark.asyncio
@patch('agoras.platforms.facebook.wrapper.FacebookAPI')
async def test_facebook_post_profile_upload_media(mock_api_class):
    """Test Facebook post to profile with media upload."""
    mock_api = MagicMock()
    mock_api.authenticate = AsyncMock()
    mock_api.check_if_page = AsyncMock(return_value=False)
    mock_api.upload_media = AsyncMock(return_value={'id': 'media-123'})
    mock_api.post = AsyncMock(return_value='post-123')
    mock_api_class.return_value = mock_api

    facebook = Facebook()
    facebook.api = mock_api
    facebook.facebook_access_token = 'user_token'
    facebook.facebook_object_id = 'user123'

    # Mock download_images
    with patch.object(facebook, 'download_images', new_callable=AsyncMock) as mock_download:
        mock_image = MagicMock()
        mock_image.url = 'img.jpg'
        mock_image.cleanup = MagicMock()
        mock_download.return_value = [mock_image]

        with patch.object(facebook, '_output_status'):
            result = await facebook.post('Profile post', 'http://link.com', status_image_url_1='img.jpg')

    assert result == 'post-123'


@pytest.mark.asyncio
@patch('agoras.platforms.facebook.wrapper.FacebookAPI')
async def test_facebook_like_no_api(mock_api_class):
    """Test Facebook like with no API initialized."""
    facebook = Facebook()

    with pytest.raises(Exception, match='Facebook API not initialized'):
        await facebook.like('post123')


@pytest.mark.asyncio
@patch('agoras.platforms.facebook.wrapper.FacebookAPI')
async def test_facebook_like_no_post_id(mock_api_class):
    """Test Facebook like with no post ID."""
    mock_api = MagicMock()
    mock_api.authenticate = AsyncMock()
    mock_api_class.return_value = mock_api

    facebook = Facebook()
    facebook.api = mock_api
    facebook.facebook_object_id = 'user123'
    # post_id is None

    with pytest.raises(Exception, match='Facebook post ID is required'):
        await facebook.like()


@pytest.mark.asyncio
@patch('agoras.platforms.facebook.wrapper.FacebookAPI')
async def test_facebook_like_no_object_id(mock_api_class):
    """Test Facebook like with no object ID."""
    mock_api = MagicMock()
    mock_api.authenticate = AsyncMock()
    mock_api_class.return_value = mock_api

    facebook = Facebook()
    facebook.api = mock_api
    facebook.facebook_access_token = 'token'
    facebook.facebook_post_id = 'post123'
    # object_id is None

    with pytest.raises(Exception, match='Facebook object ID is required'):
        await facebook.like('post123')


@pytest.mark.asyncio
@patch('agoras.platforms.facebook.wrapper.FacebookAPI')
async def test_facebook_delete_no_post_id(mock_api_class):
    """Test Facebook delete with no post ID."""
    mock_api = MagicMock()
    mock_api.authenticate = AsyncMock()
    mock_api_class.return_value = mock_api

    facebook = Facebook()
    facebook.api = mock_api
    facebook.facebook_access_token = 'token'
    facebook.facebook_object_id = 'user123'
    # post_id is None

    with pytest.raises(Exception, match='Facebook post ID is required'):
        await facebook.delete()


@pytest.mark.asyncio
@patch('agoras.platforms.facebook.wrapper.FacebookAPI')
async def test_facebook_delete_no_object_id(mock_api_class):
    """Test Facebook delete with no object ID."""
    mock_api = MagicMock()
    mock_api.authenticate = AsyncMock()
    mock_api_class.return_value = mock_api

    facebook = Facebook()
    facebook.api = mock_api
    facebook.facebook_access_token = 'token'
    facebook.facebook_post_id = 'post123'
    # object_id is None

    with pytest.raises(Exception, match='Facebook object ID is required'):
        await facebook.delete('post123')


@pytest.mark.asyncio
@patch('agoras.platforms.facebook.wrapper.FacebookAPI')
async def test_facebook_share_no_post_id(mock_api_class):
    """Test Facebook share with no post ID."""
    mock_api = MagicMock()
    mock_api.authenticate = AsyncMock()
    mock_api_class.return_value = mock_api

    facebook = Facebook()
    facebook.api = mock_api
    facebook.facebook_access_token = 'token'
    facebook.facebook_object_id = 'user123'
    facebook.facebook_profile_id = 'profile123'
    # post_id is None

    with pytest.raises(Exception, match='Facebook post ID is required'):
        await facebook.share()


@pytest.mark.asyncio
@patch('agoras.platforms.facebook.wrapper.FacebookAPI')
async def test_facebook_share_no_object_id(mock_api_class):
    """Test Facebook share with no object ID."""
    mock_api = MagicMock()
    mock_api.authenticate = AsyncMock()
    mock_api_class.return_value = mock_api

    facebook = Facebook()
    facebook.api = mock_api
    facebook.facebook_access_token = 'token'
    facebook.facebook_post_id = 'post123'
    facebook.facebook_profile_id = 'profile123'
    # object_id is None

    with pytest.raises(Exception, match='Facebook object ID is required'):
        await facebook.share('post123')


@pytest.mark.asyncio
@patch('agoras.platforms.facebook.wrapper.FacebookAPI')
async def test_facebook_share_no_profile_id(mock_api_class):
    """Test Facebook share with no profile ID."""
    mock_api = MagicMock()
    mock_api.authenticate = AsyncMock()
    mock_api_class.return_value = mock_api

    facebook = Facebook()
    facebook.api = mock_api
    facebook.facebook_access_token = 'token'
    facebook.facebook_object_id = 'user123'
    facebook.facebook_post_id = 'post123'
    # profile_id is None

    with pytest.raises(Exception, match='Facebook profile ID is required'):
        await facebook.share('post123')


@pytest.mark.asyncio
@patch('agoras.platforms.facebook.wrapper.FacebookAPI')
async def test_facebook_upload_reel_or_story_no_api(mock_api_class):
    """Test Facebook _upload_reel_or_story with no API."""
    facebook = Facebook()

    with pytest.raises(Exception, match='Facebook API client not initialized'):
        await facebook._upload_reel_or_story('reel', 'text', 'url')


@pytest.mark.asyncio
@patch('agoras.platforms.facebook.wrapper.FacebookAPI')
async def test_facebook_upload_reel_or_story_success(mock_api_class):
    """Test Facebook _upload_reel_or_story success."""
    mock_api = MagicMock()
    mock_api.authenticate = AsyncMock()
    mock_api.check_if_page = AsyncMock(return_value=False)
    mock_api.upload_reel_or_story = AsyncMock(return_value='reel-123')
    mock_api_class.return_value = mock_api

    facebook = Facebook()
    facebook.api = mock_api
    facebook.facebook_access_token = 'token'
    facebook.facebook_object_id = 'user123'

    result = await facebook._upload_reel_or_story('reel', 'Reel text', 'http://video.mp4')

    assert result == 'reel-123'


@pytest.mark.asyncio
@patch('agoras.platforms.facebook.wrapper.FacebookAPI')
async def test_facebook_upload_regular_video_no_app_id(mock_api_class):
    """Test Facebook _upload_regular_video with no app ID."""
    mock_api = MagicMock()
    mock_api.authenticate = AsyncMock()
    mock_api_class.return_value = mock_api

    facebook = Facebook()
    facebook.api = mock_api
    facebook.facebook_access_token = 'token'
    facebook.facebook_object_id = 'user123'
    facebook.facebook_app_id = None

    mock_video = MagicMock()
    mock_video.content = b'video'
    mock_video.file_type = MagicMock()
    mock_video.get_file_size = MagicMock(return_value=1024)
    mock_video.file_type.extension = 'mp4'

    with pytest.raises(Exception, match='Facebook app ID is required'):
        await facebook._upload_regular_video(mock_video, 'text', 'title')


@pytest.mark.asyncio
@patch('agoras.platforms.facebook.wrapper.FacebookAPI')
async def test_facebook_upload_regular_video_success(mock_api_class):
    """Test Facebook _upload_regular_video success."""
    mock_api = MagicMock()
    mock_api.authenticate = AsyncMock()
    mock_api.check_if_page = AsyncMock(return_value=False)
    mock_api.upload_regular_video = AsyncMock(return_value='video-123')
    mock_api_class.return_value = mock_api

    facebook = Facebook()
    facebook.api = mock_api
    facebook.facebook_access_token = 'token'
    facebook.facebook_object_id = 'user123'
    facebook.facebook_app_id = 'app123'

    mock_video = MagicMock()
    mock_video.content = b'video_content'
    mock_video.file_type = MagicMock()
    mock_video.get_file_size = MagicMock(return_value=1024)
    mock_video.file_type.extension = 'mp4'

    result = await facebook._upload_regular_video(mock_video, 'Video text', 'Video Title')

    assert result == 'video-123'


@pytest.mark.asyncio
@patch('agoras.platforms.facebook.wrapper.FacebookAPI')
async def test_facebook_video_no_api(mock_api_class):
    """Test Facebook video with no API initialized."""
    facebook = Facebook()

    with pytest.raises(Exception, match='Facebook API not initialized'):
        await facebook.video('text', 'url', 'title')


@pytest.mark.asyncio
@patch('agoras.platforms.facebook.wrapper.FacebookAPI')
async def test_facebook_video_no_title_or_description(mock_api_class):
    """Test Facebook video with missing title or description."""
    mock_api = MagicMock()
    mock_api.authenticate = AsyncMock()
    mock_api_class.return_value = mock_api

    facebook = Facebook()
    facebook.api = mock_api
    facebook.facebook_access_token = 'token'
    facebook.facebook_object_id = 'user123'

    with pytest.raises(Exception, match='Video title and description are required'):
        await facebook.video('', 'http://video.mp4', 'title')

    with pytest.raises(Exception, match='Video title and description are required'):
        await facebook.video('text', 'http://video.mp4', '')


@pytest.mark.asyncio
@patch('agoras.platforms.facebook.wrapper.FacebookAPI')
async def test_facebook_video_no_url(mock_api_class):
    """Test Facebook video with no URL."""
    mock_api = MagicMock()
    mock_api.authenticate = AsyncMock()
    mock_api_class.return_value = mock_api

    facebook = Facebook()
    facebook.api = mock_api
    facebook.facebook_access_token = 'token'
    facebook.facebook_object_id = 'user123'

    with pytest.raises(Exception, match='Video URL is required'):
        await facebook.video('text', '', 'title')


@pytest.mark.asyncio
@patch('agoras.platforms.facebook.wrapper.FacebookAPI')
async def test_facebook_video_no_object_id(mock_api_class):
    """Test Facebook video with no object ID."""
    mock_api = MagicMock()
    mock_api.authenticate = AsyncMock()
    mock_api_class.return_value = mock_api

    facebook = Facebook()
    facebook.api = mock_api
    facebook.facebook_access_token = 'token'
    # object_id is None

    with pytest.raises(Exception, match='Facebook object ID is required'):
        await facebook.video('text', 'http://video.mp4', 'title')


@pytest.mark.asyncio
@patch('agoras.platforms.facebook.wrapper.FacebookAPI')
async def test_facebook_handle_like_action_missing_post_id(mock_api_class):
    """Test Facebook _handle_like_action with missing post ID."""
    mock_api = MagicMock()
    mock_api.authenticate = AsyncMock()
    mock_api_class.return_value = mock_api

    facebook = Facebook()
    facebook.api = mock_api
    facebook.facebook_access_token = 'token'
    facebook.facebook_object_id = 'user123'

    with patch.object(facebook, '_get_config_value', return_value=''):
        with pytest.raises(Exception, match='Facebook post ID is required for like action'):
            await facebook._handle_like_action()


@pytest.mark.asyncio
@patch('agoras.platforms.facebook.wrapper.FacebookAPI')
async def test_facebook_handle_share_action_missing_post_id(mock_api_class):
    """Test Facebook _handle_share_action with missing post ID."""
    mock_api = MagicMock()
    mock_api.authenticate = AsyncMock()
    mock_api_class.return_value = mock_api

    facebook = Facebook()
    facebook.api = mock_api
    facebook.facebook_access_token = 'token'
    facebook.facebook_object_id = 'user123'
    facebook.facebook_profile_id = 'profile123'

    with patch.object(facebook, '_get_config_value', return_value=''):
        with pytest.raises(Exception, match='Facebook post ID is required for share action'):
            await facebook._handle_share_action()


@pytest.mark.asyncio
@patch('agoras.platforms.facebook.wrapper.FacebookAPI')
async def test_facebook_handle_delete_action_missing_post_id(mock_api_class):
    """Test Facebook _handle_delete_action with missing post ID."""
    mock_api = MagicMock()
    mock_api.authenticate = AsyncMock()
    mock_api_class.return_value = mock_api

    facebook = Facebook()
    facebook.api = mock_api
    facebook.facebook_access_token = 'token'
    facebook.facebook_object_id = 'user123'

    with patch.object(facebook, '_get_config_value', return_value=''):
        with pytest.raises(Exception, match='Facebook post ID is required for delete action'):
            await facebook._handle_delete_action()


@pytest.mark.asyncio
@patch('agoras.platforms.facebook.wrapper.FacebookAPI')
async def test_facebook_handle_video_action_missing_url(mock_api_class):
    """Test Facebook _handle_video_action with missing URL."""
    mock_api = MagicMock()
    mock_api.authenticate = AsyncMock()
    mock_api_class.return_value = mock_api

    facebook = Facebook()
    facebook.api = mock_api
    facebook.facebook_access_token = 'token'
    facebook.facebook_object_id = 'user123'

    with patch.object(facebook, '_get_config_value', side_effect=['desc', '', 'title']):
        with pytest.raises(Exception, match='Facebook video URL is required for video action'):
            await facebook._handle_video_action()


@pytest.mark.asyncio
async def test_facebook_main_async_empty_action():
    """Test Facebook main_async with empty action."""
    from agoras.platforms.facebook.wrapper import main_async

    with pytest.raises(Exception, match="Action is a required argument"):
        await main_async({})


@pytest.mark.asyncio
@patch('agoras.platforms.facebook.wrapper.Facebook')
async def test_facebook_main_async_authorize(mock_facebook_class):
    """Test Facebook main_async with authorize action."""
    from agoras.platforms.facebook.wrapper import main_async

    mock_facebook = MagicMock()
    mock_facebook.authorize_credentials = AsyncMock(return_value=True)
    mock_facebook_class.return_value = mock_facebook

    result = await main_async({'action': 'authorize'})

    assert result == 0
    mock_facebook.authorize_credentials.assert_called_once()


@pytest.mark.asyncio
@patch('agoras.platforms.facebook.wrapper.Facebook')
async def test_facebook_main_async_execute_action(mock_facebook_class):
    """Test Facebook main_async with other actions."""
    from agoras.platforms.facebook.wrapper import main_async

    mock_facebook = MagicMock()
    mock_facebook.execute_action = AsyncMock()
    mock_facebook.disconnect = AsyncMock()
    mock_facebook_class.return_value = mock_facebook

    result = await main_async({'action': 'video'})

    assert result is None
    mock_facebook.execute_action.assert_called_once_with('video')
    mock_facebook.disconnect.assert_called_once()


# Facebook API Tests

def test_facebook_api_class_exists():
    """Test FacebookAPI class exists."""
    assert FacebookAPI is not None
