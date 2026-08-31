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

from agoras.platforms.linkedin import LinkedIn
from agoras.platforms.linkedin.api import LinkedInAPI

from .wrapper_test_helpers import (
    LINKEDIN_KWARGS,
    configure_linkedin_auth_mock,
)

# LinkedIn Wrapper Tests


@pytest.mark.asyncio
@patch("agoras.platforms.linkedin.wrapper.LinkedInAPI")
@patch("agoras.platforms.linkedin.auth.LinkedInAuthManager")
async def test_linkedin_initialize_client(mock_auth_manager_class, mock_api_class):
    """Test LinkedIn _initialize_client extracts config and creates API."""
    configure_linkedin_auth_mock(mock_auth_manager_class, access_token="test_token")
    mock_api = MagicMock()
    mock_api.authenticate = AsyncMock()
    mock_api_class.return_value = mock_api

    linkedin = LinkedIn(**{**LINKEDIN_KWARGS, "linkedin_access_token": "test_token"})

    await linkedin._initialize_client()

    assert linkedin.linkedin_access_token == "test_token"
    assert linkedin.api is mock_api
    mock_api.authenticate.assert_called_once()


@pytest.mark.asyncio
@patch("agoras.platforms.linkedin.auth.LinkedInAuthManager._load_credentials_from_storage", return_value=False)
async def test_linkedin_initialize_client_missing_credentials(mock_load_credentials):
    """Test LinkedIn _initialize_client raises exception without credentials."""
    linkedin = LinkedIn()

    with pytest.raises(Exception, match="Not authenticated"):
        await linkedin._initialize_client()


@pytest.mark.asyncio
@patch("agoras.platforms.linkedin.wrapper.LinkedInAPI")
@patch("agoras.platforms.linkedin.auth.LinkedInAuthManager")
async def test_linkedin_initialize_client_loads_from_storage(mock_auth_manager_class, mock_api_class):
    """Test LinkedIn _initialize_client loads credentials from storage when not provided."""
    # Mock auth manager that loads from storage
    mock_auth_manager = MagicMock()
    mock_auth_manager.user_id = "stored_user_id"
    mock_auth_manager.client_id = "stored_client_id"
    mock_auth_manager.client_secret = "stored_client_secret"
    mock_auth_manager.refresh_token = "stored_refresh_token"
    mock_auth_manager.access_token = "stored_access_token"
    mock_auth_manager._load_credentials_from_storage = MagicMock(return_value=True)
    mock_auth_manager.authenticate = AsyncMock(return_value=True)
    mock_auth_manager_class.return_value = mock_auth_manager

    # Mock API
    mock_api = MagicMock()
    mock_api.authenticate = AsyncMock()
    mock_api_class.return_value = mock_api

    # Create LinkedIn instance with NO credentials
    linkedin = LinkedIn()

    await linkedin._initialize_client()

    # Verify credentials were loaded from storage
    assert linkedin.linkedin_object_id == "stored_user_id"
    assert linkedin.linkedin_client_id == "stored_client_id"
    assert linkedin.linkedin_client_secret == "stored_client_secret"
    assert linkedin.linkedin_refresh_token == "stored_refresh_token"
    assert linkedin.linkedin_access_token == "stored_access_token"
    assert linkedin.api is mock_api
    mock_api.authenticate.assert_called_once()


@pytest.mark.asyncio
@patch("agoras.platforms.linkedin.wrapper.LinkedInAPI")
@patch("agoras.platforms.linkedin.auth.LinkedInAuthManager")
async def test_linkedin_initialize_client_loads_access_token_only_from_storage(mock_auth_manager_class, mock_api_class):
    """Test LinkedIn _initialize_client loads and works with stored access token only."""
    # Mock auth manager that loads from storage with NO refresh token
    mock_auth_manager = MagicMock()
    mock_auth_manager.user_id = "stored_user_id"
    mock_auth_manager.client_id = "stored_client_id"
    mock_auth_manager.client_secret = "stored_client_secret"
    mock_auth_manager.refresh_token = None
    mock_auth_manager.access_token = "stored_access_token"
    mock_auth_manager._load_credentials_from_storage = MagicMock(return_value=True)
    mock_auth_manager.authenticate = AsyncMock(return_value=True)
    mock_auth_manager_class.return_value = mock_auth_manager

    # Mock API
    mock_api = MagicMock()
    mock_api.authenticate = AsyncMock()
    mock_api_class.return_value = mock_api

    # Create LinkedIn instance with NO credentials
    linkedin = LinkedIn()

    await linkedin._initialize_client()

    # Verify credentials were loaded from storage
    assert linkedin.linkedin_object_id == "stored_user_id"
    assert linkedin.linkedin_client_id == "stored_client_id"
    assert linkedin.linkedin_client_secret == "stored_client_secret"
    assert linkedin.linkedin_refresh_token is None
    assert linkedin.linkedin_access_token == "stored_access_token"
    assert linkedin.api is mock_api
    mock_api.authenticate.assert_called_once()


