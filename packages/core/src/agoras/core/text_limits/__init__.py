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
"""Shared text-limit contract for Agoras platform posts."""

from __future__ import annotations

import json
import re
import unicodedata
from dataclasses import dataclass
from functools import lru_cache
from importlib import resources
from typing import Dict, Iterable, List, Literal, Optional, Tuple

CountingRule = Literal["chars", "utf8_bytes", "utf16_runes", "weighted_x", "threads"]

PLATFORM_ALIASES: Dict[str, str] = {
    "x": "twitter",
    "X": "twitter",
    "twitter": "twitter",
    "discord": "discord",
    "Discord": "discord",
    "facebook": "facebook",
    "Facebook": "facebook",
    "instagram": "instagram",
    "Instagram": "instagram",
    "linkedin": "linkedin",
    "LinkedIn": "linkedin",
    "youtube": "youtube",
    "YouTube": "youtube",
    "tiktok": "tiktok",
    "TikTok": "tiktok",
    "threads": "threads",
    "Threads": "threads",
    "telegram": "telegram",
    "Telegram": "telegram",
    "whatsapp": "whatsapp",
    "WhatsApp": "whatsapp",
}

X_PREMIUM_SUBSCRIPTION_TYPES = frozenset({"Basic", "Premium", "PremiumPlus"})
X_FREE_LIMIT = 280
X_PREMIUM_LIMIT = 25000

# URL detection aligned with twitter-text extractURL-ish matching for length only.
_URL_RE = re.compile(r"(?i)\b(?:https?://|www\.)[^\s<>\"']+")


@dataclass(frozen=True)
class TextFieldLimit:
    """Limit for one outbound text field on a platform."""

    platform: str
    field: str
    limit: int
    counting: CountingRule
    mode: Optional[str] = None  # e.g. text vs caption; None = default/all modes


# Authoritative Agoras outbound field limits (see design doc).
TEXT_LIMITS: Tuple[TextFieldLimit, ...] = (
    TextFieldLimit("twitter", "text", X_FREE_LIMIT, "weighted_x", mode="free"),
    TextFieldLimit("twitter", "text", X_PREMIUM_LIMIT, "weighted_x", mode="premium"),
    TextFieldLimit("facebook", "message", 63206, "chars"),
    TextFieldLimit("instagram", "caption", 2200, "chars"),
    TextFieldLimit("linkedin", "text", 3000, "chars"),
    # Scraped Open Graph fields for LinkedIn article shares (conservative caps;
    # LinkedIn share article title/description are commonly constrained near these).
    TextFieldLimit("linkedin", "link_title", 200, "chars"),
    TextFieldLimit("linkedin", "link_description", 256, "chars"),
    TextFieldLimit("threads", "text", 500, "threads"),
    TextFieldLimit("youtube", "title", 100, "chars"),
    TextFieldLimit("youtube", "description", 5000, "utf8_bytes"),
    TextFieldLimit("tiktok", "title", 2200, "utf16_runes", mode="video"),
    TextFieldLimit("tiktok", "title", 90, "utf16_runes", mode="photo"),
    TextFieldLimit("tiktok", "description", 4000, "utf16_runes", mode="photo"),
    TextFieldLimit("telegram", "text", 4096, "chars", mode="text"),
    TextFieldLimit("telegram", "caption", 1024, "chars", mode="caption"),
    TextFieldLimit("discord", "content", 2000, "chars"),
    TextFieldLimit("discord", "embed_title", 256, "chars"),
    TextFieldLimit("discord", "embed_description", 4096, "chars"),
    TextFieldLimit("discord", "embed_total", 6000, "chars"),
    TextFieldLimit("discord", "thread_name", 100, "chars"),
    TextFieldLimit("whatsapp", "text", 4096, "chars", mode="text"),
    TextFieldLimit("whatsapp", "caption", 1024, "chars", mode="caption"),
)


def resolve_platform(name: str) -> str:
    """Map CLI/class names to canonical platform keys."""
    if not name:
        raise ValueError("platform name is required")
    return PLATFORM_ALIASES.get(name, name.lower())


def x_limit_for_subscription(subscription_type: Optional[str]) -> int:
    """Return X text limit from stored subscription_type (fail closed to free)."""
    if subscription_type in X_PREMIUM_SUBSCRIPTION_TYPES:
        return X_PREMIUM_LIMIT
    return X_FREE_LIMIT


def x_mode_for_subscription(subscription_type: Optional[str]) -> str:
    """Return free|premium mode key for table lookup."""
    if subscription_type in X_PREMIUM_SUBSCRIPTION_TYPES:
        return "premium"
    return "free"


def iter_text_limits(platform: Optional[str] = None) -> List[TextFieldLimit]:
    """Return text limit rows, optionally filtered by platform."""
    if platform is None:
        return list(TEXT_LIMITS)
    key = resolve_platform(platform)
    # Accept both twitter and x
    if key == "twitter":
        return [row for row in TEXT_LIMITS if row.platform == "twitter"]
    return [row for row in TEXT_LIMITS if row.platform == key]


def lookup_limit(platform: str, field: str, *, mode: Optional[str] = None) -> TextFieldLimit:
    """Look up a limit row; raise KeyError if missing."""
    key = resolve_platform(platform)
    canonical = "twitter" if key == "twitter" else key
    candidates = [row for row in TEXT_LIMITS if row.platform == canonical and row.field == field]
    if not candidates:
        raise KeyError(f"No text limit for {canonical}.{field}")
    if mode is None:
        # Prefer rows without mode, else first
        for row in candidates:
            if row.mode is None:
                return row
        return candidates[0]
    for row in candidates:
        if row.mode == mode:
            return row
    raise KeyError(f"No text limit for {canonical}.{field} mode={mode}")


