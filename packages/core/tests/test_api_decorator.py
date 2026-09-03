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
"""Tests for the composable guard decorators in agoras.core.api_base."""

import inspect
import time

import pytest

from agoras.core.api_base import (
    BaseAPI,
    guard_assert_auth,
    guard_auth_attempt,
    guard_client_presence,
    guard_ensure_auth_manager,
    guard_error_wrap,
    guard_rate_limit,
)


class _AuthError(Exception):
    """Stand-in for the categorized authentication error."""


class _StubAPI(BaseAPI):
    """Minimal concrete BaseAPI the guard decorators operate on."""

    def __init__(self):
        super().__init__()
        self._authenticated = False
        self.client = None
        self.auth_manager = None
        self._rate_limit_cache = {}
        self._last_request_time = 0
        self.auth_attempts = 0
        self.ensure_calls = 0
        self._not_authenticated_message = "Stub API not authenticated"
        self._client_not_available_message = "Stub client not available"
        self.wrapped = False

    async def authenticate(self):
        self.auth_attempts += 1
        if not getattr(self, "_auth_ok", False):
            raise _AuthError("stub auth failed")

    async def disconnect(self):
        pass

    async def post(self, *args, **kwargs):
        pass

    async def like(self, post_id, *args, **kwargs):
        pass

    async def delete(self, post_id, *args, **kwargs):
        pass

    async def share(self, post_id, *args, **kwargs):
        pass

    async def op(self, value):
        return value

    async def unguarded_op(self, value):
        return value


@pytest.mark.asyncio
async def test_guard_auth_attempt_authenticates_when_unauthenticated():
    api = _StubAPI()
    api._auth_ok = True
    decorated = guard_auth_attempt(_StubAPI.op)
    result = await decorated(api, "value")
    assert result == "value"
    assert api.auth_attempts == 1


@pytest.mark.asyncio
async def test_guard_auth_attempt_propagates_auth_error_unmodified():
    api = _StubAPI()
    decorated = guard_auth_attempt(_StubAPI.op)
    with pytest.raises(_AuthError):
        await decorated(api, "value")
    assert api.auth_attempts == 1


@pytest.mark.asyncio
async def test_guard_assert_auth_raises_when_unauthenticated():
    api = _StubAPI()
    decorated = guard_assert_auth(_StubAPI.op)
    with pytest.raises(Exception) as excinfo:
        await decorated(api, "value")
    assert str(excinfo.value) == "Stub API not authenticated"
    assert api.auth_attempts == 0


@pytest.mark.asyncio
async def test_guard_assert_auth_passes_when_authenticated_with_client():
    api = _StubAPI()
    api._authenticated = True
    api.client = object()
    decorated = guard_assert_auth(_StubAPI.op)
    assert await decorated(api, "value") == "value"


@pytest.mark.asyncio
async def test_guard_ensure_auth_manager_invokes_ensure():
    api = _StubAPI()

    class _Manager:
        def ensure_authenticated(self):
            api.ensure_calls += 1
            if not getattr(api, "_ensure_ok", False):
                raise _AuthError("ensure failed")

    api.auth_manager = _Manager()
    api._ensure_ok = True
    decorated = guard_ensure_auth_manager(_StubAPI.op)
    assert await decorated(api, "value") == "value"
    assert api.ensure_calls == 1


@pytest.mark.asyncio
async def test_guard_ensure_auth_manager_propagates_auth_error_unmodified():
    api = _StubAPI()

    class _Manager:
        def ensure_authenticated(self):
            raise _AuthError("ensure failed")

    api.auth_manager = _Manager()
    decorated = guard_ensure_auth_manager(_StubAPI.op)
    with pytest.raises(_AuthError):
        await decorated(api, "value")


@pytest.mark.asyncio
async def test_guard_client_presence_raises_when_client_missing():
    api = _StubAPI()
    api.client = None
    decorated = guard_client_presence(_StubAPI.op)
    with pytest.raises(Exception) as excinfo:
        await decorated(api, "value")
    assert str(excinfo.value) == "Stub client not available"


@pytest.mark.asyncio
async def test_guard_client_presence_passes_when_client_present():
    api = _StubAPI()
    api.client = object()
    decorated = guard_client_presence(_StubAPI.op)
    assert await decorated(api, "value") == "value"


@pytest.mark.asyncio
async def test_guard_error_wrap_normalizes_and_sanitizes():
    api = _StubAPI()

    class _BadClient:
        async def boom(self):
            raise ValueError("Bearer abc123def456 failed")

    api.client = _BadClient()

    async def op(self, value):
        return await self.client.boom()

    decorated = guard_error_wrap("stub op")(op)
    with pytest.raises(Exception) as excinfo:
        await decorated(api, "value")
    assert "Bearer [REDACTED]" in str(excinfo.value)
    assert "stub op failed" in str(excinfo.value)


