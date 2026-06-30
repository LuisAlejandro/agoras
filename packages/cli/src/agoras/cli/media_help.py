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
"""CLI help text derived from agoras.media.constraints."""

from agoras.media.constraints import (
    constraints_summary,
    format_bytes,
    resolve_platform,
)


def _mime_short_names(mime_types):
    return ", ".join(sorted({m.split("/")[-1] for m in mime_types}))


def video_url_help(platform: str) -> str:
    """Build --video-url help for a platform."""
    key = resolve_platform(platform)
    limits, mode = constraints_summary(key, "video")
    parts = [
        f"URL of video file (max {format_bytes(limits.max_bytes)}, {_mime_short_names(limits.mime_types)})",
    ]
    if limits.max_duration_s is not None:
        parts.append(f"max {int(limits.max_duration_s)}s")
    if limits.min_duration_s is not None:
        parts.append(f"min {int(limits.min_duration_s)}s")
    text = parts[0]
    if len(parts) > 1:
        text = f"{text}; {', '.join(parts[1:])}"
    if mode == "url_pull":
        text = f"{text}; URL pull"
    return text
