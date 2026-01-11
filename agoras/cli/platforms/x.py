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
X platform CLI parser.

This module provides the X command parser for the new CLI structure.
"""

from argparse import ArgumentParser, Namespace, _SubParsersAction

from ...core.x import main as x_main
from ..base import add_common_content_options
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
        help='Authorize X account (OAuth 1.0a)'
    )
    _add_x_auth_options(authorize, oauth_required=False)

    # Post action
    post = actions.add_parser(
        'post',
        help='Create a text/image post on X'
    )
    _add_x_auth_options(post, oauth_required=True)
    add_common_content_options(post, images=4)

    # Video action
    video = actions.add_parser(
        'video',
        help='Upload a video to X'
    )
    _add_x_auth_options(video, oauth_required=True)
    _add_video_options(video)
    add_common_content_options(video, images=0)

    # Like action
    like = actions.add_parser(
        'like',
        help='Like a tweet'
    )
    _add_x_auth_options(like, oauth_required=True)
    _add_post_id_option(like)

    # Share action (retweet)
    share = actions.add_parser(
        'share',
        help='Retweet/share a tweet'
    )
    _add_x_auth_options(share, oauth_required=True)
    _add_post_id_option(share)

    # Delete action
    delete = actions.add_parser(
        'delete',
        help='Delete a tweet'
    )
    _add_x_auth_options(delete, oauth_required=True)
    _add_post_id_option(delete)

    # Set handler
    parser.set_defaults(handler=_handle_x_command)

    return parser


def _add_x_auth_options(parser: ArgumentParser, oauth_required: bool = True):
    """
    Add X authentication options.

    Args:
        parser: ArgumentParser to add options to
        oauth_required: Whether OAuth tokens are required
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

    if oauth_required:
        auth.add_argument(
            '--oauth-token',
            required=True,
            metavar='<token>',
            help='X OAuth token'
        )
        auth.add_argument(
            '--oauth-secret',
            required=True,
            metavar='<secret>',
            help='X OAuth secret'
        )


def _add_video_options(parser: ArgumentParser):
    """
    Add video-specific options for X.

    Args:
        parser: ArgumentParser to add options to
    """
    video = parser.add_argument_group('Video Options')
    video.add_argument(
        '--video-url',
        required=True,
        metavar='<url>',
        help='URL of video file to upload'
    )
    video.add_argument(
        '--video-title',
        metavar='<title>',
        help='Video title/description'
    )


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
        help='Authorize Twitter/X account (OAuth 1.0a)'
    )
    _add_x_auth_options(authorize, oauth_required=False)

    # Post action
    post = actions.add_parser(
        'post',
        help='Create a text/image post on Twitter/X'
    )
    _add_x_auth_options(post, oauth_required=True)
    add_common_content_options(post, images=4)

    # Video action
    video = actions.add_parser(
        'video',
        help='Upload a video to Twitter/X'
    )
    _add_x_auth_options(video, oauth_required=True)
    _add_video_options(video)
    add_common_content_options(video, images=0)

    # Like action
    like = actions.add_parser(
        'like',
        help='Like a tweet'
    )
    _add_x_auth_options(like, oauth_required=True)
    _add_post_id_option(like)

    # Share action (retweet)
    share = actions.add_parser(
        'share',
        help='Retweet/share a tweet'
    )
    _add_x_auth_options(share, oauth_required=True)
    _add_post_id_option(share)

    # Delete action
    delete = actions.add_parser(
        'delete',
        help='Delete a tweet'
    )
    _add_x_auth_options(delete, oauth_required=True)
    _add_post_id_option(delete)

    # Set handler
    parser.set_defaults(handler=_handle_twitter_command)

    return parser
