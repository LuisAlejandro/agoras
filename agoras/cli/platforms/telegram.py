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
Telegram platform CLI parser.

This module provides the Telegram command parser for the new CLI structure.
"""

from argparse import ArgumentParser, Namespace, _SubParsersAction

from ...core.telegram import main as telegram_main
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
    parser = subparsers.add_parser(
        'telegram',
        help='Telegram messaging platform operations'
    )

    actions = parser.add_subparsers(
        dest='action',
        title='Telegram Actions',
        required=True
    )

    # Authorize action (bot token setup)
    authorize = actions.add_parser(
        'authorize',
        help='Set up Telegram bot token'
    )
    _add_telegram_auth_options(authorize)

    # Post action
    post = actions.add_parser(
        'post',
        help='Send a message to Telegram chat'
    )
    _add_telegram_auth_options(post)
    add_common_content_options(post, images=4)

    # Video action
    video = actions.add_parser(
        'video',
        help='Send a video to Telegram chat'
    )
    _add_telegram_auth_options(video)
    add_video_options(video)

    # Edit action
    edit = actions.add_parser(
        'edit',
        help='Edit an existing Telegram message'
    )
    _add_telegram_auth_options(edit)
    _add_telegram_edit_options(edit)

    # Poll action
    poll = actions.add_parser(
        'poll',
        help='Send a poll to Telegram chat'
    )
    _add_telegram_auth_options(poll)
    _add_telegram_poll_options(poll)

    # Document action
    document = actions.add_parser(
        'document',
        help='Send a document file to Telegram chat'
    )
    _add_telegram_auth_options(document)
    _add_telegram_document_options(document)

    # Audio action
    audio = actions.add_parser(
        'audio',
        help='Send an audio file to Telegram chat'
    )
    _add_telegram_auth_options(audio)
    _add_telegram_audio_options(audio)

    # Delete action
    delete = actions.add_parser(
        'delete',
        help='Delete a Telegram message'
    )
    _add_telegram_auth_options(delete)
    _add_post_id_option(delete)

    # Set handler
    parser.set_defaults(handler=_handle_telegram_command)

    return parser


def _add_telegram_auth_options(parser: ArgumentParser):
    """
    Add Telegram authentication options.

    Args:
        parser: ArgumentParser to add options to
    """
    auth = parser.add_argument_group(
        'Telegram Authentication',
        'Telegram bot credentials from @BotFather'
    )
    auth.add_argument(
        '--bot-token',
        required=True,
        metavar='<token>',
        help='Telegram bot token from @BotFather'
    )
    auth.add_argument(
        '--chat-id',
        required=True,
        metavar='<id>',
        help='Target chat ID (user, group, or channel)'
    )
    auth.add_argument(
        '--parse-mode',
        choices=['HTML', 'Markdown', 'MarkdownV2', 'None'],
        default='HTML',
        metavar='<mode>',
        help='Message parse mode (default: HTML)'
    )


def _add_telegram_edit_options(parser: ArgumentParser):
    """
    Add edit message options.

    Args:
        parser: ArgumentParser to add options to
    """
    parser.add_argument(
        '--message-id',
        required=True,
        metavar='<id>',
        help='ID of the message to edit'
    )
    parser.add_argument(
        '--text',
        required=True,
        metavar='<text>',
        help='New message text'
    )


def _add_telegram_poll_options(parser: ArgumentParser):
    """
    Add poll creation options.

    Args:
        parser: ArgumentParser to add options to
    """
    poll = parser.add_argument_group('Poll Options')
    poll.add_argument(
        '--question',
        required=True,
        metavar='<question>',
        help='Poll question (up to 300 characters)'
    )
    poll.add_argument(
        '--options',
        required=True,
        metavar='<options>',
        help='Comma-separated list of poll options (2-10 options)'
    )
    poll.add_argument(
        '--anonymous',
        action='store_true',
        default=True,
        help='Make poll anonymous (default: True)'
    )


def _add_telegram_document_options(parser: ArgumentParser):
    """
    Add document sending options.

    Args:
        parser: ArgumentParser to add options to
    """
    parser.add_argument(
        '--document-url',
        required=True,
        metavar='<url>',
        help='URL of document file to send'
    )
    parser.add_argument(
        '--caption',
        metavar='<text>',
        help='Document caption'
    )


def _add_telegram_audio_options(parser: ArgumentParser):
    """
    Add audio sending options.

    Args:
        parser: ArgumentParser to add options to
    """
    parser.add_argument(
        '--audio-url',
        required=True,
        metavar='<url>',
        help='URL of audio file to send'
    )
    parser.add_argument(
        '--caption',
        metavar='<text>',
        help='Audio caption'
    )
    parser.add_argument(
        '--duration',
        type=int,
        metavar='<seconds>',
        help='Audio duration in seconds'
    )
    parser.add_argument(
        '--performer',
        metavar='<name>',
        help='Performer name'
    )
    parser.add_argument(
        '--title',
        metavar='<title>',
        help='Track title'
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
        help='Telegram message ID to delete'
    )


def _handle_telegram_command(args: Namespace):
    """
    Handle Telegram command by converting args and calling core.

    Args:
        args: Parsed command-line arguments

    Returns:
        Exit status from core execution
    """
    # Validate action
    ActionValidator.validate('telegram', args.action)

    # Convert new args to legacy format
    converter = ParameterConverter('telegram')
    legacy_args = converter.convert_to_legacy(args)

    # Call core Telegram module
    return telegram_main(legacy_args)
