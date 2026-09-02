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

from agoras.cli.converter import ParameterConverter
from agoras.cli.platforms.discord import create_discord_parser
from agoras.cli.platforms.facebook import create_facebook_parser
from agoras.cli.platforms.instagram import create_instagram_parser
from agoras.cli.platforms.linkedin import create_linkedin_parser
from agoras.cli.platforms.telegram import create_telegram_parser
from agoras.cli.platforms.threads import create_threads_parser
from agoras.cli.platforms.tiktok import _handle_tiktok_command, create_tiktok_parser
from agoras.cli.platforms.whatsapp import create_whatsapp_parser
from agoras.cli.platforms.x import create_x_parser
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


# ---------------------------------------------------------------------------
# delete-reply parser tests (R9: uniform --post-id across the 8 in-scope nets)
# ---------------------------------------------------------------------------


def test_threads_delete_reply_action():
    """Test Threads delete-reply parses post-id."""
    root_parser = ArgumentParser()
    subparsers = root_parser.add_subparsers(dest='platform')
    create_threads_parser(subparsers)

    args = root_parser.parse_args(['threads', 'delete-reply', '--post-id', 'post123'])

    assert args.action == 'delete-reply'
    assert args.post_id == 'post123'


def test_facebook_delete_reply_action():
    """Test Facebook delete-reply parses post-id."""
    root_parser = ArgumentParser()
    subparsers = root_parser.add_subparsers(dest='platform')
    create_facebook_parser(subparsers)

    args = root_parser.parse_args(['facebook', 'delete-reply', '--post-id', 'comment123'])

    assert args.action == 'delete-reply'
    assert args.post_id == 'comment123'


def test_instagram_delete_reply_action():
    """Test Instagram delete-reply parses post-id."""
    root_parser = ArgumentParser()
    subparsers = root_parser.add_subparsers(dest='platform')
    create_instagram_parser(subparsers)

    args = root_parser.parse_args(['instagram', 'delete-reply', '--post-id', 'comment123'])

    assert args.action == 'delete-reply'
    assert args.post_id == 'comment123'


def test_instagram_delete_action():
    """Test Instagram delete parses post-id."""
    root_parser = ArgumentParser()
    subparsers = root_parser.add_subparsers(dest='platform')
    create_instagram_parser(subparsers)

    args = root_parser.parse_args(['instagram', 'delete', '--post-id', 'media123'])

    assert args.action == 'delete'
    assert args.post_id == 'media123'


def test_youtube_delete_reply_action():
    """Test YouTube delete-reply parses post-id (the comment ID)."""
    root_parser = ArgumentParser()
    subparsers = root_parser.add_subparsers(dest='platform')
    create_youtube_parser(subparsers)

    args = root_parser.parse_args(['youtube', 'delete-reply', '--post-id', 'comment123'])

    assert args.action == 'delete-reply'
    assert args.post_id == 'comment123'


def test_discord_delete_reply_action():
    """Test Discord delete-reply parses post-id."""
    root_parser = ArgumentParser()
    subparsers = root_parser.add_subparsers(dest='platform')
    create_discord_parser(subparsers)

    args = root_parser.parse_args(['discord', 'delete-reply', '--post-id', 'msg123'])

    assert args.action == 'delete-reply'
    assert args.post_id == 'msg123'


def test_linkedin_delete_reply_action():
    """Test LinkedIn delete-reply parses post-id and parent-post-id."""
    root_parser = ArgumentParser()
    subparsers = root_parser.add_subparsers(dest='platform')
    create_linkedin_parser(subparsers)

    args = root_parser.parse_args([
        'linkedin', 'delete-reply',
        '--post-id', 'comment123',
        '--parent-post-id', 'urn:li:ugcPost:456',
    ])

    assert args.action == 'delete-reply'
    assert args.post_id == 'comment123'
    assert args.parent_post_id == 'urn:li:ugcPost:456'


def test_telegram_delete_reply_action():
    """Test Telegram delete-reply parses post-id."""
    root_parser = ArgumentParser()
    subparsers = root_parser.add_subparsers(dest='platform')
    create_telegram_parser(subparsers)

    args = root_parser.parse_args(['telegram', 'delete-reply', '--post-id', 'msg123'])

    assert args.action == 'delete-reply'
    assert args.post_id == 'msg123'


