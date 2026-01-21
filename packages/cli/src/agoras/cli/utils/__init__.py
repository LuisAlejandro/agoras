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
Utility CLI commands.

This module contains cross-platform utility commands like feed-publish
and schedule-run for automation and orchestration.
"""

from argparse import ArgumentParser, _SubParsersAction

from .feed import create_feed_publish_parser
from .schedule import create_schedule_run_parser
from .tokens import create_tokens_parser


def create_utils_parser(subparsers: _SubParsersAction) -> ArgumentParser:
    """
    Create utils command group for cross-platform tools.

    Args:
        subparsers: Subparsers action from main parser

    Returns:
        ArgumentParser for utils commands
    """
    parser = subparsers.add_parser(
        'utils',
        help='Cross-platform automation and utility commands'
    )

    utils_subparsers = parser.add_subparsers(
        dest='utils_command',
        title='Utility Commands',
        required=True
    )

    # Add subcommands
    create_feed_publish_parser(utils_subparsers)
    create_schedule_run_parser(utils_subparsers)
    create_tokens_parser(utils_subparsers)

    return parser
