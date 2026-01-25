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
TikTok platform CLI parser.

This module provides the TikTok command parser for the new CLI structure.
"""

from argparse import ArgumentParser, Namespace, _SubParsersAction

from agoras.platforms.tiktok.wrapper import main as tiktok_main

from ..base import add_common_content_options
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
        help='TikTok operations. Video upload requires Production app approval. Run "agoras tiktok authorize" first.'
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

    # Post action (photo slideshow)
    post = actions.add_parser(
        'post',
        help='Create a photo slideshow post on TikTok. Requires prior authorization via "agoras tiktok authorize".'
    )
    _add_post_options(post)

    # Video action
    video = actions.add_parser(
        'video',
        help='Upload a video to TikTok. Requires Production app approval and prior authorization.'
    )
    _add_video_options(video)

    # Set handler
    parser.set_defaults(command=_handle_tiktok_command)

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


def _add_post_options(parser: ArgumentParser):
    """
    Add post-specific options for TikTok photo slideshows.

    Args:
        parser: ArgumentParser to add options to
    """
    # Add common content options (text, link, images)
    add_common_content_options(parser, images=4)

    # Add TikTok-specific post options
    post_opts = parser.add_argument_group('TikTok Post Options')
    post_opts.add_argument(
        '--title',
        metavar='<title>',
        help='Post title/caption'
    )
    post_opts.add_argument(
        '--privacy',
        metavar='<status>',
        default='SELF_ONLY',
        choices=['PUBLIC_TO_EVERYONE', 'MUTUAL_FOLLOW_FRIENDS',
                 'FOLLOWER_OF_CREATOR', 'SELF_ONLY'],
        help='Post privacy status (default: SELF_ONLY)'
    )
    post_opts.add_argument(
        '--allow-comments',
        action='store_true',
        default=None,
        help='Allow comments on the post (default: true)'
    )
    post_opts.add_argument(
        '--auto-add-music',
        action='store_true',
        default=None,
        help='Automatically add music to the slideshow (default: false)'
    )
    post_opts.add_argument(
        '--brand-organic',
        action='store_true',
        default=None,
        help='Mark content as promotional (displays "Promotional content" label)'
    )
    post_opts.add_argument(
        '--brand-content',
        action='store_true',
        default=None,
        help='Mark content as paid partnership (displays "Paid partnership" label)'
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
    video.add_argument(
        '--allow-comments',
        action='store_true',
        default=None,
        help='Allow comments on the video (default: true)'
    )
    video.add_argument(
        '--allow-duet',
        action='store_true',
        default=None,
        help='Allow other users to duet with your video (default: true)'
    )
    video.add_argument(
        '--allow-stitch',
        action='store_true',
        default=None,
        help='Allow other users to stitch your video (default: true)'
    )
    video.add_argument(
        '--brand-organic',
        action='store_true',
        default=None,
        help='Mark content as promotional (displays "Promotional content" label)'
    )
    video.add_argument(
        '--brand-content',
        action='store_true',
        default=None,
        help='Mark content as paid partnership (displays "Paid partnership" label)'
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