def test_linkedin_get_reply_action():
    """Test LinkedIn get-reply parses post-id and parent-post-id."""
    root_parser = ArgumentParser()
    subparsers = root_parser.add_subparsers(dest='platform')
    create_linkedin_parser(subparsers)

    args = root_parser.parse_args([
        'linkedin', 'get-reply',
        '--post-id', 'comment123',
        '--parent-post-id', 'urn:li:ugcPost:456',
    ])

    assert args.action == 'get-reply'
    assert args.post_id == 'comment123'
    assert args.parent_post_id == 'urn:li:ugcPost:456'


def test_facebook_get_post_action():
    """Test Facebook get-post parses post-id."""
    root_parser = ArgumentParser()
    subparsers = root_parser.add_subparsers(dest='platform')
    create_facebook_parser(subparsers)

    args = root_parser.parse_args(['facebook', 'get-post', '--post-id', 'post123'])

    assert args.action == 'get-post'
    assert args.post_id == 'post123'


def test_tiktok_get_post_action():
    """Test TikTok get-post CLI exists (runtime not supported)."""
    root_parser = ArgumentParser()
    subparsers = root_parser.add_subparsers(dest='platform')
    create_tiktok_parser(subparsers)

    args = root_parser.parse_args(['tiktok', 'get-post', '--post-id', 'vid123'])

    assert args.action == 'get-post'
    assert args.post_id == 'vid123'


def test_instagram_get_post_action():
    """Test Instagram get-post parses post-id."""
    root_parser = ArgumentParser()
    subparsers = root_parser.add_subparsers(dest='platform')
    create_instagram_parser(subparsers)

    args = root_parser.parse_args(['instagram', 'get-post', '--post-id', 'media123'])

    assert args.action == 'get-post'
    assert args.post_id == 'media123'


def test_instagram_get_reply_action():
    """Test Instagram get-reply parses post-id."""
    root_parser = ArgumentParser()
    subparsers = root_parser.add_subparsers(dest='platform')
    create_instagram_parser(subparsers)

    args = root_parser.parse_args(['instagram', 'get-reply', '--post-id', 'comment123'])

    assert args.action == 'get-reply'
    assert args.post_id == 'comment123'


def test_threads_get_post_action():
    """Test Threads get-post parses post-id."""
    root_parser = ArgumentParser()
    subparsers = root_parser.add_subparsers(dest='platform')
    create_threads_parser(subparsers)

    args = root_parser.parse_args(['threads', 'get-post', '--post-id', 'post123'])

    assert args.action == 'get-post'
    assert args.post_id == 'post123'


def test_threads_get_reply_action():
    """Test Threads get-reply parses post-id."""
    root_parser = ArgumentParser()
    subparsers = root_parser.add_subparsers(dest='platform')
    create_threads_parser(subparsers)

    args = root_parser.parse_args(['threads', 'get-reply', '--post-id', 'reply123'])

    assert args.action == 'get-reply'
    assert args.post_id == 'reply123'


def test_discord_get_post_action():
    """Test Discord get-post parses post-id."""
    root_parser = ArgumentParser()
    subparsers = root_parser.add_subparsers(dest='platform')
    create_discord_parser(subparsers)

    args = root_parser.parse_args(['discord', 'get-post', '--post-id', 'msg123'])

    assert args.action == 'get-post'
    assert args.post_id == 'msg123'


def test_discord_get_reply_action():
    """Test Discord get-reply parses post-id."""
    root_parser = ArgumentParser()
    subparsers = root_parser.add_subparsers(dest='platform')
    create_discord_parser(subparsers)

    args = root_parser.parse_args(['discord', 'get-reply', '--post-id', 'reply123'])

    assert args.action == 'get-reply'
    assert args.post_id == 'reply123'


def test_youtube_get_post_action():
    """Test YouTube get-post parses post-id as video-id."""
    root_parser = ArgumentParser()
    subparsers = root_parser.add_subparsers(dest='platform')
    create_youtube_parser(subparsers)

    args = root_parser.parse_args(['youtube', 'get-post', '--post-id', 'vid123'])

    assert args.action == 'get-post'
    assert args.post_id == 'vid123'


def test_youtube_get_reply_action():
    """Test YouTube get-reply parses post-id as comment-id."""
    root_parser = ArgumentParser()
    subparsers = root_parser.add_subparsers(dest='platform')
    create_youtube_parser(subparsers)

    args = root_parser.parse_args(['youtube', 'get-reply', '--post-id', 'comment123'])

    assert args.action == 'get-reply'
    assert args.post_id == 'comment123'


