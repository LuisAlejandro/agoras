# -*- coding: utf-8 -*-
#
# Please refer to AUTHORS.md for a complete list of Copyright holders.
# Copyright (C) 2022-2023, Agoras Developers.

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
"""

from .base import Media
from .image import Image
from .video import Video
from .factory import MediaFactory

__all__ = ['Media', 'Image', 'Video', 'MediaFactory'] 