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
"""Committed guard-behavior assertions for DiscordAPI (ensure dialect).

The existing discord suite runs authenticated fixtures, so guard behavior
is invisible to it. These tests pin the unauthenticated path: the
auth-manager ensure runs first and its categorized error propagates
unwrapped; an expired-but-refreshable token heals transparently.
"""

from unittest.mock import AsyncMock, MagicMock

import pytest

from agoras.core.auth.exceptions import AuthenticationError
from ._auth_fakes import CountingOkAuthManager, FailingAuthManager
from agoras.platforms.discord.api import DiscordAPI


def _make_api(auth_manager=None):
    api = DiscordAPI("bot_token", "Server Name", "channel-name")
    api.auth_manager = auth_manager
    api._authenticated = False
    api.client = None
    return api


@pytest.mark.asyncio
async def test_ensure_dialect_no_credentials_raises_categorized_auth_error():
    api = _make_api(auth_manager=FailingAuthManager("Discord token expired"))
    with pytest.raises(AuthenticationError):
        await api.post(content="hello")


@pytest.mark.asyncio
async def test_ensure_dialect_no_client_raises_not_available():
    api = _make_api(auth_manager=CountingOkAuthManager())
    with pytest.raises(Exception) as excinfo:
        await api.post(content="hello")
    assert str(excinfo.value) == "Discord client not available"


@pytest.mark.asyncio
async def test_ensure_dialect_heals_expired_token():
    manager = CountingOkAuthManager()
    api = _make_api(auth_manager=manager)
    api.client = MagicMock()
    api.client.send_message = AsyncMock(return_value="msg-1")
    result = await api.post(content="hello")
    assert result == "msg-1"
    assert manager.ensure_calls == 1


@pytest.mark.asyncio
async def test_authenticated_with_client_passes_guards():
    api = _make_api(auth_manager=CountingOkAuthManager())
    api._authenticated = True
    api.client = MagicMock()
    api.client.send_message = AsyncMock(return_value="msg-1")
    result = await api.post(content="hello")
    assert result == "msg-1"


@pytest.mark.asyncio
async def test_create_embed_sync_works_without_auth():
    api = _make_api()
    api.client = MagicMock()
    api.client.create_embed = MagicMock(return_value="embed-obj")
    result = api.create_embed(title="Title")
    assert result == "embed-obj"
    assert api._authenticated is False
