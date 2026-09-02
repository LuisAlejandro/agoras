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
"""Committed guard-behavior assertions for TelegramAPI (U4, auto-auth dialect).

The existing telegram suite runs authenticated fixtures, so guard behavior
is invisible to it. These tests pin the unauthenticated path: Telegram
attempts authentication first (auto-auth dialect), then raises its
not-available message when no client is present.
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from agoras.platforms.telegram.api import TelegramAPI


def _make_api():
    with patch("agoras.platforms.telegram.api.TelegramAuthManager"):
        api = TelegramAPI("bot_token", "chat_id")
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
        await api.send_message("chat_id", "hello")
    assert str(excinfo.value) == "Telegram client not available"
    assert api._authenticated is True


@pytest.mark.asyncio
async def test_get_bot_info_has_no_rate_limit():
    api = _make_api()
    api._authenticated = True
    api.client = MagicMock()
    api.client.get_me = AsyncMock(return_value={"id": 123, "username": "testbot"})
    api._rate_limit_check = AsyncMock()
    result = await api.get_bot_info()
    assert result == {"id": 123, "username": "testbot"}
    api._rate_limit_check.assert_not_called()


@pytest.mark.asyncio
async def test_like_share_raise_without_auth_attempt():
    api = _make_api()

    async def _fail():
        raise AssertionError("authenticate must not be called")

    api.authenticate = _fail
    with pytest.raises(Exception) as excinfo:
        await api.like("post-1")
    assert str(excinfo.value) == "Like not supported for Telegram"

    with pytest.raises(Exception) as excinfo:
        await api.share("post-1")
    assert str(excinfo.value) == "Share not supported for Telegram"

    assert api._authenticated is False
