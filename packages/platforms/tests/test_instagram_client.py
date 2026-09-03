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

from agoras.platforms.instagram.client import InstagramAPIClient, _resumable_upload_timeout


def test_resumable_upload_timeout_scales_and_caps():
    """Timeout grows with file size and stays between 30s and 10 minutes."""
    assert _resumable_upload_timeout(0) == 30
    assert _resumable_upload_timeout(20 * 1024 * 1024) == 40
    assert _resumable_upload_timeout(10 * 1024 * 1024 * 1024) == 600


@pytest.mark.asyncio
@patch("agoras.platforms.instagram.client.build_upload_session")
@patch("agoras.platforms.instagram.client.GraphAPI")
async def test_create_resumable_video_inits_and_uploads_bytes(mock_graph_api_class, mock_session_factory):
    """Resumable init omits video_url and POSTs bytes to rupload.facebook.com."""
    mock_graph_api = MagicMock()
    mock_graph_api.post_object.return_value = {
        "id": "ig-container-1",
        "uri": "https://rupload.facebook.com/ig-api-upload/v21.0/ig-container-1",
    }
    mock_graph_api_class.return_value = mock_graph_api

    mock_session = MagicMock()
    mock_session.post.return_value = MagicMock(status_code=200)
    mock_session.__enter__.return_value = mock_session
    mock_session_factory.return_value = mock_session

    client = InstagramAPIClient("access_token")
    await client.authenticate()
    client.wait_for_media_container = AsyncMock()

    result = await client.create_resumable_video(
        "ig-user-1",
        b"video-bytes",
        caption="Hello",
        media_type="REELS",
    )

    assert result == "ig-container-1"
    init_data = mock_graph_api.post_object.call_args.kwargs["data"]
    assert init_data["upload_type"] == "resumable"
    assert init_data["media_type"] == "REELS"
    assert init_data["caption"] == "Hello"
    assert "video_url" not in init_data

    upload_call = mock_session.post.call_args
    assert upload_call.args[0] == "https://rupload.facebook.com/ig-api-upload/v21.0/ig-container-1"
    assert upload_call.kwargs["data"] == b"video-bytes"
    assert upload_call.kwargs["headers"]["Authorization"] == "OAuth access_token"
    assert upload_call.kwargs["headers"]["offset"] == "0"
    assert upload_call.kwargs["headers"]["file_size"] == str(len(b"video-bytes"))
    client.wait_for_media_container.assert_awaited_once_with("ig-container-1")


def test_upload_session_retry_config():
    """The rupload session pins the previous retry contract."""
    from agoras.common.utils import build_upload_session

    with build_upload_session(3, {429, 500, 502, 503, 504}, ["POST"]) as session:
        adapter = session.get_adapter("https://")
        retry = adapter.max_retries
        assert retry.total == 2
        assert retry.connect == 0
        assert retry.read == 0
        assert retry.status == 2
        assert retry.status_forcelist == [429, 500, 502, 503, 504]
        assert list(retry.allowed_methods) == ["POST"]
        assert retry.backoff_factor == 1.0
        assert retry.respect_retry_after_header is False
        assert retry.raise_on_status is False


@pytest.mark.asyncio
@patch("agoras.platforms.instagram.client.build_upload_session")
@patch("agoras.platforms.instagram.client.GraphAPI")
async def test_create_resumable_video_rupload_failure_raises(mock_graph_api_class, mock_session_factory):
    """A non-retryable rupload status raises immediately."""
    mock_graph_api = MagicMock()
    mock_graph_api.post_object.return_value = {"id": "ig-container-1"}
    mock_graph_api_class.return_value = mock_graph_api

    mock_session = MagicMock()
    mock_session.post.return_value = MagicMock(status_code=400)
    mock_session.__enter__.return_value = mock_session
    mock_session_factory.return_value = mock_session

    client = InstagramAPIClient("access_token")
    await client.authenticate()
    client.wait_for_media_container = AsyncMock()

    with pytest.raises(Exception, match="Instagram resumable video upload failed: HTTP 400"):
        await client.create_resumable_video("ig-user-1", b"video-bytes")


@pytest.mark.asyncio
@patch("agoras.platforms.instagram.client.GraphAPI")
async def test_create_resumable_video_rejects_empty_bytes(mock_graph_api_class):
    """Empty local video files fail before rupload."""
    mock_graph_api = MagicMock()
    mock_graph_api.post_object.return_value = {"id": "ig-container-1"}
    mock_graph_api_class.return_value = mock_graph_api

    client = InstagramAPIClient("access_token")
    await client.authenticate()

    with pytest.raises(Exception, match="Video file is empty"):
        await client.create_resumable_video("ig-user-1", b"")


@patch("agoras.platforms.instagram.client.GraphAPI")
async def test_instagram_client_create_comment(mock_graph_api_class):
    """Test InstagramAPIClient create_comment targets the comments connection."""
    mock_graph_api = MagicMock()
    mock_graph_api.post_object.return_value = {"id": "comment-123"}
    mock_graph_api_class.return_value = mock_graph_api

    client = InstagramAPIClient("access_token")
    client.graph_api = mock_graph_api
    client._authenticated = True

    result = await client.create_comment("media-123", "A comment")

    assert result == "comment-123"
    mock_graph_api.post_object.assert_called_once_with(
        object_id="media-123", connection="comments", data={"message": "A comment"}
    )


