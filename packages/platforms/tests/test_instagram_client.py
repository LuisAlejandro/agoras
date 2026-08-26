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
@patch("agoras.platforms.instagram.client.requests.post")
@patch("agoras.platforms.instagram.client.GraphAPI")
async def test_create_resumable_video_inits_and_uploads_bytes(mock_graph_api_class, mock_requests_post):
    """Resumable init omits video_url and POSTs bytes to rupload.facebook.com."""
    mock_graph_api = MagicMock()
    mock_graph_api.post_object.return_value = {
        "id": "ig-container-1",
        "uri": "https://rupload.facebook.com/ig-api-upload/v21.0/ig-container-1",
    }
    mock_graph_api_class.return_value = mock_graph_api
    mock_requests_post.return_value = MagicMock(status_code=200)

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

    upload_call = mock_requests_post.call_args
    assert upload_call.args[0] == "https://rupload.facebook.com/ig-api-upload/v21.0/ig-container-1"
    assert upload_call.kwargs["data"] == b"video-bytes"
    assert upload_call.kwargs["headers"]["Authorization"] == "OAuth access_token"
    assert upload_call.kwargs["headers"]["offset"] == "0"
    assert upload_call.kwargs["headers"]["file_size"] == str(len(b"video-bytes"))
    client.wait_for_media_container.assert_awaited_once_with("ig-container-1")


@pytest.mark.asyncio
@patch("agoras.platforms.instagram.client.requests.post")
@patch("agoras.platforms.instagram.client.GraphAPI")
async def test_create_resumable_video_retries_rupload_5xx(mock_graph_api_class, mock_requests_post):
    """rupload POST retries 5xx then succeeds."""
    mock_graph_api = MagicMock()
    mock_graph_api.post_object.return_value = {"id": "ig-container-1"}
    mock_graph_api_class.return_value = mock_graph_api
    mock_requests_post.side_effect = [
        MagicMock(status_code=503),
        MagicMock(status_code=200),
    ]

    client = InstagramAPIClient("access_token")
    await client.authenticate()
    client.wait_for_media_container = AsyncMock()

    with patch("agoras.platforms.instagram.client.time.sleep"):
        result = await client.create_resumable_video("ig-user-1", b"video-bytes")

    assert result == "ig-container-1"
    assert mock_requests_post.call_count == 2
    fallback_url = mock_requests_post.call_args.args[0]
    assert fallback_url == "https://rupload.facebook.com/ig-api-upload/v21.0/ig-container-1"


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
