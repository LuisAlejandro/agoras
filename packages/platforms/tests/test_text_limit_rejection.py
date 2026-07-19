# -*- coding: utf-8 -*-
#
# Please refer to AUTHORS.md for a complete list of Copyright holders.
# Copyright (C) 2022-2026, Agoras Developers.

"""Focused reject-before-API text limit tests for platform wrappers."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from agoras.core.text_limits import TextValidationError
from agoras.platforms.discord.wrapper import Discord
from agoras.platforms.facebook.wrapper import Facebook
from agoras.platforms.instagram.wrapper import Instagram
from agoras.platforms.linkedin.wrapper import LinkedIn
from agoras.platforms.telegram.wrapper import Telegram
from agoras.platforms.threads.wrapper import Threads
from agoras.platforms.tiktok.wrapper import TikTok
from agoras.platforms.whatsapp.wrapper import WhatsApp
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


@pytest.mark.asyncio
async def test_whatsapp_text_allows_2000_but_caption_rejects():
    wa = WhatsApp(whatsapp_access_token="tok", whatsapp_phone_number_id="pn")
    wa.api = MagicMock()
    wa.api.send_message = AsyncMock(return_value="m1")
    wa.api.send_image = AsyncMock(return_value="m2")
    wa.whatsapp_recipient = "15551234567"

    longish = "a" * 2000
    with patch.object(wa, "_output_status"):
        await wa.post(longish, "")
    wa.api.send_message.assert_called_once()

    with pytest.raises(TextValidationError) as exc:
        await wa.post(longish, "", status_image_url_1="https://example.com/a.jpg")
    assert exc.value.field == "caption"
    assert exc.value.limit == 1024
    wa.api.send_image.assert_not_called()


@pytest.mark.asyncio
async def test_facebook_rejects_message_over_limit():
    fb = Facebook(facebook_access_token="t", facebook_object_id="oid")
    fb.api = MagicMock()
    fb.api.post = AsyncMock()
    fb.facebook_object_id = "oid"
    fb._is_page_target = True

    with pytest.raises(TextValidationError) as exc:
        await fb.post("x" * 63207, "")
    assert exc.value.field == "message"
    fb.api.post.assert_not_called()


@pytest.mark.asyncio
async def test_linkedin_rejects_text_over_3000():
    li = LinkedIn(linkedin_client_id="id", linkedin_client_secret="sec", linkedin_access_token="tok")
    li.api = MagicMock()
    li.api.post = AsyncMock()

    with pytest.raises(TextValidationError) as exc:
        await li.post("x" * 3001, "")
    assert exc.value.field == "text"
    li.api.post.assert_not_called()


@pytest.mark.asyncio
async def test_linkedin_rejects_oversized_scraped_link_title():
    li = LinkedIn(linkedin_client_id="id", linkedin_client_secret="sec", linkedin_access_token="tok")
    li.api = MagicMock()
    li.api.post = AsyncMock()

    with patch("agoras.platforms.linkedin.wrapper.parse_metatags") as mock_meta:
        mock_meta.return_value = {"title": "T" * 201, "description": "ok", "image": ""}
        with patch.object(li, "download_images", new=AsyncMock()) as mock_dl:
            with pytest.raises(TextValidationError) as exc:
                await li.post("hi", "https://example.com/article")
            assert exc.value.field == "link_title"
            mock_dl.assert_not_called()
            li.api.post.assert_not_called()


@pytest.mark.asyncio
async def test_threads_rejects_text_over_500():
    th = Threads(threads_access_token="t", threads_user_id="uid")
    th.api = MagicMock()
    th.api.create_post = AsyncMock()

    with pytest.raises(TextValidationError) as exc:
        await th.post("x" * 501, "")
    assert exc.value.field == "text"
    th.api.create_post.assert_not_called()


@pytest.mark.asyncio
async def test_tiktok_rejects_photo_title_over_90():
    tk = TikTok(tiktok_access_token="t", tiktok_open_id="oid")
    tk.api = MagicMock()
    tk.api.upload_photo = AsyncMock()
    tk.tiktok_title = None
    tk.tiktok_description = ""
    tk.tiktok_allow_duet = False
    tk.tiktok_allow_stitch = False

    with patch.object(tk, "download_images", new=AsyncMock()) as mock_dl:
        with pytest.raises(TextValidationError) as exc:
            await tk.post("T" * 91, "", status_image_url_1="https://example.com/a.jpg")
        assert exc.value.field == "title"
        assert exc.value.limit == 90
        mock_dl.assert_not_called()
        tk.api.upload_photo.assert_not_called()


@pytest.mark.asyncio
async def test_discord_rejects_oversized_scrape_embed_before_api():
    dc = Discord(discord_bot_token="tok", discord_channel_id="chan")
    dc.api = MagicMock()
    dc.api.post = AsyncMock()
    dc.api.create_embed = MagicMock(return_value={"title": "t"})
    dc.discord_channel_id = "chan"

    with patch("agoras.platforms.discord.wrapper.parse_metatags") as mock_meta:
        mock_meta.return_value = {"title": "a" * 257, "description": "d", "image": ""}
        with patch.object(dc, "download_images", new=AsyncMock()) as mock_dl:
            with pytest.raises(TextValidationError) as exc:
                await dc.post("hi", "https://example.com/page")
            assert exc.value.field == "embed_title"
            mock_dl.assert_not_called()
            dc.api.post.assert_not_called()
            dc.api.create_embed.assert_not_called()
