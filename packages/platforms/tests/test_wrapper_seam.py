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
"""Wrapper-to-api seam integration tests (U5).

The wrapper suites mock the api class entirely, so the real wrapper-to-api
error seam is invisible to them. These tests wire a REAL api instance
(auth manager + client mocked, api class real) into the wrapper and pin
the error shapes end to end. If the seam regresses to mocks, the
exact-shape assertions below fail — that non-vacuity is the point.
"""

import traceback

import pytest

from agoras.core.auth.exceptions import AuthenticationError
from agoras.core.threading import ThreadPublishError
from agoras.platforms.discord.api import DiscordAPI
from agoras.platforms.discord.wrapper import Discord
from agoras.platforms.x.api import XAPI
from agoras.platforms.x.wrapper import X

TOKEN_MSG = "HTTP 401 access_token=SECRET123 for user 42"


class _FailingAuthManager:
    """Auth manager whose ensure_authenticated raises the categorized error."""

    access_token = None
    user_info = None
    client = None

    def ensure_authenticated(self):
        raise AuthenticationError("token expired")


class _OkAuthManager:
    """Auth manager whose ensure_authenticated succeeds."""

    access_token = "valid-token"
    user_info = None
    client = None

    def ensure_authenticated(self):
        pass


class _XStubClient:
    def __init__(self, error=None):
        self._error = error

    async def create_tweet(self, text, media_ids=None, in_reply_to_tweet_id=None):
        if self._error is not None:
            raise self._error
        return "tweet-123"


class _DiscordStubClient:
    def __init__(self, error=None):
        self._error = error

    async def send_message(self, content=None, embeds=None, file=None, files=None):
        if self._error is not None:
            raise self._error
        return "msg-1"


def _make_x_api(auth_manager, client):
    api = XAPI("ck", "cs", "ot", "os")
    api.auth_manager = auth_manager
    api.client = client
    api._authenticated = False
    return api


def _make_discord_api(auth_manager, client):
    api = DiscordAPI("bot_token", "Server Name", "channel-name")
    api.auth_manager = auth_manager
    api.client = client
    api._authenticated = False
    return api


def _assert_no_token(exc, message):
    assert "SECRET123" not in message
    assert exc.__cause__ is None
    rendered = "".join(traceback.format_exception(exc))
    assert "SECRET123" not in rendered


@pytest.mark.asyncio
async def test_x_seam_uses_real_api_class():
    """Non-vacuity pin: the seam under test is the real XAPI, not a mock."""
    wrapper = X()
    wrapper.api = _make_x_api(_OkAuthManager(), _XStubClient())
    assert isinstance(wrapper.api, XAPI)


@pytest.mark.asyncio
async def test_x_seam_auth_error_propagates_unwrapped():
    wrapper = X()
    wrapper.api = _make_x_api(_FailingAuthManager(), None)
    with pytest.raises(ThreadPublishError) as excinfo:
        await wrapper.thread([{"text": "hello"}])
    error_text = excinfo.value.result.error
    assert error_text == "token expired"
    assert not error_text.startswith("X tweet creation failed")


@pytest.mark.asyncio
async def test_x_seam_wrapped_error_exact_shape():
    wrapper = X()
    wrapper.api = _make_x_api(_OkAuthManager(), _XStubClient(error=ValueError(TOKEN_MSG)))
    with pytest.raises(ThreadPublishError) as excinfo:
        await wrapper.thread([{"text": "hello"}])
    error_text = excinfo.value.result.error
    assert error_text == "X tweet creation failed: HTTP 401 access_token=[REDACTED] for user 42"
    _assert_no_token(excinfo.value, error_text)


@pytest.mark.asyncio
async def test_discord_seam_uses_real_api_class():
    """Non-vacuity pin: the seam under test is the real DiscordAPI, not a mock."""
    wrapper = Discord()
    wrapper.api = _make_discord_api(_OkAuthManager(), _DiscordStubClient())
    assert isinstance(wrapper.api, DiscordAPI)


@pytest.mark.asyncio
async def test_discord_seam_auth_error_propagates_unwrapped():
    wrapper = Discord()
    wrapper.api = _make_discord_api(_FailingAuthManager(), None)
    with pytest.raises(ThreadPublishError) as excinfo:
        await wrapper.thread([{"text": "hello"}], thread_name="t")
    error_text = excinfo.value.result.error
    assert error_text == "token expired"
    assert "failed:" not in error_text


@pytest.mark.asyncio
async def test_discord_seam_sanitizes_token_error():
    wrapper = Discord()
    wrapper.api = _make_discord_api(_OkAuthManager(), _DiscordStubClient(error=ValueError(TOKEN_MSG)))
    with pytest.raises(ThreadPublishError) as excinfo:
        await wrapper.thread([{"text": "hello"}], thread_name="t")
    error_text = excinfo.value.result.error
    assert "SECRET123" not in error_text
    assert "access_token=[REDACTED]" in error_text
    _assert_no_token(excinfo.value, error_text)
