# -*- coding: utf-8 -*-
#
# Please refer to AUTHORS.rst for a complete list of Copyright holders.
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

import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from agoras.core.sheet import ScheduleSheet, Sheet, SheetManager, SheetRow

# SheetRow Tests


def test_sheetrow_instantiation():
    """Test SheetRow can be instantiated."""
    row = SheetRow(['val1', 'val2', 'val3'], ['col1', 'col2', 'col3'])
    assert row.data == ['val1', 'val2', 'val3']
    assert row.headers == ['col1', 'col2', 'col3']


def test_sheetrow_getitem_by_index():
    """Test SheetRow access by integer index."""
    row = SheetRow(['a', 'b', 'c'])

    assert row[0] == 'a'
    assert row[1] == 'b'
    assert row[2] == 'c'


def test_sheetrow_getitem_by_index_out_of_bounds():
    """Test SheetRow access out of bounds returns empty string."""
    row = SheetRow(['a', 'b'])

    assert row[10] == ''


def test_sheetrow_getitem_by_column_name():
    """Test SheetRow access by column name with headers."""
    row = SheetRow(['val1', 'val2', 'val3'], ['name', 'email', 'age'])

    assert row['name'] == 'val1'
    assert row['email'] == 'val2'
    assert row['age'] == 'val3'


def test_sheetrow_getitem_by_column_name_not_found():
    """Test SheetRow access non-existent column returns empty."""
    row = SheetRow(['val1', 'val2'], ['col1', 'col2'])

    assert row['nonexistent'] == ''


def test_sheetrow_getitem_by_column_name_without_headers():
    """Test SheetRow access by column name without headers returns empty."""
    row = SheetRow(['val1', 'val2'])

    assert row['col1'] == ''


def test_sheetrow_setitem_by_index():
    """Test SheetRow set by integer index."""
    row = SheetRow(['a', 'b', 'c'])

    row[1] = 'updated'

    assert row[1] == 'updated'


def test_sheetrow_setitem_by_index_extends():
    """Test SheetRow set beyond length auto-extends list."""
    row = SheetRow(['a', 'b'])

    row[5] = 'new'

    assert row[5] == 'new'
    assert len(row.data) == 6


def test_sheetrow_setitem_by_column_name():
    """Test SheetRow set by column name with headers."""
    row = SheetRow(['val1', 'val2'], ['col1', 'col2'])

    row['col1'] = 'updated'

    assert row['col1'] == 'updated'


def test_sheetrow_setitem_by_column_name_extends():
    """Test SheetRow set by column beyond length auto-extends."""
    row = SheetRow(['val1'], ['col1', 'col2', 'col3'])

    row['col3'] = 'new'

    assert row['col3'] == 'new'
    assert len(row.data) >= 3


def test_sheetrow_setitem_clears_cache():
    """Test SheetRow setitem clears dict cache."""
    row = SheetRow(['a', 'b'], ['col1', 'col2'])

    # Access to_dict to create cache
    _ = row.to_dict()
    assert row._dict_cache is not None

    # Setting should clear cache
    row[0] = 'updated'

    assert row._dict_cache is None


def test_sheetrow_len():
    """Test SheetRow len returns data length."""
    row = SheetRow(['a', 'b', 'c'])

    assert len(row) == 3


def test_sheetrow_get_with_valid_key():
    """Test SheetRow get with valid key."""
    row = SheetRow(['val1', 'val2'], ['col1', 'col2'])

    assert row.get('col1') == 'val1'
    assert row.get(0) == 'val1'


def test_sheetrow_get_with_invalid_key_returns_default():
    """Test SheetRow get with invalid key returns default."""
    row = SheetRow(['val1'], ['col1'])

    # get() wraps __getitem__ which returns '' for missing keys
    assert row.get('nonexistent') == ''
    # The get method doesn't actually use the default parameter properly
    # It catches exceptions but __getitem__ returns '' not raising exception
    assert row.get(10) == ''


