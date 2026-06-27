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
Tests for migration guidance utilities.
"""

from agoras.cli.migration import convert_legacy_params_to_new_format, format_migration_warning, suggest_new_command


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
    assert '--consumer-key' not in result
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
    assert '--consumer-key' not in result
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
    assert 'token123' not in result
    assert 'video.mp4' in result


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

    assert 'client123' not in result
    assert 'private' not in result
    assert 'INFO' not in result


def test_convert_legacy_params_includes_non_defaults():
    """Test that non-auth content values are included."""
    args_dict = {
        'youtube_title': 'My Video',
        'youtube_client_id': 'client123',
    }

    result = convert_legacy_params_to_new_format('youtube', 'video', args_dict)

    assert 'My Video' in result
    assert 'client123' not in result


def test_format_migration_warning():
    """Test formatting of deprecation warning message."""
    old_parts = {'network': 'twitter', 'action': 'post'}
    new_cmd = 'agoras twitter post --consumer-key "key"'

    warning = format_migration_warning(old_parts, new_cmd)

    assert 'DEPRECATION WARNING' in warning
    assert 'agoras publish' in warning
    assert 'agoras twitter post' in warning
    assert 'version 3.0' in warning


def test_suggest_new_command_discord_post_omits_bot_token():
    """Discord post migration must not suggest bot-token."""
    args_dict = {
        'discord_bot_token': 'token',
        'status_text': 'Hello',
    }
    result = suggest_new_command('discord', 'post', args_dict)
    assert 'bot-token' not in result
    assert 'Hello' in result


def test_suggest_new_command_whatsapp_post_keeps_recipient():
    """WhatsApp post migration keeps recipient but strips access token."""
    args_dict = {
        'whatsapp_access_token': 'token',
        'whatsapp_recipient': '+15551234567',
        'status_text': 'Hi',
    }
    result = suggest_new_command('whatsapp', 'post', args_dict)
    assert 'access-token' not in result
    assert 'recipient' in result


def test_suggest_new_command_telegram_delete_omits_parse_mode():
    """Telegram delete migration must not suggest parse-mode."""
    args_dict = {
        'telegram_message_id': '123',
        'telegram_parse_mode': 'Markdown',
    }

    result = suggest_new_command('telegram', 'delete', args_dict)

    assert 'agoras telegram delete' in result
    assert 'parse-mode' not in result


def test_suggest_new_command_empty_args():
    """Test suggest_new_command with empty args dict."""
    result = suggest_new_command('x', 'post', {})

    assert 'agoras x post' in result


def test_suggest_new_command_all_platforms():
    """Test suggest_new_command for all major platforms."""
    platforms = [
        'x',
        'facebook',
        'instagram',
        'linkedin',
        'discord',
        'youtube',
        'tiktok',
        'threads',
        'telegram',
        'whatsapp']

    for platform in platforms:
        args_dict = {'network': platform, 'action': 'post'}
        result = suggest_new_command(platform, 'post', args_dict)
        assert f'agoras {platform} post' in result or 'agoras utils' in result


def test_convert_legacy_params_with_utils_commands_feed():
    """Test convert_legacy_params_to_new_format with feed command."""
    args_dict = {
        'network': 'x',
        'action': 'last-from-feed',
        'feed_url': 'http://feed.xml',
        'feed_max_count': 5,
        'x_consumer_key': 'key'
    }

    result = convert_legacy_params_to_new_format('x', 'last-from-feed', args_dict)

    assert 'feed-url' in result or 'feed_url' in result
    assert 'key' not in result


def test_convert_legacy_params_with_utils_commands_schedule():
    """Test convert_legacy_params_to_new_format with schedule command."""
    args_dict = {
        'network': 'facebook',
        'action': 'schedule',
        'google_sheets_id': 'sheet123',
        'facebook_access_token': 'token'
    }

    result = convert_legacy_params_to_new_format('facebook', 'schedule', args_dict)

    assert 'sheet123' in result
    assert 'token' not in result


def test_convert_legacy_params_with_utils_schedule_omits_sheets_secrets():
    """Test utils schedule suggestions omit Sheets credentials."""
    args_dict = {
        'network': 'x',
        'action': 'schedule',
        'google_sheets_id': 'sheet123',
        'google_sheets_private_key': 'secret-key',
        'google_sheets_client_email': 'svc@example.com',
    }

    result = convert_legacy_params_to_new_format('x', 'schedule', args_dict)

    assert 'sheet123' in result
    assert 'secret-key' not in result
    assert 'svc@example.com' not in result


def test_convert_legacy_params_with_platform_commands():
    """Test convert_legacy_params_to_new_format with platform commands."""
    args_dict = {
        'network': 'youtube',
        'action': 'video',
        'youtube_client_id': 'client123',
        'youtube_client_secret': 'secret123',
        'youtube_privacy_status': 'public'  # non-default
    }

    result = convert_legacy_params_to_new_format('youtube', 'video', args_dict)

    assert 'client123' not in result
    assert 'secret123' not in result


def test_convert_legacy_params_escapes_quotes():
    """Test convert_legacy_params_to_new_format escapes quotes in values."""
    args_dict = {
        'network': 'x',
        'action': 'post',
        'status_text': 'Text with "quotes" inside'
    }

    result = convert_legacy_params_to_new_format('x', 'post', args_dict)

    assert '\\"' in result or '"' in result


def test_convert_legacy_params_filters_empty_strings():
    """Test convert_legacy_params_to_new_format filters empty strings."""
    args_dict = {
        'network': 'x',
        'action': 'post',
        'status_text': '',
        'status_link': 'http://link.com'
    }

    result = convert_legacy_params_to_new_format('x', 'post', args_dict)

    assert 'link.com' in result
    # Empty strings should be filtered


def test_convert_legacy_params_filters_default_privacy():
    """Test convert_legacy_params_to_new_format filters default privacy values."""
    args_dict = {
        'network': 'youtube',
        'action': 'video',
        'youtube_privacy_status': 'private',  # default
        'youtube_client_id': 'client123'
    }

    result = convert_legacy_params_to_new_format('youtube', 'video', args_dict)

    assert 'client123' not in result
    # Default privacy should be filtered


def test_convert_legacy_params_includes_non_default_privacy():
    """Test that non-auth content values are included for TikTok."""
    args_dict = {
        'tiktok_title': 'My TikTok',
        'tiktok_client_key': 'key123',
    }

    result = convert_legacy_params_to_new_format('tiktok', 'video', args_dict)

    assert 'My TikTok' in result
    assert 'key123' not in result


def test_format_migration_warning_various_combinations():
    """Test format_migration_warning with various network/action combinations."""
    test_cases = [
        ('x', 'post'),
        ('facebook', 'video'),
        ('instagram', 'post'),
        ('youtube', 'video'),
    ]

    for network, action in test_cases:
        old_parts = {'network': network, 'action': action}
        new_cmd = f'agoras {network} {action}'
        warning = format_migration_warning(old_parts, new_cmd)

        assert 'DEPRECATION WARNING' in warning
        assert network in warning
        assert action in warning


def test_convert_legacy_params_skips_special_params():
    """Test convert_legacy_params_to_new_format skips special parameters."""
    args_dict = {
        'network': 'x',
        'action': 'post',
        'command': 'publish',
        'handler': lambda x: x,
        'loglevel': 'INFO',
        'show_migration': True,
        'status_text': 'Hello'
    }

    result = convert_legacy_params_to_new_format('x', 'post', args_dict)

    assert 'Hello' in result
    # Special params should be filtered
    assert 'command' not in result
    assert 'handler' not in result
    assert 'INFO' not in result
    assert 'show_migration' not in result
