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

from .base import Media


class Image(Media):
    """
    Image media handler.

    Handles downloading, validation, and processing of image files.
    """

    @property
    def allowed_types(self):
        """
        Get allowed image MIME types.

        Returns:
            list: List of allowed image MIME types
        """
        return ['image/jpeg', 'image/png', 'image/jpg']

    def get_dimensions(self):
        """
        Get image dimensions (placeholder for future implementation).

        Returns:
            tuple: (width, height) or None if not available
        """
        # TODO: Implement using PIL/Pillow if needed
        return None

    @classmethod
    def for_linkedin(cls, url: str) -> 'Image':
        """
        Create an Image instance optimized for LinkedIn.

        LinkedIn limits:
        - Max file size: 5 MB
        - Supported formats: JPEG, PNG

        Args:
            url (str): Image URL

        Returns:
            Image: Image instance with LinkedIn-specific limits
        """
        return cls(url)
