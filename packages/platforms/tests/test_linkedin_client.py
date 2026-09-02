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

from agoras.platforms.linkedin.client import LinkedInAPIClient

# Initialization Tests


def test_linkedin_client_init():
    """Test LinkedInAPIClient initialization."""
    client = LinkedInAPIClient("access_token")

    assert client.access_token == "access_token"
    assert client.restli_client is None
    assert client.api_version == "202503"
    assert client._authenticated is False


# Authentication Tests


@pytest.mark.asyncio
@patch("agoras.platforms.linkedin.client.RestliClient")
async def test_linkedin_client_authenticate(mock_restli_class):
    """Test LinkedInAPIClient authenticate method."""
    mock_restli = MagicMock()
    mock_restli_class.return_value = mock_restli

    client = LinkedInAPIClient("access_token")
    result = await client.authenticate()

    assert result is True
    assert client._authenticated is True
    assert client.restli_client is mock_restli
    mock_restli_class.assert_called_once()


@pytest.mark.asyncio
async def test_linkedin_client_authenticate_already_authenticated():
    """Test LinkedInAPIClient authenticate when already authenticated."""
    client = LinkedInAPIClient("access_token")
    client._authenticated = True

    result = await client.authenticate()

    assert result is True


@pytest.mark.asyncio
async def test_linkedin_client_authenticate_missing_token():
    """Test LinkedInAPIClient authenticate raises error without token."""
    client = LinkedInAPIClient("")

    with pytest.raises(Exception, match="access token is required"):
        await client.authenticate()


@pytest.mark.asyncio
@patch("agoras.platforms.linkedin.client.RestliClient")
async def test_linkedin_client_authenticate_failure(mock_restli_class):
    """Test LinkedInAPIClient authenticate handles RestliClient errors."""
    mock_restli_class.side_effect = Exception("RestliClient error")

    client = LinkedInAPIClient("access_token")

    with pytest.raises(Exception, match="authentication failed"):
        await client.authenticate()


# Disconnect Tests


def test_linkedin_client_disconnect():
    """Test LinkedInAPIClient disconnect method."""
    client = LinkedInAPIClient("access_token")
    mock_restli = MagicMock()
    client.restli_client = mock_restli
    client._authenticated = True

    client.disconnect()

    assert client.restli_client is None
    assert client._authenticated is False


# Upload Image Tests


@pytest.mark.asyncio
@patch("agoras.platforms.linkedin.client.requests.put")
@patch("agoras.platforms.linkedin.client.asyncio.to_thread")
async def test_linkedin_client_upload_image(mock_to_thread, mock_requests_put):
    """Test LinkedInAPIClient upload_image method."""
    client = LinkedInAPIClient("access_token")
    mock_restli = MagicMock()
    mock_request = MagicMock()
    mock_response = MagicMock()
    mock_response.json.return_value = {"value": {"uploadUrl": "http://upload.url", "image": "urn:li:image:123"}}
    mock_request.response = mock_response
    mock_restli.action.return_value = mock_request
    client.restli_client = mock_restli
    client._authenticated = True

    mock_upload_response = MagicMock()
    mock_upload_response.status_code = 201
    mock_requests_put.return_value = mock_upload_response

    # Mock asyncio.to_thread to execute the sync function
    def execute_sync(func):
        return func()

    mock_to_thread.side_effect = execute_sync

    result = await client.upload_image(b"image_content", "urn:li:person:123")

    assert result == "urn:li:image:123"
    mock_restli.action.assert_called_once()
    mock_requests_put.assert_called_once()


@pytest.mark.asyncio
@patch("agoras.platforms.linkedin.client.asyncio.to_thread")
async def test_linkedin_client_upload_image_not_initialized(mock_to_thread):
    """Test LinkedInAPIClient upload_image raises error when not initialized."""
    client = LinkedInAPIClient("access_token")

    def execute_sync(func):
        return func()

    mock_to_thread.side_effect = execute_sync

    with pytest.raises(Exception, match="RestliClient not initialized"):
        await client.upload_image(b"content", "urn:li:person:123")


