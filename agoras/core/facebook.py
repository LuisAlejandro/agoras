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

import requests

from agoras.core.base import SocialNetwork
from agoras.core.api import FacebookAPI


class Facebook(SocialNetwork):
    """
    Facebook social network implementation.

    This class provides Facebook-specific functionality for posting messages,
    videos, and managing Facebook interactions asynchronously.
    """

    def __init__(self, **kwargs):
        """
        Initialize Facebook instance.

        Args:
            **kwargs: Configuration parameters including:
                - facebook_access_token: Facebook access token
                - facebook_client_id: Facebook client ID
                - facebook_client_secret: Facebook client secret
                - facebook_refresh_token: Facebook refresh token
                - facebook_object_id: Facebook object ID
                - facebook_post_id: Facebook post ID
                - facebook_profile_id: Facebook profile ID
                - facebook_app_id: Facebook app ID
        """
        super().__init__(**kwargs)
        self.facebook_access_token = None
        self.facebook_client_id = None
        self.facebook_client_secret = None
        self.facebook_refresh_token = None
        self.facebook_object_id = None
        self.facebook_post_id = None
        self.facebook_profile_id = None
        self.facebook_app_id = None
        self.api = None

    async def _initialize_client(self):
        """
        Initialize Facebook API client.

        This method sets up the Facebook API client with configuration.
        """
        self.facebook_access_token = self._get_config_value('facebook_access_token', 'FACEBOOK_ACCESS_TOKEN')
        self.facebook_client_id = self._get_config_value('facebook_client_id', 'FACEBOOK_CLIENT_ID')
        self.facebook_client_secret = self._get_config_value('facebook_client_secret', 'FACEBOOK_CLIENT_SECRET')
        self.facebook_refresh_token = self._get_config_value('facebook_refresh_token', 'FACEBOOK_REFRESH_TOKEN')
        self.facebook_object_id = self._get_config_value('facebook_object_id', 'FACEBOOK_OBJECT_ID')
        self.facebook_post_id = self._get_config_value('facebook_post_id', 'FACEBOOK_POST_ID')
        self.facebook_profile_id = self._get_config_value('facebook_profile_id', 'FACEBOOK_PROFILE_ID')
        self.facebook_app_id = self._get_config_value('facebook_app_id', 'FACEBOOK_APP_ID')

        if not self.facebook_access_token:
            raise Exception('Facebook access token is required.')

        # Initialize Facebook API
        self.api = FacebookAPI(
            self.facebook_access_token,
            self.facebook_client_id,
            self.facebook_client_secret,
            self.facebook_refresh_token
        )
        await self.api.authenticate()

    async def post(self, status_text, status_link,
                   status_image_url_1=None, status_image_url_2=None,
                   status_image_url_3=None, status_image_url_4=None):
        """
        Create a post on Facebook.

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
        if not self.api:
            raise Exception('Facebook API not initialized')

        if not self.facebook_object_id:
            raise Exception('Facebook object ID is required.')

        attached_media = []
        source_media = list(filter(None, [
            status_image_url_1, status_image_url_2,
            status_image_url_3, status_image_url_4
        ]))

        if not source_media and not status_text and not status_link:
            raise Exception('No status text, link, or images provided.')

        # Download and validate images using the Media system
        if source_media:
            images = await self.download_images(source_media)
            for image in images:
                # Upload media to Facebook (unpublished)
                await asyncio.sleep(random.randrange(1, 5))
                media_response = await self.api.upload_media(
                    self.facebook_object_id,
                    image.url,
                    published=False
                )
                if media_response and 'id' in media_response:
                    attached_media.append({
                        'media_fbid': media_response['id']
                    })
                # Clean up temporary files
                image.cleanup()

        # Create the post
        await asyncio.sleep(random.randrange(1, 5))
        post_id = await self.api.create_post(
            self.facebook_object_id,
            message=status_text,
            link=status_link,
            attached_media=attached_media if attached_media else None
        )

        self._output_status(post_id)
        return post_id

    async def like(self, facebook_post_id=None):
        """
        Like a Facebook post.

        Args:
            facebook_post_id (str, optional): ID of the Facebook post to like.
                                               Uses instance facebook_post_id if not provided.

        Returns:
            str: Post ID
        """
        if not self.api:
            raise Exception('Facebook API not initialized')

        post_id = facebook_post_id or self.facebook_post_id
        if not post_id:
            raise Exception('Facebook post ID is required.')
        if not self.facebook_object_id:
            raise Exception('Facebook object ID is required.')

        await asyncio.sleep(random.randrange(1, 5))
        result = await self.api.like_post(self.facebook_object_id, post_id)
        self._output_status(result)
        return result

    async def delete(self, facebook_post_id=None):
        """
        Delete a Facebook post.

        Args:
            facebook_post_id (str, optional): ID of the Facebook post to delete.
                                               Uses instance facebook_post_id if not provided.

        Returns:
            str: Post ID
        """
        if not self.api:
            raise Exception('Facebook API not initialized')

        post_id = facebook_post_id or self.facebook_post_id
        if not post_id:
            raise Exception('Facebook post ID is required.')
        if not self.facebook_object_id:
            raise Exception('Facebook object ID is required.')

        await asyncio.sleep(random.randrange(1, 5))
        result = await self.api.delete_post(self.facebook_object_id, post_id)
        self._output_status(result)
        return result

    async def share(self, facebook_post_id=None):
        """
        Share a Facebook post.

        Args:
            facebook_post_id (str, optional): ID of the Facebook post to share.
                                               Uses instance facebook_post_id if not provided.

        Returns:
            str: New post ID
        """
        if not self.api:
            raise Exception('Facebook API not initialized')

        post_id = facebook_post_id or self.facebook_post_id
        if not post_id:
            raise Exception('Facebook post ID is required.')
        if not self.facebook_object_id:
            raise Exception('Facebook object ID is required.')
        if not self.facebook_profile_id:
            raise Exception('Facebook profile ID is required.')

        await asyncio.sleep(random.randrange(1, 5))
        result = await self.api.share_post(
            self.facebook_profile_id,
            self.facebook_object_id,
            post_id
        )
        self._output_status(result)
        return result

    async def _upload_reel_or_story(self, video_type, status_text, video_url):
        """
        Upload a video as a reel or story to Facebook.

        Args:
            video_type (str): Type of video ('reel' or 'story')
            status_text (str): Text content to accompany the video
            video_url (str): URL of the video to post

        Returns:
            str: Video/Post ID
        """
        if not self.api or not self.api.client:
            raise Exception('Facebook API client not initialized')

        assert self.api is not None  # Help type checker
        assert self.facebook_object_id is not None  # Help type checker

        connection = 'video_reels' if video_type == 'reel' else 'video_stories'

        # Start upload
        request = self.api.client.post_object(
            object_id=self.facebook_object_id,
            connection=connection,
            data={"upload_phase": "start"}
        )
        video_id = request.get('video_id')
        upload_url = request.get('upload_url')

        # Upload video
        if upload_url:
            requests.post(upload_url, headers={
                "file_url": video_url,
                "Authorization": f"OAuth {self.api.access_token}",
            })

        # Finish upload
        self.api.client.post_object(
            object_id=self.facebook_object_id,
            connection=connection,
            data={
                "upload_phase": "finish",
                "video_state": "PUBLISHED",
                "video_id": video_id,
                "description": status_text,
            }
        )

        return video_id

    async def _upload_regular_video(self, video, status_text, video_title):
        """
        Upload a regular video to Facebook.

        Args:
            video: Video object from Media system
            status_text (str): Text content to accompany the video
            video_title (str): Title of the video

        Returns:
            str: Post ID
        """
        if not self.facebook_app_id:
            raise Exception('Facebook app ID is required for regular video uploads.')

        assert self.api is not None  # Help type checker
        assert self.facebook_object_id is not None  # Help type checker

        # Create upload session
        upload_response = requests.post(
            f"https://graph.facebook.com/v21.0/{self.facebook_app_id}/uploads",
            headers={"Authorization": f"OAuth {self.api.access_token}"},
            data={
                "file_type": video.file_type.mime,
                "file_length": video.get_file_size(),
                "file_name": f"video.{video.file_type.extension}",
            }
        )
        upload_session_id = upload_response.json().get('id')

        # Upload video file using file-like object from video content
        video_file = video.get_file_like_object()
        upload_data_response = requests.post(
            f"https://graph.facebook.com/v21.0/{upload_session_id}",
            headers={
                "Content-Type": video.file_type.mime,
                "file_offset": "0",
                "Authorization": f"OAuth {self.api.access_token}",
            },
            data=video_file.read()
        )
        file_handle = upload_data_response.json().get('h')

        await asyncio.sleep(random.randrange(1, 5))

        # Create video post
        video_response = requests.post(
            f"https://graph-video.facebook.com/v21.0/{self.facebook_object_id}/videos",
            headers={"Authorization": f"OAuth {self.api.access_token}"},
            data={
                'title': video_title,
                'description': status_text,
                "fbuploader_video_file_chunk": file_handle,
            }
        )
        return video_response.json()['id']

    async def video(self, status_text, video_url, video_title):
        """
        Post a video to Facebook.

        Args:
            status_text (str): Text content to accompany the video (description)
            video_url (str): URL of the video to post
            video_title (str): Title of the video

        Returns:
            str: Post ID
        """
        if not self.api:
            raise Exception('Facebook API not initialized')

        if not video_title or not status_text:
            raise Exception('Video title and description are required.')
        if not video_url:
            raise Exception('Video URL is required.')
        if not self.facebook_object_id:
            raise Exception('Facebook object ID is required.')

        # Get video type from config
        video_type = self._get_config_value('facebook_video_type', 'FACEBOOK_VIDEO_TYPE') or ''

        # Download and validate video using the Media system
        video = await self.download_video(video_url)

        if not video.content or not video.file_type:
            video.cleanup()
            raise Exception('Failed to download or validate video')

        # Ensure video is MP4 format for Facebook
        if video.file_type.mime not in ['video/mp4']:
            video.cleanup()
            raise Exception(f'Invalid video type "{video.file_type.mime}" for {video_url}. '
                            f'Facebook requires MP4 format.')

        try:
            # Handle different video types
            if video_type in ['reel', 'story']:
                post_id = await self._upload_reel_or_story(video_type, status_text, video_url)
            else:
                post_id = await self._upload_regular_video(video, status_text, video_title)

        finally:
            # Clean up using Media system
            video.cleanup()

        self._output_status(post_id)
        return post_id

    # Override action handlers to use Facebook-specific parameter names
    async def _handle_like_action(self):
        """Handle like action with Facebook-specific parameter extraction."""
        facebook_post_id = self._get_config_value('facebook_post_id', 'FACEBOOK_POST_ID')
        if not facebook_post_id:
            raise Exception('Facebook post ID is required for like action.')
        await self.like(facebook_post_id)

    async def _handle_share_action(self):
        """Handle share action with Facebook-specific parameter extraction."""
        facebook_post_id = self._get_config_value('facebook_post_id', 'FACEBOOK_POST_ID')
        if not facebook_post_id:
            raise Exception('Facebook post ID is required for share action.')
        await self.share(facebook_post_id)

    async def _handle_delete_action(self):
        """Handle delete action with Facebook-specific parameter extraction."""
        facebook_post_id = self._get_config_value('facebook_post_id', 'FACEBOOK_POST_ID')
        if not facebook_post_id:
            raise Exception('Facebook post ID is required for delete action.')
        await self.delete(facebook_post_id)

    async def _handle_video_action(self):
        """Handle video action with Facebook-specific parameter extraction."""
        status_text = self._get_config_value('facebook_video_description', 'FACEBOOK_VIDEO_DESCRIPTION') or ''
        video_url = self._get_config_value('facebook_video_url', 'FACEBOOK_VIDEO_URL')
        video_title = self._get_config_value('facebook_video_title', 'FACEBOOK_VIDEO_TITLE') or ''

        if not video_url:
            raise Exception('Facebook video URL is required for video action.')

        await self.video(status_text, video_url, video_title)


async def main_async(kwargs):
    """
    Async main function to execute Facebook actions.

    Args:
        kwargs (dict): Configuration arguments
    """
    action = kwargs.get('action', '')

    if action == '':
        raise Exception('Action is a required argument.')

    # Create Facebook instance with configuration
    facebook_client = Facebook(**kwargs)

    # Execute the action using the base class method
    await facebook_client.execute_action(action)


def main(kwargs):
    """
    Main function to execute Facebook actions.

    Args:
        kwargs (dict): Configuration arguments
    """
    asyncio.run(main_async(kwargs))