@patch("agoras.platforms.instagram.client.GraphAPI")
async def test_instagram_client_delete_comment(mock_graph_api_class):
    """Test InstagramAPIClient delete_comment calls graph_api.delete_object."""
    mock_graph_api = MagicMock()
    mock_graph_api_class.return_value = mock_graph_api

    client = InstagramAPIClient("access_token")
    client.graph_api = mock_graph_api
    client._authenticated = True

    result = await client.delete_comment("comment-123")

    assert result == "comment-123"
    mock_graph_api.delete_object.assert_called_once_with(object_id="comment-123")


@patch("agoras.platforms.instagram.client.GraphAPI")
async def test_instagram_client_delete_comment_no_id(mock_graph_api_class):
    """Test InstagramAPIClient delete_comment raises when comment ID missing."""
    mock_graph_api = MagicMock()
    mock_graph_api_class.return_value = mock_graph_api

    client = InstagramAPIClient("access_token")
    client.graph_api = mock_graph_api
    client._authenticated = True

    with pytest.raises(Exception, match="Instagram comment ID is required"):
        await client.delete_comment(None)


@patch("agoras.platforms.instagram.client.GraphAPI")
async def test_instagram_client_delete_comment_permission_error(mock_graph_api_class):
    """Test InstagramAPIClient delete_comment surfaces permission errors."""
    mock_graph_api = MagicMock()
    mock_graph_api.delete_object.side_effect = Exception("Permission Error: Insufficient permissions")
    mock_graph_api_class.return_value = mock_graph_api

    client = InstagramAPIClient("access_token")
    client.graph_api = mock_graph_api
    client._authenticated = True

    with pytest.raises(Exception, match="Instagram comment delete"):
        await client.delete_comment("comment-123")


@patch("agoras.platforms.instagram.client.GraphAPI")
async def test_instagram_client_delete_comment_generic_error(mock_graph_api_class):
    """Test InstagramAPIClient delete_comment surfaces generic errors."""
    mock_graph_api = MagicMock()
    mock_graph_api.delete_object.side_effect = Exception("Graph returned an error")
    mock_graph_api_class.return_value = mock_graph_api

    client = InstagramAPIClient("access_token")
    client.graph_api = mock_graph_api
    client._authenticated = True

    with pytest.raises(Exception, match="Unable to delete comment comment-123"):
        await client.delete_comment("comment-123")


@patch("agoras.platforms.instagram.client.GraphAPI")
async def test_instagram_client_delete_media(mock_graph_api_class):
    """Test InstagramAPIClient delete_media calls graph_api.delete_object."""
    mock_graph_api = MagicMock()
    mock_graph_api_class.return_value = mock_graph_api

    client = InstagramAPIClient("access_token")
    client.graph_api = mock_graph_api
    client._authenticated = True

    result = await client.delete_media("media-123")

    assert result == "media-123"
    mock_graph_api.delete_object.assert_called_once_with(object_id="media-123")


@patch("agoras.platforms.instagram.client.GraphAPI")
async def test_instagram_client_delete_media_no_id(mock_graph_api_class):
    """Test InstagramAPIClient delete_media raises when media ID missing."""
    mock_graph_api = MagicMock()
    mock_graph_api_class.return_value = mock_graph_api

    client = InstagramAPIClient("access_token")
    client.graph_api = mock_graph_api
    client._authenticated = True

    with pytest.raises(Exception, match="Instagram media ID is required"):
        await client.delete_media(None)


@patch("agoras.platforms.instagram.client.GraphAPI")
async def test_instagram_client_delete_media_permission_error(mock_graph_api_class):
    """Test InstagramAPIClient delete_media surfaces permission errors."""
    mock_graph_api = MagicMock()
    mock_graph_api.delete_object.side_effect = Exception("Permission Error: Insufficient permissions")
    mock_graph_api_class.return_value = mock_graph_api

    client = InstagramAPIClient("access_token")
    client.graph_api = mock_graph_api
    client._authenticated = True

    with pytest.raises(Exception, match="Instagram media delete"):
        await client.delete_media("media-123")


@patch("agoras.platforms.instagram.client.GraphAPI")
async def test_instagram_client_delete_media_generic_error(mock_graph_api_class):
    """Test InstagramAPIClient delete_media surfaces generic errors."""
    mock_graph_api = MagicMock()
    mock_graph_api.delete_object.side_effect = Exception("Graph returned an error")
    mock_graph_api_class.return_value = mock_graph_api

    client = InstagramAPIClient("access_token")
    client.graph_api = mock_graph_api
    client._authenticated = True

    with pytest.raises(Exception, match="Unable to delete media media-123"):
        await client.delete_media("media-123")


@patch("agoras.platforms.instagram.client.GraphAPI")
async def test_instagram_client_create_comment_missing_id_raises(mock_graph_api_class):
    """Test InstagramAPIClient create_comment raises when response lacks an id."""
    mock_graph_api = MagicMock()
    mock_graph_api.post_object.return_value = {}
    mock_graph_api_class.return_value = mock_graph_api

    client = InstagramAPIClient("access_token")
    client.graph_api = mock_graph_api
    client._authenticated = True

    with pytest.raises(Exception, match="Invalid response from Instagram API: missing comment id"):
        await client.create_comment("media-123", "A comment")