def test_telegram_get_post_action():
    """Test Telegram get-post parses post-id."""
    root_parser = ArgumentParser()
    subparsers = root_parser.add_subparsers(dest='platform')
    create_telegram_parser(subparsers)

    args = root_parser.parse_args(['telegram', 'get-post', '--post-id', 'msg123'])

    assert args.action == 'get-post'
    assert args.post_id == 'msg123'


def test_telegram_get_reply_action():
    """Test Telegram get-reply parses post-id."""
    root_parser = ArgumentParser()
    subparsers = root_parser.add_subparsers(dest='platform')
    create_telegram_parser(subparsers)

    args = root_parser.parse_args(['telegram', 'get-reply', '--post-id', 'reply123'])

    assert args.action == 'get-reply'
    assert args.post_id == 'reply123'


def test_linkedin_get_post_action():
    """Test LinkedIn get-post parses post-id."""
    root_parser = ArgumentParser()
    subparsers = root_parser.add_subparsers(dest='platform')
    create_linkedin_parser(subparsers)

    args = root_parser.parse_args(['linkedin', 'get-post', '--post-id', 'urn:li:ugcPost:123'])

    assert args.action == 'get-post'
    assert args.post_id == 'urn:li:ugcPost:123'


def test_whatsapp_get_post_action():
    """Test WhatsApp get-post parses post-id."""
    root_parser = ArgumentParser()
    subparsers = root_parser.add_subparsers(dest='platform')
    create_whatsapp_parser(subparsers)

    args = root_parser.parse_args(['whatsapp', 'get-post', '--post-id', 'msg123'])

    assert args.action == 'get-post'
    assert args.post_id == 'msg123'


def test_whatsapp_get_reply_action():
    """Test WhatsApp get-reply parses post-id."""
    root_parser = ArgumentParser()
    subparsers = root_parser.add_subparsers(dest='platform')
    create_whatsapp_parser(subparsers)

    args = root_parser.parse_args(['whatsapp', 'get-reply', '--post-id', 'reply123'])

    assert args.action == 'get-reply'
    assert args.post_id == 'reply123'


@pytest.mark.parametrize(
    'create_parser,platform',
    [
        (create_facebook_parser, 'facebook'),
        (create_instagram_parser, 'instagram'),
        (create_discord_parser, 'discord'),
        (create_youtube_parser, 'youtube'),
        (create_telegram_parser, 'telegram'),
        (create_whatsapp_parser, 'whatsapp'),
    ],
)
def test_get_post_requires_post_id(create_parser, platform):
    """Test get-post fails without --post-id."""
    root_parser = ArgumentParser()
    subparsers = root_parser.add_subparsers(dest='platform')
    create_parser(subparsers)

    with pytest.raises(SystemExit):
        root_parser.parse_args([platform, 'get-post'])


@pytest.mark.parametrize(
    'create_parser,platform,extra',
    [
        (create_facebook_parser, 'facebook', []),
        (create_instagram_parser, 'instagram', []),
        (create_discord_parser, 'discord', []),
        (create_youtube_parser, 'youtube', []),
        (create_telegram_parser, 'telegram', []),
        (create_whatsapp_parser, 'whatsapp', []),
        (create_linkedin_parser, 'linkedin', ['--parent-post-id', 'urn:li:ugcPost:1']),
    ],
)
def test_get_reply_requires_post_id(create_parser, platform, extra):
    """Test get-reply fails without --post-id."""
    root_parser = ArgumentParser()
    subparsers = root_parser.add_subparsers(dest='platform')
    create_parser(subparsers)

    with pytest.raises(SystemExit):
        root_parser.parse_args([platform, 'get-reply', *extra])


# ---------------------------------------------------------------------------
# list-posts parser tests (R7: --limit on all 10 networks, --object-id on IG/FB)
# ---------------------------------------------------------------------------


def test_x_list_posts_action():
    """Test X list-posts parses --limit."""
    root_parser = ArgumentParser()
    subparsers = root_parser.add_subparsers(dest='platform')
    create_x_parser(subparsers)

    args = root_parser.parse_args(['x', 'list-posts', '--limit', '5'])

    assert args.action == 'list-posts'
    assert args.limit == 5