@pytest.mark.asyncio
@patch("agoras.platforms.linkedin.client.requests.put")
@patch("agoras.platforms.linkedin.client.asyncio.to_thread")
async def test_linkedin_client_upload_image_upload_failure(mock_to_thread, mock_requests_put):
    """Test LinkedInAPIClient upload_image handles upload failure."""
    client = LinkedInAPIClient("access_token")
    mock_restli = MagicMock()
    mock_request = MagicMock()
    mock_response = MagicMock()
    mock_response.json.return_value = {"value": {"uploadUrl": "http://upload.url", "image": "urn:li:image:123"}}
    mock_request.response = mock_response
    mock_restli.action.return_value = mock_request
    client.restli_client = mock_restli
    client._authenticated = True

    mock_upload_response = MagicMock()
    mock_upload_response.status_code = 400  # Upload failed
    mock_requests_put.return_value = mock_upload_response

    def execute_sync(func):
        return func()

    mock_to_thread.side_effect = execute_sync

    with pytest.raises(Exception, match="Failed to upload image"):
        await client.upload_image(b"content", "urn:li:person:123")


# Upload Video Tests


@pytest.mark.asyncio
@patch("agoras.platforms.linkedin.client.requests.put")
@patch("agoras.platforms.linkedin.client.asyncio.to_thread")
async def test_linkedin_client_upload_video(mock_to_thread, mock_requests_put):
    """Test LinkedInAPIClient upload_video method."""
    client = LinkedInAPIClient("access_token")
    mock_restli = MagicMock()
    client.restli_client = mock_restli
    client._authenticated = True

    init_request = MagicMock()
    init_request.response.json.return_value = {
        "value": {
            "video": "urn:li:video:123",
            "uploadToken": "token",
            "uploadInstructions": [
                {
                    "uploadUrl": "http://upload.url",
                    "firstByte": 0,
                    "lastByte": 11,
                }
            ],
        }
    }
    finalize_response = MagicMock()
    finalize_response.status_code = 200
    finalize_response.text = ""
    status_request = MagicMock()
    status_request.response.json.return_value = {"status": "AVAILABLE"}
    mock_restli.action.return_value = init_request
    mock_restli.get.return_value = status_request

    mock_upload_response = MagicMock()
    mock_upload_response.status_code = 200
    mock_upload_response.headers = {"etag": "part-etag-1"}
    mock_requests_put.return_value = mock_upload_response

    def execute_sync(func):
        return func()

    mock_to_thread.side_effect = execute_sync

    with patch.object(client, "_post_restli_action", return_value=finalize_response):
        result = await client.upload_video(b"video-bytes!", "urn:li:person:123")

    assert result == "urn:li:video:123"
    mock_restli.action.assert_called_once()
    mock_requests_put.assert_called_once()


@pytest.mark.asyncio
@patch("agoras.platforms.linkedin.client.asyncio.to_thread")
async def test_linkedin_client_upload_video_finalize_empty_body(mock_to_thread):
    """finalizeUpload may return 200 with an empty body (not JSON)."""
    client = LinkedInAPIClient("access_token")
    mock_restli = MagicMock()
    mock_session = MagicMock()
    mock_restli.session = mock_session
    client.restli_client = mock_restli
    client._authenticated = True

    empty_response = MagicMock()
    empty_response.status_code = 200
    empty_response.text = ""
    mock_session.send.return_value = empty_response

    prepared = MagicMock()
    with patch(
        "agoras.platforms.linkedin.client.maybe_apply_query_tunneling_requests_with_body",
        return_value=prepared,
    ):
        response = client._post_restli_action(
            "/videos",
            "finalizeUpload",
            {"finalizeUploadRequest": {"video": "urn:li:video:1"}},
        )

    assert response.status_code == 200
    mock_session.send.assert_called_once_with(prepared)


@pytest.mark.asyncio
@patch("agoras.platforms.linkedin.client.asyncio.to_thread")
async def test_linkedin_client_upload_video_not_initialized(mock_to_thread):
    """Test LinkedInAPIClient upload_video raises error when not initialized."""
    client = LinkedInAPIClient("access_token")

    def execute_sync(func):
        return func()

    mock_to_thread.side_effect = execute_sync

    with pytest.raises(Exception, match="RestliClient not initialized"):
        await client.upload_video(b"content", "urn:li:person:123")


# Create Post Tests


