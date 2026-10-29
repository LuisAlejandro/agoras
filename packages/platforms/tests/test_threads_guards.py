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
"""Committed guard-behavior assertions for ThreadsAPI (U8).

The existing threads test suite runs authenticated fixtures, so guard
behavior is invisible to it. These tests pin the unauthenticated paths:
the auth-manager-ensure dialect, the token-presence check, the
client-presence check, guard-phase error propagation, and get_profile's
token-check-only exception (no ensure, no rate limit).
"""

from unittest.mock import AsyncMock

import pytest

from agoras.core.auth.exceptions import AuthenticationError
from agoras.platforms.threads.api import ThreadsAPI


class _FailingAuthManager:
    """Auth manager whose ensure_authenticated raises the categorized error."""

    access_token = "stale-token"
    user_id = None
    user_info = None
    client = None

    def ensure_authenticated(self):
        raise AuthenticationError("Threads token expired")


class _SpyAuthManager:
    """Auth manager that records ensure_authenticated calls."""

    access_token = None
    user_id = None
    user_info = None
    client = None
    ensure_calls = 0

    def ensure_authenticated(self):
        self.ensure_calls += 1
        raise AuthenticationError("Threads token expired")


class _OkAuthManager:
    """Auth manager whose ensure_authenticated succeeds, with a token."""

    access_token = "valid-token"
    user_id = "user123"
    user_info = None
    client = None

    def ensure_authenticated(self):
        pass


class _ThreadsClientStub:
    """Sync client stub for the to_thread closures."""

    def get_profile(self):
        return {"id": "user123", "username": "testuser"}

    def create_post(self, **kwargs):
        return {"id": "post-123"}


def _make_api(auth_manager=None):
    api = ThreadsAPI("app_id", "app_secret", "refresh_token")
    api.auth_manager = auth_manager
    api.client = None
    api._authenticated = False
    return api


@pytest.mark.asyncio
async def test_create_post_no_credentials_raises_categorized_auth_error():
    api = _make_api(auth_manager=_FailingAuthManager())
    with pytest.raises(AuthenticationError):
        await api.create_post("Test post")


@pytest.mark.asyncio
async def test_create_post_no_token_raises_not_authenticated():
    api = _make_api(auth_manager=_OkAuthManager())
    api.auth_manager.access_token = None
    with pytest.raises(Exception) as excinfo:
        await api.create_post("Test post")
    assert str(excinfo.value) == "Threads API not authenticated"


@pytest.mark.asyncio
async def test_create_post_no_client_raises_not_available():
    api = _make_api(auth_manager=_OkAuthManager())
    with pytest.raises(Exception) as excinfo:
        await api.create_post("Test post")
    assert str(excinfo.value) == "Threads client not available"


@pytest.mark.asyncio
async def test_create_post_guard_errors_propagate_unwrapped():
    api = _make_api(auth_manager=_FailingAuthManager())
    with pytest.raises(AuthenticationError) as excinfo:
        await api.create_post("Test post")
    # Guard-phase errors must not be wrapped into a generic exception
    assert not str(excinfo.value).startswith("Threads post creation failed")


@pytest.mark.asyncio
async def test_get_profile_is_token_check_only():
    """get_profile raises on missing token with no ensure and no rate limit."""
    api = _make_api(auth_manager=_SpyAuthManager())
    api._rate_limit_check = AsyncMock()
    with pytest.raises(Exception) as excinfo:
        await api.get_profile()
    assert str(excinfo.value) == "Threads API not authenticated"
    assert api.auth_manager.ensure_calls == 0
    api._rate_limit_check.assert_not_called()


@pytest.mark.asyncio
async def test_authenticated_with_client_passes():
    api = _make_api(auth_manager=_OkAuthManager())
    api.client = _ThreadsClientStub()
    result = await api.create_post("Test post")
    assert result == "post-123"
    profile = await api.get_profile()
    assert profile == {"id": "user123", "username": "testuser"}
