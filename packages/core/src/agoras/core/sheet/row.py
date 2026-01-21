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


class SheetRow:
    """
    Represents a single row from a Google Sheet.

    Provides convenient access to row data with column mapping.
    """

    def __init__(self, data, headers=None):
        """
        Initialize sheet row.

        Args:
            data (list): Row data values
            headers (list, optional): Column headers for named access
        """
        self.data = data or []
        self.headers = headers or []
        self._dict_cache = None

    def __getitem__(self, key):
        """Get item by index or column name."""
        if isinstance(key, int):
            return self.data[key] if key < len(self.data) else ''
        elif isinstance(key, str) and self.headers:
            try:
                index = self.headers.index(key)
                return self.data[index] if index < len(self.data) else ''
            except ValueError:
                return ''
        return ''

    def __setitem__(self, key, value):
        """Set item by index or column name."""
        if isinstance(key, int):
            # Extend data list if necessary
            while key >= len(self.data):
                self.data.append('')
            self.data[key] = value
        elif isinstance(key, str) and self.headers:
            try:
                index = self.headers.index(key)
                while index >= len(self.data):
                    self.data.append('')
                self.data[index] = value
            except ValueError:
                pass
        self._dict_cache = None  # Clear cache

    def __len__(self):
        """Get row length."""
        return len(self.data)

    def get(self, key, default=''):
        """Get value with default."""
        try:
            return self[key]
        except (IndexError, KeyError):
            return default

    def to_dict(self):
        """Convert row to dictionary using headers."""
        if self._dict_cache is None:
            if self.headers:
                self._dict_cache = {}
                for i, header in enumerate(self.headers):
                    self._dict_cache[header] = self.data[i] if i < len(self.data) else ''
            else:
                self._dict_cache = {str(i): value for i, value in enumerate(self.data)}
        return self._dict_cache.copy()

    def to_list(self):
        """Convert row to list."""
        return self.data.copy()
