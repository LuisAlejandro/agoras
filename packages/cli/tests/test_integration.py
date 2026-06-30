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
from unittest.mock import patch

from agoras.cli.main import commandline, main
from agoras.cli.validator import ActionValidator


def test_main_help_shows_all_commands():
    """Test that main help shows all platform commands."""
    with pytest.raises(SystemExit) as exc_info:
        parser, args = commandline(['--help'])
    assert exc_info.value.code == 0


def test_all_platforms_accessible():
    """Test that all platforms can be accessed including X and twitter alias."""
    platforms = ['x', 'twitter', 'facebook', 'instagram', 'linkedin',
                 'discord', 'youtube', 'tiktok', 'threads', 'telegram', 'whatsapp']

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
    """Test complete X post command parsing without auth flags."""
    parser, args = commandline([
        'x', 'post',
        '--text', 'Test post',
        '--image-1', 'img.jpg'
    ])

    assert args.action == 'post'
    assert args.text == 'Test post'
    assert args.image_1 == 'img.jpg'


def test_twitter_post_complete_flow():
    """Test complete Twitter alias post command parsing without auth flags."""
    parser, args = commandline([
        'twitter', 'post',
        '--text', 'Test post',
        '--image-1', 'img.jpg'
    ])

    assert args.action == 'post'
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
    ])

    assert args.network == 'x'
    assert args.mode == 'last'
    assert args.feed_url == 'https://example.com/feed.xml'


def test_utils_feed_publish_rejects_cred_flags():
    """Test utils feed-publish rejects platform credential flags."""
    with pytest.raises(SystemExit):
        commandline([
            'utils', 'feed-publish',
            '--network', 'x',
            '--mode', 'last',
            '--feed-url', 'https://example.com/feed.xml',
            '--x-consumer-key', 'key',
        ])


@patch('agoras.cli.platform_runner.x')
def test_utils_feed_publish_main_reaches_platform_runner(mock_x):
    """Test utils feed-publish CLI entry dispatches through platform_runner."""
    mock_x.return_value = 0
    status = main([
        'utils', 'feed-publish',
        '--network', 'x',
        '--mode', 'last',
        '--feed-url', 'https://example.com/feed.xml',
        '--max-count', '2',
    ])
    assert status == 0
    mock_x.assert_called_once()
    call_kwargs = mock_x.call_args[0][0]
    assert call_kwargs == {
        'network': 'x',
        'action': 'last-from-feed',
        'feed_url': 'https://example.com/feed.xml',
        'max_count': 2,
        'post_lookback': None,
        'max_post_age': None,
    }


def test_utils_schedule_run_complete_flow():
    """Test complete utils schedule-run command parsing."""
    parser, args = commandline([
        'utils', 'schedule-run',
        '--network', 'x',
        '--sheets-id', 'sheet123',
        '--sheets-name', 'Schedule',
        '--sheets-client-email', 'email@example.com',
        '--sheets-private-key', 'private_key'
    ])

    assert args.network == 'x'
    assert args.sheets_id == 'sheet123'
    assert args.sheets_name == 'Schedule'


def test_utils_schedule_run_requires_network():
    """Test utils schedule-run requires --network."""
    with pytest.raises(SystemExit):
        commandline([
            'utils', 'schedule-run',
            '--sheets-id', 'sheet123',
            '--sheets-name', 'Schedule',
            '--sheets-client-email', 'email@example.com',
            '--sheets-private-key', 'private_key'
        ])


def test_utils_schedule_run_rejects_cred_flags():
    """Test utils schedule-run rejects platform credential flags."""
    with pytest.raises(SystemExit):
        commandline([
            'utils', 'schedule-run',
            '--network', 'facebook',
            '--sheets-id', 'sheet123',
            '--sheets-name', 'Schedule',
            '--sheets-client-email', 'email@example.com',
            '--sheets-private-key', 'private_key',
            '--facebook-access-token', 'token',
        ])


@patch('agoras.cli.platform_runner.x')
def test_utils_schedule_run_main_reaches_platform_runner(mock_x):
    """Test utils schedule-run CLI entry dispatches through platform_runner."""
    mock_x.return_value = 0
    status = main([
        'utils', 'schedule-run',
        '--network', 'x',
        '--sheets-id', 'sheet123',
        '--sheets-name', 'Schedule',
        '--sheets-client-email', 'email@example.com',
        '--sheets-private-key', 'private_key',
    ])
    assert status == 0
    mock_x.assert_called_once()
    call_kwargs = mock_x.call_args[0][0]
    assert call_kwargs['action'] == 'schedule'
    assert call_kwargs['network'] == 'x'
    assert call_kwargs['google_sheets_id'] == 'sheet123'


def test_discord_post_parses_content_only():
    """Test Discord post parses content flags without auth flags."""
    parser, args = commandline([
        'discord', 'post',
        '--text', 'Hello Discord'
    ])

    assert args.text == 'Hello Discord'


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

    # Valid: TikTok post (now supported)
    ActionValidator.validate('tiktok', 'post')

    # Invalid: TikTok like (not supported)
    with pytest.raises(ValueError):
        ActionValidator.validate('tiktok', 'like')


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
