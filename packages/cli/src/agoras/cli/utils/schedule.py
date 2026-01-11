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

    parser.set_defaults(handler=_handle_schedule_run)

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


def _handle_schedule_run(args: Namespace):
    """
    Handle schedule run by calling legacy publish command.

    Args:
        args: Parsed command-line arguments

    Returns:
        Exit status from core execution
    """
    import sys

    # Handle network parameter deprecation
    network = args.network
    if network == 'twitter':
        print("Warning: --network=twitter is deprecated. Use --network=x instead.", file=sys.stderr)
        network = 'x'

    # Map deprecated twitter-* parameters to x-* or legacy twitter_* format
    twitter_params_mapped = False
    if hasattr(args, 'twitter_consumer_key') and args.twitter_consumer_key:
        print("Warning: --twitter-consumer-key is deprecated. Use --x-consumer-key instead.", file=sys.stderr)
        if not hasattr(args, 'x_consumer_key') or not args.x_consumer_key:
            args.x_consumer_key = args.twitter_consumer_key
        twitter_params_mapped = True

    if hasattr(args, 'twitter_consumer_secret') and args.twitter_consumer_secret:
        if not twitter_params_mapped:
            print("Warning: --twitter-consumer-secret is deprecated. Use --x-consumer-secret instead.", file=sys.stderr)
        if not hasattr(args, 'x_consumer_secret') or not args.x_consumer_secret:
            args.x_consumer_secret = args.twitter_consumer_secret

    if hasattr(args, 'twitter_oauth_token') and args.twitter_oauth_token:
        if not twitter_params_mapped:
            print("Warning: --twitter-oauth-token is deprecated. Use --x-oauth-token instead.", file=sys.stderr)
        if not hasattr(args, 'x_oauth_token') or not args.x_oauth_token:
            args.x_oauth_token = args.twitter_oauth_token

    if hasattr(args, 'twitter_oauth_secret') and args.twitter_oauth_secret:
        if not twitter_params_mapped:
            print("Warning: --twitter-oauth-secret is deprecated. Use --x-oauth-secret instead.", file=sys.stderr)
        if not hasattr(args, 'x_oauth_secret') or not args.x_oauth_secret:
            args.x_oauth_secret = args.twitter_oauth_secret

    # Map x-* parameters to legacy twitter_* format for backward compatibility
    if hasattr(args, 'x_consumer_key') and args.x_consumer_key:
        args.twitter_consumer_key = args.x_consumer_key
    if hasattr(args, 'x_consumer_secret') and args.x_consumer_secret:
        args.twitter_consumer_secret = args.x_consumer_secret
    if hasattr(args, 'x_oauth_token') and args.x_oauth_token:
        args.twitter_oauth_token = args.x_oauth_token
    if hasattr(args, 'x_oauth_secret') and args.x_oauth_secret:
        args.twitter_oauth_secret = args.x_oauth_secret

    # Build legacy args for schedule action
    legacy_args = {
        'action': 'schedule',
        'google_sheets_id': args.sheets_id,
        'google_sheets_name': args.sheets_name,
        'google_sheets_client_email': args.sheets_client_email,
        'google_sheets_private_key': args.sheets_private_key,
    }

    # Add network if specified
    if network:
        legacy_args['network'] = network

    # Add all platform-specific auth (pass through with original names)
    for key, value in vars(args).items():
        if value is not None and key not in legacy_args and key not in ['handler']:
            legacy_args[key] = value

    return publish_main(**legacy_args)
