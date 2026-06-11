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
Base utilities for CLI.

This module provides common helper functions for argument parsing and
CLI utilities shared across platform commands.
"""

from argparse import ArgumentParser


def add_common_content_options(parser: ArgumentParser, images: int = 0):
    """
    Add common content options (text, link, images).

    Args:
        parser: ArgumentParser to add options to
        images: Number of image options to add (0-4)
    """
    content = parser.add_argument_group('Content Options')

    content.add_argument('--text',
                         help='Text content of the post')
    content.add_argument('--link',
                         help='URL to include in post')

    if images > 0:
        for i in range(1, images + 1):
            content.add_argument(f'--image-{i}',
                                 help=f'Image URL #{i}')


def add_video_options(parser: ArgumentParser, platform: str = None):
    """
    Add video-specific options.

    Args:
        parser: ArgumentParser to add options to
        platform: Optional platform key for contract-based --video-url help
    """
    from .media_help import video_url_help

    help_text = video_url_help(platform) if platform else 'URL of video file to upload'
    video = parser.add_argument_group('Video Options')
    video.add_argument(
        '--video-url',
        required=True,
        metavar='<url>',
        help=help_text,
    )
    video.add_argument(
        '--video-title',
        metavar='<title>',
        help='Video title/description',
    )
