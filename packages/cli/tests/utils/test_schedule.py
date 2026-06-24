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
Tests for schedule run utility command.
"""

from argparse import ArgumentParser, Namespace
from io import StringIO
from unittest.mock import MagicMock, patch

import pytest
from agoras.cli.utils.schedule import _handle_schedule_run, create_schedule_run_parser


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
            '--network', 'x',
            '--sheets-id', 'sheet123',
            '--sheets-name', 'Schedule',
            '--sheets-client-email', 'test@example.com',
            '--sheets-private-key', 'key123'
        ])

        assert args.sheets_id == 'sheet123'
        assert args.sheets_name == 'Schedule'
        assert args.sheets_client_email == 'test@example.com'
        assert args.sheets_private_key == 'key123'


def test_create_schedule_run_parser_network_required():
    """Test parser requires --network."""
    mock_subparsers = MagicMock()
    mock_parser = ArgumentParser()
    mock_subparsers.add_parser.return_value = mock_parser

    with patch('agoras.cli.utils.schedule.PlatformRegistry') as mock_registry:
        mock_registry.get_platform_names.return_value = ['x', 'facebook']
        parser = create_schedule_run_parser(mock_subparsers)

        with pytest.raises(SystemExit):
            parser.parse_args([
                '--sheets-id', 'sheet123',
                '--sheets-name', 'Schedule',
                '--sheets-client-email', 'test@example.com',
                '--sheets-private-key', 'key123'
            ])


def test_create_schedule_run_parser_whatsapp_recipient_optional():
    """Test parser accepts optional WhatsApp recipient without auth flags."""
    mock_subparsers = MagicMock()
    mock_parser = ArgumentParser()
    mock_subparsers.add_parser.return_value = mock_parser

    with patch('agoras.cli.utils.schedule.PlatformRegistry') as mock_registry:
        mock_registry.get_platform_names.return_value = ['whatsapp']
        parser = create_schedule_run_parser(mock_subparsers)

        args = parser.parse_args([
            '--network', 'whatsapp',
            '--sheets-id', 'sheet123',
            '--sheets-name', 'Schedule',
            '--sheets-client-email', 'test@example.com',
            '--sheets-private-key', 'key123',
            '--whatsapp-recipient', '+15551234567',
        ])
        assert args.whatsapp_recipient == '+15551234567'


def test_create_schedule_run_parser_rejects_platform_cred_flags():
    """Test parser rejects removed platform credential flags."""
    mock_subparsers = MagicMock()
    mock_parser = ArgumentParser()
    mock_subparsers.add_parser.return_value = mock_parser

    with patch('agoras.cli.utils.schedule.PlatformRegistry') as mock_registry:
        mock_registry.get_platform_names.return_value = ['facebook']
        parser = create_schedule_run_parser(mock_subparsers)

        with pytest.raises(SystemExit):
            parser.parse_args([
                '--network', 'facebook',
                '--sheets-id', 'sheet123',
                '--sheets-name', 'Schedule',
                '--sheets-client-email', 'test@example.com',
                '--sheets-private-key', 'key123',
                '--facebook-access-token', 'token',
            ])


@patch('agoras.cli.utils.schedule.execute_platform_action')
def test_handle_schedule_run_with_network(mock_execute):
    """Test _handle_schedule_run with network specified."""
    mock_execute.return_value = 0

    args = Namespace(
        network='x',
        sheets_id='sheet123',
        sheets_name='Schedule',
        sheets_client_email='test@example.com',
        sheets_private_key='key123',
        whatsapp_recipient=None,
    )

    result = _handle_schedule_run(args)

    assert result == 0
    mock_execute.assert_called_once()
    call_kwargs = mock_execute.call_args[1]
    assert call_kwargs['action'] == 'schedule'
    assert call_kwargs['network'] == 'x'
    assert call_kwargs['google_sheets_id'] == 'sheet123'
    assert call_kwargs['google_sheets_name'] == 'Schedule'
    assert call_kwargs['google_sheets_client_email'] == 'test@example.com'
    assert call_kwargs['google_sheets_private_key'] == 'key123'
    assert 'x_consumer_key' not in call_kwargs


@patch('agoras.cli.utils.schedule.execute_platform_action')
def test_handle_schedule_run_includes_whatsapp_recipient(mock_execute):
    """Test _handle_schedule_run passes whatsapp_recipient when set."""
    mock_execute.return_value = 0

    args = Namespace(
        network='whatsapp',
        sheets_id='sheet123',
        sheets_name='Schedule',
        sheets_client_email='test@example.com',
        sheets_private_key='key123',
        whatsapp_recipient='+15551234567',
    )

    _handle_schedule_run(args)

    call_kwargs = mock_execute.call_args[1]
    assert call_kwargs['whatsapp_recipient'] == '+15551234567'


@patch('agoras.cli.utils.schedule.execute_platform_action')
@patch('sys.stderr', new_callable=StringIO)
def test_handle_schedule_run_twitter_no_deprecation(mock_stderr, mock_execute):
    """Test _handle_schedule_run does not warn on twitter (runner handles alias)."""
    mock_execute.return_value = 0

    args = Namespace(
        network='twitter',
        sheets_id='sheet123',
        sheets_name='Schedule',
        sheets_client_email='test@example.com',
        sheets_private_key='key123',
        whatsapp_recipient=None,
    )

    _handle_schedule_run(args)

    assert mock_stderr.getvalue() == ''
    call_kwargs = mock_execute.call_args[1]
    assert call_kwargs['network'] == 'twitter'
