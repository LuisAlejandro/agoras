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
"""agoras.media.video module."""

from typing import Optional

import cv2

from .base import Media
from .constraints import MediaConstraints, resolve_platform, video_limits
from .errors import MediaValidationError


class Video(Media):
    """
    Video media handler.

    Handles downloading, validation, and processing of video files.
    Includes size limit validation for platform-specific requirements.
    """

    def __init__(self, url, max_size=None, platform="generic", constraints: Optional[MediaConstraints] = None):
        """Initialize a video media handler for the given URL and platform."""
        super().__init__(url)
        self.platform_key = resolve_platform(platform)
        self.constraints = constraints or video_limits(self.platform_key)
        self.max_size = max_size if max_size is not None else self.constraints.max_bytes
        self.platform = self.platform_key
        self.media_kind = "video"

    @property
    def allowed_types(self):
        """Return allowed MIME types for the configured platform."""
        return list(self.constraints.mime_types)

    def _validate_content(self):
        limits = self.constraints
        file_size = self.get_file_size()
        if self.max_size is not None and file_size > self.max_size:
            self.cleanup()
            raise MediaValidationError(self.platform_key, self.media_kind, "max_bytes", file_size, self.max_size)

        duration = None
        if self._downloaded and self.temp_file:
            duration = self.get_duration()
        if duration is not None:
            if limits.max_duration_s is not None and duration > limits.max_duration_s:
                self.cleanup()
                raise MediaValidationError(
                    self.platform_key,
                    self.media_kind,
                    "max_duration_s",
                    duration,
                    limits.max_duration_s,
                )
            if limits.min_duration_s is not None and duration < limits.min_duration_s:
                self.cleanup()
                raise MediaValidationError(
                    self.platform_key,
                    self.media_kind,
                    "min_duration_s",
                    duration,
                    limits.min_duration_s,
                )

        dimensions = self._get_frame_dimensions()
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

    def get_duration(self):
        """
        Get video duration using OpenCV.

        Returns:
            float: Duration in seconds or None if not available

        Raises:
            Exception: If video file hasn't been downloaded or doesn't exist
        """
        if not self._downloaded or not self.temp_file:
            raise Exception("Video must be downloaded before getting duration")

        try:
            cap = cv2.VideoCapture(self.temp_file)
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_count = cap.get(cv2.CAP_PROP_FRAME_COUNT)
            cap.release()

            if fps > 0:
                return float(frame_count / fps)
            return None
        except Exception:
            return None

    def _get_frame_dimensions(self):
        """Return (width, height) of the first video frame."""
        if not self._downloaded or not self.temp_file:
            return None
        try:
            cap = cv2.VideoCapture(self.temp_file)
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            cap.release()
            if width > 0 and height > 0:
                return width, height
        except Exception:
            pass
        return None
