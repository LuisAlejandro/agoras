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
Discord platform CLI parser.

This module provides the Discord command parser for the new CLI structure.
"""

from argparse import ArgumentParser, Namespace, _SubParsersAction

from agoras.platforms.discord.wrapper import main as discord_main

from ..base import add_common_content_options
from ..converter import ParameterConverter
from ..validator import ActionValidator


def create_discord_parser(subparsers: _SubParsersAction) -> ArgumentParser:
    """
    Create Discord platform subcommand parser.

    Args:
        subparsers: Subparsers action from parent parser

    Returns:
        ArgumentParser for Discord commands
    """
    parser = subparsers.add_parser(
        'discord',
        help='Discord chat platform operations'
    )

    actions = parser.add_subparsers(
        dest='action',
        title='Discord Actions',
        required=True
    )

    # Authorize action
    authorize = actions.add_parser(
        'authorize',
        help='Set up Discord bot token'
    )
    _add_discord_auth_options(authorize)

    # Post action
    post = actions.add_parser(
        'post',
        help='Send a message to Discord channel. Requires prior authorization via "agoras discord authorize".'
    )
    _add_discord_auth_options(post, required=False)
    add_common_content_options(post, images=4)

    # Video action
    video = actions.add_parser(
        'video',
        help='Send a video to Discord channel. Requires prior authorization via "agoras discord authorize".'
    )
    _add_discord_auth_options(video, required=False)
    _add_video_options(video)

    # Delete action
    delete = actions.add_parser(
        'delete',
        help='Delete a Discord message. Requires prior authorization via "agoras discord authorize".'
    )
    _add_discord_auth_options(delete, required=False)
    _add_post_id_option(delete)

    # Set handler
    parser.set_defaults(command=_handle_discord_command)

    return parser


def _add_discord_auth_options(parser: ArgumentParser, required: bool = True):
    """
    Add Discord authentication options.

    Args:
        parser: ArgumentParser to add options to
        required: Whether credentials are required (True for authorize, False for other actions)
    """
    auth = parser.add_argument_group(
        'Discord Authentication',
        'Discord bot credentials from discord.com/developers'
    )
    auth.add_argument(
        '--bot-token',
        required=required,
        metavar='<token>',
        help='Discord bot token' + (' (optional if already authorized)' if not required else '')
    )
    auth.add_argument(
        '--server-name',
        required=required,
        metavar='<name>',
        help='Discord server (guild) name' + (' (optional if already authorized)' if not required else '')
    )
    auth.add_argument(
        '--channel-name',
        required=required,
        metavar='<name>',
        help='Discord channel name' + (' (optional if already authorized)' if not required else '')
    )


def _add_video_options(parser: ArgumentParser):
    """
    Add video-specific options for Discord.

    Args:
        parser: ArgumentParser to add options to
    """
    video = parser.add_argument_group('Video Options')
    video.add_argument(
        '--video-url',
        required=True,
        metavar='<url>',
        help='URL of video file to send'
    )
    video.add_argument(
        '--video-title',
        metavar='<title>',
        help='Video title/description'
    )


def _add_post_id_option(parser: ArgumentParser):
    """
    Add post ID option for delete action.

    Args:
        parser: ArgumentParser to add options to
    """
    parser.add_argument(
        '--post-id',
        required=True,
        metavar='<id>',
        help='Discord message ID to delete'
    )


def _handle_discord_command(args: Namespace):
    """
    Handle Discord command by converting args and calling core.

    Args:
        args: Parsed command-line arguments

    Returns:
        Exit status from core execution
    """
    # Validate action
    ActionValidator.validate('discord', args.action)

    # Convert new args to legacy format
    converter = ParameterConverter('discord')
    legacy_args = converter.convert_to_legacy(args)

    # Call core Discord module
    return discord_main(legacy_args)
