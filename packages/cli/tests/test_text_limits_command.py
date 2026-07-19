# -*- coding: utf-8 -*-
#
# Please refer to AUTHORS.rst for a complete list of Copyright holders.
# Copyright (C) 2022-2026, Agoras Developers.

"""Tests for agoras utils text-limits."""

from argparse import Namespace
from io import StringIO
from unittest.mock import patch

import pytest

from agoras.cli.utils.text_limits import _handle_text_limits, main


def test_text_limits_stdout_contains_telegram_modes():
    buf = StringIO()
    with patch("sys.stdout", buf):
        _handle_text_limits(Namespace(platform="telegram", json=False))
    out = buf.getvalue()
    assert "caption" in out
    assert "1024" in out
    assert "4096" in out


def test_text_limits_json_includes_discord_and_x():
    buf = StringIO()
    with patch("sys.stdout", buf):
        _handle_text_limits(Namespace(platform=None, json=True))
    import json

    rows = json.loads(buf.getvalue())
    platforms = {row["platform"] for row in rows}
    assert "discord" in platforms
    assert "twitter" in platforms
    assert any(row["platform"] == "twitter" and row["mode"] == "premium" for row in rows)


def test_unknown_platform_raises_value_error():
    with pytest.raises(ValueError, match="Unknown platform"):
        _handle_text_limits(Namespace(platform="not-a-platform", json=False))


def test_main_unknown_platform_exits_1():
    assert main(["--platform", "not-a-platform"]) == 1
