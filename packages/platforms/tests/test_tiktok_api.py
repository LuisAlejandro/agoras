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
    with patch("agoras.platforms.tiktok.api.TikTokAuthManager") as mock_auth_class:
        mock_auth = MagicMock()
        mock_auth.authenticate = AsyncMock()
        mock_auth.access_token = "token"
        mock_auth.username = "testuser"
        mock_auth.user_info = {
            "creator_username": "testuser",
            "creator_nickname": "Test User",
            "privacy_level_options": ["SELF_ONLY"],
        }
        mock_auth.ensure_authenticated = MagicMock()  # Don't raise
        mock_auth.client = MagicMock()
        mock_auth_class.return_value = mock_auth

        api = TikTokAPI("testuser", "client_key", "client_secret", "refresh_token")
        api._authenticated = True
        api.client = MagicMock()
        api.client.get_user_info = MagicMock(
            return_value={
                "creator_username": "testuser",
                "creator_nickname": "Test User",
                "privacy_level_options": ["SELF_ONLY", "PUBLIC_TO_EVERYONE"],
                "comment_disabled": False,
                "duet_disabled": False,
                "stitch_disabled": False,
                "max_video_post_duration_sec": 180,
            }
        )
        api.client.upload_video = MagicMock(return_value={"data": {"publish_id": "video-123"}})
        api.client.get_publish_status = MagicMock(
            return_value={"data": {"status": "PUBLISH_COMPLETE", "publicaly_available_post_id": ["post-123"]}}
        )
        yield api


# Authentication Tests


@pytest.mark.asyncio
@patch("agoras.platforms.tiktok.api.TikTokAuthManager")
async def test_tiktok_api_authenticate(mock_auth_class):
    """Test TikTokAPI authenticate method."""
    mock_auth = MagicMock()
    mock_auth.authenticate = AsyncMock(return_value=True)
    mock_auth.access_token = "token123"
    mock_auth.client = MagicMock()
    mock_auth_class.return_value = mock_auth

    api = TikTokAPI("testuser", "client_key", "client_secret")
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
@patch("agoras.platforms.tiktok.api.asyncio.sleep")
async def test_tiktok_api_upload_video(mock_sleep, tiktok_api):
    """Test TikTokAPI upload_video."""
    result = await tiktok_api.upload_video(
        video_url="http://video.mp4", title="Test Video", privacy_status="PUBLIC_TO_EVERYONE"
    )

    assert result == {"publish_id": "video-123"}
    tiktok_api.client.upload_video.assert_called_once()


@pytest.mark.asyncio
@patch("agoras.platforms.tiktok.api.asyncio.sleep")
async def test_tiktok_api_upload_with_privacy_settings(mock_sleep, tiktok_api):
    """Test TikTokAPI upload_video with privacy settings."""
    result = await tiktok_api.upload_video(
        video_url="http://video.mp4",
        title="Test Video",
        privacy_status="SELF_ONLY",
        allow_comments=False,
        allow_duet=False,
        allow_stitch=False,
    )

    assert result == {"publish_id": "video-123"}
    tiktok_api.client.upload_video.assert_called_once_with(
        video_url="http://video.mp4",
        title="Test Video",
        privacy_status="SELF_ONLY",
        allow_comments=False,
        allow_duet=False,
        allow_stitch=False,
        is_brand_organic=False,
        is_brand_content=False,
    )


@pytest.mark.asyncio
@patch("agoras.platforms.tiktok.api.asyncio.sleep")
async def test_tiktok_api_upload_with_duet_stitch_options(mock_sleep, tiktok_api):
    """Test TikTokAPI upload_video with duet/stitch options."""
    result = await tiktok_api.upload_video(
        video_url="http://video.mp4",
        title="Test Video",
        privacy_status="PUBLIC_TO_EVERYONE",
        allow_duet=True,
        allow_stitch=True,
    )

    assert result == {"publish_id": "video-123"}
    tiktok_api.client.upload_video.assert_called_once()


@pytest.mark.asyncio
async def test_tiktok_api_upload_photo(tiktok_api):
    """Test TikTokAPI upload_photo."""
    # Mock the client's upload_photo to return the expected response structure
    tiktok_api.client.upload_photo = MagicMock(
        return_value={"data": {"publish_id": "photo-123"}, "error": {"code": "ok", "message": ""}}
    )

    result = await tiktok_api.upload_photo(
        photo_images=["http://image1.jpg"], title="Test Photo", privacy_status="PUBLIC_TO_EVERYONE"
    )

    assert result == {"publish_id": "photo-123"}
    tiktok_api.client.upload_photo.assert_called_once_with(
        photo_images=["http://image1.jpg"],
        title="Test Photo",
        privacy_status="PUBLIC_TO_EVERYONE",
        allow_comments=True,
        is_brand_organic=False,
        is_brand_content=False,
        auto_add_music=False,
        description="",
    )


@pytest.mark.asyncio
async def test_tiktok_api_upload_photo_with_description(tiktok_api):
    """Test TikTokAPI upload_photo with description parameter."""
    # Mock the client's upload_photo to return the expected response structure
    tiktok_api.client.upload_photo = MagicMock(
        return_value={"data": {"publish_id": "photo-456"}, "error": {"code": "ok", "message": ""}}
    )

    result = await tiktok_api.upload_photo(
        photo_images=["http://image1.jpg", "http://image2.jpg"],
        title="Test Photo",
        privacy_status="SELF_ONLY",
        allow_comments=False,
        auto_add_music=True,
        description="Test description for photo post",
    )

    assert result == {"publish_id": "photo-456"}
    tiktok_api.client.upload_photo.assert_called_once_with(
        photo_images=["http://image1.jpg", "http://image2.jpg"],
        title="Test Photo",
        privacy_status="SELF_ONLY",
        allow_comments=False,
        is_brand_organic=False,
        is_brand_content=False,
        auto_add_music=True,
        description="Test description for photo post",
    )


