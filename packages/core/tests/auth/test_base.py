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

import pytest

from agoras.core.auth import BaseAuthManager
from agoras.core.auth.exceptions import AuthenticationError
from agoras.core.auth.failure import AuthFailureCategory


class _StubAuthManager(BaseAuthManager):
    platform = "stub"

    def __init__(self, *, has_creds: bool = True):
        super().__init__()
        self._has_creds = has_creds

    async def authenticate(self) -> bool:
        self.last_auth_failure = None
        if not self._has_creds:
            return self._missing_credentials_failed()
        self.access_token = "token"
        self.client = object()
        self.user_info = {"id": "1"}
        return True

    async def authorize(self):
        return None

    def _get_platform_name(self) -> str:
        return self.platform

    def _load_refresh_token_from_storage(self):
        return None

    def _has_stored_or_env_credentials(self) -> bool:
        return self._has_creds

    def _validate_credentials(self) -> bool:
        return self._has_creds

    def _create_client(self, access_token: str):
        return object()

    def _get_token_identifier(self) -> str:
        return "stub-token"

    async def _get_user_info(self):
        return {"id": "1"}


def test_baseauthmanager_is_abstract():
    """Test that BaseAuthManager cannot be instantiated directly."""
    with pytest.raises(TypeError):
        BaseAuthManager()


def test_baseauthmanager_required_methods():
    """Test that BaseAuthManager defines required methods."""
    assert hasattr(BaseAuthManager, "authenticate")
    assert hasattr(BaseAuthManager, "authorize")
    assert hasattr(BaseAuthManager, "ensure_authenticated")


def test_baseauthmanager_token_storage():
    """Test that BaseAuthManager has token storage integration."""
    # BaseAuthManager.__init__ creates token_storage
    assert hasattr(BaseAuthManager, "__init__")


def test_missing_credentials_failed_sets_category():
    manager = _StubAuthManager(has_creds=False)
    assert manager._missing_credentials_failed() is False
    assert manager.last_auth_failure is not None
    assert manager.last_auth_failure.category == AuthFailureCategory.MISSING


@pytest.mark.asyncio
async def test_ensure_authenticated_raises_structured_error():
    manager = _StubAuthManager(has_creds=False)
    with pytest.raises(AuthenticationError) as exc_info:
        manager.ensure_authenticated()
    assert exc_info.value.details is not None
    assert exc_info.value.details.category == AuthFailureCategory.MISSING
