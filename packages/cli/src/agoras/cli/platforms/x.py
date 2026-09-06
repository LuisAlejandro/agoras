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

from ..base import (
    add_common_content_options,
    add_profile_to_all,
    add_video_options,
    run_platform_command,
)
from ..content import add_content_file_option


def create_x_parser(subparsers: _SubParsersAction) -> ArgumentParser:
    """
    Create X platform subcommand parser.

    Args:
        subparsers: Subparsers action from parent parser

    Returns:
        ArgumentParser for X commands
    """
    return _build_x_parser(
        subparsers,
        command="x",
        label="X",
        parser_help="X (formerly Twitter) social network operations",
        handler=_handle_x_command,
    )


def _build_x_parser(subparsers, *, command, label, parser_help, handler):
    """Build the shared X action parser under ``command`` (``x`` or its ``twitter`` alias)."""
    parser = subparsers.add_parser(command, help=parser_help)

    actions = parser.add_subparsers(dest="action", title=f"{label} Actions", required=True)
    authorized = f'Requires prior authorization via "agoras {command} authorize".'

    # Authorize action
    authorize = actions.add_parser(
        "authorize", help=f"Authorize {label} account (OAuth 1.0a). Run this first before any other actions."
    )
    _add_x_auth_options(authorize)

    # Post action
    post = actions.add_parser("post", help=f"Create a text/image post on {label}. {authorized}")
    add_common_content_options(post, images=4)

    # Video action
    video = actions.add_parser("video", help=f"Upload a video to {label}. {authorized}")
    _add_video_options(video)
    add_common_content_options(video, images=0, with_content_file=False)

    # Thread action
    thread = actions.add_parser("thread", help=f"Publish an ordered thread on {label}. {authorized}")
    add_content_file_option(thread)

    # Like action
    like = actions.add_parser("like", help=f"Like a tweet. {authorized}")
    _add_post_id_option(like)

    # Share action (retweet)
    share = actions.add_parser("share", help=f"Retweet/share a tweet. {authorized}")
    _add_post_id_option(share)

    # Delete action
    delete = actions.add_parser("delete", help=f"Delete a tweet. {authorized}")
    _add_post_id_option(delete)

    # Delete-reply action (alias for delete on X)
    delete_reply = actions.add_parser("delete-reply", help=f"Delete a reply tweet. {authorized}")
    _add_post_id_option(delete_reply)

    # Reply action
    reply = actions.add_parser("reply", help=f"Reply to a tweet. {authorized}")
    _add_post_id_option(reply)
    add_common_content_options(reply, images=4)
    add_video_options(reply, platform="twitter", with_content_file=False)

    # Get-post action
    get_post = actions.add_parser("get-post", help=f"Read a tweet. {authorized}")
    _add_post_id_option(get_post)

    # Get-reply action
    get_reply = actions.add_parser("get-reply", help=f"Read a reply tweet. {authorized}")
    _add_post_id_option(get_reply)

    # List-posts action
    list_posts = actions.add_parser("list-posts", help=f"List recent tweets. {authorized}")
    _add_limit_option(list_posts)

    parser.set_defaults(command=handler)

    add_profile_to_all(actions)

    return parser


def _add_x_auth_options(parser: ArgumentParser):
    """
    Add X authentication options for the authorize action.

    Args:
        parser: ArgumentParser to add options to
    """
    auth = parser.add_argument_group("X Authentication", "X API credentials from developer.twitter.com")

    auth.add_argument("--consumer-key", required=True, metavar="<key>", help="X API consumer key")
    auth.add_argument("--consumer-secret", required=True, metavar="<secret>", help="X API consumer secret")


def _add_video_options(parser: ArgumentParser):
    """Add video-specific options for X."""
    add_video_options(parser, platform="twitter")


def _add_post_id_option(parser: ArgumentParser):
    """
    Add post ID option for like/share/delete actions.

    Args:
        parser: ArgumentParser to add options to
    """
    parser.add_argument("--post-id", required=True, metavar="<id>", help="Tweet ID to interact with")


def _add_limit_option(parser: ArgumentParser):
    """
    Add limit option for list-posts action.

    Args:
        parser: ArgumentParser to add options to
    """
    parser.add_argument("--limit", type=int, metavar="<n>", help="Maximum number of posts to list")


def _handle_x_command(args: Namespace):
    """
    Handle X command by converting args and calling core.

    Args:
        args: Parsed command-line arguments

    Returns:
        Exit status from core execution
    """
    return run_platform_command("x", args, x_main)


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
    return _build_x_parser(
        subparsers,
        command="twitter",
        label="Twitter/X",
        parser_help='Twitter/X social network operations (deprecated: use "x" instead)',
        handler=_handle_twitter_command,
    )
