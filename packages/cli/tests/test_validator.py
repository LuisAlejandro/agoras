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
"""
Tests for ActionValidator.
"""

import pytest

from agoras.cli.validator import ActionValidator


def test_validate_valid_combinations():
    """Test validation passes for valid platform/action combinations."""
    # Should not raise
    ActionValidator.validate('twitter', 'post')
    ActionValidator.validate('facebook', 'video')
    ActionValidator.validate('youtube', 'video')
    ActionValidator.validate('instagram', 'post')


def test_validate_youtube_post_rejected():
    """Test YouTube doesn't support post action."""
    with pytest.raises(ValueError) as exc_info:
        ActionValidator.validate('youtube', 'post')

    assert 'not supported' in str(exc_info.value).lower()
    assert 'video' in str(exc_info.value)


def test_validate_tiktok_post_rejected():
    """Test TikTok doesn't support post action."""
    with pytest.raises(ValueError) as exc_info:
        ActionValidator.validate('tiktok', 'post')

    assert 'not supported' in str(exc_info.value).lower()


def test_validate_instagram_like_rejected():
    """Test Instagram doesn't support like action."""
    with pytest.raises(ValueError) as exc_info:
        ActionValidator.validate('instagram', 'like')

    assert 'not supported' in str(exc_info.value).lower()
    assert 'post' in str(exc_info.value)
    assert 'video' in str(exc_info.value)


def test_validate_discord_like_rejected():
    """Test Discord doesn't support like action (uses reactions)."""
    with pytest.raises(ValueError) as exc_info:
        ActionValidator.validate('discord', 'like')

    assert 'not supported' in str(exc_info.value).lower()


def test_validate_threads_like_rejected():
    """Test Threads doesn't support like action yet."""
    with pytest.raises(ValueError) as exc_info:
        ActionValidator.validate('threads', 'like')

    assert 'not supported' in str(exc_info.value).lower()
    assert 'share' in str(exc_info.value)


def test_validate_invalid_platform():
    """Test validation fails for non-existent platform."""
    with pytest.raises(ValueError) as exc_info:
        ActionValidator.validate('nonexistent', 'post')

    assert 'not supported' in str(exc_info.value).lower()
    assert 'twitter' in str(exc_info.value)


def test_get_supported_actions():
    """Test getting supported actions for a platform."""
    actions = ActionValidator.get_supported_actions('twitter')

    assert 'post' in actions
    assert 'video' in actions
    assert len(actions) == 6
