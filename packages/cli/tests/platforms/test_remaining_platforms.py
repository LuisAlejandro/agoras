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
Tests for remaining platform parsers (Instagram, LinkedIn, Discord, YouTube, TikTok, Threads).
"""

from argparse import ArgumentParser

from agoras.cli.platforms.discord import create_discord_parser
from agoras.cli.platforms.instagram import create_instagram_parser
from agoras.cli.platforms.linkedin import create_linkedin_parser
from agoras.cli.platforms.threads import create_threads_parser
from agoras.cli.platforms.tiktok import create_tiktok_parser
from agoras.cli.platforms.youtube import create_youtube_parser


def test_instagram_parser_creation():
    """Test Instagram parser creation."""
    root_parser = ArgumentParser()
    subparsers = root_parser.add_subparsers()

    parser = create_instagram_parser(subparsers)
    assert parser is not None


def test_instagram_limited_actions():
    """Test Instagram has limited actions (no like/share/delete)."""
    root_parser = ArgumentParser()
    subparsers = root_parser.add_subparsers(dest='platform')

    create_instagram_parser(subparsers)

    # Should work: post
    args = root_parser.parse_args([
        'instagram', 'post',
        '--text', 'Hello Instagram'
    ])
    assert args.action == 'post'


def test_linkedin_parser_creation():
    """Test LinkedIn parser creation."""
    root_parser = ArgumentParser()
    subparsers = root_parser.add_subparsers()

    parser = create_linkedin_parser(subparsers)
    assert parser is not None


def test_linkedin_full_actions():
    """Test LinkedIn has full action set."""
    root_parser = ArgumentParser()
    subparsers = root_parser.add_subparsers(dest='platform')

    create_linkedin_parser(subparsers)

    # Test various actions
    args = root_parser.parse_args([
        'linkedin', 'post',
        '--text', 'Hello LinkedIn'
    ])
    assert args.action == 'post'


def test_discord_parser_creation():
    """Test Discord parser creation."""
    root_parser = ArgumentParser()
    subparsers = root_parser.add_subparsers()

    parser = create_discord_parser(subparsers)
    assert parser is not None


def test_discord_unique_auth():
    """Test Discord has unique bot authentication."""
    root_parser = ArgumentParser()
    subparsers = root_parser.add_subparsers(dest='platform')

    create_discord_parser(subparsers)

    args = root_parser.parse_args([
        'discord', 'post',
        '--bot-token', 'BOT_TOKEN',
        '--server-name', 'MyServer',
        '--channel-name', 'general'
    ])

    assert args.bot_token == 'BOT_TOKEN'
    assert args.server_name == 'MyServer'
    assert args.channel_name == 'general'


def test_youtube_parser_creation():
    """Test YouTube parser creation."""
    root_parser = ArgumentParser()
    subparsers = root_parser.add_subparsers()

    parser = create_youtube_parser(subparsers)
    assert parser is not None


def test_youtube_video_only():
    """Test YouTube is video-only (no post action)."""
    root_parser = ArgumentParser()
    subparsers = root_parser.add_subparsers(dest='platform')

    create_youtube_parser(subparsers)

    # Should work: video
    args = root_parser.parse_args([
        'youtube', 'video',
        '--video-url', 'video.mp4'
    ])
    assert args.action == 'video'


def test_youtube_video_options():
    """Test YouTube has extended video options."""
    root_parser = ArgumentParser()
    subparsers = root_parser.add_subparsers(dest='platform')

    create_youtube_parser(subparsers)

    args = root_parser.parse_args([
        'youtube', 'video',
        '--video-url', 'video.mp4',
        '--title', 'Video Title',
        '--description', 'Description',
        '--category-id', '22',
        '--privacy', 'public',
        '--keywords', 'tag1,tag2'
    ])

    assert args.title == 'Video Title'
    assert args.description == 'Description'
    assert args.category_id == '22'
    assert args.privacy == 'public'
    assert args.keywords == 'tag1,tag2'


def test_tiktok_parser_creation():
    """Test TikTok parser creation."""
    root_parser = ArgumentParser()
    subparsers = root_parser.add_subparsers()

    parser = create_tiktok_parser(subparsers)
    assert parser is not None


def test_tiktok_video_only():
    """Test TikTok is video-only (no post action)."""
    root_parser = ArgumentParser()
    subparsers = root_parser.add_subparsers(dest='platform')

    create_tiktok_parser(subparsers)

    args = root_parser.parse_args([
        'tiktok', 'video',
        '--video-url', 'video.mp4'
    ])
    assert args.action == 'video'


def test_tiktok_privacy_options():
    """Test TikTok has unique privacy options."""
    root_parser = ArgumentParser()
    subparsers = root_parser.add_subparsers(dest='platform')

    create_tiktok_parser(subparsers)

    args = root_parser.parse_args([
        'tiktok', 'video',
        '--video-url', 'video.mp4',
        '--privacy', 'PUBLIC_TO_EVERYONE'
    ])

    assert args.privacy == 'PUBLIC_TO_EVERYONE'


def test_threads_parser_creation():
    """Test Threads parser creation."""
    root_parser = ArgumentParser()
    subparsers = root_parser.add_subparsers()

    parser = create_threads_parser(subparsers)
    assert parser is not None


def test_threads_actions():
    """Test Threads has specific action set."""
    root_parser = ArgumentParser()
    subparsers = root_parser.add_subparsers(dest='platform')

    create_threads_parser(subparsers)

    # Test post action
    args = root_parser.parse_args([
        'threads', 'post',
        '--text', 'Hello Threads',
        '--image-1', 'img.jpg'
    ])
    assert args.action == 'post'
    assert args.text == 'Hello Threads'


def test_threads_share_action():
    """Test Threads share action requires post ID."""
    root_parser = ArgumentParser()
    subparsers = root_parser.add_subparsers(dest='platform')

    create_threads_parser(subparsers)

    args = root_parser.parse_args([
        'threads', 'share',
        '--post-id', 'post123'
    ])

    assert args.post_id == 'post123'
