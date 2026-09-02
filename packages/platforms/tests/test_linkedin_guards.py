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
"""Committed guard-behavior assertions for LinkedInAPI (U5, auth-manager-ensure dialect).

The existing linkedin suite runs authenticated fixtures, so guard behavior is
invisible to it. These tests pin the unauthenticated path: the auth-manager
ensure raises the categorized AuthenticationError unwrapped, and the
client-check-only exception methods (like, reply, share, delete, delete_reply)
raise linkedin's not-authenticated template without invoking ensure.
"""

import pytest

from agoras.core.auth.exceptions import AuthenticationError
from agoras.platforms.linkedin.api import LinkedInAPI


class _FailingAuthManager:
    """Auth manager whose ensure_authenticated raises the categorized error."""

    access_token = None
    user_info = {"object_id": "user_id"}
    client = None

    def ensure_authenticated(self):
        raise AuthenticationError("LinkedIn token expired")


class _OkAuthManager:
    """Auth manager whose ensure_authenticated succeeds, with a token."""

    access_token = "valid-token"
    user_info = {"object_id": "user_id"}
    client = None

    def ensure_authenticated(self):
        pass


class _TrackingAuthManager:
    """Auth manager that records whether ensure_authenticated was invoked."""

    access_token = "valid-token"
    user_info = {"object_id": "user_id"}
    client = None
    ensure_calls = 0

    def ensure_authenticated(self):
        self.ensure_calls += 1


def _make_api(auth_manager=None):
    api = LinkedInAPI("user_id", "client_id", "client_secret", "refresh_token")
    api.auth_manager = auth_manager
    api.client = None
    api._authenticated = False
    return api


class _StubClient:
    async def create_post(
        self,
        author_urn,
        text,
        link=None,
        link_title=None,
        link_description=None,
        image_ids=None,
        video_id=None,
        video_title=None,
    ):
        return "post-123"

    async def like_post(self, post_id, actor_urn):
        return "like-123"


@pytest.mark.asyncio
async def test_post_no_credentials_raises_categorized_auth_error():
    api = _make_api(auth_manager=_FailingAuthManager())
    with pytest.raises(AuthenticationError):
        await api.post("Test post content")


@pytest.mark.asyncio
async def test_post_guard_errors_propagate_unwrapped():
    api = _make_api(auth_manager=_FailingAuthManager())
    with pytest.raises(AuthenticationError) as excinfo:
        await api.post("Test post content")
    # Guard-phase errors must not be wrapped into a generic exception
    assert not str(excinfo.value).startswith("LinkedIn post creation failed")


@pytest.mark.asyncio
async def test_post_no_client_raises_not_authenticated():
    api = _make_api(auth_manager=_OkAuthManager())
    with pytest.raises(Exception) as excinfo:
        await api.post("Test post content")
    assert str(excinfo.value) == "LinkedIn API not authenticated"


@pytest.mark.asyncio
async def test_client_check_only_methods_raise_without_ensure():
    api = _make_api(auth_manager=_TrackingAuthManager())
    for method, args in [
        ("like", ("post-1",)),
        ("reply", ("post-1", "A comment")),
        ("share", ("post-1",)),
        ("delete", ("post-1",)),
        ("delete_reply", ("comment-1", "post-1")),
    ]:
        with pytest.raises(Exception) as excinfo:
            await getattr(api, method)(*args)
        assert str(excinfo.value) == "LinkedIn API not authenticated"
        assert api.auth_manager.ensure_calls == 0


@pytest.mark.asyncio
async def test_like_without_object_id_raises_not_authenticated():
    api = _make_api(auth_manager=_OkAuthManager())
    api.auth_manager.user_info = None
    api.client = _StubClient()
    with pytest.raises(Exception) as excinfo:
        await api.like("post-1")
    assert str(excinfo.value) == "LinkedIn API not authenticated"


@pytest.mark.asyncio
async def test_authenticated_with_client_passes():
    api = _make_api(auth_manager=_OkAuthManager())
    api.client = _StubClient()
    result = await api.post("Test post content")
    assert result == "post-123"


@pytest.mark.asyncio
async def test_like_with_client_and_object_id_passes():
    api = _make_api(auth_manager=_OkAuthManager())
    api.client = _StubClient()
    result = await api.like("post-1")
    assert result == "like-123"