def test_sheetrow_to_dict_with_headers():
    """Test SheetRow to_dict with headers."""
    row = SheetRow(['val1', 'val2', 'val3'], ['col1', 'col2', 'col3'])

    result = row.to_dict()

    assert result == {'col1': 'val1', 'col2': 'val2', 'col3': 'val3'}


def test_sheetrow_to_dict_without_headers():
    """Test SheetRow to_dict without headers uses indices."""
    row = SheetRow(['val1', 'val2', 'val3'])

    result = row.to_dict()

    assert result == {'0': 'val1', '1': 'val2', '2': 'val3'}


def test_sheetrow_to_dict_caching():
    """Test SheetRow to_dict uses cache on subsequent calls."""
    row = SheetRow(['val1', 'val2'], ['col1', 'col2'])

    result1 = row.to_dict()
    result2 = row.to_dict()

    # Should return different objects (copy)
    assert result1 is not result2
    # But with same content
    assert result1 == result2


def test_sheetrow_to_list():
    """Test SheetRow to_list returns copy."""
    row = SheetRow(['val1', 'val2', 'val3'])

    result = row.to_list()

    assert result == ['val1', 'val2', 'val3']
    # Should be a copy, not same list
    assert result is not row.data


# Sheet Class Tests

def test_sheet_instantiation():
    """Test Sheet can be instantiated."""
    sheet = Sheet(
        sheet_id='test_id',
        client_email='test@example.com',
        private_key='test_key'
    )
    assert sheet is not None
    assert sheet.sheet_id == 'test_id'
    assert sheet._authenticated is False


def test_sheet_has_required_methods():
    """Test Sheet has required methods."""
    assert hasattr(Sheet, 'authenticate')
    assert hasattr(Sheet, 'get_worksheet')


@pytest.mark.asyncio
@patch('agoras.core.sheet.sheet.gspread.authorize')
@patch('agoras.core.sheet.sheet.Credentials.from_service_account_info')
async def test_sheet_authenticate(mock_creds, mock_authorize):
    """Test Sheet authentication."""
    mock_client = MagicMock()
    mock_spreadsheet = MagicMock()
    mock_client.open_by_key.return_value = mock_spreadsheet
    mock_authorize.return_value = mock_client

    sheet = Sheet('sheet-id', 'email@example.com', 'private-key')
    result = await sheet.authenticate()

    assert sheet._authenticated is True
    assert sheet._client is mock_client
    assert sheet._spreadsheet is mock_spreadsheet
    assert result is sheet


@pytest.mark.asyncio
@patch('agoras.core.sheet.sheet.gspread.authorize')
@patch('agoras.core.sheet.sheet.Credentials.from_service_account_info')
async def test_sheet_authenticate_caching(mock_creds, mock_authorize):
    """Test Sheet authentication caching."""
    mock_client = MagicMock()
    mock_spreadsheet = MagicMock()
    mock_client.open_by_key.return_value = mock_spreadsheet
    mock_authorize.return_value = mock_client

    sheet = Sheet('sheet-id', 'email@example.com', 'key')

    await sheet.authenticate()
    first_call_count = mock_authorize.call_count

    await sheet.authenticate()

    # Should not call authorize again
    assert mock_authorize.call_count == first_call_count


@pytest.mark.asyncio
@patch('agoras.core.sheet.sheet.gspread.authorize')
@patch('agoras.core.sheet.sheet.Credentials.from_service_account_info')
async def test_sheet_get_worksheet_by_name(mock_creds, mock_authorize):
    """Test Sheet get_worksheet by name."""
    mock_client = MagicMock()
    mock_spreadsheet = MagicMock()
    mock_worksheet = MagicMock()
    mock_spreadsheet.worksheet.return_value = mock_worksheet
    mock_client.open_by_key.return_value = mock_spreadsheet
    mock_authorize.return_value = mock_client

    sheet = Sheet('sheet-id', 'email@example.com', 'key', sheet_name='MySheet')
    await sheet.authenticate()

    result = await sheet.get_worksheet('CustomSheet')

    mock_spreadsheet.worksheet.assert_called_once_with('CustomSheet')
    assert sheet._worksheet is mock_worksheet
    assert result is sheet


