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
Threads platform CLI parser.

This module provides the Threads command parser for the new CLI structure.
"""

from argparse import ArgumentParser, Namespace, _SubParsersAction

from agoras.platforms.threads.wrapper import main as threads_main

from ..base import add_common_content_options
from ..converter import ParameterConverter
from ..validator import ActionValidator


def create_threads_parser(subparsers: _SubParsersAction) -> ArgumentParser:
    """
    Create Threads platform subcommand parser.

    Args:
        subparsers: Subparsers action from parent parser

    Returns:
        ArgumentParser for Threads commands
    """
    parser = subparsers.add_parser(
        'threads',
        help='Threads operations. Run "agoras threads authorize" before any actions.'
    )

    actions = parser.add_subparsers(
        dest='action',
        title='Threads Actions',
        required=True
    )

    # Authorize action
    authorize = actions.add_parser(
        'authorize',
        help='Authorize Threads account (OAuth 2.0). Run this first before any other actions.'
    )
    _add_threads_authorize_options(authorize)

    # Post action
    post = actions.add_parser(
        'post',
        help='Create a post on Threads. Requires prior authorization via "agoras threads authorize".'
    )
    add_common_content_options(post, images=4)

    # Video action
    video = actions.add_parser(
        'video',
        help='Upload a video to Threads. Requires prior authorization via "agoras threads authorize".'
    )
    _add_video_options(video)

    # Share action
    share = actions.add_parser(
        'share',
        help='Share/repost a Threads post. Requires prior authorization via "agoras threads authorize".'
    )
    _add_post_id_option(share)

    # Set handler
    parser.set_defaults(command=_handle_threads_command)

    return parser


def _add_threads_authorize_options(parser: ArgumentParser):
    """
    Add Threads OAuth authorization options.

    Args:
        parser: ArgumentParser to add options to
    """
    auth = parser.add_argument_group(
        'Threads OAuth Credentials',
        'Get these from https://developers.facebook.com/apps'
    )
    auth.add_argument(
        '--app-id',
        required=True,
        metavar='<id>',
        help='Threads (Meta) App ID'
    )
    auth.add_argument(
        '--app-secret',
        required=True,
        metavar='<secret>',
        help='Threads (Meta) App secret'
    )


def _add_video_options(parser: ArgumentParser):
    """
    Add video-specific options for Threads.

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
        help='Video caption/description'
    )


def _add_post_id_option(parser: ArgumentParser):
    """
    Add post ID option for share action.

    Args:
        parser: ArgumentParser to add options to
    """
    parser.add_argument(
        '--post-id',
        required=True,
        metavar='<id>',
        help='Threads post ID to share'
    )


def _handle_threads_command(args: Namespace):
    """
    Handle Threads command by converting args and calling core.

    Args:
        args: Parsed command-line arguments

    Returns:
        Exit status from core execution
    """
    # Validate action
    ActionValidator.validate('threads', args.action)

    # Convert new args to legacy format
    converter = ParameterConverter('threads')
    legacy_args = converter.convert_to_legacy(args)

    # Call core Threads module
    return threads_main(legacy_args)
