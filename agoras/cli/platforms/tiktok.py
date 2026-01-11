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
TikTok platform CLI parser.

This module provides the TikTok command parser for the new CLI structure.
Note: TikTok is a video-only platform, so no 'post' action is available.
"""

from argparse import ArgumentParser, Namespace, _SubParsersAction

from ...core.tiktok import main as tiktok_main
from ..converter import ParameterConverter
from ..validator import ActionValidator


def create_tiktok_parser(subparsers: _SubParsersAction) -> ArgumentParser:
    """
    Create TikTok platform subcommand parser.

    Args:
        subparsers: Subparsers action from parent parser

    Returns:
        ArgumentParser for TikTok commands
    """
    parser = subparsers.add_parser(
        'tiktok',
        help='TikTok operations. Run "agoras tiktok authorize" before any actions.'
    )

    actions = parser.add_subparsers(
        dest='action',
        title='TikTok Actions',
        required=True
    )

    # Authorize action
    authorize = actions.add_parser(
        'authorize',
        help='Authorize TikTok account (OAuth 2.0). Run this first before any other actions.'
    )
    _add_tiktok_authorize_options(authorize)

    # Video action (main action for TikTok)
    video = actions.add_parser(
        'video',
        help='Upload a video to TikTok. Requires prior authorization via "agoras tiktok authorize".'
    )
    _add_video_options(video)

    # Set handler
    parser.set_defaults(handler=_handle_tiktok_command)

    return parser


def _add_tiktok_authorize_options(parser: ArgumentParser):
    """
    Add TikTok OAuth authorization options.

    Args:
        parser: ArgumentParser to add options to
    """
    auth = parser.add_argument_group(
        'TikTok OAuth Credentials',
        'Get these from https://developers.tiktok.com'
    )
    auth.add_argument(
        '--client-key',
        required=True,
        metavar='<key>',
        help='TikTok App client key'
    )
    auth.add_argument(
        '--client-secret',
        required=True,
        metavar='<secret>',
        help='TikTok App client secret'
    )
    auth.add_argument(
        '--username',
        required=True,
        metavar='<username>',
        help='TikTok username for authentication'
    )


def _add_video_options(parser: ArgumentParser):
    """
    Add video-specific options for TikTok.

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
        help='Video title/caption'
    )
    video.add_argument(
        '--privacy',
        metavar='<status>',
        default='SELF_ONLY',
        choices=['PUBLIC_TO_EVERYONE', 'MUTUAL_FOLLOW_FRIENDS',
                 'FOLLOWER_OF_CREATOR', 'SELF_ONLY'],
        help='Video privacy status (default: SELF_ONLY)'
    )


def _handle_tiktok_command(args: Namespace):
    """
    Handle TikTok command by converting args and calling core.

    Args:
        args: Parsed command-line arguments

    Returns:
        Exit status from core execution
    """
    # Validate action
    ActionValidator.validate('tiktok', args.action)

    # Convert new args to legacy format
    converter = ParameterConverter('tiktok')
    legacy_args = converter.convert_to_legacy(args)

    # Call core TikTok module
    return tiktok_main(legacy_args)