@pytest.mark.asyncio
@patch("agoras.platforms.linkedin.auth.LinkedInAuthManager")
async def test_linkedin_authorize_credentials(mock_auth_manager_class):
    """Test LinkedIn authorize_credentials method."""
    mock_auth_manager = MagicMock()
    mock_auth_manager.authorize = AsyncMock(return_value="Authorization successful. Credentials stored securely.")
    mock_auth_manager_class.return_value = mock_auth_manager

    linkedin = LinkedIn(
        linkedin_object_id="user123", linkedin_client_id="client123", linkedin_client_secret="secret123"
    )

    with patch("builtins.print"):
        result = await linkedin.authorize_credentials()

    assert result is True
    mock_auth_manager.authorize.assert_called_once()


@pytest.mark.asyncio
@patch("agoras.platforms.linkedin.auth.LinkedInAuthManager")
async def test_linkedin_authorize_credentials_failure(mock_auth_manager_class):
    """Test LinkedIn authorize_credentials method when authorization fails."""
    mock_auth_manager = MagicMock()
    mock_auth_manager.authorize = AsyncMock(return_value=None)
    mock_auth_manager_class.return_value = mock_auth_manager

    linkedin = LinkedIn(
        linkedin_object_id="user123", linkedin_client_id="client123", linkedin_client_secret="secret123"
    )

    result = await linkedin.authorize_credentials()

    assert result is False
    mock_auth_manager.authorize.assert_called_once()


@pytest.mark.asyncio
@patch("agoras.platforms.linkedin.wrapper.LinkedInAPI")
@patch("agoras.platforms.linkedin.auth.LinkedInAuthManager")
async def test_linkedin_post(mock_auth_manager_class, mock_api_class):
    """Test LinkedIn post method."""
    configure_linkedin_auth_mock(mock_auth_manager_class)
    mock_api = MagicMock()
    mock_api.authenticate = AsyncMock()
    mock_api.post = AsyncMock(return_value="post-123")
    mock_api_class.return_value = mock_api

    linkedin = LinkedIn(**LINKEDIN_KWARGS)

    await linkedin._initialize_client()

    with patch.object(linkedin, "_output_status"):
        result = await linkedin.post("Hello LinkedIn", "http://link.com")

    assert result == "post-123"


@pytest.mark.asyncio
@patch("agoras.platforms.linkedin.wrapper.LinkedInAPI")
@patch("agoras.platforms.linkedin.auth.LinkedInAuthManager")
async def test_linkedin_post_with_local_image_path(mock_auth_manager_class, mock_api_class):
    """LinkedIn post uploads bytes from a local image path."""
    configure_linkedin_auth_mock(mock_auth_manager_class)
    mock_api = MagicMock()
    mock_api.authenticate = AsyncMock()
    mock_api.upload_image = AsyncMock(return_value="urn:li:image:local")
    mock_api.post = AsyncMock(return_value="post-local")
    mock_api_class.return_value = mock_api

    mock_media = MagicMock()
    mock_media.content = b"local_jpeg"
    mock_media.url = "/tmp/local.jpg"
    mock_media.cleanup = MagicMock()

    linkedin = LinkedIn(**LINKEDIN_KWARGS)

    await linkedin._initialize_client()

    with patch.object(linkedin, "download_images", new_callable=AsyncMock, return_value=[mock_media]):
        with patch.object(linkedin, "_output_status"):
            result = await linkedin.post("Hello LinkedIn", "", status_image_url_1="/tmp/local.jpg")

    assert result == "post-local"
    mock_api.upload_image.assert_called_once_with(b"local_jpeg")


