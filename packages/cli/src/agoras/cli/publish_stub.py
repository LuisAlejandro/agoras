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
"""Stub for the legacy ``agoras publish`` command, removed in 3.0."""

import argparse
import functools
import sys

MIGRATION_POINTER = (
    "Use `agoras <platform> ...` instead - see the migration guide for the mapping: "
    "https://agoras.readthedocs.io/en/latest/migration/"
)

REMOVED_MESSAGE = "`agoras publish` was removed in Agoras 3.0. " + MIGRATION_POINTER


class _RemovedPublishHelp(argparse.Action):
    """Print the removed-message pointer for any help request and exit non-zero."""

    def __call__(self, parser, namespace, values, option_string=None):
        print(REMOVED_MESSAGE, file=sys.stderr)
        parser.exit(1)


def _removed_error(parser, message):
    """Print the pointer for any parse failure and exit non-zero."""
    print(REMOVED_MESSAGE, file=sys.stderr)
    parser.exit(1)


def _absorb_remaining(parser, args=None, namespace=None):
    """Parse, absorbing remaining tokens (including option-like legacy flags)."""
    namespace, argv = argparse.ArgumentParser.parse_known_args(parser, args, namespace)
    if hasattr(namespace, "args"):
        namespace.args = list(namespace.args) + argv
    else:
        namespace.args = argv
    return namespace, []


def _publish_removed(args):
    """Print the removed-message pointer and fail loudly (no traceback)."""
    print(REMOVED_MESSAGE, file=sys.stderr)
    return 1


def create_legacy_publish_stub(subparsers):
    """
    Register the ``publish`` stub subcommand.

    The stub replaces the removed legacy command: every legacy invocation,
    including ``--help`` and any legacy flags, prints the removed-message
    pointer and exits non-zero.

    Args:
        subparsers: Subparsers action from the parent parser

    Returns:
        ArgumentParser for the stub
    """
    parser = subparsers.add_parser(
        "publish",
        help="Removed in Agoras 3.0 - use per-platform commands instead.",
        prog="agoras publish",
        description="Removed in Agoras 3.0 - use per-platform commands instead.",
        add_help=False,
    )
    # Override error handling and arg absorption on the instance via
    # functools.partial (public attribute assignment; parser_class was
    # removed from add_parser in 3.11, and instance attributes are not
    # bound, so partial supplies the parser explicitly).
    parser.error = functools.partial(_removed_error, parser)
    parser.parse_known_args = functools.partial(_absorb_remaining, parser)
    parser.add_argument(
        "-h",
        "--help",
        action=_RemovedPublishHelp,
        nargs=0,
        help="Show this message and exit.",
    )
    parser.add_argument("args", nargs=argparse.REMAINDER, help=argparse.SUPPRESS)
    parser.set_defaults(command=_publish_removed)
    return parser
