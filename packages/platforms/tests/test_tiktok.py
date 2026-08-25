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
import sys
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from agoras.platforms.tiktok import TikTok
from agoras.platforms.tiktok.api import TikTokAPI
from agoras.platforms.tiktok.auth import TikTokAuthManager
from agoras.platforms.tiktok.client import TikTokAPIClient
from agoras.platforms.tiktok.composer import ComposerPayload
from agoras.platforms.tiktok.wrapper import UNATTENDED_COMMERCIAL_ERROR, UNATTENDED_PRIVACY_ERROR

from .wrapper_test_helpers import SAMPLE_IMAGE_URL


def _ok_creator_info(**overrides):
    """Return a live creator_info payload tests can reuse."""
    info = {
        "creator_username": "testuser",
        "creator_nickname": "Test User",
        "privacy_level_options": [
            "PUBLIC_TO_EVERYONE",
            "MUTUAL_FOLLOW_FRIENDS",
            "FOLLOWER_OF_CREATOR",
            "SELF_ONLY",
        ],
        "comment_disabled": False,
        "duet_disabled": False,
        "stitch_disabled": False,
        "max_video_post_duration_sec": 180,
    }
    info.update(overrides)
    return info


def _wire_creator_info(mock_api, info=None):
    """Attach a fresh creator_info query to a mocked TikTokAPI."""
    payload = info or _ok_creator_info()
    mock_api.refresh_creator_info = AsyncMock(return_value=payload)
    mock_api.get_creator_info = AsyncMock(return_value=payload)
    mock_api.creator_info = payload
    return payload


def _composer_payload(**overrides):
    """Return a confirmed composer payload."""
    data = dict(
        title="Composed title",
        privacy_level="SELF_ONLY",
        allow_comments=False,
        allow_duet=False,
        allow_stitch=False,
        brand_organic=False,
        brand_content=False,
    )
    data.update(overrides)
    return ComposerPayload(**data)


# TikTok Wrapper Tests


@pytest.mark.asyncio
@patch("agoras.platforms.tiktok.wrapper.TikTokAPI")
async def test_tiktok_initialize_client(mock_api_class):
    """Test TikTok _initialize_client extracts config and creates API."""
    mock_api = MagicMock()
    mock_api.authenticate = AsyncMock()
    mock_api_class.return_value = mock_api

    tiktok = TikTok(
        tiktok_client_key="test_key",
        tiktok_client_secret="test_secret",
        tiktok_access_token="test_token",
        tiktok_username="testuser",
        tiktok_refresh_token="refresh",
    )

    await tiktok._initialize_client()

    assert tiktok.tiktok_client_key == "test_key"
    assert tiktok.api is mock_api
    mock_api.authenticate.assert_called_once()


@pytest.mark.asyncio
@patch("agoras.platforms.tiktok.auth.TikTokAuthManager._load_credentials_from_storage", return_value=False)
async def test_tiktok_initialize_client_missing_credentials(mock_load_credentials):
    """Test TikTok _initialize_client raises exception without credentials."""
    tiktok = TikTok()

    with pytest.raises(Exception, match="Not authenticated"):
        await tiktok._initialize_client()


@pytest.mark.asyncio
@patch("agoras.platforms.tiktok.wrapper.TikTokAPI")
@patch("agoras.platforms.tiktok.auth.TikTokAuthManager")
async def test_tiktok_initialize_client_loads_from_storage(mock_auth_manager_class, mock_api_class):
    """Test TikTok _initialize_client loads credentials from storage when not provided."""
    # Mock auth manager that loads from storage
    mock_auth_manager = MagicMock()
    mock_auth_manager.username = "stored_username"
    mock_auth_manager.client_key = "stored_client_key"
    mock_auth_manager.client_secret = "stored_client_secret"
    mock_auth_manager.refresh_token = "stored_refresh_token"
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
    assert tiktok.tiktok_username == "stored_username"
    assert tiktok.tiktok_client_key == "stored_client_key"
    assert tiktok.tiktok_client_secret == "stored_client_secret"
    assert tiktok.tiktok_refresh_token == "stored_refresh_token"
    assert tiktok.api is mock_api
    mock_api.authenticate.assert_called_once()


@pytest.mark.asyncio
@patch("agoras.platforms.tiktok.auth.TikTokAuthManager")
async def test_tiktok_authorize_credentials(mock_auth_manager_class):
    """Test TikTok authorize_credentials method."""
    mock_auth_manager = MagicMock()
    mock_auth_manager.authorize = AsyncMock(return_value="Authorization successful. Credentials stored securely.")
    mock_auth_manager_class.return_value = mock_auth_manager

    tiktok = TikTok(tiktok_username="user123", tiktok_client_key="client123", tiktok_client_secret="secret123")

    with patch("builtins.print"):
        result = await tiktok.authorize_credentials()

    assert result is True
    mock_auth_manager.authorize.assert_called_once()


