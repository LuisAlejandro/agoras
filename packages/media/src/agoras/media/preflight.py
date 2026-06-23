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

from typing import Optional
from urllib.request import Request, urlopen

from .constraints import MediaConstraints, resolve_platform
from .errors import MediaValidationError


def preflight_url(url: str, limits: MediaConstraints, *,
                  platform: str = 'generic', kind: str = 'image') -> None:
    """
    Validate remote media via HEAD before url_pull uploads.

    Args:
        url: Public HTTPS media URL
        limits: Platform constraints to check against
        platform: Canonical platform name for errors
        kind: 'image' or 'video'

    Raises:
        MediaValidationError: If Content-Type or Content-Length violate limits
        Exception: If HEAD request fails
    """
    platform_key = resolve_platform(platform)
    request = Request(url, method='HEAD', headers={'User-Agent': 'Agoras/preflight'})
    with urlopen(request, timeout=30) as response:
        content_type = response.headers.get('Content-Type', '').split(';')[0].strip().lower()
        content_length = response.headers.get('Content-Length')

    if content_type and limits.mime_types:
        if content_type not in limits.mime_types:
            raise MediaValidationError(
                platform_key, kind, 'content_type', content_type, limits.mime_type_list
            )

    if content_length and limits.max_bytes is not None:
        size = int(content_length)
        if size > limits.max_bytes:
            raise MediaValidationError(
                platform_key, kind, 'content_length', size, limits.max_bytes
            )


def preflight_url_for_platform(url: str, platform: str, kind: str = 'image',
                               limits: Optional[MediaConstraints] = None) -> None:
    """Convenience wrapper using platform image/video limits."""
    from .constraints import image_limits, video_limits

    platform_key = resolve_platform(platform)
    if limits is None:
        limits = image_limits(platform_key) if kind == 'image' else video_limits(platform_key)
    preflight_url(url, limits, platform=platform_key, kind=kind)
