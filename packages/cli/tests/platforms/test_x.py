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
Tests for X platform parser.
"""

import sys
from argparse import ArgumentParser
from io import StringIO
from unittest.mock import patch

from agoras.cli.platforms.x import create_twitter_parser_alias, create_x_parser


def test_x_parser_creation():
    """Test that X parser is created successfully."""
    root_parser = ArgumentParser()
    subparsers = root_parser.add_subparsers()

    parser = create_x_parser(subparsers)

    assert parser is not None


def test_x_actions_listed():
    """Test that X post action parses without auth flags."""
    root_parser = ArgumentParser()
    subparsers = root_parser.add_subparsers(dest='platform')

    create_x_parser(subparsers)

    args = root_parser.parse_args(['x', 'post', '--text', 'Hello'])

    assert args.platform == 'x'
    assert args.action == 'post'
    assert args.text == 'Hello'


def test_x_post_has_content_options():
    """Test that X post has content options."""
    root_parser = ArgumentParser()
    subparsers = root_parser.add_subparsers(dest='platform')

    create_x_parser(subparsers)

    args = root_parser.parse_args([
        'x', 'post',
        '--text', 'Hello',
        '--image-1', 'img1.jpg',
        '--image-2', 'img2.jpg'
    ])

    assert args.text == 'Hello'
    assert args.image_1 == 'img1.jpg'
    assert args.image_2 == 'img2.jpg'


def test_x_video_has_video_options():
    """Test that X video has video options."""
    root_parser = ArgumentParser()
    subparsers = root_parser.add_subparsers(dest='platform')

    create_x_parser(subparsers)

    args = root_parser.parse_args([
        'x', 'video',
        '--video-url', 'video.mp4',
        '--video-title', 'My Video'
    ])

    assert args.video_url == 'video.mp4'
    assert args.video_title == 'My Video'


def test_x_like_requires_post_id():
    """Test that X like requires post ID."""
    root_parser = ArgumentParser()
    subparsers = root_parser.add_subparsers(dest='platform')

    create_x_parser(subparsers)

    args = root_parser.parse_args([
        'x', 'like',
        '--post-id', '12345'
    ])

    assert args.post_id == '12345'


def test_twitter_alias_parser_creation():
    """Test that Twitter alias parser is created successfully."""
    root_parser = ArgumentParser()
    subparsers = root_parser.add_subparsers()

    parser = create_twitter_parser_alias(subparsers)

    assert parser is not None


def test_twitter_alias_actions_listed():
    """Test that Twitter alias post parses without auth flags."""
    root_parser = ArgumentParser()
    subparsers = root_parser.add_subparsers(dest='platform')

    create_twitter_parser_alias(subparsers)

    args = root_parser.parse_args(['twitter', 'post', '--text', 'Hello'])

    assert args.platform == 'twitter'
    assert args.action == 'post'
    assert args.text == 'Hello'


def test_twitter_alias_shows_deprecation_warning():
    """Test that Twitter alias command shows deprecation warning."""
    from argparse import Namespace

    from agoras.cli.platforms.x import _handle_twitter_command

    stderr_capture = StringIO()

    args = Namespace(
        action='post',
        text='Hello'
    )

    with patch('sys.stderr', stderr_capture):
        try:
            _handle_twitter_command(args)
        except Exception:
            pass

    stderr_capture.seek(0)
    output = stderr_capture.read()
    assert 'deprecated' in output.lower() or 'Warning' in output