@pytest.mark.asyncio
@patch("agoras.platforms.linkedin.wrapper.LinkedInAPI")
@patch("agoras.platforms.linkedin.auth.LinkedInAuthManager")
async def test_linkedin_like(mock_auth_manager_class, mock_api_class):
    """Test LinkedIn like method."""
    configure_linkedin_auth_mock(mock_auth_manager_class)
    mock_api = MagicMock()
    mock_api.authenticate = AsyncMock()
    mock_api.like = AsyncMock(return_value="post-123")
    mock_api_class.return_value = mock_api

    linkedin = LinkedIn(**LINKEDIN_KWARGS)

    await linkedin._initialize_client()

    with patch.object(linkedin, "_output_status"):
        result = await linkedin.like("post-123")

    assert result == "post-123"


@pytest.mark.asyncio
@patch("agoras.platforms.linkedin.wrapper.LinkedInAPI")
@patch("agoras.platforms.linkedin.auth.LinkedInAuthManager")
async def test_linkedin_share(mock_auth_manager_class, mock_api_class):
    """Test LinkedIn share method."""
    configure_linkedin_auth_mock(mock_auth_manager_class)
    mock_api = MagicMock()
    mock_api.authenticate = AsyncMock()
    mock_api.share = AsyncMock(return_value="share-456")
    mock_api_class.return_value = mock_api

    linkedin = LinkedIn(**LINKEDIN_KWARGS)

    await linkedin._initialize_client()

    with patch.object(linkedin, "_output_status"):
        result = await linkedin.share("post-123")

    assert result == "share-456"


@pytest.mark.asyncio
@patch("agoras.platforms.linkedin.wrapper.LinkedInAPI")
@patch("agoras.platforms.linkedin.auth.LinkedInAuthManager")
async def test_linkedin_delete(mock_auth_manager_class, mock_api_class):
    """Test LinkedIn delete method."""
    configure_linkedin_auth_mock(mock_auth_manager_class)
    mock_api = MagicMock()
    mock_api.authenticate = AsyncMock()
    mock_api.delete = AsyncMock(return_value="post-123")
    mock_api_class.return_value = mock_api

    linkedin = LinkedIn(**LINKEDIN_KWARGS)

    await linkedin._initialize_client()

    with patch.object(linkedin, "_output_status"):
        result = await linkedin.delete("post-123")

    assert result == "post-123"


@pytest.mark.asyncio
@patch("agoras.platforms.linkedin.wrapper.LinkedInAPI")
@patch("agoras.platforms.linkedin.auth.LinkedInAuthManager")
async def test_linkedin_reply(mock_auth_manager_class, mock_api_class):
    """Test LinkedIn reply method."""
    configure_linkedin_auth_mock(mock_auth_manager_class)
    mock_api = MagicMock()
    mock_api.authenticate = AsyncMock()
    mock_api.reply = AsyncMock(return_value="comment-123")
    mock_api_class.return_value = mock_api

    linkedin = LinkedIn(**LINKEDIN_KWARGS)

    await linkedin._initialize_client()

    with patch.object(linkedin, "_output_status"):
        result = await linkedin.reply("post-123", "A comment")

    assert result == "comment-123"
    mock_api.reply.assert_called_once_with("post-123", "A comment", image_ids=[])


@pytest.mark.asyncio
@patch("agoras.platforms.linkedin.wrapper.LinkedInAPI")
@patch("agoras.platforms.linkedin.auth.LinkedInAuthManager")
async def test_linkedin_reply_missing_post_id(mock_auth_manager_class, mock_api_class):
    """Test LinkedIn reply raises when post ID missing."""
    configure_linkedin_auth_mock(mock_auth_manager_class)
    mock_api = MagicMock()
    mock_api.authenticate = AsyncMock()
    mock_api.reply = AsyncMock(return_value="comment-123")
    mock_api_class.return_value = mock_api

    linkedin = LinkedIn(**LINKEDIN_KWARGS)

    await linkedin._initialize_client()

    with pytest.raises(Exception, match="LinkedIn post ID is required"):
        await linkedin.reply(None, "A comment")


