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

from unittest.mock import MagicMock, patch

import pytest

from agoras.platforms.tiktok.client import TikTokAPIClient


def test_file_upload_chunk_params_single_chunk():
    """Videos up to 64MB upload as one chunk."""
    size = 5 * 1024 * 1024
    chunk_size, total = TikTokAPIClient._file_upload_chunk_params(size)
    assert chunk_size == size
    assert total == 1


def test_file_upload_chunk_params_multi_chunk():
    """Videos over 64MB use 10MB chunks with ceil total_chunk_count."""
    size = 103_107_045
    chunk_size, total = TikTokAPIClient._file_upload_chunk_params(size)
    assert chunk_size == TikTokAPIClient._FILE_UPLOAD_CHUNK_SIZE
    assert total == (size + chunk_size - 1) // chunk_size


def test_file_upload_chunk_params_last_chunk_fits():
    """Non-aligned sizes over 64MB must not produce a last chunk larger than chunk_size."""
    size = TikTokAPIClient._FILE_UPLOAD_SINGLE_CHUNK_MAX + 1
    chunk_size, total = TikTokAPIClient._file_upload_chunk_params(size)
    payload = b"z" * size
    chunks = list(TikTokAPIClient._iter_file_upload_chunks(payload, chunk_size, total))
    assert total == (size + chunk_size - 1) // chunk_size
    assert all(len(chunk) <= chunk_size for _, _, chunk in chunks)
    assert sum(len(chunk) for _, _, chunk in chunks) == size


@patch("agoras.platforms.tiktok.client._build_upload_session")
@patch("agoras.platforms.tiktok.client.requests.post")
def test_upload_video_file_single_chunk(mock_post, mock_session_factory):
    """FILE_UPLOAD init + one PUT for a small local video."""
    client = TikTokAPIClient(access_token="token")
    file_content = b"x" * (5 * 1024 * 1024)

    init_response = MagicMock()
    init_response.json.return_value = {
        "data": {
            "publish_id": "pub-file-123",
            "upload_url": "https://open-upload.tiktokapis.com/video/?upload_id=1",
        },
        "error": {"code": "ok", "message": ""},
    }
    mock_post.return_value = init_response

    mock_session = MagicMock()
    put_response = MagicMock()
    put_response.status_code = 201
    mock_session.put.return_value = put_response
    mock_session.__enter__.return_value = mock_session
    mock_session_factory.return_value = mock_session

    result = client.upload_video_file(
        file_content=file_content,
        title="Local clip",
        privacy_status="SELF_ONLY",
    )

    assert result["data"]["publish_id"] == "pub-file-123"
    mock_post.assert_called_once()
    init_payload = mock_post.call_args.kwargs["data"]
    assert '"source": "FILE_UPLOAD"' in init_payload
    assert f'"video_size": {len(file_content)}' in init_payload
    assert f'"chunk_size": {len(file_content)}' in init_payload
    assert '"total_chunk_count": 1' in init_payload

    mock_session.put.assert_called_once()
    put_kwargs = mock_session.put.call_args.kwargs
    assert put_kwargs["headers"]["Content-Range"] == f"bytes 0-{len(file_content) - 1}/{len(file_content)}"
    assert put_kwargs["headers"]["Content-Type"] == "video/mp4"
    assert put_kwargs["data"] == file_content


@patch("agoras.platforms.tiktok.client._build_upload_session")
@patch("agoras.platforms.tiktok.client.requests.post")
def test_upload_video_file_multi_chunk(mock_post, mock_session_factory):
    """FILE_UPLOAD sends sequential PUTs for videos larger than 64MB."""
    client = TikTokAPIClient(access_token="token")
    chunk_size = TikTokAPIClient._FILE_UPLOAD_CHUNK_SIZE
    file_content = b"y" * (TikTokAPIClient._FILE_UPLOAD_SINGLE_CHUNK_MAX + chunk_size)

    init_response = MagicMock()
    init_response.json.return_value = {
        "data": {
            "publish_id": "pub-file-big",
            "upload_url": "https://open-upload.tiktokapis.com/video/?upload_id=2",
        },
        "error": {"code": "ok", "message": ""},
    }
    mock_post.return_value = init_response

    mock_session = MagicMock()
    put_response = MagicMock()
    put_response.status_code = 206
    mock_session.put.return_value = put_response
    mock_session.__enter__.return_value = mock_session
    mock_session_factory.return_value = mock_session

    result = client.upload_video_file(
        file_content=file_content,
        title="Big clip",
        privacy_status="PUBLIC_TO_EVERYONE",
    )

    assert result["data"]["publish_id"] == "pub-file-big"
    expected_chunk_size, expected_chunks = TikTokAPIClient._file_upload_chunk_params(len(file_content))
    assert expected_chunk_size == chunk_size
    assert mock_session.put.call_count == expected_chunks

    chunks = list(
        TikTokAPIClient._iter_file_upload_chunks(file_content, expected_chunk_size, expected_chunks)
    )
    for (start, end, chunk_bytes), put_call in zip(chunks, mock_session.put.call_args_list, strict=True):
        assert put_call.kwargs["headers"]["Content-Range"] == f"bytes {start}-{end}/{len(file_content)}"
        assert put_call.kwargs["data"] == chunk_bytes


