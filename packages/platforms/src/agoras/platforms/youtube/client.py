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
"""agoras.platforms.youtube.client module."""

import asyncio
import http.client as httplib
import random
import time
from typing import Any, Dict, List, Optional

import httplib2
from apiclient import discovery, errors, http


class YouTubeAPIClient:
    """
    YouTube API client that centralizes YouTube operations.

    Handles all YouTube API interactions through Google's YouTube API client,
    including video uploads, likes, deletions, and channel operations.
    """

    # Constants for retry logic
    MAX_RETRIES = 10
    RETRIABLE_EXCEPTIONS = (
        httplib2.HttpLib2Error,
        IOError,
        httplib.NotConnected,
        httplib.IncompleteRead,
        httplib.ImproperConnectionState,
        httplib.CannotSendRequest,
        httplib.CannotSendHeader,
        httplib.ResponseNotReady,
        httplib.BadStatusLine,
    )
    RETRIABLE_STATUS_CODES = [500, 502, 503, 504]

    def __init__(self, access_token: str):
        """
        Initialize YouTube API client.

        Args:
            access_token (str): YouTube access token (Google OAuth2 token)
        """
        self.access_token = access_token
        self.youtube_client = None
        self._authenticated = False

        # Set up retry configuration
        httplib2.RETRIES = 1

    async def authenticate(self) -> bool:
        """
        Authenticate and initialize YouTube API client.

        Returns:
            bool: True if authentication successful

        Raises:
            Exception: If authentication fails
        """
        if self._authenticated:
            return True

        if not self.access_token:
            raise Exception("YouTube access token is required")

        try:

            def _sync_create():
                # Create a custom HTTP object that includes the Bearer token
                http_instance = httplib2.Http()

                # Create a custom credentials-like object for Google API client
                class AuthorizedHttp:
                    def __init__(self, http_obj, access_token):
                        self.http = http_obj
                        self.access_token = access_token

                    def request(self, uri, method="GET", body=None, headers=None, **kwargs):
                        if headers is None:
                            headers = {}
                        # Add authorization header
                        headers["Authorization"] = f"Bearer {self.access_token}"
                        return self.http.request(uri, method, body, headers, **kwargs)

                    def __getattr__(self, name):
                        # Delegate other attributes to the underlying http object
                        return getattr(self.http, name)

                authorized_http = AuthorizedHttp(http_instance, self.access_token)

                # Build YouTube API client with authorized HTTP
                return discovery.build("youtube", "v3", http=authorized_http)

            self.youtube_client = await asyncio.to_thread(_sync_create)
            self._authenticated = True
            return True
        except Exception as e:
            raise Exception(f"YouTube client authentication failed: {str(e)}")

    def disconnect(self):
        """
        Disconnect and clean up client resources.
        """
        self.youtube_client = None
        self._authenticated = False

    def _simplify_upload_method(self, request, retry: int, error: str) -> tuple:
        """Helper method to reduce complexity of upload_video."""
        try:
            _, response = request.next_chunk()
            if response is not None:
                if "id" in response:
                    return response, None, retry
                else:
                    raise Exception(f"Upload failed with unexpected response: {response}")
        except errors.HttpError as e:
            if e.resp.status in self.RETRIABLE_STATUS_CODES:
                error = f"A retriable HTTP error {e.resp.status} occurred:\n{e.content}"
                return None, error, retry
            else:
                raise
        except self.RETRIABLE_EXCEPTIONS as e:
            error = f"A retriable error occurred: {e}"
            return None, error, retry

        return None, None, retry

    def _handle_upload_retry(self, retry: int, error: str) -> int:
        """Helper method to handle upload retries."""
        retry += 1
        if retry > self.MAX_RETRIES:
            raise Exception("No longer attempting to retry.")

        max_sleep = 2**retry
        sleep_seconds = random.random() * max_sleep
        time.sleep(sleep_seconds)
        return retry

    async def upload_video(
        self,
        video_file_path: str,
        title: str,
        description: str,
        category_id: str,
        privacy_status: str,
        keywords: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Upload a video to YouTube.

        Args:
            video_file_path (str): Path to video file
            title (str): Video title
            description (str): Video description
            category_id (str): YouTube category ID
            privacy_status (str): Privacy status (public, private, unlisted)
            keywords (str, optional): Comma-separated keywords

        Returns:
            dict: Upload response with video ID

        Raises:
            Exception: If upload fails
        """

        def _sync_upload():
            if not self.youtube_client:
                raise Exception("YouTube client not initialized")

            retry = 0
            response = None
            error = ""  # Initialize as empty string instead of None
            tags = None

            if keywords:
                tags = keywords.split(",")

            body = {
                "snippet": {"title": title, "description": description, "tags": tags, "categoryId": category_id},
                "status": {"privacyStatus": privacy_status},
            }

            # Call the API's videos.insert method to create and upload the video
            request = self.youtube_client.videos().insert(
                part=",".join(body.keys()),
                body=body,
                media_body=http.MediaFileUpload(video_file_path, chunksize=-1, resumable=True),
            )

            while response is None:
                response, new_error, retry = self._simplify_upload_method(request, retry, error)

                if response is not None:
                    break

                if new_error is not None:
                    retry = self._handle_upload_retry(retry, new_error)
                    error = ""  # Reset error for next iteration

            return response

        return await asyncio.to_thread(_sync_upload)

    async def like_video(self, video_id: str) -> None:
        """
        Like a YouTube video.

        Args:
            video_id (str): YouTube video ID

        Raises:
            Exception: If like operation fails
        """

        def _sync_like():
            if not self.youtube_client:
                raise Exception("YouTube client not initialized")

            request = self.youtube_client.videos().rate(id=video_id, rating="like")
            request.execute()

        return await asyncio.to_thread(_sync_like)

    async def delete_video(self, video_id: str) -> None:
        """
        Delete a YouTube video.

        Args:
            video_id (str): YouTube video ID

        Raises:
            Exception: If delete operation fails
        """

        def _sync_delete():
            if not self.youtube_client:
                raise Exception("YouTube client not initialized")

            request = self.youtube_client.videos().delete(id=video_id)
            request.execute()

        return await asyncio.to_thread(_sync_delete)

    async def insert_comment(self, video_id: str, text: str) -> str:
        """
        Insert a top-level comment on a YouTube video.

        Args:
            video_id (str): YouTube video ID to comment on
            text (str): Comment text

        Returns:
            str: Comment ID

        Raises:
            Exception: If comment insert fails
        """

        def _sync_insert():
            if not self.youtube_client:
                raise Exception("YouTube client not initialized")

            request = self.youtube_client.commentThreads().insert(
                part="snippet",
                body={
                    "snippet": {
                        "videoId": video_id,
                        "topLevelComment": {"snippet": {"textOriginal": text}},
                    }
                },
            )
            response = request.execute()
            return response["snippet"]["topLevelComment"]["id"]

        return await asyncio.to_thread(_sync_insert)

    async def delete_comment(self, comment_id: str) -> str:
        """
        Delete a YouTube comment.

        Args:
            comment_id (str): Comment ID to delete

        Returns:
            str: Deleted comment ID

        Raises:
            Exception: If deletion fails
        """

        def _sync_delete():
            if not self.youtube_client:
                raise Exception("YouTube client not initialized")
            if not comment_id:
                raise Exception("YouTube comment ID is required for delete-reply action.")

            request = self.youtube_client.comments().delete(id=comment_id)
            request.execute()
            return comment_id

        return await asyncio.to_thread(_sync_delete)

    async def get_comment(self, comment_id: str) -> Dict[str, Any]:
        """
        Read a YouTube comment by ID.

        Args:
            comment_id (str): Comment ID to read

        Returns:
            dict: Comment fields

        Raises:
            Exception: If the comment cannot be read
        """

        def _sync_get():
            if not self.youtube_client:
                raise Exception("YouTube client not initialized")
            if not comment_id:
                raise Exception("YouTube comment ID is required for get-reply action.")

            request = self.youtube_client.comments().list(part="snippet", id=comment_id)
            response = request.execute()
            items = response.get("items") or []
            if not items:
                raise Exception(f"Comment {comment_id} not found")

            comment = items[0]
            snippet = comment.get("snippet") or {}
            author_channel = snippet.get("authorChannelId")
            author_id = author_channel.get("value") if isinstance(author_channel, dict) else author_channel
            return {
                "id": comment.get("id", comment_id),
                "text": snippet.get("textDisplay") or snippet.get("textOriginal"),
                "author_id": author_id,
                "author_name": snippet.get("authorDisplayName"),
                "created_at": snippet.get("publishedAt"),
                "video_id": snippet.get("videoId"),
            }

        return await asyncio.to_thread(_sync_get)

    async def get_channel_info(self) -> Dict[str, Any]:
        """
        Get channel information for the authenticated user.

        Returns:
            dict: Channel information

        Raises:
            Exception: If request fails
        """

        def _sync_get_channel_info():
            if not self.youtube_client:
                raise Exception("YouTube client not initialized")

            # Get channel information for the authenticated user
            request = self.youtube_client.channels().list(part="snippet,statistics", mine=True)
            response = request.execute()

            if not response.get("items"):
                raise Exception("No YouTube channel found for authenticated user")

            channel = response["items"][0]
            return {
                "channel_id": channel["id"],
                "channel_title": channel["snippet"]["title"],
                "description": channel["snippet"].get("description", ""),
                "subscriber_count": channel["statistics"].get("subscriberCount", 0),
                "video_count": channel["statistics"].get("videoCount", 0),
                "view_count": channel["statistics"].get("viewCount", 0),
            }

        return await asyncio.to_thread(_sync_get_channel_info)

    async def get_video_info(self, video_id: str) -> Dict[str, Any]:
        """
        Get information about a specific video.

        Args:
            video_id (str): YouTube video ID

        Returns:
            dict: Video information

        Raises:
            Exception: If request fails
        """

        def _sync_get_video_info():
            if not self.youtube_client:
                raise Exception("YouTube client not initialized")

            request = self.youtube_client.videos().list(part="snippet,statistics,status", id=video_id)
            response = request.execute()

            if not response.get("items"):
                raise Exception(f"Video {video_id} not found")

            video = response["items"][0]
            return {
                "video_id": video["id"],
                "title": video["snippet"]["title"],
                "description": video["snippet"]["description"],
                "channel_id": video["snippet"]["channelId"],
                "channel_title": video["snippet"]["channelTitle"],
                "privacy_status": video["status"]["privacyStatus"],
                "view_count": video["statistics"].get("viewCount", 0),
                "like_count": video["statistics"].get("likeCount", 0),
                "comment_count": video["statistics"].get("commentCount", 0),
            }

        return await asyncio.to_thread(_sync_get_video_info)

    async def list_uploads(self, limit: int) -> List[Dict[str, Any]]:
        """
        List recent uploads from the authenticated user's channel.

        Resolves the channel's uploads playlist ID via ``channels().list``,
        then reads the playlist items via ``playlistItems().list``.

        Args:
            limit (int): Maximum number of videos to return

        Returns:
            list: Video fields (id, title, description, published_at, thumbnails)

        Raises:
            Exception: If the uploads cannot be read
        """

        def _sync_list_uploads():
            if not self.youtube_client:
                raise Exception("YouTube client not initialized")

            channel_request = self.youtube_client.channels().list(part="contentDetails", mine=True)
            channel_response = channel_request.execute()
            if not channel_response.get("items"):
                raise Exception("No YouTube channel found for authenticated user")

            uploads_playlist_id = (
                channel_response["items"][0].get("contentDetails", {}).get("relatedPlaylists", {}).get("uploads")
            )
            if not uploads_playlist_id:
                raise Exception("Unable to resolve uploads playlist for YouTube channel")

            request = self.youtube_client.playlistItems().list(
                part="snippet", playlistId=uploads_playlist_id, maxResults=limit
            )
            response = request.execute()

            items = []
            for item in response.get("items") or []:
                snippet = item.get("snippet") or {}
                thumbnails = snippet.get("thumbnails") or {}
                items.append(
                    {
                        "id": snippet.get("resourceId", {}).get("videoId"),
                        "title": snippet.get("title"),
                        "description": snippet.get("description"),
                        "published_at": snippet.get("publishedAt"),
                        "thumbnails": thumbnails,
                    }
                )
            return items

        return await asyncio.to_thread(_sync_list_uploads)

    async def search_videos(self, query: str, max_results: int = 25) -> Dict[str, Any]:
        """
        Search for videos on YouTube.

        Args:
            query (str): Search query
            max_results (int): Maximum number of results to return

        Returns:
            dict: Search results

        Raises:
            Exception: If search fails
        """

        def _sync_search():
            if not self.youtube_client:
                raise Exception("YouTube client not initialized")

            request = self.youtube_client.search().list(part="snippet", type="video", q=query, maxResults=max_results)
            return request.execute()

        return await asyncio.to_thread(_sync_search)
