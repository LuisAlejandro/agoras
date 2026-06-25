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
Feed publish utility command.

This module provides the feed-publish command for RSS/Atom feed automation.
"""

from argparse import ArgumentParser, Namespace, _SubParsersAction

from ..platform_runner import execute_platform_action
from ..registry import PlatformRegistry


def create_feed_publish_parser(subparsers: _SubParsersAction) -> ArgumentParser:
    """
    Create feed-publish utility command parser.

    Args:
        subparsers: Subparsers action from utils parser

    Returns:
        ArgumentParser for feed-publish command
    """
    parser = subparsers.add_parser(
        'feed-publish',
        help='Publish content from RSS/Atom feed to social network'
    )

    parser.add_argument(
        '--network',
        required=True,
        choices=PlatformRegistry.get_platform_names(),
        metavar='<platform>',
        help='Target social network'
    )

    parser.add_argument(
        '--mode',
        required=True,
        choices=['last', 'random'],
        metavar='<mode>',
        help='Feed entry selection mode (last or random)'
    )

    feed = parser.add_argument_group('Feed Options')
    feed.add_argument(
        '--feed-url',
        required=True,
        metavar='<url>',
        help='URL of RSS/Atom feed'
    )
    feed.add_argument(
        '--max-count',
        type=int,
        metavar='<number>',
        help='Maximum posts to publish at once (default: 1)'
    )
    feed.add_argument(
        '--post-lookback',
        type=int,
        metavar='<seconds>',
        help='Only posts within last N seconds'
    )
    feed.add_argument(
        '--max-post-age',
        type=int,
        metavar='<days>',
        help='Maximum post age in days'
    )

    parser.set_defaults(command=_handle_feed_publish)

    return parser


def _handle_feed_publish(args: Namespace):
    """
    Handle feed publish via the shared platform runner.

    Args:
        args: Parsed command-line arguments

    Returns:
        Exit status from core execution
    """
    action = 'last-from-feed' if args.mode == 'last' else 'random-from-feed'

    legacy_args = {
        'network': args.network,
        'action': action,
        'feed_url': args.feed_url,
        'max_count': args.max_count,
        'post_lookback': args.post_lookback,
        'max_post_age': args.max_post_age,
    }

    return execute_platform_action(**legacy_args)