@pytest.mark.asyncio
@patch('agoras.core.sheet.sheet.gspread.authorize')
@patch('agoras.core.sheet.sheet.Credentials.from_service_account_info')
async def test_sheet_get_worksheet_uses_default_name(mock_creds, mock_authorize):
    """Test Sheet get_worksheet uses default sheet_name."""
    mock_client = MagicMock()
    mock_spreadsheet = MagicMock()
    mock_worksheet = MagicMock()
    mock_spreadsheet.worksheet.return_value = mock_worksheet
    mock_client.open_by_key.return_value = mock_spreadsheet
    mock_authorize.return_value = mock_client

    sheet = Sheet('sheet-id', 'email@example.com', 'key', sheet_name='DefaultSheet')
    await sheet.authenticate()

    await sheet.get_worksheet()

    mock_spreadsheet.worksheet.assert_called_once_with('DefaultSheet')


@pytest.mark.asyncio
@patch('agoras.core.sheet.sheet.gspread.authorize')
@patch('agoras.core.sheet.sheet.Credentials.from_service_account_info')
async def test_sheet_get_worksheet_first_sheet_when_no_name(mock_creds, mock_authorize):
    """Test Sheet get_worksheet gets first sheet when no name."""
    mock_client = MagicMock()
    mock_spreadsheet = MagicMock()
    mock_worksheet = MagicMock()
    mock_spreadsheet.get_worksheet.return_value = mock_worksheet
    mock_client.open_by_key.return_value = mock_spreadsheet
    mock_authorize.return_value = mock_client

    sheet = Sheet('sheet-id', 'email@example.com', 'key')  # No sheet_name
    await sheet.authenticate()

    await sheet.get_worksheet()

    mock_spreadsheet.get_worksheet.assert_called_once_with(0)


@pytest.mark.asyncio
@patch('agoras.core.sheet.sheet.gspread.authorize')
@patch('agoras.core.sheet.sheet.Credentials.from_service_account_info')
async def test_sheet_get_worksheet_auto_authenticates(mock_creds, mock_authorize):
    """Test Sheet get_worksheet auto-authenticates if needed."""
    mock_client = MagicMock()
    mock_spreadsheet = MagicMock()
    mock_worksheet = MagicMock()
    mock_spreadsheet.get_worksheet.return_value = mock_worksheet
    mock_client.open_by_key.return_value = mock_spreadsheet
    mock_authorize.return_value = mock_client

    sheet = Sheet('sheet-id', 'email@example.com', 'key')

    # Not authenticated yet
    assert sheet._authenticated is False

    await sheet.get_worksheet()

    # Should auto-authenticate
    assert sheet._authenticated is True


@pytest.mark.asyncio
@patch('agoras.core.sheet.sheet.gspread.authorize')
@patch('agoras.core.sheet.sheet.Credentials.from_service_account_info')
async def test_sheet_read_all_with_headers(mock_creds, mock_authorize):
    """Test Sheet read_all with headers."""
    mock_client = MagicMock()
    mock_spreadsheet = MagicMock()
    mock_worksheet = MagicMock()
    mock_worksheet.get_all_values.return_value = [
        ['Name', 'Email', 'Age'],
        ['John', 'john@example.com', '30'],
        ['Jane', 'jane@example.com', '25']
    ]
    mock_spreadsheet.get_worksheet.return_value = mock_worksheet
    mock_client.open_by_key.return_value = mock_spreadsheet
    mock_authorize.return_value = mock_client

    sheet = Sheet('sheet-id', 'email@example.com', 'key')
    await sheet.authenticate()
    await sheet.get_worksheet()

    rows = await sheet.read_all(has_headers=True)

    assert len(rows) == 2
    assert isinstance(rows[0], SheetRow)
    assert rows[0]['Name'] == 'John'
    assert rows[0]['Email'] == 'john@example.com'


