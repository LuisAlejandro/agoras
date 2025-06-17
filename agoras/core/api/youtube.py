# -*- coding: utf-8 -*-
#
# Please refer to AUTHORS.md for a complete list of Copyright holders.
# Copyright (C) 2022-2023, Agoras Developers.

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

import asyncio
import json
import os
import random
import time
from typing import Any, Dict, Optional
import http.client as httplib

import httplib2
from apiclient import discovery, errors, http
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import run_flow
from platformdirs import user_cache_dir

from .base import BaseAPI


class YouTubeAPI(BaseAPI):
    """
    YouTube API handler that centralizes YouTube operations.

    Provides methods for YouTube OAuth authentication, video uploads,
    and all YouTube API operations.
    """

    # Constants for retry logic
    MAX_RETRIES = 10
    RETRIABLE_EXCEPTIONS = (
        httplib2.HttpLib2Error, IOError, httplib.NotConnected,
        httplib.IncompleteRead, httplib.ImproperConnectionState,
        httplib.CannotSendRequest, httplib.CannotSendHeader,
        httplib.ResponseNotReady, httplib.BadStatusLine
    )
    RETRIABLE_STATUS_CODES = [500, 502, 503, 504]

    def __init__(self, client_id, client_secret):
        """
        Initialize YouTube API instance.

        Args:
            client_id (str): YouTube client ID
            client_secret (str): YouTube client secret
        """
        super().__init__(
            client_id=client_id,
            client_secret=client_secret
        )
        self.client_id = client_id
        self.client_secret = client_secret
        self.client = None
        self.storage_file = None
        self.secrets_file = None

        # Set up retry configuration
        httplib2.RETRIES = 1

    def _setup_oauth_files(self):
        """
        Set up OAuth storage and secrets files.
        """
        cachedir = user_cache_dir("Agoras", "Agoras")
        os.makedirs(cachedir, exist_ok=True)
        self.storage_file = os.path.join(cachedir, f'youtube-storage-{self.client_id}.json')
        self.secrets_file = os.path.join(cachedir, f'youtube-secrets-{self.client_id}.json')

        # Create secrets file
        with open(self.secrets_file, 'w') as f:
            f.write(json.dumps({
                "web": {
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://accounts.google.com/o/oauth2/token",
                    "redirect_uris": ["http://localhost"]
                }
            }))

    async def authorize(self):
        """
        Perform OAuth authorization flow.

        This method should be called first to authorize the application
        with YouTube API.

        Returns:
            YouTubeAPI: Self for method chaining
        """
        if not self.client_id or not self.client_secret:
            raise Exception('YouTube client ID and secret are required for authorization.')

        self._setup_oauth_files()

        def _sync_authorize():
            storage = Storage(self.storage_file)
            flow = flow_from_clientsecrets(
                self.secrets_file,
                scope="https://www.googleapis.com/auth/youtube.upload"
            )

            # Create a minimal flags object
            class MinimalFlags:
                def __init__(self):
                    self.auth_host_name = 'localhost'
                    self.auth_host_port = [3456]
                    self.logging_level = 'INFO'
                    self.noauth_local_webserver = True

            flags = MinimalFlags()
            run_flow(flow, storage, flags)

        await asyncio.to_thread(_sync_authorize)
        return self

    async def authenticate(self):
        """
        Authenticate with YouTube API using stored OAuth credentials.

        Returns:
            YouTubeAPI: Self for method chaining

        Raises:
            Exception: If authentication fails or authorization is needed
        """
        if self._authenticated:
            return self

        if not self.client_id or not self.client_secret:
            raise Exception('YouTube client ID and secret are required.')

        self._setup_oauth_files()

        if (not self.storage_file or not self.secrets_file or
                not os.path.isfile(self.storage_file) or not os.path.isfile(self.secrets_file)):
            raise Exception('Please run authorization first using the authorize action.')

        def _sync_authenticate():
            storage = Storage(self.storage_file)
            credentials = storage.get()

            if credentials is None or credentials.invalid:
                flow = flow_from_clientsecrets(
                    self.secrets_file,
                    scope="https://www.googleapis.com/auth/youtube.upload"
                )

                # Create a minimal flags object
                class MinimalFlags:
                    def __init__(self):
                        self.auth_host_name = 'localhost'
                        self.auth_host_port = [3456]
                        self.logging_level = 'INFO'
                        self.noauth_local_webserver = True

                flags = MinimalFlags()
                credentials = run_flow(flow, storage, flags)

            return discovery.build("youtube", "v3", http=credentials.authorize(httplib2.Http()))

        self.client = await asyncio.to_thread(_sync_authenticate)
        self._authenticated = True
        return self

    async def disconnect(self):
        """
        Disconnect from YouTube API and clean up resources.
        """
        self.client = None
        self._authenticated = False

    async def upload_video(self, video_file_path: str, title: str, description: str,
                           category_id: str, privacy_status: str, keywords: Optional[str] = None) -> Dict[str, Any]:
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
        if not self.client:
            raise Exception('YouTube API not authenticated')

        await self._rate_limit_check('upload_video', 2.0)

        def _sync_upload():
            if not self.client:
                raise Exception('YouTube client not initialized')

            retry = 0
            response = None
            error = None
            tags = None

            if keywords:
                tags = keywords.split(",")

            body = {
                'snippet': {
                    'title': title,
                    'description': description,
                    'tags': tags,
                    'categoryId': category_id
                },
                'status': {
                    'privacyStatus': privacy_status
                }
            }

            # Call the API's videos.insert method to create and upload the video
            request = self.client.videos().insert(
                part=",".join(body.keys()),
                body=body,
                media_body=http.MediaFileUpload(video_file_path, chunksize=-1, resumable=True)
            )

            while response is None:
                try:
                    _, response = request.next_chunk()
                    if response is not None:
                        if 'id' in response:
                            break
                        else:
                            raise Exception(f"Upload failed with unexpected response: {response}")

                except errors.HttpError as e:
                    if e.resp.status in self.RETRIABLE_STATUS_CODES:
                        error = f"A retriable HTTP error {e.resp.status} occurred:\n{e.content}"
                    else:
                        raise

                except self.RETRIABLE_EXCEPTIONS as e:
                    error = f"A retriable error occurred: {e}"

                if error is not None:
                    retry += 1
                    if retry > self.MAX_RETRIES:
                        raise Exception("No longer attempting to retry.")

                    max_sleep = 2 ** retry
                    sleep_seconds = random.random() * max_sleep
                    time.sleep(sleep_seconds)
                    error = None

            return response

        try:
            response = await asyncio.to_thread(_sync_upload)
            return response
        except Exception as e:
            self._handle_api_error(e, 'YouTube video upload')
            raise

    async def like_video(self, video_id: str) -> None:
        """
        Like a YouTube video.

        Args:
            video_id (str): YouTube video ID

        Raises:
            Exception: If like operation fails
        """
        if not self.client:
            raise Exception('YouTube API not authenticated')

        await self._rate_limit_check('like_video', 1.0)

        def _sync_like():
            if not self.client:
                raise Exception('YouTube client not initialized')
            request = self.client.videos().rate(
                id=video_id,
                rating="like"
            )
            request.execute()

        try:
            await asyncio.to_thread(_sync_like)
        except Exception as e:
            self._handle_api_error(e, 'YouTube video like')
            raise

    async def delete_video(self, video_id: str) -> None:
        """
        Delete a YouTube video.

        Args:
            video_id (str): YouTube video ID

        Raises:
            Exception: If delete operation fails
        """
        if not self.client:
            raise Exception('YouTube API not authenticated')

        await self._rate_limit_check('delete_video', 1.0)

        def _sync_delete():
            if not self.client:
                raise Exception('YouTube client not initialized')
            request = self.client.videos().delete(id=video_id)
            request.execute()

        try:
            await asyncio.to_thread(_sync_delete)
        except Exception as e:
            self._handle_api_error(e, 'YouTube video delete')
            raise

    def get_api_info(self) -> Dict[str, Any]:
        """
        Get YouTube API configuration information.

        Returns:
            dict: API configuration details
        """
        return {
            'platform': 'YouTube',
            'authenticated': self._authenticated,
            'has_oauth_files': bool(self.storage_file and os.path.exists(self.storage_file)),
            'rate_limits': list(self._rate_limit_cache.keys())
        }
