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
"""agoras.media.image module."""

from typing import Optional

from PIL import Image as PILImage

from .base import Media
from .constraints import MediaConstraints, image_limits, resolve_platform
from .errors import MediaValidationError


class Image(Media):
    """
    Image media handler.

    Handles downloading, validation, and processing of image files.
    """

    def __init__(self, url, platform: str = "generic", constraints: Optional[MediaConstraints] = None):
        """Initialize an image media handler for the given URL and platform."""
        super().__init__(url)
        self.platform_key = resolve_platform(platform)
        self.constraints = constraints or image_limits(self.platform_key)
        self.media_kind = "image"

    @property
    def allowed_types(self):
        """Return allowed MIME types for the configured platform."""
        return list(self.constraints.mime_types)

    def get_dimensions(self):
        """
        Get image dimensions using Pillow.

        Returns:
            tuple: (width, height) or None if not available
        """
        if not self._downloaded or not self.content:
            return None
        try:
            with PILImage.open(self.get_file_like_object()) as img:
                return img.size
        except Exception:
            return None

    def _validate_content(self):
        limits = self.constraints
        file_size = self.get_file_size()
        if limits.max_bytes is not None and file_size > limits.max_bytes:
            self.cleanup()
            raise MediaValidationError(self.platform_key, self.media_kind, "max_bytes", file_size, limits.max_bytes)

        dimensions = self.get_dimensions()
        if dimensions:
            width, height = dimensions
            if limits.max_width is not None and width > limits.max_width:
                self.cleanup()
                raise MediaValidationError(
                    self.platform_key,
                    self.media_kind,
                    "max_width",
                    f"{width}x{height}",
                    limits.max_width,
                )
            if limits.max_height is not None and height > limits.max_height:
                self.cleanup()
                raise MediaValidationError(
                    self.platform_key,
                    self.media_kind,
                    "max_height",
                    f"{width}x{height}",
                    limits.max_height,
                )