@pytest.mark.asyncio
async def test_guard_error_wrap_severs_chained_cause():
    api = _StubAPI()

    async def op(self, value):
        raise ValueError("Bearer secret123")

    decorated = guard_error_wrap("stub op")(op)
    with pytest.raises(Exception) as excinfo:
        await decorated(api, "value")
    assert excinfo.value.__cause__ is None
    assert excinfo.value.__suppress_context__ is True
    import traceback

    rendered = "".join(traceback.format_exception(excinfo.value))
    assert "secret123" not in rendered
    assert "Bearer [REDACTED]" in str(excinfo.value)


@pytest.mark.asyncio
async def test_disconnect_resets_state_when_hook_raises():
    """A raising disconnect hook must not leave stale authenticated state."""
    api = _StubAPI()
    api.client = object()
    api._authenticated = True

    def raising_hook():
        raise ConnectionError("client disconnect failed")

    api._disconnect_hook = raising_hook

    with pytest.raises(ConnectionError):
        await BaseAPI.disconnect(api)

    assert api.client is None
    assert api._authenticated is False


@pytest.mark.asyncio
async def test_guard_rate_limit_waits_same_bucket():
    api = _StubAPI()
    decorated = guard_rate_limit("post", 0.05)(_StubAPI.op)
    start = time.time()
    await decorated(api, "a")
    await decorated(api, "b")
    elapsed = time.time() - start
    assert elapsed >= 0.05
    assert api._rate_limit_cache["post"] > 0


@pytest.mark.asyncio
async def test_guard_rate_limit_shared_bucket_key():
    api = _StubAPI()
    op1 = guard_rate_limit("post", 0.05)(_StubAPI.op)
    op2 = guard_rate_limit("post", 0.05)(_StubAPI.unguarded_op)
    start = time.time()
    await op1(api, "a")
    await op2(api, "b")
    assert time.time() - start >= 0.05


@pytest.mark.asyncio
async def test_full_stack_composition_order_guard_before_wait():
    api = _StubAPI()
    order = []

    async def op(self, value):
        order.append("client-call")
        return value

    class _Manager:
        def ensure_authenticated(self):
            order.append("ensure")

    api.auth_manager = _Manager()
    api.client = object()
    api._ensure_ok = True

    decorated = guard_rate_limit("op", 0.01)(
        guard_error_wrap("op")(guard_ensure_auth_manager(op))
    )
    await decorated(api, "value")
    assert order == ["ensure", "client-call"]


@pytest.mark.asyncio
async def test_guard_skip_method_raises_without_guards():
    api = _StubAPI()

    async def not_supported(self, value):
        raise Exception("not supported by stub")

    decorated = not_supported  # no guard applied — the guard-skip case
    with pytest.raises(Exception) as excinfo:
        await decorated(api, "value")
    assert str(excinfo.value) == "not supported by stub"


def test_signature_preserved_through_decorators():
    async def sample(self, chat_id: str, text: str, parse_mode=None) -> str:
        return text

    decorated = guard_error_wrap("send message")(guard_client_presence(sample))
    sig = inspect.signature(decorated)
    params = list(sig.parameters.values())
    assert params[0].name == "self"
    assert params[1].name == "chat_id"
    assert params[2].name == "text"
    assert params[3].name == "parse_mode"
    assert params[3].default is None
    assert sig.return_annotation is str


def test_baseapi_error_handler_is_noreturn_and_severs_cause():
    class _Concrete(BaseAPI):
        async def authenticate(self):
            pass

        async def disconnect(self):
            pass

        async def post(self, *args, **kwargs):
            pass

        async def like(self, post_id, *args, **kwargs):
            pass

        async def delete(self, post_id, *args, **kwargs):
            pass

        async def share(self, post_id, *args, **kwargs):
            pass

    api = _Concrete()
    with pytest.raises(Exception) as excinfo:
        api._handle_api_error(ValueError("Bearer tok123"), "op")
    assert excinfo.value.__cause__ is None
    assert "Bearer [REDACTED]" in str(excinfo.value)


@pytest.mark.asyncio
async def test_guard_error_wrap_failsafe_sanitizes_when_handler_returns():
    """A non-raising _handle_api_error override must not re-raise the raw exception."""
    api = _StubAPI()

    def returning_handler(error, operation_name):
        return None  # violates the NoReturn contract

    api._handle_api_error = returning_handler

    async def op(self, value):
        raise ValueError("Bearer tok123")

    decorated = guard_error_wrap("stub op")(op)
    with pytest.raises(Exception) as excinfo:
        await decorated(api, "value")
    assert excinfo.value.__cause__ is None
    assert "Bearer [REDACTED]" in str(excinfo.value)
    assert "tok123" not in str(excinfo.value)
