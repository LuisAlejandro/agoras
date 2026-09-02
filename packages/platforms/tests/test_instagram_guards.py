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
"""Committed guard-behavior assertions for InstagramAPI (U5, auth-manager-ensure dialect).

The existing instagram suite runs authenticated fixtures, so guard behavior is
invisible to it. These tests pin the unauthenticated path: the auth-manager
ensure raises the categorized AuthenticationError unwrapped, and the
client-check-only exception methods (create_carousel, publish_media) raise
instagram's not-authenticated template without invoking ensure.
"""

import pytest

from agoras.core.auth.exceptions import AuthenticationError
from agoras.platforms.instagram.api import InstagramAPI


class _FailingAuthManager:
    """Auth manager whose ensure_authenticated raises the categorized error."""

    access_token = None
    user_info = None
    client = None

    def ensure_authenticated(self):
        raise AuthenticationError("Instagram token expired")


class _OkAuthManager:
    """Auth manager whose ensure_authenticated succeeds, with a token."""

    access_token = "valid-token"
    user_info = None
    client = None

    def ensure_authenticated(self):
        pass


class _TrackingAuthManager:
    """Auth manager that records whether ensure_authenticated was invoked."""

    access_token = "valid-token"
    user_info = None
    client = None
    ensure_calls = 0

    def ensure_authenticated(self):
        self.ensure_calls += 1


def _make_api(auth_manager=None):
    api = InstagramAPI("user_id", "client_id", "client_secret")
    api.auth_manager = auth_manager
    api.client = None
    api._authenticated = False
    return api


class _StubClient:
    async def create_post(self, object_id, image_url=None, video_url=None, caption=None):
        return "media-123"


@pytest.mark.asyncio
async def test_post_no_credentials_raises_categorized_auth_error():
    api = _make_api(auth_manager=_FailingAuthManager())
    with pytest.raises(AuthenticationError):
        await api.post("user_id", image_url="http://image.jpg")


@pytest.mark.asyncio
async def test_post_guard_errors_propagate_unwrapped():
    api = _make_api(auth_manager=_FailingAuthManager())
    with pytest.raises(AuthenticationError) as excinfo:
        await api.post("user_id", image_url="http://image.jpg")
    # Guard-phase errors must not be wrapped into a generic exception
    assert not str(excinfo.value).startswith("Instagram post creation failed")


@pytest.mark.asyncio
async def test_post_no_client_raises_not_authenticated():
    api = _make_api(auth_manager=_OkAuthManager())
    with pytest.raises(Exception) as excinfo:
        await api.post("user_id", image_url="http://image.jpg")
    assert str(excinfo.value) == "Instagram API not authenticated"


@pytest.mark.asyncio
async def test_create_carousel_client_check_only_without_ensure():
    api = _make_api(auth_manager=_TrackingAuthManager())
    with pytest.raises(Exception) as excinfo:
        await api.create_carousel("user_id", ["media-1", "media-2"])
    assert str(excinfo.value) == "Instagram API not authenticated"
    assert api.auth_manager.ensure_calls == 0


@pytest.mark.asyncio
async def test_publish_media_client_check_only_without_ensure():
    api = _make_api(auth_manager=_TrackingAuthManager())
    with pytest.raises(Exception) as excinfo:
        await api.publish_media("user_id", "container-123")
    assert str(excinfo.value) == "Instagram API not authenticated"
    assert api.auth_manager.ensure_calls == 0


@pytest.mark.asyncio
async def test_authenticated_with_client_passes():
    api = _make_api(auth_manager=_OkAuthManager())
    api.client = _StubClient()
    result = await api.post("user_id", image_url="http://image.jpg", caption="Caption")
    assert result == "media-123"
