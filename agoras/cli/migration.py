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
Migration guidance utilities for CLI.

This module provides utilities for helping users migrate from the legacy
publish command to the new platform-specific command structure.
"""

from typing import Any, Dict

from .converter import ParameterConverter


def suggest_new_command(network: str, action: str, args_dict: Dict[str, Any]) -> str:
    """
    Generate the equivalent new command syntax from legacy arguments.

    Args:
        network: Target social network
        action: Action to perform
        args_dict: Dictionary of command arguments

    Returns:
        String with the new command format
    """
    # Determine command type based on action
    if action in ['last-from-feed', 'random-from-feed']:
        mode = 'last' if action == 'last-from-feed' else 'random'
        new_base = f'agoras utils feed-publish --network {network} --mode {mode}'
    elif action == 'schedule':
        if network:
            new_base = f'agoras utils schedule-run --network {network}'
        else:
            new_base = 'agoras utils schedule-run'
    else:
        new_base = f'agoras {network} {action}'

    # Convert parameters to new format
    new_params = convert_legacy_params_to_new_format(network, action, args_dict)

    if new_params:
        return f"{new_base} {new_params}"
    else:
        return new_base


def convert_legacy_params_to_new_format(network: str, action: str,
                                        args_dict: Dict[str, Any]) -> str:
    """
    Convert legacy parameter names to new format for command suggestion.

    Args:
        network: Target social network
        action: Action to perform
        args_dict: Dictionary of command arguments

    Returns:
        String with converted parameters
    """
    # Parameters to skip in suggestions
    skip_params = {
        'network', 'action', 'command', 'handler', 'loglevel',
        'show_migration',  # Don't include migration flag
        # Default values that shouldn't appear
        'youtube_privacy_status', 'tiktok_privacy_status',
        'privacy',  # Skip privacy if it's a default value
    }

    # Default values to skip
    default_values = {
        'privacy': 'private',
        'youtube_privacy_status': 'private',
        'tiktok_privacy_status': 'SELF_ONLY',
    }

    converter = ParameterConverter(network)
    param_parts = []

    # For utils commands, keep prefixed parameters
    if action in ['last-from-feed', 'random-from-feed', 'schedule']:
        # Pass through with original names
        for key, value in args_dict.items():
            if key in skip_params:
                continue
            # Skip empty strings and default values
            if value is None or value == '' or value == 'INFO':
                continue
            # Skip if it's a default value
            if key in default_values and value == default_values[key]:
                continue
            # Escape quotes in value
            safe_value = str(value).replace('"', '\\"')
            param_parts.append(f'--{key.replace("_", "-")} "{safe_value}"')
    else:
        # For platform commands, convert to simplified parameters
        legacy_to_new = converter.convert_from_legacy(args_dict)

        for key, value in legacy_to_new.items():
            if key in skip_params:
                continue
            # Skip empty strings and default values
            if value is None or value == '' or value == 'INFO':
                continue
            # Skip if it's a default value
            if key in default_values and value == default_values[key]:
                continue
            # Escape quotes in value
            safe_value = str(value).replace('"', '\\"')
            param_parts.append(f'--{key.replace("_", "-")} "{safe_value}"')

    return ' '.join(param_parts)


def format_migration_warning(old_command_parts: Dict[str, str],
                             new_command: str) -> str:
    """
    Format a user-friendly deprecation message.

    Args:
        old_command_parts: Dictionary with network, action from old command
        new_command: The new command syntax

    Returns:
        Formatted warning message
    """
    network = old_command_parts.get('network', 'unknown')
    action = old_command_parts.get('action', 'unknown')

    warning = f"""
{'━' * 80}
⚠️  DEPRECATION WARNING
{'━' * 80}

The 'agoras publish' command is deprecated and will be removed in version 2.0
(scheduled for 12 months from now).

Your current command:
  agoras publish --network {network} --action {action} [options]

New command format:
  {new_command}

Benefits of the new format:
  • Shorter, more intuitive commands
  • Better platform-specific help (try: agoras {network} --help)
  • Tab completion support
  • Only show actions your platform supports

Run 'agoras publish --show-migration' to see the migration preview without
executing.

For more help: https://docs.agoras.io/migration

{'━' * 80}
"""
    return warning


def get_migration_summary(network: str, action: str) -> str:
    """
    Get a brief migration summary for help text.

    Args:
        network: Target social network
        action: Action to perform

    Returns:
        Brief migration summary
    """
    if action in ['last-from-feed', 'random-from-feed']:
        mode = 'last' if action == 'last-from-feed' else 'random'
        return f"Use: agoras utils feed-publish --network {network} --mode {mode}"
    elif action == 'schedule':
        return f"Use: agoras utils schedule-run --network {network}"
    else:
        return f"Use: agoras {network} {action}"
