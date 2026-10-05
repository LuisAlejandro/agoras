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
"""Committed guard-behavior assertions for FacebookAPI (U5, auth-manager-ensure dialect).

The existing facebook suite runs authenticated fixtures, so guard behavior is
invisible to it. These tests pin the unauthenticated path: the auth-manager
ensure raises the categorized AuthenticationError and it propagates unwrapped,
and the client-presence check raises facebook's not-authenticated template.
"""

import pytest

from agoras.core.auth.exceptions import AuthenticationError
from agoras.platforms.facebook.api import FacebookAPI


class _FailingAuthManager:
    """Auth manager whose ensure_authenticated raises the categorized error."""

    access_token = None
    user_info = None
    client = None

    def ensure_authenticated(self):
        raise AuthenticationError("Facebook token expired")


class _OkAuthManager:
    """Auth manager whose ensure_authenticated succeeds, with a token."""

    access_token = "valid-token"
    user_info = None
    client = None

    def ensure_authenticated(self):
        pass


def _make_api(auth_manager=None):
    api = FacebookAPI("page_id", "client_id", "client_secret")
    api.auth_manager = auth_manager
    api.client = None
    api._authenticated = False
    return api


class _StubClient:
    async def create_post(self, object_id, message=None, link=None, attached_media=None):
        return "post-123"


@pytest.mark.asyncio
async def test_post_no_credentials_raises_categorized_auth_error():
    api = _make_api(auth_manager=_FailingAuthManager())
    with pytest.raises(AuthenticationError):
        await api.post("page_id", message="Hello")


@pytest.mark.asyncio
async def test_post_guard_errors_propagate_unwrapped():
    api = _make_api(auth_manager=_FailingAuthManager())
    with pytest.raises(AuthenticationError) as excinfo:
        await api.post("page_id", message="Hello")
    # Guard-phase errors must not be wrapped into a generic exception
    assert not str(excinfo.value).startswith("Facebook post creation failed")


@pytest.mark.asyncio
async def test_post_no_client_raises_not_authenticated():
    api = _make_api(auth_manager=_OkAuthManager())
    with pytest.raises(Exception) as excinfo:
        await api.post("page_id", message="Hello")
    assert str(excinfo.value) == "Facebook API not authenticated"


@pytest.mark.asyncio
async def test_get_page_token_missing_token_is_wrapped():
    api = _make_api(auth_manager=_OkAuthManager())
    api.auth_manager.access_token = None
    api.client = _StubClient()
    with pytest.raises(Exception) as excinfo:
        await api.get_page_token("page_id")
    assert str(excinfo.value).startswith("Facebook page token exchange failed: Facebook access token not available")


@pytest.mark.asyncio
async def test_authenticated_with_client_passes():
    api = _make_api(auth_manager=_OkAuthManager())
    api.client = _StubClient()
    result = await api.post("page_id", message="Hello")
    assert result == "post-123"
