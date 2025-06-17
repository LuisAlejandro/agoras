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

import cv2

from .base import Media


class Video(Media):
    """
    Video media handler.

    Handles downloading, validation, and processing of video files.
    Includes size limit validation for platform-specific requirements.
    """

    def __init__(self, url, max_size=None, platform='generic'):
        """
        Initialize video instance.

        Args:
            url (str): URL of the video to download
            max_size (int, optional): Maximum file size in bytes
            platform (str): Platform name for error messages
        """
        super().__init__(url)
        self.max_size = max_size
        self.platform = platform

    @property
    def allowed_types(self):
        """
        Get allowed video MIME types.

        Returns:
            list: List of allowed video MIME types
        """
        base_types = ['video/mp4', 'video/mov', 'video/webm', 'video/avi']
        
        # YouTube supports additional formats
        if self.platform.lower() == 'youtube':
            return base_types + ['video/quicktime']
        
        return base_types

    def _validate_content(self):
        """
        Validate video content including size limits.

        Raises:
            Exception: If video exceeds size limits
        """
        if self.max_size:
            file_size = self.get_file_size()
            if file_size > self.max_size:
                self.cleanup()
                raise Exception(f'Video file size ({file_size} bytes) exceeds '
                                f'{self.platform} limit of {self.max_size} bytes')

    def get_duration(self):
        """
        Get video duration using OpenCV.

        Returns:
            float: Duration in seconds or None if not available

        Raises:
            Exception: If video file hasn't been downloaded or doesn't exist
        """
        if not self._downloaded or not self.temp_file:
            raise Exception('Video must be downloaded before getting duration')

        try:
            cap = cv2.VideoCapture(self.temp_file)
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_count = cap.get(cv2.CAP_PROP_FRAME_COUNT)
            cap.release()
            
            if fps > 0:
                duration = frame_count / fps
                return float(duration)
            else:
                return None
        except Exception:
            return None

    @classmethod
    def for_discord(cls, url):
        """
        Create video instance with Discord-specific limits.

        Args:
            url (str): Video URL

        Returns:
            Video: Video instance configured for Discord
        """
        return cls(url, max_size=8 * 1024 * 1024, platform='Discord')  # 8MB limit

    @classmethod
    def for_twitter(cls, url):
        """
        Create video instance with Twitter-specific limits.

        Args:
            url (str): Video URL

        Returns:
            Video: Video instance configured for Twitter
        """
        return cls(url, max_size=512 * 1024 * 1024, platform='Twitter')  # 512MB limit

    @classmethod
    def for_facebook(cls, url):
        """
        Create video instance with Facebook-specific limits.

        Args:
            url (str): Video URL

        Returns:
            Video: Video instance configured for Facebook
        """
        return cls(url, max_size=4 * 1024 * 1024 * 1024, platform='Facebook')  # 4GB limit

    @classmethod
    def for_instagram(cls, url):
        """
        Create video instance with Instagram-specific limits.

        Args:
            url (str): Video URL

        Returns:
            Video: Video instance configured for Instagram
        """
        return cls(url, max_size=4 * 1024 * 1024 * 1024, platform='Instagram')  # 4GB limit

    @classmethod
    def for_youtube(cls, url):
        """
        Create video instance with YouTube-specific limits.

        Args:
            url (str): Video URL

        Returns:
            Video: Video instance configured for YouTube
        """
        return cls(url, max_size=256 * 1024 * 1024 * 1024, platform='YouTube')  # 256GB limit 

    @classmethod
    def for_tiktok(cls, url):
        """
        Create video instance with TikTok-specific limits.

        Args:
            url (str): Video URL

        Returns:
            Video: Video instance configured for TikTok
        """
        return cls(url, max_size=2 * 1024 * 1024 * 1024, platform='TikTok')  # 2GB limit