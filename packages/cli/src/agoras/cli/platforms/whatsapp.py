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
WhatsApp platform CLI parser.

This module provides the WhatsApp command parser for the new CLI structure.
"""

from argparse import SUPPRESS, ArgumentParser, Namespace, _SubParsersAction

from agoras.platforms.whatsapp.wrapper import main as whatsapp_main

from ..base import add_common_content_options, add_video_options, prepare_content_args
from ..content import add_content_file_option
from ..converter import ParameterConverter
from ..validator import ActionValidator


def create_whatsapp_parser(subparsers: _SubParsersAction) -> ArgumentParser:
    """
    Create WhatsApp platform subcommand parser.

    Args:
        subparsers: Subparsers action from parent parser

    Returns:
        ArgumentParser for WhatsApp commands
    """
    parser = subparsers.add_parser("whatsapp", help="WhatsApp Business API messaging platform operations")

    actions = parser.add_subparsers(dest="action", title="WhatsApp Actions", required=True)

    # Authorize action
    authorize = actions.add_parser("authorize", help="Set up WhatsApp Business API credentials")
    _add_whatsapp_authorize_options(authorize)

    # Post action
    post = actions.add_parser(
        "post",
        help='Send a text/image message via WhatsApp. Requires prior authorization via "agoras whatsapp authorize".',
    )
    _add_whatsapp_recipient_option(post)
    add_common_content_options(post, images=4)

    # Video action
    video = actions.add_parser(
        "video", help='Send a video message via WhatsApp. Requires prior authorization via "agoras whatsapp authorize".'
    )
    _add_whatsapp_recipient_option(video)
    add_video_options(video, platform="whatsapp")

    # Template action
    template = actions.add_parser(
        "template",
        help='Send a template message via WhatsApp. Requires prior authorization via "agoras whatsapp authorize".',
    )
    _add_whatsapp_recipient_option(template)
    _add_template_options(template)

    # Reply action
    reply = actions.add_parser(
        "reply", help='Reply to a WhatsApp message. Requires prior authorization via "agoras whatsapp authorize".'
    )
    _add_whatsapp_recipient_option(reply)
    _add_post_id_option(reply)
    add_common_content_options(reply, images=4)
    add_video_options(reply, platform="whatsapp", with_content_file=False)

    # Get-post action
    get_post = actions.add_parser(
        "get-post",
        help='Read a WhatsApp message (not supported). Requires prior authorization via "agoras whatsapp authorize".',
    )
    get_post.add_argument("--post-id", required=True, metavar="<id>", help="WhatsApp message ID to read")

    # Get-reply action
    get_reply = actions.add_parser(
        "get-reply",
        help='Read a WhatsApp reply (not supported). Requires prior authorization via "agoras whatsapp authorize".',
    )
    get_reply.add_argument("--post-id", required=True, metavar="<id>", help="WhatsApp reply ID to read")

    # List-posts action
    list_posts = actions.add_parser(
        "list-posts",
        help=(
            "List recent WhatsApp messages (not supported). Requires prior "
            'authorization via "agoras whatsapp authorize".'
        ),
    )
    _add_limit_option(list_posts)

    # Set handler
    parser.set_defaults(command=_handle_whatsapp_command)

    return parser


def _add_whatsapp_authorize_options(parser: ArgumentParser):
    """
    Add WhatsApp authorization options (for authorize action).

    Args:
        parser: ArgumentParser to add options to
    """
    auth = parser.add_argument_group(
        "WhatsApp Authentication", "WhatsApp Business API credentials from Meta Business Manager"
    )
    auth.add_argument("--access-token", required=True, metavar="<token>", help="Meta Graph API access token")
    auth.add_argument("--phone-number-id", required=True, metavar="<id>", help="WhatsApp Business phone number ID")
    auth.add_argument("--business-account-id", metavar="<id>", help="WhatsApp Business Account ID (optional)")


def _add_whatsapp_recipient_option(parser: ArgumentParser):
    """
    Add WhatsApp recipient option for action commands.

    Args:
        parser: ArgumentParser to add options to
    """
    parser.add_argument(
        "--recipient",
        required=True,
        metavar="<phone>",
        help="Target recipient phone number (E.164 format, e.g., +1234567890)",
    )


def _add_template_options(parser: ArgumentParser):
    """
    Add template-specific options.

    ``--template-name`` is not argparse-required so --content can supply it;
    the content contract enforces requiredness. ``--recipient`` stays required
    as a control flag.

    Args:
        parser: ArgumentParser to add options to
    """
    add_content_file_option(parser)

    template = parser.add_argument_group("Template Options")
    template.add_argument(
        "--template-name", default=SUPPRESS, metavar="<name>", help="Name of the pre-approved template"
    )
    template.add_argument(
        "--language-code",
        default=SUPPRESS,
        metavar="<code>",
        help="Language code (ISO 639-1 format, default: en)",
    )
    template.add_argument(
        "--template-components",
        default=SUPPRESS,
        metavar="<json>",
        help="Template components as JSON string (optional)",
    )


def _add_post_id_option(parser: ArgumentParser):
    """
    Add post ID option for reply action.

    Args:
        parser: ArgumentParser to add options to
    """
    parser.add_argument("--post-id", required=True, metavar="<id>", help="WhatsApp message ID to reply to")


def _add_limit_option(parser: ArgumentParser):
    """
    Add limit option for list-posts action.

    Args:
        parser: ArgumentParser to add options to
    """
    parser.add_argument("--limit", type=int, metavar="<n>", help="Maximum number of posts to list")


def _handle_whatsapp_command(args: Namespace):
    """
    Handle WhatsApp command by converting args and calling core.

    Args:
        args: Parsed command-line arguments

    Returns:
        Exit status from core execution
    """
    # Validate action
    ActionValidator.validate("whatsapp", args.action)
    prepare_content_args(args, "whatsapp")

    # Convert new args to legacy format
    converter = ParameterConverter("whatsapp")
    legacy_args = converter.convert_to_legacy(args)

    # Call core WhatsApp module
    return whatsapp_main(legacy_args)
