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
"""Committed guard-behavior assertions for DiscordAPI (U4, auto-auth dialect).

The existing discord suite runs authenticated fixtures, so guard behavior
is invisible to it. These tests pin the unauthenticated path: Discord
attempts authentication first (auto-auth dialect), then raises its
not-available message when no client is present.
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from agoras.platforms.discord.api import DiscordAPI


def _make_api():
    with patch("agoras.platforms.discord.api.DiscordAuthManager"):
        api = DiscordAPI("bot_token", "Server Name", "channel-name")
    api._authenticated = False
    api.client = None
    return api


@pytest.mark.asyncio
async def test_auto_auth_dialect_authenticates_before_client_check():
    api = _make_api()

    async def _authenticate():
        api._authenticated = True  # client stays None

    api.authenticate = _authenticate
    with pytest.raises(Exception) as excinfo:
        await api.post(content="hello")
    assert str(excinfo.value) == "Discord client not available"
    assert api._authenticated is True


@pytest.mark.asyncio
async def test_authenticated_with_client_passes_guards():
    api = _make_api()
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
