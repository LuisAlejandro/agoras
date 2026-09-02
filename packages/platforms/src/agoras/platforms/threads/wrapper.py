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
"""agoras.platforms.threads.wrapper module."""

import asyncio
from typing import Any, Dict, List, Optional

from agoras.core.interfaces import SocialNetwork, _entry_images
from agoras.core.text_limits import validate_text
from agoras.core.threading import (
    ThreadPublishError,
    ThreadResult,
    partial_result,
    success_result,
)
from agoras.platforms.threads.client import ThreadsContainerTimeoutError

from .api import ThreadsAPI


def _compose_post_text(entry: Dict[str, Any]) -> str:
    """Build Threads post text from entry text, link, and optional video_title."""
    text = entry.get("text") or ""
    link = entry.get("link") or ""
    video_title = entry.get("video_title") or ""
    video_url = entry.get("video_url")
    if video_url and video_title and not text:
        text = video_title
    return f"{text} {link}".strip()


def _is_uncertain_publish_error(exc: BaseException) -> bool:
    """Classify timeout/uncertain errors after a publish dispatch."""
    if isinstance(exc, (TimeoutError, asyncio.TimeoutError, ThreadsContainerTimeoutError)):
        return True
    message = str(exc).lower()
    return any(token in message for token in ("timeout", "timed out", "not ready after"))


