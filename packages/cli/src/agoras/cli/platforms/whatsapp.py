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
WhatsApp platform CLI parser.

This module provides the WhatsApp command parser for the new CLI structure.
"""

from argparse import ArgumentParser, Namespace, _SubParsersAction

from agoras.platforms.whatsapp.wrapper import main as whatsapp_main
from ..base import add_common_content_options, add_video_options
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
    parser = subparsers.add_parser(
        'whatsapp',
        help='WhatsApp Business API messaging platform operations'
    )

    actions = parser.add_subparsers(
        dest='action',
        title='WhatsApp Actions',
        required=True
    )

    # Post action
    post = actions.add_parser(
        'post',
        help='Send a text/image message via WhatsApp'
    )
    _add_whatsapp_auth_options(post)
    add_common_content_options(post, images=4)

    # Video action
    video = actions.add_parser(
        'video',
        help='Send a video message via WhatsApp'
    )
    _add_whatsapp_auth_options(video)
    add_video_options(video)

    # Contact action
    contact = actions.add_parser(
        'contact',
        help='Send a contact card via WhatsApp'
    )
    _add_whatsapp_auth_options(contact)
    _add_contact_options(contact)

    # Location action
    location = actions.add_parser(
        'location',
        help='Send a location message via WhatsApp'
    )
    _add_whatsapp_auth_options(location)
    _add_location_options(location)

    # Document action
    document = actions.add_parser(
        'document',
        help='Send a document file via WhatsApp'
    )
    _add_whatsapp_auth_options(document)
    _add_document_options(document)

    # Audio action
    audio = actions.add_parser(
        'audio',
        help='Send an audio file via WhatsApp'
    )
    _add_whatsapp_auth_options(audio)
    _add_audio_options(audio)

    # Template action
    template = actions.add_parser(
        'template',
        help='Send a template message via WhatsApp'
    )
    _add_whatsapp_auth_options(template)
    _add_template_options(template)

    # Set handler
    parser.set_defaults(handler=_handle_whatsapp_command)

    return parser


def _add_whatsapp_auth_options(parser: ArgumentParser):
    """
    Add WhatsApp authentication options.

    Args:
        parser: ArgumentParser to add options to
    """
    auth = parser.add_argument_group(
        'WhatsApp Authentication',
        'WhatsApp Business API credentials from Meta Business Manager'
    )
    auth.add_argument(
        '--access-token',
        required=True,
        metavar='<token>',
        help='Meta Graph API access token'
    )
    auth.add_argument(
        '--phone-number-id',
        required=True,
        metavar='<id>',
        help='WhatsApp Business phone number ID'
    )
    auth.add_argument(
        '--business-account-id',
        metavar='<id>',
        help='WhatsApp Business Account ID (optional)'
    )
    auth.add_argument(
        '--recipient',
        required=True,
        metavar='<phone>',
        help='Target recipient phone number (E.164 format, e.g., +1234567890)'
    )


def _add_contact_options(parser: ArgumentParser):
    """
    Add contact-specific options.

    Args:
        parser: ArgumentParser to add options to
    """
    contact = parser.add_argument_group('Contact Options')
    contact.add_argument(
        '--contact-name',
        required=True,
        metavar='<name>',
        help='Name of the contact to send'
    )
    contact.add_argument(
        '--contact-phone',
        required=True,
        metavar='<phone>',
        help='Phone number of the contact (E.164 format, e.g., +1234567890)'
    )


def _add_location_options(parser: ArgumentParser):
    """
    Add location-specific options.

    Args:
        parser: ArgumentParser to add options to
    """
    location = parser.add_argument_group('Location Options')
    location.add_argument(
        '--latitude',
        required=True,
        type=float,
        metavar='<lat>',
        help='Latitude coordinate (-90 to 90)'
    )
    location.add_argument(
        '--longitude',
        required=True,
        type=float,
        metavar='<lon>',
        help='Longitude coordinate (-180 to 180)'
    )
    location.add_argument(
        '--location-name',
        metavar='<name>',
        help='Location name (optional)'
    )


def _add_document_options(parser: ArgumentParser):
    """
    Add document-specific options.

    Args:
        parser: ArgumentParser to add options to
    """
    document = parser.add_argument_group('Document Options')
    document.add_argument(
        '--document-url',
        required=True,
        metavar='<url>',
        help='Publicly accessible HTTPS URL of the document'
    )
    document.add_argument(
        '--caption',
        metavar='<text>',
        help='Document caption (optional)'
    )
    document.add_argument(
        '--filename',
        metavar='<name>',
        help='Document filename (optional)'
    )


def _add_audio_options(parser: ArgumentParser):
    """
    Add audio-specific options.

    Args:
        parser: ArgumentParser to add options to
    """
    audio = parser.add_argument_group('Audio Options')
    audio.add_argument(
        '--audio-url',
        required=True,
        metavar='<url>',
        help='Publicly accessible HTTPS URL of the audio file'
    )


def _add_template_options(parser: ArgumentParser):
    """
    Add template-specific options.

    Args:
        parser: ArgumentParser to add options to
    """
    template = parser.add_argument_group('Template Options')
    template.add_argument(
        '--template-name',
        required=True,
        metavar='<name>',
        help='Name of the pre-approved template'
    )
    template.add_argument(
        '--language-code',
        default='en',
        metavar='<code>',
        help='Language code (ISO 639-1 format, default: en)'
    )
    template.add_argument(
        '--template-components',
        metavar='<json>',
        help='Template components as JSON string (optional)'
    )


def _handle_whatsapp_command(args: Namespace):
    """
    Handle WhatsApp command by converting args and calling core.

    Args:
        args: Parsed command-line arguments

    Returns:
        Exit status from core execution
    """
    # Validate action
    ActionValidator.validate('whatsapp', args.action)

    # Convert new args to legacy format
    converter = ParameterConverter('whatsapp')
    legacy_args = converter.convert_to_legacy(args)

    # Call core WhatsApp module
    return whatsapp_main(legacy_args)