@pytest.mark.asyncio
@patch("agoras.platforms.linkedin.client.asyncio.to_thread")
async def test_linkedin_client_create_post_text_only(mock_to_thread):
    """Test LinkedInAPIClient create_post with text only."""
    client = LinkedInAPIClient("access_token")
    mock_restli = MagicMock()
    mock_request = MagicMock()
    mock_request.entity_id = "post-123"
    mock_restli.create.return_value = mock_request
    client.restli_client = mock_restli
    client._authenticated = True

    def execute_sync(func):
        return func()

    mock_to_thread.side_effect = execute_sync

    result = await client.create_post("urn:li:person:123", "Test post")

    assert result == "post-123"
    mock_restli.create.assert_called_once()
    call_entity = mock_restli.create.call_args[1]["entity"]
    assert call_entity["author"] == "urn:li:person:123"
    assert call_entity["commentary"] == "Test post"


@pytest.mark.asyncio
@patch("agoras.platforms.linkedin.client.asyncio.to_thread")
async def test_linkedin_client_create_post_with_link(mock_to_thread):
    """Test LinkedInAPIClient create_post with link."""
    client = LinkedInAPIClient("access_token")
    mock_restli = MagicMock()
    mock_request = MagicMock()
    mock_request.entity_id = "post-123"
    mock_restli.create.return_value = mock_request
    client.restli_client = mock_restli
    client._authenticated = True

    def execute_sync(func):
        return func()

    mock_to_thread.side_effect = execute_sync

    result = await client.create_post(
        "urn:li:person:123",
        "Test post",
        link="http://link.com",
        link_title="Link Title",
        link_description="Link Description",
    )

    assert result == "post-123"
    call_entity = mock_restli.create.call_args[1]["entity"]
    assert "content" in call_entity
    assert call_entity["content"]["article"]["source"] == "http://link.com"
    assert call_entity["content"]["article"]["title"] == "Link Title"
    assert call_entity["content"]["article"]["description"] == "Link Description"


@pytest.mark.asyncio
@patch("agoras.platforms.linkedin.client.asyncio.to_thread")
async def test_linkedin_client_create_post_with_video(mock_to_thread):
    """Test LinkedInAPIClient create_post with video."""
    client = LinkedInAPIClient("access_token")
    mock_restli = MagicMock()
    mock_request = MagicMock()
    mock_request.entity_id = "post-123"
    mock_restli.create.return_value = mock_request
    client.restli_client = mock_restli
    client._authenticated = True

    def execute_sync(func):
        return func()

    mock_to_thread.side_effect = execute_sync

    result = await client.create_post(
        "urn:li:person:123",
        "Test post",
        video_id="urn:li:video:456",
        video_title="My Video",
    )

    assert result == "post-123"
    call_entity = mock_restli.create.call_args[1]["entity"]
    assert call_entity["content"]["media"]["id"] == "urn:li:video:456"
    assert call_entity["content"]["media"]["title"] == "My Video"


@pytest.mark.asyncio
@patch("agoras.platforms.linkedin.client.asyncio.to_thread")
async def test_linkedin_client_create_post_with_single_image(mock_to_thread):
    """Test LinkedInAPIClient create_post with single image."""
    client = LinkedInAPIClient("access_token")
    mock_restli = MagicMock()
    mock_request = MagicMock()
    mock_request.entity_id = "post-123"
    mock_restli.create.return_value = mock_request
    client.restli_client = mock_restli
    client._authenticated = True

    def execute_sync(func):
        return func()

    mock_to_thread.side_effect = execute_sync

    result = await client.create_post("urn:li:person:123", "Test post", image_ids=["image-123"])

    assert result == "post-123"
    call_entity = mock_restli.create.call_args[1]["entity"]
    assert call_entity["content"]["media"]["id"] == "image-123"


