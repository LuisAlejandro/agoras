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
Instagram platform CLI parser.

This module provides the Instagram command parser for the new CLI structure.
"""

from argparse import SUPPRESS, ArgumentParser, Namespace, _SubParsersAction

from agoras.platforms.instagram.wrapper import main as instagram_main

from ..base import add_common_content_options, add_profile_to_all, prepare_content_args, resolve_action_profile
from ..content import add_content_file_option
from ..converter import ParameterConverter
from ..media_help import video_url_help
from ..validator import ActionValidator


def create_instagram_parser(subparsers: _SubParsersAction) -> ArgumentParser:
    """
    Create Instagram platform subcommand parser.

    Args:
        subparsers: Subparsers action from parent parser

    Returns:
        ArgumentParser for Instagram commands
    """
    parser = subparsers.add_parser(
        "instagram", help='Instagram operations. Run "agoras instagram authorize" before any actions.'
    )

    actions = parser.add_subparsers(dest="action", title="Instagram Actions", required=True)

    # Authorize action
    authorize = actions.add_parser(
        "authorize", help="Authorize Instagram account (OAuth 2.0). Run this first before any other actions."
    )
    _add_instagram_authorize_options(authorize)

    # Post action
    post = actions.add_parser(
        "post", help='Create a photo post on Instagram. Requires prior authorization via "agoras instagram authorize".'
    )
    _add_instagram_action_options(post, object_id_required=False)
    add_common_content_options(post, images=1)

    # Video action
    video = actions.add_parser(
        "video", help='Upload a video to Instagram. Requires prior authorization via "agoras instagram authorize".'
    )
    _add_instagram_action_options(video, object_id_required=False)
    _add_video_options(video)

    # Reply action
    reply = actions.add_parser(
        "reply", help='Comment on an Instagram post. Requires prior authorization via "agoras instagram authorize".'
    )
    _add_instagram_action_options(reply, object_id_required=False)
    _add_post_id_option(reply)
    reply.add_argument("--text", required=True, metavar="<text>", help="Comment text to post on the Instagram post")

    # Delete-reply action (delete an Instagram comment)
    delete_reply = actions.add_parser(
        "delete-reply",
        help='Delete an Instagram comment. Requires prior authorization via "agoras instagram authorize".',
    )
    _add_instagram_action_options(delete_reply, object_id_required=False)
    _add_post_id_option(delete_reply)

    # Delete action (delete an Instagram media post)
    delete = actions.add_parser(
        "delete",
        help='Delete an Instagram media post. Requires prior authorization via "agoras instagram authorize".',
    )
    _add_instagram_action_options(delete, object_id_required=False)
    _add_post_id_option(delete)

    # Get-post action
    get_post = actions.add_parser(
        "get-post",
        help='Read an Instagram media object. Requires prior authorization via "agoras instagram authorize".',
    )
    _add_post_id_option(get_post)

    # Get-reply action
    get_reply = actions.add_parser(
        "get-reply",
        help='Read an Instagram comment. Requires prior authorization via "agoras instagram authorize".',
    )
    _add_post_id_option(get_reply)

    # List-posts action
    list_posts = actions.add_parser(
        "list-posts",
        help='List recent Instagram media. Requires prior authorization via "agoras instagram authorize".',
    )
    _add_limit_option(list_posts)
    list_posts.add_argument(
        "--object-id",
        required=True,
        metavar="<id>",
        help="Instagram business account ID whose media to list",
    )

    # Set handler
    parser.set_defaults(command=_handle_instagram_command)

    add_profile_to_all(actions)

    return parser


def _add_instagram_authorize_options(parser: ArgumentParser):
    """
    Add Instagram OAuth authorization options.

    Args:
        parser: ArgumentParser to add options to
    """
    auth = parser.add_argument_group(
        "Instagram OAuth Credentials",
        "Get these from https://developers.facebook.com/apps (Instagram uses Facebook OAuth)",
    )
    auth.add_argument("--client-id", required=True, metavar="<id>", help="Facebook App client ID")
    auth.add_argument("--client-secret", required=True, metavar="<secret>", help="Facebook App client secret")
    auth.add_argument(
        "--object-id", required=True, metavar="<id>", help="Facebook user ID (for Instagram business account)"
    )


def _add_instagram_action_options(parser: ArgumentParser, object_id_required: bool = True):
    """
    Add Instagram action-specific options (no authentication tokens needed).

    Args:
        parser: ArgumentParser to add options to
        object_id_required: Whether object ID is required for this action
    """
    if object_id_required:
        parser.add_argument("--object-id", required=True, metavar="<id>", help="Instagram business account ID")


def _add_video_options(parser: ArgumentParser):
    """
    Add video-specific options for Instagram.

    Content fields use SUPPRESS so --content can supply them without argparse
    requiredness blocking file mode.

    Args:
        parser: ArgumentParser to add options to
    """
    add_content_file_option(parser)

    video = parser.add_argument_group("Video Options")
    video.add_argument("--video-url", default=SUPPRESS, metavar="<media>", help=video_url_help("instagram"))
    video.add_argument("--video-caption", default=SUPPRESS, metavar="<caption>", help="Video caption")
    video.add_argument(
        "--video-type",
        default=SUPPRESS,
        metavar="<type>",
        help="Video type: REELS (default) or STORIES (case-insensitive; reel/story also accepted)",
    )


def _add_post_id_option(parser: ArgumentParser):
    """
    Add post ID option for reply action.

    Args:
        parser: ArgumentParser to add options to
    """
    parser.add_argument("--post-id", required=True, metavar="<id>", help="Instagram post ID to interact with")


def _add_limit_option(parser: ArgumentParser):
    """
    Add limit option for list-posts action.

    Args:
        parser: ArgumentParser to add options to
    """
    parser.add_argument("--limit", type=int, metavar="<n>", help="Maximum number of posts to list")


def _handle_instagram_command(args: Namespace):
    """
    Handle Instagram command by converting args and calling core.

    Args:
        args: Parsed command-line arguments

    Returns:
        Exit status from core execution
    """
    # Validate action
    ActionValidator.validate("instagram", args.action)
    prepare_content_args(args, "instagram")

    # Convert new args to legacy format
    converter = ParameterConverter("instagram")
    legacy_args = converter.convert_to_legacy(args)

    # Resolve and inject the credential profile for non-authorize actions
    resolve_action_profile("instagram", args, legacy_args)

    # Call core Instagram module
    return instagram_main(legacy_args)
