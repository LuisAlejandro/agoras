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
"""
Base utilities for CLI.

This module provides common helper functions for argument parsing and
CLI utilities shared across platform commands.
"""

import os
import sys
from argparse import SUPPRESS, ArgumentParser, Namespace
from typing import Optional

from agoras.core.auth.storage import SecureTokenStorage

from .content import ContentError, add_content_file_option, ensure_content_source_xor
from .media_help import video_url_help

# Per-platform required env credential vars (content params excluded).
# A platform's env set is "complete" when every listed var is set.
PLATFORM_ENV_REQUIREMENTS = {
    "x": ["TWITTER_CONSUMER_KEY", "TWITTER_CONSUMER_SECRET", "TWITTER_OAUTH_TOKEN", "TWITTER_OAUTH_SECRET"],
    "twitter": ["TWITTER_CONSUMER_KEY", "TWITTER_CONSUMER_SECRET", "TWITTER_OAUTH_TOKEN", "TWITTER_OAUTH_SECRET"],
    "facebook": ["FACEBOOK_CLIENT_ID", "FACEBOOK_CLIENT_SECRET", "FACEBOOK_REFRESH_TOKEN"],
    "instagram": ["INSTAGRAM_CLIENT_ID", "INSTAGRAM_CLIENT_SECRET", "INSTAGRAM_REFRESH_TOKEN"],
    "linkedin": ["LINKEDIN_CLIENT_ID", "LINKEDIN_CLIENT_SECRET"],
    "youtube": ["YOUTUBE_CLIENT_ID", "YOUTUBE_CLIENT_SECRET", "YOUTUBE_REFRESH_TOKEN"],
    "tiktok": ["TIKTOK_CLIENT_KEY", "TIKTOK_CLIENT_SECRET", "TIKTOK_REFRESH_TOKEN"],
    "threads": ["THREADS_APP_ID", "THREADS_APP_SECRET", "THREADS_REFRESH_TOKEN"],
    "discord": ["DISCORD_BOT_TOKEN", "DISCORD_SERVER_NAME", "DISCORD_CHANNEL_NAME"],
    "telegram": ["TELEGRAM_BOT_TOKEN", "TELEGRAM_CHAT_ID"],
    "whatsapp": ["WHATSAPP_ACCESS_TOKEN", "WHATSAPP_PHONE_NUMBER_ID"],
}


def _linkedin_env_complete() -> bool:
    """Return whether the LinkedIn env credential set is complete."""
    if not (os.environ.get("LINKEDIN_CLIENT_ID") and os.environ.get("LINKEDIN_CLIENT_SECRET")):
        return False
    return bool(os.environ.get("LINKEDIN_REFRESH_TOKEN") or os.environ.get("LINKEDIN_ACCESS_TOKEN"))


def env_credential_state(platform: str) -> str:
    """Return the env credential state for a platform: complete, partial, or none.

    ``complete`` means every required env var is set (env wins wholesale).
    ``partial`` means some but not all are set (fail fast, no silent blend).
    ``none`` means no env credential vars are set (fall through to storage).
    """
    if platform == "linkedin":
        required = PLATFORM_ENV_REQUIREMENTS["linkedin"]
        if _linkedin_env_complete():
            return "complete"
        if any(os.environ.get(v) for v in required):
            return "partial"
        return "none"

    required = PLATFORM_ENV_REQUIREMENTS.get(platform, [])
    if not required:
        return "none"
    present = [v for v in required if os.environ.get(v)]
    if len(present) == len(required):
        return "complete"
    if present:
        return "partial"
    return "none"


def add_profile_option(parser: ArgumentParser):
    """Add a ``--profile`` option for credential profile selection."""
    parser.add_argument(
        "--profile",
        metavar="<app@account>",
        help="Credential profile (app@account composite) to use",
    )


def add_profile_to_all(actions):
    """Add a ``--profile`` option to every subcommand of a platform."""
    for subparser in actions.choices.values():
        add_profile_option(subparser)


def _list_profiles(platform: str) -> list:
    """Return the stored profile identifiers for a platform."""
    storage = SecureTokenStorage()
    return [identifier for p, identifier in storage.list_tokens(platform) if p == platform]


def _read_tty_choice(profiles: list, platform: str) -> str:
    """Present a text menu on /dev/tty and return the chosen profile.

    Reads from /dev/tty (not stdin) so piped content is never consumed.
    """
    with open("/dev/tty", "r") as tty:
        print(f"Multiple profiles found for {platform}. Select one:", file=sys.stderr)
        for i, profile in enumerate(profiles, 1):
            print(f"  {i}. {profile}", file=sys.stderr)
        while True:
            print("Enter number: ", end="", file=sys.stderr, flush=True)
            line = tty.readline()
            if not line:
                raise SystemExit(2)
            try:
                idx = int(line.strip())
            except ValueError:
                continue
            if 1 <= idx <= len(profiles):
                return profiles[idx - 1]


