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

from dataclasses import dataclass
from typing import Dict, FrozenSet, Literal, Optional, Tuple

MediaKind = Literal['image', 'video']
TransferMode = Literal['upload_bytes', 'url_pull']

MB = 1024 * 1024
GB = 1024 * 1024 * 1024

GENERIC_IMAGE_MIME = frozenset({'image/jpeg', 'image/png', 'image/jpg'})
GENERIC_VIDEO_MIME = frozenset({
    'video/mp4', 'video/mov', 'video/webm', 'video/avi',
})
YOUTUBE_VIDEO_MIME = GENERIC_VIDEO_MIME | frozenset({'video/quicktime'})


@dataclass(frozen=True)
class MediaConstraints:
    """Platform media limits shared across agoras modules."""

    mime_types: FrozenSet[str]
    max_bytes: Optional[int] = None
    min_duration_s: Optional[float] = None
    max_duration_s: Optional[float] = None
    max_width: Optional[int] = None
    max_height: Optional[int] = None
    min_width: Optional[int] = None
    min_height: Optional[int] = None
    max_images_per_post: Optional[int] = None

    @property
    def mime_type_list(self):
        return sorted(self.mime_types)


# CLI / wrapper class names -> canonical contract keys
PLATFORM_ALIASES: Dict[str, str] = {
    'x': 'twitter',
    'X': 'twitter',
    'twitter': 'twitter',
    'discord': 'discord',
    'Discord': 'discord',
    'facebook': 'facebook',
    'Facebook': 'facebook',
    'instagram': 'instagram',
    'Instagram': 'instagram',
    'linkedin': 'linkedin',
    'LinkedIn': 'linkedin',
    'youtube': 'youtube',
    'YouTube': 'youtube',
    'tiktok': 'tiktok',
    'TikTok': 'tiktok',
    'threads': 'threads',
    'Threads': 'threads',
    'telegram': 'telegram',
    'Telegram': 'telegram',
    'whatsapp': 'whatsapp',
    'WhatsApp': 'whatsapp',
}

IMAGE: Dict[str, MediaConstraints] = {
    # Discord bot upload limit (non-Nitro)
    'discord': MediaConstraints(
        mime_types=GENERIC_IMAGE_MIME | frozenset({'image/webp'}),
        max_bytes=8 * MB,
    ),
    'twitter': MediaConstraints(
        mime_types=GENERIC_IMAGE_MIME,
        max_bytes=5 * MB,
        max_width=8192,
        max_height=8192,
    ),
    'facebook': MediaConstraints(
        mime_types=GENERIC_IMAGE_MIME,
        max_bytes=4 * MB,
    ),
    'instagram': MediaConstraints(
        mime_types=GENERIC_IMAGE_MIME,
        max_bytes=8 * MB,
        max_width=1440,
        max_height=1440,
    ),
    # LinkedIn images API: 5 MB JPEG/PNG, max 6012px per side
    'linkedin': MediaConstraints(
        mime_types=GENERIC_IMAGE_MIME,
        max_bytes=5 * MB,
        max_width=6012,
        max_height=6012,
    ),
    # TikTok photo post via PULL_FROM_URL
    'tiktok': MediaConstraints(
        mime_types=frozenset({'image/jpeg', 'image/png', 'image/jpg'}),
        max_bytes=20 * MB,
    ),
    'threads': MediaConstraints(
        mime_types=frozenset({'image/jpeg', 'image/png', 'image/jpg'}),
        max_bytes=8 * MB,
        max_width=1440,
        max_height=1440,
        max_images_per_post=4,
    ),
    'telegram': MediaConstraints(
        mime_types=GENERIC_IMAGE_MIME | frozenset({'image/webp'}),
        max_bytes=10 * MB,
    ),
}

