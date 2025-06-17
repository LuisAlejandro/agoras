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
Sheet module providing Google Sheets integration capabilities.

Contains:
- SheetRow: Represents individual rows with column mapping
- Sheet: Main Google Sheets handler with authentication and operations
- SheetManager: Manager for handling multiple sheets and batch operations
- ScheduleSheet: Specialized sheet for social media scheduling
"""

from .row import SheetRow
from .sheet import Sheet
from .manager import SheetManager
from .schedule import ScheduleSheet

__all__ = ['SheetRow', 'Sheet', 'SheetManager', 'ScheduleSheet']