def test_x_list_posts_no_limit():
    """Test X list-posts parses with --limit absent."""
    root_parser = ArgumentParser()
    subparsers = root_parser.add_subparsers(dest='platform')
    create_x_parser(subparsers)

    args = root_parser.parse_args(['x', 'list-posts'])

    assert args.action == 'list-posts'
    assert args.limit is None


def test_x_list_posts_non_integer_limit_fails():
    """Test X list-posts rejects a non-integer --limit."""
    root_parser = ArgumentParser()
    subparsers = root_parser.add_subparsers(dest='platform')
    create_x_parser(subparsers)

    with pytest.raises(SystemExit):
        root_parser.parse_args(['x', 'list-posts', '--limit', 'abc'])


def test_instagram_list_posts_object_id_and_limit():
    """Test Instagram list-posts parses --object-id and --limit."""
    root_parser = ArgumentParser()
    subparsers = root_parser.add_subparsers(dest='platform')
    create_instagram_parser(subparsers)

    args = root_parser.parse_args(['instagram', 'list-posts', '--object-id', 'user123', '--limit', '5'])

    assert args.action == 'list-posts'
    assert args.object_id == 'user123'
    assert args.limit == 5


def test_facebook_list_posts_object_id_and_limit():
    """Test Facebook list-posts parses --object-id and --limit."""
    root_parser = ArgumentParser()
    subparsers = root_parser.add_subparsers(dest='platform')
    create_facebook_parser(subparsers)

    args = root_parser.parse_args(['facebook', 'list-posts', '--object-id', 'page123', '--limit', '5'])

    assert args.action == 'list-posts'
    assert args.object_id == 'page123'
    assert args.limit == 5


@pytest.mark.parametrize(
    'create_parser,platform',
    [
        (create_linkedin_parser, 'linkedin'),
        (create_discord_parser, 'discord'),
        (create_youtube_parser, 'youtube'),
        (create_tiktok_parser, 'tiktok'),
        (create_threads_parser, 'threads'),
        (create_telegram_parser, 'telegram'),
        (create_whatsapp_parser, 'whatsapp'),
    ],
)
def test_list_posts_parses_for_remaining_platforms(create_parser, platform):
    """Test list-posts subcommand parses for the remaining platforms."""
    root_parser = ArgumentParser()
    subparsers = root_parser.add_subparsers(dest='platform')
    create_parser(subparsers)

    args = root_parser.parse_args([platform, 'list-posts', '--limit', '3'])

    assert args.action == 'list-posts'
    assert args.limit == 3


def test_list_posts_e2e_emits_parseable_json_array():
    """End-to-end: list-posts dispatch emits a parseable 6-key JSON array (plan U5)."""
    import asyncio
    import json as _json
    from unittest.mock import AsyncMock, MagicMock, patch

    root_parser = ArgumentParser()
    subparsers = root_parser.add_subparsers(dest='platform')
    create_x_parser(subparsers)

    args = root_parser.parse_args(['x', 'list-posts', '--limit', '2'])
    assert args.action == 'list-posts'
    assert args.limit == 2

    # Drive the real handler -> list_posts -> _output_list path. Set up an X
    # wrapper with a stubbed api.list_posts so no network runs; capture the
    # _output_list argument to assert the emitted JSON.
    from agoras.platforms.x.wrapper import X as XWrapper

    x = XWrapper(
        twitter_consumer_key='key', twitter_consumer_secret='secret',
        twitter_oauth_token='token', twitter_oauth_secret='secret',
    )
    x.config = {'limit': '2'}
    x.api = MagicMock()
    x.api.list_posts = AsyncMock(return_value=[
        {'id': '1', 'text': 'hello', 'author_id': 'user-1', 'created_at': '2026-01-01T00:00:00Z'},
        {'id': '2', 'text': 'world', 'author_id': None, 'created_at': '2026-01-02T00:00:00Z'},
    ])

    async def run():
        with patch.object(x, '_output_list') as mock_out:
            await x._handle_list_posts_action()
            return mock_out.call_args.args[0]

    emitted = asyncio.run(run())
    parsed = _json.loads(_json.dumps(emitted))
    assert isinstance(parsed, list)
    assert len(parsed) == 2
    for item in parsed:
        assert set(item.keys()) == {'id', 'text', 'media', 'author', 'created_at', 'metadata'}
