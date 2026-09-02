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
"""agoras.platforms.x.client module."""

import asyncio
import mimetypes
import os
import tempfile
from typing import Any, Dict, List, Optional, Tuple

from tweepy import API, Client, OAuth1UserHandler


def _x_media_type_and_url(item: Any) -> Optional[Dict[str, str]]:
    """Map a tweepy/media object to normalized {type, url}."""
    if isinstance(item, dict):
        mtype = (item.get("type") or "").lower()
        url = item.get("url")
        preview = item.get("preview_image_url")
        variants = item.get("variants") or []
    else:
        mtype = (getattr(item, "type", None) or "").lower()
        url = getattr(item, "url", None)
        preview = getattr(item, "preview_image_url", None)
        variants = getattr(item, "variants", None) or []

    if mtype == "photo" and url:
        return {"type": "image", "url": url}
    if mtype in ("video", "animated_gif"):
        for variant in variants:
            vurl = variant.get("url") if isinstance(variant, dict) else getattr(variant, "url", None)
            if vurl:
                return {"type": "video", "url": vurl}
        fallback = preview or url
        if fallback:
            return {"type": "video", "url": fallback}
    fallback = url or preview
    if fallback:
        return {"type": "unknown", "url": fallback}
    return None


def _x_media_from_includes(includes: Any, attachments: Any) -> List[Dict[str, str]]:
    """Resolve attachment media_keys to normalized media entries."""
    if not attachments:
        return []

    if isinstance(attachments, dict):
        media_keys = attachments.get("media_keys") or []
    else:
        media_keys = getattr(attachments, "media_keys", None) or []
    if not media_keys:
        return []

    if isinstance(includes, dict):
        raw_media = includes.get("media") or []
    elif includes is not None:
        raw_media = getattr(includes, "media", None) or []
    else:
        raw_media = []

    media_by_key: Dict[str, Any] = {}
    for item in raw_media:
        key = item.get("media_key") if isinstance(item, dict) else getattr(item, "media_key", None)
        if key:
            media_by_key[key] = item

    media: List[Dict[str, str]] = []
    for key in media_keys:
        entry = _x_media_type_and_url(media_by_key.get(key))
        if entry:
            media.append(entry)
    return media


def _upload_path_for_media_type(media_type: str) -> Tuple[str, Optional[str]]:
    """Return temp-file suffix and X media_category for a MIME type."""
    if media_type.startswith("video/"):
        suffix = mimetypes.guess_extension(media_type) or ".mp4"
        return suffix, "tweet_video"
    if media_type.startswith("image/"):
        suffix = mimetypes.guess_extension(media_type) or ".bin"
        return suffix, "tweet_image"
    return ".bin", None


