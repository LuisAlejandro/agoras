#!/usr/bin/env python3
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
"""
Refresh unattended OAuth credentials without starting interactive authorization.

This script is test infrastructure only. It is intended to run at the end of
the live unattended suites, before storage cleanup and unattended.env sync.
"""

import argparse
import asyncio
import os
import sys
from dataclasses import dataclass
from typing import Awaitable, Callable, Optional

from agoras.platforms.facebook.auth import FacebookAuthManager
from agoras.platforms.instagram.auth import InstagramAuthManager
from agoras.platforms.linkedin.auth import LinkedInAuthManager
from agoras.platforms.threads.auth import ThreadsAuthManager
from agoras.platforms.tiktok.auth import TikTokAuthManager
from agoras.platforms.youtube.auth import YouTubeAuthManager

RefreshCallable = Callable[[], Awaitable[str]]


@dataclass(frozen=True)
class PlatformRefresh:
    """Refresh configuration for one unattended OAuth platform."""

    name: str
    required_env: tuple[str, ...]
    refresh: Callable[[], Awaitable[str]]


def _env(name: str) -> str:
    return os.environ.get(name, "")


def _missing_env(names: tuple[str, ...]) -> list[str]:
    return [name for name in names if not _env(name)]


def _save_if_rotated(manager, token_data: dict, token_field: str = "refresh_token") -> str:
    new_refresh_token = token_data.get(token_field)
    if not new_refresh_token:
        return "ok"
    if new_refresh_token == manager.refresh_token:
        return "ok"

    manager.refresh_token = new_refresh_token
    manager._save_credentials_to_storage()
    return "updated"


async def _refresh_youtube() -> str:
    manager = YouTubeAuthManager(
        client_id=_env("YOUTUBE_CLIENT_ID"),
        client_secret=_env("YOUTUBE_CLIENT_SECRET"),
        refresh_token=_env("YOUTUBE_REFRESH_TOKEN"),
    )
    token_data = await manager._refresh_access_token_with_authlib()
    if "access_token" not in token_data:
        raise RuntimeError("missing access_token")
    return _save_if_rotated(manager, token_data)


async def _refresh_facebook() -> str:
    manager = FacebookAuthManager(
        user_id=_env("FACEBOOK_OBJECT_ID"),
        client_id=_env("FACEBOOK_CLIENT_ID"),
        client_secret=_env("FACEBOOK_CLIENT_SECRET"),
        refresh_token=_env("FACEBOOK_REFRESH_TOKEN"),
    )
    token_data = await manager._refresh_access_token()
    if "access_token" not in token_data:
        raise RuntimeError("missing access_token")
    return _save_if_rotated(manager, token_data, token_field="access_token")


async def _refresh_instagram() -> str:
    manager = InstagramAuthManager(
        user_id=_env("INSTAGRAM_OBJECT_ID"),
        client_id=_env("INSTAGRAM_CLIENT_ID"),
        client_secret=_env("INSTAGRAM_CLIENT_SECRET"),
        refresh_token=_env("INSTAGRAM_REFRESH_TOKEN"),
    )
    token_data = await manager._refresh_access_token()
    if "access_token" not in token_data:
        raise RuntimeError("missing access_token")
    return _save_if_rotated(manager, token_data, token_field="access_token")


async def _refresh_linkedin() -> str:
    refresh_token = _env("LINKEDIN_REFRESH_TOKEN")
    access_token = os.environ.get("LINKEDIN_ACCESS_TOKEN")
    if not refresh_token and access_token:
        return "skipped access-token-only credential"

    manager = LinkedInAuthManager(
        user_id=_env("LINKEDIN_OBJECT_ID"),
        client_id=_env("LINKEDIN_CLIENT_ID"),
        client_secret=_env("LINKEDIN_CLIENT_SECRET"),
        refresh_token=_env("LINKEDIN_REFRESH_TOKEN"),
    )

    def _sync_refresh() -> dict:
        return manager.oauth_session.refresh_token(
            token_url="https://www.linkedin.com/oauth/v2/accessToken",
            refresh_token=manager.refresh_token,
        )

    token_data = await asyncio.to_thread(_sync_refresh)
    if "access_token" not in token_data:
        raise RuntimeError("missing access_token")
    return _save_if_rotated(manager, token_data)