@pytest.mark.asyncio
@patch('agoras.core.sheet.sheet.gspread.authorize')
@patch('agoras.core.sheet.sheet.Credentials.from_service_account_info')
async def test_sheet_read_all_without_headers(mock_creds, mock_authorize):
    """Test Sheet read_all without headers."""
    mock_client = MagicMock()
    mock_spreadsheet = MagicMock()
    mock_worksheet = MagicMock()
    mock_worksheet.get_all_values.return_value = [
        ['data1', 'data2'],
        ['data3', 'data4']
    ]
    mock_spreadsheet.get_worksheet.return_value = mock_worksheet
    mock_client.open_by_key.return_value = mock_spreadsheet
    mock_authorize.return_value = mock_client

    sheet = Sheet('sheet-id', 'email@example.com', 'key')
    await sheet.authenticate()
    await sheet.get_worksheet()

    rows = await sheet.read_all(has_headers=False)

    assert len(rows) == 2
    assert rows[0].headers == []


@pytest.mark.asyncio
@patch('agoras.core.sheet.sheet.gspread.authorize')
@patch('agoras.core.sheet.sheet.Credentials.from_service_account_info')
async def test_sheet_read_all_auto_gets_worksheet(mock_creds, mock_authorize):
    """Test Sheet read_all auto-gets worksheet if needed."""
    mock_client = MagicMock()
    mock_spreadsheet = MagicMock()
    mock_worksheet = MagicMock()
    mock_worksheet.get_all_values.return_value = []
    mock_spreadsheet.get_worksheet.return_value = mock_worksheet
    mock_client.open_by_key.return_value = mock_spreadsheet
    mock_authorize.return_value = mock_client

    sheet = Sheet('sheet-id', 'email@example.com', 'key')
    await sheet.authenticate()

    # Worksheet not set yet
    assert sheet._worksheet is None

    await sheet.read_all()

    # Should auto-get worksheet
    assert sheet._worksheet is not None


@pytest.mark.asyncio
@patch('agoras.core.sheet.sheet.gspread.authorize')
@patch('agoras.core.sheet.sheet.Credentials.from_service_account_info')
async def test_sheet_read_range(mock_creds, mock_authorize):
    """Test Sheet read_range."""
    mock_client = MagicMock()
    mock_spreadsheet = MagicMock()
    mock_worksheet = MagicMock()
    mock_worksheet.get.return_value = [['A1', 'B1'], ['A2', 'B2']]
    mock_spreadsheet.get_worksheet.return_value = mock_worksheet
    mock_client.open_by_key.return_value = mock_spreadsheet
    mock_authorize.return_value = mock_client

    sheet = Sheet('sheet-id', 'email@example.com', 'key')
    await sheet.authenticate()
    await sheet.get_worksheet()

    data = await sheet.read_range('A1:B2')

    assert len(data) == 2
    mock_worksheet.get.assert_called_once_with('A1:B2')


@pytest.mark.asyncio
@patch('agoras.core.sheet.sheet.gspread.authorize')
@patch('agoras.core.sheet.sheet.Credentials.from_service_account_info')
async def test_sheet_write_all_with_clear(mock_creds, mock_authorize):
    """Test Sheet write_all with clear_first=True."""
    mock_client = MagicMock()
    mock_spreadsheet = MagicMock()
    mock_worksheet = MagicMock()
    mock_spreadsheet.get_worksheet.return_value = mock_worksheet
    mock_client.open_by_key.return_value = mock_spreadsheet
    mock_authorize.return_value = mock_client

    sheet = Sheet('sheet-id', 'email@example.com', 'key')
    await sheet.authenticate()
    await sheet.get_worksheet()

    data = [['a', 'b'], ['c', 'd']]
    await sheet.write_all(data, clear_first=True)

    mock_worksheet.clear.assert_called_once()
    # write_all uses append_row, not update
    assert mock_worksheet.append_row.call_count == 2