class XAPIClient:
    """
    X API client that centralizes both v1.1 and v2 API operations.

    Handles all X API interactions including authentication, media upload,
    tweet operations, and user interactions using the appropriate API version.
    """

    def __init__(self, consumer_key: str, consumer_secret: str, oauth_token: str, oauth_secret: str):
        """
        Initialize X API client.

        Args:
            consumer_key (str): X consumer key
            consumer_secret (str): X consumer secret
            oauth_token (str): X OAuth token
            oauth_secret (str): X OAuth secret
        """
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret
        self.oauth_token = oauth_token
        self.oauth_secret = oauth_secret
        self.client_v1: Optional[API] = None
        self.client_v2: Optional[Client] = None
        self._authenticated = False

    async def authenticate(self) -> bool:
        """
        Authenticate and initialize both v1 and v2 clients.

        Returns:
            bool: True if authentication successful

        Raises:
            Exception: If authentication fails
        """
        if self._authenticated:
            return True

        if not all([self.consumer_key, self.consumer_secret, self.oauth_token, self.oauth_secret]):
            raise Exception("All X OAuth credentials are required.")

        try:
            # Ensure all tokens are strings (not None or other types)
            consumer_key = str(self.consumer_key) if self.consumer_key else None
            consumer_secret = str(self.consumer_secret) if self.consumer_secret else None
            oauth_token = str(self.oauth_token) if self.oauth_token else None
            oauth_secret = str(self.oauth_secret) if self.oauth_secret else None

            if not all([consumer_key, consumer_secret, oauth_token, oauth_secret]):
                raise Exception("All X OAuth credentials are required and must be non-empty strings.")

            # Set up OAuth 1.0a authentication
            # Note: access_token and access_token_secret must be keyword arguments in Tweepy 4.x
            auth = OAuth1UserHandler(
                consumer_key, consumer_secret, access_token=oauth_token, access_token_secret=oauth_secret
            )

            # Verify the access tokens are set correctly on the auth object
            if not hasattr(auth, "access_token") or auth.access_token != oauth_token:
                # If tokens aren't set correctly, try using set_access_token as fallback
                auth.set_access_token(oauth_token, oauth_secret)

            # Clear any request_token that might be set (from OAuth flow)
            # This ensures we're using access tokens, not request tokens
            if hasattr(auth, "request_token") and auth.request_token:
                object.__setattr__(auth, "request_token", None)

            # Create both v1.1 and v2 clients
            self.client_v1 = API(auth, wait_on_rate_limit=False)
            self.client_v2 = Client(
                consumer_key=consumer_key,
                consumer_secret=consumer_secret,
                access_token=oauth_token,
                access_token_secret=oauth_secret,
                wait_on_rate_limit=False,
            )

            # Skip credential verification - other platforms don't verify during auth
            # Invalid tokens will fail during actual API calls with clearer errors
            self._authenticated = True
            return True

        except Exception:
            raise

    def disconnect(self):
        """
        Disconnect and clean up clients.
        """
        self.client_v1 = None
        self.client_v2 = None
        self._authenticated = False

    async def get_user_info(self) -> dict:
        """
        Get authenticated user information using v1 API.

        Returns:
            dict: User information dictionary

        Raises:
            Exception: If unable to get user info
        """
        if not self.client_v1:
            raise Exception("X v1 client not initialized")

        def _sync_get_info():
            if not self.client_v1:
                raise Exception("X v1 client not initialized")

            user = self.client_v1.verify_credentials()
            if not user:
                raise Exception("Failed to verify X credentials")

            return {
                "user_id": str(user.id),
                "screen_name": user.screen_name,
                "name": user.name,
                "description": getattr(user, "description", ""),
                "followers_count": getattr(user, "followers_count", 0),
                "friends_count": getattr(user, "friends_count", 0),
                "statuses_count": getattr(user, "statuses_count", 0),
                "verified": getattr(user, "verified", False),
            }

        return await asyncio.to_thread(_sync_get_info)

    async def get_subscription_type(self) -> Optional[str]:
        """
        Fetch authenticated user subscription_type via API v2.

        Returns:
            str | None: Basic, Premium, PremiumPlus, None, or None if unavailable
        """
        if not self.client_v2:
            raise Exception("X v2 client not initialized")

        def _sync_get_subscription():
            if not self.client_v2:
                raise Exception("X v2 client not initialized")
            response = self.client_v2.get_me(user_fields=["subscription_type"])
            data = getattr(response, "data", None)
            if data is None:
                return None
            return getattr(data, "subscription_type", None)

        return await asyncio.to_thread(_sync_get_subscription)

    async def upload_media(self, media_content: bytes, media_type: str) -> str:
        """
        Upload media using v1.1 API.

        Args:
            media_content (bytes): Raw media content
            media_type (str): Media MIME type

        Returns:
            str: Media ID

        Raises:
            Exception: If media upload fails
        """
        if not self.client_v1:
            raise Exception("X v1 client not initialized")

        def _sync_upload():
            suffix, media_category = _upload_path_for_media_type(media_type)
            _, temp_file = tempfile.mkstemp(suffix=suffix)
            try:
                with open(temp_file, "wb") as f:
                    f.write(media_content)

                upload_kwargs = {}
                if media_category:
                    upload_kwargs["media_category"] = media_category

                # Tweepy infers file_type from temp path suffix; do not pass file_type
                # (duplicate kwarg breaks chunked_upload for video).
                media = self.client_v1.media_upload(temp_file, **upload_kwargs)  # type: ignore
                return media.media_id
            finally:
                # Clean up temporary file
                if os.path.exists(temp_file):
                    os.unlink(temp_file)

        media_id = await asyncio.to_thread(_sync_upload)
        return str(media_id)

    async def create_tweet(
        self,
        text: str,
        media_ids: Optional[List[str]] = None,
        in_reply_to_tweet_id: Optional[str] = None,
    ) -> str:
        """
        Create a tweet using v2 API.

        Args:
            text (str): Tweet text content
            media_ids (list, optional): List of media IDs
            in_reply_to_tweet_id (str, optional): Parent tweet ID for reply chains

        Returns:
            str: Tweet ID

        Raises:
            Exception: If tweet creation fails
        """
        if not self.client_v2:
            raise Exception("X v2 client not initialized")

        def _sync_create_tweet():
            try:
                kwargs: Dict[str, Any] = {"text": text}
                if media_ids:
                    kwargs["media_ids"] = media_ids
                if in_reply_to_tweet_id:
                    kwargs["in_reply_to_tweet_id"] = in_reply_to_tweet_id
                response = self.client_v2.create_tweet(**kwargs)  # type: ignore

                # Handle Tweepy response object safely
                response_data = getattr(response, "data", None)
                if response_data and isinstance(response_data, dict) and "id" in response_data:
                    return str(response_data["id"])
                else:
                    raise Exception("Invalid response from X API")
            except Exception as api_error:
                raise Exception(f"X API error: {str(api_error)}")

        tweet_id = await asyncio.to_thread(_sync_create_tweet)
        return tweet_id

    async def like_tweet(self, tweet_id: str) -> str:
        """
        Like a tweet using v2 API.

        Args:
            tweet_id (str): Tweet ID to like

        Returns:
            str: Tweet ID

        Raises:
            Exception: If like operation fails
        """
        if not self.client_v2:
            raise Exception("X v2 client not initialized")

        def _sync_like():
            self.client_v2.like(tweet_id)  # type: ignore
            return tweet_id

        result = await asyncio.to_thread(_sync_like)
        return result

    async def retweet(self, tweet_id: str) -> str:
        """
        Retweet a tweet using v2 API.

        Args:
            tweet_id (str): Tweet ID to retweet

        Returns:
            str: Tweet ID

        Raises:
            Exception: If retweet operation fails
        """
        if not self.client_v2:
            raise Exception("X v2 client not initialized")

        def _sync_retweet():
            self.client_v2.retweet(tweet_id)  # type: ignore
            return tweet_id

        result = await asyncio.to_thread(_sync_retweet)
        return result

    async def delete_tweet(self, tweet_id: str) -> str:
        """
        Delete a tweet using v2 API.

        Args:
            tweet_id (str): Tweet ID to delete

        Returns:
            str: Tweet ID

        Raises:
            Exception: If deletion fails
        """
        if not self.client_v2:
            raise Exception("X v2 client not initialized")

        def _sync_delete():
            self.client_v2.delete_tweet(tweet_id)  # type: ignore
            return tweet_id

        result = await asyncio.to_thread(_sync_delete)
        return result

    async def get_users_tweets(self, user_id: str, limit: int) -> List[Dict[str, Any]]:
        """
        List recent tweets from a user using v2 API.

        Args:
            user_id (str): User ID whose tweets to list
            limit (int): Maximum number of tweets to return

        Returns:
            list: Tweet fields (id, text, author_id, created_at, media)

        Raises:
            Exception: If the tweets cannot be read
        """
        if not self.client_v2:
            raise Exception("X v2 client not initialized")

        def _sync_get_users_tweets():
            response = self.client_v2.get_users_tweets(  # type: ignore
                user_id,
                max_results=limit,
                tweet_fields=["created_at", "author_id", "attachments"],
                expansions=["attachments.media_keys"],
                media_fields=["url", "preview_image_url", "type", "variants"],
            )
            response_data = getattr(response, "data", None)
            if response_data is None:
                return []
            includes = getattr(response, "includes", None)
            items = []
            for item in response_data:
                if hasattr(item, "data"):
                    item = item.data
                if isinstance(item, dict):
                    attachments = item.get("attachments")
                    media = _x_media_from_includes(includes, attachments)
                    items.append(
                        {
                            "id": str(item.get("id")),
                            "text": item.get("text"),
                            "author_id": item.get("author_id"),
                            "created_at": (str(item.get("created_at")) if item.get("created_at") is not None else None),
                            "attachments": attachments,
                            "media": media,
                        }
                    )
                else:
                    attachments = getattr(item, "attachments", None)
                    media = _x_media_from_includes(includes, attachments)
                    items.append(
                        {
                            "id": str(getattr(item, "id")),
                            "text": getattr(item, "text", None),
                            "author_id": getattr(item, "author_id", None),
                            "created_at": (
                                str(getattr(item, "created_at"))
                                if getattr(item, "created_at", None) is not None
                                else None
                            ),
                            "attachments": attachments,
                            "media": media,
                        }
                    )
            return items

        return await asyncio.to_thread(_sync_get_users_tweets)

    async def get_tweet(self, tweet_id: str) -> Dict[str, Any]:
        """
        Read a tweet by ID using v2 API.

        Args:
            tweet_id (str): Tweet ID to read

        Returns:
            dict: Tweet fields (id, text, author_id, created_at)

        Raises:
            Exception: If the tweet cannot be read
        """
        if not self.client_v2:
            raise Exception("X v2 client not initialized")

        def _sync_get_tweet():
            response = self.client_v2.get_tweet(  # type: ignore
                tweet_id,
                tweet_fields=["created_at", "author_id", "attachments"],
                expansions=["attachments.media_keys"],
                media_fields=["url", "preview_image_url", "type", "variants"],
            )
            response_data = getattr(response, "data", None)
            if response_data is None:
                raise Exception(f"Tweet {tweet_id} not found")
            if hasattr(response_data, "data"):
                response_data = response_data.data
            includes = getattr(response, "includes", None)
            if isinstance(response_data, dict):
                attachments = response_data.get("attachments")
                media = _x_media_from_includes(includes, attachments)
                return {
                    "id": str(response_data.get("id", tweet_id)),
                    "text": response_data.get("text"),
                    "author_id": response_data.get("author_id"),
                    "created_at": (
                        str(response_data.get("created_at")) if response_data.get("created_at") is not None else None
                    ),
                    "attachments": attachments,
                    "media": media,
                }
            attachments = getattr(response_data, "attachments", None)
            media = _x_media_from_includes(includes, attachments)
            return {
                "id": str(getattr(response_data, "id", tweet_id)),
                "text": getattr(response_data, "text", None),
                "author_id": getattr(response_data, "author_id", None),
                "created_at": (
                    str(getattr(response_data, "created_at"))
                    if getattr(response_data, "created_at", None) is not None
                    else None
                ),
                "attachments": attachments,
                "media": media,
            }

        return await asyncio.to_thread(_sync_get_tweet)