async def _refresh_tiktok() -> str:
    refresh_token = _env("TIKTOK_REFRESH_TOKEN")
    if refresh_token.startswith("access_only_"):
        return "skipped access-only token"

    manager = TikTokAuthManager(
        username=_env("TIKTOK_USERNAME"),
        client_key=_env("TIKTOK_CLIENT_KEY"),
        client_secret=_env("TIKTOK_CLIENT_SECRET"),
        refresh_token=refresh_token,
    )
    token_data = await manager._refresh_access_token()
    if "access_token" not in token_data:
        raise RuntimeError("missing access_token")
    return _save_if_rotated(manager, token_data)


async def _refresh_threads() -> str:
    user_id = _env("THREADS_USER_ID")
    manager = ThreadsAuthManager(
        app_id=_env("THREADS_APP_ID"),
        app_secret=_env("THREADS_APP_SECRET"),
        refresh_token=_env("THREADS_REFRESH_TOKEN"),
    )
    token_data = await manager._refresh_access_token()
    access_token = token_data.get("access_token")
    if not access_token:
        raise RuntimeError("missing access_token")
    if access_token == manager.refresh_token:
        return "ok"

    manager.refresh_token = access_token
    manager.user_id = user_id
    manager._save_credentials_to_storage(access_token, user_id)
    return "updated"


def _platform_refreshers() -> tuple[PlatformRefresh, ...]:
    return (
        PlatformRefresh(
            name="youtube",
            required_env=("YOUTUBE_CLIENT_ID", "YOUTUBE_CLIENT_SECRET", "YOUTUBE_REFRESH_TOKEN"),
            refresh=_refresh_youtube,
        ),
        PlatformRefresh(
            name="facebook",
            required_env=(
                "FACEBOOK_OBJECT_ID",
                "FACEBOOK_CLIENT_ID",
                "FACEBOOK_CLIENT_SECRET",
                "FACEBOOK_REFRESH_TOKEN",
            ),
            refresh=_refresh_facebook,
        ),
        PlatformRefresh(
            name="instagram",
            required_env=(
                "INSTAGRAM_OBJECT_ID",
                "INSTAGRAM_CLIENT_ID",
                "INSTAGRAM_CLIENT_SECRET",
                "INSTAGRAM_REFRESH_TOKEN",
            ),
            refresh=_refresh_instagram,
        ),
        PlatformRefresh(
            name="linkedin",
            required_env=(
                "LINKEDIN_OBJECT_ID",
                "LINKEDIN_CLIENT_ID",
                "LINKEDIN_CLIENT_SECRET",
                "LINKEDIN_REFRESH_TOKEN",
            ),
            refresh=_refresh_linkedin,
        ),
        PlatformRefresh(
            name="tiktok",
            required_env=("TIKTOK_USERNAME", "TIKTOK_CLIENT_KEY", "TIKTOK_CLIENT_SECRET", "TIKTOK_REFRESH_TOKEN"),
            refresh=_refresh_tiktok,
        ),
        PlatformRefresh(
            name="threads",
            required_env=("THREADS_APP_ID", "THREADS_APP_SECRET", "THREADS_REFRESH_TOKEN", "THREADS_USER_ID"),
            refresh=_refresh_threads,
        ),
    )


async def _run_refresh(platforms_filter: Optional[list[str]]) -> int:
    failures = 0
    selected = set(platforms_filter or [])

    for platform in _platform_refreshers():
        if selected and platform.name not in selected:
            continue

        missing = _missing_env(platform.required_env)
        if missing:
            print(f"SKIP refresh {platform.name}: missing {', '.join(missing)}", file=sys.stderr)
            continue

        try:
            result = await platform.refresh()
        except Exception as exc:
            failures += 1
            print(f"FAIL refresh {platform.name}: {exc}", file=sys.stderr)
            continue

        print(f"OK refresh {platform.name}: {result}", file=sys.stderr)

    return 1 if failures else 0


def main(argv: Optional[list[str]] = None) -> int:
    """Run noninteractive refresh checks for unattended OAuth credentials."""
    parser = argparse.ArgumentParser(description="Refresh unattended OAuth credentials without interactive auth.")
    parser.add_argument(
        "--platform",
        action="append",
        metavar="<platform>",
        dest="platforms",
        help="Limit refresh to platform(s); default: all refresh-capable unattended platforms",
    )
    args = parser.parse_args(argv)
    return asyncio.run(_run_refresh(args.platforms))


if __name__ == "__main__":
    sys.exit(main())