@pytest.mark.asyncio
@patch("agoras.platforms.tiktok.auth.TikTokAuthManager")
async def test_tiktok_authorize_credentials_failure(mock_auth_manager_class):
    """Test TikTok authorize_credentials method when authorization fails."""
    mock_auth_manager = MagicMock()
    mock_auth_manager.authorize = AsyncMock(return_value=None)
    mock_auth_manager_class.return_value = mock_auth_manager

    tiktok = TikTok(tiktok_username="user123", tiktok_client_key="client123", tiktok_client_secret="secret123")

    result = await tiktok.authorize_credentials()

    assert result is False
    mock_auth_manager.authorize.assert_called_once()


@pytest.mark.asyncio
@patch("agoras.media.preflight.preflight_url_for_platform")
@patch("agoras.platforms.tiktok.wrapper.TikTokAPI")
async def test_tiktok_post(mock_api_class, mock_preflight):
    """Test TikTok post method."""
    mock_api = MagicMock()
    mock_api.authenticate = AsyncMock()
    mock_api.post = AsyncMock(return_value="video-123")
    mock_api_class.return_value = mock_api

    tiktok = TikTok(
        tiktok_client_key="key",
        tiktok_client_secret="secret",
        tiktok_access_token="token",
        tiktok_username="testuser",
        tiktok_refresh_token="refresh",
    )

    await tiktok._initialize_client()
    _wire_creator_info(mock_api)

    # Ensure allow_duet is False for photo posts
    tiktok.tiktok_allow_duet = False
    tiktok.tiktok_allow_stitch = False

    # Mock upload_photo since post with images calls it
    mock_api.upload_photo = AsyncMock(return_value={"publish_id": "video-123"})

    # Mock download_images to avoid actual HTTP call
    with patch.object(tiktok, "download_images", new_callable=AsyncMock) as mock_download:
        mock_image = MagicMock()
        mock_image.content = b"image_content"
        mock_file_type = MagicMock()
        mock_file_type.mime = "image/jpeg"
        mock_image.file_type = mock_file_type
        mock_image.url = SAMPLE_IMAGE_URL
        mock_image.cleanup = MagicMock()
        mock_download.return_value = [mock_image]

        with patch.object(tiktok, "_output_status"):
            result = await tiktok.post(
                "Hello TikTok",
                "http://link.com",
                status_image_url_1=SAMPLE_IMAGE_URL,
            )

    assert result == "video-123"
    mock_preflight.assert_called_once_with(SAMPLE_IMAGE_URL, "tiktok", kind="image")


@pytest.mark.asyncio
@patch("agoras.media.preflight.preflight_url_for_platform")
@patch("agoras.platforms.tiktok.wrapper.TikTokAPI")
async def test_tiktok_post_with_description(mock_api_class, mock_preflight):
    """Test TikTok post method with description parameter."""
    mock_api = MagicMock()
    mock_api.authenticate = AsyncMock()
    mock_api_class.return_value = mock_api

    tiktok = TikTok(
        tiktok_client_key="key",
        tiktok_client_secret="secret",
        tiktok_access_token="token",
        tiktok_username="testuser",
        tiktok_refresh_token="refresh",
        tiktok_description="Test description",
    )

    await tiktok._initialize_client()
    _wire_creator_info(mock_api)

    # Ensure allow_duet is False for photo posts
    tiktok.tiktok_allow_duet = False
    tiktok.tiktok_allow_stitch = False

    # Mock upload_photo since post with images calls it
    mock_api.upload_photo = AsyncMock(return_value={"publish_id": "photo-123"})

    # Mock download_images to avoid actual HTTP call
    with patch.object(tiktok, "download_images", new_callable=AsyncMock) as mock_download:
        mock_image = MagicMock()
        mock_image.content = b"image_content"
        mock_file_type = MagicMock()
        mock_file_type.mime = "image/jpeg"
        mock_image.file_type = mock_file_type
        mock_image.url = SAMPLE_IMAGE_URL
        mock_image.cleanup = MagicMock()
        mock_download.return_value = [mock_image]

        with patch.object(tiktok, "_output_status"):
            result = await tiktok.post(
                "Hello TikTok",
                "http://link.com",
                status_image_url_1=SAMPLE_IMAGE_URL,
            )

    assert result == "photo-123"
    mock_preflight.assert_called_once_with(SAMPLE_IMAGE_URL, "tiktok", kind="image")
    # Verify description was passed to upload_photo
    mock_api.upload_photo.assert_called_once()
    assert mock_api.upload_photo.call_args.args[7] == "Test description"


