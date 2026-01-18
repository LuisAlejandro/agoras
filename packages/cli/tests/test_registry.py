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
"""
Tests for PlatformRegistry.
"""

from agoras.cli.registry import PlatformRegistry


def test_get_platform_names():
    """Test that all platforms are registered including X and twitter alias."""
    platforms = PlatformRegistry.get_platform_names()

    assert len(platforms) >= 8
    assert 'x' in platforms
    assert 'twitter' in platforms  # Backward compatibility alias
    assert 'facebook' in platforms
    assert 'instagram' in platforms
    assert 'linkedin' in platforms
    assert 'discord' in platforms
    assert 'youtube' in platforms
    assert 'tiktok' in platforms
    assert 'threads' in platforms


def test_get_supported_actions_x():
    """Test X has full action support."""
    actions = PlatformRegistry.get_supported_actions('x')

    assert 'authorize' in actions
    assert 'post' in actions
    assert 'video' in actions
    assert 'like' in actions
    assert 'share' in actions
    assert 'delete' in actions
    assert len(actions) == 6


def test_get_supported_actions_twitter_alias():
    """Test Twitter alias has same actions as X."""
    x_actions = PlatformRegistry.get_supported_actions('x')
    twitter_actions = PlatformRegistry.get_supported_actions('twitter')

    assert x_actions == twitter_actions


def test_get_supported_actions_youtube():
    """Test YouTube is video-only (no post action)."""
    actions = PlatformRegistry.get_supported_actions('youtube')

    assert 'authorize' in actions
    assert 'video' in actions
    assert 'like' in actions
    assert 'delete' in actions
    assert 'post' not in actions
    assert 'share' not in actions


def test_get_supported_actions_instagram():
    """Test Instagram has limited actions."""
    actions = PlatformRegistry.get_supported_actions('instagram')

    assert 'authorize' in actions
    assert 'post' in actions
    assert 'video' in actions
    assert 'like' not in actions
    assert 'share' not in actions
    assert 'delete' not in actions


def test_get_supported_actions_threads():
    """Test Threads has specific action set."""
    actions = PlatformRegistry.get_supported_actions('threads')

    assert 'authorize' in actions
    assert 'post' in actions
    assert 'video' in actions
    assert 'share' in actions
    assert 'like' not in actions
    assert 'delete' not in actions


def test_validate_action_valid():
    """Test validation passes for valid combinations."""
    assert PlatformRegistry.validate_action('x', 'post') is True
    assert PlatformRegistry.validate_action('twitter', 'post') is True  # Backward compatibility
    assert PlatformRegistry.validate_action('facebook', 'video') is True
    assert PlatformRegistry.validate_action('youtube', 'video') is True


def test_validate_action_invalid():
    """Test validation fails for invalid combinations."""
    assert PlatformRegistry.validate_action('youtube', 'post') is False
    assert PlatformRegistry.validate_action('tiktok', 'post') is False
    assert PlatformRegistry.validate_action('instagram', 'like') is False
    assert PlatformRegistry.validate_action('discord', 'like') is False


def test_platform_exists():
    """Test platform existence check."""
    assert PlatformRegistry.platform_exists('x') is True
    assert PlatformRegistry.platform_exists('twitter') is True  # Backward compatibility
    assert PlatformRegistry.platform_exists('threads') is True
    assert PlatformRegistry.platform_exists('nonexistent') is False


def test_get_platform_info():
    """Test getting platform information."""
    info = PlatformRegistry.get_platform_info('x')

    assert info['name'] == 'X'
    assert 'X' in info['description']
    assert 'actions' in info
    assert 'module' in info


def test_get_platform_info_twitter_alias():
    """Test getting platform information for Twitter alias."""
    info = PlatformRegistry.get_platform_info('twitter')

    # Twitter alias should point to X
    assert 'X' in info['name'] or 'Twitter' in info['name']
    assert 'actions' in info
    assert 'module' in info