# Post Tests


@pytest.mark.asyncio
async def test_tiktok_api_post_not_supported(tiktok_api):
    """Test TikTokAPI post method raises exception."""
    with pytest.raises(Exception, match="Regular posts not supported"):
        await tiktok_api.post("Test post")


@pytest.mark.asyncio
async def test_tiktok_api_post_with_video_url(tiktok_api):
    """Test TikTokAPI post method raises exception even with video URL."""
    with pytest.raises(Exception, match="Regular posts not supported"):
        await tiktok_api.post("Test post", video_url="http://video.mp4")


# User Info Tests


@pytest.mark.asyncio
async def test_tiktok_api_refresh_creator_info_username_mismatch(tiktok_api):
    """Test refresh_creator_info aborts when the username does not match."""
    tiktok_api.client.get_user_info = MagicMock(
        return_value={
            "creator_username": "otheruser",
            "creator_nickname": "Other",
        }
    )

    with pytest.raises(Exception, match="Username mismatch"):
        await tiktok_api.refresh_creator_info()


@pytest.mark.asyncio
async def test_tiktok_api_refresh_creator_info_try_later(tiktok_api):
    """Test non-ok creator_info becomes a try-later error, not Not authenticated."""
    tiktok_api.client.get_user_info = MagicMock(
        side_effect=Exception("TikTok is rate limiting this account. Try again later.")
    )

    with pytest.raises(Exception, match="again later"):
        await tiktok_api.refresh_creator_info()


def test_tiktok_client_parses_nested_error_and_429():
    """Test creator_info parsing uses error.code and HTTP 429."""
    from agoras.platforms.tiktok.client import TikTokAPIClient

    ok = MagicMock()
    ok.status_code = 200
    ok.json.return_value = {
        "data": {
            "creator_nickname": "Ada",
            "privacy_level_options": ["SELF_ONLY"],
        },
        "error": {"code": "ok", "message": ""},
    }
    parsed = TikTokAPIClient._parse_creator_info_response(ok)
    assert parsed["creator_nickname"] == "Ada"

    limited = MagicMock()
    limited.status_code = 429
    with pytest.raises(Exception, match="again later"):
        TikTokAPIClient._parse_creator_info_response(limited)

    nested = MagicMock()
    nested.status_code = 200
    nested.json.return_value = {
        "error": {"code": "spam_risk_too_many_posts", "message": "slow down"},
        "data": {},
    }
    with pytest.raises(Exception, match="again later"):
        TikTokAPIClient._parse_creator_info_response(nested)

    missing = MagicMock()
    missing.status_code = 200
    missing.json.return_value = {"error": {"code": "ok"}, "data": None}
    with pytest.raises(Exception, match="cannot post"):
        TikTokAPIClient._parse_creator_info_response(missing)

    other = MagicMock()
    other.status_code = 200
    other.json.return_value = {
        "error": {"code": "access_token_invalid", "message": "bad token"},
        "message": "this top-level message must not be used",
    }
    with pytest.raises(Exception, match=r"\[access_token_invalid\] bad token"):
        TikTokAPIClient._parse_creator_info_response(other)


# Not Supported Tests


@pytest.mark.asyncio
async def test_tiktok_api_like_raises_exception(tiktok_api):
    """Test TikTokAPI like raises exception."""
    with pytest.raises(Exception, match="Like not supported"):
        await tiktok_api.like("post-123")


@pytest.mark.asyncio
async def test_tiktok_api_delete_raises_exception(tiktok_api):
    """Test TikTokAPI delete raises exception."""
    with pytest.raises(Exception, match="Delete not supported"):
        await tiktok_api.delete("post-123")


@pytest.mark.asyncio
async def test_tiktok_api_share_raises_exception(tiktok_api):
    """Test TikTokAPI share raises exception."""
    with pytest.raises(Exception, match="Share not supported"):
        await tiktok_api.share("post-123")


# Error Handling Tests


@pytest.mark.asyncio
@patch("agoras.platforms.tiktok.api.asyncio.sleep")
async def test_tiktok_api_upload_error(mock_sleep, tiktok_api):
    """Test TikTokAPI handles upload errors."""
    tiktok_api.client.upload_video = MagicMock(side_effect=Exception("Upload failed"))

    with pytest.raises(Exception, match="Upload failed"):
        await tiktok_api.upload_video(video_url="http://video.mp4", title="Test", privacy_status="PUBLIC_TO_EVERYONE")


# Property Tests


def test_tiktok_api_properties():
    """Test TikTokAPI property accessors."""
    with patch("agoras.platforms.tiktok.api.TikTokAuthManager") as mock_auth_class:
        mock_auth = MagicMock()
        mock_auth.access_token = "token123"
        mock_auth.user_info = {"username": "testuser"}
        mock_auth_class.return_value = mock_auth

        api = TikTokAPI("testuser", "client_key", "client_secret")

        assert api.access_token == "token123"
        assert api.creator_info == {"username": "testuser"}