@pytest.mark.asyncio
@patch("agoras.platforms.tiktok.wrapper.TikTokAPI")
async def test_tiktok_disconnect(mock_api_class):
    """Test TikTok disconnect method."""
    mock_api = MagicMock()
    mock_api.authenticate = AsyncMock()
    mock_api.disconnect = AsyncMock()
    mock_api_class.return_value = mock_api

    tiktok = TikTok(
        tiktok_client_key="key",
        tiktok_client_secret="secret",
        tiktok_access_token="token",
        tiktok_username="testuser",
        tiktok_refresh_token="refresh",
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
@patch("agoras.platforms.tiktok.wrapper.TikTokAPI")
async def test_tiktok_video(mock_api_class):
    """Test TikTok video method."""
    mock_api = MagicMock()
    mock_api.authenticate = AsyncMock()
    mock_api.upload_video = AsyncMock(return_value={"publish_id": "video-456"})
    mock_api.creator_info = None  # Skip duration check
    mock_api_class.return_value = mock_api

    tiktok = TikTok(
        tiktok_client_key="key",
        tiktok_client_secret="secret",
        tiktok_access_token="token",
        tiktok_username="testuser",
        tiktok_refresh_token="refresh",
    )

    await tiktok._initialize_client()
    _wire_creator_info(mock_api)

    # Mock download_video to avoid actual HTTP call
    with patch.object(tiktok, "download_video", new_callable=AsyncMock) as mock_download:
        mock_video = MagicMock()
        mock_video.content = b"video_content"
        mock_file_type = MagicMock()
        mock_file_type.mime = "video/mp4"
        mock_video.file_type = mock_file_type
        mock_video.url = "http://video.mp4"
        mock_video.cleanup = MagicMock()
        mock_video.get_duration = MagicMock(return_value=None)  # Skip duration check
        mock_download.return_value = mock_video

        with patch.object(tiktok, "_output_status"):
            with patch("builtins.print"):
                result = await tiktok.video("Video description", "http://video.mp4", "Video Title")

    assert result == "video-456"
    mock_api.upload_video.assert_called_once()


@pytest.mark.asyncio
@patch("agoras.platforms.tiktok.wrapper.TikTokAPI")
async def test_tiktok_unattended_public_privacy_fail_closed(mock_api_class):
    """Unattended PUBLIC_TO_EVERYONE must not call init/."""
    mock_api = MagicMock()
    mock_api.authenticate = AsyncMock()
    mock_api.upload_video = AsyncMock(return_value={"publish_id": "video-456"})
    mock_api_class.return_value = mock_api

    tiktok = TikTok(
        tiktok_client_key="key",
        tiktok_client_secret="secret",
        tiktok_access_token="token",
        tiktok_username="testuser",
        tiktok_refresh_token="refresh",
        tiktok_privacy_status="PUBLIC_TO_EVERYONE",
        tiktok_allow_duet=True,
        tiktok_allow_stitch=True,
        action="video",
    )

    await tiktok._initialize_client()
    _wire_creator_info(mock_api)

    with patch.object(tiktok, "download_video", new_callable=AsyncMock) as mock_download:
        mock_video = MagicMock()
        mock_video.content = b"video_content"
        mock_file_type = MagicMock()
        mock_file_type.mime = "video/mp4"
        mock_video.file_type = mock_file_type
        mock_video.url = "http://video.mp4"
        mock_video.cleanup = MagicMock()
        mock_video.get_duration = MagicMock(return_value=None)
        mock_download.return_value = mock_video

        with pytest.raises(Exception, match="SELF_ONLY"):
            await tiktok.video("Description", "http://video.mp4", "Title")

    mock_api.upload_video.assert_not_called()
    mock_api.refresh_creator_info.assert_not_called()


@pytest.mark.asyncio
@patch("agoras.platforms.tiktok.wrapper.TikTokAPI")
async def test_tiktok_like_not_supported(mock_api_class):
    """Test TikTok like raises exception."""
    mock_api = MagicMock()
    mock_api.authenticate = AsyncMock()
    mock_api.like = AsyncMock(side_effect=Exception("Like not supported"))
    mock_api_class.return_value = mock_api

    tiktok = TikTok(
        tiktok_client_key="key",
        tiktok_client_secret="secret",
        tiktok_access_token="token",
        tiktok_username="testuser",
        tiktok_refresh_token="refresh",
    )

    await tiktok._initialize_client()

    with pytest.raises(Exception, match="not supported"):
        await tiktok.like("post-123")


@pytest.mark.asyncio
@patch("agoras.platforms.tiktok.wrapper.TikTokAPI")
async def test_tiktok_delete_not_supported(mock_api_class):
    """Test TikTok delete raises exception."""
    mock_api = MagicMock()
    mock_api.authenticate = AsyncMock()
    mock_api.delete = AsyncMock(side_effect=Exception("Delete not supported"))
    mock_api_class.return_value = mock_api

    tiktok = TikTok(
        tiktok_client_key="key",
        tiktok_client_secret="secret",
        tiktok_access_token="token",
        tiktok_username="testuser",
        tiktok_refresh_token="refresh",
    )

    await tiktok._initialize_client()

    with pytest.raises(Exception, match="not supported"):
        await tiktok.delete("post-123")


@pytest.mark.asyncio
@patch("agoras.platforms.tiktok.wrapper.TikTokAPI")
async def test_tiktok_share_not_supported(mock_api_class):
    """Test TikTok share raises exception."""
    mock_api = MagicMock()
    mock_api.authenticate = AsyncMock()
    mock_api.share = AsyncMock(side_effect=Exception("Share not supported"))
    mock_api_class.return_value = mock_api

    tiktok = TikTok(
        tiktok_client_key="key",
        tiktok_client_secret="secret",
        tiktok_access_token="token",
        tiktok_username="testuser",
        tiktok_refresh_token="refresh",
    )

    await tiktok._initialize_client()

    with pytest.raises(Exception, match="not supported"):
        await tiktok.share("post-123")


@pytest.mark.asyncio
@patch("agoras.platforms.tiktok.wrapper.TikTokAPI")
async def test_tiktok_post_with_duet_enabled_raises_error(mock_api_class):
    """Test TikTok post raises error when allow_duet is enabled for photos."""
    mock_api = MagicMock()
    mock_api.authenticate = AsyncMock()
    mock_api_class.return_value = mock_api

    tiktok = TikTok(
        tiktok_client_key="key",
        tiktok_client_secret="secret",
        tiktok_access_token="token",
        tiktok_username="testuser",
        tiktok_refresh_token="refresh",
        tiktok_allow_duet=True,
    )

    await tiktok._initialize_client()

    with pytest.raises(Exception, match="allow-duet is not supported for photo posts"):
        await tiktok.post("Hello", "http://link.com", status_image_url_1="img.jpg")


@pytest.mark.asyncio
@patch("agoras.platforms.tiktok.wrapper.TikTokAPI")
async def test_tiktok_post_with_stitch_enabled_raises_error(mock_api_class):
    """Test TikTok post raises error when allow_stitch is enabled for photos."""
    mock_api = MagicMock()
    mock_api.authenticate = AsyncMock()
    mock_api_class.return_value = mock_api

    tiktok = TikTok(
        tiktok_client_key="key",
        tiktok_client_secret="secret",
        tiktok_access_token="token",
        tiktok_username="testuser",
        tiktok_refresh_token="refresh",
        tiktok_allow_stitch=True,
    )

    await tiktok._initialize_client()

    with pytest.raises(Exception, match="not supported for photo posts"):
        await tiktok.post("Hello", "http://link.com", status_image_url_1="img.jpg")


def test_tiktok_convert_bool():
    """Test TikTok _convert_bool utility method."""
    tiktok = TikTok(tiktok_client_key="key", tiktok_client_secret="secret", tiktok_username="testuser")

    # Test various truthy values
    assert tiktok._convert_bool("true", False) is True
    assert tiktok._convert_bool("True", False) is True
    assert tiktok._convert_bool("1", False) is True
    assert tiktok._convert_bool(1, False) is True
    assert tiktok._convert_bool(True, False) is True

    # Test falsy values
    assert tiktok._convert_bool("false", True) is False
    assert tiktok._convert_bool("False", True) is False
    assert tiktok._convert_bool("0", True) is False
    assert tiktok._convert_bool(0, True) is False
    assert tiktok._convert_bool(False, True) is False

    # Test default
    assert tiktok._convert_bool(None, True) is True
    assert tiktok._convert_bool(None, False) is False


@pytest.mark.asyncio
@patch("agoras.platforms.tiktok.wrapper.TikTokAPI")
async def test_tiktok_handle_post_action(mock_api_class):
    """Test TikTok _handle_post_action method."""
    mock_api = MagicMock()
    mock_api.authenticate = AsyncMock()
    mock_api.upload_photo = AsyncMock(return_value={"publish_id": "post-123"})
    mock_api_class.return_value = mock_api

    tiktok = TikTok(
        tiktok_client_key="key",
        tiktok_client_secret="secret",
        tiktok_access_token="token",
        tiktok_username="testuser",
        tiktok_refresh_token="refresh",
    )

    await tiktok._initialize_client()
    tiktok.tiktok_allow_duet = False
    tiktok.tiktok_allow_stitch = False

    # Set config values
    with patch.object(tiktok, "_get_config_value") as mock_get_config:
        mock_get_config.side_effect = lambda key, env_key, default=None: {
            "status_image_url_1": "http://image.jpg",
            "status_image_url_2": None,
            "status_image_url_3": None,
            "status_image_url_4": None,
        }.get(key, default)

        with patch.object(tiktok, "post", new_callable=AsyncMock) as mock_post:
            mock_post.return_value = "post-123"
            with patch.object(tiktok, "_output_status"):
                await tiktok._handle_post_action()

            # Action handler calls post but doesn't return value
            mock_post.assert_called_once()


@pytest.mark.asyncio
@patch("agoras.platforms.tiktok.wrapper.TikTokAPI")
async def test_tiktok_handle_video_action(mock_api_class):
    """Test TikTok _handle_video_action method."""
    mock_api = MagicMock()
    mock_api.authenticate = AsyncMock()
    mock_api.upload_video = AsyncMock(return_value={"publish_id": "video-123"})
    mock_api.creator_info = None
    mock_api_class.return_value = mock_api

    tiktok = TikTok(
        tiktok_client_key="key",
        tiktok_client_secret="secret",
        tiktok_access_token="token",
        tiktok_username="testuser",
        tiktok_refresh_token="refresh",
        tiktok_title="Video Title",
    )

    await tiktok._initialize_client()

    with patch.object(tiktok, "_get_config_value", return_value="http://video.mp4"):
        with patch.object(tiktok, "video", new_callable=AsyncMock) as mock_video:
            mock_video.return_value = "video-123"
            with patch.object(tiktok, "_output_status"):
                with patch.object(tiktok, "download_video", new_callable=AsyncMock) as mock_download:
                    mock_video_obj = MagicMock()
                    mock_video_obj.content = b"content"
                    mock_video_obj.file_type = MagicMock(mime="video/mp4")
                    mock_video_obj.get_duration = MagicMock(return_value=None)
                    mock_video_obj.cleanup = MagicMock()
                    mock_download.return_value = mock_video_obj
                    with patch("builtins.print"):
                        await tiktok._handle_video_action()

            # Action handler calls video but doesn't return value
            mock_video.assert_called_once()


@pytest.mark.asyncio
@patch("agoras.platforms.tiktok.wrapper.TikTokAPI")
async def test_tiktok_handle_like_action(mock_api_class):
    """Test TikTok _handle_like_action method."""
    mock_api = MagicMock()
    mock_api.authenticate = AsyncMock()
    mock_api.like = AsyncMock(side_effect=Exception("Like not supported"))
    mock_api_class.return_value = mock_api

    tiktok = TikTok(
        tiktok_client_key="key",
        tiktok_client_secret="secret",
        tiktok_access_token="token",
        tiktok_username="testuser",
        tiktok_refresh_token="refresh",
    )

    await tiktok._initialize_client()

    with patch.object(tiktok, "_get_config_value", return_value="post-123"):
        with pytest.raises(Exception, match="not supported"):
            await tiktok._handle_like_action()


@pytest.mark.asyncio
@patch("agoras.platforms.tiktok.wrapper.TikTokAPI")
async def test_tiktok_handle_share_action(mock_api_class):
    """Test TikTok _handle_share_action method."""
    mock_api = MagicMock()
    mock_api.authenticate = AsyncMock()
    mock_api.share = AsyncMock(side_effect=Exception("Share not supported"))
    mock_api_class.return_value = mock_api

    tiktok = TikTok(
        tiktok_client_key="key",
        tiktok_client_secret="secret",
        tiktok_access_token="token",
        tiktok_username="testuser",
        tiktok_refresh_token="refresh",
    )

    await tiktok._initialize_client()

    with patch.object(tiktok, "_get_config_value", return_value="post-123"):
        with pytest.raises(Exception, match="not supported"):
            await tiktok._handle_share_action()


@pytest.mark.asyncio
@patch("agoras.platforms.tiktok.wrapper.TikTokAPI")
async def test_tiktok_handle_delete_action(mock_api_class):
    """Test TikTok _handle_delete_action method."""
    mock_api = MagicMock()
    mock_api.authenticate = AsyncMock()
    mock_api.delete = AsyncMock(side_effect=Exception("Delete not supported"))
    mock_api_class.return_value = mock_api

    tiktok = TikTok(
        tiktok_client_key="key",
        tiktok_client_secret="secret",
        tiktok_access_token="token",
        tiktok_username="testuser",
        tiktok_refresh_token="refresh",
    )

    await tiktok._initialize_client()

    with patch.object(tiktok, "_get_config_value", return_value="post-123"):
        with pytest.raises(Exception, match="not supported"):
            await tiktok._handle_delete_action()


@pytest.mark.asyncio
@patch("agoras.platforms.tiktok.wrapper.TikTokAPI")
@patch("builtins.print")
async def test_tiktok_print_brand_content_notices(mock_print, mock_api_class):
    """Test TikTok _print_brand_content_notices method."""
    mock_api = MagicMock()
    mock_api.authenticate = AsyncMock()
    mock_api_class.return_value = mock_api

    tiktok = TikTok(
        tiktok_client_key="key",
        tiktok_client_secret="secret",
        tiktok_access_token="token",
        tiktok_username="testuser",
        tiktok_refresh_token="refresh",
    )

    await tiktok._initialize_client()
    tiktok.brand_organic = True
    tiktok.brand_content = True

    tiktok._print_brand_content_notices()

    # Should print notices when brand content flags are set
    assert mock_print.called


def _mock_downloaded_video():
    """Return a downloaded video stub that passes MIME validation."""
    mock_video = MagicMock()
    mock_video.content = b"video_content"
    mock_video.file_type = MagicMock(mime="video/mp4")
    mock_video.url = "http://video.mp4"
    mock_video.cleanup = MagicMock()
    mock_video.get_duration = MagicMock(return_value=10)
    return mock_video


@pytest.mark.asyncio
@patch("agoras.media.preflight.preflight_url_for_platform")
@patch("agoras.platforms.tiktok.wrapper.TikTokAPI")
async def test_tiktok_failed_creator_info_never_uploads(mock_api_class, mock_preflight):
    """Failed creator_info must not reach upload_photo."""
    mock_api = MagicMock()
    mock_api.authenticate = AsyncMock()
    mock_api.upload_photo = AsyncMock(return_value={"publish_id": "nope"})
    mock_api.refresh_creator_info = AsyncMock(
        side_effect=Exception("TikTok is rate limiting this account. Try again later.")
    )
    mock_api_class.return_value = mock_api

    tiktok = TikTok(
        tiktok_client_key="key",
        tiktok_client_secret="secret",
        tiktok_access_token="token",
        tiktok_username="testuser",
        tiktok_refresh_token="refresh",
        action="post",
    )
    await tiktok._initialize_client()
    tiktok.tiktok_allow_duet = False
    tiktok.tiktok_allow_stitch = False

    with patch.object(tiktok, "_should_open_composer", return_value=False):
        with patch.object(tiktok, "download_images", new_callable=AsyncMock) as mock_download:
            mock_image = MagicMock()
            mock_image.content = b"image_content"
            mock_image.file_type = MagicMock(mime="image/jpeg")
            mock_image.url = SAMPLE_IMAGE_URL
            mock_image.cleanup = MagicMock()
            mock_download.return_value = [mock_image]
            with pytest.raises(Exception, match="again later"):
                await tiktok.post("Hello", "", status_image_url_1=SAMPLE_IMAGE_URL)

    mock_api.upload_photo.assert_not_called()


@pytest.mark.asyncio
@patch("agoras.platforms.tiktok.wrapper.TikTokAPI")
async def test_tiktok_username_mismatch_aborts_before_upload(mock_api_class):
    """Username mismatch aborts before composer or init/."""
    mock_api = MagicMock()
    mock_api.authenticate = AsyncMock()
    mock_api.upload_video = AsyncMock()
    mock_api.refresh_creator_info = AsyncMock(side_effect=Exception("Username mismatch: other != testuser"))
    mock_api_class.return_value = mock_api

    tiktok = TikTok(
        tiktok_client_key="key",
        tiktok_client_secret="secret",
        tiktok_access_token="token",
        tiktok_username="testuser",
        tiktok_refresh_token="refresh",
        action="video",
    )
    await tiktok._initialize_client()

    with patch.object(tiktok, "_should_open_composer", return_value=False):
        with patch.object(tiktok, "download_video", new_callable=AsyncMock) as mock_download:
            mock_download.return_value = _mock_downloaded_video()
            with pytest.raises(Exception, match="Username mismatch"):
                await tiktok.video("desc", "http://video.mp4", "Title")

    mock_api.upload_video.assert_not_called()


@pytest.mark.asyncio
@patch("agoras.platforms.tiktok.wrapper.TikTokAPI")
async def test_tiktok_video_duration_zero_max_is_not_reject_all(mock_api_class):
    """max_video_post_duration_sec of 0 must not reject every video."""
    mock_api = MagicMock()
    mock_api.authenticate = AsyncMock()
    mock_api.upload_video = AsyncMock(return_value={"publish_id": "video-ok"})
    mock_api_class.return_value = mock_api

    tiktok = TikTok(
        tiktok_client_key="key",
        tiktok_client_secret="secret",
        tiktok_access_token="token",
        tiktok_username="testuser",
        tiktok_refresh_token="refresh",
    )
    await tiktok._initialize_client()
    _wire_creator_info(mock_api, _ok_creator_info(max_video_post_duration_sec=0))

    with patch.object(tiktok, "_should_open_composer", return_value=False):
        with patch.object(tiktok, "download_video", new_callable=AsyncMock) as mock_download:
            mock_download.return_value = _mock_downloaded_video()
            with patch.object(tiktok, "_output_status"):
                with patch("builtins.print"):
                    result = await tiktok.video("desc", "http://video.mp4", "Title")

    assert result == "video-ok"
    mock_api.upload_video.assert_called_once()


@pytest.mark.asyncio
@patch("agoras.platforms.tiktok.wrapper.TikTokAPI")
async def test_tiktok_video_duration_exceeds_max(mock_api_class):
    """Videos longer than creator max duration abort before init/."""
    mock_api = MagicMock()
    mock_api.authenticate = AsyncMock()
    mock_api.upload_video = AsyncMock()
    mock_api_class.return_value = mock_api

    tiktok = TikTok(
        tiktok_client_key="key",
        tiktok_client_secret="secret",
        tiktok_access_token="token",
        tiktok_username="testuser",
        tiktok_refresh_token="refresh",
    )
    await tiktok._initialize_client()
    _wire_creator_info(mock_api, _ok_creator_info(max_video_post_duration_sec=5))

    with patch.object(tiktok, "_should_open_composer", return_value=False):
        with patch.object(tiktok, "download_video", new_callable=AsyncMock) as mock_download:
            mock_download.return_value = _mock_downloaded_video()
            with pytest.raises(Exception, match="exceeds max duration"):
                await tiktok.video("desc", "http://video.mp4", "Title")

    mock_api.upload_video.assert_not_called()


@pytest.mark.asyncio
@patch("agoras.platforms.tiktok.wrapper.TikTokAPI")
async def test_tiktok_unattended_omitted_privacy_uses_self_only(mock_api_class):
    """Unattended omitted privacy uses SELF_ONLY and does not start the composer."""
    mock_api = MagicMock()
    mock_api.authenticate = AsyncMock()
    mock_api.upload_video = AsyncMock(return_value={"publish_id": "video-priv"})
    mock_api_class.return_value = mock_api

    tiktok = TikTok(
        tiktok_client_key="key",
        tiktok_client_secret="secret",
        tiktok_access_token="token",
        tiktok_username="testuser",
        tiktok_refresh_token="refresh",
        action="video",
    )
    await tiktok._initialize_client()
    _wire_creator_info(mock_api)

    with patch.object(tiktok, "_should_open_composer", return_value=False):
        with patch.object(tiktok, "_open_composer") as mock_composer:
            with patch.object(tiktok, "download_video", new_callable=AsyncMock) as mock_download:
                mock_download.return_value = _mock_downloaded_video()
                with patch.object(tiktok, "_output_status"):
                    with patch("builtins.print"):
                        await tiktok.video("desc", "http://video.mp4", "Title")

    mock_composer.assert_not_called()
    assert mock_api.upload_video.call_args[0][2] == "SELF_ONLY"


@pytest.mark.asyncio
@patch("agoras.platforms.tiktok.wrapper.TikTokAPI")
async def test_tiktok_unattended_brand_content_rejected(mock_api_class):
    """Unattended commercial flags are rejected locally."""
    mock_api = MagicMock()
    mock_api.authenticate = AsyncMock()
    mock_api.upload_video = AsyncMock()
    mock_api_class.return_value = mock_api

    tiktok = TikTok(
        tiktok_client_key="key",
        tiktok_client_secret="secret",
        tiktok_access_token="token",
        tiktok_username="testuser",
        tiktok_refresh_token="refresh",
        tiktok_brand_content=True,
        action="video",
    )
    await tiktok._initialize_client()
    _wire_creator_info(mock_api)

    with patch.object(tiktok, "_should_open_composer", return_value=False):
        with patch.object(tiktok, "download_video", new_callable=AsyncMock) as mock_download:
            mock_download.return_value = _mock_downloaded_video()
            with pytest.raises(Exception, match="composer"):
                await tiktok.video("desc", "http://video.mp4", "Title")

    mock_api.upload_video.assert_not_called()
    assert UNATTENDED_COMMERCIAL_ERROR


@pytest.mark.asyncio
@patch("agoras.platforms.tiktok.wrapper.TikTokAPI")
async def test_tiktok_interactive_self_only_still_starts_composer(mock_api_class):
    """Interactive SELF_ONLY still opens the composer."""
    mock_api = MagicMock()
    mock_api.authenticate = AsyncMock()
    mock_api.upload_video = AsyncMock(return_value={"publish_id": "video-f1"})
    mock_api_class.return_value = mock_api

    tiktok = TikTok(
        tiktok_client_key="key",
        tiktok_client_secret="secret",
        tiktok_access_token="token",
        tiktok_username="testuser",
        tiktok_refresh_token="refresh",
        tiktok_privacy_status="SELF_ONLY",
        action="video",
    )
    await tiktok._initialize_client()
    _wire_creator_info(mock_api)
    payload = _composer_payload(title="From composer", privacy_level="SELF_ONLY")

    with patch.object(tiktok, "_should_open_composer", return_value=True):
        with patch.object(tiktok, "_open_composer", return_value=payload) as mock_composer:
            with patch.object(tiktok, "download_video", new_callable=AsyncMock) as mock_download:
                mock_download.return_value = _mock_downloaded_video()
                with patch.object(tiktok, "_output_status"):
                    with patch("builtins.print"):
                        result = await tiktok.video("CLI title", "http://video.mp4", "CLI title")

    mock_composer.assert_called_once()
    assert result == "video-f1"
    assert mock_api.upload_video.call_args[0][1] == "From composer"
    assert mock_api.upload_video.call_args[0][0] == "http://video.mp4"


@pytest.mark.asyncio
@patch("agoras.platforms.tiktok.wrapper.TikTokAPI")
async def test_tiktok_interactive_empty_composer_title_is_used_as_is(mock_api_class):
    """Confirmed empty title must not fall back to the CLI seed."""
    mock_api = MagicMock()
    mock_api.authenticate = AsyncMock()
    mock_api.upload_video = AsyncMock(return_value={"publish_id": "video-empty"})
    mock_api_class.return_value = mock_api

    tiktok = TikTok(
        tiktok_client_key="key",
        tiktok_client_secret="secret",
        tiktok_access_token="token",
        tiktok_username="testuser",
        tiktok_refresh_token="refresh",
        tiktok_privacy_status="SELF_ONLY",
        action="video",
    )
    await tiktok._initialize_client()
    _wire_creator_info(mock_api)
    payload = _composer_payload(title="", privacy_level="SELF_ONLY")

    with patch.object(tiktok, "_should_open_composer", return_value=True):
        with patch.object(tiktok, "_open_composer", return_value=payload):
            with patch.object(tiktok, "download_video", new_callable=AsyncMock) as mock_download:
                mock_download.return_value = _mock_downloaded_video()
                with patch.object(tiktok, "_output_status"):
                    with patch("builtins.print"):
                        await tiktok.video("CLI title", "http://video.mp4", "CLI title")

    assert mock_api.upload_video.call_args[0][1] == ""


@pytest.mark.asyncio
@patch("agoras.platforms.tiktok.wrapper.TikTokAPI")
async def test_tiktok_interactive_public_uses_composer_not_flags(mock_api_class):
    """Interactive public uses composer metadata instead of flag-only init/."""
    mock_api = MagicMock()
    mock_api.authenticate = AsyncMock()
    mock_api.upload_video = AsyncMock(return_value={"publish_id": "video-pub"})
    mock_api_class.return_value = mock_api

    tiktok = TikTok(
        tiktok_client_key="key",
        tiktok_client_secret="secret",
        tiktok_access_token="token",
        tiktok_username="testuser",
        tiktok_refresh_token="refresh",
        tiktok_privacy_status="PUBLIC_TO_EVERYONE",
        tiktok_allow_comments=True,
        action="video",
    )
    await tiktok._initialize_client()
    _wire_creator_info(mock_api)
    payload = _composer_payload(
        title="Public from composer",
        privacy_level="PUBLIC_TO_EVERYONE",
        allow_comments=False,
        allow_duet=True,
        allow_stitch=False,
    )

    with patch.object(tiktok, "_should_open_composer", return_value=True):
        with patch.object(tiktok, "_open_composer", return_value=payload):
            with patch.object(tiktok, "download_video", new_callable=AsyncMock) as mock_download:
                mock_download.return_value = _mock_downloaded_video()
                with patch.object(tiktok, "_output_status"):
                    with patch("builtins.print"):
                        await tiktok.video("CLI title", "http://video.mp4", "CLI title")

    call_args = mock_api.upload_video.call_args[0]
    assert call_args[2] == "PUBLIC_TO_EVERYONE"
    assert call_args[3] is False  # composer comments override CLI --allow-comments
    assert call_args[4] is True
    assert call_args[5] is False


@pytest.mark.asyncio
@patch("agoras.platforms.tiktok.wrapper.TikTokAPI")
async def test_tiktok_composer_cancel_skips_init(mock_api_class):
    """Composer cancel must not call init/."""
    mock_api = MagicMock()
    mock_api.authenticate = AsyncMock()
    mock_api.upload_video = AsyncMock()
    mock_api_class.return_value = mock_api

    tiktok = TikTok(
        tiktok_client_key="key",
        tiktok_client_secret="secret",
        tiktok_access_token="token",
        tiktok_username="testuser",
        tiktok_refresh_token="refresh",
        action="video",
    )
    await tiktok._initialize_client()
    _wire_creator_info(mock_api)

    with patch.object(tiktok, "_should_open_composer", return_value=True):
        with patch.object(tiktok, "_open_composer", return_value=None):
            with patch.object(tiktok, "download_video", new_callable=AsyncMock) as mock_download:
                mock_download.return_value = _mock_downloaded_video()
                with pytest.raises(Exception, match="cancelled"):
                    await tiktok.video("desc", "http://video.mp4", "Title")

    mock_api.upload_video.assert_not_called()


def test_tiktok_feed_actions_never_open_composer():
    """last-from-feed / random-from-feed / schedule stay on the unattended path."""
    tiktok = TikTok(action="last-from-feed")
    with patch("sys.stdin") as mock_stdin:
        mock_stdin.isatty.return_value = True
        with patch.dict("os.environ", {}, clear=False):
            os.environ.pop("CI", None)
            assert tiktok._should_open_composer() is False
    tiktok._action = "random-from-feed"
    with patch.object(sys.stdin, "isatty", return_value=True):
        assert tiktok._should_open_composer() is False
    tiktok._action = "schedule"
    with patch.object(sys.stdin, "isatty", return_value=True):
        assert tiktok._should_open_composer() is False


def test_tiktok_ci_selects_unattended_path():
    """CI=1 selects F2 even on a TTY."""
    tiktok = TikTok(action="video")
    with patch.object(sys.stdin, "isatty", return_value=True):
        with patch.dict("os.environ", {"CI": "true"}):
            assert tiktok._should_open_composer() is False


def test_tiktok_ci_false_still_opens_composer():
    """CI=false must not skip the composer on an interactive TTY."""
    tiktok = TikTok(action="video")
    with patch.object(sys.stdin, "isatty", return_value=True):
        with patch.dict("os.environ", {"CI": "false"}):
            assert tiktok._should_open_composer() is True


def test_tiktok_unattended_privacy_error_mentions_composer():
    """Fail-closed copy points operators at the interactive composer."""
    assert "composer" in UNATTENDED_PRIVACY_ERROR.lower()