@pytest.mark.asyncio
@patch('agoras.core.sheet.sheet.gspread.authorize')
@patch('agoras.core.sheet.sheet.Credentials.from_service_account_info')
async def test_sheet_write_all_with_sheetrow(mock_creds, mock_authorize):
    """Test Sheet write_all with SheetRow instances."""
    mock_client = MagicMock()
    mock_spreadsheet = MagicMock()
    mock_worksheet = MagicMock()
    mock_spreadsheet.get_worksheet.return_value = mock_worksheet
    mock_client.open_by_key.return_value = mock_spreadsheet
    mock_authorize.return_value = mock_client

    sheet = Sheet('sheet-id', 'email@example.com', 'key')
    await sheet.authenticate()
    await sheet.get_worksheet()

    rows = [SheetRow(['a', 'b']), SheetRow(['c', 'd'])]
    await sheet.write_all(rows, clear_first=False)

    # Should convert SheetRow to list and append
    assert mock_worksheet.append_row.call_count == 2


@pytest.mark.asyncio
@patch('agoras.core.sheet.sheet.gspread.authorize')
@patch('agoras.core.sheet.sheet.Credentials.from_service_account_info')
async def test_sheet_append_row(mock_creds, mock_authorize):
    """Test Sheet append_row method."""
    mock_client = MagicMock()
    mock_spreadsheet = MagicMock()
    mock_worksheet = MagicMock()
    mock_spreadsheet.get_worksheet.return_value = mock_worksheet
    mock_client.open_by_key.return_value = mock_spreadsheet
    mock_authorize.return_value = mock_client

    sheet = Sheet('sheet-id', 'email@example.com', 'key')
    await sheet.authenticate()
    await sheet.get_worksheet()

    await sheet.append_row(['new', 'data'])

    mock_worksheet.append_row.assert_called_once()


@pytest.mark.asyncio
@patch('agoras.core.sheet.sheet.gspread.authorize')
@patch('agoras.core.sheet.sheet.Credentials.from_service_account_info')
async def test_sheet_update_cell(mock_creds, mock_authorize):
    """Test Sheet update_cell method."""
    mock_client = MagicMock()
    mock_spreadsheet = MagicMock()
    mock_worksheet = MagicMock()
    mock_spreadsheet.get_worksheet.return_value = mock_worksheet
    mock_client.open_by_key.return_value = mock_spreadsheet
    mock_authorize.return_value = mock_client

    sheet = Sheet('sheet-id', 'email@example.com', 'key')
    await sheet.authenticate()
    await sheet.get_worksheet()

    await sheet.update_cell(1, 1, 'new value')

    mock_worksheet.update_cell.assert_called_once_with(1, 1, 'new value')


@pytest.mark.asyncio
@patch('agoras.core.sheet.sheet.gspread.authorize')
@patch('agoras.core.sheet.sheet.Credentials.from_service_account_info')
async def test_sheet_write_row(mock_creds, mock_authorize):
    """Test Sheet update_range method for writing a row."""
    mock_client = MagicMock()
    mock_spreadsheet = MagicMock()
    mock_worksheet = MagicMock()
    mock_spreadsheet.get_worksheet.return_value = mock_worksheet
    mock_client.open_by_key.return_value = mock_spreadsheet
    mock_authorize.return_value = mock_client

    sheet = Sheet('sheet-id', 'email@example.com', 'key')
    await sheet.authenticate()
    await sheet.get_worksheet()

    await sheet.update_range('A5:B5', [['row', 'data']])

    mock_worksheet.update.assert_called_once_with('A5:B5', [['row', 'data']])


# ScheduleSheet Tests

def test_schedulesheet_instantiation():
    """Test ScheduleSheet can be instantiated."""
    sheet = ScheduleSheet(
        sheet_id='test_id',
        client_email='test@example.com',
        private_key='test_key',
        sheet_name='test_sheet'
    )
    assert sheet is not None


def test_schedulesheet_has_required_methods():
    """Test ScheduleSheet has required methods."""
    assert hasattr(ScheduleSheet, 'authenticate')
    assert hasattr(ScheduleSheet, 'get_worksheet')
    assert hasattr(ScheduleSheet, 'process_scheduled_posts')


