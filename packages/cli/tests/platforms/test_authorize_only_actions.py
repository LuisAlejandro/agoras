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
Tests that platform action commands reject auth CLI flags.
"""

from argparse import ArgumentParser

import pytest
from agoras.cli.main import commandline
from agoras.cli.platforms.discord import create_discord_parser
from agoras.cli.platforms.telegram import create_telegram_parser
from agoras.cli.platforms.whatsapp import create_whatsapp_parser
from agoras.cli.platforms.x import create_twitter_parser_alias, create_x_parser


def _parse_or_fail(root_parser, argv):
    with pytest.raises(SystemExit):
        root_parser.parse_args(argv)


@pytest.mark.parametrize('platform,parser_factory,auth_argv', [
    ('x', create_x_parser, ['--consumer-key', 'k']),
    ('twitter', create_twitter_parser_alias, ['--consumer-key', 'k']),
    ('discord', create_discord_parser, ['--bot-token', 't']),
    ('telegram', create_telegram_parser, ['--bot-token', 't']),
    ('whatsapp', create_whatsapp_parser, ['--access-token', 't']),
])
def test_action_rejects_auth_flags(platform, parser_factory, auth_argv):
    """Platform actions must not accept credential flags on the command line."""
    root_parser = ArgumentParser()
    subparsers = root_parser.add_subparsers(dest='platform')
    parser_factory(subparsers)

    _parse_or_fail(root_parser, [platform, 'post'] + auth_argv)


def test_x_post_parses_content_only():
    """X post accepts content flags without auth flags."""
    root_parser = ArgumentParser()
    subparsers = root_parser.add_subparsers(dest='platform')
    create_x_parser(subparsers)

    args = root_parser.parse_args(['x', 'post', '--text', 'Hello'])
    assert args.text == 'Hello'


def test_telegram_post_keeps_parse_mode():
    """Telegram post keeps parse-mode while rejecting bot-token."""
    root_parser = ArgumentParser()
    subparsers = root_parser.add_subparsers(dest='platform')
    create_telegram_parser(subparsers)

    args = root_parser.parse_args([
        'telegram', 'post', '--parse-mode', 'Markdown', '--text', 'Hi'
    ])
    assert args.parse_mode == 'Markdown'
    assert args.text == 'Hi'


def test_whatsapp_post_keeps_recipient():
    """WhatsApp post keeps recipient while rejecting access-token."""
    root_parser = ArgumentParser()
    subparsers = root_parser.add_subparsers(dest='platform')
    create_whatsapp_parser(subparsers)

    args = root_parser.parse_args([
        'whatsapp', 'post', '--recipient', '+15551234567', '--text', 'Hi'
    ])
    assert args.recipient == '+15551234567'
    assert args.text == 'Hi'


def test_x_authorize_still_accepts_credentials():
    """X authorize still requires consumer key and secret."""
    root_parser = ArgumentParser()
    subparsers = root_parser.add_subparsers(dest='platform')
    create_x_parser(subparsers)

    args = root_parser.parse_args([
        'x', 'authorize', '--consumer-key', 'k', '--consumer-secret', 's'
    ])
    assert args.consumer_key == 'k'
    assert args.consumer_secret == 's'


def test_x_post_help_has_no_authentication_group(capsys):
    """X post --help must not advertise an Authentication option group."""
    with pytest.raises(SystemExit):
        commandline(['x', 'post', '--help'])

    captured = capsys.readouterr()
    assert 'Authentication' not in captured.out
