# -*- coding: utf-8 -*-
#
# Please refer to AUTHORS.rst for a complete list of Copyright holders.
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
"""Shared platform status poll: ready, failed, timeout, and budget capping."""

import pytest

from agoras.core.polling import ProcessingFailedError, ProcessingTimeoutError, poll_status


class _Clock:
    """Deterministic clock whose sleep advances time."""

    def __init__(self):
        self.now = 0.0
        self.sleeps = []

    def monotonic(self):
        return self.now

    def sleep(self, seconds):
        self.sleeps.append(seconds)
        self.now += seconds


def _probe_from(statuses):
    """Return a probe that yields the given statuses in order, repeating the last."""
    remaining = list(statuses)

    def probe():
        return remaining.pop(0) if len(remaining) > 1 else remaining[0]

    return probe


def test_ready_on_first_probe_never_sleeps():
    """An already-complete object costs no wait."""
    clock = _Clock()
    status = poll_status(
        _probe_from(["FINISHED"]),
        ready={"FINISHED"},
        failed={"ERROR"},
        subject="thing",
        timeout_s=30,
        interval_s=5,
        clock=clock.monotonic,
        sleep=clock.sleep,
    )

    assert status == "FINISHED"
    assert clock.sleeps == []


def test_polls_until_ready():
    """Polling continues at the configured interval until ready."""
    clock = _Clock()
    status = poll_status(
        _probe_from(["IN_PROGRESS", "IN_PROGRESS", "PUBLISHED"]),
        ready={"PUBLISHED"},
        failed={"ERROR"},
        subject="thing",
        timeout_s=30,
        interval_s=5,
        clock=clock.monotonic,
        sleep=clock.sleep,
    )

    assert status == "PUBLISHED"
    assert clock.sleeps == [5, 5]


def test_failed_status_raises_a_distinct_error():
    """A terminal failure is not a timeout: callers must be able to tell them apart."""
    clock = _Clock()
    with pytest.raises(ProcessingFailedError, match="processing failed with status ERROR"):
        poll_status(
            _probe_from(["ERROR"]),
            ready={"FINISHED"},
            failed={"ERROR"},
            subject="thing",
            timeout_s=30,
            interval_s=5,
            clock=clock.monotonic,
            sleep=clock.sleep,
        )

    assert clock.sleeps == []


def test_timeout_caps_the_last_sleep_to_the_remaining_budget():
    """The final sleep cannot overshoot the deadline."""
    clock = _Clock()
    with pytest.raises(ProcessingTimeoutError, match="not ready after 10s"):
        poll_status(
            _probe_from(["IN_PROGRESS"]),
            ready={"FINISHED"},
            failed={"ERROR"},
            subject="thing",
            timeout_s=10,
            interval_s=4,
            clock=clock.monotonic,
            sleep=clock.sleep,
        )

    assert clock.sleeps == [4, 4, 2]
    assert clock.now == 10


def test_timeout_is_a_timeout_error_for_uncertainty_classification():
    """Publish-error classifiers treat this as uncertain, not confirmed failure."""
    assert issubclass(ProcessingTimeoutError, TimeoutError)
    assert not issubclass(ProcessingFailedError, TimeoutError)
