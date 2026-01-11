# -*- coding: utf-8 -*-
#
# Please refer to AUTHORS.rst for a complete list of Copyright holders.
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
agoras.common
=============

Common utilities, logging, and shared constants for Agoras.

This package provides low-level utilities used throughout the Agoras ecosystem:
- Version and metadata information
- Logging infrastructure
- URL manipulation utilities
- Web scraping utilities
"""

from .version import (
    __version__,
    __author__,
    __email__,
    __url__,
    __description__
)

from .logger import logger, ControlableLogger
from .utils import add_url_timestamp, parse_metatags

__all__ = [
    '__version__',
    '__author__',
    '__email__',
    '__url__',
    '__description__',
    'logger',
    'ControlableLogger',
    'add_url_timestamp',
    'parse_metatags',
]
