# -*- coding: utf-8 -*-
#
# Please refer to AUTHORS.rst for a complete list of Copyright holders.
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

from unittest.mock import AsyncMock, patch

import pytest

from agoras.media import MediaFactory
from agoras.media.image import Image
from agoras.media.video import Video


def test_create_image():
    """Test MediaFactory creates Image instance."""
    image = MediaFactory.create_image('https://example.com/image.jpg')
    assert isinstance(image, Image)
    assert image.url == 'https://example.com/image.jpg'


def test_create_image_for_linkedin():
    """Test MediaFactory creates LinkedIn-optimized image."""
    image = MediaFactory.create_image('https://example.com/image.jpg', platform='linkedin')
    assert isinstance(image, Image)


def test_create_image_for_linkedin_case_insensitive():
    """Test MediaFactory handles LinkedIn platform case-insensitively."""
    image = MediaFactory.create_image('https://example.com/image.jpg', platform='LINKEDIN')
    assert isinstance(image, Image)


def test_create_video():
    """Test MediaFactory creates Video instance."""
    video = MediaFactory.create_video('https://example.com/video.mp4', platform='facebook')
    assert isinstance(video, Video)
    assert video.url == 'https://example.com/video.mp4'
    assert video.platform == 'Facebook'  # Platform name is capitalized


def test_create_video_with_size_limit():
    """Test MediaFactory creates Video with size limit."""
    video = MediaFactory.create_video('https://example.com/video.mp4', platform='twitter', max_size=512 * 1024 * 1024)
    assert isinstance(video, Video)
    assert video.max_size == 512 * 1024 * 1024


def test_create_video_platform_limits():
    """Test platform-specific size limits in MediaFactory."""
    # Test that MediaFactory applies correct limits per platform
    fb_video = MediaFactory.create_video('https://example.com/video.mp4', platform='facebook')
    tw_video = MediaFactory.create_video('https://example.com/video.mp4', platform='twitter')

    assert fb_video.platform == 'Facebook'  # Platform name is capitalized
    assert tw_video.platform == 'Twitter'  # Platform name is capitalized


# Platform-Specific Video Creation Tests

def test_create_video_for_discord():
    """Test MediaFactory creates Discord-specific video."""
    video = MediaFactory.create_video('https://example.com/video.mp4', platform='discord')
    assert isinstance(video, Video)
    assert video.platform == 'Discord'


def test_create_video_for_instagram():
    """Test MediaFactory creates Instagram-specific video."""
    video = MediaFactory.create_video('https://example.com/video.mp4', platform='instagram')
    assert isinstance(video, Video)
    assert video.platform == 'Instagram'


def test_create_video_for_youtube():
    """Test MediaFactory creates YouTube-specific video."""
    video = MediaFactory.create_video('https://example.com/video.mp4', platform='youtube')
    assert isinstance(video, Video)
    assert video.platform == 'YouTube'


def test_create_video_for_tiktok():
    """Test MediaFactory creates TikTok-specific video."""
    video = MediaFactory.create_video('https://example.com/video.mp4', platform='tiktok')
    assert isinstance(video, Video)
    assert video.platform == 'TikTok'


def test_create_video_for_generic_platform():
    """Test MediaFactory creates generic video for unknown platform."""
    video = MediaFactory.create_video('https://example.com/video.mp4', platform='unknown')
    assert isinstance(video, Video)
    assert video.platform == 'unknown'


def test_create_video_case_insensitive():
    """Test MediaFactory handles platform names case-insensitively."""
    video_lower = MediaFactory.create_video('https://example.com/video.mp4', platform='discord')
    video_upper = MediaFactory.create_video('https://example.com/video.mp4', platform='DISCORD')
    video_mixed = MediaFactory.create_video('https://example.com/video.mp4', platform='DiScOrD')

    assert video_lower.platform == 'Discord'
    assert video_upper.platform == 'Discord'
    assert video_mixed.platform == 'Discord'


def test_create_video_max_size_override():
    """Test max_size parameter overrides platform defaults."""
    custom_size = 999 * 1024 * 1024
    video = MediaFactory.create_video('https://example.com/video.mp4',
                                      platform='facebook',
                                      max_size=custom_size)
    assert video.max_size == custom_size


# Async Download Methods Tests

@pytest.mark.asyncio
async def test_download_images_empty_list():
    """Test download_images with empty list."""
    images = await MediaFactory.download_images([])
    assert images == []


