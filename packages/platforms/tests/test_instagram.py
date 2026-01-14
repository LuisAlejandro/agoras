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

from agoras.platforms.instagram import Instagram
from agoras.platforms.instagram.api import InstagramAPI

# Instagram Wrapper Tests


@pytest.mark.asyncio
@patch('agoras.platforms.instagram.wrapper.InstagramAPI')
async def test_instagram_initialize_client(mock_api_class):
    """Test Instagram _initialize_client extracts config and creates API."""
    mock_api = MagicMock()
    mock_api.authenticate = AsyncMock()
    mock_api_class.return_value = mock_api

    instagram = Instagram(
        instagram_access_token='test_token',
        instagram_object_id='user123'
    )

    await instagram._initialize_client()

    assert instagram.instagram_access_token == 'test_token'
    assert instagram.api is mock_api
    mock_api.authenticate.assert_called_once()


@pytest.mark.asyncio
async def test_instagram_initialize_client_missing_credentials():
    """Test Instagram _initialize_client raises exception without credentials."""
    instagram = Instagram()

    with pytest.raises(Exception, match="Not authenticated"):
        await instagram._initialize_client()


@pytest.mark.asyncio
@patch('agoras.platforms.instagram.wrapper.InstagramAPI')
@patch('agoras.platforms.instagram.auth.InstagramAuthManager')
async def test_instagram_initialize_client_loads_from_storage(mock_auth_manager_class, mock_api_class):
    """Test Instagram _initialize_client loads credentials from storage when not provided."""
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

    # Create Instagram instance with NO credentials
    instagram = Instagram()

    await instagram._initialize_client()

    # Verify credentials were loaded from storage
    assert instagram.instagram_object_id == 'stored_user_id'
    assert instagram.instagram_client_id == 'stored_client_id'
    assert instagram.instagram_client_secret == 'stored_client_secret'
    assert instagram.instagram_refresh_token == 'stored_refresh_token'
    assert instagram.instagram_access_token == 'stored_access_token'
    assert instagram.api is mock_api
    mock_api.authenticate.assert_called_once()


@pytest.mark.asyncio
@patch('agoras.platforms.instagram.auth.InstagramAuthManager')
async def test_instagram_authorize_credentials(mock_auth_manager_class):
    """Test Instagram authorize_credentials method."""
    mock_auth_manager = MagicMock()
    mock_auth_manager.authorize = AsyncMock(return_value="Authorization successful. Credentials stored securely.")
    mock_auth_manager_class.return_value = mock_auth_manager

    instagram = Instagram(
        instagram_object_id='user123',
        instagram_client_id='client123',
        instagram_client_secret='secret123'
    )

    with patch('builtins.print'):
        result = await instagram.authorize_credentials()

    assert result is True
    mock_auth_manager.authorize.assert_called_once()


@pytest.mark.asyncio
@patch('agoras.platforms.instagram.auth.InstagramAuthManager')
async def test_instagram_authorize_credentials_failure(mock_auth_manager_class):
    """Test Instagram authorize_credentials method when authorization fails."""
    mock_auth_manager = MagicMock()
    mock_auth_manager.authorize = AsyncMock(return_value=None)
    mock_auth_manager_class.return_value = mock_auth_manager

    instagram = Instagram(
        instagram_object_id='user123',
        instagram_client_id='client123',
        instagram_client_secret='secret123'
    )

    result = await instagram.authorize_credentials()

    assert result is False
    mock_auth_manager.authorize.assert_called_once()


@pytest.mark.asyncio
@patch('agoras.platforms.instagram.wrapper.InstagramAPI')
async def test_instagram_post(mock_api_class):
    """Test Instagram post method."""
    mock_api = MagicMock()
    mock_api.authenticate = AsyncMock()
    mock_api.post = AsyncMock(return_value='media-123')
    mock_api_class.return_value = mock_api

    instagram = Instagram(
        instagram_access_token='token',
        instagram_object_id='user123'
    )

    await instagram._initialize_client()

    # Mock download_images to avoid actual HTTP call
    with patch.object(instagram, 'download_images', new_callable=AsyncMock) as mock_download:
        mock_image = MagicMock()
        mock_image.url = 'img.jpg'
        mock_image.cleanup = MagicMock()
        mock_download.return_value = [mock_image]

        # Mock create_media to be async
        mock_api.create_media = AsyncMock(return_value='container-123')
        mock_api.create_carousel = AsyncMock(return_value='media-123')
        mock_api.publish_media = AsyncMock(return_value='media-123')

        with patch.object(instagram, '_output_status'):
            result = await instagram.post('Hello Instagram', 'http://link.com',
                                          status_image_url_1='img.jpg')

    assert result == 'media-123'


@pytest.mark.asyncio
@patch('agoras.platforms.instagram.wrapper.InstagramAPI')
async def test_instagram_like_not_supported(mock_api_class):
    """Test Instagram like is not supported."""
    mock_api = MagicMock()
    mock_api.authenticate = AsyncMock()
    mock_api.like = AsyncMock(side_effect=Exception('Like not supported'))
    mock_api_class.return_value = mock_api

    instagram = Instagram(
        instagram_access_token='token',
        instagram_object_id='user123'
    )

    await instagram._initialize_client()

    with pytest.raises(Exception, match='not supported'):
        await instagram.like('media-123')


@pytest.mark.asyncio
@patch('agoras.platforms.instagram.wrapper.InstagramAPI')
async def test_instagram_share_not_supported(mock_api_class):
    """Test Instagram share is not supported."""
    mock_api = MagicMock()
    mock_api.authenticate = AsyncMock()
    mock_api.share = AsyncMock(side_effect=Exception('Share not supported'))
    mock_api_class.return_value = mock_api

    instagram = Instagram(
        instagram_access_token='token',
        instagram_object_id='user123'
    )

    await instagram._initialize_client()

    with pytest.raises(Exception, match='not supported'):
        await instagram.share('media-123')


@pytest.mark.asyncio
@patch('agoras.platforms.instagram.wrapper.InstagramAPI')
async def test_instagram_delete_not_supported(mock_api_class):
    """Test Instagram delete is not supported."""
    mock_api = MagicMock()
    mock_api.authenticate = AsyncMock()
    mock_api.delete = AsyncMock(side_effect=Exception('Delete not supported'))
    mock_api_class.return_value = mock_api

    instagram = Instagram(
        instagram_access_token='token',
        instagram_object_id='user123'
    )

    await instagram._initialize_client()

    with pytest.raises(Exception, match='not supported'):
        await instagram.delete('media-123')


@pytest.mark.asyncio
@patch('agoras.platforms.instagram.wrapper.InstagramAPI')
async def test_instagram_disconnect(mock_api_class):
    """Test Instagram disconnect method."""
    mock_api = MagicMock()
    mock_api.authenticate = AsyncMock()
    mock_api.disconnect = AsyncMock()
    mock_api_class.return_value = mock_api

    instagram = Instagram(
        instagram_access_token='token',
        instagram_object_id='user123'
    )

    await instagram._initialize_client()
    await instagram.disconnect()

    mock_api.disconnect.assert_called_once()


# Instagram API Tests

def test_instagram_api_class_exists():
    """Test InstagramAPI class exists."""
    assert InstagramAPI is not None
