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
"""Committed guard-behavior assertions for YouTubeAPI (U8).

The existing youtube test suite runs authenticated fixtures, so guard
behavior is invisible to it. These tests pin the unauthenticated paths:
the auth-manager-ensure dialect, the client-presence check, guard-phase
error propagation, and delete's client-check-only exception (no ensure).
"""

import pytest

from agoras.core.auth.exceptions import AuthenticationError
from agoras.platforms.youtube.api import YouTubeAPI


class _FailingAuthManager:
    """Auth manager whose ensure_authenticated raises the categorized error."""

    access_token = "stale-token"
    client = None

    def ensure_authenticated(self):
        raise AuthenticationError("YouTube token expired")


class _SpyAuthManager:
    """Auth manager that records ensure_authenticated calls."""

    access_token = "stale-token"
    client = None
    ensure_calls = 0

    def ensure_authenticated(self):
        self.ensure_calls += 1
        raise AuthenticationError("YouTube token expired")


class _OkAuthManager:
    """Auth manager whose ensure_authenticated succeeds, with a token."""

    access_token = "valid-token"
    client = None

    def ensure_authenticated(self):
        pass


class _YouTubeClientStub:
    """Async client stub for direct client calls."""

    async def upload_video(self, **kwargs):
        return {"id": "video-1"}

    async def delete_video(self, video_id):
        return None


def _make_api(auth_manager=None):
    api = YouTubeAPI("client_id", "client_secret")
    api.auth_manager = auth_manager
    api.client = None
    api._authenticated = False
    return api


@pytest.mark.asyncio
async def test_upload_video_no_credentials_raises_categorized_auth_error():
    api = _make_api(auth_manager=_FailingAuthManager())
    with pytest.raises(AuthenticationError):
        await api.upload_video(
            video_file_path="/path/to/video.mp4",
            title="title",
            description="description",
            category_id="22",
            privacy_status="public",
        )


@pytest.mark.asyncio
async def test_upload_video_no_client_raises_not_authenticated():
    api = _make_api(auth_manager=_OkAuthManager())
    with pytest.raises(Exception) as excinfo:
        await api.upload_video(
            video_file_path="/path/to/video.mp4",
            title="title",
            description="description",
            category_id="22",
            privacy_status="public",
        )
    assert str(excinfo.value) == "YouTube API not authenticated"


@pytest.mark.asyncio
async def test_upload_video_guard_errors_propagate_unwrapped():
    api = _make_api(auth_manager=_FailingAuthManager())
    with pytest.raises(AuthenticationError) as excinfo:
        await api.upload_video(
            video_file_path="/path/to/video.mp4",
            title="title",
            description="description",
            category_id="22",
            privacy_status="public",
        )
    # Guard-phase errors must not be wrapped into a generic exception
    assert not str(excinfo.value).startswith("YouTube video upload failed")


@pytest.mark.asyncio
async def test_delete_is_client_check_only():
    """delete raises on missing client with no ensure."""
    api = _make_api(auth_manager=_SpyAuthManager())
    with pytest.raises(Exception) as excinfo:
        await api.delete("video-1")
    assert str(excinfo.value) == "YouTube API not authenticated"
    assert api.auth_manager.ensure_calls == 0


@pytest.mark.asyncio
async def test_authenticated_with_client_passes():
    api = _make_api(auth_manager=_OkAuthManager())
    api.client = _YouTubeClientStub()
    result = await api.upload_video(
        video_file_path="/path/to/video.mp4",
        title="title",
        description="description",
        category_id="22",
        privacy_status="public",
    )
    assert result == {"id": "video-1"}
    await api.delete("video-1")
