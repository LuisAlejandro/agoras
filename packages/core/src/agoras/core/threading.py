# -*- coding: utf-8 -*-
#
# Please refer to AUTHORS.md for a complete list of Copyright holders.
# Copyright (C) 2022-2026, Agoras Developers.

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""Shared thread result models and serialization for Agoras."""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import List, Literal, Optional

ThreadOutcome = Literal["failed", "unknown"]


@dataclass(frozen=True)
class ThreadResult:
    """One structured result for a thread publish operation."""

    id: str
    ids: List[str]
    complete: bool
    thread_id: Optional[str] = None
    failed_index: Optional[int] = None
    outcome: Optional[ThreadOutcome] = None
    error: Optional[str] = None

    def to_dict(self) -> dict:
        """Return JSON-serializable dict omitting null optional fields when complete."""
        data = {
            "id": self.id,
            "ids": list(self.ids),
            "complete": self.complete,
        }
        if self.thread_id is not None:
            data["thread_id"] = self.thread_id
        if not self.complete:
            if self.failed_index is not None:
                data["failed_index"] = self.failed_index
            if self.outcome is not None:
                data["outcome"] = self.outcome
            if self.error is not None:
                data["error"] = self.error
        return data

    def to_json(self) -> str:
        """Serialize as one compact JSON object."""
        return json.dumps(self.to_dict(), separators=(",", ":"))


class ThreadPublishError(Exception):
    """Raised after a partial or failed thread publish with a structured result."""

    def __init__(self, result: ThreadResult, message: Optional[str] = None):
        """Attach a ThreadResult and optional message to the exception."""
        self.result = result
        super().__init__(message or result.error or "Thread publish incomplete")


def emit_thread_result(result: ThreadResult) -> None:
    """Print exactly one JSON line for a thread operation."""
    print(result.to_json())


def success_result(ids: List[str], *, thread_id: Optional[str] = None) -> ThreadResult:
    """Build a complete success result."""
    if not ids:
        raise ValueError("Thread success requires at least one id")
    return ThreadResult(id=ids[0], ids=list(ids), complete=True, thread_id=thread_id)


def partial_result(
    ids: List[str],
    *,
    failed_index: int,
    outcome: ThreadOutcome,
    error: Optional[str] = None,
    thread_id: Optional[str] = None,
) -> ThreadResult:
    """Build an incomplete result after a confirmed or uncertain failure."""
    root = ids[0] if ids else ""
    return ThreadResult(
        id=root,
        ids=list(ids),
        complete=False,
        thread_id=thread_id,
        failed_index=failed_index,
        outcome=outcome,
        error=error,
    )
