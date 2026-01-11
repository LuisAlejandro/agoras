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
Action validator for CLI.

This module validates that requested actions are supported by the target platform.
"""

from .registry import PlatformRegistry


class ActionValidator:
    """Validates that platform supports requested action."""

    @staticmethod
    def validate(platform: str, action: str) -> None:
        """
        Validate action is supported by platform.

        Args:
            platform: Platform name
            action: Action name

        Raises:
            ValueError: If action not supported by platform
        """
        if not PlatformRegistry.platform_exists(platform):
            raise ValueError(
                f"Platform '{platform}' is not supported. "
                f"Supported platforms: {', '.join(PlatformRegistry.get_platform_names())}"
            )

        if not PlatformRegistry.validate_action(platform, action):
            supported = ', '.join(sorted(
                PlatformRegistry.get_supported_actions(platform)
            ))
            raise ValueError(
                f"Action '{action}' is not supported by {platform}. "
                f"Supported actions: {supported}"
            )

    @staticmethod
    def get_supported_actions(platform: str) -> set:
        """
        Get supported actions for a platform.

        Args:
            platform: Platform name

        Returns:
            Set of supported action names
        """
        return PlatformRegistry.get_supported_actions(platform)
