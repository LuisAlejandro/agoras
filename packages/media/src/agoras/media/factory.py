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

import asyncio

from .image import Image
from .video import Video


class MediaFactory:
    """
    Factory class for creating appropriate media instances.
    """

    @staticmethod
    def create_image(url, platform=None):
        """
        Create an Image instance, optionally optimized for a specific platform.

        Args:
            url (str): Image URL
            platform (str, optional): Platform name ('linkedin', etc.)

        Returns:
            Image: Image instance
        """
        if platform and platform.lower() == 'linkedin':
            return Image.for_linkedin(url)
        else:
            return Image(url)

    @staticmethod
    def create_video(url, platform='generic', max_size=None):
        """
        Create a Video instance with platform-specific configuration.

        Args:
            url (str): Video URL
            platform (str): Platform name ('discord', 'twitter', 'facebook', etc.)
            max_size (int, optional): Custom max size override

        Returns:
            Video: Video instance configured for the platform
        """
        if max_size:
            return Video(url, max_size=max_size, platform=platform)

        platform_lower = platform.lower()
        if platform_lower == 'discord':
            return Video.for_discord(url)
        elif platform_lower == 'twitter':
            return Video.for_twitter(url)
        elif platform_lower == 'facebook':
            return Video.for_facebook(url)
        elif platform_lower == 'instagram':
            return Video.for_instagram(url)
        elif platform_lower == 'youtube':
            return Video.for_youtube(url)
        elif platform_lower == 'tiktok':
            return Video.for_tiktok(url)
        else:
            return Video(url, platform=platform)

    @staticmethod
    async def download_images(urls):
        """
        Download multiple images concurrently.

        Args:
            urls (list): List of image URLs

        Returns:
            list: List of downloaded Image instances
        """
        if not urls:
            return []

        images = [Image(url) for url in urls if url]

        # Download all images concurrently
        download_tasks = [image.download() for image in images]
        await asyncio.gather(*download_tasks, return_exceptions=True)

        return images

    @staticmethod
    async def download_video_and_images(video_url, image_urls, platform='generic'):
        """
        Download video and images concurrently.

        Args:
            video_url (str): Video URL
            image_urls (list): List of image URLs
            platform (str): Platform name for video limits

        Returns:
            tuple: (video_instance, list_of_image_instances)
        """
        tasks = []

        # Create video instance and add download task
        video = None
        if video_url:
            video = MediaFactory.create_video(video_url, platform)
            tasks.append(video.download())

        # Create image instances and add download tasks
        images = []
        if image_urls:
            images = [Image(url) for url in image_urls if url]
            tasks.extend([image.download() for image in images])

        # Download all media concurrently
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

        return video, images
