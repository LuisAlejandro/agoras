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

from unittest.mock import patch

import pytest

from agoras.media.errors import MediaValidationError
from agoras.media.factory import MediaFactory
from agoras.media.image import Image


def test_image_instantiation():
    """Test Image class can be instantiated."""
    image = Image('https://example.com/image.jpg')
    assert image.url == 'https://example.com/image.jpg'


def test_image_allowed_types():
    """Test Image has correct allowed MIME types."""
    image = Image('https://example.com/image.jpg')
    assert 'image/jpeg' in image.allowed_types
    assert 'image/png' in image.allowed_types
    assert 'image/jpg' in image.allowed_types


def test_image_for_linkedin():
    """Test LinkedIn-specific image creation."""
    image = MediaFactory.create_image('https://example.com/image.jpg', platform='linkedin')
    assert isinstance(image, Image)
    assert image.platform_key == 'linkedin'
    assert image.constraints.max_bytes == 5 * 1024 * 1024


def test_image_get_dimensions():
    """Test get_dimensions method exists."""
    image = Image('https://example.com/image.jpg')
    assert image.get_dimensions() is None


@patch('agoras.media.image.Image.cleanup')
@patch('agoras.media.image.Image.get_dimensions', return_value=(7000, 7000))
def test_validate_content_exceeds_max_width(mock_dimensions, mock_cleanup):
    """Test _validate_content rejects images over platform max width."""
    image = MediaFactory.create_image('https://example.com/image.jpg', platform='linkedin')
    image.content = b'x' * 1024
    image._downloaded = True

    with pytest.raises(MediaValidationError, match='max_width'):
        image._validate_content()

    mock_cleanup.assert_called_once()
