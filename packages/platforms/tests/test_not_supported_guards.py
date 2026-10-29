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
"""Pin the guard-skip on all fifteen not-supported platform methods (U9).

Every platform API was migrated to guard decorators, but not-supported
methods must stay guard-free: they raise their not-supported message with
NO auth attempt, NO rate-limit wait, and NO error wrap. Each API is built
with a mocked auth manager whose ``ensure_authenticated`` raises the
categorized ``AuthenticationError``, ``_authenticated=False`` and
``client=None`` — any guard leak would surface a different message.
"""

import pytest

from agoras.core.auth.exceptions import AuthenticationError
from agoras.platforms.discord.api import DiscordAPI
from agoras.platforms.instagram.api import InstagramAPI
from agoras.platforms.telegram.api import TelegramAPI
from agoras.platforms.threads.api import ThreadsAPI
from agoras.platforms.tiktok.api import TikTokAPI
from agoras.platforms.whatsapp.api import WhatsAppAPI
from agoras.platforms.youtube.api import YouTubeAPI


class _FailingAuthManager:
    """Auth manager whose ensure_authenticated raises the categorized error."""

    def ensure_authenticated(self):
        raise AuthenticationError("credentials unavailable")


def _make_api(api_class, *credentials):
    api = api_class(*credentials)
    api.auth_manager = _FailingAuthManager()
    api.client = None
    api._authenticated = False
    return api


NOT_SUPPORTED = {
    ("tiktok", "post"): (
        lambda: _make_api(TikTokAPI, "testuser", "client_key", "client_secret", "refresh_token"),
        "Regular posts not supported for TikTok - use upload_photo() method instead",
    ),
    ("tiktok", "like"): (
        lambda: _make_api(TikTokAPI, "testuser", "client_key", "client_secret", "refresh_token"),
        "Like not supported for TikTok",
    ),
    ("tiktok", "delete"): (
        lambda: _make_api(TikTokAPI, "testuser", "client_key", "client_secret", "refresh_token"),
        "Delete not supported for TikTok",
    ),
    ("tiktok", "share"): (
        lambda: _make_api(TikTokAPI, "testuser", "client_key", "client_secret", "refresh_token"),
        "Share not supported for TikTok",
    ),
    ("discord", "share"): (
        lambda: _make_api(DiscordAPI, "bot_token", "Server Name", "channel-name"),
        "Share not supported for Discord",
    ),
    ("telegram", "like"): (
        lambda: _make_api(TelegramAPI, "bot_token", "chat_id"),
        "Like not supported for Telegram",
    ),
    ("telegram", "share"): (
        lambda: _make_api(TelegramAPI, "bot_token", "chat_id"),
        "Share not supported for Telegram",
    ),
    ("instagram", "like"): (
        lambda: _make_api(InstagramAPI, "user_id", "client_id", "client_secret"),
        "Like not supported for Instagram",
    ),
    ("instagram", "share"): (
        lambda: _make_api(InstagramAPI, "user_id", "client_id", "client_secret"),
        "Share not supported for Instagram",
    ),
    ("threads", "like"): (
        lambda: _make_api(ThreadsAPI, "app_id", "app_secret", "refresh_token"),
        "Like not supported for Threads",
    ),
    ("whatsapp", "like"): (
        lambda: _make_api(WhatsAppAPI, "access_token", "phone_number_id", "business_account_id"),
        "Like not supported for WhatsApp",
    ),
    ("whatsapp", "delete"): (
        lambda: _make_api(WhatsAppAPI, "access_token", "phone_number_id", "business_account_id"),
        "Delete not supported for WhatsApp",
    ),
    ("whatsapp", "share"): (
        lambda: _make_api(WhatsAppAPI, "access_token", "phone_number_id", "business_account_id"),
        "Share not supported for WhatsApp",
    ),
    ("youtube", "post"): (
        lambda: _make_api(YouTubeAPI, "client_id", "client_secret"),
        "Regular posts not supported for YouTube - use upload_video() method instead",
    ),
    ("youtube", "share"): (
        lambda: _make_api(YouTubeAPI, "client_id", "client_secret"),
        "Share not supported for YouTube",
    ),
}


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "platform,method,factory,message",
    [(platform, method, factory, message) for (platform, method), (factory, message) in NOT_SUPPORTED.items()],
    ids=[f"{platform}-{method}" for platform, method in NOT_SUPPORTED],
)
async def test_not_supported_methods_skip_guards(platform, method, factory, message):
    api = factory()
    with pytest.raises(Exception) as excinfo:
        await getattr(api, method)("x")
    assert str(excinfo.value) == message
    assert not isinstance(excinfo.value, AuthenticationError)
