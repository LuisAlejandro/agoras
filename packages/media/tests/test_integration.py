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
from agoras.common import __version__


def test_version_available():
    """Test that media can access common version."""
    assert __version__ == '2.0.0'


def test_factory_creates_image():
    """Test MediaFactory image creation."""
    image = MediaFactory.create_image('https://example.com/image.jpg')
    assert image is not None
    assert hasattr(image, 'url')
    assert image.url == 'https://example.com/image.jpg'


def test_factory_creates_video():
    """Test MediaFactory video creation."""
    video = MediaFactory.create_video('https://example.com/video.mp4')
    assert video is not None
    assert hasattr(video, 'url')
    assert video.url == 'https://example.com/video.mp4'


def test_common_and_media_integration():
    """Test that agoras.common and agoras.media integrate correctly."""
    # Import from both packages
    from agoras.common import logger
    from agoras.media import Image

    # Both should work together
    assert logger is not None
    image = Image('https://example.com/test.jpg')
    assert image is not None
