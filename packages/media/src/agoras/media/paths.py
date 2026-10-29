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
"""Local media path detection and normalization."""

from __future__ import annotations

import os
from typing import Optional
from urllib.parse import unquote, urlparse
from urllib.request import url2pathname


def is_local_media_source(value: str) -> bool:
    """
    Return True when value is a local filesystem path or file:// URI.

    HTTP(s) URLs are not local. Bare paths, relative paths, absolute paths,
    file:// URIs, and Windows drive paths are treated as local.
    """
    if not value or not isinstance(value, str):
        return False

    parsed = urlparse(value)
    if parsed.scheme in ("http", "https"):
        return False
    if parsed.scheme == "file":
        return True
    if value.startswith(("/", "./", "../")):
        return True
    if len(value) >= 2 and value[1] == ":":
        return True
    if not parsed.scheme:
        return True
    return False


def media_is_local(media, url: Optional[str] = None) -> bool:
    """Return True when a media object or URL is a local filesystem source.

    Uses ``is_local_media_source`` on the URL, then a strict ``_is_local is True``
    check so MagicMock defaults are not treated as local.
    """
    source = url if url is not None else getattr(media, "url", None)
    if isinstance(source, str) and is_local_media_source(source):
        return True
    return getattr(media, "_is_local", False) is True


def normalize_media_path(value: str, base_dir: Optional[str] = None) -> str:
    """
    Normalize a media source to an absolute local path or return remote URLs unchanged.

    Args:
        value: HTTP(s) URL, file:// URI, or filesystem path.
        base_dir: Directory used to resolve relative paths.

    Returns:
        Absolute local path for local sources; original value for HTTP(s) URLs.
    """
    parsed = urlparse(value)
    if parsed.scheme in ("http", "https"):
        return value

    if parsed.scheme == "file":
        local_path = url2pathname(unquote(parsed.path))
    else:
        local_path = value

    local_path = os.path.expanduser(local_path)
    if base_dir and not os.path.isabs(local_path):
        local_path = os.path.join(base_dir, local_path)
    return os.path.abspath(local_path)