@pytest.mark.asyncio
@patch("agoras.platforms.linkedin.client.asyncio.to_thread")
async def test_linkedin_client_create_post_with_multiple_images(mock_to_thread):
    """Test LinkedInAPIClient create_post with multiple images."""
    client = LinkedInAPIClient("access_token")
    mock_restli = MagicMock()
    mock_request = MagicMock()
    mock_request.entity_id = "post-123"
    mock_restli.create.return_value = mock_request
    client.restli_client = mock_restli
    client._authenticated = True

    def execute_sync(func):
        return func()

    mock_to_thread.side_effect = execute_sync

    result = await client.create_post("urn:li:person:123", "Test post", image_ids=["img1", "img2", "img3"])

    assert result == "post-123"
    call_entity = mock_restli.create.call_args[1]["entity"]
    assert "multiImage" in call_entity["content"]
    assert len(call_entity["content"]["multiImage"]["images"]) == 3


@pytest.mark.asyncio
@patch("agoras.platforms.linkedin.client.asyncio.to_thread")
async def test_linkedin_client_create_post_not_initialized(mock_to_thread):
    """Test LinkedInAPIClient create_post raises error when not initialized."""
    client = LinkedInAPIClient("access_token")

    def execute_sync(func):
        return func()

    mock_to_thread.side_effect = execute_sync

    with pytest.raises(Exception, match="RestliClient not initialized"):
        await client.create_post("urn:li:person:123", "Test")


@pytest.mark.asyncio
@patch("agoras.platforms.linkedin.client.asyncio.to_thread")
async def test_linkedin_client_create_post_invalid_response(mock_to_thread):
    """Test LinkedInAPIClient create_post handles invalid response."""
    client = LinkedInAPIClient("access_token")
    mock_restli = MagicMock()
    mock_request = MagicMock()
    mock_request.entity_id = None  # Invalid response
    mock_restli.create.return_value = mock_request
    client.restli_client = mock_restli
    client._authenticated = True

    def execute_sync(func):
        return func()

    mock_to_thread.side_effect = execute_sync

    with pytest.raises(Exception, match="Invalid response from LinkedIn API"):
        await client.create_post("urn:li:person:123", "Test")


# Like Post Tests


@pytest.mark.asyncio
@patch("agoras.platforms.linkedin.client.asyncio.to_thread")
async def test_linkedin_client_like_post(mock_to_thread):
    """Test LinkedInAPIClient like_post method."""
    client = LinkedInAPIClient("access_token")
    mock_restli = MagicMock()
    mock_request = MagicMock()
    mock_request.status_code = 201
    mock_restli.create.return_value = mock_request
    client.restli_client = mock_restli
    client._authenticated = True

    def execute_sync(func):
        return func()

    mock_to_thread.side_effect = execute_sync

    result = await client.like_post("post-123", "urn:li:person:123")

    assert result == "post-123"
    mock_restli.create.assert_called_once()
    call_entity = mock_restli.create.call_args[1]["entity"]
    assert call_entity["actor"] == "urn:li:person:123"
    assert call_entity["object"] == "post-123"


@pytest.mark.asyncio
@patch("agoras.platforms.linkedin.client.asyncio.to_thread")
async def test_linkedin_client_like_post_failure(mock_to_thread):
    """Test LinkedInAPIClient like_post handles failure."""
    client = LinkedInAPIClient("access_token")
    mock_restli = MagicMock()
    mock_request = MagicMock()
    mock_request.status_code = 400  # Failure
    mock_restli.create.return_value = mock_request
    client.restli_client = mock_restli
    client._authenticated = True

    def execute_sync(func):
        return func()

    mock_to_thread.side_effect = execute_sync

    with pytest.raises(Exception, match="Unable to like post"):
        await client.like_post("post-123", "urn:li:person:123")


# Create Comment Tests


@pytest.mark.asyncio
@patch("agoras.platforms.linkedin.client.asyncio.to_thread")
async def test_linkedin_client_create_comment(mock_to_thread):
    """Test LinkedInAPIClient create_comment method."""
    client = LinkedInAPIClient("access_token")
    mock_restli = MagicMock()
    mock_request = MagicMock()
    mock_request.status_code = 201
    mock_request.entity_id = "comment-123"
    mock_restli.create.return_value = mock_request
    client.restli_client = mock_restli
    client._authenticated = True

    def execute_sync(func):
        return func()

    mock_to_thread.side_effect = execute_sync

    result = await client.create_comment("post-123", "urn:li:person:123", "A comment")

    assert result == "comment-123"
    mock_restli.create.assert_called_once()
    call_entity = mock_restli.create.call_args[1]["entity"]
    assert call_entity["actor"] == "urn:li:person:123"
    assert call_entity["object"] == "post-123"
    assert call_entity["comment"] == "A comment"


