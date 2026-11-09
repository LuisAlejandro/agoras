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
"""agoras.core.polling module.

Bounded status polling shared by the platform processing pipelines.

Threads, Instagram, LinkedIn and TikTok all wait on a remote object that moves
through provider-defined status strings. Each used to own its own
``while status not in ready: sleep; poll`` loop with its own ready/failed sets,
its own deadline arithmetic, and its own (or no) terminal failure state. This
module owns the loop; each platform keeps only its status vocabulary.
"""

import time
from typing import Callable, Collection, Optional


class ProcessingFailedError(Exception):
    """Raised when a remote object reports a terminal failure status."""


class ProcessingTimeoutError(TimeoutError):
    """Raised when a remote object does not become ready within the poll budget.

    Subclasses ``TimeoutError`` so the publish-error classifiers in
    ``agoras.core.interfaces`` treat it as an uncertain outcome (the request may
    still complete remotely) rather than a confirmed failure.
    """


def poll_status(
    probe: Callable[[], str],
    *,
    ready: Collection[str],
    failed: Collection[str],
    subject: str,
    timeout_s: float,
    interval_s: float = 2.0,
    clock: Optional[Callable[[], float]] = None,
    sleep: Optional[Callable[[float], None]] = None,
) -> str:
    """Poll ``probe`` until it returns a status in ``ready``.

    Probes before it waits, so an already-complete object costs no sleep time.

    Args:
        probe: Returns one status token; may raise to abort the poll.
        ready: Statuses that mean the object is usable.
        failed: Statuses that mean the object will never be usable.
        subject: Human-readable object name used in error messages.
        timeout_s: Total budget for the poll.
        interval_s: Delay between probes, capped by the remaining budget.
        clock: Monotonic clock; resolved at call time so tests can patch it.
        sleep: Sleeper; resolved at call time so tests can patch it.

    Returns:
        str: The first status that matched ``ready``.

    Raises:
        ProcessingFailedError: On a status in ``failed``.
        ProcessingTimeoutError: When the budget is exhausted.
    """
    clock = clock or time.monotonic
    sleep = sleep or time.sleep
    deadline = clock() + timeout_s

    while True:
        status = probe()
        if status in ready:
            return status
        if status in failed:
            raise ProcessingFailedError(f"{subject} processing failed with status {status}")
        remaining = deadline - clock()
        if remaining <= 0:
            raise ProcessingTimeoutError(f"{subject} not ready after {timeout_s:g}s (last status {status!r})")
        sleep(min(interval_s, remaining))
