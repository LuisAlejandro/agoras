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
Tests for schedule run utility command.
"""

import sys
from argparse import ArgumentParser, Namespace
from io import StringIO
from unittest.mock import MagicMock, patch

import pytest

from agoras.cli.utils.schedule import _add_all_platform_auth_options, _handle_schedule_run, create_schedule_run_parser

# Parser Creation Tests


def test_create_schedule_run_parser_creates_parser():
    """Test create_schedule_run_parser creates ArgumentParser."""
    mock_subparsers = MagicMock()
    mock_parser = ArgumentParser()
    mock_subparsers.add_parser.return_value = mock_parser

    with patch('agoras.cli.utils.schedule.PlatformRegistry') as mock_registry:
        mock_registry.get_platform_names.return_value = ['x', 'facebook']
        parser = create_schedule_run_parser(mock_subparsers)

        assert isinstance(parser, ArgumentParser)
        mock_subparsers.add_parser.assert_called_once_with(
            'schedule-run',
            help='Run scheduled posts from Google Sheets'
        )


def test_create_schedule_run_parser_has_required_sheets_args():
    """Test parser has required Google Sheets arguments."""
    mock_subparsers = MagicMock()
    mock_parser = ArgumentParser()
    mock_subparsers.add_parser.return_value = mock_parser

    with patch('agoras.cli.utils.schedule.PlatformRegistry') as mock_registry:
        mock_registry.get_platform_names.return_value = ['x']
        parser = create_schedule_run_parser(mock_subparsers)

        # Parse with missing required args should fail
        with pytest.raises(SystemExit):
            parser.parse_args([])


def test_create_schedule_run_parser_has_sheets_options():
    """Test parser has Google Sheets option group."""
    mock_subparsers = MagicMock()
    mock_parser = ArgumentParser()
    mock_subparsers.add_parser.return_value = mock_parser

    with patch('agoras.cli.utils.schedule.PlatformRegistry') as mock_registry:
        mock_registry.get_platform_names.return_value = ['x']
        parser = create_schedule_run_parser(mock_subparsers)

        args = parser.parse_args([
            '--sheets-id', 'sheet123',
            '--sheets-name', 'Schedule',
            '--sheets-client-email', 'test@example.com',
            '--sheets-private-key', 'key123'
        ])

        assert args.sheets_id == 'sheet123'
        assert args.sheets_name == 'Schedule'
        assert args.sheets_client_email == 'test@example.com'
        assert args.sheets_private_key == 'key123'


def test_create_schedule_run_parser_network_optional():
    """Test parser has optional --network argument."""
    mock_subparsers = MagicMock()
    mock_parser = ArgumentParser()
    mock_subparsers.add_parser.return_value = mock_parser

    with patch('agoras.cli.utils.schedule.PlatformRegistry') as mock_registry:
        mock_registry.get_platform_names.return_value = ['x', 'facebook']
        parser = create_schedule_run_parser(mock_subparsers)

        # Network is optional
        args = parser.parse_args([
            '--sheets-id', 'sheet123',
            '--sheets-name', 'Schedule',
            '--sheets-client-email', 'test@example.com',
            '--sheets-private-key', 'key123'
        ])
        assert args.network is None

        # But can be specified
        args = parser.parse_args([
            '--network', 'x',
            '--sheets-id', 'sheet123',
            '--sheets-name', 'Schedule',
            '--sheets-client-email', 'test@example.com',
            '--sheets-private-key', 'key123'
        ])
        assert args.network == 'x'


# Auth Options Tests (same as feed.py)

def test_add_all_platform_auth_options_adds_all_platforms():
    """Test _add_all_platform_auth_options adds all platform auth groups."""
    parser = ArgumentParser()
    _add_all_platform_auth_options(parser)

    # Test a few key platforms
    args = parser.parse_args([
        '--x-consumer-key', 'key',
        '--facebook-access-token', 'token',
        '--instagram-access-token', 'token2',
        '--linkedin-access-token', 'token3',
        '--discord-bot-token', 'bot123',
        '--youtube-client-id', 'yt123',
        '--tiktok-client-key', 'tt123',
        '--threads-app-id', 'th123',
        '--telegram-bot-token', 'tg123',
        '--whatsapp-access-token', 'wa123'
    ])

    assert args.x_consumer_key == 'key'
    assert args.facebook_access_token == 'token'
    assert args.instagram_access_token == 'token2'
    assert args.linkedin_access_token == 'token3'
    assert args.discord_bot_token == 'bot123'
    assert args.youtube_client_id == 'yt123'
    assert args.tiktok_client_key == 'tt123'
    assert args.threads_app_id == 'th123'
    assert args.telegram_bot_token == 'tg123'
    assert args.whatsapp_access_token == 'wa123'


# Handler Tests

@patch('agoras.cli.utils.schedule.publish_main')
def test_handle_schedule_run_with_network(mock_publish_main):
    """Test _handle_schedule_run with network specified."""
    mock_publish_main.return_value = 0

    args = Namespace()
    args.network = 'x'
    args.sheets_id = 'sheet123'
    args.sheets_name = 'Schedule'
    args.sheets_client_email = 'test@example.com'
    args.sheets_private_key = 'key123'
    args.handler = None
    args.x_consumer_key = 'key'

    result = _handle_schedule_run(args)

    assert result == 0
    mock_publish_main.assert_called_once()
    call_kwargs = mock_publish_main.call_args[1]
    assert call_kwargs['action'] == 'schedule'
    assert call_kwargs['network'] == 'x'
    assert call_kwargs['google_sheets_id'] == 'sheet123'
    assert call_kwargs['google_sheets_name'] == 'Schedule'
    assert call_kwargs['google_sheets_client_email'] == 'test@example.com'
    assert call_kwargs['google_sheets_private_key'] == 'key123'


@patch('agoras.cli.utils.schedule.publish_main')
def test_handle_schedule_run_without_network(mock_publish_main):
    """Test _handle_schedule_run without network (process all)."""
    mock_publish_main.return_value = 0

    args = Namespace()
    args.network = None
    args.sheets_id = 'sheet123'
    args.sheets_name = 'Schedule'
    args.sheets_client_email = 'test@example.com'
    args.sheets_private_key = 'key123'
    args.handler = None

    result = _handle_schedule_run(args)

    assert result == 0
    call_kwargs = mock_publish_main.call_args[1]
    assert call_kwargs['action'] == 'schedule'
    assert 'network' not in call_kwargs  # Network not included when None


@patch('agoras.cli.utils.schedule.publish_main')
@patch('sys.stderr', new_callable=StringIO)
def test_handle_schedule_run_twitter_deprecation(mock_stderr, mock_publish_main):
    """Test _handle_schedule_run shows Twitter deprecation warning."""
    mock_publish_main.return_value = 0

    args = Namespace()
    args.network = 'twitter'
    args.sheets_id = 'sheet123'
    args.sheets_name = 'Schedule'
    args.sheets_client_email = 'test@example.com'
    args.sheets_private_key = 'key123'
    args.handler = None
    args.twitter_consumer_key = None
    args.twitter_consumer_secret = None
    args.twitter_oauth_token = None
    args.twitter_oauth_secret = None
    args.x_consumer_key = None
    args.x_consumer_secret = None
    args.x_oauth_token = None
    args.x_oauth_secret = None

    _handle_schedule_run(args)

    stderr_output = mock_stderr.getvalue()
    assert 'deprecated' in stderr_output.lower() or 'twitter' in stderr_output.lower()
    call_kwargs = mock_publish_main.call_args[1]
    assert call_kwargs['network'] == 'x'  # Should be converted to 'x'


@patch('agoras.cli.utils.schedule.publish_main')
@patch('sys.stderr', new_callable=StringIO)
def test_handle_schedule_run_maps_twitter_to_x_params(mock_stderr, mock_publish_main):
    """Test _handle_schedule_run maps twitter-* params to x-* params."""
    mock_publish_main.return_value = 0

    args = Namespace()
    args.network = 'twitter'
    args.sheets_id = 'sheet123'
    args.sheets_name = 'Schedule'
    args.sheets_client_email = 'test@example.com'
    args.sheets_private_key = 'key123'
    args.handler = None
    args.twitter_consumer_key = 'old_key'
    args.twitter_consumer_secret = 'old_secret'
    args.twitter_oauth_token = 'old_token'
    args.twitter_oauth_secret = 'old_secret2'
    args.x_consumer_key = None
    args.x_consumer_secret = None
    args.x_oauth_token = None
    args.x_oauth_secret = None

    _handle_schedule_run(args)

    # Check that twitter params were mapped to x params
    assert args.x_consumer_key == 'old_key'
    assert args.x_consumer_secret == 'old_secret'
    assert args.x_oauth_token == 'old_token'
    assert args.x_oauth_secret == 'old_secret2'


@patch('agoras.cli.utils.schedule.publish_main')
def test_handle_schedule_run_maps_x_to_twitter_params(mock_publish_main):
    """Test _handle_schedule_run maps x-* params to twitter_* for legacy compatibility."""
    mock_publish_main.return_value = 0

    args = Namespace()
    args.network = 'x'
    args.sheets_id = 'sheet123'
    args.sheets_name = 'Schedule'
    args.sheets_client_email = 'test@example.com'
    args.sheets_private_key = 'key123'
    args.handler = None
    args.x_consumer_key = 'new_key'
    args.x_consumer_secret = 'new_secret'
    args.x_oauth_token = 'new_token'
    args.x_oauth_secret = 'new_secret2'
    args.twitter_consumer_key = None
    args.twitter_consumer_secret = None
    args.twitter_oauth_token = None
    args.twitter_oauth_secret = None

    _handle_schedule_run(args)

    # Check that x params were mapped to twitter_* for legacy
    assert args.twitter_consumer_key == 'new_key'
    assert args.twitter_consumer_secret == 'new_secret'
    assert args.twitter_oauth_token == 'new_token'
    assert args.twitter_oauth_secret == 'new_secret2'


@patch('agoras.cli.utils.schedule.publish_main')
def test_handle_schedule_run_passes_all_auth_params(mock_publish_main):
    """Test _handle_schedule_run passes all platform auth parameters to legacy."""
    mock_publish_main.return_value = 0

    args = Namespace()
    args.network = 'facebook'
    args.sheets_id = 'sheet123'
    args.sheets_name = 'Schedule'
    args.sheets_client_email = 'test@example.com'
    args.sheets_private_key = 'key123'
    args.handler = None
    args.facebook_access_token = 'token'
    args.facebook_object_id = 'obj123'
    args.facebook_app_id = 'app123'

    _handle_schedule_run(args)

    call_kwargs = mock_publish_main.call_args[1]
    assert call_kwargs['facebook_access_token'] == 'token'
    assert call_kwargs['facebook_object_id'] == 'obj123'
    assert call_kwargs['facebook_app_id'] == 'app123'


@patch('agoras.cli.utils.schedule.publish_main')
def test_handle_schedule_run_filters_handler_from_legacy_args(mock_publish_main):
    """Test _handle_schedule_run excludes handler from legacy args."""
    mock_publish_main.return_value = 0

    args = Namespace()
    args.network = 'x'
    args.sheets_id = 'sheet123'
    args.sheets_name = 'Schedule'
    args.sheets_client_email = 'test@example.com'
    args.sheets_private_key = 'key123'
    args.handler = _handle_schedule_run  # Should be excluded

    _handle_schedule_run(args)

    call_kwargs = mock_publish_main.call_args[1]
    assert 'handler' not in call_kwargs


@patch('agoras.cli.utils.schedule.publish_main')
def test_handle_schedule_run_includes_sheets_params(mock_publish_main):
    """Test _handle_schedule_run includes all Google Sheets parameters."""
    mock_publish_main.return_value = 0

    args = Namespace()
    args.network = None
    args.sheets_id = 'sheet123'
    args.sheets_name = 'MySchedule'
    args.sheets_client_email = 'service@example.com'
    args.sheets_private_key = 'private_key_123'
    args.handler = None

    _handle_schedule_run(args)

    call_kwargs = mock_publish_main.call_args[1]
    assert call_kwargs['google_sheets_id'] == 'sheet123'
    assert call_kwargs['google_sheets_name'] == 'MySchedule'
    assert call_kwargs['google_sheets_client_email'] == 'service@example.com'
    assert call_kwargs['google_sheets_private_key'] == 'private_key_123'
