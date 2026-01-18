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
Token management utility command.

This module provides the tokens command for viewing and managing stored credentials.
"""

import json
import sys
from argparse import ArgumentParser, Namespace, _SubParsersAction
from typing import Optional

from agoras.core.auth.storage import SecureTokenStorage


def create_tokens_parser(subparsers: _SubParsersAction) -> ArgumentParser:
    """
    Create tokens utility command parser.

    Args:
        subparsers: Subparsers action from utils parser

    Returns:
        ArgumentParser for tokens command
    """
    parser = subparsers.add_parser(
        'tokens',
        help='View and manage stored authentication tokens'
    )

    tokens_subparsers = parser.add_subparsers(
        dest='tokens_command',
        title='Token Commands',
        required=True
    )

    # List command
    list_parser = tokens_subparsers.add_parser(
        'list',
        help='List all stored tokens'
    )
    list_parser.add_argument(
        '--platform',
        metavar='<platform>',
        help='Filter by platform name (e.g., facebook, instagram)'
    )
    list_parser.set_defaults(command=_handle_list)

    # Show command
    show_parser = tokens_subparsers.add_parser(
        'show',
        help='Show decrypted token data'
    )
    show_parser.add_argument(
        '--platform',
        required=True,
        metavar='<platform>',
        help='Platform name (e.g., facebook, instagram)'
    )
    show_parser.add_argument(
        '--identifier',
        metavar='<identifier>',
        help='Token identifier (e.g., object_id, client_id). If not provided, shows all tokens for the platform'
    )
    show_parser.add_argument(
        '--field',
        metavar='<field>',
        help='Show only a specific field (e.g., refresh_token, client_id)'
    )
    show_parser.add_argument(
        '--format',
        choices=['json', 'plain'],
        default='plain',
        help='Output format (default: plain)'
    )
    show_parser.set_defaults(command=_handle_show)

    return parser


def _handle_list(args: Namespace) -> int:
    """
    Handle tokens list command.

    Args:
        args: Parsed command-line arguments

    Returns:
        Exit status code
    """
    storage = SecureTokenStorage()
    tokens = storage.list_tokens(args.platform)

    if not tokens:
        platform_filter = f" for platform '{args.platform}'" if args.platform else ""
        print(f"No stored tokens found{platform_filter}.", file=sys.stderr)
        return 1

    print(f"Stored tokens{(' for platform: ' + args.platform) if args.platform else ''}:")
    print()
    for platform, identifier in tokens:
        print(f"  {platform}: {identifier}")

    return 0


def _handle_show(args: Namespace) -> int:
    """
    Handle tokens show command.

    Args:
        args: Parsed command-line arguments

    Returns:
        Exit status code
    """
    storage = SecureTokenStorage()

    if args.identifier:
        # Show specific token
        token_data = storage.load_token(args.platform, args.identifier)
        if not token_data:
            print(
                f"Token not found for platform '{args.platform}' with identifier '{args.identifier}'.",
                file=sys.stderr
            )
            return 1

        _display_token_data(token_data, args.field, args.format, args.platform, args.identifier)
    else:
        # Show all tokens for the platform
        tokens = storage.list_tokens(args.platform)
        if not tokens:
            print(f"No stored tokens found for platform '{args.platform}'.", file=sys.stderr)
            return 1

        found_any = False
        for platform, identifier in tokens:
            if platform == args.platform:
                token_data = storage.load_token(platform, identifier)
                if token_data:
                    if found_any:
                        print()  # Add spacing between tokens
                    _display_token_data(token_data, args.field, args.format, platform, identifier)
                    found_any = True

        if not found_any:
            print(f"No stored tokens found for platform '{args.platform}'.", file=sys.stderr)
            return 1

    return 0


def _display_token_data(
    token_data: dict,
    field: Optional[str],
    format_type: str,
    platform: str,
    identifier: str
):
    """
    Display token data in the requested format.

    Args:
        token_data: Decrypted token data dictionary
        field: Optional field name to display (if None, display all)
        format_type: Output format ('json' or 'plain')
        platform: Platform name
        identifier: Token identifier
    """
    if field:
        # Show only specific field
        if field not in token_data:
            print(f"Field '{field}' not found in token data.", file=sys.stderr)
            print(f"Available fields: {', '.join(token_data.keys())}", file=sys.stderr)
            sys.exit(1)
        value = token_data[field]
        if format_type == 'json':
            print(json.dumps({field: value}, indent=2))
        else:
            print(value)
    else:
        # Show all fields
        if format_type == 'json':
            output = {
                'platform': platform,
                'identifier': identifier,
                'data': token_data
            }
            print(json.dumps(output, indent=2))
        else:
            print(f"Platform: {platform}")
            print(f"Identifier: {identifier}")
            print("Data:")
            for key, value in token_data.items():
                # Mask sensitive values for plain output
                if 'token' in key.lower() or 'secret' in key.lower() or 'key' in key.lower():
                    masked_value = _mask_sensitive_value(value) if value else value
                    print(f"  {key}: {masked_value}")
                else:
                    print(f"  {key}: {value}")


def _mask_sensitive_value(value: str, visible_chars: int = 4) -> str:
    """
    Mask sensitive value showing only first and last few characters.

    Args:
        value: Value to mask
        visible_chars: Number of characters to show at start and end

    Returns:
        Masked value string
    """
    if not value or len(value) <= visible_chars * 2:
        return "***" if value else ""
    return f"{value[:visible_chars]}...{value[-visible_chars:]}"
