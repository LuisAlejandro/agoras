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
"""agoras.platforms.threads.client module."""

import time
from typing import Any, Dict, List, Optional

import requests

# Bounded container readiness poll (~5 minutes at 5s intervals).
VIDEO_POLL_INTERVAL_S = 5
VIDEO_POLL_MAX_WAIT_S = 300
CONTAINER_READY_STATUSES = frozenset({"FINISHED", "PUBLISHED"})
CONTAINER_FAILED_STATUSES = frozenset({"ERROR", "EXPIRED"})


class ThreadsContainerTimeoutError(Exception):
    """Raised when container processing does not finish within the poll budget."""


class ThreadsAPIClient:
    """
    Threads API client for making HTTP requests to Threads endpoints.

    Centralizes all Threads API calls including authentication, content publishing,
    and user profile operations using Meta's Threads Graph API.
    """

    def __init__(self, access_token: str, user_id: str):
        """
        Initialize Threads API client.

        Args:
            access_token (str): Threads access token for authenticated requests
            user_id (str): Threads user ID for API operations
        """
        self.access_token = access_token
        self.user_id = user_id
        self.base_url = "https://graph.threads.net/v1.0"

    def get_profile(self) -> Dict[str, Any]:
        """
        Get user profile information from Threads API.

        Returns:
            dict: User profile information containing user_id and token validity

        Raises:
            Exception: If API call fails or not authenticated
        """
        if not self.access_token:
            raise Exception("No access token available")

        if not self.user_id:
            raise Exception("No user ID available")

        try:
            # Return basic info we have (no API call needed for profile)
            profile_data = {"user_id": self.user_id, "access_token_valid": bool(self.access_token)}

            return profile_data
        except Exception as e:
            raise Exception(f"Failed to get profile: {str(e)}")

    def _wait_for_container_ready(self, creation_id: str) -> None:
        """
        Poll container status until ready, failed, or timeout.

        Args:
            creation_id (str): Container creation ID

        Raises:
            Exception: On terminal ERROR/EXPIRED status
            ThreadsContainerTimeoutError: If readiness is not reached in time
        """
        deadline = time.monotonic() + VIDEO_POLL_MAX_WAIT_S
        status = "IN_PROGRESS"
        while status not in CONTAINER_READY_STATUSES:
            if time.monotonic() >= deadline:
                raise ThreadsContainerTimeoutError(
                    f"Threads container {creation_id} not ready after {VIDEO_POLL_MAX_WAIT_S}s"
                )
            time.sleep(VIDEO_POLL_INTERVAL_S)
            status_resp = requests.get(
                f"{self.base_url}/{creation_id}",
                params={"fields": "status", "access_token": self.access_token},
                timeout=30,
            )
            self._check_response(status_resp)
            status = status_resp.json().get("status", "")
            if status in CONTAINER_FAILED_STATUSES:
                raise Exception(f"Threads video processing failed with status {status}")

    def _publish_container(self, creation_id: str) -> Dict[str, Any]:
        """Publish a ready container and return the published media ID payload."""
        publish_data = {"access_token": self.access_token, "creation_id": creation_id}
        publish_resp = requests.post(f"{self.base_url}/{self.user_id}/threads_publish", data=publish_data, timeout=30)
        self._check_response(publish_resp)
        # Always return the published media id from the publish response — never the container id.
        return {"id": publish_resp.json()["id"]}

    def create_post(
        self,
        post_text: str,
        files: Optional[List[str]] = None,
        file_captions: Optional[List[str]] = None,
        who_can_reply: str = "everyone",
        reply_to_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Create a post on Threads using Meta's Graph API.

        Args:
            post_text (str): Text content of the post
            files (list, optional): List of file URLs to attach
            file_captions (list, optional): Captions for files
            who_can_reply (str): Who can reply to this post
            reply_to_id (str, optional): Published media ID to reply to

        Returns:
            dict: Post creation response with published media id

        Raises:
            Exception: If post creation fails or not authenticated
        """
        if not self.access_token:
            raise Exception("No access token available")

        if not self.user_id:
            raise Exception("No user ID available")

        files = files or []
        file_captions = file_captions or []

        try:
            # Determine post type and build container creation data
            container_data = {"access_token": self.access_token, "text": post_text, "reply_control": who_can_reply}
            if reply_to_id:
                container_data["reply_to_id"] = reply_to_id

            if len(files) == 0:
                # Text-only post
                container_data["media_type"] = "TEXT"
            elif len(files) == 1:
                # Single image post
                container_data["media_type"] = "IMAGE"
                container_data["image_url"] = files[0]
                if file_captions and file_captions[0]:
                    container_data["alt_text"] = file_captions[0]
            else:
                # Carousel post (2-4 images)
                # First create individual carousel item containers
                item_ids = []
                for idx, image_url in enumerate(files):
                    item_data = {
                        "access_token": self.access_token,
                        "media_type": "IMAGE",
                        "image_url": image_url,
                        "is_carousel_item": True,
                    }
                    if file_captions and idx < len(file_captions) and file_captions[idx]:
                        item_data["alt_text"] = file_captions[idx]
                    resp = requests.post(f"{self.base_url}/me/threads", data=item_data, timeout=30)
                    self._check_response(resp)
                    item_ids.append(resp.json()["id"])

                # Now create the carousel container
                container_data["media_type"] = "CAROUSEL"
                container_data["children"] = ",".join(item_ids)

            # Create the container
            resp = requests.post(f"{self.base_url}/me/threads", data=container_data, timeout=30)
            self._check_response(resp)
            creation_id = resp.json()["id"]

            # Short bounded readiness wait for image/text containers
            time.sleep(min(2, VIDEO_POLL_INTERVAL_S))

            return self._publish_container(creation_id)

        except ThreadsContainerTimeoutError:
            raise
        except Exception as e:
            raise Exception(f"Failed to create post: {str(e)}")

    def _check_response(self, response: requests.Response):
        """Check API response for errors and raise appropriate exceptions."""
        if response.status_code != 200:
            try:
                error_data = response.json()
                if "error" in error_data:
                    raise Exception(f"API error: {error_data['error'].get('message', str(error_data))}")
            except ValueError:
                pass
            raise Exception(f"HTTP {response.status_code}: {response.text}")

    def create_video_post(
        self,
        post_text: str,
        video_url: str,
        who_can_reply: str = "everyone",
        reply_to_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Create a video post on Threads using Meta's Graph API.

        Args:
            post_text (str): Text content / caption for the video
            video_url (str): Publicly accessible URL of the video
            who_can_reply (str): Who can reply to this post
            reply_to_id (str, optional): Published media ID to reply to

        Returns:
            dict: Post creation response with published media id

        Raises:
            Exception: If video post creation fails or not authenticated
            ThreadsContainerTimeoutError: If processing does not finish in time
        """
        if not self.access_token:
            raise Exception("No access token available")

        if not self.user_id:
            raise Exception("No user ID available")

        if not video_url:
            raise Exception("Video URL is required")

        try:
            container_data = {
                "access_token": self.access_token,
                "text": post_text,
                "reply_control": who_can_reply,
                "media_type": "VIDEO",
                "video_url": video_url,
            }
            if reply_to_id:
                container_data["reply_to_id"] = reply_to_id

            resp = requests.post(f"{self.base_url}/me/threads", data=container_data, timeout=30)
            self._check_response(resp)
            creation_id = resp.json()["id"]

            self._wait_for_container_ready(creation_id)
            return self._publish_container(creation_id)

        except ThreadsContainerTimeoutError:
            raise
        except Exception as e:
            raise Exception(f"Failed to create video post: {str(e)}")

    def repost_post(self, post_id: str) -> Dict[str, Any]:
        """
        Repost an existing post using Meta's Graph API.

        Args:
            post_id (str): ID of the post to repost

        Returns:
            dict: Repost response

        Raises:
            Exception: If repost fails or not authenticated
        """
        if not self.access_token:
            raise Exception("No access token available")

        if not self.user_id:
            raise Exception("No user ID available")

        try:
            data = {"access_token": self.access_token}

            response = requests.post(f"{self.base_url}/{post_id}/repost", data=data, timeout=30)
            self._check_response(response)

            return {"id": response.json()["id"]}
        except Exception as e:
            raise Exception(f"Failed to repost: {str(e)}")

    def delete_post(self, post_id: str) -> Dict[str, Any]:
        """
        Delete a published Threads post.

        Args:
            post_id (str): ID of the post to delete

        Returns:
            dict: Deletion response containing the post ID

        Raises:
            Exception: If deletion fails or not authenticated
        """
        if not self.access_token:
            raise Exception("No access token available")

        if not post_id:
            raise Exception("Post ID is required")

        try:
            response = requests.delete(
                f"{self.base_url}/{post_id}", params={"access_token": self.access_token}, timeout=30
            )
            if response.status_code not in (200, 204):
                self._check_response(response)

            return {"id": post_id}
        except Exception as e:
            raise Exception(f"Failed to delete post: {str(e)}")
