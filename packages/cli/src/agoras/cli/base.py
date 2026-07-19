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

from argparse import SUPPRESS, ArgumentParser, Namespace
from typing import Optional

from .content import ContentError, add_content_file_option, ensure_content_source_xor
from .media_help import video_url_help


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
            content.add_argument(f"--image-{i}", default=SUPPRESS, help=f"Image URL #{i}")


def add_video_options(parser: ArgumentParser, platform: Optional[str] = None, *, with_content_file: bool = True):
    """
    Add video-specific options.

    ``--video-url`` is not argparse-required so --content can supply it; the
    shared content contract enforces requiredness after parse.
    """
    if with_content_file:
        add_content_file_option(parser)

    help_text = video_url_help(platform) if platform else "URL of video file to upload"
    video = parser.add_argument_group("Video Options")
    video.add_argument(
        "--video-url",
        default=SUPPRESS,
        metavar="<url>",
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
