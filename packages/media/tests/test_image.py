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
    image = Image.for_linkedin('https://example.com/image.jpg')
    assert image is not None
    assert isinstance(image, Image)
    assert image.url == 'https://example.com/image.jpg'


def test_image_get_dimensions():
    """Test get_dimensions method exists."""
    image = Image('https://example.com/image.jpg')
    # Currently returns None (not implemented)
    assert image.get_dimensions() is None
