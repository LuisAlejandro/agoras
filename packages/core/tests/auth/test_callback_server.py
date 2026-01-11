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

from agoras.core.auth.callback_server import OAuthCallbackHandler, OAuthCallbackServer


def test_callback_server_instantiation():
    """Test OAuthCallbackServer can be instantiated."""
    server = OAuthCallbackServer()
    assert server is not None


def test_callback_server_with_state():
    """Test OAuthCallbackServer with expected state."""
    server = OAuthCallbackServer(expected_state='test_state_123')
    assert server.expected_state == 'test_state_123'


@pytest.mark.asyncio
async def test_callback_server_get_available_port():
    """Test that callback server can find an available port."""
    server = OAuthCallbackServer()
    port = await server.get_available_port()
    assert isinstance(port, int)
    assert 1024 <= port <= 65535


def test_callback_handler_exists():
    """Test that OAuthCallbackHandler class exists."""
    assert OAuthCallbackHandler is not None
    assert hasattr(OAuthCallbackHandler, 'do_GET')
