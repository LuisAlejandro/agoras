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
"""Committed guard-behavior assertions for XAPI (U4, assert-or-raise dialect).

The existing x suite runs authenticated fixtures, so guard behavior is
invisible to it. These tests pin the unauthenticated path: X raises its
not-authenticated message without attempting authentication.
"""

import pytest

from agoras.platforms.x.api import XAPI


def _make_api():
    api = XAPI("ck", "cs", "ot", "os")
    api._authenticated = False
    api.client = None
    return api


@pytest.mark.asyncio
async def test_assert_dialect_raises_without_auth_attempt():
    api = _make_api()
    with pytest.raises(Exception) as excinfo:
        await api.post("hello")
    assert str(excinfo.value) == "X API not authenticated"
    assert api._authenticated is False


@pytest.mark.asyncio
async def test_assert_dialect_does_not_attempt_authentication():
    api = _make_api()
    with pytest.raises(Exception):
        await api.like("tweet-1")
    # assert dialect never calls authenticate — verified by _authenticated staying False
    assert api._authenticated is False


@pytest.mark.asyncio
async def test_authenticated_with_client_passes_guards():
    api = _make_api()
    api._authenticated = True
    api.client = _StubClient()
    result = await api.get_post("tweet-1")
    assert result == {"id": "tweet-1"}


class _StubClient:
    async def get_tweet(self, tweet_id):
        return {"id": tweet_id}
