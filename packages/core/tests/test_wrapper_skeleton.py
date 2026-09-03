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
"""Tests for the hoisted wrapper skeleton in the SocialNetwork base."""

import pytest

from agoras.core.interfaces import SocialNetwork, _entry_images, _is_uncertain_publish_error


class _Stub(SocialNetwork):
    """Minimal concrete SocialNetwork for skeleton tests."""

    _proxy_delete_reply = False

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.api = None
        self.init_calls = 0
        self.executed_actions = []
        self.disconnect_calls = 0

    async def _initialize_client(self):
        self.init_calls += 1
        if getattr(self, "_fail_init", False):
            raise Exception(f"{self.__class__.__name__} API not initialized")
        self.api = _Api()

    async def post(self, *args, **kwargs):
        return "post-id"

    async def like(self, post_id, *args, **kwargs):
        return post_id

    async def delete(self, post_id, *args, **kwargs):
        return post_id

    async def share(self, post_id, *args, **kwargs):
        return post_id

    async def execute_action(self, action):
        self.executed_actions.append(action)
        await self._initialize_client()
        if getattr(self, "_fail_action", False):
            raise Exception("boom")


class _ProxyStub(_Stub):
    _proxy_delete_reply = True
    _proxy_get_reply = True


class _Api:
    def __init__(self):
        self.disconnect_calls = 0

    async def disconnect(self):
        self.disconnect_calls += 1


@pytest.mark.asyncio
async def test_run_main_async_dispatches_action_and_disconnects():
    stub = _Stub()
    result = await stub.run_main_async({"action": "post"})
    assert stub.executed_actions == ["post"]
    assert stub.api.disconnect_calls == 1
    assert result is None


@pytest.mark.asyncio
async def test_run_main_async_disconnects_on_action_failure():
    stub = _Stub()
    stub._fail_action = True
    with pytest.raises(Exception, match="boom"):
        await stub.run_main_async({"action": "post"})
    assert stub.api.disconnect_calls == 1


@pytest.mark.asyncio
async def test_run_main_async_authorize_returns_0_without_init():
    stub = _Stub()

    async def authorize():
        return True

    stub.authorize_credentials = authorize
    result = await stub.run_main_async({"action": "authorize"})
    assert result == 0
    assert stub.init_calls == 0


@pytest.mark.asyncio
async def test_run_main_async_authorize_failure_returns_1():
    stub = _Stub()

    async def authorize():
        return False

    stub.authorize_credentials = authorize
    result = await stub.run_main_async({"action": "authorize"})
    assert result == 1


@pytest.mark.asyncio
async def test_run_main_async_requires_action():
    stub = _Stub()
    with pytest.raises(Exception, match="Action is a required argument."):
        await stub.run_main_async({})


@pytest.mark.asyncio
async def test_require_api_raises_platform_message():
    stub = _Stub()
    with pytest.raises(Exception) as excinfo:
        stub._require_api()
    assert str(excinfo.value) == "_Stub API not initialized"


@pytest.mark.asyncio
async def test_require_api_passes_when_api_present():
    stub = _Stub()
    stub.api = object()
    stub._require_api()


@pytest.mark.asyncio
async def test_disconnect_delegates_to_api():
    stub = _Stub()
    api = _Api()
    stub.api = api
    await stub.disconnect()
    assert api.disconnect_calls == 1


@pytest.mark.asyncio
async def test_disconnect_noop_without_api():
    stub = _Stub()
    stub.api = None
    await stub.disconnect()


@pytest.mark.asyncio
async def test_authorize_credentials_default_raises_not_supported():
    stub = _Stub()
    with pytest.raises(Exception, match="Authorize not supported for _Stub"):
        await stub.authorize_credentials()


@pytest.mark.asyncio
async def test_delete_reply_default_raises_not_supported():
    stub = _Stub()
    with pytest.raises(Exception, match="Delete reply not supported for _Stub"):
        await stub.delete_reply("r1")


@pytest.mark.asyncio
async def test_get_reply_default_raises_not_supported():
    stub = _Stub()
    with pytest.raises(Exception, match="Get reply not supported for _Stub"):
        await stub.get_reply("r1")


@pytest.mark.asyncio
async def test_proxy_flag_delete_reply_delegates_to_delete():
    stub = _ProxyStub()
    assert await stub.delete_reply("r1") == "r1"


@pytest.mark.asyncio
async def test_proxy_flag_get_reply_delegates_to_get_post():
    stub = _ProxyStub()

    async def get_post(post_id):
        return {"id": post_id}

    stub.get_post = get_post
    assert await stub.get_reply("r1") == {"id": "r1"}


def test_entry_images_collects_image_fields():
    entry = {"image_1": "a", "image_2": "b", "image_3": None, "image_4": "d"}
    assert _entry_images(entry) == ["a", "b", "d"]


def test_entry_images_empty():
    assert _entry_images({}) == []


def test_is_uncertain_publish_error_classifies_timeouts():
    import asyncio

    assert _is_uncertain_publish_error(TimeoutError("timed out")) is True
    assert _is_uncertain_publish_error(asyncio.TimeoutError()) is True
    assert _is_uncertain_publish_error(ValueError("temporarily unavailable")) is True
    assert _is_uncertain_publish_error(ValueError("permanently failed")) is False


@pytest.mark.asyncio
async def test_run_main_async_teardown_failure_preserves_action_exception():
    stub = _Stub()

    class _FailingApi(_Api):
        async def disconnect(self):
            raise Exception("teardown boom")

    async def execute_action(action):
        stub.executed_actions.append(action)
        raise Exception("action boom")

    stub.execute_action = execute_action
    stub.api = _FailingApi()
    with pytest.raises(Exception, match="action boom"):
        await stub.run_main_async({"action": "post"})


@pytest.mark.asyncio
async def test_run_main_async_teardown_failure_keeps_success_result():
    stub = _Stub()

    class _FailingApi(_Api):
        async def disconnect(self):
            raise Exception("teardown boom")

    stub.api = _FailingApi()
    result = await stub.run_main_async({"action": "post"})
    assert result is None
    assert stub.executed_actions == ["post"]


@pytest.mark.asyncio
async def test_run_main_async_authorize_skips_teardown():
    stub = _Stub()
    api = _Api()
    stub.api = api

    async def authorize():
        return True

    stub.authorize_credentials = authorize
    result = await stub.run_main_async({"action": "authorize"})
    assert result == 0
    assert api.disconnect_calls == 0
    assert stub.init_calls == 0


def test_shim_pattern_end_to_end():
    """A real instance through a module-level shim (the wrapper pattern)."""

    async def main_async(kwargs):
        instance = _Stub(**kwargs)
        return await SocialNetwork.run_main_async(instance, kwargs)

    import asyncio

    result = asyncio.run(main_async({"action": "post"}))
    assert result is None
