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
"""agoras.platforms.instagram.client module."""

import asyncio
import time
from typing import Any, Dict, List, Optional

from pyfacebook import GraphAPI

from agoras.common import __version__
from agoras.common.utils import build_upload_session


def _resumable_upload_timeout(video_file_size: int) -> int:
    """Scale rupload POST timeout with file size, capped at 10 minutes."""
    megabytes = max(0, video_file_size) // (1024 * 1024)
    return max(30, min(600, megabytes * 2 or 30))


class InstagramAPIClient:
    """
    Instagram API client that centralizes Instagram operations.

    Handles all Instagram API interactions through Facebook's GraphAPI,
    including media creation, carousel posts, publishing, and basic operations.
    Uses the same GraphAPI as Facebook since Instagram is part of Meta's ecosystem.
    """

    def __init__(self, access_token: str):
        """
        Initialize Instagram API client.

        Args:
            access_token (str): Instagram access token (Facebook token with Instagram permissions)
        """
        self.access_token = access_token
        self.graph_api: Optional[GraphAPI] = None
        self.api_version = "21.0"
        self._authenticated = False
        self._RUPLOAD_RETRY_STATUSES = frozenset({429, 500, 502, 503, 504})
        self._RUPLOAD_MAX_ATTEMPTS = 3

    async def authenticate(self) -> bool:
        """
        Authenticate and initialize GraphAPI client for Instagram.

        Returns:
            bool: True if authentication successful

        Raises:
            Exception: If authentication fails
        """
        if self._authenticated:
            return True

        if not self.access_token:
            raise Exception("Instagram access token is required")

        try:
            self.graph_api = GraphAPI(access_token=self.access_token, version=self.api_version)
            self._authenticated = True
            return True
        except Exception as e:
            raise Exception(f"Instagram client authentication failed: {str(e)}")

    def disconnect(self):
        """
        Disconnect and clean up client resources.
        """
        self.graph_api = None
        self._authenticated = False

    def post_object(self, object_id: str, connection: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Post to an Instagram object connection using GraphAPI.

        Args:
            object_id (str): Instagram object ID
            connection (str): Connection type (media, media_publish, etc.)
            data (dict, optional): Data to post

        Returns:
            dict: Response from Instagram API

        Raises:
            Exception: If post fails
        """
        if not self.graph_api:
            raise Exception("Instagram GraphAPI not initialized")

        try:
            return self.graph_api.post_object(object_id=object_id, connection=connection, data=data or {})
        except Exception as e:
            raise Exception(f"Instagram post_object failed: {str(e)}")

    async def create_comment(self, post_id: str, text: str) -> str:
        """
        Comment on an Instagram media post.

        Args:
            post_id (str): Instagram media ID to comment on
            text (str): Comment text

        Returns:
            str: Comment ID

        Raises:
            Exception: If comment fails
        """
        response = self.post_object(post_id, connection="comments", data={"message": text})
        comment_id = response.get("id")
        if not comment_id:
            raise Exception("Invalid response from Instagram API: missing comment id")
        return str(comment_id)

    async def delete_comment(self, comment_id: str) -> str:
        """
        Delete an Instagram comment.

        Args:
            comment_id (str): Comment ID to delete

        Returns:
            str: Deleted comment ID

        Raises:
            Exception: If deletion fails
        """
        if not self.graph_api:
            raise Exception("Instagram GraphAPI not initialized")
        if not comment_id:
            raise Exception("Instagram comment ID is required for delete-reply action.")

        graph_api = self.graph_api

        def _sync_delete_comment():
            try:
                graph_api.delete_object(object_id=comment_id)
            except Exception as exc:
                message = str(exc).lower()
                if "permission" in message or "not exist" in message or "not found" in message:
                    raise Exception(f"Instagram comment delete: {str(exc)}") from exc
                raise Exception(f"Unable to delete comment {comment_id}: {str(exc)}") from exc
            return comment_id

        return await asyncio.to_thread(_sync_delete_comment)

    async def delete_media(self, media_id: str) -> str:
        """
        Delete an Instagram media post.

        Args:
            media_id (str): Instagram media ID to delete

        Returns:
            str: Deleted media ID

        Raises:
            Exception: If deletion fails
        """
        if not self.graph_api:
            raise Exception("Instagram GraphAPI not initialized")
        if not media_id:
            raise Exception("Instagram media ID is required for delete action.")

        graph_api = self.graph_api

        def _sync_delete_media():
            try:
                graph_api.delete_object(object_id=media_id)
            except Exception as exc:
                message = str(exc).lower()
                if "permission" in message or "not exist" in message or "not found" in message:
                    raise Exception(f"Instagram media delete: {str(exc)}") from exc
                raise Exception(f"Unable to delete media {media_id}: {str(exc)}") from exc
            return media_id

        return await asyncio.to_thread(_sync_delete_media)

    def get_object(self, object_id: str, fields: Optional[str] = None) -> Dict[str, Any]:
        """
        Get an Instagram object using GraphAPI.

        Args:
            object_id (str): Instagram object ID
            fields (str, optional): Fields to retrieve

        Returns:
            dict: Object data from Instagram API

        Raises:
            Exception: If get fails
        """
        if not self.graph_api:
            raise Exception("Instagram GraphAPI not initialized")

        try:
            if fields:
                return self.graph_api.get_object(object_id=object_id, fields=fields)
            else:
                return self.graph_api.get_object(object_id=object_id)
        except Exception as e:
            raise Exception(f"Instagram get_object failed: {str(e)}")

    async def wait_for_media_container(
        self, container_id: str, max_wait_time: int = 300, poll_interval: float = 3.0
    ) -> None:
        """
        Wait until an Instagram media container is ready to publish.

        Args:
            container_id (str): Media container ID from create_media/create_carousel
            max_wait_time (int): Maximum wait time in seconds
            poll_interval (float): Seconds between status checks

        Raises:
            Exception: If container fails, expires, or times out
        """

        def _sync_wait():
            start = time.time()
            while True:
                if time.time() - start > max_wait_time:
                    raise Exception(f"Instagram media container {container_id} not ready after {max_wait_time} seconds")

                response = self.get_object(object_id=container_id, fields="status_code,status")
                status_code = response.get("status_code")

                if status_code in ("FINISHED", "PUBLISHED"):
                    return
                if status_code in ("ERROR", "EXPIRED"):
                    detail = response.get("status", status_code)
                    raise Exception(f"Instagram media container {container_id} failed: {detail}")

                time.sleep(poll_interval)

        await asyncio.to_thread(_sync_wait)

    async def create_media(
        self,
        object_id: str,
        image_url: Optional[str] = None,
        video_url: Optional[str] = None,
        caption: Optional[str] = None,
        is_carousel_item: bool = False,
        media_type: Optional[str] = None,
    ) -> str:
        """
        Create media for Instagram post.

        Args:
            object_id (str): Instagram object ID
            image_url (str, optional): Image URL
            video_url (str, optional): Video URL
            caption (str, optional): Media caption
            is_carousel_item (bool): Whether this is part of a carousel
            media_type (str, optional): Media type (REELS, STORIES)

        Returns:
            str: Media ID

        Raises:
            Exception: If media creation fails
        """

        def _sync_create_media():
            data: Dict[str, Any] = {
                "is_carousel_item": is_carousel_item,
            }

            if video_url:
                data["video_url"] = video_url
                if media_type:
                    data["media_type"] = media_type
                elif not is_carousel_item:
                    data["media_type"] = "REELS"
            elif image_url:
                data["image_url"] = image_url

            if caption and not is_carousel_item:
                data["caption"] = caption

            response = self.post_object(object_id=object_id, connection="media", data=data)
            return response["id"]

        media_id = await asyncio.to_thread(_sync_create_media)
        await self.wait_for_media_container(media_id)
        return media_id

    def _rupload_url(self, container_id: str, uri: Optional[str] = None) -> str:
        """Return the rupload endpoint, preferring Meta's uri when it is on rupload.facebook.com."""
        if uri and uri.startswith("https://rupload.facebook.com/"):
            return uri
        return f"https://rupload.facebook.com/ig-api-upload/v{self.api_version}/{container_id}"

    def upload_resumable_video(self, container_id: str, video_content: bytes, upload_uri: Optional[str] = None) -> None:
        """POST local video bytes to rupload.facebook.com for a resumable container."""
        if not video_content:
            raise Exception("Video file is empty")

        url = self._rupload_url(container_id, upload_uri)
        headers = {
            "Authorization": f"OAuth {self.access_token}",
            "offset": "0",
            "file_size": str(len(video_content)),
            "User-Agent": f"Agoras/{__version__}",
        }
        timeout = _resumable_upload_timeout(len(video_content))
        with build_upload_session(self._RUPLOAD_MAX_ATTEMPTS, self._RUPLOAD_RETRY_STATUSES, ["POST"]) as session:
            response = session.post(url, headers=headers, data=video_content, timeout=timeout)
        if response.status_code not in (200, 201):
            raise Exception(f"Instagram resumable video upload failed: HTTP {response.status_code}")

    async def create_resumable_video(
        self,
        object_id: str,
        video_content: bytes,
        caption: Optional[str] = None,
        media_type: Optional[str] = None,
    ) -> str:
        """
        Create a resumable Instagram video container and upload local bytes.

        Args:
            object_id (str): Instagram object ID
            video_content (bytes): Raw video file bytes
            caption (str, optional): Video caption
            media_type (str, optional): REELS or STORIES

        Returns:
            str: Media container ID ready to publish

        Raises:
            Exception: If container creation or rupload fails
        """
        if not video_content:
            raise Exception("Video file is empty")

        def _sync_create_resumable():
            data: Dict[str, Any] = {
                "upload_type": "resumable",
                "media_type": media_type or "REELS",
            }
            if caption:
                data["caption"] = caption

            response = self.post_object(object_id=object_id, connection="media", data=data)
            container_id = response.get("id")
            if not container_id:
                raise Exception("Instagram resumable upload did not return a container id")
            self.upload_resumable_video(container_id, video_content, response.get("uri"))
            return container_id

        container_id = await asyncio.to_thread(_sync_create_resumable)
        await self.wait_for_media_container(container_id)
        return container_id

    async def create_carousel(self, object_id: str, media_ids: List[str], caption: Optional[str] = None) -> str:
        """
        Create carousel media for Instagram.

        Args:
            object_id (str): Instagram object ID
            media_ids (list): List of media IDs
            caption (str, optional): Carousel caption

        Returns:
            str: Carousel ID

        Raises:
            Exception: If carousel creation fails
        """

        def _sync_create_carousel():
            data = {
                "media_type": "CAROUSEL",
                "children": ",".join(media_ids),
            }

            if caption:
                data["caption"] = caption

            response = self.post_object(object_id=object_id, connection="media", data=data)
            return response["id"]

        carousel_id = await asyncio.to_thread(_sync_create_carousel)
        await self.wait_for_media_container(carousel_id)
        return carousel_id

    async def publish_media(self, object_id: str, creation_id: str) -> str:
        """
        Publish created media to Instagram.

        Args:
            object_id (str): Instagram object ID
            creation_id (str): Media creation ID

        Returns:
            str: Published post ID

        Raises:
            Exception: If media publishing fails
        """
        await self.wait_for_media_container(creation_id)

        def _sync_publish_media():
            data = {
                "creation_id": creation_id,
            }

            response = self.post_object(object_id=object_id, connection="media_publish", data=data)
            return response["id"]

        return await asyncio.to_thread(_sync_publish_media)

    async def create_post(
        self,
        object_id: str,
        image_url: Optional[str] = None,
        video_url: Optional[str] = None,
        caption: Optional[str] = None,
        media_type: Optional[str] = None,
    ) -> str:
        """
        Create and publish an Instagram post in one operation.

        Args:
            object_id (str): Instagram object ID
            image_url (str, optional): Image URL
            video_url (str, optional): Video URL
            caption (str, optional): Post caption
            media_type (str, optional): Media type (REELS, STORIES)

        Returns:
            str: Published post ID

        Raises:
            Exception: If post creation fails
        """
        # Create media first
        media_id = await self.create_media(
            object_id=object_id, image_url=image_url, video_url=video_url, caption=caption, media_type=media_type
        )

        # Then publish it
        return await self.publish_media(object_id=object_id, creation_id=media_id)

    async def get_user_media(self, object_id: str, fields: Optional[str] = None, limit: int = 25) -> Dict[str, Any]:
        """
        Get user's Instagram media.

        Args:
            object_id (str): Instagram object ID
            fields (str, optional): Fields to retrieve
            limit (int): Number of media items to retrieve

        Returns:
            dict: Media data from Instagram API

        Raises:
            Exception: If get fails
        """

        def _sync_get_user_media():
            default_fields = "id,caption,media_type,media_url,permalink,timestamp"
            query_fields = fields or default_fields

            if not self.graph_api:
                raise Exception("Instagram API client not initialized")
            return self.graph_api.get_object(object_id=f"{object_id}/media", fields=query_fields, limit=limit)

        return await asyncio.to_thread(_sync_get_user_media)
