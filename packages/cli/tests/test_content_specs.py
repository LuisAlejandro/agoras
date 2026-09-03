# -*- coding: utf-8 -*-
#
# Please refer to AUTHORS.rst for a complete list of Copyright holders.
# Copyright (C) 2022-2026, Agoras Developers.

"""Tests for content_specs registry."""

from agoras.cli.content_specs import (
    CONTENT_SPECS,
    get_action_spec,
    supports_content_file,
)


def test_all_expected_actions_registered():
    expected = {
        ("x", "post"),
        ("x", "video"),
        ("x", "thread"),
        ("x", "reply"),
        ("twitter", "post"),
        ("twitter", "video"),
        ("twitter", "thread"),
        ("twitter", "reply"),
        ("facebook", "post"),
        ("facebook", "video"),
        ("facebook", "reply"),
        ("instagram", "post"),
        ("instagram", "video"),
        ("instagram", "reply"),
        ("linkedin", "post"),
        ("linkedin", "video"),
        ("linkedin", "reply"),
        ("discord", "post"),
        ("discord", "video"),
        ("discord", "thread"),
        ("discord", "reply"),
        ("youtube", "video"),
        ("youtube", "reply"),
        ("tiktok", "post"),
        ("tiktok", "video"),
        ("threads", "post"),
        ("threads", "video"),
        ("threads", "thread"),
        ("threads", "reply"),
        ("telegram", "post"),
        ("telegram", "video"),
        ("telegram", "reply"),
        ("whatsapp", "post"),
        ("whatsapp", "video"),
        ("whatsapp", "template"),
        ("whatsapp", "reply"),
    }
    assert set(CONTENT_SPECS.keys()) == expected


def test_supports_content_file():
    assert supports_content_file("x", "post") is True
    assert supports_content_file("X", "post") is True
    assert supports_content_file("youtube", "like") is False
    assert supports_content_file("discord", "delete") is False


def test_get_action_spec_discord_thread_requires_name():
    spec = get_action_spec("discord", "thread")
    assert "thread_name" in spec.field_map
    assert spec.field_map["thread_name"].required is True
    assert "entries" in spec.field_map


def test_reply_content_specs_media():
    """Threads/Facebook/LinkedIn reply specs accept media; Instagram/YouTube are text-only."""
    threads = get_action_spec("threads", "reply")
    assert "images" in threads.field_map
    assert threads.field_map["images"].media_source is True
    assert "video_url" in threads.field_map

    facebook = get_action_spec("facebook", "reply")
    assert "images" in facebook.field_map
    assert facebook.field_map["images"].max_items == 1

    linkedin = get_action_spec("linkedin", "reply")
    assert "images" in linkedin.field_map
    assert linkedin.field_map["images"].media_source is True

    instagram = get_action_spec("instagram", "reply")
    assert set(instagram.field_map.keys()) == {"text"}
    assert instagram.field_map["text"].required is True

    youtube = get_action_spec("youtube", "reply")
    assert set(youtube.field_map.keys()) == {"text"}
    assert youtube.field_map["text"].required is True


def test_reply_content_spec_omits_post_id():
    """Reply content-file specs do not declare post_id (enforced by the CLI parser)."""
    threads = get_action_spec("threads", "reply")
    assert "post_id" not in threads.field_map