@pytest.mark.asyncio
@patch("agoras.platforms.linkedin.wrapper.LinkedInAPI")
@patch("agoras.platforms.linkedin.auth.LinkedInAuthManager")
async def test_linkedin_reply_missing_text(mock_auth_manager_class, mock_api_class):
    """Test LinkedIn reply raises when reply text missing."""
    configure_linkedin_auth_mock(mock_auth_manager_class)
    mock_api = MagicMock()
    mock_api.authenticate = AsyncMock()
    mock_api.reply = AsyncMock(return_value="comment-123")
    mock_api_class.return_value = mock_api

    linkedin = LinkedIn(**LINKEDIN_KWARGS)

    await linkedin._initialize_client()

    with pytest.raises(Exception, match="LinkedIn reply text or image is required"):
        await linkedin.reply("post-123", None)


@pytest.mark.asyncio
@patch("agoras.platforms.linkedin.wrapper.LinkedInAPI")
@patch("agoras.platforms.linkedin.auth.LinkedInAuthManager")
async def test_linkedin_reply_with_image(mock_auth_manager_class, mock_api_class):
    """Test LinkedIn reply uploads an image and posts a comment with it."""
    configure_linkedin_auth_mock(mock_auth_manager_class)
    mock_api = MagicMock()
    mock_api.authenticate = AsyncMock()
    mock_api.upload_image = AsyncMock(return_value="urn:li:image:img1")
    mock_api.reply = AsyncMock(return_value="comment-123")
    mock_api_class.return_value = mock_api

    linkedin = LinkedIn(**LINKEDIN_KWARGS)
    await linkedin._initialize_client()

    mock_media = MagicMock()
    mock_media.content = b"jpeg"
    mock_media.url = "http://example.com/image.jpg"
    mock_media.cleanup = MagicMock()

    with (
        patch.object(linkedin, "download_images", new_callable=AsyncMock, return_value=[mock_media]),
        patch.object(linkedin, "_output_status"),
    ):
        result = await linkedin.reply("post-123", "A comment", status_image_url_1="http://example.com/image.jpg")

    assert result == "comment-123"
    mock_api.upload_image.assert_called_once_with(b"jpeg")
    mock_api.reply.assert_called_once_with("post-123", "A comment", image_ids=["urn:li:image:img1"])
    mock_media.cleanup.assert_called_once()


@pytest.mark.asyncio
@patch("agoras.platforms.linkedin.wrapper.LinkedInAPI")
@patch("agoras.platforms.linkedin.auth.LinkedInAuthManager")
async def test_linkedin_reply_with_video_raises(mock_auth_manager_class, mock_api_class):
    """Test LinkedIn reply raises when a video is provided."""
    configure_linkedin_auth_mock(mock_auth_manager_class)
    mock_api = MagicMock()
    mock_api.authenticate = AsyncMock()
    mock_api.reply = AsyncMock(return_value="comment-123")
    mock_api_class.return_value = mock_api

    linkedin = LinkedIn(**LINKEDIN_KWARGS)
    await linkedin._initialize_client()

    with pytest.raises(Exception, match="Video not supported in LinkedIn comments"):
        await linkedin.reply("post-123", "A comment", video_url="http://example.com/video.mp4")

    mock_api.reply.assert_not_called()


@pytest.mark.asyncio
@patch("agoras.platforms.linkedin.wrapper.LinkedInAPI")
@patch("agoras.platforms.linkedin.auth.LinkedInAuthManager")
async def test_linkedin_handle_reply_action(mock_auth_manager_class, mock_api_class):
    """Test LinkedIn _handle_reply_action uses the shared base handler with the post_id remap."""
    configure_linkedin_auth_mock(mock_auth_manager_class)
    mock_api = MagicMock()
    mock_api.authenticate = AsyncMock()
    mock_api.reply = AsyncMock(return_value="comment-123")
    mock_api_class.return_value = mock_api

    linkedin = LinkedIn(**{**LINKEDIN_KWARGS, "linkedin_post_id": "post-123", "status_text": "A comment"})

    await linkedin._initialize_client()

    with patch.object(linkedin, "reply", new_callable=AsyncMock) as mock_reply:
        await linkedin._handle_reply_action()
        mock_reply.assert_called_once_with(
            "post-123",
            "A comment",
            status_image_url_1=None,
            status_image_url_2=None,
            status_image_url_3=None,
            status_image_url_4=None,
            video_url=None,
        )


