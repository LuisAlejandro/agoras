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
Facebook platform CLI parser.

This module provides the Facebook command parser for the new CLI structure.
"""

from argparse import ArgumentParser, Namespace, _SubParsersAction

from agoras.platforms.facebook.wrapper import main as facebook_main

from ..base import add_common_content_options
from ..converter import ParameterConverter
from ..validator import ActionValidator


def create_facebook_parser(subparsers: _SubParsersAction) -> ArgumentParser:
    """
    Create Facebook platform subcommand parser.

    Args:
        subparsers: Subparsers action from parent parser

    Returns:
        ArgumentParser for Facebook commands
    """
    parser = subparsers.add_parser(
        'facebook',
        help='Facebook operations. Run "agoras facebook authorize" before any actions.'
    )

    actions = parser.add_subparsers(
        dest='action',
        title='Facebook Actions',
        required=True
    )

    # Authorize action
    authorize = actions.add_parser(
        'authorize',
        help='Authorize Facebook account (OAuth 2.0). Run this first before any other actions.'
    )
    _add_facebook_authorize_options(authorize)

    # Post action
    post = actions.add_parser(
        'post',
        help='Create a text/image post on Facebook. Requires prior authorization via "agoras facebook authorize".'
    )
    _add_facebook_action_options(post, object_id_required=False)
    add_common_content_options(post, images=4)

    # Video action
    video = actions.add_parser(
        'video',
        help='Upload a video to Facebook. Requires prior authorization via "agoras facebook authorize".'
    )
    _add_facebook_action_options(video, object_id_required=False)
    _add_video_options(video)
    add_common_content_options(video, images=0)

    # Like action
    like = actions.add_parser(
        'like',
        help='Like a Facebook post. Requires prior authorization via "agoras facebook authorize".'
    )
    _add_facebook_action_options(like, object_id_required=False)
    _add_post_id_option(like)

    # Share action
    share = actions.add_parser(
        'share',
        help='Share a Facebook post. Requires prior authorization via "agoras facebook authorize".'
    )
    _add_facebook_action_options(share, object_id_required=False)
    _add_post_id_option(share)
    _add_profile_id_option(share)

    # Delete action
    delete = actions.add_parser(
        'delete',
        help='Delete a Facebook post. Requires prior authorization via "agoras facebook authorize".'
    )
    _add_facebook_action_options(delete, object_id_required=False)
    _add_post_id_option(delete)

    # Set handler
    parser.set_defaults(command=_handle_facebook_command)

    return parser


def _add_facebook_authorize_options(parser: ArgumentParser):
    """
    Add Facebook OAuth authorization options.

    Args:
        parser: ArgumentParser to add options to
    """
    auth = parser.add_argument_group(
        'Facebook OAuth Credentials',
        'Get these from https://developers.facebook.com/apps'
    )
    auth.add_argument(
        '--client-id',
        required=True,
        metavar='<id>',
        help='Facebook App client ID'
    )
    auth.add_argument(
        '--client-secret',
        required=True,
        metavar='<secret>',
        help='Facebook App client secret'
    )
    auth.add_argument(
        '--app-id',
        required=True,
        metavar='<id>',
        help='Facebook App ID'
    )
    auth.add_argument(
        '--object-id',
        required=True,
        metavar='<id>',
        help='Facebook user ID for authentication'
    )


def _add_facebook_action_options(parser: ArgumentParser, object_id_required: bool = True):
    """
    Add Facebook action-specific options (no authentication tokens needed).

    Args:
        parser: ArgumentParser to add options to
        object_id_required: Whether object ID is required for this action
    """
    if object_id_required:
        parser.add_argument(
            '--object-id',
            required=True,
            metavar='<id>',
            help='Facebook page or profile ID where post will be published'
        )


def _add_video_options(parser: ArgumentParser):
    """
    Add video-specific options for Facebook.

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
    video.add_argument(
        '--video-description',
        metavar='<description>',
        help='Video description'
    )
    video.add_argument(
        '--video-type',
        metavar='<type>',
        help='Video type'
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
        help='Facebook post ID to interact with'
    )


def _add_profile_id_option(parser: ArgumentParser):
    """
    Add profile ID option for share action.

    Args:
        parser: ArgumentParser to add options to
    """
    parser.add_argument(
        '--profile-id',
        metavar='<id>',
        help='Facebook profile ID where post will be shared'
    )


def _handle_facebook_command(args: Namespace):
    """
    Handle Facebook command by converting args and calling core.

    Args:
        args: Parsed command-line arguments

    Returns:
        Exit status from core execution
    """
    # Validate action
    ActionValidator.validate('facebook', args.action)

    # Convert new args to legacy format
    converter = ParameterConverter('facebook')
    legacy_args = converter.convert_to_legacy(args)

    # Call core Facebook module
    return facebook_main(legacy_args)
