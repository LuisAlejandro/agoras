# -*- coding: utf-8 -*-
#
# Please refer to AUTHORS.md for a complete list of Copyright holders.
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
"""agoras.media.errors module."""

from typing import Any, Optional


class MediaValidationError(Exception):
    """Raised when media fails platform constraint checks."""

    def __init__(self, platform: str, kind: str, field: str, actual: Any, limit: Any, message: Optional[str] = None):
        """Initialize a media validation error with platform limit details."""
        self.platform = platform
        self.kind = kind
        self.field = field
        self.actual = actual
        self.limit = limit
        super().__init__(message or format_limit_error(platform, kind, field, actual, limit))


def format_limit_error(platform: str, kind: str, field: str, actual: Any, limit: Any) -> str:
    """Build a consistent validation error message."""
    if field == "mime_types":
        return f'Invalid {kind} type "{actual}" for {platform}. Allowed types: {sorted(limit)}'
    if field == "max_bytes":
        return f"{kind.capitalize()} file size ({actual} bytes) exceeds {platform} limit of {limit} bytes"
    if field == "max_duration_s":
        return f"{kind.capitalize()} duration ({actual}s) exceeds {platform} limit of {limit}s"
    if field == "min_duration_s":
        return f"{kind.capitalize()} duration ({actual}s) is below {platform} minimum of {limit}s"
    if field in ("max_width", "max_height"):
        return f"{kind.capitalize()} dimensions ({actual}) exceed {platform} {field} limit of {limit}"
    if field == "content_type":
        return f'URL content type "{actual}" is not allowed for {platform} {kind}. Allowed types: {sorted(limit)}'
    if field == "content_length":
        return f"URL content length ({actual} bytes) exceeds {platform} {kind} limit of {limit} bytes"
    return f"{platform} {kind} validation failed for {field}: actual={actual!r}, limit={limit!r}"
