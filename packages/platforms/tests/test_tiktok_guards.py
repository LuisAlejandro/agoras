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
"""Committed guard-behavior assertions for TikTokAPI (U3 pilot).

The existing tiktok test suite runs authenticated fixtures, so guard
behavior is invisible to it. These tests pin the unauthenticated paths:
the auth-manager-ensure dialect, the token-presence check, the
client-presence check, and guard-phase error propagation.
"""

import pytest

from agoras.core.auth.exceptions import AuthenticationError
from agoras.platforms.tiktok.api import TikTokAPI


class _FailingAuthManager:
    """Auth manager whose ensure_authenticated raises the categorized error."""

    access_token = None
    username = "testuser"
    user_info = None
    client = None

    def ensure_authenticated(self):
        raise AuthenticationError("TikTok token expired")


class _OkAuthManager:
    """Auth manager whose ensure_authenticated succeeds, with a token."""

    access_token = "valid-token"
    username = "testuser"
    user_info = None
    client = None

    def ensure_authenticated(self):
        pass


def _make_api(auth_manager=None):
    api = TikTokAPI("testuser", "client_key", "client_secret", "refresh_token")
    api.auth_manager = auth_manager
    api.client = None
    api._authenticated = False
    return api


@pytest.mark.asyncio
async def test_upload_video_no_credentials_raises_categorized_auth_error():
    api = _make_api(auth_manager=_FailingAuthManager())
    with pytest.raises(AuthenticationError):
        await api.upload_video(
            video_url="https://example.com/v.mp4",
            title="title",
            privacy_status="SELF_ONLY",
        )


@pytest.mark.asyncio
async def test_upload_video_no_token_raises_not_authenticated():
    api = _make_api(auth_manager=_FailingAuthManager())
    # ensure passes but token is missing on the manager
    api.auth_manager = _OkAuthManager()
    api.auth_manager.access_token = None
    with pytest.raises(Exception) as excinfo:
        await api.upload_video(
            video_url="https://example.com/v.mp4",
            title="title",
            privacy_status="SELF_ONLY",
        )
    assert str(excinfo.value) == "TikTok API not authenticated"


@pytest.mark.asyncio
async def test_upload_video_no_client_raises_not_available():
    api = _make_api(auth_manager=_OkAuthManager())
    with pytest.raises(Exception) as excinfo:
        await api.upload_video(
            video_url="https://example.com/v.mp4",
            title="title",
            privacy_status="SELF_ONLY",
        )
    assert str(excinfo.value) == "TikTok client not available"


@pytest.mark.asyncio
async def test_upload_video_guard_errors_propagate_unwrapped():
    api = _make_api(auth_manager=_FailingAuthManager())
    with pytest.raises(AuthenticationError) as excinfo:
        await api.upload_video(
            video_url="https://example.com/v.mp4",
            title="title",
            privacy_status="SELF_ONLY",
        )
    # Guard-phase errors must not be wrapped into a generic exception
    assert not str(excinfo.value).startswith("TikTok video upload failed")


@pytest.mark.asyncio
async def test_refresh_creator_info_ensure_invoked():
    api = _make_api(auth_manager=_FailingAuthManager())
    with pytest.raises(AuthenticationError):
        await api.refresh_creator_info()


@pytest.mark.asyncio
async def test_not_supported_methods_raise_without_guards():
    api = _make_api(auth_manager=_FailingAuthManager())
    with pytest.raises(Exception) as excinfo:
        await api.post("x")
    assert str(excinfo.value) == "Regular posts not supported for TikTok - use upload_photo() method instead"

    with pytest.raises(Exception) as excinfo:
        await api.like("x")
    assert str(excinfo.value) == "Like not supported for TikTok"

    with pytest.raises(Exception) as excinfo:
        await api.delete("x")
    assert str(excinfo.value) == "Delete not supported for TikTok"

    with pytest.raises(Exception) as excinfo:
        await api.share("x")
    assert str(excinfo.value) == "Share not supported for TikTok"