@pytest.mark.asyncio
@patch('agoras.core.sheet.schedule.datetime')
async def test_schedulesheet_process_posts_due_now(mock_datetime):
    """Test ScheduleSheet processes posts due now."""
    # Mock current time
    mock_now = datetime.datetime(2024, 1, 15, 14, 0, 0)
    mock_datetime.datetime.now.return_value = mock_now

    # Create mock row data for a post due now
    row_data = SheetRow([
        'Post text', 'http://link.com', 'img1.jpg', '', '', '',
        '15-01-2024', '14', ''  # Today at 14:00, not published
    ])

    sheet = ScheduleSheet('sheet-id', 'email@example.com', 'key')

    with patch.object(sheet, 'read_all', new_callable=AsyncMock) as mock_read:
        with patch.object(sheet, 'write_all', new_callable=AsyncMock) as mock_write:
            mock_read.return_value = [row_data]

            posts = await sheet.process_scheduled_posts()

            assert len(posts) == 1
            assert posts[0]['status_text'] == 'Post text'
            mock_write.assert_called_once()


@pytest.mark.asyncio
async def test_schedulesheet_respects_max_count():
    """Test ScheduleSheet respects max_count parameter."""
    sheet = ScheduleSheet('sheet-id', 'email@example.com', 'key')

    # Create 5 posts all due now
    rows = []
    for i in range(5):
        rows.append(SheetRow([
            f'Post {i}', 'http://link.com', '', '', '', '',
            '15-01-2024', '14', ''
        ]))

    with patch('agoras.core.sheet.schedule.datetime') as mock_datetime:
        mock_now = datetime.datetime(2024, 1, 15, 14, 0, 0)
        mock_datetime.datetime.now.return_value = mock_now

        with patch.object(sheet, 'read_all', new_callable=AsyncMock) as mock_read:
            with patch.object(sheet, 'write_all', new_callable=AsyncMock):
                mock_read.return_value = rows

                posts = await sheet.process_scheduled_posts(max_count=3)

                # Should only process 3 posts
                assert len(posts) == 3


@pytest.mark.asyncio
async def test_schedulesheet_skips_published_posts():
    """Test ScheduleSheet skips already published posts."""
    sheet = ScheduleSheet('sheet-id', 'email@example.com', 'key')

    row_data = SheetRow([
        'Post text', 'http://link.com', '', '', '', '',
        '15-01-2024', '14', 'published'  # Already published
    ])

    with patch('agoras.core.sheet.schedule.datetime') as mock_datetime:
        mock_now = datetime.datetime(2024, 1, 15, 14, 0, 0)
        mock_datetime.datetime.now.return_value = mock_now

        with patch.object(sheet, 'read_all', new_callable=AsyncMock) as mock_read:
            with patch.object(sheet, 'write_all', new_callable=AsyncMock):
                mock_read.return_value = [row_data]

                posts = await sheet.process_scheduled_posts()

                # Should skip published post
                assert len(posts) == 0


@pytest.mark.asyncio
async def test_schedulesheet_skips_insufficient_columns():
    """Test ScheduleSheet skips rows with insufficient columns."""
    sheet = ScheduleSheet('sheet-id', 'email@example.com', 'key')

    # Row with only 5 columns (need 9)
    row_data = SheetRow(['Post', 'http://link.com', '', '', ''])

    with patch.object(sheet, 'read_all', new_callable=AsyncMock) as mock_read:
        with patch.object(sheet, 'write_all', new_callable=AsyncMock):
            mock_read.return_value = [row_data]

            posts = await sheet.process_scheduled_posts()

            # Should skip row gracefully
            assert len(posts) == 0


@pytest.mark.asyncio
async def test_schedulesheet_handles_invalid_date():
    """Test ScheduleSheet handles invalid date format."""
    sheet = ScheduleSheet('sheet-id', 'email@example.com', 'key')

    row_data = SheetRow([
        'Post text', 'http://link.com', '', '', '', '',
        'invalid-date', '14', ''
    ])

    with patch.object(sheet, 'read_all', new_callable=AsyncMock) as mock_read:
        with patch.object(sheet, 'write_all', new_callable=AsyncMock):
            mock_read.return_value = [row_data]

            # Should not raise exception
            posts = await sheet.process_scheduled_posts()

            # Should skip row with invalid date
            assert len(posts) == 0


# SheetManager Tests