VIDEO: Dict[str, MediaConstraints] = {
    'discord': MediaConstraints(
        mime_types=frozenset({'video/mp4'}) | GENERIC_VIDEO_MIME,
        max_bytes=8 * MB,
    ),
    'twitter': MediaConstraints(
        mime_types=frozenset({'video/mp4'}),
        max_bytes=512 * MB,
    ),
    'facebook': MediaConstraints(
        mime_types=frozenset({'video/mp4'}),
        max_bytes=4 * GB,
    ),
    'instagram': MediaConstraints(
        mime_types=frozenset({'video/mp4'}),
        max_bytes=4 * GB,
        max_duration_s=90 * 60,
    ),
    # LinkedIn Videos API: MP4, 75KB–500MB, 3s–30min
    'linkedin': MediaConstraints(
        mime_types=frozenset({'video/mp4'}),
        max_bytes=500 * MB,
        min_duration_s=3,
        max_duration_s=30 * 60,
    ),
    'youtube': MediaConstraints(
        mime_types=YOUTUBE_VIDEO_MIME,
        max_bytes=256 * GB,
        max_duration_s=12 * 60 * 60,
    ),
    'tiktok': MediaConstraints(
        mime_types=frozenset({'video/mp4', 'video/webm', 'video/quicktime'}),
        max_bytes=2 * GB,
        max_duration_s=10 * 60,
        min_duration_s=3,
    ),
    'threads': MediaConstraints(
        mime_types=GENERIC_VIDEO_MIME,
        max_bytes=4 * GB,
    ),
    'whatsapp': MediaConstraints(
        mime_types=frozenset({'video/mp4', 'video/3gp', 'video/3gpp'}),
        max_bytes=16 * MB,
    ),
    'telegram': MediaConstraints(
        mime_types=GENERIC_VIDEO_MIME,
        max_bytes=50 * MB,
    ),
}

TRANSFER: Dict[str, Dict[MediaKind, TransferMode]] = {
    'tiktok': {'image': 'url_pull'},
    'threads': {'image': 'url_pull', 'video': 'upload_bytes'},
}

def resolve_platform(name: str) -> str:
    """Map CLI, class, or env names to canonical platform keys."""
    if not name:
        return 'generic'
    key = PLATFORM_ALIASES.get(name, name.lower())
    return key


def image_limits(platform: str) -> MediaConstraints:
    """Return image constraints for a platform (generic fallback)."""
    key = resolve_platform(platform)
    return IMAGE.get(key, MediaConstraints(mime_types=GENERIC_IMAGE_MIME))


def video_limits(platform: str) -> MediaConstraints:
    """Return video constraints for a platform (generic fallback)."""
    key = resolve_platform(platform)
    return VIDEO.get(key, MediaConstraints(mime_types=GENERIC_VIDEO_MIME))


def transfer_mode(platform: str, kind: MediaKind) -> TransferMode:
    """Return how media is sent to the platform API."""
    key = resolve_platform(platform)
    return TRANSFER.get(key, {}).get(kind, 'upload_bytes')


# Canonical keys for CLI platforms with post/video actions (x → twitter).
REGISTRY_MEDIA_PLATFORM_KEYS: FrozenSet[str] = frozenset({
    'twitter', 'facebook', 'instagram', 'linkedin', 'discord',
    'youtube', 'tiktok', 'threads', 'telegram', 'whatsapp',
})


def platforms_with_post_or_video() -> FrozenSet[str]:
    """Canonical platforms that accept images or videos via CLI."""
    return REGISTRY_MEDIA_PLATFORM_KEYS


def format_bytes(num_bytes: Optional[int]) -> str:
    """Human-readable byte size for CLI help."""
    if num_bytes is None:
        return 'unknown'
    if num_bytes >= GB:
        return f'{num_bytes // GB}GB'
    if num_bytes >= MB:
        return f'{num_bytes // MB}MB'
    if num_bytes >= 1024:
        return f'{num_bytes // 1024}KB'
    return f'{num_bytes}B'


def constraints_summary(platform: str, kind: MediaKind) -> Tuple[MediaConstraints, TransferMode]:
    """Return limits and transfer mode for CLI / scripts."""
    limits = image_limits(platform) if kind == 'image' else video_limits(platform)
    mode = transfer_mode(platform, kind)
    return limits, mode
