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
Tests that TikTok, Telegram, and WhatsApp raise not-supported for get-post/get-reply.
"""

from unittest.mock import AsyncMock

import pytest

from agoras.platforms.telegram.wrapper import Telegram
from agoras.platforms.tiktok.wrapper import TikTok
from agoras.platforms.whatsapp.wrapper import WhatsApp


@pytest.mark.asyncio
async def test_tiktok_get_post_not_supported():
    wrapper = TikTok()
    wrapper._initialize_client = AsyncMock()

    with pytest.raises(Exception, match="Get post not supported"):
        await wrapper.execute_action("get-post")


@pytest.mark.asyncio
async def test_tiktok_get_reply_not_supported():
    wrapper = TikTok()
    wrapper._initialize_client = AsyncMock()

    with pytest.raises(Exception, match="Get reply not supported"):
        await wrapper.execute_action("get-reply")


@pytest.mark.asyncio
async def test_telegram_get_post_not_supported():
    wrapper = Telegram()
    wrapper._initialize_client = AsyncMock()

    with pytest.raises(Exception, match="Get post not supported"):
        await wrapper.execute_action("get-post")


@pytest.mark.asyncio
async def test_telegram_get_reply_not_supported():
    wrapper = Telegram()
    wrapper._initialize_client = AsyncMock()

    with pytest.raises(Exception, match="Get reply not supported"):
        await wrapper.execute_action("get-reply")


@pytest.mark.asyncio
async def test_whatsapp_get_post_not_supported():
    """WhatsApp override has no get-post key → action not supported."""
    wrapper = WhatsApp()
    wrapper._initialize_client = AsyncMock()

    with pytest.raises(Exception, match="Get post not supported"):
        await wrapper.execute_action("get-post")


@pytest.mark.asyncio
async def test_whatsapp_get_reply_not_supported():
    """WhatsApp delegates get-reply to base SocialNetwork default."""
    wrapper = WhatsApp()
    wrapper._initialize_client = AsyncMock()

    with pytest.raises(Exception, match="Get reply not supported"):
        await wrapper.execute_action("get-reply")
