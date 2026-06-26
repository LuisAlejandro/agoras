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
Telegram platform CLI parser.

This module provides the Telegram command parser for the new CLI structure.
"""

from argparse import ArgumentParser, Namespace, _SubParsersAction

from agoras.platforms.telegram.wrapper import main as telegram_main

from ..base import add_common_content_options, add_video_options
from ..converter import ParameterConverter
from ..validator import ActionValidator


def create_telegram_parser(subparsers: _SubParsersAction) -> ArgumentParser:
    """
    Create Telegram platform subcommand parser.

    Args:
        subparsers: Subparsers action from parent parser

    Returns:
        ArgumentParser for Telegram commands
    """
    parser = subparsers.add_parser("telegram", help="Telegram messaging platform operations")

    actions = parser.add_subparsers(dest="action", title="Telegram Actions", required=True)

    # Authorize action (bot token setup)
    authorize = actions.add_parser("authorize", help="Set up Telegram bot token")
    _add_telegram_authorize_options(authorize)

    # Post action
    post = actions.add_parser(
        "post", help='Send a message to Telegram chat. Requires prior authorization via "agoras telegram authorize".'
    )
    _add_telegram_action_options(post)
    add_common_content_options(post, images=4)

    # Video action
    video = actions.add_parser(
        "video", help='Send a video to Telegram chat. Requires prior authorization via "agoras telegram authorize".'
    )
    _add_telegram_action_options(video)
    add_video_options(video, platform="telegram")

    # Delete action
    delete = actions.add_parser(
        "delete", help='Delete a Telegram message. Requires prior authorization via "agoras telegram authorize".'
    )
    _add_post_id_option(delete)

    # Set handler
    parser.set_defaults(command=_handle_telegram_command)

    return parser


def _add_telegram_authorize_options(parser: ArgumentParser):
    """
    Add Telegram authorization options for the authorize action.

    Args:
        parser: ArgumentParser to add options to
    """
    auth = parser.add_argument_group("Telegram Authentication", "Telegram bot credentials from @BotFather")
    auth.add_argument("--bot-token", required=True, metavar="<token>", help="Telegram bot token from @BotFather")
    auth.add_argument("--chat-id", required=True, metavar="<id>", help="Target chat ID (user, group, or channel)")


def _add_telegram_action_options(parser: ArgumentParser):
    """
    Add Telegram action options (non-auth).

    Args:
        parser: ArgumentParser to add options to
    """
    parser.add_argument(
        "--parse-mode",
        choices=["HTML", "Markdown", "MarkdownV2", "None"],
        default="HTML",
        metavar="<mode>",
        help="Message parse mode (default: HTML)",
    )


def _add_post_id_option(parser: ArgumentParser):
    """
    Add post ID option for delete action.

    Args:
        parser: ArgumentParser to add options to
    """
    parser.add_argument("--post-id", required=True, metavar="<id>", help="Telegram message ID to delete")


def _handle_telegram_command(args: Namespace):
    """
    Handle Telegram command by converting args and calling core.

    Args:
        args: Parsed command-line arguments

    Returns:
        Exit status from core execution
    """
    # Validate action
    ActionValidator.validate("telegram", args.action)

    # Convert new args to legacy format
    converter = ParameterConverter("telegram")
    legacy_args = converter.convert_to_legacy(args)

    # Call core Telegram module
    return telegram_main(legacy_args)