@pytest.mark.asyncio
@patch("agoras.platforms.linkedin.client.asyncio.to_thread")
async def test_linkedin_client_create_comment_with_image(mock_to_thread):
    """Test LinkedInAPIClient create_comment includes content[].entity.image."""
    client = LinkedInAPIClient("access_token")
    mock_restli = MagicMock()
    mock_request = MagicMock()
    mock_request.status_code = 201
    mock_request.entity_id = "comment-123"
    mock_restli.create.return_value = mock_request
    client.restli_client = mock_restli
    client._authenticated = True

    def execute_sync(func):
        return func()

    mock_to_thread.side_effect = execute_sync

    result = await client.create_comment(
        "post-123", "urn:li:person:123", "A comment", image_ids=["urn:li:image:img1", "urn:li:image:img2"]
    )

    assert result == "comment-123"
    call_entity = mock_restli.create.call_args[1]["entity"]
    assert call_entity["content"] == [
        {"entity": {"image": "urn:li:image:img1"}},
        {"entity": {"image": "urn:li:image:img2"}},
    ]


@pytest.mark.asyncio
@patch("agoras.platforms.linkedin.client.asyncio.to_thread")
async def test_linkedin_client_create_comment_encodes_post_id(mock_to_thread):
    """Test LinkedInAPIClient create_comment URL-encodes the post URN in the path."""
    client = LinkedInAPIClient("access_token")
    mock_restli = MagicMock()
    mock_request = MagicMock()
    mock_request.status_code = 201
    mock_request.entity_id = "comment-123"
    mock_restli.create.return_value = mock_request
    client.restli_client = mock_restli
    client._authenticated = True

    def execute_sync(func):
        return func()

    mock_to_thread.side_effect = execute_sync

    await client.create_comment("urn:li:ugcPost:123", "urn:li:person:123", "A comment")

    resource_path = mock_restli.create.call_args[1]["resource_path"]
    assert "ugcPost" in resource_path


@pytest.mark.asyncio
@patch("agoras.platforms.linkedin.client.asyncio.to_thread")
async def test_linkedin_client_create_comment_rejects_activity_urn(mock_to_thread):
    """Test create_comment rejects activity URNs with a clear error."""
    client = LinkedInAPIClient("access_token")
    client.restli_client = MagicMock()
    client._authenticated = True

    with pytest.raises(Exception, match="not an activity URN"):
        await client.create_comment("urn:li:activity:123", "urn:li:person:123", "A comment")


@pytest.mark.asyncio
@patch("agoras.platforms.linkedin.client.asyncio.to_thread")
async def test_linkedin_client_create_comment_failure(mock_to_thread):
    """Test LinkedInAPIClient create_comment handles failure."""
    client = LinkedInAPIClient("access_token")
    mock_restli = MagicMock()
    mock_request = MagicMock()
    mock_request.status_code = 400  # Failure
    mock_restli.create.return_value = mock_request
    client.restli_client = mock_restli
    client._authenticated = True

    def execute_sync(func):
        return func()

    mock_to_thread.side_effect = execute_sync

    with pytest.raises(Exception, match="Unable to comment on post"):
        await client.create_comment("post-123", "urn:li:person:123", "A comment")


@pytest.mark.asyncio
@patch("agoras.platforms.linkedin.client.asyncio.to_thread")
async def test_linkedin_client_create_comment_access_denied(mock_to_thread):
    """Test LinkedInAPIClient create_comment surfaces the Community Management API message."""
    client = LinkedInAPIClient("access_token")
    mock_restli = MagicMock()
    mock_request = MagicMock()
    mock_request.status_code = 403
    mock_response = MagicMock()
    mock_response.json.return_value = {"code": "ACCESS_DENIED", "message": "denied"}
    mock_request.response = mock_response
    mock_restli.create.return_value = mock_request
    client.restli_client = mock_restli
    client._authenticated = True

    def execute_sync(func):
        return func()

    mock_to_thread.side_effect = execute_sync

    with pytest.raises(Exception, match="Community Management API"):
        await client.create_comment("post-123", "urn:li:person:123", "A comment")


