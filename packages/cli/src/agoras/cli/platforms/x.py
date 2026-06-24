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
X platform CLI parser.

This module provides the X command parser for the new CLI structure.
"""

from argparse import ArgumentParser, Namespace, _SubParsersAction

from agoras.platforms.x.wrapper import main as x_main

from ..base import add_common_content_options, add_video_options
from ..converter import ParameterConverter
from ..validator import ActionValidator


def create_x_parser(subparsers: _SubParsersAction) -> ArgumentParser:
    """
    Create X platform subcommand parser.

    Args:
        subparsers: Subparsers action from parent parser

    Returns:
        ArgumentParser for X commands
    """
    parser = subparsers.add_parser(
        'x',
        help='X (formerly Twitter) social network operations'
    )

    actions = parser.add_subparsers(
        dest='action',
        title='X Actions',
        required=True
    )

    # Authorize action
    authorize = actions.add_parser(
        'authorize',
        help='Authorize X account (OAuth 1.0a). Run this first before any other actions.'
    )
    _add_x_auth_options(authorize)

    # Post action
    post = actions.add_parser(
        'post',
        help='Create a text/image post on X. Requires prior authorization via "agoras x authorize".'
    )
    add_common_content_options(post, images=4)

    # Video action
    video = actions.add_parser(
        'video',
        help='Upload a video to X. Requires prior authorization via "agoras x authorize".'
    )
    _add_video_options(video)
    add_common_content_options(video, images=0)

    # Like action
    like = actions.add_parser(
        'like',
        help='Like a tweet. Requires prior authorization via "agoras x authorize".'
    )
    _add_post_id_option(like)

    # Share action (retweet)
    share = actions.add_parser(
        'share',
        help='Retweet/share a tweet. Requires prior authorization via "agoras x authorize".'
    )
    _add_post_id_option(share)

    # Delete action
    delete = actions.add_parser(
        'delete',
        help='Delete a tweet. Requires prior authorization via "agoras x authorize".'
    )
    _add_post_id_option(delete)

    # Set handler
    parser.set_defaults(command=_handle_x_command)

    return parser


def _add_x_auth_options(parser: ArgumentParser):
    """
    Add X authentication options for the authorize action.

    Args:
        parser: ArgumentParser to add options to
    """
    auth = parser.add_argument_group(
        'X Authentication',
        'X API credentials from developer.twitter.com'
    )

    auth.add_argument(
        '--consumer-key',
        required=True,
        metavar='<key>',
        help='X API consumer key'
    )
    auth.add_argument(
        '--consumer-secret',
        required=True,
        metavar='<secret>',
        help='X API consumer secret'
    )


def _add_video_options(parser: ArgumentParser):
    """Add video-specific options for X."""
    add_video_options(parser, platform='twitter')


def _add_post_id_option(parser: ArgumentParser):
    """
    Add post ID option for like/share/delete actions.

    Args:
        parser: ArgumentParser to add options to
    """
    parser.add_argument(
        '--post-id',
        required=True,
        metavar='<id>',
        help='Tweet ID to interact with'
    )


def _handle_x_command(args: Namespace):
    """
    Handle X command by converting args and calling core.

    Args:
        args: Parsed command-line arguments

    Returns:
        Exit status from core execution
    """
    # Validate action
    ActionValidator.validate('x', args.action)

    # Convert new args to legacy format
    converter = ParameterConverter('x')
    legacy_args = converter.convert_to_legacy(args)

    # Call core X module
    return x_main(legacy_args)


def _handle_twitter_command(args: Namespace):
    """
    Handle Twitter command (deprecated alias for X).

    Args:
        args: Parsed command-line arguments

    Returns:
        Exit status from core execution
    """
    import sys
    print("Warning: 'agoras twitter' is deprecated. Use 'agoras x' instead.", file=sys.stderr)

    # Delegate to X command handler
    return _handle_x_command(args)


def create_twitter_parser_alias(subparsers: _SubParsersAction) -> ArgumentParser:
    """
    Create Twitter platform subcommand parser (deprecated alias for X).

    This creates a 'twitter' command that delegates to the 'x' command
    with a deprecation warning.

    Args:
        subparsers: Subparsers action from parent parser

    Returns:
        ArgumentParser for Twitter commands (alias for X)
    """
    parser = subparsers.add_parser(
        'twitter',
        help='Twitter/X social network operations (deprecated: use "x" instead)'
    )

    actions = parser.add_subparsers(
        dest='action',
        title='Twitter Actions',
        required=True
    )

    # Authorize action
    authorize = actions.add_parser(
        'authorize',
        help='Authorize Twitter/X account (OAuth 1.0a). Run this first before any other actions.'
    )
    _add_x_auth_options(authorize)

    # Post action
    post = actions.add_parser(
        'post',
        help='Create a text/image post on Twitter/X. Requires prior authorization via "agoras twitter authorize".'
    )
    add_common_content_options(post, images=4)

    # Video action
    video = actions.add_parser(
        'video',
        help='Upload a video to Twitter/X. Requires prior authorization via "agoras twitter authorize".'
    )
    _add_video_options(video)
    add_common_content_options(video, images=0)

    # Like action
    like = actions.add_parser(
        'like',
        help='Like a tweet. Requires prior authorization via "agoras twitter authorize".'
    )
    _add_post_id_option(like)

    # Share action (retweet)
    share = actions.add_parser(
        'share',
        help='Retweet/share a tweet. Requires prior authorization via "agoras twitter authorize".'
    )
    _add_post_id_option(share)

    # Delete action
    delete = actions.add_parser(
        'delete',
        help='Delete a tweet. Requires prior authorization via "agoras twitter authorize".'
    )
    _add_post_id_option(delete)

    # Set handler
    parser.set_defaults(command=_handle_twitter_command)

    return parser
