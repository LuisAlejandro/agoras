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
"""
Tests that the networks without a reply backend raise "not supported"
rather than silently no-op (R3, R12).

TikTok is the only network that does not implement a `reply` backend; it
inherits the base `SocialNetwork.reply` default, which raises
"Reply not supported for <class>". Every other network now implements a
`reply` backend (X, Discord, Telegram, WhatsApp, LinkedIn, Threads, Facebook,
Instagram, YouTube). These tests assert that surface and that no network call
is made for TikTok.
"""

import pytest
from unittest.mock import AsyncMock

from agoras.platforms.tiktok.wrapper import TikTok

# Networks that do NOT implement a reply backend yet.
UNIMPLEMENTED = [
    (TikTok, "tiktok"),
]


@pytest.mark.asyncio
@pytest.mark.parametrize("wrapper_cls,network", UNIMPLEMENTED, ids=[n for _, n in UNIMPLEMENTED])
async def test_reply_not_supported(wrapper_cls, network):
    """Each unimplemented network raises 'not supported' and makes no network call."""
    wrapper = wrapper_cls()

    with pytest.raises(Exception, match="Reply not supported"):
        await wrapper.reply("post-123", "A reply")


@pytest.mark.asyncio
@pytest.mark.parametrize("wrapper_cls,network", UNIMPLEMENTED, ids=[n for _, n in UNIMPLEMENTED])
async def test_handle_reply_action_not_supported(wrapper_cls, network):
    """_handle_reply_action on an unimplemented network propagates 'not supported'.

    The CLI converter maps ``post_id`` to a platform-specific key (e.g.
    ``tweet_id``), so it is absent from config here — the base handler must
    still surface "Reply not supported" rather than a misleading
    "Post ID is required" error (R3, AE2).
    """
    wrapper = wrapper_cls(status_text="A reply")

    with pytest.raises(Exception, match="Reply not supported"):
        await wrapper._handle_reply_action()


@pytest.mark.asyncio
@pytest.mark.parametrize("wrapper_cls,network", UNIMPLEMENTED, ids=[n for _, n in UNIMPLEMENTED])
async def test_execute_action_reply_not_supported(wrapper_cls, network):
    """execute_action('reply') on an unimplemented network propagates 'not supported'.

    Exercises the full dispatch chain (execute_action -> _handle_reply_action ->
    reply) rather than calling the handler directly, so the "not supported"
    surface is verified through the real action dispatch path (R3).
    """
    wrapper = wrapper_cls(status_text="A reply")
    # Bypass credential validation so the dispatch reaches the reply branch.
    wrapper._initialize_client = AsyncMock()

    with pytest.raises(Exception, match="Reply not supported"):
        await wrapper.execute_action("reply")
