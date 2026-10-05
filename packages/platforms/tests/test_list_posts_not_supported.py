# -*- coding: utf-8 -*-
#
# Please refer to AUTHORS.rst for a complete list of Copyright holders.
# Copyright (C) 2022-2026, Agoras Developers.

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""
Tests that TikTok, Telegram, and WhatsApp raise not-supported for list-posts.
"""

from unittest.mock import AsyncMock

import pytest

from agoras.platforms.telegram.wrapper import Telegram
from agoras.platforms.tiktok.wrapper import TikTok
from agoras.platforms.whatsapp.wrapper import WhatsApp


@pytest.mark.asyncio
async def test_tiktok_list_posts_not_supported():
    wrapper = TikTok()
    wrapper._initialize_client = AsyncMock()

    with pytest.raises(Exception, match="List posts not supported"):
        await wrapper.execute_action("list-posts")


@pytest.mark.asyncio
async def test_telegram_list_posts_not_supported():
    wrapper = Telegram()
    wrapper._initialize_client = AsyncMock()

    with pytest.raises(Exception, match="List posts not supported"):
        await wrapper.execute_action("list-posts")


@pytest.mark.asyncio
async def test_whatsapp_list_posts_not_supported():
    """WhatsApp override has no list-posts key → action not supported."""
    wrapper = WhatsApp()
    wrapper._initialize_client = AsyncMock()

    with pytest.raises(Exception, match='"list-posts" action not supported'):
        await wrapper.execute_action("list-posts")
