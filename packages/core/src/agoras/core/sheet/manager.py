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

import asyncio

from .sheet import Sheet


class SheetManager:
    """
    Manager class for handling multiple sheets and batch operations.
    """

    def __init__(self):
        """Initialize sheet manager."""
        self.sheets = {}

    async def add_sheet(self, name, sheet_id, client_email, private_key, sheet_name=None):
        """
        Add a sheet to the manager.

        Args:
            name (str): Sheet identifier
            sheet_id (str): Google Sheets document ID
            client_email (str): Service account email
            private_key (str): Service account private key
            sheet_name (str, optional): Worksheet name

        Returns:
            Sheet: Sheet instance
        """
        sheet = Sheet(sheet_id, client_email, private_key, sheet_name)
        await sheet.authenticate()
        self.sheets[name] = sheet
        return sheet

    def get_sheet(self, name):
        """
        Get sheet by name.

        Args:
            name (str): Sheet identifier

        Returns:
            Sheet: Sheet instance or None if not found
        """
        return self.sheets.get(name)

    async def read_all_sheets(self):
        """
        Read data from all sheets concurrently.

        Returns:
            dict: Dictionary of sheet names to data
        """
        read_tasks = []
        sheet_names = []

        for name, sheet in self.sheets.items():
            read_tasks.append(sheet.read_all())
            sheet_names.append(name)

        results = await asyncio.gather(*read_tasks, return_exceptions=True)
        return dict(zip(sheet_names, results))

    async def write_to_multiple_sheets(self, data_map):
        """
        Write data to multiple sheets concurrently.

        Args:
            data_map (dict): Dictionary of sheet names to data
        """
        write_tasks = []

        for name, data in data_map.items():
            if name in self.sheets:
                write_tasks.append(self.sheets[name].write_all(data))

        await asyncio.gather(*write_tasks, return_exceptions=True)
