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
"""Wrapper token-leak tests (R12).

The existing wrapper suites mock the api class entirely, so the publish
except paths never see a realistic token-bearing error. These tests drive
token-bearing and signed-URL exceptions through each wrapper re-chain
site and assert the sanitized result/exception and clean rendered
traceback.
"""

import traceback

import pytest

from agoras.core.threading import ThreadPublishError
from agoras.platforms.discord.wrapper import Discord
from agoras.platforms.threads.wrapper import Threads
from agoras.platforms.tiktok.wrapper import TikTok
from agoras.platforms.whatsapp.wrapper import WhatsApp
from agoras.platforms.x.wrapper import X

TOKEN_MSG = "HTTP 401 access_token=SECRET123 for user 42"
SIGNED_URL_MSG = "download failed https://cdn.example.com/v.mp4?X-Amz-Signature=abc123"


class _TokenApi:
    """Stub api whose publish method raises a token-bearing error."""

    def __init__(self, method_name, message):
        self._method_name = method_name
        self._message = message

    def __getattr__(self, name):
        async def _raise(*args, **kwargs):
            raise ValueError(self._message)

        async def _noop(*args, **kwargs):
            return None

        return _raise if name == self._method_name else _noop


def _assert_no_token(exc, message):
    if message is not None:
        assert "SECRET123" not in message
        assert "abc123" not in message
    assert exc.__cause__ is None
    assert exc.__suppress_context__ is True
    rendered = "".join(traceback.format_exception(exc))
    assert "SECRET123" not in rendered
    assert "abc123" not in rendered


@pytest.mark.asyncio
async def test_x_thread_rechain_sanitizes_token_error():
    wrapper = X()
    wrapper.api = _TokenApi("post", TOKEN_MSG)
    with pytest.raises(ThreadPublishError) as excinfo:
        await wrapper.thread([{"text": "hello"}])
    error_text = excinfo.value.result.error
    assert error_text is not None
    assert "SECRET123" not in error_text
    assert "access_token=[REDACTED]" in error_text
    _assert_no_token(excinfo.value, error_text)


@pytest.mark.asyncio
async def test_x_thread_rechain_sanitizes_signed_url_error():
    wrapper = X()
    wrapper.api = _TokenApi("post", SIGNED_URL_MSG)
    with pytest.raises(ThreadPublishError) as excinfo:
        await wrapper.thread([{"text": "hello"}])
    error_text = excinfo.value.result.error
    assert error_text is not None
    assert "abc123" not in error_text
    _assert_no_token(excinfo.value, error_text)


@pytest.mark.asyncio
async def test_threads_thread_rechain_sanitizes_token_error():
    wrapper = Threads()
    wrapper.api = _TokenApi("create_post", TOKEN_MSG)
    with pytest.raises(ThreadPublishError) as excinfo:
        await wrapper.thread([{"text": "hello"}])
    error_text = excinfo.value.result.error
    assert error_text is not None
    assert "SECRET123" not in error_text
    _assert_no_token(excinfo.value, error_text)


@pytest.mark.asyncio
async def test_discord_thread_rechain_sanitizes_token_error():
    wrapper = Discord()
    wrapper.api = _TokenApi("post", TOKEN_MSG)
    with pytest.raises(ThreadPublishError) as excinfo:
        await wrapper.thread([{"text": "hello"}], thread_name="test-thread")
    error_text = excinfo.value.result.error
    assert error_text is not None
    assert "SECRET123" not in error_text
    _assert_no_token(excinfo.value, error_text)


@pytest.mark.asyncio
async def test_whatsapp_template_json_error_sanitized():
    wrapper = WhatsApp()
    wrapper.api = _TokenApi("send_template", TOKEN_MSG)
    wrapper.config = {"whatsapp_template_components": '{"payload": "access_token=SECRET123"'}
    with pytest.raises(Exception) as excinfo:
        await wrapper._handle_template_action()
    message = str(excinfo.value)
    assert "SECRET123" not in message
    _assert_no_token(excinfo.value, message)


@pytest.mark.asyncio
async def test_tiktok_creator_info_classified_reraise_sanitized():
    wrapper = TikTok()
    wrapper.api = _TokenApi(
        "refresh_creator_info",
        "TikTok user not authenticated: access_token=SECRET123",
    )
    with pytest.raises(Exception) as excinfo:
        await wrapper._require_fresh_creator_info()
    message = str(excinfo.value)
    assert "SECRET123" not in message
    assert "not authenticated" in message.lower()
    _assert_no_token(excinfo.value, message)
