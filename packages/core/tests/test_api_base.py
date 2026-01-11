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
from agoras.core.api_base import BaseAPI


def test_baseapi_is_abstract():
    """Test that BaseAPI cannot be instantiated directly."""
    with pytest.raises(TypeError):
        BaseAPI()


def test_baseapi_required_methods():
    """Test that BaseAPI defines required abstract methods."""
    assert hasattr(BaseAPI, 'authenticate')
    assert hasattr(BaseAPI, 'disconnect')


def test_baseapi_rate_limiting():
    """Test that rate limiting structure exists."""
    assert hasattr(BaseAPI, '_rate_limit_check')


def test_baseapi_error_handling():
    """Test that error handling method exists."""
    assert hasattr(BaseAPI, '_handle_api_error')