@pytest.mark.asyncio
@patch("agoras.platforms.linkedin.wrapper.LinkedInAPI")
@patch("agoras.platforms.linkedin.auth.LinkedInAuthManager")
async def test_linkedin_handle_reply_action_missing_post_id(mock_auth_manager_class, mock_api_class):
    """Test LinkedIn _handle_reply_action raises when post_id missing."""
    configure_linkedin_auth_mock(mock_auth_manager_class)
    mock_api = MagicMock()
    mock_api.authenticate = AsyncMock()
    mock_api_class.return_value = mock_api

    linkedin = LinkedIn(**{**LINKEDIN_KWARGS, "status_text": "A comment"})

    await linkedin._initialize_client()

    with pytest.raises(Exception, match="LinkedIn post ID is required"):
        await linkedin._handle_reply_action()


@pytest.mark.asyncio
@patch("agoras.platforms.linkedin.wrapper.LinkedInAPI")
@patch("agoras.platforms.linkedin.auth.LinkedInAuthManager")
async def test_linkedin_handle_reply_action_missing_text(mock_auth_manager_class, mock_api_class):
    """Test LinkedIn _handle_reply_action raises when text missing."""
    configure_linkedin_auth_mock(mock_auth_manager_class)
    mock_api = MagicMock()
    mock_api.authenticate = AsyncMock()
    mock_api_class.return_value = mock_api

    linkedin = LinkedIn(**{**LINKEDIN_KWARGS, "linkedin_post_id": "post-123"})

    await linkedin._initialize_client()

    with pytest.raises(Exception, match="LinkedIn reply text or image is required"):
        await linkedin._handle_reply_action()


@pytest.mark.asyncio
@patch("agoras.platforms.linkedin.wrapper.LinkedInAPI")
@patch("agoras.platforms.linkedin.auth.LinkedInAuthManager")
async def test_linkedin_video(mock_auth_manager_class, mock_api_class):
    """Test LinkedIn video method uploads and posts."""
    configure_linkedin_auth_mock(mock_auth_manager_class)
    mock_api = MagicMock()
    mock_api.authenticate = AsyncMock()
    mock_api.upload_video = AsyncMock(return_value="urn:li:video:123")
    mock_api.post = AsyncMock(return_value="post-789")
    mock_api_class.return_value = mock_api

    linkedin = LinkedIn(**LINKEDIN_KWARGS)
    await linkedin._initialize_client()

    mock_video = MagicMock()
    mock_video.content = b"video-bytes"
    mock_file_type = MagicMock()
    mock_file_type.mime = "video/mp4"
    mock_video.file_type = mock_file_type
    mock_video.cleanup = MagicMock()

    with (
        patch.object(linkedin, "download_video", new_callable=AsyncMock, return_value=mock_video),
        patch.object(linkedin, "_output_status"),
    ):
        result = await linkedin.video("Caption", "http://video.mp4", "Title")

    assert result == "post-789"
    mock_api.upload_video.assert_called_once_with(b"video-bytes")
    mock_api.post.assert_called_once_with(
        text="Caption",
        video_id="urn:li:video:123",
        video_title="Title",
    )
    mock_video.cleanup.assert_called_once()


@pytest.mark.asyncio
@patch("agoras.platforms.linkedin.wrapper.LinkedInAPI")
@patch("agoras.platforms.linkedin.auth.LinkedInAuthManager")
async def test_linkedin_disconnect(mock_auth_manager_class, mock_api_class):
    """Test LinkedIn disconnect method."""
    configure_linkedin_auth_mock(mock_auth_manager_class)
    mock_api = MagicMock()
    mock_api.authenticate = AsyncMock()
    mock_api.disconnect = AsyncMock()
    mock_api_class.return_value = mock_api

    linkedin = LinkedIn(**LINKEDIN_KWARGS)

    await linkedin._initialize_client()
    await linkedin.disconnect()

    mock_api.disconnect.assert_called_once()


