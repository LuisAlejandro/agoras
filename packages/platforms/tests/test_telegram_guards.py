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
"""Committed guard-behavior assertions for TelegramAPI (ensure dialect).

The existing telegram suite runs authenticated fixtures, so guard behavior
is invisible to it. These tests pin the unauthenticated path: the
auth-manager ensure runs first and its categorized error propagates
unwrapped; an expired-but-refreshable token heals transparently.
"""

from unittest.mock import AsyncMock

import pytest

from agoras.core.auth.exceptions import AuthenticationError
from ._auth_fakes import CountingOkAuthManager, FailingAuthManager
from agoras.platforms.telegram.api import TelegramAPI


def _make_api(auth_manager=None):
    api = TelegramAPI("bot_token", "chat_id")
    api.auth_manager = auth_manager
    api._authenticated = False
    api.client = None
    return api


@pytest.mark.asyncio
async def test_ensure_dialect_no_credentials_raises_categorized_auth_error():
    api = _make_api(auth_manager=FailingAuthManager("Telegram token expired"))
    with pytest.raises(AuthenticationError):
        await api.send_message("chat_id", "hello")


@pytest.mark.asyncio
async def test_ensure_dialect_heals_expired_token():
    manager = CountingOkAuthManager()
    api = _make_api(auth_manager=manager)
    api.client = AsyncMock()
    api.client.send_message = AsyncMock(return_value={"message_id": 1})
    result = await api.send_message("chat_id", "hello")
    assert result == "1"
    assert manager.ensure_calls == 1


@pytest.mark.asyncio
async def test_like_share_raise_without_guards():
    api = _make_api(auth_manager=FailingAuthManager("Telegram token expired"))
    with pytest.raises(Exception) as excinfo:
        await api.like("post-1")
    assert str(excinfo.value) == "Like not supported for Telegram"

    with pytest.raises(Exception) as excinfo:
        await api.share("post-1")
    assert str(excinfo.value) == "Share not supported for Telegram"


@pytest.mark.asyncio
async def test_send_photo_media_prep_error_surfaces_unwrapped():
    """Media-prep errors ('No photo content available') must not gain a wrap prefix."""
    api = _make_api(auth_manager=CountingOkAuthManager())
    api._authenticated = True
    api.client = AsyncMock()
    with pytest.raises(Exception) as excinfo:
        await api.send_photo(chat_id="chat-1", photo_url=None, photo_content=None)
    assert str(excinfo.value) == "No photo content available"
    assert not str(excinfo.value).startswith("Telegram send photo failed")


@pytest.mark.asyncio
async def test_send_photo_client_call_error_is_wrapped():
    """Client-call errors are still wrapped with the operation prefix."""
    api = _make_api(auth_manager=CountingOkAuthManager())
    api._authenticated = True
    api.client = AsyncMock()
    api.client.send_photo.side_effect = Exception("Bearer tok123")
    with pytest.raises(Exception) as excinfo:
        await api.send_photo(chat_id="chat-1", photo_url=None, photo_content=b"data")
    assert str(excinfo.value).startswith("Telegram send photo failed:")
    assert "Bearer [REDACTED]" in str(excinfo.value)


@pytest.mark.asyncio
async def test_reply_ensure_failure_raises_unwrapped():
    api = _make_api(auth_manager=FailingAuthManager("Telegram token expired"))
    with pytest.raises(AuthenticationError) as excinfo:
        await api.reply("123", "hello")
    assert "failed:" not in str(excinfo.value)


@pytest.mark.asyncio
async def test_reply_no_client_raises_not_available():
    from unittest.mock import MagicMock

    api = _make_api(auth_manager=CountingOkAuthManager())
    api.chat_id = "chat-1"
    with pytest.raises(Exception) as excinfo:
        await api.reply("123", "hello")
    assert str(excinfo.value) == "Telegram client not available"


@pytest.mark.asyncio
async def test_reply_missing_chat_id_and_invalid_post_id():
    from unittest.mock import MagicMock

    api = _make_api(auth_manager=CountingOkAuthManager())
    api.client = MagicMock()
    api.chat_id = None
    with pytest.raises(Exception) as excinfo:
        await api.reply("123", "hello")
    assert str(excinfo.value) == "Telegram chat_id is required for reply"

    api.chat_id = "chat-1"
    with pytest.raises(ValueError):
        await api.reply("not-an-int", "hello")
