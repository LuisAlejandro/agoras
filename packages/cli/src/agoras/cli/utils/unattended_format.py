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
Export stored credentials as unattended.env-style shell variables.
"""

import os
import shlex
from dataclasses import dataclass
from typing import Callable, Optional

from agoras.core.auth.storage import SecureTokenStorage

TokenGetter = Callable[[dict], Optional[str]]


@dataclass(frozen=True)
class PlatformSection:
    """One platform block in unattended.env output."""

    platform: str
    header: str
    env_vars: tuple[tuple[str, TokenGetter], ...]


def _field(name: str) -> TokenGetter:
    def getter(token_data: dict) -> Optional[str]:
        value = token_data.get(name)
        if value is None:
            return None
        return str(value)

    return getter


def _facebook_app_id(token_data: dict) -> Optional[str]:
    client_id = token_data.get("client_id")
    if client_id is None:
        return None
    return str(client_id)


def _empty(_token_data: dict) -> Optional[str]:
    return None


PLATFORM_SECTIONS: tuple[PlatformSection, ...] = (
    PlatformSection(
        platform="x",
        header="# X (Twitter) - OAuth 1.0a",
        env_vars=(
            ("TWITTER_CONSUMER_KEY", _field("consumer_key")),
            ("TWITTER_CONSUMER_SECRET", _field("consumer_secret")),
            ("TWITTER_OAUTH_TOKEN", _field("oauth_token")),
            ("TWITTER_OAUTH_SECRET", _field("oauth_secret")),
        ),
    ),
    PlatformSection(
        platform="facebook",
        header="# Facebook - OAuth 2.0",
        env_vars=(
            ("FACEBOOK_APP_ID", _facebook_app_id),
            ("FACEBOOK_OBJECT_ID", _field("user_id")),
            ("FACEBOOK_CLIENT_ID", _field("client_id")),
            ("FACEBOOK_CLIENT_SECRET", _field("client_secret")),
            ("FACEBOOK_REFRESH_TOKEN", _field("refresh_token")),
        ),
    ),
    PlatformSection(
        platform="instagram",
        header="# Instagram - OAuth 2.0",
        env_vars=(
            ("INSTAGRAM_CLIENT_ID", _field("client_id")),
            ("INSTAGRAM_CLIENT_SECRET", _field("client_secret")),
            ("INSTAGRAM_OBJECT_ID", _field("user_id")),
            ("INSTAGRAM_REFRESH_TOKEN", _field("refresh_token")),
        ),
    ),
    PlatformSection(
        platform="linkedin",
        header="# LinkedIn - OAuth 2.0",
        env_vars=(
            ("LINKEDIN_CLIENT_ID", _field("client_id")),
            ("LINKEDIN_CLIENT_SECRET", _field("client_secret")),
            ("LINKEDIN_OBJECT_ID", _field("user_id")),
            ("LINKEDIN_REFRESH_TOKEN", _field("refresh_token")),
            ("LINKEDIN_ACCESS_TOKEN", _field("access_token")),
        ),
    ),
    PlatformSection(
        platform="youtube",
        header="# YouTube - OAuth 2.0",
        env_vars=(
            ("YOUTUBE_CLIENT_ID", _field("client_id")),
            ("YOUTUBE_CLIENT_SECRET", _field("client_secret")),
            ("YOUTUBE_REFRESH_TOKEN", _field("refresh_token")),
        ),
    ),
    PlatformSection(
        platform="tiktok",
        header="# TikTok - OAuth 2.0",
        env_vars=(
            ("TIKTOK_USERNAME", _field("username")),
            ("TIKTOK_CLIENT_KEY", _field("client_key")),
            ("TIKTOK_CLIENT_SECRET", _field("client_secret")),
            ("TIKTOK_REFRESH_TOKEN", _field("refresh_token")),
        ),
    ),
    PlatformSection(
        platform="threads",
        header="# Threads - OAuth 2.0",
        env_vars=(
            ("THREADS_APP_ID", _field("app_id")),
            ("THREADS_APP_SECRET", _field("app_secret")),
            ("THREADS_REFRESH_TOKEN", _field("refresh_token")),
            ("THREADS_USER_ID", _field("user_id")),
        ),
    ),
    PlatformSection(
        platform="discord",
        header="# Discord - Bot Token",
        env_vars=(
            ("DISCORD_BOT_TOKEN", _field("bot_token")),
            ("DISCORD_SERVER_NAME", _field("server_name")),
            ("DISCORD_CHANNEL_NAME", _field("channel_name")),
        ),
    ),
    PlatformSection(
        platform="telegram",
        header="# Telegram - Bot Token",
        env_vars=(
            ("TELEGRAM_BOT_TOKEN", _field("bot_token")),
            ("TELEGRAM_CHAT_ID", _field("chat_id")),
        ),
    ),
    PlatformSection(
        platform="whatsapp",
        header="# WhatsApp - API Token",
        env_vars=(
            ("WHATSAPP_ACCESS_TOKEN", _field("access_token")),
            ("WHATSAPP_PHONE_NUMBER_ID", _field("phone_number_id")),
            ("WHATSAPP_RECIPIENT", _empty),
        ),
    ),
)

PLATFORM_SECTION_BY_NAME = {section.platform: section for section in PLATFORM_SECTIONS}


def load_platform_token(storage: SecureTokenStorage, platform: str) -> Optional[dict]:
    """
    Load token data for a platform using the same order as auth managers.

    Tries the ``default`` identifier first, then the first listed token.
    """
    token_data = storage.load_token(platform, "default")
    if token_data:
        return token_data

    for listed_platform, identifier in storage.list_tokens(platform):
        if listed_platform == platform:
            return storage.load_token(platform, identifier)

    return None


def _shell_env_line(name: str, value: Optional[str]) -> str:
    if not value:
        return f"{name}="
    if value.isalnum() or all(c in "._-:@/" for c in value):
        return f"{name}={value}"
    return f"{name}={shlex.quote(value)}"


def build_section_lines(section: PlatformSection, token_data: dict) -> list[str]:
    """Build comment header and KEY=value lines for one platform section."""
    lines = [section.header]
    for env_name, getter in section.env_vars:
        lines.append(_shell_env_line(env_name, getter(token_data)))
    return lines


def _file_header() -> list[str]:
    lines = [
        "# Unattended Execution Environment Variables",
        "# ==========================================",
        "#",
        "# Workflow:",
        "#   1. Fill in credentials below",
        "#   2. Run test-unattended.sh to run tests using stored credentials",
        "",
    ]
    storage_dir = os.environ.get("AGORAS_STORAGE_DIR")
    if storage_dir:
        lines.append(f"# AGORAS_STORAGE_DIR={storage_dir}")
        lines.append("")
    return lines


def format_unattended_env(
    storage: SecureTokenStorage,
    platforms_filter: Optional[list[str]] = None,
) -> Optional[str]:
    """
    Format stored credentials as unattended.env content.

    Returns None when no matching platforms have stored tokens.
    """
    if platforms_filter:
        sections = []
        for platform in platforms_filter:
            section = PLATFORM_SECTION_BY_NAME.get(platform)
            if section is not None:
                sections.append(section)
    else:
        sections = list(PLATFORM_SECTIONS)

    output_lines = _file_header()
    included_any = False

    for section in sections:
        token_data = load_platform_token(storage, section.platform)
        if not token_data:
            continue

        if included_any:
            output_lines.append("")
        output_lines.extend(build_section_lines(section, token_data))
        included_any = True

    if not included_any:
        return None

    return "\n".join(output_lines) + "\n"