@pytest.mark.asyncio
@patch("agoras.platforms.linkedin.wrapper.LinkedInAPI")
@patch("agoras.platforms.linkedin.auth.LinkedInAuthManager")
async def test_linkedin_delete_reply(mock_auth_manager_class, mock_api_class):
    """Test LinkedIn delete_reply deletes a comment with the parent post URN."""
    configure_linkedin_auth_mock(mock_auth_manager_class)
    mock_api = MagicMock()
    mock_api.authenticate = AsyncMock()
    mock_api.delete_reply = AsyncMock(return_value="comment-123")
    mock_api_class.return_value = mock_api

    linkedin = LinkedIn(**{**LINKEDIN_KWARGS, "linkedin_parent_post_id": "urn:li:ugcPost:123"})
    await linkedin._initialize_client()

    with patch.object(linkedin, "_output_status"):
        result = await linkedin.delete_reply("comment-123")

    assert result == "comment-123"
    mock_api.delete_reply.assert_called_once_with(comment_id="comment-123", parent_post_id="urn:li:ugcPost:123")


@pytest.mark.asyncio
@patch("agoras.platforms.linkedin.wrapper.LinkedInAPI")
@patch("agoras.platforms.linkedin.auth.LinkedInAuthManager")
async def test_linkedin_get_post(mock_auth_manager_class, mock_api_class):
    """Test LinkedIn get_post returns normalized content."""
    configure_linkedin_auth_mock(mock_auth_manager_class)
    mock_api = MagicMock()
    mock_api.authenticate = AsyncMock()
    mock_api.get_post = AsyncMock(
        return_value={
            "id": "urn:li:ugcPost:123",
            "commentary": "Hello LinkedIn",
            "author": "urn:li:person:1",
            "createdAt": 1700000000000,
        }
    )
    mock_api_class.return_value = mock_api

    linkedin = LinkedIn(**LINKEDIN_KWARGS)
    await linkedin._initialize_client()

    with patch.object(linkedin, "_output_content") as mock_out:
        result = await linkedin.get_post("urn:li:ugcPost:123")

    assert result["id"] == "urn:li:ugcPost:123"
    assert result["text"] == "Hello LinkedIn"
    assert result["author"]["id"] == "urn:li:person:1"
    mock_api.get_post.assert_called_once_with("urn:li:ugcPost:123")
    mock_out.assert_called_once()


@pytest.mark.asyncio
@patch("agoras.platforms.linkedin.wrapper.LinkedInAPI")
@patch("agoras.platforms.linkedin.auth.LinkedInAuthManager")
async def test_linkedin_get_post_resolves_media(mock_auth_manager_class, mock_api_class):
    """Test LinkedIn get_post resolves media URNs to normalized URLs."""
    configure_linkedin_auth_mock(mock_auth_manager_class)
    mock_api = MagicMock()
    mock_api.authenticate = AsyncMock()
    mock_api.get_post = AsyncMock(
        return_value={
            "id": "urn:li:ugcPost:123",
            "commentary": "Hello LinkedIn",
            "author": "urn:li:person:1",
            "createdAt": 1700000000000,
            "content": {
                "media": {"id": "urn:li:image:img1"},
            },
        }
    )
    mock_api.get_media = AsyncMock(return_value={"downloadUrl": "https://example.com/img1.jpg"})
    mock_api_class.return_value = mock_api

    linkedin = LinkedIn(**LINKEDIN_KWARGS)
    await linkedin._initialize_client()

    with patch.object(linkedin, "_output_content"):
        result = await linkedin.get_post("urn:li:ugcPost:123")

    assert result["media"] == [{"type": "image", "url": "https://example.com/img1.jpg"}]
    mock_api.get_media.assert_called_once_with("urn:li:image:img1")


@pytest.mark.asyncio
@patch("agoras.platforms.linkedin.wrapper.LinkedInAPI")
@patch("agoras.platforms.linkedin.auth.LinkedInAuthManager")
async def test_linkedin_get_post_media_resolution_failure_skipped(mock_auth_manager_class, mock_api_class):
    """Test LinkedIn get_post skips media whose URN cannot be resolved."""
    configure_linkedin_auth_mock(mock_auth_manager_class)
    mock_api = MagicMock()
    mock_api.authenticate = AsyncMock()
    mock_api.get_post = AsyncMock(
        return_value={
            "id": "urn:li:ugcPost:123",
            "commentary": "Hello LinkedIn",
            "content": {
                "multiImage": {"images": [{"id": "urn:li:image:img1"}, {"id": "urn:li:image:img2"}]},
            },
        }
    )
    mock_api.get_media = AsyncMock(side_effect=Exception("media not found"))
    mock_api_class.return_value = mock_api

    linkedin = LinkedIn(**LINKEDIN_KWARGS)
    await linkedin._initialize_client()

    with patch.object(linkedin, "_output_content"):
        result = await linkedin.get_post("urn:li:ugcPost:123")

    assert result["media"] == []


