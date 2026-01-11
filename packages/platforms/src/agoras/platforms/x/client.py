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
import os
import tempfile
from typing import List, Optional

from tweepy import API, Client, OAuth1UserHandler


class XAPIClient:
    """
    X API client that centralizes both v1.1 and v2 API operations.

    Handles all X API interactions including authentication, media upload,
    tweet operations, and user interactions using the appropriate API version.
    """

    def __init__(self, consumer_key: str, consumer_secret: str,
                 oauth_token: str, oauth_secret: str):
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

        if not all([self.consumer_key, self.consumer_secret,
                   self.oauth_token, self.oauth_secret]):
            raise Exception('All X OAuth credentials are required.')

        try:
            # Set up OAuth 1.0a authentication
            auth = OAuth1UserHandler(
                self.consumer_key, self.consumer_secret,
                self.oauth_token, self.oauth_secret
            )

            # Create both v1.1 and v2 clients
            self.client_v1 = API(auth)
            self.client_v2 = Client(
                consumer_key=self.consumer_key,
                consumer_secret=self.consumer_secret,
                access_token=self.oauth_token,
                access_token_secret=self.oauth_secret
            )

            # Verify credentials using v1 client
            await asyncio.to_thread(self._verify_credentials)
            self._authenticated = True
            return True

        except Exception as e:
            raise Exception(f'X authentication failed: {str(e)}')

    def disconnect(self):
        """
        Disconnect and clean up clients.
        """
        self.client_v1 = None
        self.client_v2 = None
        self._authenticated = False

    def _verify_credentials(self):
        """
        Verify X credentials using v1 API.

        Raises:
            Exception: If verification fails
        """
        if not self.client_v1:
            raise Exception('X v1 client not initialized')

        user = self.client_v1.verify_credentials()
        if not user:
            raise Exception('Failed to verify X credentials')

    async def get_user_info(self) -> dict:
        """
        Get authenticated user information using v1 API.

        Returns:
            dict: User information dictionary

        Raises:
            Exception: If unable to get user info
        """
        if not self.client_v1:
            raise Exception('X v1 client not initialized')

        def _sync_get_info():
            if not self.client_v1:
                raise Exception('X v1 client not initialized')

            user = self.client_v1.verify_credentials()
            if not user:
                raise Exception('Failed to verify X credentials')

            return {
                'user_id': str(user.id),
                'screen_name': user.screen_name,
                'name': user.name,
                'description': getattr(user, 'description', ''),
                'followers_count': getattr(user, 'followers_count', 0),
                'friends_count': getattr(user, 'friends_count', 0),
                'statuses_count': getattr(user, 'statuses_count', 0),
                'verified': getattr(user, 'verified', False)
            }

        return await asyncio.to_thread(_sync_get_info)

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
            raise Exception('X v1 client not initialized')

        def _sync_upload():
            # Create temporary file for upload
            _, temp_file = tempfile.mkstemp(suffix='.bin')
            try:
                with open(temp_file, 'wb') as f:
                    f.write(media_content)

                # Upload using v1.1 API
                media = self.client_v1.media_upload(temp_file)  # type: ignore
                return media.media_id
            finally:
                # Clean up temporary file
                if os.path.exists(temp_file):
                    os.unlink(temp_file)

        media_id = await asyncio.to_thread(_sync_upload)
        return str(media_id)

    async def create_tweet(self, text: str, media_ids: Optional[List[str]] = None) -> str:
        """
        Create a tweet using v2 API.

        Args:
            text (str): Tweet text content
            media_ids (list, optional): List of media IDs

        Returns:
            str: Tweet ID

        Raises:
            Exception: If tweet creation fails
        """
        if not self.client_v2:
            raise Exception('X v2 client not initialized')

        def _sync_create_tweet():
            try:
                # Use the correct method signature for Tweepy v2
                if media_ids:
                    response = self.client_v2.create_tweet(text=text, media_ids=media_ids)  # type: ignore
                else:
                    response = self.client_v2.create_tweet(text=text)  # type: ignore

                # Handle Tweepy response object safely
                response_data = getattr(response, 'data', None)
                if response_data and isinstance(response_data, dict) and 'id' in response_data:
                    return str(response_data['id'])
                else:
                    raise Exception('Invalid response from X API')
            except Exception as api_error:
                raise Exception(f'X API error: {str(api_error)}')

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
            raise Exception('X v2 client not initialized')

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
            raise Exception('X v2 client not initialized')

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
            raise Exception('X v2 client not initialized')

        def _sync_delete():
            self.client_v2.delete_tweet(tweet_id)  # type: ignore
            return tweet_id

        result = await asyncio.to_thread(_sync_delete)
        return result
