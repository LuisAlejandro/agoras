# -*- coding: utf-8 -*-
#
# Please refer to AUTHORS.md for a complete list of Copyright holders.
# Copyright (C) 2022-2026, Agoras Developers.

"""Tests for agoras.core.text_limits."""

import pytest

from agoras.core.text_limits import (
    TextValidationError,
    iter_text_limits,
    lookup_limit,
    measure_length,
    threads_length,
    validate_discord_embeds,
    validate_text,
    weighted_x_length,
    x_limit_for_subscription,
    x_mode_for_subscription,
)


def test_chars_under_and_over_limit():
    assert validate_text("facebook", "message", "hi") == 2
    with pytest.raises(TextValidationError) as exc:
        validate_text("instagram", "caption", "x" * 2201)
    assert exc.value.field == "caption"
    assert exc.value.actual == 2201
    assert exc.value.limit == 2200
    assert exc.value.counting == "chars"


def test_exact_limit_passes():
    assert validate_text("discord", "content", "a" * 2000) == 2000


def test_empty_passes():
    assert validate_text("linkedin", "text", "") == 0
    assert validate_text("linkedin", "text", None) == 0


def test_youtube_description_utf8_bytes_ae6():
    # One emoji is multiple UTF-8 bytes; pad so chars <= 5000 but bytes > 5000
    emoji = "😀"  # 4 bytes
    # 1249 emoji => 4996 bytes; add 5 ascii => 5001 bytes, chars = 1254
    text = emoji * 1249 + "abcde"
    assert len(text) < 5000
    assert len(text.encode("utf-8")) == 5001
    with pytest.raises(TextValidationError) as exc:
        validate_text("youtube", "description", text)
    assert exc.value.counting == "utf8_bytes"
    assert exc.value.actual == 5001


def test_tiktok_utf16_runes_non_bmp():
    # Non-BMP emoji is one Python char but two UTF-16 code units
    text = "😀"
    assert measure_length(text, "utf16_runes") == 2
    assert validate_text("tiktok", "title", text, mode="video") == 2


def test_telegram_mode_limits():
    longish = "a" * 2000
    assert validate_text("telegram", "text", longish, mode="text") == 2000
    with pytest.raises(TextValidationError) as exc:
        validate_text("telegram", "caption", longish, mode="caption")
    assert exc.value.field == "caption"
    assert exc.value.limit == 1024
    assert exc.value.actual == 2000


def test_x_subscription_limits():
    assert x_limit_for_subscription(None) == 280
    assert x_limit_for_subscription("None") == 280
    assert x_limit_for_subscription("Premium") == 25000
    assert x_limit_for_subscription("Basic") == 25000
    assert x_limit_for_subscription("PremiumPlus") == 25000
    assert x_mode_for_subscription("Premium") == "premium"
    assert x_mode_for_subscription(None) == "free"


def test_weighted_x_plain_ascii():
    assert weighted_x_length("hello") == 5


def test_weighted_x_url_counts_as_23():
    text = "https://example.com/some/long/path/here"
    assert weighted_x_length(text) == 23
    # Same URL plus spaces + short text
    assert weighted_x_length(f"hi {text}") == 26


def test_weighted_x_zwj_emoji_per_codepoint_limitation():
    """Document known limitation: ZWJ sequences are not clustered (emojiParsingEnabled=false).

    Family emoji 👨‍👩‍👧 is multiple code points; full twitter-text with emoji parsing
    would weight the cluster differently. Our per-codepoint approximation counts each.
    """
    from agoras.core.text_limits import _twitter_text_config

    _twitter_text_config.cache_clear()
    assert _twitter_text_config().get("emojiParsingEnabled") is False
    family = "👨\u200d👩\u200d👧"  # man ZWJ woman ZWJ girl
    # Per-codepoint: 3 emoji (defaultWeight 200) + 2 ZWJ (range weight 100) =>
    # (3*200 + 2*100) / 100 = 8 character units
    assert weighted_x_length(family) == 8
    assert len(family) == 5  # 3 emoji + 2 ZWJ code points


def test_validate_x_free_over_limit():
    with pytest.raises(TextValidationError) as exc:
        validate_text("x", "text", "a" * 281, mode="free")
    assert exc.value.limit == 280
    assert exc.value.counting == "weighted_x"


def test_validate_x_premium_allows_long():
    assert validate_text("twitter", "text", "a" * 1000, mode="premium") == 1000


def test_threads_emoji_utf8_bytes():
    # Single emoji 😀 is 4 UTF-8 bytes under Threads rule
    assert threads_length("😀") == 4
    assert threads_length("ab") == 2


def test_threads_emoji_over_limit_despite_short_codepoints():
    # 126 emoji => 126 code points (<=500) but threads_length 504 (>500)
    text = "😀" * 126
    assert len(text) <= 500
    assert threads_length(text) > 500
    with pytest.raises(TextValidationError) as exc:
        validate_text("threads", "text", text)
    assert exc.value.field == "text"
    assert exc.value.counting == "threads"
    assert exc.value.actual == 504
    assert exc.value.limit == 500


def test_discord_embed_budget():
    validate_discord_embeds([{"title": "t", "description": "d"}])
    with pytest.raises(TextValidationError) as exc:
        validate_discord_embeds([{"title": "a" * 257}])
    assert exc.value.field == "embed_title"


def test_discord_embed_total_over_budget():
    embeds = [
        {"description": "a" * 4096},
        {"description": "b" * 2000},
    ]
    with pytest.raises(TextValidationError) as exc:
        validate_discord_embeds(embeds)
    assert exc.value.field == "embed_total"
    assert exc.value.actual == 6096
    assert exc.value.limit == lookup_limit("discord", "embed_total").limit


def test_iter_text_limits_filter():
    rows = iter_text_limits("telegram")
    fields = {(r.field, r.mode) for r in rows}
    assert ("text", "text") in fields
    assert ("caption", "caption") in fields


def test_lookup_limit_missing():
    with pytest.raises(KeyError):
        lookup_limit("facebook", "nope")


def test_error_message_includes_counting():
    with pytest.raises(TextValidationError, match="Counting: chars"):
        validate_text("discord", "content", "x" * 2001)
