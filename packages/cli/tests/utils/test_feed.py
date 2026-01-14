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
Tests for feed publish utility command.
"""

import sys
from argparse import ArgumentParser, Namespace
from io import StringIO
from unittest.mock import MagicMock, patch

import pytest

from agoras.cli.utils.feed import _add_all_platform_auth_options, _handle_feed_publish, create_feed_publish_parser

# Parser Creation Tests


def test_create_feed_publish_parser_creates_parser():
    """Test create_feed_publish_parser creates ArgumentParser."""
    mock_subparsers = MagicMock()
    mock_parser = ArgumentParser()
    mock_subparsers.add_parser.return_value = mock_parser

    with patch('agoras.cli.utils.feed.PlatformRegistry') as mock_registry:
        mock_registry.get_platform_names.return_value = ['x', 'facebook']
        parser = create_feed_publish_parser(mock_subparsers)

        assert isinstance(parser, ArgumentParser)
        mock_subparsers.add_parser.assert_called_once_with(
            'feed-publish',
            help='Publish content from RSS/Atom feed to social network'
        )


def test_create_feed_publish_parser_has_required_args():
    """Test parser has required arguments."""
    mock_subparsers = MagicMock()
    mock_parser = ArgumentParser()
    mock_subparsers.add_parser.return_value = mock_parser

    with patch('agoras.cli.utils.feed.PlatformRegistry') as mock_registry:
        mock_registry.get_platform_names.return_value = ['x', 'facebook']
        parser = create_feed_publish_parser(mock_subparsers)

        # Parse with missing required args should fail
        with pytest.raises(SystemExit):
            parser.parse_args([])


def test_create_feed_publish_parser_has_network_arg():
    """Test parser has --network argument with choices."""
    mock_subparsers = MagicMock()
    mock_subparsers.add_parser.return_value = ArgumentParser()

    with patch('agoras.cli.utils.feed.PlatformRegistry') as mock_registry:
        mock_registry.get_platform_names.return_value = ['x', 'facebook', 'instagram']
        parser = create_feed_publish_parser(mock_subparsers)

        # Check network argument was added
        args = parser.parse_args(['--network', 'x', '--mode', 'last', '--feed-url', 'http://feed.xml'])
        assert args.network == 'x'


def test_create_feed_publish_parser_has_mode_arg():
    """Test parser has --mode argument with choices."""
    mock_subparsers = MagicMock()
    mock_subparsers.add_parser.return_value = ArgumentParser()

    with patch('agoras.cli.utils.feed.PlatformRegistry') as mock_registry:
        mock_registry.get_platform_names.return_value = ['x']
        parser = create_feed_publish_parser(mock_subparsers)

        args = parser.parse_args(['--network', 'x', '--mode', 'last', '--feed-url', 'http://feed.xml'])
        assert args.mode == 'last'

        args = parser.parse_args(['--network', 'x', '--mode', 'random', '--feed-url', 'http://feed.xml'])
        assert args.mode == 'random'


def test_create_feed_publish_parser_has_feed_options():
    """Test parser has feed option group."""
    mock_subparsers = MagicMock()
    mock_subparsers.add_parser.return_value = ArgumentParser()

    with patch('agoras.cli.utils.feed.PlatformRegistry') as mock_registry:
        mock_registry.get_platform_names.return_value = ['x']
        parser = create_feed_publish_parser(mock_subparsers)

        args = parser.parse_args([
            '--network', 'x',
            '--mode', 'last',
            '--feed-url', 'http://feed.xml',
            '--max-count', '5',
            '--post-lookback', '3600',
            '--max-post-age', '7'
        ])

        assert args.feed_url == 'http://feed.xml'
        assert args.max_count == 5
        assert args.post_lookback == 3600
        assert args.max_post_age == 7


# Auth Options Tests

def test_add_all_platform_auth_options_adds_x_auth():
    """Test _add_all_platform_auth_options adds X authentication group."""
    parser = ArgumentParser()
    _add_all_platform_auth_options(parser)

    # Check X auth group exists
    args = parser.parse_args([
        '--x-consumer-key', 'key',
        '--x-consumer-secret', 'secret',
        '--x-oauth-token', 'token',
        '--x-oauth-secret', 'secret2'
    ])

    assert args.x_consumer_key == 'key'
    assert args.x_consumer_secret == 'secret'
    assert args.x_oauth_token == 'token'
    assert args.x_oauth_secret == 'secret2'


def test_add_all_platform_auth_options_adds_twitter_auth():
    """Test _add_all_platform_auth_options adds Twitter (deprecated) authentication group."""
    parser = ArgumentParser()
    _add_all_platform_auth_options(parser)

    args = parser.parse_args([
        '--twitter-consumer-key', 'key',
        '--twitter-consumer-secret', 'secret',
        '--twitter-oauth-token', 'token',
        '--twitter-oauth-secret', 'secret2'
    ])

    assert args.twitter_consumer_key == 'key'
    assert args.twitter_consumer_secret == 'secret'
    assert args.twitter_oauth_token == 'token'
    assert args.twitter_oauth_secret == 'secret2'


def test_add_all_platform_auth_options_adds_facebook_auth():
    """Test _add_all_platform_auth_options adds Facebook authentication group."""
    parser = ArgumentParser()
    _add_all_platform_auth_options(parser)

    args = parser.parse_args([
        '--facebook-access-token', 'token',
        '--facebook-object-id', 'obj123',
        '--facebook-app-id', 'app123'
    ])

    assert args.facebook_access_token == 'token'
    assert args.facebook_object_id == 'obj123'
    assert args.facebook_app_id == 'app123'


def test_add_all_platform_auth_options_adds_all_platforms():
    """Test _add_all_platform_auth_options adds all 10 platform auth groups."""
    parser = ArgumentParser()
    _add_all_platform_auth_options(parser)

    # Test a few key platforms
    args = parser.parse_args([
        '--instagram-access-token', 'token',
        '--linkedin-access-token', 'token2',
        '--discord-bot-token', 'bot123',
        '--youtube-client-id', 'yt123',
        '--tiktok-client-key', 'tt123',
        '--threads-app-id', 'th123',
        '--telegram-bot-token', 'tg123',
        '--whatsapp-access-token', 'wa123'
    ])

    assert args.instagram_access_token == 'token'
    assert args.linkedin_access_token == 'token2'
    assert args.discord_bot_token == 'bot123'
    assert args.youtube_client_id == 'yt123'
    assert args.tiktok_client_key == 'tt123'
    assert args.threads_app_id == 'th123'
    assert args.telegram_bot_token == 'tg123'
    assert args.whatsapp_access_token == 'wa123'


# Handler Tests

@patch('agoras.cli.utils.feed.publish_main')
def test_handle_feed_publish_with_last_mode(mock_publish_main):
    """Test _handle_feed_publish with 'last' mode."""
    mock_publish_main.return_value = 0

    args = Namespace()
    args.network = 'x'
    args.mode = 'last'
    args.feed_url = 'http://feed.xml'
    args.max_count = None
    args.post_lookback = None
    args.max_post_age = None
    args.x_consumer_key = 'key'
    args.x_consumer_secret = 'secret'
    args.handler = None

    result = _handle_feed_publish(args)

    assert result == 0
    mock_publish_main.assert_called_once()
    call_kwargs = mock_publish_main.call_args[1]
    assert call_kwargs['network'] == 'x'
    assert call_kwargs['action'] == 'last-from-feed'
    assert call_kwargs['feed_url'] == 'http://feed.xml'


@patch('agoras.cli.utils.feed.publish_main')
def test_handle_feed_publish_with_random_mode(mock_publish_main):
    """Test _handle_feed_publish with 'random' mode."""
    mock_publish_main.return_value = 0

    args = Namespace()
    args.network = 'facebook'
    args.mode = 'random'
    args.feed_url = 'http://feed.xml'
    args.max_count = 3
    args.post_lookback = 3600
    args.max_post_age = 7
    args.facebook_access_token = 'token'
    args.handler = None

    result = _handle_feed_publish(args)

    assert result == 0
    call_kwargs = mock_publish_main.call_args[1]
    assert call_kwargs['action'] == 'random-from-feed'
    assert call_kwargs['feed_max_count'] == 3
    assert call_kwargs['feed_post_lookback'] == 3600
    assert call_kwargs['feed_max_post_age'] == 7


@patch('agoras.cli.utils.feed.publish_main')
@patch('sys.stderr', new_callable=StringIO)
def test_handle_feed_publish_twitter_deprecation(mock_stderr, mock_publish_main):
    """Test _handle_feed_publish shows Twitter deprecation warning."""
    mock_publish_main.return_value = 0

    args = Namespace()
    args.network = 'twitter'
    args.mode = 'last'
    args.feed_url = 'http://feed.xml'
    args.max_count = None
    args.post_lookback = None
    args.max_post_age = None
    args.handler = None
    args.twitter_consumer_key = None
    args.twitter_consumer_secret = None
    args.twitter_oauth_token = None
    args.twitter_oauth_secret = None
    args.x_consumer_key = None
    args.x_consumer_secret = None
    args.x_oauth_token = None
    args.x_oauth_secret = None

    _handle_feed_publish(args)

    stderr_output = mock_stderr.getvalue()
    assert 'deprecated' in stderr_output.lower() or 'twitter' in stderr_output.lower()
    call_kwargs = mock_publish_main.call_args[1]
    assert call_kwargs['network'] == 'x'  # Should be converted to 'x'


@patch('agoras.cli.utils.feed.publish_main')
@patch('sys.stderr', new_callable=StringIO)
def test_handle_feed_publish_maps_twitter_to_x_params(mock_stderr, mock_publish_main):
    """Test _handle_feed_publish maps twitter-* params to x-* params."""
    mock_publish_main.return_value = 0

    args = Namespace()
    args.network = 'twitter'
    args.mode = 'last'
    args.feed_url = 'http://feed.xml'
    args.max_count = None
    args.post_lookback = None
    args.max_post_age = None
    args.handler = None
    args.twitter_consumer_key = 'old_key'
    args.twitter_consumer_secret = 'old_secret'
    args.twitter_oauth_token = 'old_token'
    args.twitter_oauth_secret = 'old_secret2'
    args.x_consumer_key = None
    args.x_consumer_secret = None
    args.x_oauth_token = None
    args.x_oauth_secret = None

    _handle_feed_publish(args)

    # Check that twitter params were mapped to x params
    assert args.x_consumer_key == 'old_key'
    assert args.x_consumer_secret == 'old_secret'
    assert args.x_oauth_token == 'old_token'
    assert args.x_oauth_secret == 'old_secret2'


@patch('agoras.cli.utils.feed.publish_main')
def test_handle_feed_publish_maps_x_to_twitter_params(mock_publish_main):
    """Test _handle_feed_publish maps x-* params to twitter_* for legacy compatibility."""
    mock_publish_main.return_value = 0

    args = Namespace()
    args.network = 'x'
    args.mode = 'last'
    args.feed_url = 'http://feed.xml'
    args.max_count = None
    args.post_lookback = None
    args.max_post_age = None
    args.handler = None
    args.x_consumer_key = 'new_key'
    args.x_consumer_secret = 'new_secret'
    args.x_oauth_token = 'new_token'
    args.x_oauth_secret = 'new_secret2'
    args.twitter_consumer_key = None
    args.twitter_consumer_secret = None
    args.twitter_oauth_token = None
    args.twitter_oauth_secret = None

    _handle_feed_publish(args)

    # Check that x params were mapped to twitter_* for legacy
    assert args.twitter_consumer_key == 'new_key'
    assert args.twitter_consumer_secret == 'new_secret'
    assert args.twitter_oauth_token == 'new_token'
    assert args.twitter_oauth_secret == 'new_secret2'


@patch('agoras.cli.utils.feed.publish_main')
def test_handle_feed_publish_passes_all_auth_params(mock_publish_main):
    """Test _handle_feed_publish passes all platform auth parameters to legacy."""
    mock_publish_main.return_value = 0

    args = Namespace()
    args.network = 'facebook'
    args.mode = 'last'
    args.feed_url = 'http://feed.xml'
    args.max_count = None
    args.post_lookback = None
    args.max_post_age = None
    args.handler = None
    args.facebook_access_token = 'token'
    args.facebook_object_id = 'obj123'
    args.facebook_app_id = 'app123'

    _handle_feed_publish(args)

    call_kwargs = mock_publish_main.call_args[1]
    assert call_kwargs['facebook_access_token'] == 'token'
    assert call_kwargs['facebook_object_id'] == 'obj123'
    assert call_kwargs['facebook_app_id'] == 'app123'


@patch('agoras.cli.utils.feed.publish_main')
def test_handle_feed_publish_filters_handler_from_legacy_args(mock_publish_main):
    """Test _handle_feed_publish excludes handler from legacy args."""
    mock_publish_main.return_value = 0

    args = Namespace()
    args.network = 'x'
    args.mode = 'last'
    args.feed_url = 'http://feed.xml'
    args.max_count = None
    args.post_lookback = None
    args.max_post_age = None
    args.handler = _handle_feed_publish  # Should be excluded

    _handle_feed_publish(args)

    call_kwargs = mock_publish_main.call_args[1]
    assert 'handler' not in call_kwargs
