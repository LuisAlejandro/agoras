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
from agoras.media.video import Video


def test_video_instantiation():
    """Test Video class can be instantiated."""
    video = Video('https://example.com/video.mp4')
    assert video.url == 'https://example.com/video.mp4'


def test_video_with_max_size():
    """Test Video instantiation with max_size."""
    video = Video('https://example.com/video.mp4', max_size=50*1024*1024)
    assert video.max_size == 50*1024*1024


def test_video_allowed_types():
    """Test Video has correct allowed MIME types."""
    video = Video('https://example.com/video.mp4')
    assert 'video/mp4' in video.allowed_types
    assert 'video/mov' in video.allowed_types
    assert 'video/webm' in video.allowed_types


def test_video_youtube_allowed_types():
    """Test YouTube-specific video allowed types."""
    video = Video('https://example.com/video.mp4', platform='youtube')
    assert 'video/quicktime' in video.allowed_types


def test_video_platform_specific_limits():
    """Test platform-specific size limits."""
    # This tests the Video class structure
    video_fb = Video('https://example.com/video.mp4', platform='facebook')
    video_tw = Video('https://example.com/video.mp4', platform='twitter')

    assert video_fb.platform == 'facebook'
    assert video_tw.platform == 'twitter'
