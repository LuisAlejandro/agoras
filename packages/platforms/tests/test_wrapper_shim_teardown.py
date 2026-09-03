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
"""Per-platform failure-path teardown pins for the wrapper skeleton hoist.

The base template guarantees ``disconnect`` on every action-path exit for
the nine shimmed wrappers — six platforms (facebook, instagram, linkedin,
tiktok, youtube, telegram) historically disconnected only on success. These
tests pin the accepted, documented deviation. whatsapp keeps its own runner,
which does NOT disconnect on action failure — pinned separately.
"""

import importlib

import pytest
from unittest.mock import AsyncMock, patch

SHIMMED_PLATFORMS = [
    ("x", "X"),
    ("discord", "Discord"),
    ("telegram", "Telegram"),
    ("threads", "Threads"),
    ("facebook", "Facebook"),
    ("instagram", "Instagram"),
    ("linkedin", "LinkedIn"),
    ("youtube", "YouTube"),
    ("tiktok", "TikTok"),
]


@pytest.mark.asyncio
@pytest.mark.parametrize("platform,class_name", SHIMMED_PLATFORMS)
async def test_shim_disconnects_on_action_failure(platform, class_name):
    wrapper = importlib.import_module(f"agoras.platforms.{platform}.wrapper")
    cls = getattr(wrapper, class_name)

    with patch.object(cls, "execute_action", AsyncMock(side_effect=Exception("boom"))), patch.object(
        cls, "disconnect", AsyncMock()
    ) as disconnect:
        with pytest.raises(Exception, match="boom"):
            await wrapper.main_async({"action": "post"})
        disconnect.assert_awaited_once()


@pytest.mark.asyncio
async def test_whatsapp_runner_does_not_disconnect_on_failure():
    """whatsapp's kept runner skips teardown on failure (two-tier contract)."""
    from agoras.platforms.whatsapp.wrapper import WhatsApp, main_async

    with patch.object(WhatsApp, "execute_action", AsyncMock(side_effect=Exception("boom"))), patch.object(
        WhatsApp, "disconnect", AsyncMock()
    ) as disconnect:
        with pytest.raises(Exception, match="boom"):
            await main_async({"action": "post"})
        disconnect.assert_not_awaited()