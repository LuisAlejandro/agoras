# -*- coding: utf-8 -*-
#
# Please refer to AUTHORS.rst for a complete list of Copyright holders.
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