def measure_length(text: str, counting: CountingRule) -> int:
    """Measure text length under a platform counting rule."""
    if text is None:
        text = ""
    if counting == "chars":
        return len(text)
    if counting == "utf8_bytes":
        return len(text.encode("utf-8"))
    if counting == "utf16_runes":
        return len(text.encode("utf-16-le")) // 2
    if counting == "weighted_x":
        return weighted_x_length(text)
    if counting == "threads":
        return threads_length(text)
    raise ValueError(f"Unknown counting rule: {counting}")


def threads_length(text: str) -> int:
    """
    Threads length: non-emoji characters count as 1; emoji count as UTF-8 byte length.

    Uses Unicode emoji presentation / extended pictographic as a practical approximation
    of Threads' documented emoji UTF-8-byte rule.
    """
    if not text:
        return 0
    total = 0
    for ch in text:
        if _is_emoji_char(ch):
            total += len(ch.encode("utf-8"))
        else:
            total += 1
    return total


def _is_emoji_char(ch: str) -> bool:
    code = ord(ch)
    # Common emoji blocks + variation selectors / ZWJ handled per code point
    if 0x1F300 <= code <= 0x1FAFF:
        return True
    if 0x2600 <= code <= 0x27BF:
        return True
    if code in (0x200D, 0xFE0F, 0x20E3):
        return True
    if 0x1F1E6 <= code <= 0x1F1FF:  # regional indicators
        return True
    return False


@lru_cache(maxsize=1)
def _twitter_text_config() -> dict:
    data = resources.files("agoras.core.text_limits").joinpath("data/twitter_text_v3.json").read_text(encoding="utf-8")
    return json.loads(data)


def weighted_x_length(text: str) -> int:
    """
    twitter-text weighted length (scale units), rounded up to whole characters.

    URLs are replaced with transformedURLLength (23). Remaining text is NFC-normalized
    and weighted per v3 ranges (defaultWeight outside ranges).

    Approximation: ``emojiParsingEnabled`` is false in twitter_text_v3.json — this
    implementation weights each Unicode code point independently and does not cluster
    ZWJ / multi-codepoint emoji sequences the way full twitter-text does.
    """
    config = _twitter_text_config()
    scale = int(config["scale"])
    default_weight = int(config["defaultWeight"])
    url_length = int(config["transformedURLLength"])
    ranges = [(int(r["start"]), int(r["end"]), int(r["weight"])) for r in config["ranges"]]

    # Replace URLs with placeholders of weight url_length * scale
    parts: List[Tuple[str, bool]] = []
    last = 0
    for match in _URL_RE.finditer(text or ""):
        if match.start() > last:
            parts.append((text[last : match.start()], False))
        parts.append(("", True))  # URL slot
        last = match.end()
    if last < len(text or ""):
        parts.append((text[last:], False))
    if not parts and text:
        parts.append((text, False))

    weighted = 0
    for chunk, is_url in parts:
        if is_url:
            weighted += url_length * scale
            continue
        normalized = unicodedata.normalize("NFC", chunk)
        for ch in normalized:
            code = ord(ch)
            weight = default_weight
            for start, end, range_weight in ranges:
                if start <= code <= end:
                    weight = range_weight
                    break
            weighted += weight

    # Convert scale units to character units (ceil division)
    return (weighted + scale - 1) // scale


class TextValidationError(Exception):
    """Raised when outbound text exceeds a platform limit."""

    def __init__(
        self,
        platform: str,
        field: str,
        actual: int,
        limit: int,
        counting: CountingRule,
        message: Optional[str] = None,
    ):
        """Initialize with platform field length details."""
        self.platform = platform
        self.field = field
        self.actual = actual
        self.limit = limit
        self.counting = counting
        super().__init__(message or format_text_limit_error(platform, field, actual, limit, counting))


def format_text_limit_error(platform: str, field: str, actual: int, limit: int, counting: CountingRule) -> str:
    """Build a consistent text validation error message."""
    return f"{platform} {field} length ({actual} {counting}) exceeds limit of {limit}. Counting: {counting}."


def validate_text(
    platform: str,
    field: str,
    text: Optional[str],
    *,
    mode: Optional[str] = None,
    limit: Optional[int] = None,
    counting: Optional[CountingRule] = None,
) -> int:
    """
    Validate outbound text against platform limits.

    Returns measured length when valid. Raises TextValidationError when over limit.
    Empty/None text is treated as length 0 and always passes.
    """
    key = resolve_platform(platform)
    canonical = "twitter" if key == "twitter" else key
    if limit is None or counting is None:
        row = lookup_limit(canonical, field, mode=mode)
        if limit is None:
            limit = row.limit
        if counting is None:
            counting = row.counting
    assert counting is not None and limit is not None
    measured = measure_length(text or "", counting)
    if measured > limit:
        raise TextValidationError(canonical, field, measured, limit, counting)
    return measured


def validate_discord_embeds(embeds: Iterable[dict]) -> None:
    """
    Validate Discord embed title/description fields and total embed text budget.

    Each item may include optional keys: title, description.
    """
    embed_total = lookup_limit("discord", "embed_total")
    total = 0
    for embed in embeds:
        title = embed.get("title") or ""
        description = embed.get("description") or ""
        if title:
            validate_text("discord", "embed_title", title)
            total += len(title)
        if description:
            validate_text("discord", "embed_description", description)
            total += len(description)
    if total > embed_total.limit:
        raise TextValidationError("discord", "embed_total", total, embed_total.limit, embed_total.counting)
