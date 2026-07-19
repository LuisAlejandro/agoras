# -*- coding: utf-8 -*-
#
# Please refer to AUTHORS.rst for a complete list of Copyright holders.
# Copyright (C) 2022-2026, Agoras Developers.

"""Tests for agoras.core.threading result models."""

from agoras.core.threading import (
    ThreadPublishError,
    partial_result,
    success_result,
)


def test_success_result_json():
    result = success_result(["1", "2", "3"], thread_id="t1")
    data = result.to_dict()
    assert data["id"] == "1"
    assert data["ids"] == ["1", "2", "3"]
    assert data["complete"] is True
    assert data["thread_id"] == "t1"
    assert "failed_index" not in data
    assert '"complete":true' in result.to_json()


def test_partial_failed_result():
    result = partial_result(["1"], failed_index=1, outcome="failed", error="boom")
    data = result.to_dict()
    assert data["complete"] is False
    assert data["failed_index"] == 1
    assert data["outcome"] == "failed"
    assert data["error"] == "boom"


def test_partial_unknown_result():
    result = partial_result(["1", "2"], failed_index=2, outcome="unknown")
    assert result.to_dict()["outcome"] == "unknown"


def test_thread_publish_error_carries_result():
    result = partial_result([], failed_index=0, outcome="failed", error="nope")
    exc = ThreadPublishError(result)
    assert exc.result is result
    assert "nope" in str(exc)
