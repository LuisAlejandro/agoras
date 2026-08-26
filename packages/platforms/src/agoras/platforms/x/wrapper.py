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
"""agoras.platforms.x.wrapper module."""

import asyncio
import sys
from typing import Any, Dict, List, Optional

from agoras.core.interfaces import SocialNetwork
from agoras.core.text_limits import validate_text, x_mode_for_subscription
from agoras.core.threading import (
    ThreadPublishError,
    ThreadResult,
    partial_result,
    success_result,
)

from .api import XAPI


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


def _compose_tweet_text(entry: Dict[str, Any]) -> str:
    """Build tweet text from entry text, link, and optional video_title."""
    text = entry.get("text") or ""
    link = entry.get("link") or ""
    video_title = entry.get("video_title") or ""
    video_url = entry.get("video_url")
    if video_url and video_title and not text:
        text = video_title
    elif video_url and video_title and text:
        text = f"{video_title} - {text}"
    return f"{text} {link}".strip()


def _is_uncertain_publish_error(exc: BaseException) -> bool:
    """Classify timeout/uncertain errors after a publish dispatch."""
    if isinstance(exc, (TimeoutError, asyncio.TimeoutError)):
        return True
    message = str(exc).lower()
    return any(token in message for token in ("timeout", "timed out", "temporarily unavailable"))


