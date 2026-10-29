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
        "x": {
            "actions": {
                "authorize",
                "post",
                "video",
                "thread",
                "like",
                "share",
                "delete",
                "delete-reply",
                "reply",
                "get-post",
                "get-reply",
                "list-posts",
            },
        },
        "twitter": {
            "actions": {
                "authorize",
                "post",
                "video",
                "thread",
                "like",
                "share",
                "delete",
                "delete-reply",
                "reply",
                "get-post",
                "get-reply",
                "list-posts",
            },
        },
        "facebook": {
            "actions": {
                "authorize",
                "post",
                "video",
                "like",
                "share",
                "delete",
                "delete-reply",
                "reply",
                "get-post",
                "get-reply",
                "list-posts",
            },
        },
        "instagram": {
            "actions": {
                "authorize",
                "post",
                "video",
                "reply",
                "delete-reply",
                "get-post",
                "get-reply",
                "delete",
                "list-posts",
            },
        },
        "linkedin": {
            "actions": {
                "authorize",
                "post",
                "video",
                "like",
                "share",
                "delete",
                "delete-reply",
                "reply",
                "get-post",
                "get-reply",
                "list-posts",
            },
        },
        "discord": {
            "actions": {
                "authorize",
                "post",
                "video",
                "thread",
                "delete",
                "delete-reply",
                "reply",
                "get-post",
                "get-reply",
                "list-posts",
            },
        },
        "youtube": {
            "actions": {
                "authorize",
                "video",
                "like",
                "delete",
                "delete-reply",
                "reply",
                "get-post",
                "get-reply",
                "list-posts",
            },
        },
        "tiktok": {
            "actions": {"authorize", "post", "video", "reply", "get-post", "get-reply", "list-posts"},
        },
        "threads": {
            "actions": {
                "authorize",
                "post",
                "video",
                "thread",
                "share",
                "delete",
                "delete-reply",
                "reply",
                "get-post",
                "get-reply",
                "list-posts",
            },
        },
        "telegram": {
            "actions": {
                "authorize",
                "post",
                "video",
                "delete",
                "delete-reply",
                "reply",
                "get-post",
                "get-reply",
                "list-posts",
            },
        },
        "whatsapp": {
            "actions": {"authorize", "post", "video", "template", "reply", "get-post", "get-reply", "list-posts"},
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
        return cls.PLATFORMS.get(platform, {}).get("actions", set())

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
    def platform_exists(cls, platform: str) -> bool:
        """
        Check if platform exists in registry.

        Args:
            platform: Platform name

        Returns:
            True if platform exists, False otherwise
        """
        return platform in cls.PLATFORMS
