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

"""
Media module providing media download and processing capabilities.

Contains:
- Media: Abstract base class for media handling
- Image: Handles image media files
- Video: Handles video media files with platform-specific limits
- MediaFactory: Factory for creating and managing media instances
- constraints: Shared per-platform MIME/size/duration limits
"""

from .base import Media
from .constraints import (
    IMAGE,
    TRANSFER,
    VIDEO,
    MediaConstraints,
    constraints_summary,
    format_bytes,
    image_limits,
    platforms_with_post_or_video,
    resolve_platform,
    transfer_mode,
    video_limits,
)
from .errors import MediaValidationError, format_limit_error
from .factory import MediaFactory
from .image import Image
from .preflight import preflight_url, preflight_url_for_platform
from .video import Video

__all__ = [
    'Media',
    'Image',
    'Video',
    'MediaFactory',
    'MediaConstraints',
    'MediaValidationError',
    'IMAGE',
    'VIDEO',
    'TRANSFER',
    'constraints_summary',
    'format_bytes',
    'format_limit_error',
    'image_limits',
    'video_limits',
    'resolve_platform',
    'transfer_mode',
    'platforms_with_post_or_video',
    'preflight_url',
    'preflight_url_for_platform',
]
