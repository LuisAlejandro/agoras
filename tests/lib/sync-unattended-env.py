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
Patch *_REFRESH_TOKEN lines in unattended.env from tokens in AGORAS_STORAGE_DIR.

Invoked by live E2E test runners on EXIT (see tests/lib/common.sh).
"""

import argparse
import os
import re
import shlex
import sys
import tempfile
from pathlib import Path
from typing import Optional

from agoras.cli.utils.unattended_format import PLATFORM_SECTIONS, load_platform_token
from agoras.core.auth.storage import SecureTokenStorage

REFRESH_TOKEN_ENV_BY_PLATFORM: tuple[tuple[str, str], ...] = tuple(
    (section.platform, env_name)
    for section in PLATFORM_SECTIONS
    for env_name, _getter in section.env_vars
    if env_name.endswith("_REFRESH_TOKEN")
)


def _shell_env_line(name: str, value: Optional[str]) -> str:
    if not value:
        return f"{name}="
    if value.isalnum() or all(c in "._-:@/" for c in value):
        return f"{name}={value}"
    return f"{name}={shlex.quote(value)}"


def _parse_env_line_value(raw_value: str) -> str:
    """Parse the value portion of a shell env assignment."""
    raw_value = raw_value.strip()
    if not raw_value:
        return ""
    if raw_value[0] in "'\"":
        return shlex.split(raw_value)[0]
    return raw_value


def _env_assignment_pattern(env_name: str) -> re.Pattern[str]:
    return re.compile(rf"^(?:export\s+)?{re.escape(env_name)}=(.*)$")


def _collect_refresh_token_updates(
    storage: SecureTokenStorage,
    platforms_filter: Optional[list[str]] = None,
) -> dict[str, str]:
    """Map refresh-token env var names to values read from storage."""
    updates: dict[str, str] = {}
    for platform, env_name in REFRESH_TOKEN_ENV_BY_PLATFORM:
        if platforms_filter is not None and platform not in platforms_filter:
            continue
        token_data = load_platform_token(storage, platform)
        if not token_data:
            continue
        refresh_token = token_data.get("refresh_token")
        if refresh_token is None or refresh_token == "":
            continue
        updates[env_name] = str(refresh_token)
    return updates


def patch_unattended_env_refresh_tokens(  # noqa: C901
    env_path: str | Path,
    storage: SecureTokenStorage,
    platforms_filter: Optional[list[str]] = None,
) -> list[str]:
    """
    Patch *_REFRESH_TOKEN lines in an unattended.env file from stored tokens.

    Only lines whose values differ from storage are rewritten. Other file content
    (comments, FEED_URL, sheets fixtures, etc.) is preserved.

    Returns:
        Env var names that were updated or appended.

    Raises:
        FileNotFoundError: When env_path does not exist.
        OSError: When the file cannot be read or written.
    """
    path = Path(env_path)
    if not path.is_file():
        raise FileNotFoundError(f"Unattended env file not found: {path}")

    updates = _collect_refresh_token_updates(storage, platforms_filter)
    if not updates:
        return []

    original_text = path.read_text(encoding="utf-8")
    original_lines = original_text.splitlines(keepends=True)
    if not original_lines and original_text:
        original_lines = [original_text]

    found_keys: set[str] = set()
    new_lines: list[str] = []
    changed_keys: list[str] = []

    for line in original_lines:
        replaced = False
        for env_name, new_value in updates.items():
            match = _env_assignment_pattern(env_name).match(line.rstrip("\n"))
            if not match:
                continue
            found_keys.add(env_name)
            old_value = _parse_env_line_value(match.group(1))
            if old_value != new_value:
                changed_keys.append(env_name)
                new_line = _shell_env_line(env_name, new_value)
                if line.endswith("\n"):
                    new_line = new_line + "\n"
                new_lines.append(new_line)
            else:
                new_lines.append(line)
            replaced = True
            break
        if not replaced:
            new_lines.append(line)

    missing_keys = [env_name for env_name in updates if env_name not in found_keys]
    for env_name in missing_keys:
        new_value = updates[env_name]
        changed_keys.append(env_name)
        if new_lines and not new_lines[-1].endswith("\n"):
            new_lines[-1] = new_lines[-1] + "\n"
        if new_lines and new_lines[-1].strip():
            new_lines.append("\n")
        new_lines.append(_shell_env_line(env_name, new_value) + "\n")

    new_text = "".join(new_lines)
    if not changed_keys:
        return []

    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_path = tempfile.mkstemp(dir=path.parent, prefix=f".{path.name}.", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as tmp_file:
            tmp_file.write(new_text)
        os.replace(tmp_path, path)
    except Exception:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
        raise

    path.chmod(0o600)
    return changed_keys


def main(argv: list[str] | None = None) -> int:
    """Run refresh-token sync for an unattended.env file."""
    parser = argparse.ArgumentParser(description="Patch unattended.env refresh tokens from storage.")
    parser.add_argument(
        "--file",
        required=True,
        metavar="<path>",
        help="Path to unattended.env (or equivalent) to update in place",
    )
    parser.add_argument(
        "--platform",
        action="append",
        metavar="<platform>",
        dest="platforms",
        help="Limit sync to platform(s); default: all platforms with stored refresh tokens",
    )
    args = parser.parse_args(argv)

    storage = SecureTokenStorage()
    try:
        updated = patch_unattended_env_refresh_tokens(
            args.file,
            storage,
            platforms_filter=args.platforms,
        )
    except FileNotFoundError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    except OSError as exc:
        print(f"Failed to update unattended env file: {exc}", file=sys.stderr)
        return 1

    if updated:
        print(f"Updated refresh tokens in {args.file}: {', '.join(updated)}", file=sys.stderr)
    else:
        print("No refresh tokens in storage to sync.", file=sys.stderr)

    return 0


if __name__ == "__main__":
    sys.exit(main())
