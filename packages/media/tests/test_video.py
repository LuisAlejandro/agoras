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

from unittest.mock import MagicMock, mock_open, patch

import pytest

from agoras.media.video import Video


def test_video_instantiation():
    """Test Video class can be instantiated."""
    video = Video('https://example.com/video.mp4')
    assert video.url == 'https://example.com/video.mp4'


def test_video_with_max_size():
    """Test Video instantiation with max_size."""
    video = Video('https://example.com/video.mp4', max_size=50 * 1024 * 1024)
    assert video.max_size == 50 * 1024 * 1024


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


# Size Validation Tests

def test_validate_content_within_limit():
    """Test _validate_content with size within limit."""
    video = Video('https://example.com/video.mp4', max_size=10 * 1024 * 1024)
    video.content = b'x' * (5 * 1024 * 1024)  # 5MB
    video._downloaded = True  # Simulate post-download state

    # Should not raise exception
    video._validate_content()


@patch('agoras.media.video.Video.cleanup')
def test_validate_content_exceeds_limit(mock_cleanup):
    """Test _validate_content with size exceeding limit."""
    video = Video('https://example.com/video.mp4', max_size=10 * 1024 * 1024, platform='Discord')
    video.content = b'x' * (15 * 1024 * 1024)  # 15MB
    video._downloaded = True  # Simulate post-download state

    with pytest.raises(Exception, match='exceeds.*Discord.*limit'):
        video._validate_content()

    # Verify cleanup was called
    mock_cleanup.assert_called_once()


def test_validate_content_no_size_limit():
    """Test _validate_content without size limit."""
    video = Video('https://example.com/video.mp4')  # No max_size
    video.content = b'x' * (1000 * 1024 * 1024)  # 1GB
    video._downloaded = True

    # Should not raise exception
    video._validate_content()


# Duration Tests

def test_get_duration_before_download():
    """Test get_duration raises exception before download."""
    video = Video('https://example.com/video.mp4')

    with pytest.raises(Exception, match='Video must be downloaded'):
        video.get_duration()


@patch('agoras.media.video.cv2.VideoCapture')
def test_get_duration_valid_video(mock_capture):
    """Test get_duration with valid video."""
    mock_cap = MagicMock()
    mock_cap.get.side_effect = [30.0, 900.0]  # fps=30, frame_count=900
    mock_capture.return_value = mock_cap

    video = Video('https://example.com/video.mp4')
    video._downloaded = True
    video.temp_file = '/tmp/video.mp4'

    duration = video.get_duration()

    assert duration == 30.0
    mock_cap.release.assert_called_once()


@patch('agoras.media.video.cv2.VideoCapture')
def test_get_duration_zero_fps(mock_capture):
    """Test get_duration with zero fps returns None."""
    mock_cap = MagicMock()
    mock_cap.get.side_effect = [0.0, 900.0]  # fps=0, frame_count=900
    mock_capture.return_value = mock_cap

    video = Video('https://example.com/video.mp4')
    video._downloaded = True
    video.temp_file = '/tmp/video.mp4'

    duration = video.get_duration()

    assert duration is None
    mock_cap.release.assert_called_once()


@patch('agoras.media.video.cv2.VideoCapture')
def test_get_duration_handles_exception(mock_capture):
    """Test get_duration handles cv2 exceptions gracefully."""
    mock_capture.side_effect = Exception('OpenCV error')

    video = Video('https://example.com/video.mp4')
    video._downloaded = True
    video.temp_file = '/tmp/video.mp4'

    # Should not raise exception, returns None
    duration = video.get_duration()

    assert duration is None


@patch('agoras.media.video.cv2.VideoCapture')
def test_get_duration_no_temp_file(mock_capture):
    """Test get_duration raises exception when temp_file is None."""
    video = Video('https://example.com/video.mp4')
    video._downloaded = True
    video.temp_file = None  # No temp file

    with pytest.raises(Exception, match='Video must be downloaded'):
        video.get_duration()


# Platform-Specific Factory Method Tests

def test_for_discord():
    """Test for_discord creates video with Discord limits."""
    video = Video.for_discord('https://example.com/video.mp4')

    assert isinstance(video, Video)
    assert video.max_size == 8 * 1024 * 1024  # 8MB
    assert video.platform == 'Discord'
    assert video.url == 'https://example.com/video.mp4'


def test_for_twitter():
    """Test for_twitter creates video with Twitter limits."""
    video = Video.for_twitter('https://example.com/video.mp4')

    assert isinstance(video, Video)
    assert video.max_size == 512 * 1024 * 1024  # 512MB
    assert video.platform == 'Twitter'


def test_for_facebook():
    """Test for_facebook creates video with Facebook limits."""
    video = Video.for_facebook('https://example.com/video.mp4')

    assert isinstance(video, Video)
    assert video.max_size == 4 * 1024 * 1024 * 1024  # 4GB
    assert video.platform == 'Facebook'


def test_for_instagram():
    """Test for_instagram creates video with Instagram limits."""
    video = Video.for_instagram('https://example.com/video.mp4')

    assert isinstance(video, Video)
    assert video.max_size == 4 * 1024 * 1024 * 1024  # 4GB
    assert video.platform == 'Instagram'


def test_for_youtube():
    """Test for_youtube creates video with YouTube limits."""
    video = Video.for_youtube('https://example.com/video.mp4')

    assert isinstance(video, Video)
    assert video.max_size == 256 * 1024 * 1024 * 1024  # 256GB
    assert video.platform == 'YouTube'
    # YouTube supports additional video/quicktime format
    assert 'video/quicktime' in video.allowed_types


def test_for_tiktok():
    """Test for_tiktok creates video with TikTok limits."""
    video = Video.for_tiktok('https://example.com/video.mp4')

    assert isinstance(video, Video)
    assert video.max_size == 2 * 1024 * 1024 * 1024  # 2GB
    assert video.platform == 'TikTok'
