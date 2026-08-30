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

from argparse import ArgumentParser, Namespace

import pytest

from agoras.cli.platforms.discord import create_discord_parser
from agoras.cli.platforms.facebook import create_facebook_parser
from agoras.cli.platforms.instagram import create_instagram_parser
from agoras.cli.platforms.linkedin import create_linkedin_parser
from agoras.cli.platforms.threads import create_threads_parser
from agoras.cli.platforms.tiktok import _handle_tiktok_command, create_tiktok_parser
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


def test_linkedin_reply_action():
    """Test LinkedIn reply action parses post-id and text."""
    root_parser = ArgumentParser()
    subparsers = root_parser.add_subparsers(dest='platform')

    create_linkedin_parser(subparsers)

    args = root_parser.parse_args([
        'linkedin', 'reply',
        '--post-id', 'urn:li:activity:123',
        '--text', 'A comment'
    ])

    assert args.action == 'reply'
    assert args.post_id == 'urn:li:activity:123'
    assert args.text == 'A comment'


def test_discord_parser_creation():
    """Test Discord parser creation."""
    root_parser = ArgumentParser()
    subparsers = root_parser.add_subparsers()

    parser = create_discord_parser(subparsers)
    assert parser is not None


def test_discord_post_parses_content_only():
    """Test Discord post parses without bot auth flags."""
    root_parser = ArgumentParser()
    subparsers = root_parser.add_subparsers(dest='platform')

    create_discord_parser(subparsers)

    args = root_parser.parse_args([
        'discord', 'post',
        '--text', 'Hello Discord'
    ])

    assert args.text == 'Hello Discord'


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


def test_youtube_reply_action():
    """Test YouTube reply action parses video-id and text."""
    root_parser = ArgumentParser()
    subparsers = root_parser.add_subparsers(dest='platform')

    create_youtube_parser(subparsers)

    args = root_parser.parse_args([
        'youtube', 'reply',
        '--video-id', 'video123',
        '--text', 'A comment'
    ])

    assert args.action == 'reply'
    assert args.video_id == 'video123'
    assert args.text == 'A comment'


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


def test_tiktok_reply_action():
    """Test TikTok reply action parses post-id and text."""
    root_parser = ArgumentParser()
    subparsers = root_parser.add_subparsers(dest='platform')

    create_tiktok_parser(subparsers)

    args = root_parser.parse_args([
        'tiktok', 'reply',
        '--post-id', 'video123',
        '--text', 'A comment'
    ])

    assert args.action == 'reply'
    assert args.post_id == 'video123'
    assert args.text == 'A comment'


def test_tiktok_reply_propagates_not_supported():
    """TikTok reply subcommand propagates the 'not supported' error through the CLI path."""
    from unittest.mock import patch

    from agoras.platforms.tiktok.wrapper import main as tiktok_main

    with patch("agoras.cli.platforms.tiktok.tiktok_main", wraps=tiktok_main) as mock_main:
        mock_main.side_effect = Exception("Reply not supported for <class 'agoras.platforms.tiktok.wrapper.TikTok'>")
        with pytest.raises(Exception, match="Reply not supported"):
            _handle_tiktok_command(
                Namespace(
                    action="reply",
                    post_id="video123",
                    text="A comment",
                    handler=None,
                )
            )


def test_tiktok_help_describes_composer_not_silent_public():
    """Interactive TikTok help mentions the localhost composer."""
    root_parser = ArgumentParser()
    subparsers = root_parser.add_subparsers(dest='platform')
    create_tiktok_parser(subparsers)
    tiktok_parser = subparsers.choices['tiktok']
    choices = tiktok_parser._subparsers._group_actions[0].choices
    post_help = choices['post'].format_help()
    video_help = choices['video'].format_help()
    assert 'localhost' in post_help
    assert 'localhost' in video_help
    assert 'composer' in video_help.lower()


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


def test_threads_reply_action():
    """Test Threads reply action parses post-id and text."""
    root_parser = ArgumentParser()
    subparsers = root_parser.add_subparsers(dest='platform')

    create_threads_parser(subparsers)

    args = root_parser.parse_args([
        'threads', 'reply',
        '--post-id', 'post123',
        '--text', 'A reply'
    ])

    assert args.action == 'reply'
    assert args.post_id == 'post123'
    assert args.text == 'A reply'


