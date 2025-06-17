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
import random
from typing import Any, Dict, List, Optional, Union

from tweepy import API, Client, OAuth1UserHandler

from .base import BaseAPI


class TwitterAPI(BaseAPI):
    """
    Twitter API handler that centralizes Twitter operations.

    Provides methods for Twitter authentication and all Twitter API operations
    including tweets, likes, retweets, and media uploads using both v1.1 and v2 APIs.
    """

    def __init__(self, consumer_key, consumer_secret, oauth_token, oauth_secret):
        """
        Initialize Twitter API instance.

        Args:
            consumer_key (str): Twitter consumer key
            consumer_secret (str): Twitter consumer secret
            oauth_token (str): Twitter OAuth token
            oauth_secret (str): Twitter OAuth secret
        """
        super().__init__(
            access_token=oauth_token,
            client_id=consumer_key,
            client_secret=consumer_secret
        )
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret
        self.oauth_token = oauth_token
        self.oauth_secret = oauth_secret
        self.client_v2 = None
        self.client_v1 = None

    async def authenticate(self):
        """
        Authenticate with Twitter API using OAuth 1.0a.

        Returns:
            TwitterAPI: Self for method chaining

        Raises:
            Exception: If authentication fails
        """
        if self._authenticated:
            return self

        if not all([self.consumer_key, self.consumer_secret, self.oauth_token, self.oauth_secret]):
            raise Exception('All Twitter OAuth credentials are required.')

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

            # Verify credentials
            def _verify_credentials():
                if not self.client_v1:
                    raise Exception('Twitter v1 client not initialized')
                return self.client_v1.verify_credentials()

            user = await asyncio.to_thread(_verify_credentials)
            if not user:
                raise Exception('Failed to verify Twitter credentials')

            self._authenticated = True
            return self

        except Exception as e:
            raise Exception(f'Twitter authentication failed: {str(e)}')

    async def disconnect(self):
        """
        Disconnect from Twitter API and clean up resources.
        """
        self.client_v1 = None
        self.client_v2 = None
        self._authenticated = False

    async def upload_media(self, media_content: bytes, media_type: str) -> str:
        """
        Upload media to Twitter.

        Args:
            media_content (bytes): Raw media content
            media_type (str): Media MIME type

        Returns:
            str: Media ID

        Raises:
            Exception: If media upload fails
        """
        if not self.client_v1:
            raise Exception('Twitter API not authenticated')

        await self._rate_limit_check('upload_media', 1.0)

        def _sync_upload():
            import tempfile
            import os

            if not self.client_v1:
                raise Exception('Twitter v1 client not initialized')

            # Create temporary file for upload
            _, temp_file = tempfile.mkstemp(suffix='.bin')
            try:
                with open(temp_file, 'wb') as f:
                    f.write(media_content)

                # Upload using v1.1 API
                media = self.client_v1.media_upload(temp_file)
                return media.media_id
            finally:
                # Clean up temporary file
                if os.path.exists(temp_file):
                    os.unlink(temp_file)

        try:
            await asyncio.sleep(random.randrange(1, 5))
            media_id = await asyncio.to_thread(_sync_upload)
            return str(media_id)
        except Exception as e:
            self._handle_api_error(e, 'Twitter media upload')
            raise

    async def create_tweet(self, text: str, media_ids: Optional[List[str]] = None) -> str:
        """
        Create a tweet.

        Args:
            text (str): Tweet text content
            media_ids (list, optional): List of media IDs

        Returns:
            str: Tweet ID

        Raises:
            Exception: If tweet creation fails
        """
        if not self.client_v2:
            raise Exception('Twitter API not authenticated')

        await self._rate_limit_check('create_tweet', 1.0)

        # Twitter has a 280 character limit
        if len(text) > 280:
            text = text[:277] + '...'

        # Build request data with proper typing
        data: Dict[str, Union[str, List[str]]] = {'text': text}
        if media_ids:
            data['media_ids'] = media_ids

        def _sync_create_tweet():
            if not self.client_v2:
                raise Exception('Twitter v2 client not initialized')

            try:
                # Use the correct method signature for Tweepy v2
                if media_ids:
                    response = self.client_v2.create_tweet(text=text, media_ids=media_ids)
                else:
                    response = self.client_v2.create_tweet(text=text)

                # Handle Tweepy response object safely
                response_data = getattr(response, 'data', None)
                if response_data and isinstance(response_data, dict) and 'id' in response_data:
                    return str(response_data['id'])
                else:
                    raise Exception('Invalid response from Twitter API')
            except Exception as api_error:
                raise Exception(f'Twitter API error: {str(api_error)}')

        try:
            await asyncio.sleep(random.randrange(1, 5))
            tweet_id = await asyncio.to_thread(_sync_create_tweet)
            return tweet_id
        except Exception as e:
            self._handle_api_error(e, 'Twitter tweet creation')
            raise

    async def like_tweet(self, tweet_id: str) -> str:
        """
        Like a tweet.

        Args:
            tweet_id (str): Tweet ID to like

        Returns:
            str: Tweet ID

        Raises:
            Exception: If like operation fails
        """
        if not self.client_v2:
            raise Exception('Twitter API not authenticated')

        await self._rate_limit_check('like_tweet', 0.5)

        def _sync_like():
            if not self.client_v2:
                raise Exception('Twitter v2 client not initialized')
            self.client_v2.like(tweet_id)
            return tweet_id

        try:
            await asyncio.sleep(random.randrange(1, 5))
            result = await asyncio.to_thread(_sync_like)
            return result
        except Exception as e:
            self._handle_api_error(e, 'Twitter like')
            raise

    async def retweet(self, tweet_id: str) -> str:
        """
        Retweet a tweet.

        Args:
            tweet_id (str): Tweet ID to retweet

        Returns:
            str: Tweet ID

        Raises:
            Exception: If retweet operation fails
        """
        if not self.client_v2:
            raise Exception('Twitter API not authenticated')

        await self._rate_limit_check('retweet', 0.5)

        def _sync_retweet():
            if not self.client_v2:
                raise Exception('Twitter v2 client not initialized')
            self.client_v2.retweet(tweet_id)
            return tweet_id

        try:
            await asyncio.sleep(random.randrange(1, 5))
            result = await asyncio.to_thread(_sync_retweet)
            return result
        except Exception as e:
            self._handle_api_error(e, 'Twitter retweet')
            raise

    async def delete_tweet(self, tweet_id: str) -> str:
        """
        Delete a tweet.

        Args:
            tweet_id (str): Tweet ID to delete

        Returns:
            str: Tweet ID

        Raises:
            Exception: If deletion fails
        """
        if not self.client_v2:
            raise Exception('Twitter API not authenticated')

        await self._rate_limit_check('delete_tweet', 0.5)

        def _sync_delete():
            if not self.client_v2:
                raise Exception('Twitter v2 client not initialized')
            self.client_v2.delete_tweet(tweet_id)
            return tweet_id

        try:
            await asyncio.sleep(random.randrange(1, 5))
            result = await asyncio.to_thread(_sync_delete)
            return result
        except Exception as e:
            self._handle_api_error(e, 'Twitter delete')
            raise

    def get_api_info(self) -> Dict[str, Any]:
        """
        Get Twitter API configuration information.

        Returns:
            dict: API configuration details
        """
        return {
            'platform': 'Twitter',
            'authenticated': self._authenticated,
            'has_v1_client': self.client_v1 is not None,
            'has_v2_client': self.client_v2 is not None,
            'rate_limits': list(self._rate_limit_cache.keys())
        }
