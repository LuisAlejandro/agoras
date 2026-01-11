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

import os
import tempfile
import pytest
from agoras.core.auth.storage import SecureTokenStorage


def test_tokenstorage_instantiation():
    """Test SecureTokenStorage can be instantiated."""
    storage = SecureTokenStorage()
    assert storage is not None


def test_tokenstorage_save_and_load():
    """Test SecureTokenStorage save and load methods."""
    storage = SecureTokenStorage()
    test_tokens = {'access_token': 'test123', 'refresh_token': 'refresh456'}

    # Save tokens
    storage.save_token('test_platform', 'test_user', test_tokens)

    # Load tokens
    loaded = storage.load_token('test_platform', 'test_user')
    assert loaded == test_tokens

    # Cleanup
    storage.delete_token('test_platform', 'test_user')


def test_tokenstorage_delete():
    """Test SecureTokenStorage delete method."""
    storage = SecureTokenStorage()
    storage.save_token('test_platform', 'test_user', {'token': 'value'})
    storage.delete_token('test_platform', 'test_user')

    # Should return None after deletion
    loaded = storage.load_token('test_platform', 'test_user')
    assert loaded is None


def test_securetokenstorage_instantiation():
    """Test SecureTokenStorage can be instantiated."""
    storage = SecureTokenStorage()
    assert storage is not None


def test_securetokenstorage_encryption():
    """Test SecureTokenStorage encrypts tokens."""
    storage = SecureTokenStorage()
    test_tokens = {'access_token': 'secret123'}

    storage.save_token('test_platform', 'test_user', test_tokens)
    loaded = storage.load_token('test_platform', 'test_user')

    # Should decrypt correctly
    assert loaded == test_tokens

    # Cleanup
    storage.delete_token('test_platform', 'test_user')
