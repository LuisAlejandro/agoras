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

from agoras.media.base import Media


def test_media_is_abstract():
    """Test that Media cannot be instantiated directly."""
    with pytest.raises(TypeError):
        Media('https://example.com/file.jpg')


def test_media_url_attribute():
    """Test that Media subclasses have url attribute."""
    # We'll test this via Image in test_image.py
    pass


def test_media_cleanup_method_exists():
    """Test that cleanup method exists in Media interface."""
    assert hasattr(Media, 'cleanup')
    assert callable(getattr(Media, 'cleanup'))
