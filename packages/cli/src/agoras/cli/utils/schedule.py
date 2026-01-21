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
Schedule run utility command.

This module provides the schedule-run command for Google Sheets automation.
"""

from argparse import ArgumentParser, Namespace, _SubParsersAction

from ..commands.publish import main as publish_main
from ..registry import PlatformRegistry


def create_schedule_run_parser(subparsers: _SubParsersAction) -> ArgumentParser:
    """
    Create schedule-run utility command parser.

    Args:
        subparsers: Subparsers action from utils parser

    Returns:
        ArgumentParser for schedule-run command
    """
    parser = subparsers.add_parser(
        'schedule-run',
        help='Run scheduled posts from Google Sheets'
    )

    # Network selection (optional - can process all)
    parser.add_argument(
        '--network',
        choices=PlatformRegistry.get_platform_names(),
        metavar='<platform>',
        help='Target specific network (default: process all networks in sheet)'
    )

    # Google Sheets options
    sheets = parser.add_argument_group('Google Sheets Options')
    sheets.add_argument(
        '--sheets-id',
        required=True,
        metavar='<id>',
        help='Google Sheets document ID'
    )
    sheets.add_argument(
        '--sheets-name',
        required=True,
        metavar='<name>',
        help='Sheet name within document'
    )
    sheets.add_argument(
        '--sheets-client-email',
        required=True,
        metavar='<email>',
        help='Google service account email'
    )
    sheets.add_argument(
        '--sheets-private-key',
        required=True,
        metavar='<key>',
        help='Google service account private key'
    )

    # Platform authentication for all platforms (with prefixes)
    _add_all_platform_auth_options(parser)

    parser.set_defaults(command=_handle_schedule_run)

    return parser


def _add_all_platform_auth_options(parser: ArgumentParser):
    """
    Add auth options for all platforms with prefixes.

    Args:
        parser: ArgumentParser to add options to
    """
    # X (formerly Twitter)
    x_auth = parser.add_argument_group(
        'X Authentication',
        'Required if scheduling X posts'
    )
    x_auth.add_argument('--x-consumer-key', metavar='<key>')
    x_auth.add_argument('--x-consumer-secret', metavar='<secret>')
    x_auth.add_argument('--x-oauth-token', metavar='<token>')
    x_auth.add_argument('--x-oauth-secret', metavar='<secret>')

    # Twitter (deprecated - use X instead)
    twitter_auth = parser.add_argument_group(
        'Twitter Authentication (Deprecated)',
        'Required if scheduling Twitter posts (deprecated: use X authentication with --x-* parameters)'
    )
    twitter_auth.add_argument('--twitter-consumer-key', metavar='<key>')
    twitter_auth.add_argument('--twitter-consumer-secret', metavar='<secret>')
    twitter_auth.add_argument('--twitter-oauth-token', metavar='<token>')
    twitter_auth.add_argument('--twitter-oauth-secret', metavar='<secret>')

    # Facebook
    facebook_auth = parser.add_argument_group(
        'Facebook Authentication',
        'Required if scheduling Facebook posts'
    )
    facebook_auth.add_argument('--facebook-access-token', metavar='<token>')
    facebook_auth.add_argument('--facebook-object-id', metavar='<id>')
    facebook_auth.add_argument('--facebook-app-id', metavar='<id>')

    # Instagram
    instagram_auth = parser.add_argument_group(
        'Instagram Authentication',
        'Required if scheduling Instagram posts'
    )
    instagram_auth.add_argument('--instagram-access-token', metavar='<token>')
    instagram_auth.add_argument('--instagram-object-id', metavar='<id>')
    instagram_auth.add_argument('--instagram-client-id', metavar='<id>')
    instagram_auth.add_argument('--instagram-client-secret', metavar='<secret>')

    # LinkedIn
    linkedin_auth = parser.add_argument_group(
        'LinkedIn Authentication',
        'Required if scheduling LinkedIn posts'
    )
    linkedin_auth.add_argument('--linkedin-access-token', metavar='<token>')
    linkedin_auth.add_argument('--linkedin-client-id', metavar='<id>')
    linkedin_auth.add_argument('--linkedin-client-secret', metavar='<secret>')

    # Discord
    discord_auth = parser.add_argument_group(
        'Discord Authentication',
        'Required if scheduling Discord posts'
    )
    discord_auth.add_argument('--discord-bot-token', metavar='<token>')
    discord_auth.add_argument('--discord-server-name', metavar='<name>')
    discord_auth.add_argument('--discord-channel-name', metavar='<name>')

    # YouTube
    youtube_auth = parser.add_argument_group(
        'YouTube Authentication',
        'Required if scheduling YouTube posts'
    )
    youtube_auth.add_argument('--youtube-client-id', metavar='<id>')
    youtube_auth.add_argument('--youtube-client-secret', metavar='<secret>')

    # TikTok
    tiktok_auth = parser.add_argument_group(
        'TikTok Authentication',
        'Required if scheduling TikTok posts'
    )
    tiktok_auth.add_argument('--tiktok-client-key', metavar='<key>')
    tiktok_auth.add_argument('--tiktok-client-secret', metavar='<secret>')
    tiktok_auth.add_argument('--tiktok-access-token', metavar='<token>')
    tiktok_auth.add_argument('--tiktok-refresh-token', metavar='<token>')
    tiktok_auth.add_argument('--tiktok-username', metavar='<username>')

    # Threads
    threads_auth = parser.add_argument_group(
        'Threads Authentication',
        'Required if scheduling Threads posts'
    )
    threads_auth.add_argument('--threads-app-id', metavar='<id>')
    threads_auth.add_argument('--threads-app-secret', metavar='<secret>')
    threads_auth.add_argument('--threads-refresh-token', metavar='<token>')

    # Telegram
    telegram_auth = parser.add_argument_group(
        'Telegram Authentication',
        'Required if scheduling Telegram posts'
    )
    telegram_auth.add_argument('--telegram-bot-token', metavar='<token>')
    telegram_auth.add_argument('--telegram-chat-id', metavar='<id>')

    # WhatsApp
    whatsapp_auth = parser.add_argument_group(
        'WhatsApp Authentication',
        'Required if scheduling WhatsApp posts'
    )
    whatsapp_auth.add_argument('--whatsapp-access-token', metavar='<token>')
    whatsapp_auth.add_argument('--whatsapp-phone-number-id', metavar='<id>')
    whatsapp_auth.add_argument('--whatsapp-business-account-id', metavar='<id>')
    whatsapp_auth.add_argument('--whatsapp-recipient', metavar='<phone>')


def _normalize_network(network):
    """
    Normalize network parameter, handling twitter deprecation.

    Args:
        network: Network name from args

    Returns:
        Normalized network name
    """
    import sys
    if network == 'twitter':
        print("Warning: --network=twitter is deprecated. Use --network=x instead.", file=sys.stderr)
        return 'x'
    return network


def _map_deprecated_twitter_params(args):
    """
    Map deprecated twitter-* parameters to x-* format.

    Args:
        args: Parsed command-line arguments
    """
    import sys

    twitter_params_mapped = False
    param_mappings = [
        ('twitter_consumer_key', 'x_consumer_key', '--twitter-consumer-key', '--x-consumer-key', True),
        ('twitter_consumer_secret', 'x_consumer_secret', '--twitter-consumer-secret', '--x-consumer-secret', False),
        ('twitter_oauth_token', 'x_oauth_token', '--twitter-oauth-token', '--x-oauth-token', False),
        ('twitter_oauth_secret', 'x_oauth_secret', '--twitter-oauth-secret', '--x-oauth-secret', False),
    ]

    for old_attr, new_attr, old_param, new_param, always_warn in param_mappings:
        if hasattr(args, old_attr) and getattr(args, old_attr):
            should_warn = always_warn or not twitter_params_mapped
            if should_warn:
                print(f"Warning: {old_param} is deprecated. Use {new_param} instead.", file=sys.stderr)
                twitter_params_mapped = True
            if not hasattr(args, new_attr) or not getattr(args, new_attr):
                setattr(args, new_attr, getattr(args, old_attr))


def _map_x_to_legacy_twitter(args):
    """
    Map x-* parameters to legacy twitter_* format for backward compatibility.

    Args:
        args: Parsed command-line arguments
    """
    param_mappings = [
        ('x_consumer_key', 'twitter_consumer_key'),
        ('x_consumer_secret', 'twitter_consumer_secret'),
        ('x_oauth_token', 'twitter_oauth_token'),
        ('x_oauth_secret', 'twitter_oauth_secret'),
    ]

    for new_attr, old_attr in param_mappings:
        if hasattr(args, new_attr) and getattr(args, new_attr):
            setattr(args, old_attr, getattr(args, new_attr))


def _build_legacy_args(args, network):
    """
    Build legacy args dictionary for schedule action.

    Args:
        args: Parsed command-line arguments
        network: Normalized network name

    Returns:
        Dictionary of legacy arguments
    """
    legacy_args = {
        'action': 'schedule',
        'google_sheets_id': args.sheets_id,
        'google_sheets_name': args.sheets_name,
        'google_sheets_client_email': args.sheets_client_email,
        'google_sheets_private_key': args.sheets_private_key,
    }

    if network:
        legacy_args['network'] = network

    # Add all platform-specific auth (pass through with original names)
    excluded_keys = {'handler', *legacy_args.keys()}
    for key, value in vars(args).items():
        if value is not None and key not in excluded_keys:
            legacy_args[key] = value

    return legacy_args


def _handle_schedule_run(args: Namespace):
    """
    Handle schedule run by calling legacy publish command.

    Args:
        args: Parsed command-line arguments

    Returns:
        Exit status from core execution
    """
    network = _normalize_network(args.network)
    _map_deprecated_twitter_params(args)
    _map_x_to_legacy_twitter(args)
    legacy_args = _build_legacy_args(args, network)
    return publish_main(**legacy_args)