@pytest.mark.asyncio
@patch("agoras.platforms.linkedin.client.asyncio.to_thread")
async def test_linkedin_client_create_comment_invalid_response(mock_to_thread):
    """Test LinkedInAPIClient create_comment handles invalid response."""
    client = LinkedInAPIClient("access_token")
    mock_restli = MagicMock()
    mock_request = MagicMock()
    mock_request.status_code = 201
    mock_request.entity_id = None  # Invalid response
    mock_restli.create.return_value = mock_request
    client.restli_client = mock_restli
    client._authenticated = True

    def execute_sync(func):
        return func()

    mock_to_thread.side_effect = execute_sync

    with pytest.raises(Exception, match="Invalid response from LinkedIn API"):
        await client.create_comment("post-123", "urn:li:person:123", "A comment")


# Share Post Tests


@pytest.mark.asyncio
@patch("agoras.platforms.linkedin.client.asyncio.to_thread")
async def test_linkedin_client_share_post(mock_to_thread):
    """Test LinkedInAPIClient share_post method."""
    client = LinkedInAPIClient("access_token")
    mock_restli = MagicMock()
    mock_request = MagicMock()
    mock_request.status_code = 201
    mock_request.entity_id = "share-123"
    mock_restli.create.return_value = mock_request
    client.restli_client = mock_restli
    client._authenticated = True

    def execute_sync(func):
        return func()

    mock_to_thread.side_effect = execute_sync

    result = await client.share_post("post-123", "urn:li:person:123", commentary="Shared!")

    assert result == "share-123"
    call_entity = mock_restli.create.call_args[1]["entity"]
    assert call_entity["author"] == "urn:li:person:123"
    assert call_entity["commentary"] == "Shared!"
    assert call_entity["reshareContext"]["parent"] == "post-123"


@pytest.mark.asyncio
@patch("agoras.platforms.linkedin.client.asyncio.to_thread")
async def test_linkedin_client_share_post_failure(mock_to_thread):
    """Test LinkedInAPIClient share_post handles failure."""
    client = LinkedInAPIClient("access_token")
    mock_restli = MagicMock()
    mock_request = MagicMock()
    mock_request.status_code = 400
    mock_restli.create.return_value = mock_request
    client.restli_client = mock_restli
    client._authenticated = True

    def execute_sync(func):
        return func()

    mock_to_thread.side_effect = execute_sync

    with pytest.raises(Exception, match="Unable to share post"):
        await client.share_post("post-123", "urn:li:person:123")


# Delete Post Tests


@pytest.mark.asyncio
@patch("agoras.platforms.linkedin.client.asyncio.to_thread")
async def test_linkedin_client_delete_post(mock_to_thread):
    """Test LinkedInAPIClient delete_post method."""
    client = LinkedInAPIClient("access_token")
    mock_restli = MagicMock()
    mock_request = MagicMock()
    mock_request.status_code = 204
    mock_restli.delete.return_value = mock_request
    client.restli_client = mock_restli
    client._authenticated = True

    def execute_sync(func):
        return func()

    mock_to_thread.side_effect = execute_sync

    result = await client.delete_post("post-123")

    assert result == "post-123"
    mock_restli.delete.assert_called_once()
    call_path_keys = mock_restli.delete.call_args[1]["path_keys"]
    assert call_path_keys["id"] == "post-123"


@pytest.mark.asyncio
@patch("agoras.platforms.linkedin.client.asyncio.to_thread")
async def test_linkedin_client_delete_post_failure(mock_to_thread):
    """Test LinkedInAPIClient delete_post handles failure."""
    client = LinkedInAPIClient("access_token")
    mock_restli = MagicMock()
    mock_request = MagicMock()
    mock_request.status_code = 404
    mock_restli.delete.return_value = mock_request
    client.restli_client = mock_restli
    client._authenticated = True

    def execute_sync(func):
        return func()

    mock_to_thread.side_effect = execute_sync

    with pytest.raises(Exception, match="Unable to delete post"):
        await client.delete_post("post-123")


