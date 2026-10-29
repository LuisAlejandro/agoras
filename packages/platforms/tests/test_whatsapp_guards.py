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
"""Committed guard-behavior assertions for WhatsAppAPI (U8).

The existing whatsapp test suite runs authenticated fixtures, so guard
behavior is invisible to it. These tests pin the unauthenticated paths:
the auth-manager-ensure dialect, the client-presence check, and
guard-phase error propagation.
"""

import pytest

from agoras.core.auth.exceptions import AuthenticationError
from agoras.platforms.whatsapp.api import WhatsAppAPI


class _FailingAuthManager:
    """Auth manager whose ensure_authenticated raises the categorized error."""

    access_token = "stale-token"
    client = None

    def ensure_authenticated(self):
        raise AuthenticationError("WhatsApp token expired")


class _OkAuthManager:
    """Auth manager whose ensure_authenticated succeeds, with a token."""

    access_token = "valid-token"
    client = None

    def ensure_authenticated(self):
        pass


class _WhatsAppClientStub:
    """Sync client stub for the to_thread closures."""

    def send_message(self, to, text, buttons=None, context=None):
        return {"message_id": "msg-1"}


def _make_api(auth_manager=None):
    api = WhatsAppAPI("access_token", "phone_number_id", "business_account_id")
    api.auth_manager = auth_manager
    api.client = None
    api._authenticated = False
    return api


@pytest.mark.asyncio
async def test_send_message_no_credentials_raises_categorized_auth_error():
    api = _make_api(auth_manager=_FailingAuthManager())
    with pytest.raises(AuthenticationError):
        await api.send_message("+1234567890", "Test message")


@pytest.mark.asyncio
async def test_send_message_no_client_raises_not_authenticated():
    api = _make_api(auth_manager=_OkAuthManager())
    with pytest.raises(Exception) as excinfo:
        await api.send_message("+1234567890", "Test message")
    assert str(excinfo.value) == "WhatsApp API not authenticated"


@pytest.mark.asyncio
async def test_send_message_guard_errors_propagate_unwrapped():
    api = _make_api(auth_manager=_FailingAuthManager())
    with pytest.raises(AuthenticationError) as excinfo:
        await api.send_message("+1234567890", "Test message")
    # Guard-phase errors must not be wrapped into a generic exception
    assert not str(excinfo.value).startswith("WhatsApp send_message failed")


@pytest.mark.asyncio
async def test_authenticated_with_client_passes():
    api = _make_api(auth_manager=_OkAuthManager())
    api.client = _WhatsAppClientStub()
    result = await api.send_message("+1234567890", "Test message")
    assert result == "msg-1"
