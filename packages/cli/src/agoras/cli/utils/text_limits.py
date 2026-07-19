# -*- coding: utf-8 -*-
#
# Please refer to AUTHORS.rst for a complete list of Copyright holders.
# Copyright (C) 2022-2026, Agoras Developers.

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""Display shared text-limit tables for ops and E2E."""

import json
import sys
from argparse import ArgumentParser, Namespace, _SubParsersAction

from agoras.core.text_limits import TEXT_LIMITS, iter_text_limits


def create_text_limits_parser(subparsers: _SubParsersAction) -> ArgumentParser:
    """Register ``agoras utils text-limits``."""
    parser = subparsers.add_parser(
        "text-limits",
        help="Show per-platform outbound text field limits and counting rules",
    )
    parser.add_argument(
        "--platform",
        metavar="<name>",
        help="Filter to one platform (aliases such as x → twitter)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit machine-readable JSON",
    )
    parser.set_defaults(command=_handle_text_limits)
    return parser


def _row(limit) -> dict:
    return {
        "platform": limit.platform,
        "field": limit.field,
        "limit": limit.limit,
        "counting": limit.counting,
        "mode": limit.mode,
    }


def _handle_text_limits(args: Namespace) -> None:
    if args.platform:
        rows = [_row(item) for item in iter_text_limits(args.platform)]
        if not rows:
            raise ValueError(f"Unknown platform or no text limits: {args.platform}")
    else:
        rows = [_row(item) for item in TEXT_LIMITS]

    if args.json:
        print(json.dumps(rows, indent=2))
        return

    for row in rows:
        mode = row["mode"] or "-"
        print(
            f"{row['platform']:12} {row['field']:18} limit={row['limit']:<6} counting={row['counting']:12} mode={mode}"
        )


def main(argv=None) -> int:
    """Optional standalone entry point for text-limits output."""
    parser = ArgumentParser(description="Show Agoras text limits")
    parser.add_argument("--platform")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    try:
        _handle_text_limits(args)
    except Exception as exc:
        print(str(exc), file=sys.stderr)
        return 1
    return 0