class Threads(SocialNetwork):
    """
    Threads social network implementation.

    This class provides Threads-specific functionality for posting messages,
    images, videos, replies, and managing Threads interactions asynchronously.
    """

    # Pure-proxy platform: delete_reply/get_reply delegate to delete/get_post
    _proxy_delete_reply = True
    _proxy_get_reply = True

    def __init__(self, **kwargs):
        """
        Initialize Threads instance.

        Args:
            **kwargs: Configuration parameters including:
                - threads_app_id: Threads (Meta) app ID
                - threads_app_secret: Threads (Meta) app secret
                - threads_refresh_token: Threads refresh token
                - threads_who_can_reply: Who can reply setting
                - threads_post_id: Post ID for share actions
        """
        # Map platform-specific key to generic key for core interface compatibility
        if "threads_post_id" in kwargs:
            kwargs["post_id"] = kwargs["threads_post_id"]
        if "threads_video_url" in kwargs:
            kwargs["video_url"] = kwargs["threads_video_url"]

        super().__init__(**kwargs)
        self.threads_app_id = None
        self.threads_app_secret = None
        self.threads_refresh_token = None
        self.threads_who_can_reply = None
        # Action-specific attributes
        self.threads_post_id = None

    async def _initialize_client(self):
        """
        Initialize Threads API client.

        Tries to load credentials from CLI params, environment variables, or storage.
        """
        # Try params/environment first
        self.threads_app_id = self._get_auth_config_value("threads_app_id", "THREADS_APP_ID")
        self.threads_app_secret = self._get_auth_config_value("threads_app_secret", "THREADS_APP_SECRET")
        self.threads_refresh_token = self._get_auth_config_value("threads_refresh_token", "THREADS_REFRESH_TOKEN")
        # Configuration options
        self.threads_who_can_reply = (
            self._get_config_value("threads_who_can_reply", "THREADS_WHO_CAN_REPLY") or "everyone"
        )
        # Action-specific attributes
        self.threads_post_id = self._get_config_value("threads_post_id", "THREADS_POST_ID")

        # If credentials not provided, try loading from storage
        # Threads needs app_id, app_secret, and refresh_token to authenticate
        if not all([self.threads_app_id, self.threads_app_secret, self.threads_refresh_token]):
            from .auth import ThreadsAuthManager

            auth_manager = ThreadsAuthManager(
                app_id=self.threads_app_id or "",
                app_secret=self.threads_app_secret or "",
                profile=self._get_config_value("profile"),
            )

            if auth_manager._load_credentials_from_storage():
                # Fill in missing credentials from storage
                if not self.threads_app_id:
                    self.threads_app_id = auth_manager.app_id
                if not self.threads_app_secret:
                    self.threads_app_secret = auth_manager.app_secret
                if not self.threads_refresh_token:
                    self.threads_refresh_token = auth_manager.refresh_token

        # Validate all credentials are now available
        if not all([self.threads_app_id, self.threads_app_secret, self.threads_refresh_token]):
            raise Exception("Not authenticated. Please run 'agoras threads authorize' first.")

        app_id = self.threads_app_id
        app_secret = self.threads_app_secret
        refresh_token = self.threads_refresh_token
        if not app_id or not app_secret or not refresh_token:
            raise Exception("Not authenticated. Please run 'agoras threads authorize' first.")

        # Initialize Threads API
        self.api = ThreadsAPI(app_id, app_secret, refresh_token)

        # Authenticate with provided credentials
        await self.api.authenticate()

    async def post(
        self,
        status_text,
        status_link,
        status_image_url_1=None,
        status_image_url_2=None,
        status_image_url_3=None,
        status_image_url_4=None,
    ):
        """
        Create a post on Threads.

        Args:
            status_text (str): Text content of the post
            status_link (str): URL to include in the post
            status_image_url_1 (str, optional): First image URL
            status_image_url_2 (str, optional): Second image URL
            status_image_url_3 (str, optional): Third image URL
            status_image_url_4 (str, optional): Fourth image URL

        Returns:
            str: Post ID
        """
        self._require_api()

        # Combine text and link
        post_text = f"{status_text} {status_link}".strip()
        validate_text("threads", "text", post_text)

        # Collect media files
        files = list(filter(None, [status_image_url_1, status_image_url_2, status_image_url_3, status_image_url_4]))

        # Call ThreadsAPI.create_post() which handles Media system validation
        post_id = await self.api.create_post(
            post_text, files if files else None, who_can_reply=self.threads_who_can_reply or "everyone"
        )

        self._output_status(post_id)
        return post_id

    async def thread(self, entries, **kwargs) -> ThreadResult:
        """
        Publish an ordered reply-chain thread on Meta Threads.

        Args:
            entries: Ordered entry mappings (text/link/images/video)
            **kwargs: May include who_can_reply

        Returns:
            ThreadResult: Structured success result

        Raises:
            ThreadPublishError: On partial or failed publish with structured result
        """
        self._require_api()

        if not entries or not isinstance(entries, list):
            raise Exception("Thread entries are required.")

        who_can_reply = kwargs.get("who_can_reply") or self.threads_who_can_reply or "everyone"

        prepared: List[Dict[str, Any]] = []
        for entry in entries:
            if not isinstance(entry, dict):
                raise Exception("Each thread entry must be a mapping.")
            images = _entry_images(entry)
            video_url = entry.get("video_url")
            if images and video_url:
                raise Exception("Images and video_url are mutually exclusive in a thread entry.")
            post_text = _compose_post_text(entry)
            if not post_text and not images and not video_url:
                raise Exception("Thread entry requires text, link, images, or video_url.")
            if post_text:
                validate_text("threads", "text", post_text)
            alt_texts = entry.get("alt_texts")
            if alt_texts is not None and not isinstance(alt_texts, list):
                raise Exception("alt_texts must be a list when provided.")
            prepared.append(
                {
                    "text": post_text,
                    "images": images,
                    "video_url": video_url,
                    "alt_texts": alt_texts,
                }
            )

        ids: List[str] = []
        previous_id: Optional[str] = None
        for index, item in enumerate(prepared):
            try:
                if item["video_url"]:
                    post_id = await self.api.create_video_post(
                        item["text"],
                        item["video_url"],
                        who_can_reply=who_can_reply,
                        reply_to_id=previous_id,
                    )
                else:
                    post_id = await self.api.create_post(
                        item["text"],
                        files=item["images"] or None,
                        file_captions=item["alt_texts"],
                        who_can_reply=who_can_reply,
                        reply_to_id=previous_id,
                    )
            except Exception as exc:
                outcome = "unknown" if _is_uncertain_publish_error(exc) else "failed"
                result = partial_result(
                    ids,
                    failed_index=index,
                    outcome=outcome,
                    error=str(exc),
                )
                raise ThreadPublishError(result) from exc

            ids.append(str(post_id))
            previous_id = str(post_id)

        return success_result(ids)

    async def like(self, post_id):
        """
        Like a Threads post (not supported via API).

        Args:
            post_id (str): Post ID to like

        Raises:
            Exception: Like not supported for Threads
        """
        raise Exception("Like not supported for Threads")

    async def delete(self, post_id):
        """
        Delete a Threads post.

        Args:
            post_id (str): Post ID to delete

        Returns:
            str: Deleted post ID
        """
        self._require_api()

        if not post_id:
            post_id = self.threads_post_id

        if not post_id:
            raise Exception("Post ID is required for delete action.")

        result = await self.api.delete(post_id)
        self._output_status(result)
        return result

    async def get_post(self, post_id):
        """
        Read a Threads post by ID and return normalized content.

        Args:
            post_id (str): Post ID to read

        Returns:
            dict: Normalized content
        """
        self._require_api()

        if not post_id:
            raise Exception("Post ID is required for get-post action.")

        raw = await self.api.get_post(post_id)
        media = []
        media_url = raw.get("media_url")
        media_type = (raw.get("media_type") or "").upper()
        if media_url:
            media.append(
                {
                    "type": "video" if media_type in ("VIDEO", "REELS") else "image",
                    "url": media_url,
                }
            )
        username = raw.get("username")
        content = {
            "id": str(raw.get("id", post_id)),
            "text": raw.get("text"),
            "media": media,
            "author": {"id": None, "name": username} if username else None,
            "created_at": raw.get("timestamp"),
            "metadata": {"permalink": raw.get("permalink")} if raw.get("permalink") else {},
        }
        self._output_content(content)
        return content

    async def list_posts(self, limit):
        """
        List the authenticated user's recent posts and return normalized content.

        Args:
            limit (int): Maximum number of posts to return

        Returns:
            list: Normalized content dicts
        """
        self._require_api()

        if limit == 0:
            self._output_list([])
            return []

        raw_items = await self.api.list_posts(limit)
        items = []
        for raw in raw_items:
            media = []
            media_url = raw.get("media_url")
            media_type = (raw.get("media_type") or "").upper()
            if media_url:
                media.append(
                    {
                        "type": "video" if media_type in ("VIDEO", "REELS") else "image",
                        "url": media_url,
                    }
                )
            username = raw.get("username")
            items.append(
                {
                    "id": str(raw.get("id")),
                    "text": raw.get("text"),
                    "media": media,
                    "author": {"id": None, "name": username} if username else None,
                    "created_at": raw.get("timestamp"),
                    "metadata": {"permalink": raw.get("permalink")} if raw.get("permalink") else {},
                }
            )
        self._output_list(items)
        return items

    async def share(self, post_id):
        """
        Share/repost a Threads post.

        Args:
            post_id (str): Post ID to share/repost

        Returns:
            str: Repost ID
        """
        self._require_api()

        # Get post_id from parameter or instance attribute
        if not post_id:
            post_id = self.threads_post_id

        if not post_id:
            raise Exception("Post ID is required for share action.")

        repost_id = await self.api.repost_post(post_id)
        self._output_status(repost_id)
        return repost_id

    # Override action handlers to use Threads-specific parameter names
    async def _handle_post_action(self):
        """Handle post action with Threads-specific parameter extraction."""
        status_text = self._get_config_value("status_text", "STATUS_TEXT") or ""
        status_link = self._get_config_value("status_link", "STATUS_LINK") or ""
        status_image_url_1 = self._get_config_value("status_image_url_1", "STATUS_IMAGE_URL_1")
        status_image_url_2 = self._get_config_value("status_image_url_2", "STATUS_IMAGE_URL_2")
        status_image_url_3 = self._get_config_value("status_image_url_3", "STATUS_IMAGE_URL_3")
        status_image_url_4 = self._get_config_value("status_image_url_4", "STATUS_IMAGE_URL_4")

        await self.post(
            status_text, status_link, status_image_url_1, status_image_url_2, status_image_url_3, status_image_url_4
        )

    async def _handle_share_action(self):
        """Handle share action with Threads-specific parameter extraction."""
        threads_post_id = self._get_config_value("threads_post_id", "THREADS_POST_ID")
        if not threads_post_id:
            raise Exception("Threads post ID is required for share action.")
        await self.share(threads_post_id)

    async def _handle_like_action(self):
        """Handle like action - not supported for Threads."""
        await self.like(None)

    async def _handle_delete_action(self):
        """Handle delete action with Threads-specific parameter extraction."""
        threads_post_id = self._get_config_value("threads_post_id", "THREADS_POST_ID")
        if not threads_post_id:
            raise Exception("Threads post ID is required for delete action.")
        await self.delete(threads_post_id)

    async def video(self, status_text, video_url, video_title):
        """
        Post a video to Threads.

        Args:
            status_text (str): Text content to accompany the video
            video_url (str): URL of the video to post
            video_title (str): Title / caption for the video

        Returns:
            str: Post ID
        """
        self._require_api()

        if not video_url:
            raise Exception("Threads video URL is required.")

        post_text = status_text or video_title or ""
        validate_text("threads", "text", post_text)

        post_id = await self.api.create_video_post(
            post_text, video_url, who_can_reply=self.threads_who_can_reply or "everyone"
        )

        self._output_status(post_id)
        return post_id

    async def reply(
        self,
        post_id,
        text,
        status_image_url_1=None,
        status_image_url_2=None,
        status_image_url_3=None,
        status_image_url_4=None,
        video_url=None,
    ):
        """
        Reply to a Threads post with optional media.

        Args:
            post_id (str): ID of the Threads post to reply to
            text (str): Reply text
            status_image_url_1 (str, optional): First image URL
            status_image_url_2 (str, optional): Second image URL
            status_image_url_3 (str, optional): Third image URL
            status_image_url_4 (str, optional): Fourth image URL
            video_url (str, optional): URL of a video to attach to the reply

        Returns:
            str: Reply post ID
        """
        self._require_api()

        if not post_id:
            raise Exception("Threads post ID is required for reply action.")

        files = list(filter(None, [status_image_url_1, status_image_url_2, status_image_url_3, status_image_url_4]))

        if not files and not text and not video_url:
            raise Exception("No reply text or media provided.")

        post_text = text or ""
        validate_text("threads", "text", post_text)

        if video_url:
            reply_id = await self.api.create_video_post(
                post_text,
                video_url,
                who_can_reply=self.threads_who_can_reply or "everyone",
                reply_to_id=post_id,
            )
        else:
            reply_id = await self.api.create_post(
                post_text,
                files=files if files else None,
                who_can_reply=self.threads_who_can_reply or "everyone",
                reply_to_id=post_id,
            )

        self._output_status(reply_id)
        return reply_id

    async def _handle_video_action(self):
        """Handle video action with Threads-specific parameter extraction."""
        video_url = self._get_config_value("threads_video_url", "THREADS_VIDEO_URL")
        video_title = self._get_config_value("threads_video_title", "THREADS_VIDEO_TITLE") or ""
        status_text = self._get_config_value("status_text", "STATUS_TEXT") or video_title

        if not video_url:
            raise Exception("Threads video URL is required for video action.")

        await self.video(status_text, video_url, video_title)

    async def authorize_credentials(self):
        """
        Authorize and store Threads credentials for future use.

        Returns:
            bool: True if authorization successful
        """
        from .auth import ThreadsAuthManager

        app_id = self._get_config_value("threads_app_id", "THREADS_APP_ID")
        app_secret = self._get_config_value("threads_app_secret", "THREADS_APP_SECRET")

        auth_manager = ThreadsAuthManager(
            app_id=app_id,
            app_secret=app_secret,
            profile=self._get_config_value("profile"),
        )

        result = await auth_manager.authorize()
        if result:
            print(result)
            return True
        return False

    async def execute_action(self, action):
        """
        Execute the specified action asynchronously.

        Args:
            action (str): Action to execute

        Raises:
            Exception: If action is not supported or required arguments missing
        """
        if action == "":
            raise Exception("Action is a required argument.")

        # Initialize client before executing other actions
        await self._initialize_client()

        handlers = {
            "post": self._handle_post_action,
            "like": self._handle_like_action,
            "share": self._handle_share_action,
            "delete": self._handle_delete_action,
            "video": self._handle_video_action,
            "thread": self._handle_thread_action,
            "reply": self._handle_reply_action,
            "delete-reply": self._handle_delete_reply_action,
            "get-post": self._handle_get_post_action,
            "get-reply": self._handle_get_reply_action,
            "list-posts": self._handle_list_posts_action,
            "last-from-feed": self._handle_last_from_feed_action,
            "random-from-feed": self._handle_random_from_feed_action,
            "schedule": self._handle_schedule_action,
        }
        handler = handlers.get(action)
        if handler is None:
            raise Exception(f'"{action}" action not supported.')
        await handler()


async def main_async(kwargs):
    """
    Async main function to execute Threads actions.

    Thin shim: delegates to the base template runner via unbound dispatch,
    so test mocks of ``Threads`` (which stub ``execute_action``/``disconnect``/
    ``authorize_credentials`` but not the base method) keep working. The
    name is kept module-level because tests and the CLI import it.

    Args:
        kwargs (dict): Configuration arguments
    """
    instance = Threads(**kwargs)
    return await SocialNetwork.run_main_async(instance, kwargs)


def main(kwargs):
    """
    Main function to execute Threads actions (for backwards compatibility).

    Thin shim kept module-level because the CLI imports it.

    Args:
        kwargs (dict): Configuration arguments
    """
    asyncio.run(main_async(kwargs))
