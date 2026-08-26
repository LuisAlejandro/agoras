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
"""Display shared media constraint tables for ops and E2E."""

import json
import sys
from argparse import ArgumentParser, Namespace, _SubParsersAction

from agoras.media.constraints import (
    IMAGE,
    VIDEO,
    MediaKind,
    constraints_summary,
    format_bytes,
    resolve_platform,
)


def create_media_limits_parser(subparsers: _SubParsersAction) -> ArgumentParser:
    """Register ``agoras utils media-limits``."""
    parser = subparsers.add_parser(
        "media-limits",
        help="Show per-platform media MIME, size, and transfer limits",
    )
    parser.add_argument(
        "--platform",
        metavar="<name>",
        help="Filter to one platform (aliases such as x → twitter)",
    )
    parser.add_argument(
        "--kind",
        choices=["image", "video"],
        help="Show only image or video limits",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit machine-readable JSON",
    )
    parser.set_defaults(command=_handle_media_limits)
    return parser


def _row(platform: str, kind: MediaKind) -> dict:
    limits, mode = constraints_summary(platform, kind)
    return {
        "platform": platform,
        "kind": kind,
        "mime_types": limits.mime_type_list,
        "max_bytes": limits.max_bytes,
        "max_bytes_human": format_bytes(limits.max_bytes),
        "min_duration_s": limits.min_duration_s,
        "max_duration_s": limits.max_duration_s,
        "max_width": limits.max_width,
        "max_height": limits.max_height,
        "transfer": mode,
    }


def _iter_rows(platform_filter=None, kind_filter=None):
    if platform_filter:
        platforms = [resolve_platform(platform_filter)]
    else:
        platforms = sorted(set(IMAGE) | set(VIDEO))

    for platform in platforms:
        if kind_filter in (None, "image") and platform in IMAGE:
            yield _row(platform, "image")
        if kind_filter in (None, "video") and platform in VIDEO:
            yield _row(platform, "video")


def _handle_media_limits(args: Namespace) -> None:
    rows = list(_iter_rows(args.platform, args.kind))
    if args.json:
        print(json.dumps(rows, indent=2))
        return

    for row in rows:
        print(
            f"{row['platform']:12} {row['kind']:5} "
            f"max={row['max_bytes_human']:>6} "
            f"transfer={row['transfer']:12} "
            f"mime={','.join(row['mime_types'])}"
        )


def main(argv=None) -> int:
    """Optional standalone entry point for media-limits output."""
    parser = ArgumentParser(description="Show Agoras media limits")
    parser.add_argument("--platform")
    parser.add_argument("--kind", choices=["image", "video"])
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    try:
        _handle_media_limits(args)
    except Exception as exc:
        print(str(exc), file=sys.stderr)
        return 1
    return 0