class X(SocialNetwork):
    """
    X social network implementation.

    This class provides X-specific functionality for posting tweets,
    images, videos, and managing X interactions asynchronously.
    """

    def __init__(self, **kwargs):
        """
        Initialize X instance.

        Args:
            **kwargs: Configuration parameters including:
                - twitter_consumer_key: X consumer key
                - twitter_consumer_secret: X consumer secret
                - twitter_oauth_token: X OAuth token
                - twitter_oauth_secret: X OAuth secret
                - tweet_id: Tweet ID for operations
        """
        super().__init__(**kwargs)
        self.twitter_consumer_key = None
        self.twitter_consumer_secret = None
        self.twitter_oauth_token = None
        self.twitter_oauth_secret = None
        self.tweet_id = None
        self.api = None
        self._subscription_type = None
        self._subscription_resolved = False

    def _load_subscription_type(self):
        """Load stored X subscription_type bound to active oauth tokens (no network)."""
        from .auth import XAuthManager

        auth_manager = XAuthManager(
            consumer_key=self.twitter_consumer_key,
            consumer_secret=self.twitter_consumer_secret,
            oauth_token=self.twitter_oauth_token,
            oauth_secret=self.twitter_oauth_secret,
        )
        # Bind tier to active oauth only — never adopt unrelated stored tokens
        self._subscription_type = auth_manager.load_subscription_type_for_active_oauth()
        return self._subscription_type

    async def _fetch_live_subscription_type(self) -> None:
        """Fetch subscription_type from the authenticated client. Fail closed. No storage write."""
        client = getattr(self.api, "client", None) if self.api else None
        getter = getattr(client, "get_subscription_type", None) if client is not None else None
        if getter is None:
            self._subscription_type = None
            self._subscription_resolved = True
            return
        try:
            self._subscription_type = await getter()
        except Exception:
            self._subscription_type = None
        self._subscription_resolved = True

    def _validate_tweet_text(self, tweet_text: str) -> None:
        """Reject oversized tweet text using live entitlement (fail closed to free)."""
        if not self._subscription_resolved:
            self._load_subscription_type()
            self._subscription_resolved = True
        mode = x_mode_for_subscription(self._subscription_type)
        validate_text("twitter", "text", tweet_text, mode=mode)

    async def _initialize_client(self):
        """
        Initialize X API client.

        Tries to load credentials from CLI params, environment variables, or storage.
        """
        # Try params/environment first
        self.twitter_consumer_key = self._get_config_value("twitter_consumer_key", "TWITTER_CONSUMER_KEY")
        self.twitter_consumer_secret = self._get_config_value("twitter_consumer_secret", "TWITTER_CONSUMER_SECRET")
        self.twitter_oauth_token = self._get_config_value("twitter_oauth_token", "TWITTER_OAUTH_TOKEN")
        self.twitter_oauth_secret = self._get_config_value("twitter_oauth_secret", "TWITTER_OAUTH_SECRET")
        self.tweet_id = self._get_config_value("tweet_id", "TWEET_ID")

        # If any credentials missing, try loading from storage
        if not all(
            [
                self.twitter_consumer_key,
                self.twitter_consumer_secret,
                self.twitter_oauth_token,
                self.twitter_oauth_secret,
            ]
        ):
            from .auth import XAuthManager

            auth_manager = XAuthManager(
                consumer_key=self.twitter_consumer_key, consumer_secret=self.twitter_consumer_secret
            )

            if auth_manager._load_credentials_from_storage():
                # Fill in missing credentials from storage
                if not self.twitter_consumer_key:
                    self.twitter_consumer_key = auth_manager.consumer_key
                if not self.twitter_consumer_secret:
                    self.twitter_consumer_secret = auth_manager.consumer_secret
                if not self.twitter_oauth_token:
                    self.twitter_oauth_token = auth_manager.oauth_token
                if not self.twitter_oauth_secret:
                    self.twitter_oauth_secret = auth_manager.oauth_secret

        # Validate all credentials are now available
        if not all(
            [
                self.twitter_consumer_key,
                self.twitter_consumer_secret,
                self.twitter_oauth_token,
                self.twitter_oauth_secret,
            ]
        ):
            raise Exception("Not authenticated. Please run 'agoras x authorize' first.")

        # Initialize X API
        self.api = XAPI(
            self.twitter_consumer_key, self.twitter_consumer_secret, self.twitter_oauth_token, self.twitter_oauth_secret
        )

        # Authenticate with provided credentials, then ask X for the live tier.
        await self.api.authenticate()
        await self._fetch_live_subscription_type()

    async def authorize_credentials(self):
        """
        Authorize and store X credentials for future use.

        Returns:
            bool: True if authorization successful
        """
        from .auth import XAuthManager

        consumer_key = self._get_config_value("twitter_consumer_key", "TWITTER_CONSUMER_KEY")
        consumer_secret = self._get_config_value("twitter_consumer_secret", "TWITTER_CONSUMER_SECRET")
        oauth_token = self._get_config_value("twitter_oauth_token", "TWITTER_OAUTH_TOKEN")
        oauth_secret = self._get_config_value("twitter_oauth_secret", "TWITTER_OAUTH_SECRET")

        auth_manager = XAuthManager(
            consumer_key=consumer_key,
            consumer_secret=consumer_secret,
            oauth_token=oauth_token,
            oauth_secret=oauth_secret,
        )

        result = await auth_manager.authorize()
        if result:
            print(result)
            return True
        return False

    async def disconnect(self):
        """
        Disconnect from X API and clean up resources.
        """
        if self.api:
            await self.api.disconnect()

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
        Publish content to X.

        Args:
            status_text (str): Text content of the tweet
            status_link (str): URL to include in the tweet
            status_image_url_1 (str, optional): First image URL
            status_image_url_2 (str, optional): Second image URL
            status_image_url_3 (str, optional): Third image URL
            status_image_url_4 (str, optional): Fourth image URL

        Returns:
            str: Tweet ID
        """
        if not self.api:
            raise Exception("X API not initialized")

        media_ids = []
        source_media = list(
            filter(None, [status_image_url_1, status_image_url_2, status_image_url_3, status_image_url_4])
        )

        if not source_media and not status_text and not status_link:
            raise Exception("No status text, link, or images provided.")

        # Compose tweet text and validate before media I/O when possible
        tweet_text = f"{status_text} {status_link}".strip()
        self._validate_tweet_text(tweet_text)

        # Download and upload media using the Media system
        if source_media:
            # Handle both images and videos
            for media_url in source_media:
                try:
                    # Try to download as image first, then video
                    try:
                        image = await self.download_images([media_url])
                        if image and len(image) > 0:
                            media_obj = image[0]
                        else:
                            raise Exception("Failed to download as image")
                    except Exception:
                        # Try as video
                        video = await self.download_video(media_url)
                        media_obj = video

                    # Upload media to X
                    if media_obj.content and media_obj.file_type:
                        media_id = await self.api.upload_media(media_obj.content, media_obj.file_type.mime)
                        if media_id:
                            media_ids.append(media_id)

                    # Clean up temporary files
                    media_obj.cleanup()

                except Exception as e:
                    print(f"Failed to upload media {media_url}: {str(e)}", file=sys.stderr)

        # Create the tweet
        tweet_id = await self.api.post(tweet_text, media_ids or [], validate=False)

        self._output_status(tweet_id)
        return tweet_id

    async def like(self, tweet_id=None):
        """
        Like a tweet.

        Args:
            tweet_id (str, optional): ID of the tweet to like.
                                     Uses instance tweet_id if not provided.

        Returns:
            str: Tweet ID
        """
        if not self.api:
            raise Exception("X API not initialized")

        post_id = tweet_id or self.tweet_id
        if not post_id:
            raise Exception("Tweet ID is required.")

        result = await self.api.like(post_id)
        self._output_status(result)
        return result

    async def delete(self, tweet_id=None):
        """
        Delete a tweet.

        Args:
            tweet_id (str, optional): ID of the tweet to delete.
                                     Uses instance tweet_id if not provided.

        Returns:
            str: Tweet ID
        """
        if not self.api:
            raise Exception("X API not initialized")

        post_id = tweet_id or self.tweet_id
        if not post_id:
            raise Exception("Tweet ID is required.")

        result = await self.api.delete(post_id)
        self._output_status(result)
        return result

    async def share(self, tweet_id=None):
        """
        Share a tweet (retweet).

        Args:
            tweet_id (str, optional): ID of the tweet to retweet.
                                     Uses instance tweet_id if not provided.

        Returns:
            str: Tweet ID
        """
        if not self.api:
            raise Exception("X API not initialized")

        post_id = tweet_id or self.tweet_id
        if not post_id:
            raise Exception("Tweet ID is required.")

        result = await self.api.share(post_id)
        self._output_status(result)
        return result

    async def video(self, status_text, video_url, video_title):
        """
        Post a video to X.

        Args:
            status_text (str): Text content to accompany the video
            video_url (str): URL of the video to post
            video_title (str): Title of the video

        Returns:
            str: Tweet ID
        """
        if not self.api:
            raise Exception("X API not initialized")

        if not video_url:
            raise Exception("Video URL is required.")

        # Compose tweet text and validate before media I/O
        tweet_text_parts = []
        if video_title:
            tweet_text_parts.append(video_title)
        if status_text:
            tweet_text_parts.append(status_text)
        final_text = " - ".join(tweet_text_parts) if tweet_text_parts else ""
        self._validate_tweet_text(final_text)

        # Download and validate video using the Media system
        video = await self.download_video(video_url)

        if not video.content or not video.file_type:
            video.cleanup()
            raise Exception("Failed to download or validate video")

        from agoras.media.constraints import video_limits
        from agoras.media.errors import MediaValidationError

        allowed = video_limits("twitter").mime_types
        if video.file_type.mime not in allowed:
            video.cleanup()
            raise MediaValidationError(
                "twitter",
                "video",
                "mime_types",
                video.file_type.mime,
                sorted(allowed),
            )

        try:
            # Upload video to X
            media_id = await self.api.upload_media(video.content, video.file_type.mime)

            # Create the tweet with video
            tweet_id = await self.api.post(final_text, [media_id] if media_id else [], validate=False)

        finally:
            # Clean up using Media system
            video.cleanup()

        self._output_status(tweet_id)
        return tweet_id

    async def _upload_entry_media(self, entry: Dict[str, Any]) -> List[str]:
        """Upload images or video for one thread entry; return media IDs."""
        if not self.api:
            raise Exception("X API not initialized")

        media_ids: List[str] = []
        images = _entry_images(entry)
        video_url = entry.get("video_url")
        if images and video_url:
            raise Exception("Images and video_url are mutually exclusive in a thread entry.")

        if images:
            for media_url in images:
                try:
                    downloaded = await self.download_images([media_url])
                    if not downloaded:
                        raise Exception(f"Failed to download image: {media_url}")
                    media_obj = downloaded[0]
                except Exception:
                    media_obj = await self.download_video(media_url)

                try:
                    if media_obj.content and media_obj.file_type:
                        media_id = await self.api.upload_media(media_obj.content, media_obj.file_type.mime)
                        if media_id:
                            media_ids.append(media_id)
                finally:
                    media_obj.cleanup()

        if video_url:
            video = await self.download_video(video_url)
            try:
                if not video.content or not video.file_type:
                    raise Exception("Failed to download or validate video")
                media_id = await self.api.upload_media(video.content, video.file_type.mime)
                if media_id:
                    media_ids.append(media_id)
            finally:
                video.cleanup()

        return media_ids

    async def thread(self, entries, **kwargs) -> ThreadResult:
        """
        Publish an ordered reply-chain thread on X.

        Args:
            entries: Ordered entry mappings (text/link/images/video)
            **kwargs: Unused platform options

        Returns:
            ThreadResult: Structured success result

        Raises:
            ThreadPublishError: On partial or failed publish with structured result
        """
        del kwargs  # X reply chains do not use Discord/Threads-specific options
        if not self.api:
            raise Exception("X API not initialized")

        if not entries or not isinstance(entries, list):
            raise Exception("Thread entries are required.")

        prepared: List[Dict[str, Any]] = []
        for entry in entries:
            if not isinstance(entry, dict):
                raise Exception("Each thread entry must be a mapping.")
            images = _entry_images(entry)
            video_url = entry.get("video_url")
            if images and video_url:
                raise Exception("Images and video_url are mutually exclusive in a thread entry.")
            tweet_text = _compose_tweet_text(entry)
            if not tweet_text and not images and not video_url:
                raise Exception("Thread entry requires text, link, images, or video_url.")
            if tweet_text:
                self._validate_tweet_text(tweet_text)
            prepared.append({"text": tweet_text, "entry": entry})

        ids: List[str] = []
        previous_id: Optional[str] = None
        for index, item in enumerate(prepared):
            try:
                media_ids = await self._upload_entry_media(item["entry"])
                tweet_id = await self.api.post(
                    item["text"],
                    media_ids or None,
                    in_reply_to_tweet_id=previous_id,
                    validate=False,  # already validated above
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

            ids.append(str(tweet_id))
            previous_id = str(tweet_id)

        return success_result(ids)

    # Override action handlers to use X-specific parameter names
    async def _handle_like_action(self):
        """Handle like action with X-specific parameter extraction."""
        tweet_id = self._get_config_value("tweet_id", "TWEET_ID")
        if not tweet_id:
            raise Exception("Tweet ID is required for like action.")
        await self.like(tweet_id)

    async def _handle_share_action(self):
        """Handle share action with X-specific parameter extraction."""
        tweet_id = self._get_config_value("tweet_id", "TWEET_ID")
        if not tweet_id:
            raise Exception("Tweet ID is required for share action.")
        await self.share(tweet_id)

    async def _handle_delete_action(self):
        """Handle delete action with X-specific parameter extraction."""
        tweet_id = self._get_config_value("tweet_id", "TWEET_ID")
        if not tweet_id:
            raise Exception("Tweet ID is required for delete action.")
        await self.delete(tweet_id)

    async def _handle_video_action(self):
        """Handle video action with X-specific parameter extraction."""
        status_text = self._get_config_value("status_text", "STATUS_TEXT") or ""
        video_url = self._get_config_value("twitter_video_url", "TWITTER_VIDEO_URL")
        video_title = self._get_config_value("twitter_video_title", "TWITTER_VIDEO_TITLE") or ""

        if not video_url:
            raise Exception("X video URL is required for video action.")

        await self.video(status_text, video_url, video_title)


async def main_async(kwargs):
    """
    Async main function to execute X actions.

    Args:
        kwargs (dict): Configuration arguments
    """
    action = kwargs.get("action", "")

    if action == "":
        raise Exception("Action is a required argument.")

    # Create X instance with configuration
    instance = X(**kwargs)

    # Handle authorize action separately (doesn't need client initialization)
    if action == "authorize":
        success = await instance.authorize_credentials()
        return 0 if success else 1

    try:
        await instance.execute_action(action)
    finally:
        await instance.disconnect()


def main(kwargs):
    """
    Main function to execute X actions (for backwards compatibility).

    Args:
        kwargs (dict): Configuration arguments
    """
    asyncio.run(main_async(kwargs))
