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

from agoras.core.interfaces import SocialNetwork


def test_socialnetwork_is_abstract():
    """Test that SocialNetwork cannot be instantiated directly."""
    with pytest.raises(TypeError):
        SocialNetwork()


def test_socialnetwork_required_methods():
    """Test that SocialNetwork defines required abstract methods."""
    assert hasattr(SocialNetwork, '_initialize_client')
    assert hasattr(SocialNetwork, 'disconnect')
    assert hasattr(SocialNetwork, 'post')
    assert hasattr(SocialNetwork, 'like')
    assert hasattr(SocialNetwork, 'delete')
    assert hasattr(SocialNetwork, 'share')


def test_socialnetwork_execute_action_exists():
    """Test that execute_action method exists."""
    assert hasattr(SocialNetwork, 'execute_action')
    assert callable(getattr(SocialNetwork, 'execute_action'))


def test_socialnetwork_media_methods():
    """Test that media helper methods exist."""
    assert hasattr(SocialNetwork, 'download_images')
    assert hasattr(SocialNetwork, 'download_video')
    assert hasattr(SocialNetwork, 'download_feed')
