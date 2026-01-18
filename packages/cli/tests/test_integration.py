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
Integration tests for CLI end-to-end behavior.
"""

import pytest

from agoras.cli.main import commandline
from agoras.cli.validator import ActionValidator


def test_main_help_shows_all_commands():
    """Test that main help shows all platform commands."""
    with pytest.raises(SystemExit) as exc_info:
        parser, args = commandline(['--help'])
    assert exc_info.value.code == 0


def test_all_platforms_accessible():
    """Test that all platforms can be accessed including X and twitter alias."""
    platforms = ['x', 'twitter', 'facebook', 'instagram', 'linkedin',
                 'discord', 'youtube', 'tiktok', 'threads']

    for platform in platforms:
        with pytest.raises(SystemExit) as exc_info:
            parser, args = commandline([platform, '--help'])
        assert exc_info.value.code == 0


def test_utils_command_accessible():
    """Test that utils command is accessible."""
    with pytest.raises(SystemExit) as exc_info:
        parser, args = commandline(['utils', '--help'])
    assert exc_info.value.code == 0


def test_legacy_publish_still_works():
    """Test that legacy publish command still works."""
    with pytest.raises(SystemExit) as exc_info:
        parser, args = commandline(['publish', '--help'])
    assert exc_info.value.code == 0


def test_x_post_complete_flow():
    """Test complete X post command parsing."""
    parser, args = commandline([
        'x', 'post',
        '--consumer-key', 'key',
        '--consumer-secret', 'secret',
        '--oauth-token', 'token',
        '--oauth-secret', 'oauth',
        '--text', 'Test post',
        '--image-1', 'img.jpg'
    ])

    assert args.action == 'post'
    assert args.consumer_key == 'key'
    assert args.text == 'Test post'
    assert args.image_1 == 'img.jpg'


def test_twitter_post_complete_flow():
    """Test complete Twitter alias post command parsing (backward compatibility)."""
    parser, args = commandline([
        'twitter', 'post',
        '--consumer-key', 'key',
        '--consumer-secret', 'secret',
        '--oauth-token', 'token',
        '--oauth-secret', 'oauth',
        '--text', 'Test post',
        '--image-1', 'img.jpg'
    ])

    assert args.action == 'post'
    assert args.consumer_key == 'key'
    assert args.text == 'Test post'
    assert args.image_1 == 'img.jpg'


def test_youtube_video_complete_flow():
    """Test complete YouTube video command parsing."""
    parser, args = commandline([
        'youtube', 'video',
        '--video-url', 'video.mp4',
        '--title', 'My Video',
        '--privacy', 'public'
    ])

    assert args.action == 'video'
    assert args.video_url == 'video.mp4'
    assert args.title == 'My Video'
    assert args.privacy == 'public'


def test_utils_feed_publish_complete_flow():
    """Test complete utils feed-publish command parsing."""
    parser, args = commandline([
        'utils', 'feed-publish',
        '--network', 'x',
        '--mode', 'last',
        '--feed-url', 'https://example.com/feed.xml',
        '--x-consumer-key', 'key'
    ])

    assert args.network == 'x'
    assert args.mode == 'last'
    assert args.feed_url == 'https://example.com/feed.xml'
    assert args.x_consumer_key == 'key'


def test_utils_schedule_run_complete_flow():
    """Test complete utils schedule-run command parsing."""
    parser, args = commandline([
        'utils', 'schedule-run',
        '--sheets-id', 'sheet123',
        '--sheets-name', 'Schedule',
        '--sheets-client-email', 'email@example.com',
        '--sheets-private-key', 'private_key'
    ])

    assert args.sheets_id == 'sheet123'
    assert args.sheets_name == 'Schedule'


def test_discord_unique_auth_flow():
    """Test Discord unique authentication flow."""
    parser, args = commandline([
        'discord', 'post',
        '--bot-token', 'BOT_TOKEN',
        '--server-name', 'Server',
        '--channel-name', 'general',
        '--text', 'Hello Discord'
    ])

    assert args.bot_token == 'BOT_TOKEN'
    assert args.server_name == 'Server'
    assert args.channel_name == 'general'


def test_threads_new_platform_accessible():
    """Test that new Threads platform is accessible."""
    parser, args = commandline([
        'threads', 'post',
        '--text', 'Hello Threads',
        '--image-1', 'img.jpg'
    ])

    assert args.action == 'post'
    assert args.text == 'Hello Threads'
    assert args.image_1 == 'img.jpg'


def test_action_validation_integration():
    """Test that action validation is enforced."""
    # Valid: Twitter post
    ActionValidator.validate('twitter', 'post')

    # Invalid: YouTube post
    with pytest.raises(ValueError):
        ActionValidator.validate('youtube', 'post')

    # Invalid: TikTok post
    with pytest.raises(ValueError):
        ActionValidator.validate('tiktok', 'post')


def test_legacy_publish_with_migration_flag():
    """Test legacy publish with --show-migration flag."""
    parser, args = commandline([
        'publish',
        '--network', 'twitter',
        '--action', 'post',
        '--twitter-consumer-key', 'key',
        '--show-migration'
    ])

    assert args.network == 'twitter'
    assert args.action == 'post'
    assert args.show_migration is True
