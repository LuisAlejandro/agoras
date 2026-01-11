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
YouTube platform CLI parser.

This module provides the YouTube command parser for the new CLI structure.
Note: YouTube is a video-only platform, so no 'post' action is available.
"""

from argparse import ArgumentParser, Namespace, _SubParsersAction

from agoras.platforms.youtube.wrapper import main as youtube_main
from ..converter import ParameterConverter
from ..validator import ActionValidator


def create_youtube_parser(subparsers: _SubParsersAction) -> ArgumentParser:
    """
    Create YouTube platform subcommand parser.

    Args:
        subparsers: Subparsers action from parent parser

    Returns:
        ArgumentParser for YouTube commands
    """
    parser = subparsers.add_parser(
        'youtube',
        help='YouTube operations. Run "agoras youtube authorize" before any actions.'
    )

    actions = parser.add_subparsers(
        dest='action',
        title='YouTube Actions',
        required=True
    )

    # Authorize action
    authorize = actions.add_parser(
        'authorize',
        help='Authorize YouTube account (OAuth 2.0). Run this first before any other actions.'
    )
    _add_youtube_authorize_options(authorize)

    # Video action (main action for YouTube)
    video = actions.add_parser(
        'video',
        help='Upload a video to YouTube. Requires prior authorization via "agoras youtube authorize".'
    )
    _add_video_options(video)

    # Like action
    like = actions.add_parser(
        'like',
        help='Like a YouTube video. Requires prior authorization via "agoras youtube authorize".'
    )
    _add_video_id_option(like)

    # Delete action
    delete = actions.add_parser(
        'delete',
        help='Delete a YouTube video. Requires prior authorization via "agoras youtube authorize".'
    )
    _add_video_id_option(delete)

    # Set handler
    parser.set_defaults(handler=_handle_youtube_command)

    return parser


def _add_youtube_authorize_options(parser: ArgumentParser):
    """
    Add YouTube OAuth authorization options.

    Args:
        parser: ArgumentParser to add options to
    """
    auth = parser.add_argument_group(
        'YouTube OAuth Credentials',
        'Get these from https://console.cloud.google.com'
    )
    auth.add_argument(
        '--client-id',
        required=True,
        metavar='<id>',
        help='YouTube (Google) OAuth client ID'
    )
    auth.add_argument(
        '--client-secret',
        required=True,
        metavar='<secret>',
        help='YouTube (Google) OAuth client secret'
    )


def _add_video_options(parser: ArgumentParser):
    """
    Add video-specific options for YouTube.

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
        '--title',
        metavar='<title>',
        help='Video title'
    )
    video.add_argument(
        '--description',
        metavar='<description>',
        help='Video description'
    )
    video.add_argument(
        '--category-id',
        metavar='<id>',
        help='YouTube category ID'
    )
    video.add_argument(
        '--privacy',
        metavar='<status>',
        default='private',
        choices=['public', 'private', 'unlisted'],
        help='Video privacy status (default: private)'
    )
    video.add_argument(
        '--keywords',
        metavar='<keywords>',
        help='Video keywords separated by comma'
    )


def _add_video_id_option(parser: ArgumentParser):
    """
    Add video ID option for like/delete actions.

    Args:
        parser: ArgumentParser to add options to
    """
    parser.add_argument(
        '--video-id',
        required=True,
        metavar='<id>',
        help='YouTube video ID to interact with'
    )


def _handle_youtube_command(args: Namespace):
    """
    Handle YouTube command by converting args and calling core.

    Args:
        args: Parsed command-line arguments

    Returns:
        Exit status from core execution
    """
    # Validate action
    ActionValidator.validate('youtube', args.action)

    # Convert new args to legacy format
    converter = ParameterConverter('youtube')
    legacy_args = converter.convert_to_legacy(args)

    # Call core YouTube module
    return youtube_main(legacy_args)
