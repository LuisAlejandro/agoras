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
Platform registry for CLI.

This module contains the registry of all supported platforms and their
supported actions.
"""

from typing import Any, Dict, List, Set


class PlatformRegistry:
    """Registry of all platforms and their supported actions."""

    PLATFORMS: Dict[str, Dict[str, Any]] = {
        'x': {
            'name': 'X',
            'description': 'X (formerly Twitter) social network',
            'actions': {'authorize', 'post', 'video', 'like', 'share', 'delete'},
            'module': 'agoras.cli.platforms.x',
        },
        'twitter': {
            'name': 'Twitter',
            'description': 'Twitter/X social network',
            'actions': {'authorize', 'post', 'video', 'like', 'share', 'delete'},
            'module': 'agoras.cli.platforms.x',  # Phase 2 will add proper aliasing
        },
        'facebook': {
            'name': 'Facebook',
            'description': 'Facebook social network',
            'actions': {'authorize', 'post', 'video', 'like', 'share', 'delete'},
            'module': 'agoras.cli.platforms.facebook',
        },
        'instagram': {
            'name': 'Instagram',
            'description': 'Instagram social network',
            'actions': {'authorize', 'post', 'video'},
            'module': 'agoras.cli.platforms.instagram',
        },
        'linkedin': {
            'name': 'LinkedIn',
            'description': 'LinkedIn professional network',
            'actions': {'authorize', 'post', 'video', 'like', 'share', 'delete'},
            'module': 'agoras.cli.platforms.linkedin',
        },
        'discord': {
            'name': 'Discord',
            'description': 'Discord chat platform',
            'actions': {'authorize', 'post', 'video', 'delete'},
            'module': 'agoras.cli.platforms.discord',
        },
        'youtube': {
            'name': 'YouTube',
            'description': 'YouTube video platform',
            'actions': {'authorize', 'video', 'like', 'delete'},
            'module': 'agoras.cli.platforms.youtube',
        },
        'tiktok': {
            'name': 'TikTok',
            'description': 'TikTok video platform',
            'actions': {'authorize', 'post', 'video'},
            'module': 'agoras.cli.platforms.tiktok',
        },
        'threads': {
            'name': 'Threads',
            'description': 'Threads (Meta) social network',
            'actions': {'authorize', 'post', 'video', 'share'},
            'module': 'agoras.cli.platforms.threads',
        },
        'telegram': {
            'name': 'Telegram',
            'description': 'Telegram messaging platform',
            'actions': {'authorize', 'post', 'video', 'delete'},
            'module': 'agoras.cli.platforms.telegram',
        },
        'whatsapp': {
            'name': 'WhatsApp',
            'description': 'WhatsApp Business API messaging platform',
            'actions': {'authorize', 'post', 'video', 'template'},
            'module': 'agoras.cli.platforms.whatsapp',
        },
    }

    @classmethod
    def get_platform_names(cls) -> List[str]:
        """
        Get list of all platform names.

        Returns:
            List of platform names
        """
        return list(cls.PLATFORMS.keys())

    @classmethod
    def get_supported_actions(cls, platform: str) -> Set[str]:
        """
        Get set of actions supported by platform.

        Args:
            platform: Platform name

        Returns:
            Set of supported action names
        """
        return cls.PLATFORMS.get(platform, {}).get('actions', set())

    @classmethod
    def validate_action(cls, platform: str, action: str) -> bool:
        """
        Check if platform supports action.

        Args:
            platform: Platform name
            action: Action name

        Returns:
            True if action is supported, False otherwise
        """
        return action in cls.get_supported_actions(platform)

    @classmethod
    def get_platform_info(cls, platform: str) -> Dict[str, Any]:
        """
        Get platform information.

        Args:
            platform: Platform name

        Returns:
            Dictionary with platform information
        """
        return cls.PLATFORMS.get(platform, {})

    @classmethod
    def platform_exists(cls, platform: str) -> bool:
        """
        Check if platform exists in registry.

        Args:
            platform: Platform name

        Returns:
            True if platform exists, False otherwise
        """
        return platform in cls.PLATFORMS