@pytest.mark.asyncio
@patch("agoras.platforms.linkedin.client.asyncio.to_thread")
async def test_linkedin_client_delete_comment(mock_to_thread):
    """Test LinkedInAPIClient delete_comment issues a DELETE on the comment resource."""
    client = LinkedInAPIClient("access_token")
    mock_restli = MagicMock()
    mock_request = MagicMock()
    mock_request.status_code = 204
    mock_restli.delete.return_value = mock_request
    client.restli_client = mock_restli
    client._authenticated = True

    def execute_sync(func):
        return func()

    mock_to_thread.side_effect = execute_sync

    result = await client.delete_comment("comment-123", parent_post_id="urn:li:ugcPost:123")

    assert result == "comment-123"
    mock_restli.delete.assert_called_once()
    resource_path = mock_restli.delete.call_args[1]["resource_path"]
    assert resource_path == "/socialActions/urn%3Ali%3AugcPost%3A123/comments/comment-123"


@pytest.mark.asyncio
@patch("agoras.platforms.linkedin.client.asyncio.to_thread")
async def test_linkedin_client_delete_comment_access_denied(mock_to_thread):
    """Test LinkedInAPIClient delete_comment surfaces the Community Management API message."""
    client = LinkedInAPIClient("access_token")
    mock_restli = MagicMock()
    mock_request = MagicMock()
    mock_request.status_code = 403
    mock_response = MagicMock()
    mock_response.json.return_value = {"code": "ACCESS_DENIED", "message": "denied"}
    mock_request.response = mock_response
    mock_restli.delete.return_value = mock_request
    client.restli_client = mock_restli
    client._authenticated = True

    def execute_sync(func):
        return func()

    mock_to_thread.side_effect = execute_sync

    with pytest.raises(Exception, match="Community Management API"):
        await client.delete_comment("comment-123", parent_post_id="urn:li:ugcPost:123")


@pytest.mark.asyncio
@patch("agoras.platforms.linkedin.client.asyncio.to_thread")
async def test_linkedin_client_delete_comment_not_found(mock_to_thread):
    """Test LinkedInAPIClient delete_comment surfaces a NOT_FOUND error."""
    client = LinkedInAPIClient("access_token")
    mock_restli = MagicMock()
    mock_request = MagicMock()
    mock_request.status_code = 404
    mock_response = MagicMock()
    mock_response.json.return_value = {"code": "NOT_FOUND", "message": "gone"}
    mock_request.response = mock_response
    mock_restli.delete.return_value = mock_request
    client.restli_client = mock_restli
    client._authenticated = True

    def execute_sync(func):
        return func()

    mock_to_thread.side_effect = execute_sync

    with pytest.raises(Exception, match="not found or already deleted"):
        await client.delete_comment("comment-123", parent_post_id="urn:li:ugcPost:123")


# Get User Info Tests


@pytest.mark.asyncio
@patch("agoras.platforms.linkedin.client.asyncio.to_thread")
async def test_linkedin_client_get_user_info(mock_to_thread):
    """Test LinkedInAPIClient get_user_info method."""
    client = LinkedInAPIClient("access_token")
    mock_restli = MagicMock()
    mock_request = MagicMock()
    mock_response = MagicMock()
    mock_response.json.return_value = {"sub": "user123", "name": "Test User"}
    mock_request.response = mock_response
    mock_restli.get.return_value = mock_request
    client.restli_client = mock_restli
    client._authenticated = True

    def execute_sync(func):
        return func()

    mock_to_thread.side_effect = execute_sync

    result = await client.get_user_info()

    assert result == {"sub": "user123", "name": "Test User"}
    mock_restli.get.assert_called_once_with(resource_path="/userinfo", access_token="access_token")


@pytest.mark.asyncio
@patch("agoras.platforms.linkedin.client.asyncio.to_thread")
async def test_linkedin_client_get_user_info_expired_token(mock_to_thread):
    """Test LinkedInAPIClient get_user_info handles expired token."""
    client = LinkedInAPIClient("access_token")
    mock_restli = MagicMock()
    mock_request = MagicMock()
    mock_response = MagicMock()
    mock_response.json.return_value = {"code": "EXPIRED_ACCESS_TOKEN"}
    mock_request.response = mock_response
    mock_restli.get.return_value = mock_request
    client.restli_client = mock_restli
    client._authenticated = True

    def execute_sync(func):
        return func()

    mock_to_thread.side_effect = execute_sync

    with pytest.raises(Exception, match="access token has expired"):
        await client.get_user_info()


