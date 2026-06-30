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
Schedule run utility command.

This module provides the schedule-run command for Google Sheets automation.
"""

from argparse import ArgumentParser, Namespace, _SubParsersAction

from ..platform_runner import execute_platform_action
from ..registry import PlatformRegistry


def create_schedule_run_parser(subparsers: _SubParsersAction) -> ArgumentParser:
    """
    Create schedule-run utility command parser.

    Args:
        subparsers: Subparsers action from utils parser

    Returns:
        ArgumentParser for schedule-run command
    """
    parser = subparsers.add_parser("schedule-run", help="Run scheduled posts from Google Sheets")

    parser.add_argument(
        "--network",
        required=True,
        choices=PlatformRegistry.get_platform_names(),
        metavar="<platform>",
        help="Target social network for this run",
    )

    sheets = parser.add_argument_group("Google Sheets Options")
    sheets.add_argument("--sheets-id", required=True, metavar="<id>", help="Google Sheets document ID")
    sheets.add_argument("--sheets-name", required=True, metavar="<name>", help="Sheet name within document")
    sheets.add_argument("--sheets-client-email", required=True, metavar="<email>", help="Google service account email")
    sheets.add_argument(
        "--sheets-private-key", required=True, metavar="<key>", help="Google service account private key"
    )

    _add_whatsapp_recipient_option(parser)

    parser.set_defaults(command=_handle_schedule_run)

    return parser


def _add_whatsapp_recipient_option(parser: ArgumentParser) -> None:
    """Add optional WhatsApp recipient routing (not platform auth)."""
    parser.add_argument(
        "--whatsapp-recipient",
        dest="whatsapp_recipient",
        metavar="<phone>",
        help="WhatsApp recipient phone number when not set in the sheet",
    )


def _handle_schedule_run(args: Namespace):
    """
    Handle schedule run via the shared platform runner.

    Args:
        args: Parsed command-line arguments

    Returns:
        Exit status from core execution
    """
    legacy_args = {
        "action": "schedule",
        "network": args.network,
        "google_sheets_id": args.sheets_id,
        "google_sheets_name": args.sheets_name,
        "google_sheets_client_email": args.sheets_client_email,
        "google_sheets_private_key": args.sheets_private_key,
    }

    if args.whatsapp_recipient is not None:
        legacy_args["whatsapp_recipient"] = args.whatsapp_recipient

    return execute_platform_action(**legacy_args)
