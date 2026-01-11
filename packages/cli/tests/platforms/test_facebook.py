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
Tests for Facebook platform parser.
"""

from argparse import ArgumentParser

from agoras.cli.platforms.facebook import create_facebook_parser


def test_facebook_parser_creation():
    """Test that Facebook parser is created successfully."""
    root_parser = ArgumentParser()
    subparsers = root_parser.add_subparsers()

    parser = create_facebook_parser(subparsers)

    assert parser is not None


def test_facebook_post_requires_object_id():
    """Test that Facebook post requires object ID."""
    root_parser = ArgumentParser()
    subparsers = root_parser.add_subparsers(dest='platform')

    create_facebook_parser(subparsers)

    args = root_parser.parse_args([
        'facebook', 'post',
        '--access-token', 'token',
        '--object-id', 'page123',
        '--text', 'Hello Facebook'
    ])

    assert args.access_token == 'token'
    assert args.object_id == 'page123'
    assert args.text == 'Hello Facebook'


def test_facebook_video_has_extra_options():
    """Test that Facebook video has video-specific options."""
    root_parser = ArgumentParser()
    subparsers = root_parser.add_subparsers(dest='platform')

    create_facebook_parser(subparsers)

    args = root_parser.parse_args([
        'facebook', 'video',
        '--access-token', 'token',
        '--object-id', 'page123',
        '--video-url', 'video.mp4',
        '--video-title', 'Title',
        '--video-description', 'Description',
        '--video-type', 'TYPE'
    ])

    assert args.video_url == 'video.mp4'
    assert args.video_title == 'Title'
    assert args.video_description == 'Description'
    assert args.video_type == 'TYPE'


def test_facebook_share_has_profile_id():
    """Test that Facebook share has optional profile ID."""
    root_parser = ArgumentParser()
    subparsers = root_parser.add_subparsers(dest='platform')

    create_facebook_parser(subparsers)

    args = root_parser.parse_args([
        'facebook', 'share',
        '--access-token', 'token',
        '--post-id', 'post123',
        '--profile-id', 'profile456'
    ])

    assert args.post_id == 'post123'
    assert args.profile_id == 'profile456'