def test_threads_reply_media_flags():
    """Test Threads reply parses image and video media flags."""
    root_parser = ArgumentParser()
    subparsers = root_parser.add_subparsers(dest='platform')

    create_threads_parser(subparsers)

    args = root_parser.parse_args([
        'threads', 'reply',
        '--post-id', 'post123',
        '--text', 'A reply',
        '--image-1', 'http://example.com/a.jpg',
        '--video-url', 'http://example.com/v.mp4',
    ])

    assert args.action == 'reply'
    assert args.image_1 == 'http://example.com/a.jpg'
    assert args.video_url == 'http://example.com/v.mp4'


def test_facebook_reply_media_flag():
    """Test Facebook reply parses a single image media flag."""
    root_parser = ArgumentParser()
    subparsers = root_parser.add_subparsers(dest='platform')

    create_facebook_parser(subparsers)

    args = root_parser.parse_args([
        'facebook', 'reply',
        '--post-id', 'post123',
        '--text', 'A comment',
        '--image-1', 'http://example.com/a.jpg',
    ])

    assert args.action == 'reply'
    assert args.image_1 == 'http://example.com/a.jpg'


def test_linkedin_reply_media_flags():
    """Test LinkedIn reply parses image media flags."""
    root_parser = ArgumentParser()
    subparsers = root_parser.add_subparsers(dest='platform')

    create_linkedin_parser(subparsers)

    args = root_parser.parse_args([
        'linkedin', 'reply',
        '--post-id', 'urn:li:activity:123',
        '--text', 'A comment',
        '--image-1', 'http://example.com/a.jpg',
    ])

    assert args.action == 'reply'
    assert args.image_1 == 'http://example.com/a.jpg'


def test_instagram_reply_rejects_media_flag():
    """Test Instagram reply rejects media flags (text-only)."""
    root_parser = ArgumentParser()
    subparsers = root_parser.add_subparsers(dest='platform')

    create_instagram_parser(subparsers)

    with pytest.raises(SystemExit):
        root_parser.parse_args([
            'instagram', 'reply',
            '--post-id', 'media123',
            '--text', 'A comment',
            '--image-1', 'http://example.com/a.jpg',
        ])


def test_youtube_reply_rejects_media_flag():
    """Test YouTube reply rejects media flags (text-only)."""
    root_parser = ArgumentParser()
    subparsers = root_parser.add_subparsers(dest='platform')

    create_youtube_parser(subparsers)

    with pytest.raises(SystemExit):
        root_parser.parse_args([
            'youtube', 'reply',
            '--video-id', 'video123',
            '--text', 'A comment',
            '--image-1', 'http://example.com/a.jpg',
        ])


def test_discord_reply_action():
    """Test Discord reply action parses post-id and text."""
    root_parser = ArgumentParser()
    subparsers = root_parser.add_subparsers(dest='platform')

    create_discord_parser(subparsers)

    args = root_parser.parse_args([
        'discord', 'reply',
        '--post-id', 'msg123',
        '--text', 'A reply'
    ])

    assert args.action == 'reply'
    assert args.post_id == 'msg123'
    assert args.text == 'A reply'


def test_instagram_reply_action():
    """Test Instagram reply action parses post-id and text."""
    root_parser = ArgumentParser()
    subparsers = root_parser.add_subparsers(dest='platform')

    create_instagram_parser(subparsers)

    args = root_parser.parse_args([
        'instagram', 'reply',
        '--post-id', 'media123',
        '--text', 'A comment'
    ])

    assert args.action == 'reply'
    assert args.post_id == 'media123'
    assert args.text == 'A comment'


def test_threads_reply_requires_post_id():
    """Test Threads reply rejects a content-file reply without --post-id."""
    root_parser = ArgumentParser()
    subparsers = root_parser.add_subparsers(dest='platform')

    create_threads_parser(subparsers)

    with pytest.raises(SystemExit):
        root_parser.parse_args([
            'threads', 'reply',
            '--text', 'A reply',
            '--content', 'reply.yaml',
        ])