@pytest.mark.asyncio
@patch("agoras.platforms.linkedin.wrapper.LinkedInAPI")
@patch("agoras.platforms.linkedin.auth.LinkedInAuthManager")
async def test_linkedin_get_reply(mock_auth_manager_class, mock_api_class):
    """Test LinkedIn get_reply reads comment with parent URN."""
    configure_linkedin_auth_mock(mock_auth_manager_class)
    mock_api = MagicMock()
    mock_api.authenticate = AsyncMock()
    mock_api.get_reply = AsyncMock(
        return_value={
            "id": "comment-123",
            "message": {"text": "A comment"},
            "actor": "urn:li:person:1",
            "created": 1700000000000,
        }
    )
    mock_api_class.return_value = mock_api

    linkedin = LinkedIn(**{**LINKEDIN_KWARGS, "linkedin_parent_post_id": "urn:li:ugcPost:123"})
    await linkedin._initialize_client()

    with patch.object(linkedin, "_output_content"):
        result = await linkedin.get_reply("comment-123")

    assert result["id"] == "comment-123"
    assert result["text"] == "A comment"
    mock_api.get_reply.assert_called_once_with(comment_id="comment-123", parent_post_id="urn:li:ugcPost:123")
    assert result["metadata"]["parent_post_id"] == "urn:li:ugcPost:123"


@pytest.mark.asyncio
@patch("agoras.platforms.linkedin.wrapper.LinkedInAPI")
@patch("agoras.platforms.linkedin.auth.LinkedInAuthManager")
async def test_linkedin_get_reply_missing_parent_post_id(mock_auth_manager_class, mock_api_class):
    """Test LinkedIn get_reply raises when parent post ID missing."""
    configure_linkedin_auth_mock(mock_auth_manager_class)
    mock_api = MagicMock()
    mock_api.authenticate = AsyncMock()
    mock_api_class.return_value = mock_api

    linkedin = LinkedIn(**LINKEDIN_KWARGS)
    await linkedin._initialize_client()

    with pytest.raises(Exception, match="LinkedIn parent post ID is required"):
        await linkedin.get_reply("comment-123")


@pytest.mark.asyncio
@patch("agoras.platforms.linkedin.wrapper.LinkedInAPI")
@patch("agoras.platforms.linkedin.auth.LinkedInAuthManager")
async def test_linkedin_delete_reply_no_post_id(mock_auth_manager_class, mock_api_class):
    """Test LinkedIn delete_reply raises when comment ID missing."""
    configure_linkedin_auth_mock(mock_auth_manager_class)
    mock_api = MagicMock()
    mock_api.authenticate = AsyncMock()
    mock_api_class.return_value = mock_api

    linkedin = LinkedIn(**{**LINKEDIN_KWARGS, "linkedin_parent_post_id": "urn:li:ugcPost:123"})
    await linkedin._initialize_client()

    with pytest.raises(Exception, match="LinkedIn comment ID is required"):
        await linkedin.delete_reply(None)


@pytest.mark.asyncio
@patch("agoras.platforms.linkedin.wrapper.LinkedInAPI")
@patch("agoras.platforms.linkedin.auth.LinkedInAuthManager")
async def test_linkedin_delete_reply_missing_parent_post_id(mock_auth_manager_class, mock_api_class):
    """Test LinkedIn delete_reply raises when parent post ID missing."""
    configure_linkedin_auth_mock(mock_auth_manager_class)
    mock_api = MagicMock()
    mock_api.authenticate = AsyncMock()
    mock_api_class.return_value = mock_api

    linkedin = LinkedIn(**LINKEDIN_KWARGS)
    await linkedin._initialize_client()

    with pytest.raises(Exception, match="LinkedIn parent post ID is required"):
        await linkedin.delete_reply("comment-123")


# LinkedIn API Tests


def test_linkedin_api_class_exists():
    """Test LinkedInAPI class exists."""
    assert LinkedInAPI is not None
