# -*- coding: utf-8 -*-
#
# Please refer to AUTHORS.rst for a complete list of Copyright holders.
# Copyright (C) 2022-2023, Agoras Developers.

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
Tests for base CLI utilities.
"""

from argparse import ArgumentParser

from agoras.cli.base import (
    add_common_content_options,
    add_feed_options,
    add_video_options,
)


def test_add_common_content_options_no_images():
    """Test adding content options without images."""
    parser = ArgumentParser()
    add_common_content_options(parser, images=0)

    args = parser.parse_args(['--text', 'Hello', '--link', 'http://example.com'])

    assert args.text == 'Hello'
    assert args.link == 'http://example.com'


def test_add_common_content_options_with_images():
    """Test adding content options with images."""
    parser = ArgumentParser()
    add_common_content_options(parser, images=4)

    args = parser.parse_args([
        '--text', 'Hello',
        '--image-1', 'img1.jpg',
        '--image-2', 'img2.jpg',
        '--image-3', 'img3.jpg',
        '--image-4', 'img4.jpg'
    ])

    assert args.text == 'Hello'
    assert args.image_1 == 'img1.jpg'
    assert args.image_2 == 'img2.jpg'
    assert args.image_3 == 'img3.jpg'
    assert args.image_4 == 'img4.jpg'


def test_add_common_content_options_single_image():
    """Test adding content options with single image."""
    parser = ArgumentParser()
    add_common_content_options(parser, images=1)

    args = parser.parse_args(['--image-1', 'img.jpg'])

    assert args.image_1 == 'img.jpg'


def test_add_feed_options():
    """Test adding feed options."""
    parser = ArgumentParser()
    add_feed_options(parser)

    args = parser.parse_args([
        '--feed-url', 'https://example.com/feed.xml',
        '--max-count', '5',
        '--post-lookback', '3600',
        '--max-post-age', '7'
    ])

    assert args.feed_url == 'https://example.com/feed.xml'
    assert args.max_count == 5
    assert args.post_lookback == 3600
    assert args.max_post_age == 7


def test_add_video_options():
    """Test adding video options."""
    parser = ArgumentParser()
    add_video_options(parser)

    args = parser.parse_args([
        '--video-url', 'video.mp4',
        '--video-title', 'My Video'
    ])

    assert args.video_url == 'video.mp4'
    assert args.video_title == 'My Video'