def resolve_profile(platform: str, profile_arg: Optional[str]) -> Optional[str]:
    """Resolve the effective credential profile for a platform action.

    Returns the profile identifier to use, or None when no stored profiles
    exist (caller falls through to the MISSING/authorize path). Raises
    SystemExit(2) for an invalid explicit selector or a non-interactive
    multi-profile selection.
    """
    profiles = _list_profiles(platform)
    if profile_arg:
        if profile_arg not in profiles:
            available = ", ".join(profiles) if profiles else "(none)"
            print(f"error: profile '{profile_arg}' not found for {platform}. Available: {available}", file=sys.stderr)
            raise SystemExit(2)
        return profile_arg
    if not profiles:
        return None
    if len(profiles) == 1:
        return profiles[0]
    if sys.stdin.isatty():
        return _read_tty_choice(profiles, platform)
    available = ", ".join(profiles)
    print(f"error: multiple profiles for {platform}. Pass --profile. Available: {available}", file=sys.stderr)
    raise SystemExit(2)


def resolve_action_profile(platform: str, args: Namespace, legacy_args: dict) -> None:
    """Resolve and inject the profile for a non-authorize action.

    Authorize creates a new profile, so selection is skipped there. For other
    actions the resolution order is: explicit selector → complete env set →
    single stored profile → (multi-profile) interactive menu or non-interactive
    fail-hard.

    - An explicit ``--profile`` makes the selected profile the sole credential
      source; env is not consulted.
    - A complete env set (no selector) wins wholesale; stored profiles are
      ignored and no profile is injected.
    - A partial env set (no selector) fails fast rather than silently blending
      with stored profiles.
    """
    if getattr(args, "action", None) == "authorize":
        return

    profile_arg = getattr(args, "profile", None)
    if profile_arg:
        profile = resolve_profile(platform, profile_arg)
        if profile:
            legacy_args["profile"] = profile
        return

    state = env_credential_state(platform)
    if state == "complete":
        # Env is a self-contained profile; stored profiles are ignored.
        return
    if state == "partial":
        missing = [v for v in PLATFORM_ENV_REQUIREMENTS.get(platform, []) if not os.environ.get(v)]
        if platform == "linkedin" and not missing:
            missing = ["LINKEDIN_REFRESH_TOKEN or LINKEDIN_ACCESS_TOKEN"]
        print(
            f"error: incomplete {platform} environment credentials. Missing: {', '.join(missing)}. "
            "Set all env vars or pass --profile.",
            file=sys.stderr,
        )
        raise SystemExit(2)

    profile = resolve_profile(platform, None)
    if profile:
        legacy_args["profile"] = profile


def add_common_content_options(parser: ArgumentParser, images: int = 0, *, with_content_file: bool = True):
    """
    Add common content options (text, link, images) and optional --content.

    Content destinations use SUPPRESS so unspecified flags are absent from the
    Namespace (required for --content XOR detection and file-only mode).
    """
    if with_content_file:
        add_content_file_option(parser)

    content = parser.add_argument_group("Content Options")

    content.add_argument("--text", default=SUPPRESS, help="Text content of the post")
    content.add_argument("--link", default=SUPPRESS, help="URL to include in post")

    if images > 0:
        for i in range(1, images + 1):
            content.add_argument(
                f"--image-{i}",
                default=SUPPRESS,
                metavar="<media>",
                help=f"HTTP(s) URL, local path, or file:// URI #{i}",
            )


def add_video_options(parser: ArgumentParser, platform: Optional[str] = None, *, with_content_file: bool = True):
    """
    Add video-specific options.

    ``--video-url`` is not argparse-required so --content can supply it; the
    shared content contract enforces requiredness after parse.
    """
    if with_content_file:
        add_content_file_option(parser)

    help_text = video_url_help(platform) if platform else "HTTP(s) URL, local path, or file:// URI of video file"
    video = parser.add_argument_group("Video Options")
    video.add_argument(
        "--video-url",
        default=SUPPRESS,
        metavar="<media>",
        help=help_text,
    )
    video.add_argument(
        "--video-title",
        default=SUPPRESS,
        metavar="<title>",
        help="Video title/description",
    )


def prepare_content_args(args: Namespace, platform: str) -> None:
    """Apply content-file XOR rules and required-field checks for an action."""
    action = getattr(args, "action", None)
    if not action:
        return
    try:
        ensure_content_source_xor(args, platform, action)
    except ContentError as exc:
        raise SystemExit(f"error: {exc}") from exc