@pytest.mark.asyncio
@patch("agoras.platforms.linkedin.client.asyncio.to_thread")
async def test_linkedin_client_get_post_rejects_activity_urn(mock_to_thread):
    """Test get_post rejects activity URNs with a clear error."""
    client = LinkedInAPIClient("access_token")
    mock_restli = MagicMock()
    client.restli_client = mock_restli
    client._authenticated = True

    def execute_sync(func):
        return func()

    mock_to_thread.side_effect = execute_sync

    with pytest.raises(Exception, match="not an activity URN"):
        await client.get_post("urn:li:activity:123")

    mock_restli.get.assert_not_called()


@pytest.mark.asyncio
@patch("agoras.platforms.linkedin.client.asyncio.to_thread")
async def test_linkedin_client_get_comment_rejects_activity_urn(mock_to_thread):
    """Test get_comment rejects activity URNs on parent post."""
    client = LinkedInAPIClient("access_token")
    client.restli_client = MagicMock()
    client._authenticated = True

    def execute_sync(func):
        return func()

    mock_to_thread.side_effect = execute_sync

    with pytest.raises(Exception, match="not an activity URN"):
        await client.get_comment("comment-123", "urn:li:activity:456")

    client.restli_client.get.assert_not_called()


@pytest.mark.asyncio
@patch("agoras.platforms.linkedin.client.asyncio.to_thread")
async def test_linkedin_client_get_media_returns_download_url(mock_to_thread):
    """Test get_media resolves a media URN to its downloadUrl."""
    client = LinkedInAPIClient("access_token")
    mock_restli = MagicMock()
    mock_request = MagicMock()
    mock_request.status_code = 200
    mock_request.entity = {"downloadUrl": "https://example.com/img1.jpg"}
    mock_restli.get.return_value = mock_request
    client.restli_client = mock_restli
    client._authenticated = True

    def execute_sync(func):
        return func()

    mock_to_thread.side_effect = execute_sync

    result = await client.get_media("urn:li:image:img1")

    assert result == {"downloadUrl": "https://example.com/img1.jpg"}
    mock_restli.get.assert_called_once_with(
        resource_path="/media/urn%3Ali%3Aimage%3Aimg1",
        version_string=client.api_version,
        access_token="access_token",
    )


@pytest.mark.asyncio
@patch("agoras.platforms.linkedin.client.asyncio.to_thread")
async def test_linkedin_client_list_posts(mock_to_thread):
    """Test list_posts returns the author's recent posts."""
    client = LinkedInAPIClient("access_token")
    mock_restli = MagicMock()
    mock_request = MagicMock()
    mock_request.status_code = 200
    mock_request.entity = {
        "elements": [
            {"id": "urn:li:share:1", "commentary": "hello"},
            {"id": "urn:li:share:2", "commentary": "world"},
        ]
    }
    mock_restli.get.return_value = mock_request
    client.restli_client = mock_restli
    client._authenticated = True

    def execute_sync(func):
        return func()

    mock_to_thread.side_effect = execute_sync

    result = await client.list_posts("urn:li:person:42", 2)

    assert len(result) == 2
    assert result[0]["id"] == "urn:li:share:1"
    assert result[1]["id"] == "urn:li:share:2"
    mock_restli.get.assert_called_once_with(
        resource_path="/posts",
        query_params={"author": "urn:li:person:42", "count": 2},
        version_string=client.api_version,
        access_token="access_token",
    )


@pytest.mark.asyncio
@patch("agoras.platforms.linkedin.client.asyncio.to_thread")
async def test_linkedin_client_list_posts_no_author(mock_to_thread):
    """Test list_posts raises when the author URN is missing."""
    client = LinkedInAPIClient("access_token")
    client.restli_client = MagicMock()
    client._authenticated = True

    def execute_sync(func):
        return func()

    mock_to_thread.side_effect = execute_sync

    with pytest.raises(Exception, match="author URN is required"):
        await client.list_posts("", 2)

    client.restli_client.get.assert_not_called()
