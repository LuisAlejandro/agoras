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
LinkedIn platform CLI parser.

This module provides the LinkedIn command parser for the new CLI structure.
"""

from argparse import ArgumentParser, Namespace, _SubParsersAction

from ...core.linkedin import main as linkedin_main
from ..base import add_common_content_options
from ..converter import ParameterConverter
from ..validator import ActionValidator


def create_linkedin_parser(subparsers: _SubParsersAction) -> ArgumentParser:
    """
    Create LinkedIn platform subcommand parser.

    Args:
        subparsers: Subparsers action from parent parser

    Returns:
        ArgumentParser for LinkedIn commands
    """
    parser = subparsers.add_parser(
        'linkedin',
        help='LinkedIn operations. Run "agoras linkedin authorize" before any actions.'
    )

    actions = parser.add_subparsers(
        dest='action',
        title='LinkedIn Actions',
        required=True
    )

    # Authorize action
    authorize = actions.add_parser(
        'authorize',
        help='Authorize LinkedIn account (OAuth 2.0). Run this first before any other actions.'
    )
    _add_linkedin_authorize_options(authorize)

    # Post action
    post = actions.add_parser(
        'post',
        help='Create a post on LinkedIn. Requires prior authorization via "agoras linkedin authorize".'
    )
    add_common_content_options(post, images=1)

    # Video action
    video = actions.add_parser(
        'video',
        help='Upload a video to LinkedIn. Requires prior authorization via "agoras linkedin authorize".'
    )
    _add_video_options(video)

    # Like action
    like = actions.add_parser(
        'like',
        help='Like a LinkedIn post. Requires prior authorization via "agoras linkedin authorize".'
    )
    _add_post_id_option(like)

    # Share action
    share = actions.add_parser(
        'share',
        help='Share a LinkedIn post. Requires prior authorization via "agoras linkedin authorize".'
    )
    _add_post_id_option(share)

    # Delete action
    delete = actions.add_parser(
        'delete',
        help='Delete a LinkedIn post. Requires prior authorization via "agoras linkedin authorize".'
    )
    _add_post_id_option(delete)

    # Set handler
    parser.set_defaults(handler=_handle_linkedin_command)

    return parser


def _add_linkedin_authorize_options(parser: ArgumentParser):
    """
    Add LinkedIn OAuth authorization options.

    Args:
        parser: ArgumentParser to add options to
    """
    auth = parser.add_argument_group(
        'LinkedIn OAuth Credentials',
        'Get these from https://www.linkedin.com/developers/apps'
    )
    auth.add_argument(
        '--client-id',
        required=True,
        metavar='<id>',
        help='LinkedIn App client ID'
    )
    auth.add_argument(
        '--client-secret',
        required=True,
        metavar='<secret>',
        help='LinkedIn App client secret'
    )
    auth.add_argument(
        '--object-id',
        required=True,
        metavar='<id>',
        help='LinkedIn user/organization ID'
    )


def _add_video_options(parser: ArgumentParser):
    """
    Add video-specific options for LinkedIn.

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
        help='Video title'
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
        help='LinkedIn post ID to interact with'
    )


def _handle_linkedin_command(args: Namespace):
    """
    Handle LinkedIn command by converting args and calling core.

    Args:
        args: Parsed command-line arguments

    Returns:
        Exit status from core execution
    """
    # Validate action
    ActionValidator.validate('linkedin', args.action)

    # Convert new args to legacy format
    converter = ParameterConverter('linkedin')
    legacy_args = converter.convert_to_legacy(args)

    # Call core LinkedIn module
    return linkedin_main(legacy_args)