def test_sheetmanager_instantiation():
    """Test SheetManager can be instantiated."""
    manager = SheetManager()
    assert manager.sheets == {}


@pytest.mark.asyncio
@patch('agoras.core.sheet.manager.Sheet')
async def test_sheetmanager_add_sheet(mock_sheet_class):
    """Test SheetManager add_sheet."""
    mock_sheet = MagicMock()
    mock_sheet.authenticate = AsyncMock()
    mock_sheet_class.return_value = mock_sheet

    manager = SheetManager()

    result = await manager.add_sheet(
        'my_sheet', 'sheet-id', 'email@example.com', 'key', 'Sheet1'
    )

    assert 'my_sheet' in manager.sheets
    assert manager.sheets['my_sheet'] is mock_sheet
    mock_sheet.authenticate.assert_called_once()
    assert result is mock_sheet


def test_sheetmanager_get_sheet():
    """Test SheetManager get_sheet."""
    manager = SheetManager()
    mock_sheet = MagicMock()
    manager.sheets['test'] = mock_sheet

    result = manager.get_sheet('test')

    assert result is mock_sheet


def test_sheetmanager_get_sheet_unknown():
    """Test SheetManager get_sheet returns None for unknown."""
    manager = SheetManager()

    result = manager.get_sheet('nonexistent')

    assert result is None


@pytest.mark.asyncio
async def test_sheetmanager_read_all_sheets():
    """Test SheetManager read_all_sheets concurrently."""
    manager = SheetManager()

    mock_sheet1 = MagicMock()
    mock_sheet1.read_all = AsyncMock(return_value=[['data1']])

    mock_sheet2 = MagicMock()
    mock_sheet2.read_all = AsyncMock(return_value=[['data2']])

    manager.sheets['sheet1'] = mock_sheet1
    manager.sheets['sheet2'] = mock_sheet2

    results = await manager.read_all_sheets()

    assert 'sheet1' in results
    assert 'sheet2' in results
    mock_sheet1.read_all.assert_called_once()
    mock_sheet2.read_all.assert_called_once()


@pytest.mark.asyncio
async def test_sheetmanager_read_all_sheets_handles_exceptions():
    """Test SheetManager read_all_sheets handles exceptions."""
    manager = SheetManager()

    mock_sheet_success = MagicMock()
    mock_sheet_success.read_all = AsyncMock(return_value=[['data']])

    mock_sheet_fail = MagicMock()
    mock_sheet_fail.read_all = AsyncMock(side_effect=Exception('Read failed'))

    manager.sheets['success'] = mock_sheet_success
    manager.sheets['failure'] = mock_sheet_fail

    results = await manager.read_all_sheets()

    assert 'success' in results
    assert 'failure' in results
    assert isinstance(results['failure'], Exception)


@pytest.mark.asyncio
async def test_sheetmanager_write_to_multiple_sheets():
    """Test SheetManager write_to_multiple_sheets."""
    manager = SheetManager()

    mock_sheet1 = MagicMock()
    mock_sheet1.write_all = AsyncMock()

    mock_sheet2 = MagicMock()
    mock_sheet2.write_all = AsyncMock()

    manager.sheets['sheet1'] = mock_sheet1
    manager.sheets['sheet2'] = mock_sheet2

    data_map = {
        'sheet1': [['data1']],
        'sheet2': [['data2']]
    }

    await manager.write_to_multiple_sheets(data_map)

    mock_sheet1.write_all.assert_called_once_with([['data1']])
    mock_sheet2.write_all.assert_called_once_with([['data2']])


@pytest.mark.asyncio
async def test_sheetmanager_write_skips_unknown_sheets():
    """Test SheetManager write_to_multiple_sheets skips unknown sheets."""
    manager = SheetManager()

    mock_sheet = MagicMock()
    mock_sheet.write_all = AsyncMock()

    manager.sheets['known'] = mock_sheet

    data_map = {
        'known': [['data1']],
        'unknown': [['data2']]  # This sheet doesn't exist
    }

    await manager.write_to_multiple_sheets(data_map)

    # Should only write to known sheet
    mock_sheet.write_all.assert_called_once()
