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
"""Tests for tokens unattended-format export."""

import tempfile
from argparse import Namespace
from unittest.mock import patch

import pytest

from agoras.cli.utils.tokens import _handle_unattended_format
from agoras.cli.utils.unattended_format import format_unattended_env
from agoras.core.auth.storage import SecureTokenStorage


@pytest.fixture
def temp_storage(monkeypatch):
    """SecureTokenStorage backed by a temporary AGORAS_STORAGE_DIR."""
    with tempfile.TemporaryDirectory() as tmpdir:
        monkeypatch.setenv('AGORAS_STORAGE_DIR', tmpdir)
        yield SecureTokenStorage()


def test_format_x_token_exports_twitter_vars(temp_storage):
    temp_storage.save_token('x', 'default', {
        'consumer_key': 'ck',
        'consumer_secret': 'cs',
        'oauth_token': 'ot',
        'oauth_secret': 'os',
    })

    output = format_unattended_env(temp_storage)

    assert output is not None
    assert 'TWITTER_CONSUMER_KEY=ck' in output
    assert 'TWITTER_CONSUMER_SECRET=cs' in output
    assert 'TWITTER_OAUTH_TOKEN=ot' in output
    assert 'TWITTER_OAUTH_SECRET=os' in output
    assert 'FACEBOOK_APP_ID=' not in output


def test_format_facebook_maps_object_id_and_app_id(temp_storage):
    temp_storage.save_token('facebook', 'default', {
        'user_id': 'page-123',
        'client_id': 'app-456',
        'client_secret': 'secret',
        'refresh_token': 'refresh',
    })

    output = format_unattended_env(temp_storage)

    assert output is not None
    assert 'FACEBOOK_OBJECT_ID=page-123' in output
    assert 'FACEBOOK_CLIENT_ID=app-456' in output
    assert 'FACEBOOK_APP_ID=app-456' in output
    assert 'FACEBOOK_REFRESH_TOKEN=refresh' in output


def test_format_whatsapp_includes_empty_recipient(temp_storage):
    temp_storage.save_token('whatsapp', 'default', {
        'access_token': 'wa-token',
        'phone_number_id': 'phone-1',
    })

    output = format_unattended_env(temp_storage)

    assert output is not None
    assert 'WHATSAPP_ACCESS_TOKEN=wa-token' in output
    assert 'WHATSAPP_PHONE_NUMBER_ID=phone-1' in output
    assert 'WHATSAPP_RECIPIENT=' in output


def test_format_returns_none_when_no_tokens(temp_storage):
    assert format_unattended_env(temp_storage) is None


def test_format_platform_filter_limits_sections(temp_storage):
    temp_storage.save_token('x', 'default', {
        'consumer_key': 'ck',
        'consumer_secret': 'cs',
        'oauth_token': 'ot',
        'oauth_secret': 'os',
    })
    temp_storage.save_token('facebook', 'default', {
        'user_id': 'page-123',
        'client_id': 'app-456',
        'client_secret': 'secret',
        'refresh_token': 'refresh',
    })

    output = format_unattended_env(temp_storage, platforms_filter=['x'])

    assert output is not None
    assert 'TWITTER_CONSUMER_KEY=ck' in output
    assert 'FACEBOOK_APP_ID=' not in output


def test_shell_env_line_quotes_values_with_spaces(temp_storage):
    temp_storage.save_token('discord', 'default', {
        'bot_token': 'bot-token',
        'server_name': 'My Server',
        'channel_name': 'general',
    })

    output = format_unattended_env(temp_storage)

    assert output is not None
    assert "DISCORD_SERVER_NAME='My Server'" in output


def test_handle_unattended_format_writes_stdout_and_warns_stderr(temp_storage, capsys):
    temp_storage.save_token('x', 'default', {
        'consumer_key': 'ck',
        'consumer_secret': 'cs',
        'oauth_token': 'ot',
        'oauth_secret': 'os',
    })

    with patch('agoras.cli.utils.tokens.SecureTokenStorage', return_value=temp_storage):
        status = _handle_unattended_format(Namespace(platforms=None))

    captured = capsys.readouterr()
    assert status == 0
    assert 'TWITTER_CONSUMER_KEY=ck' in captured.out
    assert 'cleartext credentials' in captured.err.lower()


def test_handle_unattended_format_exits_one_when_empty(temp_storage, capsys):
    with patch('agoras.cli.utils.tokens.SecureTokenStorage', return_value=temp_storage):
        status = _handle_unattended_format(Namespace(platforms=None))

    captured = capsys.readouterr()
    assert status == 1
    assert captured.out == ''
    assert 'No stored tokens found' in captured.err


def test_header_includes_agoras_storage_dir(monkeypatch, temp_storage):
    monkeypatch.setenv('AGORAS_STORAGE_DIR', '/tmp/agoras-test')
    temp_storage.save_token('x', 'default', {
        'consumer_key': 'ck',
        'consumer_secret': 'cs',
        'oauth_token': 'ot',
        'oauth_secret': 'os',
    })

    output = format_unattended_env(temp_storage)

    assert output is not None
    assert '# AGORAS_STORAGE_DIR=/tmp/agoras-test' in output
