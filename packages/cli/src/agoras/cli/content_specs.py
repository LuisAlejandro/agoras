# -*- coding: utf-8 -*-
#
# Please refer to AUTHORS.rst for a complete list of Copyright holders.
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
"""Immutable content-file specifications keyed by (platform, action)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, FrozenSet, Optional, Tuple

FieldKind = str  # str | bool | int | str_list | map_list | entries | any

CONTENT_SCHEMA_VERSION = 1
MAX_THREAD_ENTRIES = 100
MIN_THREAD_ENTRIES = 2
MAX_IMAGES = 4

# Keys never allowed in content YAML (CLI owns these).
RESERVED_CONTENT_KEYS: FrozenSet[str] = frozenset(
    {
        "platform",
        "action",
        "kind",
        "network",
        "content",
        "content_file",
    }
)

@dataclass(frozen=True)
class FieldSpec:
    """One content field allowed for a platform action."""

    name: str
    kind: FieldKind
    required: bool = False
    default: Any = None
    choices: Optional[FrozenSet[str]] = None
    max_items: Optional[int] = None
    min_items: Optional[int] = None
    http_url: bool = False
    media_source: bool = False
    max_length: Optional[int] = None


@dataclass(frozen=True)
class ActionSpec:
    """Content contract for one (platform, action)."""

    platform: str
    action: str
    fields: Tuple[FieldSpec, ...]
    require_one_of: Tuple[Tuple[str, ...], ...] = ()
    conflicts: Tuple[Tuple[str, ...], ...] = ()
    # For thread actions: field names that belong on each entry (not root).
    entry_fields: Tuple[FieldSpec, ...] = ()
    entry_require_one_of: Tuple[Tuple[str, ...], ...] = ()
    entry_conflicts: Tuple[Tuple[str, ...], ...] = ()

    @property
    def field_map(self) -> Dict[str, FieldSpec]:
        """Map root field name -> FieldSpec."""
        return {field.name: field for field in self.fields}

    @property
    def entry_field_map(self) -> Dict[str, FieldSpec]:
        """Map entry field name -> FieldSpec."""
        return {field.name: field for field in self.entry_fields}

    @property
    def allowed_keys(self) -> FrozenSet[str]:
        """Root keys allowed for this action (excluding version)."""
        return frozenset(self.field_map.keys())


def _f(
    name: str,
    kind: FieldKind = "str",
    *,
    required: bool = False,
    default: Any = None,
    choices: Optional[FrozenSet[str]] = None,
    max_items: Optional[int] = None,
    min_items: Optional[int] = None,
    http_url: bool = False,
    media_source: bool = False,
    max_length: Optional[int] = None,
) -> FieldSpec:
    return FieldSpec(
        name=name,
        kind=kind,
        required=required,
        default=default,
        choices=choices,
        max_items=max_items,
        min_items=min_items,
        http_url=http_url,
        media_source=media_source,
        max_length=max_length,
    )


_COMMON_POST = (
    _f("text"),
    _f("link", http_url=True),
    _f("images", "str_list", max_items=MAX_IMAGES, min_items=1, media_source=True),
)

_COMMON_REPLY = (
    _f("text"),
    _f("images", "str_list", max_items=MAX_IMAGES, min_items=1, media_source=True),
    _f("video_url", media_source=True),
)

_COMMON_VIDEO = (
    _f("video_url", required=True, media_source=True),
    _f("video_title"),
    _f("text"),
)

_THREAD_ENTRY_BASE = (
    _f("text"),
    _f("link", http_url=True),
    _f("images", "str_list", max_items=MAX_IMAGES, min_items=1, media_source=True),
    _f("video_url", media_source=True),
    _f("video_title"),
)

_THREAD_ENTRY_REQUIRE = (("text", "link", "images", "video_url"),)
_THREAD_ENTRY_CONFLICTS = (("images", "video_url"),)

_TIKTOK_PRIVACY = frozenset({"PUBLIC_TO_EVERYONE", "MUTUAL_FOLLOW_FRIENDS", "FOLLOWER_OF_CREATOR", "SELF_ONLY"})
_YOUTUBE_PRIVACY = frozenset({"public", "private", "unlisted"})
_FACEBOOK_VIDEO_TYPES = frozenset({"regular", "reel", "story"})
_INSTAGRAM_VIDEO_TYPES = frozenset({"REELS", "STORIES", "reels", "stories", "reel", "story"})
_THREADS_REPLY = frozenset({"everyone", "accounts_you_follow", "mentioned_only"})
_TELEGRAM_PARSE = frozenset({"HTML", "Markdown", "MarkdownV2", "None"})
_DISCORD_ARCHIVE = frozenset({60, 1440, 4320, 10080})


def _spec(platform: str, action: str, fields: Tuple[FieldSpec, ...], **kwargs: Any) -> ActionSpec:
    return ActionSpec(platform=platform, action=action, fields=fields, **kwargs)


def _build_specs() -> Dict[Tuple[str, str], ActionSpec]:
    specs: Dict[Tuple[str, str], ActionSpec] = {}

    def add(spec: ActionSpec) -> None:
        specs[(spec.platform, spec.action)] = spec

    # --- X / twitter ---
    for platform in ("x", "twitter"):
        add(
            _spec(
                platform,
                "post",
                _COMMON_POST,
                require_one_of=(("text", "link", "images"),),
            )
        )
        add(
            _spec(
                platform,
                "reply",
                _COMMON_REPLY,
                require_one_of=(("text", "images", "video_url"),),
            )
        )
        add(_spec(platform, "video", _COMMON_VIDEO))
        add(
            _spec(
                platform,
                "thread",
                (_f("entries", "entries", required=True, min_items=MIN_THREAD_ENTRIES, max_items=MAX_THREAD_ENTRIES),),
                entry_fields=_THREAD_ENTRY_BASE,
                entry_require_one_of=_THREAD_ENTRY_REQUIRE,
                entry_conflicts=_THREAD_ENTRY_CONFLICTS,
            )
        )

    # --- Facebook ---
    add(
        _spec(
            "facebook",
            "post",
            _COMMON_POST,
            require_one_of=(("text", "link", "images"),),
        )
    )
    add(
        _spec(
            "facebook",
            "video",
            (
                _f("video_url", required=True, media_source=True),
                _f("video_title", required=True),
                _f("video_description", required=True),
                _f("video_type", choices=_FACEBOOK_VIDEO_TYPES),
                _f("text"),
            ),
        )
    )
    add(
        _spec(
            "facebook",
            "reply",
            (
                _f("text"),
                _f("images", "str_list", max_items=1, min_items=1, media_source=True),
            ),
            require_one_of=(("text", "images"),),
        )
    )

    # --- Instagram ---
    add(
        _spec(
            "instagram",
            "post",
            (
                _f("text"),
                _f("link", http_url=True),
                _f("images", "str_list", required=True, max_items=MAX_IMAGES, min_items=1, media_source=True),
            ),
        )
    )
    add(
        _spec(
            "instagram",
            "video",
            (
                _f("video_url", required=True, media_source=True),
                _f("video_caption"),
                _f("video_type", choices=_INSTAGRAM_VIDEO_TYPES),
                _f("text"),
            ),
        )
    )
    add(
        _spec(
            "instagram",
            "reply",
            (_f("text", required=True),),
        )
    )

    # --- LinkedIn ---
    add(
        _spec(
            "linkedin",
            "post",
            (
                _f("text"),
                _f("link", http_url=True),
                _f("images", "str_list", max_items=MAX_IMAGES, min_items=1, media_source=True),
            ),
            require_one_of=(("text", "link", "images"),),
        )
    )
    add(_spec("linkedin", "video", _COMMON_VIDEO))
    add(
        _spec(
            "linkedin",
            "reply",
            (
                _f("text"),
                _f("images", "str_list", max_items=MAX_IMAGES, min_items=1, media_source=True),
            ),
            require_one_of=(("text", "images"),),
        )
    )

    # --- Discord ---
    add(
        _spec(
            "discord",
            "post",
            (
                *_COMMON_POST,
                _f("embeds", "map_list", max_items=10),
            ),
            require_one_of=(("text", "link", "images", "embeds"),),
        )
    )
    add(
        _spec(
            "discord",
            "reply",
            (
                *_COMMON_REPLY,
                _f("embeds", "map_list", max_items=10),
            ),
            require_one_of=(("text", "images", "video_url", "embeds"),),
        )
    )
    add(
        _spec(
            "discord",
            "video",
            (
                _f("video_url", required=True, media_source=True),
                _f("video_title"),
                _f("text"),
                _f("embeds", "map_list", max_items=10),
            ),
        )
    )
    add(
        _spec(
            "discord",
            "thread",
            (
                _f("thread_name", required=True, max_length=100),
                _f("auto_archive_duration", "int", choices=frozenset(str(v) for v in _DISCORD_ARCHIVE)),
                _f("entries", "entries", required=True, min_items=MIN_THREAD_ENTRIES, max_items=MAX_THREAD_ENTRIES),
            ),
            entry_fields=(
                *_THREAD_ENTRY_BASE,
                _f("embeds", "map_list", max_items=10),
            ),
            entry_require_one_of=(("text", "link", "images", "video_url", "embeds"),),
            entry_conflicts=_THREAD_ENTRY_CONFLICTS,
        )
    )

    # --- YouTube ---
    add(
        _spec(
            "youtube",
            "video",
            (
                _f("video_url", required=True, media_source=True),
                _f("title", required=True),
                _f("description"),
                _f("category_id"),
                _f("privacy", default="private", choices=_YOUTUBE_PRIVACY),
                _f("keywords", "str_list"),
            ),
        )
    )
    add(
        _spec(
            "youtube",
            "reply",
            (_f("text", required=True),),
        )
    )

    # --- TikTok ---
    add(
        _spec(
            "tiktok",
            "post",
            (
                _f("images", "str_list", required=True, max_items=MAX_IMAGES, min_items=1, media_source=True),
                _f("title"),
                _f("description"),
                _f("privacy", default="SELF_ONLY", choices=_TIKTOK_PRIVACY),
                _f("allow_comments", "bool"),
                _f("auto_add_music", "bool"),
                _f("brand_organic", "bool"),
                _f("brand_content", "bool"),
            ),
        )
    )
    add(
        _spec(
            "tiktok",
            "video",
            (
                _f("video_url", required=True, media_source=True),
                _f("title", required=True),
                _f("privacy", default="SELF_ONLY", choices=_TIKTOK_PRIVACY),
                _f("allow_comments", "bool"),
                _f("allow_duet", "bool"),
                _f("allow_stitch", "bool"),
                _f("brand_organic", "bool"),
                _f("brand_content", "bool"),
            ),
        )
    )

    # --- Meta Threads ---
    add(
        _spec(
            "threads",
            "post",
            (
                *_COMMON_POST,
                _f("who_can_reply", default="everyone", choices=_THREADS_REPLY),
                _f("alt_texts", "str_list", max_items=MAX_IMAGES),
            ),
            require_one_of=(("text", "link", "images"),),
        )
    )
    add(
        _spec(
            "threads",
            "video",
            (
                _f("video_url", required=True, media_source=True),
                _f("video_title"),
                _f("text"),
                _f("who_can_reply", default="everyone", choices=_THREADS_REPLY),
            ),
        )
    )
    add(
        _spec(
            "threads",
            "reply",
            (
                *_COMMON_REPLY,
                _f("who_can_reply", default="everyone", choices=_THREADS_REPLY),
                _f("alt_texts", "str_list", max_items=MAX_IMAGES),
            ),
            require_one_of=(("text", "images", "video_url"),),
        )
    )
    add(
        _spec(
            "threads",
            "thread",
            (
                _f("who_can_reply", default="everyone", choices=_THREADS_REPLY),
                _f("entries", "entries", required=True, min_items=MIN_THREAD_ENTRIES, max_items=MAX_THREAD_ENTRIES),
            ),
            entry_fields=(
                *_THREAD_ENTRY_BASE,
                _f("alt_texts", "str_list", max_items=MAX_IMAGES),
            ),
            entry_require_one_of=_THREAD_ENTRY_REQUIRE,
            entry_conflicts=_THREAD_ENTRY_CONFLICTS,
        )
    )

    # --- Telegram ---
    add(
        _spec(
            "telegram",
            "post",
            (
                *_COMMON_POST,
                _f("parse_mode", default="HTML", choices=_TELEGRAM_PARSE),
            ),
            require_one_of=(("text", "link", "images"),),
        )
    )
    add(
        _spec(
            "telegram",
            "reply",
            (
                *_COMMON_REPLY,
                _f("parse_mode", default="HTML", choices=_TELEGRAM_PARSE),
            ),
            require_one_of=(("text", "images", "video_url"),),
        )
    )
    add(
        _spec(
            "telegram",
            "video",
            (
                *_COMMON_VIDEO,
                _f("parse_mode", default="HTML", choices=_TELEGRAM_PARSE),
            ),
        )
    )

    # --- WhatsApp ---
    add(
        _spec(
            "whatsapp",
            "post",
            _COMMON_POST,
            require_one_of=(("text", "link", "images"),),
        )
    )
    add(
        _spec(
            "whatsapp",
            "reply",
            _COMMON_REPLY,
            require_one_of=(("text", "images", "video_url"),),
        )
    )
    add(_spec("whatsapp", "video", _COMMON_VIDEO))
    add(
        _spec(
            "whatsapp",
            "template",
            (
                _f("template_name", required=True),
                _f("language_code", default="en"),
                _f("template_components", "any"),
            ),
        )
    )

    return specs


CONTENT_SPECS: Dict[Tuple[str, str], ActionSpec] = _build_specs()

# Union of all content keys across specs (for incompatible-vs-unknown).
ALL_CONTENT_KEYS: FrozenSet[str] = frozenset(
    key
    for spec in CONTENT_SPECS.values()
    for key in list(spec.allowed_keys)
    + [f.name for f in spec.entry_fields]
    + ["version", "entries", "thread_name", "auto_archive_duration"]
) | frozenset(
    {
        "text",
        "link",
        "images",
        "image_1",
        "image_2",
        "image_3",
        "image_4",
        "video_url",
        "video_title",
        "video_description",
        "video_type",
        "video_caption",
        "title",
        "description",
        "category_id",
        "privacy",
        "keywords",
        "allow_comments",
        "allow_duet",
        "allow_stitch",
        "auto_add_music",
        "brand_organic",
        "brand_content",
        "who_can_reply",
        "alt_texts",
        "parse_mode",
        "template_name",
        "language_code",
        "template_components",
        "embeds",
        "thread_name",
        "auto_archive_duration",
        "entries",
    }
)

# Destinations that conflict with --content when explicitly supplied on CLI.
INLINE_CONTENT_DESTINATIONS: FrozenSet[str] = frozenset(
    {
        "text",
        "link",
        "image_1",
        "image_2",
        "image_3",
        "image_4",
        "video_url",
        "video_title",
        "video_description",
        "video_type",
        "video_caption",
        "title",
        "description",
        "category_id",
        "privacy",
        "keywords",
        "allow_comments",
        "allow_duet",
        "allow_stitch",
        "auto_add_music",
        "brand_organic",
        "brand_content",
        "who_can_reply",
        "alt_texts",
        "template_name",
        "language_code",
        "template_components",
        "embeds",
        "thread_name",
        "auto_archive_duration",
        "entries",
        # parse_mode is control for telegram (destination), not XOR content —
        # kept off this set intentionally.
    }
)


def canonical_platform(platform: str) -> str:
    """Normalize platform aliases for lookup (twitter stays twitter for alias parity)."""
    return platform.lower()


def get_action_spec(platform: str, action: str) -> ActionSpec:
    """Return ActionSpec or raise KeyError."""
    key = (canonical_platform(platform), action)
    if key not in CONTENT_SPECS:
        raise KeyError(f"No content specification for {platform}.{action}")
    return CONTENT_SPECS[key]


def supports_content_file(platform: str, action: str) -> bool:
    """True when (platform, action) accepts --content."""
    return (canonical_platform(platform), action) in CONTENT_SPECS
