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

import pytest
from agoras.core.sheet import ScheduleSheet, Sheet


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


def test_sheet_instantiation():
    """Test Sheet can be instantiated."""
    sheet = Sheet(
        sheet_id='test_id',
        client_email='test@example.com',
        private_key='test_key'
    )
    assert sheet is not None


def test_sheet_has_required_methods():
    """Test Sheet has required methods."""
    assert hasattr(Sheet, 'authenticate')
    assert hasattr(Sheet, 'get_worksheet')
