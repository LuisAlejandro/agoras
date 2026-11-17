# -*- coding: utf-8 -*-
#
# Please refer to AUTHORS.rst for a complete list of Copyright holders.
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
"""Auth state machine: one derived state, fail-closed refresh, one writer."""

import asyncio
from unittest.mock import MagicMock, patch

import pytest

from agoras.core.api_base import AuthLifecycle, AuthState, BaseAPI
from agoras.core.auth import BaseAuthManager
from agoras.core.auth.exceptions import AuthenticationError
from agoras.core.auth.failure import AuthFailureCategory


class _StubAuthManager(BaseAuthManager):
    """Minimal auth manager: payload is set directly, no network."""

    def __init__(self, *, has_creds: bool = True):
        super().__init__()
        self._has_creds = has_creds

    async def authenticate(self) -> bool:
        self._begin_auth_attempt()
        if not self._has_creds:
            return self._missing_credentials_failed()
        self.access_token = "token"
        self.client = object()
        self.user_info = {"id": "1"}
        self._mark_authenticated()
        return True

    async def authorize(self):
        return None

    def _get_platform_name(self):
        return "stub"

    def _validate_credentials(self):
        return self._has_creds

    def _create_client(self, access_token):
        return object()

    def _get_token_identifier(self):
        return "stub-token"

    async def _get_user_info(self):
        return {"id": "1"}


class _StubAPI(BaseAPI):
    """Minimal concrete BaseAPI."""

    async def post(self, *args, **kwargs):
        return "post-1"

    async def like(self, post_id, *args, **kwargs):
        return post_id

    async def delete(self, post_id, *args, **kwargs):
        return post_id

    async def share(self, post_id, *args, **kwargs):
        return post_id


def test_auth_state_derives_from_the_payload():
    """The named state is a single view over token, client, and last failure."""
    manager = _StubAuthManager()
    assert manager._auth_state is AuthState.UNAUTHENTICATED
    assert manager.authenticated is False

    manager.access_token = "token"
    assert manager._auth_state is AuthState.UNAUTHENTICATED, "a token without a client is not authenticated"

    manager.client = object()
    assert manager._auth_state is AuthState.AUTHENTICATED
    assert manager.authenticated is True


def test_failure_is_a_state_and_a_new_attempt_clears_it():
    """FAILED is reachable and clearable; last_auth_failure has one writer."""
    manager = _StubAuthManager()
    assert manager._missing_credentials_failed() is False
    assert manager._auth_state is AuthState.FAILED
    assert manager.last_auth_failure.category is AuthFailureCategory.MISSING

    manager._begin_auth_attempt()
    assert manager._auth_state is AuthState.UNAUTHENTICATED
    assert manager.last_auth_failure is None


def test_mark_authenticated_rejects_an_incomplete_payload():
    """Reporting success without a client is a loud bug, not a silent lie."""
    manager = _StubAuthManager()
    manager.access_token = "token"
    with pytest.raises(RuntimeError, match="reported success without an access token and a client"):
        manager._mark_authenticated()


@pytest.mark.asyncio
@patch("agoras.core.auth.base.SecureTokenStorage")
async def test_storage_refresh_fails_closed_inside_a_running_loop(mock_storage_class):
    """A refresh that cannot run must not report success (previously returned True)."""
    storage = MagicMock()
    storage.load_token.return_value = {"refresh_token": "stored-refresh"}
    storage.seed_from_environment.return_value = False
    mock_storage_class.return_value = storage

    manager = _StubAuthManager()
    with patch.object(_StubAuthManager, "_load_refresh_token_from_storage", return_value="stored-refresh"):
        assert manager._load_and_refresh_from_storage() is False
    assert manager.authenticated is False


@pytest.mark.asyncio
@patch("agoras.core.auth.base.SecureTokenStorage")
async def test_ensure_authenticated_raises_when_refresh_cannot_run(mock_storage_class):
    """Fail-fast: the caller gets the categorized auth error, not a missing client."""
    storage = MagicMock()
    storage.load_token.return_value = {"refresh_token": "stored-refresh"}
    storage.seed_from_environment.return_value = False
    mock_storage_class.return_value = storage

    manager = _StubAuthManager()
    with patch.object(_StubAuthManager, "_load_refresh_token_from_storage", return_value="stored-refresh"):
        with pytest.raises(AuthenticationError):
            manager.ensure_authenticated()


def test_client_flag_is_derived_and_keeps_its_shim():
    """AuthLifecycle exposes _authenticated as a view, with a writable bridge."""
    lifecycle = AuthLifecycle()
    assert lifecycle._authenticated is False

    lifecycle._set_auth_state(AuthState.AUTHENTICATED)
    assert lifecycle._authenticated is True

    lifecycle._authenticated = False
    assert lifecycle._auth_state is AuthState.UNAUTHENTICATED


@pytest.mark.asyncio
async def test_disconnect_marks_unauthenticated_and_serializes_on_the_lock():
    """BaseAPI.disconnect() resets the state and actually takes the auth lock."""
    api = _StubAPI()
    api.client = MagicMock()
    api._set_auth_state(AuthState.AUTHENTICATED)
    assert isinstance(api._auth_lock, asyncio.Lock)

    await api._auth_lock.acquire()
    try:
        task = asyncio.create_task(api.disconnect())
        await asyncio.sleep(0)
        assert not task.done(), "disconnect() must wait for the auth lock"
    finally:
        api._auth_lock.release()

    await asyncio.wait_for(task, timeout=5)
    assert api._authenticated is False
    assert api.client is None
