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
Migration guidance utilities for CLI.

This module provides utilities for helping users migrate from the legacy
publish command to the new platform-specific command structure.
"""

from typing import Any, Dict, FrozenSet, Set

from .converter import ParameterConverter

# New-format parameter names to omit from platform action command suggestions.
PLATFORM_ACTION_AUTH_PARAMS: Dict[str, FrozenSet[str]] = {
    'x': frozenset({
        'consumer_key', 'consumer_secret', 'oauth_token', 'oauth_secret',
    }),
    'twitter': frozenset({
        'consumer_key', 'consumer_secret', 'oauth_token', 'oauth_secret',
    }),
    'discord': frozenset({
        'bot_token', 'server_name', 'channel_name',
    }),
    'telegram': frozenset({
        'bot_token', 'chat_id',
    }),
    'whatsapp': frozenset({
        'access_token', 'phone_number_id', 'business_account_id',
    }),
    'facebook': frozenset({
        'client_id', 'client_secret', 'app_id', 'object_id', 'profile_id',
        'refresh_token', 'facebook_access_token',
    }),
    'instagram': frozenset({
        'client_id', 'client_secret', 'object_id', 'instagram_access_token',
    }),
    'linkedin': frozenset({
        'client_id', 'client_secret', 'object_id', 'linkedin_access_token',
    }),
    'youtube': frozenset({
        'client_id', 'client_secret', 'refresh_token',
    }),
    'tiktok': frozenset({
        'client_key', 'client_secret', 'username',
        'access_token', 'refresh_token',
        'tiktok_access_token', 'tiktok_refresh_token',
    }),
    'threads': frozenset({
        'app_id', 'app_secret', 'threads_access_token',
    }),
}

UTILS_ACTIONS = frozenset({'last-from-feed', 'random-from-feed', 'schedule'})
AUTHORIZE_ACTION = 'authorize'

# Legacy publish dest names omitted from utils command suggestions (not whatsapp_recipient).
UTILS_ACTION_AUTH_PARAMS: FrozenSet[str] = frozenset({
    'x_consumer_key', 'x_consumer_secret', 'x_oauth_token', 'x_oauth_secret',
    'twitter_consumer_key', 'twitter_consumer_secret',
    'twitter_oauth_token', 'twitter_oauth_secret',
    'facebook_access_token', 'facebook_object_id', 'facebook_app_id',
    'instagram_access_token', 'instagram_object_id',
    'instagram_client_id', 'instagram_client_secret',
    'linkedin_access_token', 'linkedin_client_id', 'linkedin_client_secret',
    'discord_bot_token', 'discord_server_name', 'discord_channel_name',
    'youtube_client_id', 'youtube_client_secret',
    'tiktok_client_key', 'tiktok_client_secret', 'tiktok_access_token',
    'tiktok_refresh_token', 'tiktok_username',
    'threads_app_id', 'threads_app_secret', 'threads_refresh_token',
    'telegram_bot_token', 'telegram_chat_id',
    'whatsapp_access_token', 'whatsapp_phone_number_id',
    'whatsapp_business_account_id',
})

# Sensitive Sheets fields omitted from utils migration suggestions (routing IDs may remain).
UTILS_ACTION_SHEETS_SECRET_PARAMS: FrozenSet[str] = frozenset({
    'google_sheets_client_email',
    'google_sheets_private_key',
})

# Content params valid only on specific platform actions (new-format keys).
PLATFORM_ACTION_CONTENT_PARAMS: Dict[str, Dict[str, FrozenSet[str]]] = {
    'telegram': {
        'parse_mode': frozenset({'post', 'video'}),
    },
}


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
            new_base = 'agoras utils schedule-run --network <platform>'
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

    # For utils commands, pass through feed/sheets params but omit platform auth.
    if action in UTILS_ACTIONS:
        for key, value in args_dict.items():
            if key in skip_params or key in UTILS_ACTION_AUTH_PARAMS or key in UTILS_ACTION_SHEETS_SECRET_PARAMS:
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
        auth_skip = _platform_action_auth_skip(network, action)

        for key, value in legacy_to_new.items():
            if key in skip_params:
                continue
            if key in auth_skip:
                continue
            if not _platform_action_allows_content_param(network, action, key):
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


def _platform_action_auth_skip(network: str, action: str) -> Set[str]:
    """
    Return new-format parameter names to omit from platform action suggestions.

    Auth and identity fields belong on authorize or in environment variables,
    not on action or utils command lines.
    """
    if action in UTILS_ACTIONS or action == AUTHORIZE_ACTION:
        return set()

    return set(PLATFORM_ACTION_AUTH_PARAMS.get(network, frozenset()))


def _platform_action_allows_content_param(network: str, action: str, key: str) -> bool:
    """Return whether a content param applies to the given platform action."""
    allowed_actions = PLATFORM_ACTION_CONTENT_PARAMS.get(network, {}).get(key)
    if allowed_actions is None:
        return True
    return action in allowed_actions


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

The 'agoras publish' command is deprecated. It is supported through Agoras 2.x and will be removed in version 3.0.

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

For more help: https://agoras.luisalejandro.org/en/latest/migration.html

{'━' * 80}
"""
    return warning
