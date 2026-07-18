# -*- coding: utf-8 -*-
#
# Please refer to AUTHORS.md for a complete list of Copyright holders.
# Copyright (C) 2022-2026, Agoras Developers.

"""Focused reject-before-API text limit tests for platform wrappers."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from agoras.core.text_limits import TextValidationError
from agoras.platforms.instagram.wrapper import Instagram
from agoras.platforms.telegram.wrapper import Telegram
from agoras.platforms.youtube.wrapper import YouTube


@pytest.mark.asyncio
async def test_instagram_rejects_caption_over_2200():
    ig = Instagram(instagram_access_token="t", instagram_object_id="oid")
    ig.api = MagicMock()
    ig.instagram_object_id = "oid"

    with pytest.raises(TextValidationError) as exc:
        await ig.post("x" * 2201, "", status_image_url_1="https://example.com/a.jpg")
    assert exc.value.field == "caption"
    ig.api.create_media.assert_not_called()


@pytest.mark.asyncio
async def test_telegram_text_allows_2000_but_caption_rejects():
    tg = Telegram(telegram_bot_token="tok", telegram_chat_id="chat")
    tg.api = MagicMock()
    tg.api.send_message = AsyncMock(return_value="m1")
    tg.api.send_photo = AsyncMock(return_value="m2")
    tg.telegram_chat_id = "chat"
    tg.telegram_parse_mode = None

    longish = "a" * 2000
    with patch.object(tg, "_output_status"):
        await tg.post(longish, "")
    tg.api.send_message.assert_called_once()

    with pytest.raises(TextValidationError) as exc:
        await tg.post(longish, "", status_image_url_1="https://example.com/a.jpg")
    assert exc.value.field == "caption"
    assert exc.value.limit == 1024


@pytest.mark.asyncio
async def test_youtube_rejects_title_over_100():
    yt = YouTube(youtube_client_id="id", youtube_client_secret="sec", youtube_refresh_token="ref")
    yt.api = MagicMock()
    yt.api.upload_video = AsyncMock()

    with pytest.raises(TextValidationError) as exc:
        await yt.video("desc", "https://example.com/v.mp4", "T" * 101)
    assert exc.value.field == "title"
    yt.api.upload_video.assert_not_called()