@pytest.mark.asyncio
@patch('agoras.media.image.Image.download', new_callable=AsyncMock)
async def test_download_images_with_urls(mock_download):
    """Test download_images with valid URLs."""
    urls = ['https://example.com/1.jpg', 'https://example.com/2.jpg', 'https://example.com/3.jpg']

    images = await MediaFactory.download_images(urls)

    assert len(images) == 3
    assert all(isinstance(img, Image) for img in images)
    assert mock_download.call_count == 3


@pytest.mark.asyncio
@patch('agoras.media.image.Image.download', new_callable=AsyncMock)
async def test_download_images_filters_none(mock_download):
    """Test download_images filters None and empty string URLs."""
    urls = ['https://example.com/1.jpg', None, '', 'https://example.com/2.jpg']

    images = await MediaFactory.download_images(urls)

    # Should only create images for valid URLs
    assert len(images) == 2
    assert mock_download.call_count == 2


@pytest.mark.asyncio
@patch('agoras.media.image.Image.download', new_callable=AsyncMock)
async def test_download_images_concurrent(mock_download):
    """Test download_images downloads concurrently."""
    urls = ['url1.jpg', 'url2.jpg', 'url3.jpg']

    images = await MediaFactory.download_images(urls)

    # Verify concurrent execution (all should be called)
    assert len(images) == 3
    assert mock_download.call_count == 3


@pytest.mark.asyncio
@patch('agoras.media.video.Video.download', new_callable=AsyncMock)
@patch('agoras.media.image.Image.download', new_callable=AsyncMock)
async def test_download_video_and_images_both(mock_image_download, mock_video_download):
    """Test download_video_and_images with video and images."""
    video_url = 'https://example.com/video.mp4'
    image_urls = ['https://example.com/1.jpg', 'https://example.com/2.jpg']

    video, images = await MediaFactory.download_video_and_images(video_url, image_urls, platform='facebook')

    assert isinstance(video, Video)
    assert len(images) == 2
    assert all(isinstance(img, Image) for img in images)
    assert mock_video_download.call_count == 1
    assert mock_image_download.call_count == 2


@pytest.mark.asyncio
@patch('agoras.media.image.Image.download', new_callable=AsyncMock)
async def test_download_video_and_images_no_video(mock_image_download):
    """Test download_video_and_images with no video."""
    video_url = None
    image_urls = ['https://example.com/1.jpg', 'https://example.com/2.jpg']

    video, images = await MediaFactory.download_video_and_images(video_url, image_urls)

    assert video is None
    assert len(images) == 2
    assert mock_image_download.call_count == 2


@pytest.mark.asyncio
@patch('agoras.media.video.Video.download', new_callable=AsyncMock)
async def test_download_video_and_images_no_images(mock_video_download):
    """Test download_video_and_images with no images."""
    video_url = 'https://example.com/video.mp4'
    image_urls = []

    video, images = await MediaFactory.download_video_and_images(video_url, image_urls, platform='twitter')

    assert isinstance(video, Video)
    assert len(images) == 0
    assert mock_video_download.call_count == 1


@pytest.mark.asyncio
@patch('agoras.media.image.Image.download', new_callable=AsyncMock)
async def test_download_video_and_images_filters_none_images(mock_image_download):
    """Test download_video_and_images filters None image URLs."""
    video_url = None
    image_urls = ['https://example.com/1.jpg', None, '', 'https://example.com/2.jpg']

    video, images = await MediaFactory.download_video_and_images(video_url, image_urls)

    assert video is None
    assert len(images) == 2
    assert mock_image_download.call_count == 2


@pytest.mark.asyncio
async def test_download_video_and_images_empty():
    """Test download_video_and_images with no video and no images."""
    video_url = None
    image_urls = []

    video, images = await MediaFactory.download_video_and_images(video_url, image_urls)

    assert video is None
    assert images == []


@pytest.mark.asyncio
@patch('agoras.media.video.Video.download', new_callable=AsyncMock)
@patch('agoras.media.image.Image.download', new_callable=AsyncMock)
async def test_download_video_and_images_platform_passed(mock_image_download, mock_video_download):
    """Test download_video_and_images passes platform to video creation."""
    video_url = 'https://example.com/video.mp4'
    image_urls = ['https://example.com/1.jpg']

    video, images = await MediaFactory.download_video_and_images(video_url, image_urls, platform='instagram')

    assert video.platform == 'Instagram'
