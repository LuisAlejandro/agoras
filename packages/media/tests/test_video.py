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

from agoras.media.errors import MediaValidationError
from agoras.media.factory import MediaFactory
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
    video = Video('https://example.com/video.mp4', max_size=10 * 1024 * 1024, platform='discord')
    video.content = b'x' * (15 * 1024 * 1024)  # 15MB
    video._downloaded = True  # Simulate post-download state

    with pytest.raises(MediaValidationError, match='exceeds.*discord.*limit'):
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


@patch('agoras.media.video.Video.cleanup')
@patch('agoras.media.video.cv2.VideoCapture')
def test_validate_content_exceeds_max_duration(mock_capture, mock_cleanup):
    """Test _validate_content rejects videos over platform max duration."""
    mock_cap = MagicMock()
    mock_cap.get.side_effect = [30.0, 30.0 * 700]
    mock_capture.return_value = mock_cap

    video = MediaFactory.create_video('https://example.com/video.mp4', 'tiktok')
    video.content = b'x' * 1024
    video._downloaded = True
    video.temp_file = '/tmp/video.mp4'

    with pytest.raises(MediaValidationError, match='exceeds.*tiktok limit'):
        video._validate_content()

    mock_cleanup.assert_called_once()


@patch('agoras.media.video.Video.cleanup')
@patch('agoras.media.video.cv2.VideoCapture')
def test_validate_content_below_min_duration(mock_capture, mock_cleanup):
    """Test _validate_content rejects videos under platform min duration."""
    mock_cap = MagicMock()
    mock_cap.get.side_effect = [30.0, 60.0]
    mock_capture.return_value = mock_cap

    video = MediaFactory.create_video('https://example.com/video.mp4', 'tiktok')
    video.content = b'x' * 1024
    video._downloaded = True
    video.temp_file = '/tmp/video.mp4'

    with pytest.raises(MediaValidationError, match='below tiktok minimum'):
        video._validate_content()

    mock_cleanup.assert_called_once()


# Platform limits via MediaFactory / contract

@pytest.mark.parametrize('platform,expected_bytes', [
    ('discord', 8 * 1024 * 1024),
    ('twitter', 512 * 1024 * 1024),
    ('facebook', 4 * 1024 * 1024 * 1024),
    ('instagram', 4 * 1024 * 1024 * 1024),
    ('youtube', 256 * 1024 * 1024 * 1024),
    ('tiktok', 2 * 1024 * 1024 * 1024),
])
def test_factory_platform_video_limits(platform, expected_bytes):
    video = MediaFactory.create_video('https://example.com/video.mp4', platform)
    assert video.max_size == expected_bytes
    assert video.platform_key == platform


def test_factory_youtube_quicktime_allowed():
    video = MediaFactory.create_video('https://example.com/video.mp4', 'youtube')
    assert 'video/quicktime' in video.allowed_types
