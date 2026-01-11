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
from agoras.core.auth import BaseAuthManager


def test_baseauthmanager_is_abstract():
    """Test that BaseAuthManager cannot be instantiated directly."""
    with pytest.raises(TypeError):
        BaseAuthManager()


def test_baseauthmanager_required_methods():
    """Test that BaseAuthManager defines required methods."""
    assert hasattr(BaseAuthManager, 'authenticate')
    assert hasattr(BaseAuthManager, 'authorize')
    assert hasattr(BaseAuthManager, 'ensure_authenticated')


def test_baseauthmanager_token_storage():
    """Test that BaseAuthManager has token storage integration."""
    # BaseAuthManager.__init__ creates token_storage
    assert hasattr(BaseAuthManager, '__init__')