@patch("agoras.platforms.tiktok.client.requests.post")
def test_upload_video_file_requires_token(mock_post):
    """FILE_UPLOAD rejects missing access token."""
    client = TikTokAPIClient()
    with pytest.raises(Exception, match="No access token"):
        client.upload_video_file(b"video", "title", "SELF_ONLY")
    mock_post.assert_not_called()


@patch("agoras.platforms.tiktok.client._build_upload_session")
@patch("agoras.platforms.tiktok.client.requests.post")
def test_upload_video_file_put_failure(mock_post, mock_session_factory):
    """FILE_UPLOAD raises when a chunk PUT returns a non-success status."""
    client = TikTokAPIClient(access_token="token")
    init_response = MagicMock()
    init_response.json.return_value = {
        "data": {
            "publish_id": "pub-fail",
            "upload_url": "https://open-upload.tiktokapis.com/video/?upload_id=3",
        },
        "error": {"code": "ok", "message": ""},
    }
    mock_post.return_value = init_response

    mock_session = MagicMock()
    put_response = MagicMock()
    put_response.status_code = 400
    mock_session.put.return_value = put_response
    mock_session.__enter__.return_value = mock_session
    mock_session_factory.return_value = mock_session

    with pytest.raises(Exception, match="Error uploading video chunk: HTTP 400"):
        client.upload_video_file(b"video-bytes", "title", "SELF_ONLY")


def test_upload_video_file_empty_content():
    """FILE_UPLOAD rejects empty video bytes before init."""
    client = TikTokAPIClient(access_token="token")
    with pytest.raises(Exception, match="Video file is empty"):
        client.upload_video_file(b"", "title", "SELF_ONLY")


def test_iter_file_upload_chunks_uses_memoryview():
    """Chunk iteration exposes a memoryview over the original buffer, not a copy."""
    payload = b"abcdefghij"
    chunks = list(TikTokAPIClient._iter_file_upload_chunks(payload, 4, 3))
    assert all(isinstance(chunk, memoryview) for _, _, chunk in chunks)
    assert b"".join(bytes(chunk) for _, _, chunk in chunks) == payload


def test_upload_session_retry_config():
    """The upload session pins the previous retry contract."""
    from agoras.platforms.tiktok.client import _build_upload_session

    with _build_upload_session(3, {429, 500, 502, 503, 504}) as session:
        adapter = session.get_adapter("https://")
        retry = adapter.max_retries
        assert retry.total == 2
        assert retry.connect == 0
        assert retry.read == 0
        assert retry.status == 2
        assert retry.status_forcelist == [429, 500, 502, 503, 504]
        assert list(retry.allowed_methods) == ["PUT"]
        assert retry.backoff_factor == 1.0
        assert retry.respect_retry_after_header is False


@patch("agoras.platforms.tiktok.client._build_upload_session")
@patch("agoras.platforms.tiktok.client.requests.post")
def test_upload_video_file_put_retry_exhaustion_raises(mock_post, mock_session_factory):
    """Exhausted status retries surface the last HTTP status."""
    from urllib3.exceptions import MaxRetryError

    client = TikTokAPIClient(access_token="token")
    init_response = MagicMock()
    init_response.json.return_value = {
        "data": {
            "publish_id": "pub-retry",
            "upload_url": "https://open-upload.tiktokapis.com/video/?upload_id=4",
        },
        "error": {"code": "ok", "message": ""},
    }
    mock_post.return_value = init_response

    mock_session = MagicMock()
    exhausted = MaxRetryError(MagicMock(), "too many retries")
    exhausted.response = MagicMock(status_code=503)
    mock_session.put.side_effect = exhausted
    mock_session.__enter__.return_value = mock_session
    mock_session_factory.return_value = mock_session

    with pytest.raises(Exception, match="Error uploading video chunk: HTTP 503"):
        client.upload_video_file(b"video-bytes", "title", "SELF_ONLY")


@patch("agoras.platforms.tiktok.client.requests.put")
@patch("agoras.platforms.tiktok.client.requests.post")
def test_upload_video_pull_from_url_unchanged(mock_post, mock_put):
    """PULL_FROM_URL path remains separate from FILE_UPLOAD."""
    client = TikTokAPIClient(access_token="token")
    init_response = MagicMock()
    init_response.json.return_value = {
        "data": {"publish_id": "pub-url"},
        "error": {"code": "ok", "message": ""},
    }
    mock_post.return_value = init_response

    result = client.upload_video(
        video_url="https://example.com/video.mp4",
        title="Remote",
        privacy_status="SELF_ONLY",
    )

    assert result["data"]["publish_id"] == "pub-url"
    init_payload = mock_post.call_args.kwargs["data"]
    assert '"source": "PULL_FROM_URL"' in init_payload
    assert "https://example.com/video.mp4" in init_payload
    mock_put.assert_not_called()
