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
Tests for feed publish utility command.
"""

from argparse import ArgumentParser, Namespace
from io import StringIO
from unittest.mock import MagicMock, patch

import pytest
from agoras.cli.utils.feed import _handle_feed_publish, create_feed_publish_parser


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

        with pytest.raises(SystemExit):
            parser.parse_args([])


def test_create_feed_publish_parser_has_network_arg():
    """Test parser has --network argument with choices."""
    mock_subparsers = MagicMock()
    mock_subparsers.add_parser.return_value = ArgumentParser()

    with patch('agoras.cli.utils.feed.PlatformRegistry') as mock_registry:
        mock_registry.get_platform_names.return_value = ['x', 'facebook', 'instagram']
        parser = create_feed_publish_parser(mock_subparsers)

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


def test_create_feed_publish_parser_rejects_platform_cred_flags():
    """Test parser rejects removed platform credential flags."""
    mock_subparsers = MagicMock()
    mock_subparsers.add_parser.return_value = ArgumentParser()

    with patch('agoras.cli.utils.feed.PlatformRegistry') as mock_registry:
        mock_registry.get_platform_names.return_value = ['x']
        parser = create_feed_publish_parser(mock_subparsers)

        with pytest.raises(SystemExit):
            parser.parse_args([
                '--network', 'x',
                '--mode', 'last',
                '--feed-url', 'http://feed.xml',
                '--x-consumer-key', 'key',
            ])


@patch('agoras.cli.utils.feed.execute_platform_action')
def test_handle_feed_publish_with_last_mode(mock_execute):
    """Test _handle_feed_publish with 'last' mode."""
    mock_execute.return_value = 0

    args = Namespace(
        network='x',
        mode='last',
        feed_url='http://feed.xml',
        max_count=None,
        post_lookback=None,
        max_post_age=None,
    )

    result = _handle_feed_publish(args)

    assert result == 0
    mock_execute.assert_called_once()
    call_kwargs = mock_execute.call_args[1]
    assert call_kwargs == {
        'network': 'x',
        'action': 'last-from-feed',
        'feed_url': 'http://feed.xml',
        'max_count': None,
        'post_lookback': None,
        'max_post_age': None,
    }


@patch('agoras.cli.utils.feed.execute_platform_action')
def test_handle_feed_publish_with_random_mode(mock_execute):
    """Test _handle_feed_publish with 'random' mode."""
    mock_execute.return_value = 0

    args = Namespace(
        network='facebook',
        mode='random',
        feed_url='http://feed.xml',
        max_count=3,
        post_lookback=3600,
        max_post_age=7,
    )

    result = _handle_feed_publish(args)

    assert result == 0
    call_kwargs = mock_execute.call_args[1]
    assert call_kwargs['action'] == 'random-from-feed'
    assert call_kwargs['max_count'] == 3
    assert call_kwargs['post_lookback'] == 3600
    assert call_kwargs['max_post_age'] == 7


@patch('agoras.cli.utils.feed.execute_platform_action')
@patch('sys.stderr', new_callable=StringIO)
def test_handle_feed_publish_twitter_no_deprecation(mock_stderr, mock_execute):
    """Test _handle_feed_publish does not warn on twitter (runner handles alias)."""
    mock_execute.return_value = 0

    args = Namespace(
        network='twitter',
        mode='last',
        feed_url='http://feed.xml',
        max_count=None,
        post_lookback=None,
        max_post_age=None,
    )

    _handle_feed_publish(args)

    assert mock_stderr.getvalue() == ''
    call_kwargs = mock_execute.call_args[1]
    assert call_kwargs['network'] == 'twitter'
