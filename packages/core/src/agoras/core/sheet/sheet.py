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
from typing import Optional

import gspread
from google.oauth2.service_account import Credentials

from .row import SheetRow


class Sheet:
    """
    Google Sheets handler that centralizes sheet operations.

    Provides methods for authentication, reading, writing, and processing
    Google Sheets data with support for various data formats.
    """

    def __init__(self, sheet_id, client_email, private_key, sheet_name=None):
        """
        Initialize sheet instance.

        Args:
            sheet_id (str): Google Sheets document ID
            client_email (str): Service account email
            private_key (str): Service account private key
            sheet_name (str, optional): Specific worksheet name
        """
        self.sheet_id = sheet_id
        self.client_email = client_email
        self.private_key = private_key
        self.sheet_name = sheet_name
        self._client: Optional[gspread.Client] = None
        self._spreadsheet: Optional[gspread.Spreadsheet] = None
        self._worksheet: Optional[gspread.Worksheet] = None
        self._authenticated = False

    async def authenticate(self):
        """
        Authenticate with Google Sheets API asynchronously.

        Returns:
            Sheet: Self for method chaining

        Raises:
            Exception: If authentication fails
        """
        if self._authenticated:
            return self

        def _sync_auth():
            scope = ['https://spreadsheets.google.com/feeds']
            account_info = {
                'private_key': self.private_key,
                'client_email': self.client_email,
                'token_uri': 'https://oauth2.googleapis.com/token',
                'type': 'service_account'
            }

            creds = Credentials.from_service_account_info(account_info, scopes=scope)
            client = gspread.authorize(creds)
            spreadsheet = client.open_by_key(self.sheet_id)

            return client, spreadsheet

        self._client, self._spreadsheet = await asyncio.to_thread(_sync_auth)
        self._authenticated = True

        return self

    async def get_worksheet(self, name=None):
        """
        Get worksheet by name.

        Args:
            name (str, optional): Worksheet name. Uses default if None.

        Returns:
            Sheet: Self for method chaining

        Raises:
            Exception: If worksheet not found
        """
        if not self._authenticated:
            await self.authenticate()

        if not self._spreadsheet:
            raise Exception('Spreadsheet not available after authentication')

        def _sync_get_worksheet():
            assert self._spreadsheet is not None  # Help type checker
            worksheet_name = name or self.sheet_name
            if worksheet_name:
                return self._spreadsheet.worksheet(worksheet_name)
            else:
                # Get first worksheet if no name specified
                return self._spreadsheet.get_worksheet(0)

        self._worksheet = await asyncio.to_thread(_sync_get_worksheet)
        return self

    async def read_all(self, has_headers=True):
        """
        Read all data from the worksheet.

        Args:
            has_headers (bool): Whether first row contains headers

        Returns:
            list: List of SheetRow instances
        """
        if not self._worksheet:
            await self.get_worksheet()

        if not self._worksheet:
            raise Exception('Worksheet not available')

        def _sync_read():
            assert self._worksheet is not None  # Help type checker
            return self._worksheet.get_all_values()

        raw_data = await asyncio.to_thread(_sync_read)

        if not raw_data:
            return []

        headers = raw_data[0] if has_headers else None
        data_rows = raw_data[1:] if has_headers else raw_data

        return [SheetRow(row, headers) for row in data_rows]

    async def read_range(self, range_name):
        """
        Read data from a specific range.

        Args:
            range_name (str): Range in A1 notation (e.g., 'A1:C10')

        Returns:
            list: List of lists containing cell values
        """
        if not self._worksheet:
            await self.get_worksheet()

        if not self._worksheet:
            raise Exception('Worksheet not available')

        def _sync_read():
            assert self._worksheet is not None  # Help type checker
            return self._worksheet.get(range_name)

        return await asyncio.to_thread(_sync_read)

    async def write_all(self, data, clear_first=True, table_range='A1'):
        """
        Write all data to the worksheet.

        Args:
            data (list): List of lists or SheetRow instances
            clear_first (bool): Whether to clear sheet before writing
            table_range (str): Starting range for the table
        """
        if not self._worksheet:
            await self.get_worksheet()

        if not self._worksheet:
            raise Exception('Worksheet not available')

        def _sync_write():
            assert self._worksheet is not None  # Help type checker
            if clear_first:
                self._worksheet.clear()

            # Convert data to list of lists if needed
            rows_data = []
            for row in data:
                if isinstance(row, SheetRow):
                    rows_data.append(row.to_list())
                elif isinstance(row, dict):
                    # Convert dict to list (order may vary)
                    rows_data.append(list(row.values()))
                else:
                    rows_data.append(list(row))

            # Write data in batches for efficiency
            for row_data in rows_data:
                self._worksheet.append_row(row_data, table_range=table_range)

        await asyncio.to_thread(_sync_write)

    async def append_row(self, row_data, table_range='A1'):
        """
        Append a single row to the worksheet.

        Args:
            row_data (list, dict, or SheetRow): Row data to append
            table_range (str): Table range for appending
        """
        if not self._worksheet:
            await self.get_worksheet()

        if not self._worksheet:
            raise Exception('Worksheet not available')

        def _sync_append():
            assert self._worksheet is not None  # Help type checker
            if isinstance(row_data, SheetRow):
                data = row_data.to_list()
            elif isinstance(row_data, dict):
                data = list(row_data.values())
            else:
                data = list(row_data)

            self._worksheet.append_row(data, table_range=table_range)

        await asyncio.to_thread(_sync_append)

    async def update_cell(self, row, col, value):
        """
        Update a single cell.

        Args:
            row (int): Row number (1-indexed)
            col (int): Column number (1-indexed)
            value: Cell value
        """
        if not self._worksheet:
            await self.get_worksheet()

        if not self._worksheet:
            raise Exception('Worksheet not available')

        def _sync_update():
            assert self._worksheet is not None  # Help type checker
            self._worksheet.update_cell(row, col, value)

        await asyncio.to_thread(_sync_update)

    async def update_range(self, range_name, values):
        """
        Update a range of cells.

        Args:
            range_name (str): Range in A1 notation
            values (list): List of lists containing new values
        """
        if not self._worksheet:
            await self.get_worksheet()

        if not self._worksheet:
            raise Exception('Worksheet not available')

        def _sync_update():
            assert self._worksheet is not None  # Help type checker
            self._worksheet.update(range_name, values)

        await asyncio.to_thread(_sync_update)

    async def clear(self):
        """Clear all data from the worksheet."""
        if not self._worksheet:
            await self.get_worksheet()

        if not self._worksheet:
            raise Exception('Worksheet not available')

        def _sync_clear():
            assert self._worksheet is not None  # Help type checker
            self._worksheet.clear()

        await asyncio.to_thread(_sync_clear)

    async def find_rows(self, condition):
        """
        Find rows matching a condition.

        Args:
            condition (callable): Function that takes a SheetRow and returns bool

        Returns:
            list: List of matching SheetRow instances
        """
        all_rows = await self.read_all()
        return [row for row in all_rows if condition(row)]

    async def filter_rows(self, **filters):
        """
        Filter rows by column values.

        Args:
            **filters: Column name to value mappings

        Returns:
            list: List of matching SheetRow instances
        """
        def condition(row):
            for column, value in filters.items():
                if row.get(column) != str(value):
                    return False
            return True

        return await self.find_rows(condition)

    async def get_row_count(self):
        """
        Get the number of rows with data.

        Returns:
            int: Number of rows
        """
        if not self._worksheet:
            await self.get_worksheet()

        if not self._worksheet:
            raise Exception('Worksheet not available')

        def _sync_count():
            assert self._worksheet is not None  # Help type checker
            return len(self._worksheet.get_all_values())

        return await asyncio.to_thread(_sync_count)

    async def get_column_count(self):
        """
        Get the number of columns with data.

        Returns:
            int: Number of columns
        """
        if not self._worksheet:
            await self.get_worksheet()

        if not self._worksheet:
            raise Exception('Worksheet not available')

        def _sync_count():
            assert self._worksheet is not None  # Help type checker
            all_values = self._worksheet.get_all_values()
            return max(len(row) for row in all_values) if all_values else 0

        return await asyncio.to_thread(_sync_count)

    def get_sheet_info(self):
        """
        Get basic sheet information.

        Returns:
            dict: Sheet metadata
        """
        if not self._authenticated:
            raise Exception('Sheet must be authenticated before getting info')

        return {
            'sheet_id': self.sheet_id,
            'title': self._spreadsheet.title if self._spreadsheet else None,
            'worksheet_name': self._worksheet.title if self._worksheet else None,
            'url': self._spreadsheet.url if self._spreadsheet else None
        }
