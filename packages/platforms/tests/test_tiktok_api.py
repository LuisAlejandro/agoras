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

from agoras.platforms.tiktok.api import TikTokAPI


@pytest.fixture
def tiktok_api():
    """Fixture to create TikTokAPI instance with mocked auth."""
    with patch('agoras.platforms.tiktok.api.TikTokAuthManager') as mock_auth_class:
        mock_auth = MagicMock()
        mock_auth.authenticate = AsyncMock()
        mock_auth.access_token = 'token'
        mock_auth.user_info = {'username': 'testuser', 'display_name': 'Test User'}
        mock_auth.ensure_authenticated = MagicMock()  # Don't raise
        mock_auth.client = MagicMock()
        mock_auth_class.return_value = mock_auth

        api = TikTokAPI('testuser', 'client_key', 'client_secret', 'refresh_token')
        api._authenticated = True
        api.client = MagicMock()
        api.client.upload_video = MagicMock(return_value={'data': {'publish_id': 'video-123'}})
        api.client.get_publish_status = MagicMock(return_value={
            'data': {
                'status': 'PUBLISH_COMPLETE',
                'publicaly_available_post_id': ['post-123']
            }
        })
        yield api


# Authentication Tests

@pytest.mark.asyncio
@patch('agoras.platforms.tiktok.api.TikTokAuthManager')
async def test_tiktok_api_authenticate(mock_auth_class):
    """Test TikTokAPI authenticate method."""
    mock_auth = MagicMock()
    mock_auth.authenticate = AsyncMock(return_value=True)
    mock_auth.access_token = 'token123'
    mock_auth.client = MagicMock()
    mock_auth_class.return_value = mock_auth

    api = TikTokAPI('testuser', 'client_key', 'client_secret')
    result = await api.authenticate()

    assert api._authenticated is True
    assert result is api
    mock_auth.authenticate.assert_called_once()


@pytest.mark.asyncio
async def test_tiktok_api_disconnect(tiktok_api):
    """Test TikTokAPI disconnect method."""
    await tiktok_api.disconnect()

    assert tiktok_api._authenticated is False
    assert tiktok_api.client is None


# Upload Tests

@pytest.mark.asyncio
@patch('agoras.platforms.tiktok.api.asyncio.sleep')
async def test_tiktok_api_upload_video(mock_sleep, tiktok_api):
    """Test TikTokAPI upload_video."""
    result = await tiktok_api.upload_video(
        video_url='http://video.mp4',
        title='Test Video',
        privacy_status='PUBLIC_TO_EVERYONE'
    )

    assert result == {'publish_id': 'video-123'}
    tiktok_api.client.upload_video.assert_called_once()


@pytest.mark.asyncio
@patch('agoras.platforms.tiktok.api.asyncio.sleep')
async def test_tiktok_api_upload_with_privacy_settings(mock_sleep, tiktok_api):
    """Test TikTokAPI upload_video with privacy settings."""
    result = await tiktok_api.upload_video(
        video_url='http://video.mp4',
        title='Test Video',
        privacy_status='SELF_ONLY',
        allow_comments=False,
        allow_duet=False,
        allow_stitch=False
    )

    assert result == {'publish_id': 'video-123'}
    tiktok_api.client.upload_video.assert_called_once_with(
        video_url='http://video.mp4',
        title='Test Video',
        privacy_status='SELF_ONLY',
        allow_comments=False,
        allow_duet=False,
        allow_stitch=False,
        is_brand_organic=False,
        is_brand_content=False
    )


@pytest.mark.asyncio
@patch('agoras.platforms.tiktok.api.asyncio.sleep')
async def test_tiktok_api_upload_with_duet_stitch_options(mock_sleep, tiktok_api):
    """Test TikTokAPI upload_video with duet/stitch options."""
    result = await tiktok_api.upload_video(
        video_url='http://video.mp4',
        title='Test Video',
        privacy_status='PUBLIC_TO_EVERYONE',
        allow_duet=True,
        allow_stitch=True
    )

    assert result == {'publish_id': 'video-123'}
    tiktok_api.client.upload_video.assert_called_once()


# Post Tests

@pytest.mark.asyncio
async def test_tiktok_api_post_not_supported(tiktok_api):
    """Test TikTokAPI post method raises exception."""
    with pytest.raises(Exception, match='Regular posts not supported'):
        await tiktok_api.post('Test post')


@pytest.mark.asyncio
async def test_tiktok_api_post_with_video_url(tiktok_api):
    """Test TikTokAPI post method raises exception even with video URL."""
    with pytest.raises(Exception, match='Regular posts not supported'):
        await tiktok_api.post('Test post', video_url='http://video.mp4')


# User Info Tests

@pytest.mark.asyncio
async def test_tiktok_api_get_creator_info(tiktok_api):
    """Test TikTokAPI get_creator_info method."""
    result = await tiktok_api.get_creator_info()

    assert result == {'username': 'testuser', 'display_name': 'Test User'}


# Not Supported Tests

@pytest.mark.asyncio
async def test_tiktok_api_like_raises_exception(tiktok_api):
    """Test TikTokAPI like raises exception."""
    with pytest.raises(Exception, match='Like not supported'):
        await tiktok_api.like('post-123')


@pytest.mark.asyncio
async def test_tiktok_api_delete_raises_exception(tiktok_api):
    """Test TikTokAPI delete raises exception."""
    with pytest.raises(Exception, match='Delete not supported'):
        await tiktok_api.delete('post-123')


@pytest.mark.asyncio
async def test_tiktok_api_share_raises_exception(tiktok_api):
    """Test TikTokAPI share raises exception."""
    with pytest.raises(Exception, match='Share not supported'):
        await tiktok_api.share('post-123')


# Error Handling Tests

@pytest.mark.asyncio
@patch('agoras.platforms.tiktok.api.asyncio.sleep')
async def test_tiktok_api_upload_error(mock_sleep, tiktok_api):
    """Test TikTokAPI handles upload errors."""
    tiktok_api.client.upload_video = MagicMock(side_effect=Exception('Upload failed'))

    with pytest.raises(Exception, match='Upload failed'):
        await tiktok_api.upload_video(
            video_url='http://video.mp4',
            title='Test',
            privacy_status='PUBLIC_TO_EVERYONE'
        )


# Property Tests

def test_tiktok_api_properties():
    """Test TikTokAPI property accessors."""
    with patch('agoras.platforms.tiktok.api.TikTokAuthManager') as mock_auth_class:
        mock_auth = MagicMock()
        mock_auth.access_token = 'token123'
        mock_auth.user_info = {'username': 'testuser'}
        mock_auth_class.return_value = mock_auth

        api = TikTokAPI('testuser', 'client_key', 'client_secret')

        assert api.access_token == 'token123'
        assert api.creator_info == {'username': 'testuser'}
