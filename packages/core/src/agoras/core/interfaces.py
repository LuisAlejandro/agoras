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
"""
Core interfaces and shared social network abstractions for Agoras.
"""

import asyncio
import datetime
import json
import os
import sys
from abc import ABC, abstractmethod
from typing import Any, Dict, List

from agoras.core.feed import Feed
from agoras.core.sheet import ScheduleSheet
from agoras.media import create_video, download_images
from agoras.media.constraints import resolve_platform


def _entry_images(entry: Dict[str, Any]) -> List[str]:
    """Collect flattened image_1..image_4 URLs from a thread entry."""
    return list(
        filter(
            None,
            [
                entry.get("image_1"),
                entry.get("image_2"),
                entry.get("image_3"),
                entry.get("image_4"),
            ],
        )
    )


def _is_uncertain_publish_error(exc: BaseException) -> bool:
    """Classify timeout/uncertain errors after a publish dispatch."""
    if isinstance(exc, (TimeoutError, asyncio.TimeoutError)):
        return True
    message = str(exc).lower()
    return any(token in message for token in ("timeout", "timed out", "temporarily unavailable"))


class SocialNetwork(ABC):
    """
    Abstract base class for social network implementations.

    This class provides common functionality and defines the interface
    that all social network implementations must follow. All methods
    are asynchronous by default.
    """

    def __init__(self, **kwargs):
        """
        Initialize the social network instance with configuration.

        Args:
            **kwargs: Configuration parameters specific to each social network
        """
        self.config = kwargs
        self.client = None
        self.api: Any = None

    @abstractmethod
    async def _initialize_client(self):
        """
        Initialize the API client for the specific social network.

        This method must be implemented by each social network to set up
        their specific API clients and authentication.
        """

    async def disconnect(self):
        """
        Disconnect from the social network.
        """
        if self.api:
            await self.api.disconnect()

    def _require_api(self):
        """
        Raise the platform's not-initialized message when no api is available.

        Guard-phase helper replacing the per-platform
        ``if not self.api: raise Exception("<Platform> API not initialized")``
        pairs. The message matches the historical per-platform text.
        """
        if not self.api:
            raise Exception(f"{self.__class__.__name__} API not initialized")

    async def authorize_credentials(self):
        """
        Authorize credentials for the social network.

        Default implementation raises not supported. Platforms that support
        interactive credential authorization override this.

        Returns:
            bool: True if authorization succeeded

        Raises:
            Exception: If authorization is not supported
        """
        raise Exception(f"Authorize not supported for {self.__class__.__name__}")

    async def run_main_async(self, kwargs):
        """
        Template runner for the CLI main entry point.

        Dispatches the authorize action directly to ``authorize_credentials``
        without client initialization, and sends every other action through
        ``execute_action`` (which initializes the client internally).
        Note: the action path now guarantees ``disconnect`` on every exit,
        including failures — six platforms (facebook, instagram, linkedin,
        tiktok, youtube, telegram) historically disconnected only on success;
        this is an accepted, documented deviation from strict parity (in-memory
        auth state is cleared on failure too, and teardown errors never mask
        the action outcome). The authorize branch deliberately skips teardown
        because no ``authorize_credentials`` implementation sets ``self.api``.

        Args:
            kwargs (dict): Configuration arguments

        Returns:
            int or None: 0 if authorize succeeded, 1 if it failed,
                None for other actions
        """
        action = kwargs.get("action", "")

        if action == "":
            raise Exception("Action is a required argument.")

        if action == "authorize":
            success = await self.authorize_credentials()
            return 0 if success else 1

        try:
            await self.execute_action(action)
        finally:
            try:
                await self.disconnect()
            except Exception:
                # Teardown must never replace the action's outcome or exception.
                print("Warning: disconnect failed after action execution.", file=sys.stderr)
        return None

    @abstractmethod
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
        Create a post on the social network.

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

    @abstractmethod
    async def like(self, post_id):
        """
        Like/react to a post.

        Args:
            post_id (str): ID of the post to like

        Returns:
            str: Post ID
        """

    @abstractmethod
    async def delete(self, post_id):
        """
        Delete a post.

        Args:
            post_id (str): ID of the post to delete

        Returns:
            str: Post ID
        """

    @abstractmethod
    async def share(self, post_id):
        """
        Share/retweet a post.

        Args:
            post_id (str): ID of the post to share

        Returns:
            str: Post ID
        """

    async def video(self, status_text, video_url, video_title):
        """
        Post a video. Default implementation raises not supported error.

        Args:
            status_text (str): Text content to accompany the video
            video_url (str): URL of the video to post
            video_title (str): Title of the video

        Returns:
            str: Post ID

        Raises:
            Exception: If video posting is not supported
        """
        raise Exception(f"Video posting not supported for {self.__class__.__name__}")

    async def thread(self, entries, **kwargs):
        """
        Publish an ordered multi-entry thread.

        Default implementation raises not supported. Platforms that support
        threads override this and return a ThreadResult without printing
        intermediate single-post JSON lines.

        Args:
            entries (list): Ordered entry mappings (text/link/images/video fields)
            **kwargs: Platform-specific options (e.g. thread_name for Discord)

        Returns:
            ThreadResult: Structured success or partial result
        """
        raise Exception(f"Thread publishing not supported for {self.__class__.__name__}")

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
        Reply to a post/message on the social network.

        Default implementation raises not supported. Platforms that support
        replying (commenting on a post, replying to a message) override this
        and return the created reply/comment ID.

        Args:
            post_id (str): ID of the post/message to reply to
            text (str): Reply/comment text
            status_image_url_1 (str, optional): First image URL
            status_image_url_2 (str, optional): Second image URL
            status_image_url_3 (str, optional): Third image URL
            status_image_url_4 (str, optional): Fourth image URL
            video_url (str, optional): URL of a video to attach to the reply

        Returns:
            str: Reply/comment ID

        Raises:
            Exception: If replying is not supported
        """
        raise Exception(f"Reply not supported for {self.__class__.__name__}")

    async def delete_reply(self, post_id):
        """
        Delete a reply/comment on the social network.

        Default implementation raises not supported. Platforms that support
        deleting a reply (a comment on a post, or a reply message) override
        this and return the deleted reply/comment ID. Pure-proxy platforms
        set ``_proxy_delete_reply = True`` to delegate to ``delete``.

        Args:
            post_id (str): ID of the reply/comment to delete

        Returns:
            str: Deleted reply/comment ID

        Raises:
            Exception: If deleting a reply is not supported
        """
        if getattr(self, "_proxy_delete_reply", False):
            return await self.delete(post_id)
        raise Exception(f"Delete reply not supported for {self.__class__.__name__}")

    async def get_post(self, post_id):
        """
        Read a post/message by ID and return its normalized content.

        Default implementation raises not supported. Platforms that support
        reading a post override this and return a normalized content dict.

        Args:
            post_id (str): ID of the post/message to read

        Returns:
            dict: Normalized content (id, text, media, author, created_at, metadata)

        Raises:
            Exception: If reading a post is not supported
        """
        raise Exception(f"Get post not supported for {self.__class__.__name__}")

    async def get_reply(self, post_id):
        """
        Read a reply/comment by ID and return its normalized content.

        Default implementation raises not supported. Platforms that support
        reading a reply override this and return a normalized content dict.
        Pure-proxy platforms set ``_proxy_get_reply = True`` to delegate
        to ``get_post``.

        Args:
            post_id (str): ID of the reply/comment to read

        Returns:
            dict: Normalized content (id, text, media, author, created_at, metadata)

        Raises:
            Exception: If reading a reply is not supported
        """
        if getattr(self, "_proxy_get_reply", False):
            return await self.get_post(post_id)
        raise Exception(f"Get reply not supported for {self.__class__.__name__}")

    async def list_posts(self, limit):
        """
        List the account's recent posts and return a list of normalized content.

        Default implementation raises not supported. Platforms that support
        listing posts override this and return a list of normalized content
        dicts.

        Args:
            limit (int): Maximum number of posts to return

        Returns:
            list: Normalized content dicts (id, text, media, author, created_at, metadata)

        Raises:
            Exception: If listing posts is not supported
        """
        raise Exception(f"List posts not supported for {self.__class__.__name__}")

    def get_platform_name(self):
        """
        Get the platform name for media handling.

        Returns:
            str: Platform name (class name without 'Network' suffix if present)
        """
        name = self.__class__.__name__
        if name.endswith("Network"):
            return name[:-7]  # Remove 'Network' suffix
        return name

    async def download_images(self, image_urls):
        """
        Download multiple images using the Media system.

        Args:
            image_urls (list): List of image URLs

        Returns:
            list: List of downloaded Image instances
        """
        platform = resolve_platform(self.get_platform_name())
        return await download_images(image_urls, platform=platform)

    async def download_video(self, video_url):
        """
        Download video using the Media system with platform-specific limits.

        Args:
            video_url (str): Video URL

        Returns:
            Video: Downloaded Video instance
        """
        platform = resolve_platform(self.get_platform_name())
        video = create_video(video_url, platform)
        await video.download()
        return video

    async def download_feed(self, feed_url):
        """
        Download and parse RSS feed using the Feed system.

        Args:
            feed_url (str): RSS feed URL

        Returns:
            Feed: Downloaded Feed instance
        """
        feed = Feed(feed_url)
        await feed.download()
        return feed

    async def create_schedule_sheet(
        self, google_sheets_id, google_sheets_name, google_sheets_client_email, google_sheets_private_key
    ):
        """
        Create a ScheduleSheet instance with proper configuration.

        Args:
            google_sheets_id (str): Google Sheets document ID
            google_sheets_name (str): Worksheet name
            google_sheets_client_email (str): Service account email
            google_sheets_private_key (str): Service account private key

        Returns:
            ScheduleSheet: Configured schedule sheet instance
        """
        # Clean up private key format
        if google_sheets_private_key:
            google_sheets_private_key = google_sheets_private_key.replace("\\n", "\n")

        sheet = ScheduleSheet(
            google_sheets_id, google_sheets_client_email, google_sheets_private_key, google_sheets_name
        )

        await sheet.authenticate()
        await sheet.get_worksheet()

        return sheet

    async def last_from_feed(self, feed_url, max_count, post_lookback):
        """
        Post recent items from RSS feed asynchronously.

        Args:
            feed_url (str): URL of the RSS feed
            max_count (int): Maximum number of posts to create
            post_lookback (int): Lookback period in seconds
        """
        feed = await self.download_feed(feed_url)
        recent_items = feed.get_items_since(post_lookback)

        count = 0
        today = datetime.datetime.now()

        for item in recent_items:
            if count >= max_count:
                break

            status_link = item.get_timestamped_link(today.strftime("%Y%m%d%H%M%S")) if item.link else ""
            status_title = item.title
            status_image = item.image_url

            count += 1
            try:
                await self.post(status_title, status_link, status_image)
            except Exception as exc:
                print(f"Feed item failed ({count}): {exc}", file=sys.stderr)

    async def random_from_feed(self, feed_url, max_post_age):
        """
        Post a random item from RSS feed asynchronously.

        Args:
            feed_url (str): URL of the RSS feed
            max_post_age (int): Maximum age of posts in days
        """
        feed = await self.download_feed(feed_url)
        random_item = feed.get_random_item(max_post_age)

        today = datetime.datetime.now()
        status_link = random_item.get_timestamped_link(today.strftime("%Y%m%d%H%M%S")) if random_item.link else ""
        status_title = random_item.title
        status_image = random_item.image_url

        await self.post(status_title, status_link, status_image)

    async def schedule(
        self, google_sheets_id, google_sheets_name, google_sheets_client_email, google_sheets_private_key, max_count
    ):
        """
        Schedule posts from Google Sheets asynchronously.

        Args:
            google_sheets_id (str): Google Sheets document ID
            google_sheets_name (str): Worksheet name
            google_sheets_client_email (str): Service account email
            google_sheets_private_key (str): Service account private key
            max_count (int): Maximum number of posts to process
        """
        # Create and configure the schedule sheet
        sheet = await self.create_schedule_sheet(
            google_sheets_id, google_sheets_name, google_sheets_client_email, google_sheets_private_key
        )

        # Process scheduled posts (selection only — not marked published yet)
        posts_to_create = await sheet.process_scheduled_posts(max_count)

        # Create posts asynchronously; mark published only after success
        for index, post_data in enumerate(posts_to_create, start=1):
            try:
                await self.post(
                    post_data["status_text"],
                    post_data["status_link"],
                    post_data["status_image_url_1"],
                    post_data["status_image_url_2"],
                    post_data["status_image_url_3"],
                    post_data["status_image_url_4"],
                )
                sheet_row = post_data.get("_sheet_row")
                if sheet_row is not None:
                    await sheet.mark_as_published(sheet_row)
            except Exception as exc:
                print(f"Scheduled item failed ({index}): {exc}", file=sys.stderr)

    def _output_status(self, post_id):
        """
        Output status response in JSON format.

        Args:
            post_id (str): ID of the created/modified post
        """
        status = {"id": post_id}
        print(json.dumps(status, separators=(",", ":")))

    @staticmethod
    def _normalize_content(content):
        """
        Normalize a content dict onto the stable get-post/get-reply schema.

        Missing fields become null (not omitted) so the key set is stable
        across networks. ``media`` defaults to an empty list; ``metadata``
        defaults to an empty dict.

        Args:
            content (dict): Partial or full content mapping

        Returns:
            dict: Normalized content with a stable key set
        """
        content = content or {}
        author = content.get("author")
        if author is None:
            author = None
        elif isinstance(author, dict):
            author = {
                "id": author.get("id"),
                "name": author.get("name"),
            }
        media = content.get("media")
        if media is None:
            media = []
        metadata = content.get("metadata")
        if metadata is None:
            metadata = {}
        return {
            "id": content.get("id"),
            "text": content.get("text"),
            "media": media,
            "author": author,
            "created_at": content.get("created_at"),
            "metadata": metadata,
        }

    def _output_content(self, content_dict):
        """
        Output full get-post/get-reply content as normalized JSON.

        Args:
            content_dict (dict): Content mapping (normalized before emit)
        """
        print(json.dumps(self._normalize_content(content_dict), separators=(",", ":")))

    def _output_list(self, items):
        """
        Output a list of normalized content items as a JSON array.

        Args:
            items (list): Content mappings (each normalized before emit)
        """
        print(json.dumps([self._normalize_content(c) for c in items], separators=(",", ":")))

    @staticmethod
    def _collect_status_image_urls(
        status_image_url_1=None,
        status_image_url_2=None,
        status_image_url_3=None,
        status_image_url_4=None,
        limit=4,
    ):
        """Collect non-empty status image URLs in order."""
        urls = [
            status_image_url_1,
            status_image_url_2,
            status_image_url_3,
            status_image_url_4,
        ][:limit]
        return [url for url in urls if url]

    def _get_config_value(self, key, env_key=None) -> Any:
        """
        Get configuration value from kwargs or environment.

        File-mode content (`_content_source=file`) never falls back to payload
        environment variables for keys present in config (including explicit
        False / empty / None). Inline mode preserves explicit False/0 and uses
        environment fallback for missing or blank values. Auth keys without a
        config entry still read from the environment.
        """
        env_key = env_key or key.upper()
        file_mode = self.config.get("_content_source") == "file"

        if key in self.config:
            value = self.config[key]
            if file_mode:
                return value
            if value is False or value == 0:
                return value
            if value is not None and value != "":
                return value
            # Blank / None in inline mode: fall through to environment

        return os.environ.get(env_key)

    def _get_auth_config_value(self, key, env_key=None) -> Any:
        """
        Get an auth credential, skipping env when a profile is selected.

        When an explicit ``--profile`` is set, the selected profile is the sole
        credential source: env is not consulted for auth keys. Without a
        profile, this falls back to the normal kwargs-then-env resolution.
        """
        if self.config.get("profile"):
            return self.config.get(key)
        return self._get_config_value(key, env_key)

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

    async def _handle_post_action(self):
        """Handle post action with common parameter extraction."""
        status_text = self._get_config_value("status_text", "STATUS_TEXT") or ""
        status_link = self._get_config_value("status_link", "STATUS_LINK") or ""
        status_image_url_1 = self._get_config_value("status_image_url_1", "STATUS_IMAGE_URL_1")
        status_image_url_2 = self._get_config_value("status_image_url_2", "STATUS_IMAGE_URL_2")
        status_image_url_3 = self._get_config_value("status_image_url_3", "STATUS_IMAGE_URL_3")
        status_image_url_4 = self._get_config_value("status_image_url_4", "STATUS_IMAGE_URL_4")

        await self.post(
            status_text, status_link, status_image_url_1, status_image_url_2, status_image_url_3, status_image_url_4
        )

    async def _handle_like_action(self):
        """Handle like action with common parameter extraction."""
        post_id = self._get_config_value("post_id")
        if not post_id:
            raise Exception("Post ID is required for like action.")
        await self.like(post_id)

    async def _handle_share_action(self):
        """Handle share action with common parameter extraction."""
        post_id = self._get_config_value("post_id")
        if not post_id:
            raise Exception("Post ID is required for share action.")
        await self.share(post_id)

    async def _handle_delete_action(self):
        """Handle delete action with common parameter extraction."""
        post_id = self._get_config_value("post_id")
        if not post_id:
            raise Exception("Post ID is required for delete action.")
        await self.delete(post_id)

    async def _handle_video_action(self):
        """Handle video action with common parameter extraction."""
        status_text = self._get_config_value("status_text", "STATUS_TEXT") or ""
        video_url = self._get_config_value("video_url")
        video_title = self._get_config_value("video_title") or ""

        if not video_url:
            raise Exception("Video URL is required for video action.")

        await self.video(status_text, video_url, video_title)

    async def _handle_thread_action(self):
        """Handle thread action: validate entries, publish, emit one result."""
        from agoras.core.threading import ThreadPublishError, emit_thread_result

        entries = self._get_config_value("entries")
        if not entries or not isinstance(entries, list):
            raise Exception("Thread entries are required for thread action.")

        thread_name = self._get_config_value("thread_name")
        auto_archive_duration = self._get_config_value("auto_archive_duration")
        who_can_reply = self._get_config_value("threads_who_can_reply") or self._get_config_value("who_can_reply")

        try:
            result = await self.thread(
                entries,
                thread_name=thread_name,
                auto_archive_duration=auto_archive_duration,
                who_can_reply=who_can_reply,
            )
        except ThreadPublishError as exc:
            emit_thread_result(exc.result)
            raise
        emit_thread_result(result)
        if not result.complete:
            raise ThreadPublishError(result)

    async def _handle_reply_action(self):
        """Handle reply action with common parameter extraction.

        Delegates to ``self.reply`` so the base default raises "not supported"
        for networks without a reply backend, even when ``post_id``/``text``
        are absent (the CLI converter maps ``post_id`` to a platform-specific
        key, so it is not present here for unimplemented networks). Networks
        that implement ``reply`` validate their own parameters.
        """
        post_id, text, media = self._extract_reply_params()
        await self.reply(post_id, text, **media)

    def _extract_reply_params(self):
        """Extract reply parameters (post_id, text, media) from config.

        Shared by the base ``_handle_reply_action`` and the WhatsApp
        ``execute_action`` override so the WhatsApp reply branch cannot diverge
        from the base handler's media extraction and validation.
        """
        post_id = self._get_config_value("post_id")
        text = self._get_config_value("status_text")
        media = {
            "status_image_url_1": self._get_config_value("status_image_url_1", "STATUS_IMAGE_URL_1"),
            "status_image_url_2": self._get_config_value("status_image_url_2", "STATUS_IMAGE_URL_2"),
            "status_image_url_3": self._get_config_value("status_image_url_3", "STATUS_IMAGE_URL_3"),
            "status_image_url_4": self._get_config_value("status_image_url_4", "STATUS_IMAGE_URL_4"),
            "video_url": self._get_config_value("video_url"),
        }
        return post_id, text, media

    async def _handle_delete_reply_action(self):
        """Handle delete-reply action with common parameter extraction.

        Delegates to ``self.delete_reply`` so the base default raises "not
        supported" for networks without a delete-reply backend, even when
        ``post_id`` is absent. Networks that implement ``delete_reply``
        validate their own parameters.
        """
        post_id = self._get_config_value("post_id")
        await self.delete_reply(post_id)

    async def _handle_get_post_action(self):
        """Handle get-post action with common parameter extraction.

        Delegates to ``self.get_post`` so the base default raises "not
        supported" for networks without a get-post backend, even when
        ``post_id`` is absent. Networks that implement ``get_post``
        validate their own parameters.
        """
        post_id = self._get_config_value("post_id")
        await self.get_post(post_id)

    async def _handle_get_reply_action(self):
        """Handle get-reply action with common parameter extraction.

        Delegates to ``self.get_reply`` so the base default raises "not
        supported" for networks without a get-reply backend, even when
        ``post_id`` is absent. Networks that implement ``get_reply``
        validate their own parameters.
        """
        post_id = self._get_config_value("post_id")
        await self.get_reply(post_id)

    async def _handle_list_posts_action(self):
        """Handle list-posts action with common parameter extraction.

        Delegates to ``self.list_posts`` so the base default raises "not
        supported" for networks without a list-posts backend, even when
        ``limit`` is absent. Networks that implement ``list_posts`` validate
        their own parameters.
        """
        raw_limit = self._get_config_value("limit")
        limit = int(raw_limit) if raw_limit not in (None, "") else 10
        await self.list_posts(limit)

    async def _handle_last_from_feed_action(self):
        """Handle last-from-feed action with common parameter extraction."""
        feed_url = self._get_config_value("feed_url", "FEED_URL")
        max_count = int(self._get_config_value("max_count", "MAX_COUNT") or 1)
        post_lookback = int(self._get_config_value("post_lookback", "POST_LOOKBACK") or 3600)

        await self.last_from_feed(feed_url, max_count, post_lookback)

    async def _handle_random_from_feed_action(self):
        """Handle random-from-feed action with common parameter extraction."""
        feed_url = self._get_config_value("feed_url", "FEED_URL")
        max_post_age = int(self._get_config_value("max_post_age", "MAX_POST_AGE") or 365)

        await self.random_from_feed(feed_url, max_post_age)

    async def _handle_schedule_action(self):
        """Handle schedule action with common parameter extraction."""
        google_sheets_id = self._get_config_value("google_sheets_id", "GOOGLE_SHEETS_ID")
        google_sheets_name = self._get_config_value("google_sheets_name", "GOOGLE_SHEETS_NAME")
        google_sheets_client_email = self._get_config_value("google_sheets_client_email", "GOOGLE_SHEETS_CLIENT_EMAIL")
        google_sheets_private_key = self._get_config_value("google_sheets_private_key", "GOOGLE_SHEETS_PRIVATE_KEY")
        max_count = int(self._get_config_value("max_count", "MAX_COUNT") or 1)

        await self.schedule(
            google_sheets_id, google_sheets_name, google_sheets_client_email, google_sheets_private_key, max_count
        )
