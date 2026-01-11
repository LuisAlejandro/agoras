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

from typing import Any, Dict, List, Optional

from threadspipepy.threadspipe import ThreadsPipe


class ThreadsAPIClient:
    """
    Threads API client for making HTTP requests to Threads endpoints.

    Centralizes all Threads API calls including authentication, content publishing,
    and user profile operations using threadspipepy as the underlying library.
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

        # Initialize ThreadsPipe with configuration
        self.api = ThreadsPipe(
            access_token=access_token,
            user_id=user_id,
            handle_hashtags=True,  # Automatic hashtag processing
            auto_handle_hashtags=False  # Manual control over hashtag processing
        )

    def get_profile(self) -> Dict[str, Any]:
        """
        Get user profile information from Threads API.

        Returns:
            dict: User profile information containing user_id and token validity

        Raises:
            Exception: If API call fails or not authenticated
        """
        if not self.access_token:
            raise Exception('No access token available')

        if not self.user_id:
            raise Exception('No user ID available')

        try:
            # ThreadsPipe doesn't have a direct profile method,
            # so we'll return basic info we have
            profile_data = {
                'user_id': self.user_id,
                'access_token_valid': bool(self.access_token)
            }

            return profile_data
        except Exception as e:
            raise Exception(f"Failed to get profile: {str(e)}")

    def create_post(self, post_text: str, files: Optional[List[str]] = None,
                    file_captions: Optional[List[str]] = None,
                    who_can_reply: str = "everyone") -> Dict[str, Any]:
        """
        Create a post on Threads.

        Args:
            post_text (str): Text content of the post
            files (list, optional): List of file URLs to attach
            file_captions (list, optional): Captions for files
            who_can_reply (str): Who can reply to this post

        Returns:
            dict: Post creation response

        Raises:
            Exception: If post creation fails or not authenticated
        """
        if not self.access_token:
            raise Exception('No access token available')

        if not self.user_id:
            raise Exception('No user ID available')

        try:
            response = self.api.pipe(
                post=post_text,
                files=files or [],
                file_captions=file_captions or [],
                who_can_reply=who_can_reply
            )

            return response
        except Exception as e:
            raise Exception(f"Failed to create post: {str(e)}")

    def create_reply(self, reply_text: str, reply_to_id: str) -> Dict[str, Any]:
        """
        Create a reply to a specific post.

        Args:
            reply_text (str): Text content of the reply
            reply_to_id (str): ID of the post to reply to

        Returns:
            dict: Reply creation response

        Raises:
            Exception: If reply creation fails or not authenticated
        """
        if not self.access_token:
            raise Exception('No access token available')

        if not self.user_id:
            raise Exception('No user ID available')

        try:
            response = self.api.reply(
                reply_text=reply_text,
                reply_to_id=reply_to_id
            )

            return response
        except Exception as e:
            raise Exception(f"Failed to create reply: {str(e)}")

    def repost_post(self, post_id: str) -> Dict[str, Any]:
        """
        Repost an existing post.

        Args:
            post_id (str): ID of the post to repost

        Returns:
            dict: Repost response

        Raises:
            Exception: If repost fails or not authenticated
        """
        if not self.access_token:
            raise Exception('No access token available')

        if not self.user_id:
            raise Exception('No user ID available')

        try:
            response = self.api.repost(post_id=post_id)

            return response
        except Exception as e:
            raise Exception(f"Failed to repost: {str(e)}")

    def get_posts(self, limit: int = 25) -> Dict[str, Any]:
        """
        Get user's posts.

        Args:
            limit (int): Maximum number of posts to retrieve

        Returns:
            dict: Posts data

        Raises:
            Exception: If API call fails
        """
        try:
            response = self.api.get_posts(limit=limit)

            return response
        except Exception as e:
            raise Exception(f"Failed to get posts: {str(e)}")

    def get_post_insights(self, post_id: str) -> Dict[str, Any]:
        """
        Get insights/analytics for a specific post.

        Args:
            post_id (str): ID of the post to get insights for

        Returns:
            dict: Post insights data

        Raises:
            Exception: If API call fails
        """
        try:
            response = self.api.get_insights(post_id=post_id)

            return response
        except Exception as e:
            raise Exception(f"Failed to get post insights: {str(e)}")

    def hide_reply(self, reply_id: str) -> Dict[str, Any]:
        """
        Hide a reply (moderation functionality).

        Args:
            reply_id (str): ID of the reply to hide

        Returns:
            dict: Hide reply response

        Raises:
            Exception: If API call fails
        """
        try:
            response = self.api.hide_reply(reply_id=reply_id)

            return response
        except Exception as e:
            raise Exception(f"Failed to hide reply: {str(e)}")

    def unhide_reply(self, reply_id: str) -> Dict[str, Any]:
        """
        Unhide a reply (moderation functionality).

        Args:
            reply_id (str): ID of the reply to unhide

        Returns:
            dict: Unhide reply response

        Raises:
            Exception: If API call fails
        """
        try:
            response = self.api.unhide_reply(reply_id=reply_id)

            return response
        except Exception as e:
            raise Exception(f"Failed to unhide reply: {str(e)}")
