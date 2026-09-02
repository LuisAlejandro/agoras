# -*- coding: utf-8 -*-
#
# Please refer to AUTHORS.md for a complete list of Copyright holders.
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
"""agoras.platforms.linkedin.client module."""

import asyncio
import time
import urllib.parse
from typing import Any, Dict, List, Optional

import requests
from linkedin_api.clients.restli.client import RestliClient
from linkedin_api.clients.restli.utils import api as apiutils
from linkedin_api.clients.restli.utils.query_tunneling import maybe_apply_query_tunneling_requests_with_body
from linkedin_api.common.constants import RESTLI_METHODS


def _reject_activity_urn(urn: str, action: str) -> None:
    """Reject activity URNs where ugcPost/share URNs are required."""
    if urn and urn.startswith("urn:li:activity:"):
        raise Exception(
            f"LinkedIn {action} requires a ugcPost or share URN, not an activity URN. "
            "Use the post URN returned when creating the post."
        )


class LinkedInAPIClient:
    """
    LinkedIn API client that centralizes LinkedIn operations.

    Handles all LinkedIn API interactions through RestliClient,
    including posts, image uploads, likes, shares, and deletions.
    """

    def __init__(self, access_token: str):
        """
        Initialize LinkedIn API client.

        Args:
            access_token (str): LinkedIn access token
        """
        self.access_token = access_token
        self.restli_client: Optional[RestliClient] = None
        self.api_version = "202503"
        self._authenticated = False

    async def authenticate(self) -> bool:
        """
        Authenticate and initialize RestliClient.

        Returns:
            bool: True if authentication successful

        Raises:
            Exception: If authentication fails
        """
        if self._authenticated:
            return True

        if not self.access_token:
            raise Exception("LinkedIn access token is required")

        try:
            self.restli_client = RestliClient()
            self._authenticated = True
            return True
        except Exception as e:
            raise Exception(f"LinkedIn client authentication failed: {str(e)}")

    def disconnect(self):
        """
        Disconnect and clean up client resources.
        """
        self.restli_client = None
        self._authenticated = False

    def _post_restli_action(
        self,
        resource_path: str,
        action_name: str,
        action_params: Dict[str, Any],
    ) -> requests.Response:
        """
        Send a Rest.li ACTION and return the raw HTTP response.

        Some LinkedIn actions (e.g. finalizeUpload) return 2xx with an empty
        body; RestliClient.action() cannot parse those responses.
        """
        if not self.restli_client:
            raise Exception("LinkedIn RestliClient not initialized")
        if not self.access_token:
            raise Exception("No access token available")

        url = apiutils.build_rest_url(
            resource_path=resource_path,
            version_string=self.api_version,
        )
        prepared = maybe_apply_query_tunneling_requests_with_body(
            encoded_query_param_string=f"action={action_name}",
            url=url,
            original_restli_method=RESTLI_METHODS.ACTION,
            original_request_body=action_params,
            access_token=self.access_token,
            version_string=self.api_version,
        )
        return self.restli_client.session.send(prepared)

    async def upload_image(self, image_content: bytes, owner_urn: str) -> str:
        """
        Upload an image to LinkedIn.

        Args:
            image_content (bytes): Raw image content
            owner_urn (str): LinkedIn owner URN (e.g., "urn:li:person:12345")

        Returns:
            str: Media ID for the uploaded image

        Raises:
            Exception: If image upload fails
        """

        def _sync_upload():
            if not self.restli_client:
                raise Exception("LinkedIn RestliClient not initialized")
            if not self.access_token:
                raise Exception("No access token available")

            # Initialize upload
            request = self.restli_client.action(
                resource_path="/images",
                action_name="initializeUpload",
                action_params={
                    "initializeUploadRequest": {
                        "owner": owner_urn,
                    }
                },
                version_string=self.api_version,
                access_token=self.access_token,
            )

            response = request.response.json()
            upload_url = response.get("value", {}).get("uploadUrl", "")
            media_id = response.get("value", {}).get("image", "")

            if not upload_url or not media_id:
                raise Exception("Failed to get upload URL or media ID from LinkedIn")

            # Upload the image content
            upload_response = requests.put(
                upload_url, headers={"Authorization": f"Bearer {self.access_token}"}, data=image_content, timeout=30
            )

            if upload_response.status_code != 201:
                raise Exception(f"Failed to upload image: {upload_response.status_code}")

            return media_id

        return await asyncio.to_thread(_sync_upload)

    @staticmethod
    def _etag_from_response(response: requests.Response) -> str:
        """Extract ETag header value for multipart video finalize."""
        etag = response.headers.get("etag") or response.headers.get("ETag") or ""
        etag = etag.strip().strip('"')
        if not etag:
            raise Exception("Missing ETag from video upload response")
        return etag

    async def upload_video(self, video_content: bytes, owner_urn: str) -> str:
        """
        Upload a video to LinkedIn via the Videos API.

        Initializes upload, sends byte chunks, finalizes, and waits until
        the video status is AVAILABLE.

        Args:
            video_content (bytes): Raw video content
            owner_urn (str): LinkedIn owner URN (e.g., "urn:li:person:12345")

        Returns:
            str: Video URN for the uploaded video

        Raises:
            Exception: If any upload step fails
        """

        def _sync_upload():
            if not self.restli_client:
                raise Exception("LinkedIn RestliClient not initialized")
            if not self.access_token:
                raise Exception("No access token available")

            init_request = self.restli_client.action(
                resource_path="/videos",
                action_name="initializeUpload",
                action_params={
                    "initializeUploadRequest": {
                        "owner": owner_urn,
                        "fileSizeBytes": len(video_content),
                        "uploadCaptions": False,
                        "uploadThumbnail": False,
                    }
                },
                version_string=self.api_version,
                access_token=self.access_token,
            )

            init_value = init_request.response.json().get("value", {})
            video_urn = init_value.get("video", "")
            upload_token = init_value.get("uploadToken", "")
            instructions = init_value.get("uploadInstructions", [])

            if not video_urn or not instructions:
                raise Exception("Failed to initialize video upload with LinkedIn")

            uploaded_part_ids = []
            for instruction in instructions:
                first_byte = instruction.get("firstByte", 0)
                last_byte = instruction.get("lastByte", len(video_content) - 1)
                upload_url = instruction.get("uploadUrl", "")
                if not upload_url:
                    raise Exception("Missing upload URL in LinkedIn video instructions")

                chunk = video_content[first_byte : last_byte + 1]
                upload_response = requests.put(
                    upload_url,
                    headers={"Content-Type": "application/octet-stream"},
                    data=chunk,
                    timeout=30,
                )

                if upload_response.status_code not in (200, 201):
                    raise Exception(f"Failed to upload video part: {upload_response.status_code}")

                uploaded_part_ids.append(self._etag_from_response(upload_response))

            finalize_response = self._post_restli_action(
                resource_path="/videos",
                action_name="finalizeUpload",
                action_params={
                    "finalizeUploadRequest": {
                        "video": video_urn,
                        "uploadToken": upload_token,
                        "uploadedPartIds": uploaded_part_ids,
                    }
                },
            )

            if finalize_response.status_code not in (200, 201, 204):
                detail = finalize_response.text.strip() or finalize_response.reason
                raise Exception(f"Failed to finalize video upload: {finalize_response.status_code} ({detail})")

            self._wait_for_video_available(video_urn)
            return video_urn

        return await asyncio.to_thread(_sync_upload)

    def _wait_for_video_available(self, video_urn: str, timeout_s: int = 120) -> None:
        """Poll LinkedIn until the uploaded video is AVAILABLE."""
        if not self.restli_client:
            raise Exception("LinkedIn RestliClient not initialized")

        encoded_urn = urllib.parse.quote(video_urn, safe="")
        deadline = time.monotonic() + timeout_s

        while time.monotonic() < deadline:
            request = self.restli_client.get(
                resource_path=f"/videos/{encoded_urn}", version_string=self.api_version, access_token=self.access_token
            )
            status = request.response.json().get("status", "")
            if status == "AVAILABLE":
                return
            if status == "PROCESSING_FAILED":
                raise Exception("LinkedIn video processing failed")

            time.sleep(2)

        raise Exception("Timed out waiting for LinkedIn video to become available")

    @staticmethod
    def _build_post_content(
        link: Optional[str],
        text: str,
        link_title: Optional[str],
        link_description: Optional[str],
        image_ids: Optional[List[str]],
        video_id: Optional[str],
        video_title: Optional[str],
    ) -> Optional[Dict[str, Any]]:
        """Build the LinkedIn post ``content`` payload for the given media."""
        if link and text:
            article: Dict[str, Any] = {
                "source": link,
                "title": text,
            }
            if image_ids:
                article["thumbnail"] = image_ids[0]
            if link_title:
                article["title"] = link_title
            if link_description:
                article["description"] = link_description
            return {"article": article}

        if not link and video_id:
            media: Dict[str, Any] = {"id": video_id}
            if video_title:
                media["title"] = video_title
            return {"media": media}

        if not link and image_ids:
            if len(image_ids) == 1:
                return {"media": {"id": image_ids[0]}}
            return {"multiImage": {"images": [{"id": image_id} for image_id in image_ids]}}

        return None

    async def create_post(
        self,
        author_urn: str,
        text: str,
        link: Optional[str] = None,
        link_title: Optional[str] = None,
        link_description: Optional[str] = None,
        image_ids: Optional[List[str]] = None,
        video_id: Optional[str] = None,
        video_title: Optional[str] = None,
    ) -> str:
        """
        Create a LinkedIn post.

        Args:
            author_urn (str): LinkedIn author URN (e.g., "urn:li:person:12345")
            text (str): Post text content
            link (str, optional): URL to include
            link_title (str, optional): Title of the link
            link_description (str, optional): Description of the link
            image_ids (list, optional): List of uploaded image IDs
            video_id (str, optional): Uploaded video URN
            video_title (str, optional): Title for the video post

        Returns:
            str: Post ID

        Raises:
            Exception: If post creation fails
        """

        def _sync_create_post():
            if not self.restli_client:
                raise Exception("LinkedIn RestliClient not initialized")
            if not self.access_token:
                raise Exception("No access token available")

            entity = {
                "author": author_urn,
                "commentary": text,
                "visibility": "PUBLIC",
                "distribution": {
                    "feedDistribution": "MAIN_FEED",
                    "targetEntities": [],
                    "thirdPartyDistributionChannels": [],
                },
                "lifecycleState": "PUBLISHED",
                "isReshareDisabledByAuthor": False,
            }

            content = self._build_post_content(
                link,
                text,
                link_title,
                link_description,
                image_ids,
                video_id,
                video_title,
            )
            if content:
                entity["content"] = content

            request = self.restli_client.create(
                resource_path="/posts", entity=entity, version_string=self.api_version, access_token=self.access_token
            )

            if hasattr(request, "entity_id") and request.entity_id:
                return str(request.entity_id)
            else:
                raise Exception("Invalid response from LinkedIn API")

        return await asyncio.to_thread(_sync_create_post)

    async def like_post(self, post_id: str, actor_urn: str) -> str:
        """
        Like a LinkedIn post.

        Args:
            post_id (str): Post ID to like
            actor_urn (str): LinkedIn actor URN (e.g., "urn:li:person:12345")

        Returns:
            str: Post ID

        Raises:
            Exception: If like operation fails
        """

        def _sync_like():
            if not self.restli_client:
                raise Exception("LinkedIn RestliClient not initialized")
            if not self.access_token:
                raise Exception("No access token available")

            entity = {
                "actor": actor_urn,
                "object": post_id,
            }

            # Use the correct LinkedIn social actions endpoint for likes
            # According to LinkedIn API docs: POST /v2/socialActions/{postUrn}/likes
            # URL-encode the post_id for the path
            import urllib.parse

            encoded_post_id = urllib.parse.quote(post_id, safe="")

            request = self.restli_client.create(
                resource_path=f"/socialActions/{encoded_post_id}/likes",
                entity=entity,
                version_string=self.api_version,
                access_token=self.access_token,
            )

            if request.status_code != 201:
                try:
                    response_data = request.response.json()
                    if response_data.get("code") == "ACCESS_DENIED":
                        raise Exception(
                            'LinkedIn like permission denied. Your LinkedIn app needs "Community Management API" '
                            "product enabled and w_member_social_feed scope approved. Visit "
                            "https://developers.linkedin.com/ to configure your app permissions."
                        )
                    else:
                        raise Exception(
                            f"Unable to like post {post_id}: {response_data.get('message', 'Unknown error')}"
                        )
                except Exception as e:
                    if "permission denied" in str(e).lower():
                        raise e
                    raise Exception(f"Unable to like post {post_id} - Status: {request.status_code}")
            return post_id

        return await asyncio.to_thread(_sync_like)

    async def create_comment(
        self, post_id: str, actor_urn: str, text: str, image_ids: Optional[List[str]] = None
    ) -> str:
        """
        Comment on a LinkedIn post.

        Args:
            post_id (str): Post ID to comment on
            actor_urn (str): LinkedIn actor URN (e.g., "urn:li:person:12345")
            text (str): Comment text
            image_ids (list, optional): List of uploaded image IDs to attach

        Returns:
            str: Comment ID

        Raises:
            Exception: If comment operation fails
        """
        _reject_activity_urn(post_id, "reply")

        def _sync_comment():
            if not self.restli_client:
                raise Exception("LinkedIn RestliClient not initialized")
            if not self.access_token:
                raise Exception("No access token available")

            entity: Dict[str, Any] = {
                "actor": actor_urn,
                "object": post_id,
                "comment": text,
            }

            if image_ids:
                entity["content"] = [{"entity": {"image": image_id}} for image_id in image_ids]

            # Use the LinkedIn social actions endpoint for comments.
            # POST /v2/socialActions/{postUrn}/comments
            # URL-encode the post_id for the path.
            encoded_post_id = urllib.parse.quote(post_id, safe="")

            request = self.restli_client.create(
                resource_path=f"/socialActions/{encoded_post_id}/comments",
                entity=entity,
                version_string=self.api_version,
                access_token=self.access_token,
            )

            if request.status_code != 201:
                try:
                    response_data = request.response.json()
                    if response_data.get("code") == "ACCESS_DENIED":
                        raise Exception(
                            'LinkedIn comment permission denied. Your LinkedIn app needs "Community Management API" '
                            "product enabled and w_member_social_feed scope approved. Visit "
                            "https://developers.linkedin.com/ to configure your app permissions."
                        )
                    else:
                        raise Exception(
                            f"Unable to comment on post {post_id}: {response_data.get('message', 'Unknown error')}"
                        )
                except Exception as e:
                    if "permission denied" in str(e).lower():
                        raise e
                    raise Exception(f"Unable to comment on post {post_id} - Status: {request.status_code}")

            if hasattr(request, "entity_id") and request.entity_id:
                return str(request.entity_id)
            else:
                raise Exception("Invalid response from LinkedIn API")

        return await asyncio.to_thread(_sync_comment)

    async def delete_comment(self, comment_id: str, parent_post_id: str) -> str:
        """
        Delete a LinkedIn comment.

        The LinkedIn Comments API requires both the parent post URN and the
        comment ID in the resource path.

        Args:
            comment_id (str): Comment ID to delete
            parent_post_id (str): Parent post/share URN the comment belongs to

        Returns:
            str: Deleted comment ID

        Raises:
            Exception: If deletion fails
        """

        def _sync_delete_comment():
            if not self.restli_client:
                raise Exception("LinkedIn RestliClient not initialized")
            if not self.access_token:
                raise Exception("No access token available")
            if not parent_post_id:
                raise Exception("LinkedIn parent post ID is required for delete-reply action.")
            if not comment_id:
                raise Exception("LinkedIn comment ID is required for delete-reply action.")
            _reject_activity_urn(parent_post_id, "delete-reply")

            encoded_parent = urllib.parse.quote(parent_post_id, safe="")
            encoded_comment = urllib.parse.quote(comment_id, safe="")

            request = self.restli_client.delete(
                resource_path=f"/socialActions/{encoded_parent}/comments/{encoded_comment}",
                version_string=self.api_version,
                access_token=self.access_token,
            )

            if request.status_code not in (200, 204):
                try:
                    response_data = request.response.json()
                    if response_data.get("code") == "ACCESS_DENIED":
                        raise Exception(
                            'LinkedIn comment delete permission denied. Your LinkedIn app needs "Community '
                            'Management API" product enabled and w_member_social_feed scope approved. Visit '
                            "https://developers.linkedin.com/ to configure your app permissions."
                        )
                    if response_data.get("code") == "NOT_FOUND":
                        raise Exception(f"LinkedIn comment {comment_id} not found or already deleted.")
                    raise Exception(
                        f"Unable to delete comment {comment_id}: {response_data.get('message', 'Unknown error')}"
                    )
                except Exception as exc:
                    if "permission" in str(exc).lower() or "not found" in str(exc).lower():
                        raise exc
                    raise Exception(f"Unable to delete comment {comment_id} - Status: {request.status_code}") from exc
            return comment_id

        return await asyncio.to_thread(_sync_delete_comment)

    async def share_post(self, post_id: str, author_urn: str, commentary: str = "") -> str:
        """
        Share (repost) a LinkedIn post.

        Args:
            post_id (str): Post ID to share
            author_urn (str): LinkedIn author URN (e.g., "urn:li:person:12345")
            commentary (str, optional): Commentary to add to the share

        Returns:
            str: Share ID

        Raises:
            Exception: If share operation fails
        """

        def _sync_share():
            if not self.restli_client:
                raise Exception("LinkedIn RestliClient not initialized")
            if not self.access_token:
                raise Exception("No access token available")

            entity = {
                "author": author_urn,
                "commentary": commentary,
                "visibility": "PUBLIC",
                "distribution": {
                    "feedDistribution": "MAIN_FEED",
                    "targetEntities": [],
                    "thirdPartyDistributionChannels": [],
                },
                "lifecycleState": "PUBLISHED",
                "isReshareDisabledByAuthor": False,
                "reshareContext": {"parent": post_id},
            }

            request = self.restli_client.create(
                resource_path="/posts", entity=entity, version_string=self.api_version, access_token=self.access_token
            )

            if request.status_code != 201:
                raise Exception(f"Unable to share post {post_id}")

            if hasattr(request, "entity_id") and request.entity_id:
                return str(request.entity_id)
            else:
                raise Exception("Invalid response from LinkedIn API")

        return await asyncio.to_thread(_sync_share)

    async def delete_post(self, post_id: str) -> str:
        """
        Delete a LinkedIn post.

        Args:
            post_id (str): Post ID to delete

        Returns:
            str: Post ID

        Raises:
            Exception: If deletion fails
        """

        def _sync_delete():
            if not self.restli_client:
                raise Exception("LinkedIn RestliClient not initialized")
            if not self.access_token:
                raise Exception("No access token available")

            request = self.restli_client.delete(
                resource_path="/posts/{id}",
                path_keys={"id": post_id},
                version_string=self.api_version,
                access_token=self.access_token,
            )

            if request.status_code != 204:
                raise Exception(f"Unable to delete post {post_id}")
            return post_id

        return await asyncio.to_thread(_sync_delete)

    async def get_post(self, post_id: str) -> Dict[str, Any]:
        """
        Read a LinkedIn post by URN.

        Args:
            post_id (str): Post URN to read

        Returns:
            dict: Post entity from the LinkedIn Posts API

        Raises:
            Exception: If the post cannot be read
        """

        def _sync_get():
            if not self.restli_client:
                raise Exception("LinkedIn RestliClient not initialized")
            if not self.access_token:
                raise Exception("No access token available")
            if not post_id:
                raise Exception("LinkedIn post ID is required for get-post action.")
            _reject_activity_urn(post_id, "get-post")

            request = self.restli_client.get(
                resource_path="/posts/{id}",
                path_keys={"id": post_id},
                version_string=self.api_version,
                access_token=self.access_token,
            )

            if request.status_code != 200:
                raise Exception(f"Unable to get LinkedIn post {post_id} - Status: {request.status_code}")

            entity = getattr(request, "entity", None)
            if entity is None:
                try:
                    entity = request.response.json()
                except Exception as exc:
                    raise Exception(f"Unable to parse LinkedIn post {post_id}") from exc
            if isinstance(entity, dict):
                return entity
            return {"id": post_id, "raw": entity}

        return await asyncio.to_thread(_sync_get)

    async def get_comment(self, comment_id: str, parent_post_id: str) -> Dict[str, Any]:
        """
        Read a LinkedIn comment by ID and parent post URN.

        Args:
            comment_id (str): Comment ID to read
            parent_post_id (str): Parent post/share URN the comment belongs to

        Returns:
            dict: Comment entity from the LinkedIn Comments API

        Raises:
            Exception: If the comment cannot be read
        """

        def _sync_get_comment():
            if not self.restli_client:
                raise Exception("LinkedIn RestliClient not initialized")
            if not self.access_token:
                raise Exception("No access token available")
            if not parent_post_id:
                raise Exception("LinkedIn parent post ID is required for get-reply action.")
            if not comment_id:
                raise Exception("LinkedIn comment ID is required for get-reply action.")
            _reject_activity_urn(parent_post_id, "get-reply")

            encoded_parent = urllib.parse.quote(parent_post_id, safe="")
            encoded_comment = urllib.parse.quote(comment_id, safe="")

            request = self.restli_client.get(
                resource_path=f"/socialActions/{encoded_parent}/comments/{encoded_comment}",
                version_string=self.api_version,
                access_token=self.access_token,
            )

            if request.status_code != 200:
                raise Exception(f"Unable to get LinkedIn comment {comment_id} - Status: {request.status_code}")

            entity = getattr(request, "entity", None)
            if entity is None:
                try:
                    entity = request.response.json()
                except Exception as exc:
                    raise Exception(f"Unable to parse LinkedIn comment {comment_id}") from exc
            if isinstance(entity, dict):
                return entity
            return {"id": comment_id, "raw": entity}

        return await asyncio.to_thread(_sync_get_comment)

    async def get_media(self, media_urn: str) -> Dict[str, Any]:
        """
        Resolve a LinkedIn media URN to its downloadable URL.

        Args:
            media_urn (str): Media URN (e.g. "urn:li:image:123" or "urn:li:video:456")

        Returns:
            dict: Media entity containing a ``downloadUrl``

        Raises:
            Exception: If the media cannot be resolved
        """

        def _sync_get_media():
            if not self.restli_client:
                raise Exception("LinkedIn RestliClient not initialized")
            if not self.access_token:
                raise Exception("No access token available")
            if not media_urn:
                raise Exception("LinkedIn media URN is required.")

            encoded_urn = urllib.parse.quote(media_urn, safe="")
            request = self.restli_client.get(
                resource_path=f"/media/{encoded_urn}",
                version_string=self.api_version,
                access_token=self.access_token,
            )

            if request.status_code != 200:
                raise Exception(f"Unable to get LinkedIn media {media_urn} - Status: {request.status_code}")

            entity = getattr(request, "entity", None)
            if entity is None:
                try:
                    entity = request.response.json()
                except Exception as exc:
                    raise Exception(f"Unable to parse LinkedIn media {media_urn}") from exc
            if isinstance(entity, dict):
                return entity
            return {"id": media_urn, "raw": entity}

        return await asyncio.to_thread(_sync_get_media)

    async def get_user_info(self) -> Dict[str, Any]:
        """
        Get user information from LinkedIn API.

        Returns:
            dict: User information

        Raises:
            Exception: If request fails
        """

        def _sync_get_user_info():
            if not self.restli_client:
                raise Exception("LinkedIn RestliClient not initialized")
            if not self.access_token:
                raise Exception("No access token available")

            me = self.restli_client.get(resource_path="/userinfo", access_token=self.access_token)
            result = me.response.json()

            # Handle potential token expiration
            if result.get("code", "") == "EXPIRED_ACCESS_TOKEN":
                raise Exception("LinkedIn access token has expired")

            return result

        return await asyncio.to_thread(_sync_get_user_info)

    async def list_posts(self, author_urn: str, limit: int) -> List[Dict[str, Any]]:
        """
        List recent posts by an author.

        Args:
            author_urn (str): LinkedIn author URN (e.g. "urn:li:person:12345")
            limit (int): Maximum number of posts to return

        Returns:
            list: Post entities from the LinkedIn Posts API

        Raises:
            Exception: If the posts cannot be read
        """

        def _sync_list():
            if not self.restli_client:
                raise Exception("LinkedIn RestliClient not initialized")
            if not self.access_token:
                raise Exception("No access token available")
            if not author_urn:
                raise Exception("LinkedIn author URN is required for list-posts action.")

            request = self.restli_client.get(
                resource_path="/posts",
                query_params={"author": author_urn, "count": limit},
                version_string=self.api_version,
                access_token=self.access_token,
            )

            if request.status_code != 200:
                raise Exception(f"Unable to list LinkedIn posts - Status: {request.status_code}")

            entity = getattr(request, "entity", None)
            if entity is None:
                try:
                    entity = request.response.json()
                except Exception as exc:
                    raise Exception("Unable to parse LinkedIn posts") from exc
            if isinstance(entity, dict):
                elements = entity.get("elements") or []
                return [e for e in elements if isinstance(e, dict)]
            return []

        return await asyncio.to_thread(_sync_list)
