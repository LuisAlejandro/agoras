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
"""agoras.core.sheet.sheet module."""

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
            scope = ["https://spreadsheets.google.com/feeds"]
            account_info = {
                "private_key": self.private_key,
                "client_email": self.client_email,
                "token_uri": "https://oauth2.googleapis.com/token",
                "type": "service_account",
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
            raise Exception("Spreadsheet not available after authentication")

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
            raise Exception("Worksheet not available")

        def _sync_read():
            assert self._worksheet is not None  # Help type checker
            return self._worksheet.get_all_values()

        raw_data = await asyncio.to_thread(_sync_read)

        if not raw_data:
            return []

        headers = raw_data[0] if has_headers else None
        data_rows = raw_data[1:] if has_headers else raw_data

        return [SheetRow(row, headers) for row in data_rows]

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
            raise Exception("Worksheet not available")

        def _sync_update():
            assert self._worksheet is not None  # Help type checker
            self._worksheet.update_cell(row, col, value)

        await asyncio.to_thread(_sync_update)
