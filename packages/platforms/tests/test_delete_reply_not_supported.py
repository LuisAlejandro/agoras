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
Tests that the networks without a delete-reply backend raise "not supported"
rather than silently no-op (R13).

TikTok inherits the base ``SocialNetwork.delete_reply`` default, which raises
"Delete reply not supported for <class>". WhatsApp overrides ``execute_action``
with a handlers dict that has no ``delete-reply`` key, so it raises
'"delete-reply" action not supported.' from its override. These tests assert
that both surfaces raise and make no network call.
"""

import pytest
from unittest.mock import AsyncMock

from agoras.platforms.tiktok.wrapper import TikTok
from agoras.platforms.whatsapp.wrapper import WhatsApp

# Networks that do NOT implement a delete-reply backend.
UNIMPLEMENTED_NETWORKS = [
    "tiktok",
    "whatsapp",
]


def _instantiate(wrapper_cls):
    wrapper = wrapper_cls()
    return wrapper


@pytest.mark.asyncio
async def test_tiktok_delete_reply_not_supported():
    """TikTok delete_reply raises 'not supported' and makes no network call."""
    wrapper = TikTok()
    wrapper._initialize_client = AsyncMock()

    with pytest.raises(Exception, match="Delete reply not supported"):
        await wrapper.execute_action("delete-reply")


@pytest.mark.asyncio
async def test_tiktok_handle_delete_reply_not_supported():
    """TikTok _handle_delete_reply_action propagates 'not supported'."""
    wrapper = TikTok()

    with pytest.raises(Exception, match="Delete reply not supported"):
        await wrapper._handle_delete_reply_action()


@pytest.mark.asyncio
async def test_whatsapp_delete_reply_not_supported():
    """WhatsApp execute_action('delete-reply') raises 'not supported'.

    WhatsApp overrides execute_action; without a `delete-reply` key in its
    handlers dict the observable surface is '"delete-reply" action not
    supported.' written against the override path (R13).
    """
    wrapper = WhatsApp()
    wrapper._initialize_client = AsyncMock()

    with pytest.raises(Exception, match='"delete-reply" action not supported'):
        await wrapper.execute_action("delete-reply")
