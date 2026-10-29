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
"""Committed guard-behavior assertions for XAPI (ensure dialect).

The existing x suite runs authenticated fixtures, so guard behavior is
invisible to it. These tests pin the unauthenticated path: the auth-manager
ensure runs first and its categorized error propagates unwrapped; an
expired-but-refreshable token heals transparently.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from agoras.core.auth.exceptions import AuthenticationError
from ._auth_fakes import CountingOkAuthManager, FailingAuthManager
from agoras.platforms.x.api import XAPI
from agoras.platforms.x.auth import XAuthManager


def _make_api(auth_manager=None):
    api = XAPI("ck", "cs", "ot", "os")
    api.auth_manager = auth_manager
    api.client = None
    api._authenticated = False
    return api


class _StubClient:
    async def get_tweet(self, tweet_id):
        return {"id": tweet_id}

    async def create_tweet(self, text, media_ids=None, in_reply_to_tweet_id=None):
        return "tweet-123"


@pytest.mark.asyncio
async def test_ensure_dialect_no_credentials_raises_categorized_auth_error():
    api = _make_api(auth_manager=FailingAuthManager("X token expired"))
    with pytest.raises(AuthenticationError):
        await api.post("hello")


@pytest.mark.asyncio
async def test_ensure_dialect_guard_errors_propagate_unwrapped():
    api = _make_api(auth_manager=FailingAuthManager("X token expired"))
    with pytest.raises(AuthenticationError) as excinfo:
        await api.like("tweet-1")
    assert not str(excinfo.value).startswith("X like failed")


@pytest.mark.asyncio
async def test_ensure_dialect_heals_expired_token():
    manager = CountingOkAuthManager()
    api = _make_api(auth_manager=manager)
    api.client = _StubClient()
    result = await api.post("hello", validate=False)
    assert result == "tweet-123"
    assert manager.ensure_calls == 1


@pytest.mark.asyncio
async def test_authenticated_with_client_passes_guards():
    api = _make_api(auth_manager=CountingOkAuthManager())
    api._authenticated = True
    api.client = _StubClient()
    result = await api.get_post("tweet-1")
    assert result == {"id": "tweet-1"}


@pytest.mark.asyncio
async def test_reply_shares_post_rate_limit_bucket():
    """reply throttles on the 'post' bucket key, not a reply key."""
    from unittest.mock import AsyncMock

    api = _make_api(auth_manager=CountingOkAuthManager())
    api._authenticated = True
    api.client = _StubClient()
    api._rate_limit_check = AsyncMock()

    await api.post("hello", validate=False)
    await api.reply("hello", in_reply_to_tweet_id="tweet-1")

    calls = [c.args[0] for c in api._rate_limit_check.call_args_list]
    assert calls == ["post", "post"], f"expected shared 'post' bucket, got {calls}"


@pytest.mark.asyncio
async def test_real_manager_ensure_passes_after_authenticate():
    """Real XAuthManager: authenticate() establishes manager.authenticated so ensure passes."""
    manager = XAuthManager("ck", "cs", "ot", "os")
    stub_client = MagicMock()
    stub_client.authenticate = AsyncMock()
    with patch.object(XAuthManager, "_create_client", return_value=stub_client):
        assert await manager.authenticate() is True
    assert manager.authenticated is True
    manager.ensure_authenticated()  # must not raise


@pytest.mark.asyncio
async def test_real_manager_ensure_raises_without_credentials():
    """Real XAuthManager without credentials still raises the categorized error."""
    from agoras.core.auth.exceptions import AuthenticationError as AuthError

    manager = XAuthManager(None, None, None, None)
    with pytest.raises(AuthError):
        manager.ensure_authenticated()
