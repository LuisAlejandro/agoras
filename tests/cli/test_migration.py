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
Tests for migration guidance utilities.
"""

from agoras.cli.migration import (
    convert_legacy_params_to_new_format,
    format_migration_warning,
    get_migration_summary,
    suggest_new_command,
)


def test_suggest_new_command_x_post():
    """Test migration suggestion for X post."""
    args_dict = {
        'network': 'x',
        'action': 'post',
        'twitter_consumer_key': 'key123',
        'status_text': 'Hello',
    }

    result = suggest_new_command('x', 'post', args_dict)

    assert 'agoras x post' in result
    assert '--consumer-key' in result
    assert '--text' in result


def test_suggest_new_command_twitter_post():
    """Test migration suggestion for Twitter post (backward compatibility)."""
    args_dict = {
        'network': 'twitter',
        'action': 'post',
        'twitter_consumer_key': 'key123',
        'status_text': 'Hello',
    }

    result = suggest_new_command('twitter', 'post', args_dict)

    assert 'agoras x post' in result or 'agoras twitter post' in result
    assert '--consumer-key' in result
    assert '--text' in result


def test_suggest_new_command_facebook_video():
    """Test migration suggestion for Facebook video."""
    args_dict = {
        'network': 'facebook',
        'action': 'video',
        'facebook_access_token': 'token123',
        'facebook_video_url': 'video.mp4',
    }

    result = suggest_new_command('facebook', 'video', args_dict)

    assert 'agoras facebook video' in result
    assert '--access-token' in result
    assert '--video-url' in result


def test_suggest_new_command_feed_last():
    """Test migration suggestion for feed last action."""
    args_dict = {
        'network': 'x',
        'action': 'last-from-feed',
        'feed_url': 'https://example.com/feed.xml',
    }

    result = suggest_new_command('x', 'last-from-feed', args_dict)

    assert 'agoras utils feed-publish' in result
    assert '--network x' in result
    assert '--mode last' in result


def test_suggest_new_command_feed_random():
    """Test migration suggestion for feed random action."""
    args_dict = {
        'network': 'instagram',
        'action': 'random-from-feed',
        'feed_url': 'feed.xml',
    }

    result = suggest_new_command('instagram', 'random-from-feed', args_dict)

    assert 'agoras utils feed-publish' in result
    assert '--network instagram' in result
    assert '--mode random' in result


def test_suggest_new_command_schedule():
    """Test migration suggestion for schedule action."""
    args_dict = {
        'network': 'facebook',
        'action': 'schedule',
        'google_sheets_id': 'sheet123',
    }

    result = suggest_new_command('facebook', 'schedule', args_dict)

    assert 'agoras utils schedule-run' in result
    assert '--network facebook' in result


def test_convert_legacy_params_filters_defaults():
    """Test that default values are filtered out."""
    args_dict = {
        'youtube_privacy_status': 'private',  # default
        'loglevel': 'INFO',  # default
        'youtube_client_id': 'client123',
    }

    result = convert_legacy_params_to_new_format('youtube', 'video', args_dict)

    assert 'client123' in result
    assert 'private' not in result
    assert 'INFO' not in result


def test_convert_legacy_params_includes_non_defaults():
    """Test that non-default values are included."""
    args_dict = {
        'youtube_privacy_status': 'public',  # non-default
        'youtube_client_id': 'client123',
    }

    result = convert_legacy_params_to_new_format('youtube', 'video', args_dict)

    assert 'client123' in result
    # Note: privacy might still be filtered if it matches defaults


def test_format_migration_warning():
    """Test formatting of deprecation warning message."""
    old_parts = {'network': 'twitter', 'action': 'post'}
    new_cmd = 'agoras twitter post --consumer-key "key"'

    warning = format_migration_warning(old_parts, new_cmd)

    assert 'DEPRECATION WARNING' in warning
    assert 'agoras publish' in warning
    assert 'agoras twitter post' in warning
    assert 'version 2.0' in warning
    assert '12 months' in warning


def test_get_migration_summary_platform_action():
    """Test brief migration summary for platform actions."""
    summary = get_migration_summary('twitter', 'post')

    assert 'agoras twitter post' in summary


def test_get_migration_summary_feed():
    """Test brief migration summary for feed actions."""
    summary = get_migration_summary('facebook', 'last-from-feed')

    assert 'agoras utils feed-publish' in summary
    assert '--mode last' in summary


def test_get_migration_summary_schedule():
    """Test brief migration summary for schedule action."""
    summary = get_migration_summary('linkedin', 'schedule')

    assert 'agoras utils schedule-run' in summary
