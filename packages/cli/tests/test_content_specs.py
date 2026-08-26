# -*- coding: utf-8 -*-
#
# Please refer to AUTHORS.rst for a complete list of Copyright holders.
# Copyright (C) 2022-2026, Agoras Developers.

"""Tests for content_specs registry."""

from agoras.cli.content_specs import (
    CONTENT_SPECS,
    content_capable_actions,
    get_action_spec,
    supports_content_file,
)


def test_all_expected_actions_registered():
    expected = {
        ("x", "post"),
        ("x", "video"),
        ("x", "thread"),
        ("twitter", "post"),
        ("twitter", "video"),
        ("twitter", "thread"),
        ("facebook", "post"),
        ("facebook", "video"),
        ("instagram", "post"),
        ("instagram", "video"),
        ("linkedin", "post"),
        ("linkedin", "video"),
        ("discord", "post"),
        ("discord", "video"),
        ("discord", "thread"),
        ("youtube", "video"),
        ("tiktok", "post"),
        ("tiktok", "video"),
        ("threads", "post"),
        ("threads", "video"),
        ("threads", "thread"),
        ("telegram", "post"),
        ("telegram", "video"),
        ("whatsapp", "post"),
        ("whatsapp", "video"),
        ("whatsapp", "template"),
    }
    assert set(CONTENT_SPECS.keys()) == expected


def test_supports_content_file():
    assert supports_content_file("x", "post") is True
    assert supports_content_file("X", "post") is True
    assert supports_content_file("youtube", "like") is False
    assert supports_content_file("discord", "delete") is False


def test_content_capable_actions_x():
    assert content_capable_actions("x") == frozenset({"post", "video", "thread"})


def test_get_action_spec_discord_thread_requires_name():
    spec = get_action_spec("discord", "thread")
    assert "thread_name" in spec.field_map
    assert spec.field_map["thread_name"].required is True
    assert "entries" in spec.field_map
