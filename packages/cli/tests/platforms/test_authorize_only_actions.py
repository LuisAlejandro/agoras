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


def test_x_post_accepts_profile_flag():
    """X post accepts --profile without auth flags."""
    root_parser = ArgumentParser()
    subparsers = root_parser.add_subparsers(dest='platform')
    create_x_parser(subparsers)

    args = root_parser.parse_args(['x', 'post', '--text', 'Hello', '--profile', 'app@acct'])
    assert args.profile == 'app@acct'
    assert args.text == 'Hello'


def test_x_authorize_accepts_profile_flag():
    """X authorize accepts --profile alongside credentials."""
    root_parser = ArgumentParser()
    subparsers = root_parser.add_subparsers(dest='platform')
    create_x_parser(subparsers)

    args = root_parser.parse_args([
        'x', 'authorize', '--consumer-key', 'k', '--consumer-secret', 's', '--profile', 'app@acct'
    ])
    assert args.profile == 'app@acct'
    assert args.consumer_key == 'k'


def test_resolve_profile_single_auto_selects(monkeypatch, tmp_path):
    """Single stored profile auto-selects with no prompt."""
    from agoras.cli.base import resolve_profile
    from agoras.core.auth.storage import SecureTokenStorage

    monkeypatch.setenv("AGORAS_STORAGE_DIR", str(tmp_path))
    storage = SecureTokenStorage()
    storage.save_token("x", "app@acct", {"consumer_key": "k"})

    assert resolve_profile("x", None) == "app@acct"


def test_resolve_profile_explicit_selector(monkeypatch, tmp_path):
    """--profile selects the named composite."""
    from agoras.cli.base import resolve_profile
    from agoras.core.auth.storage import SecureTokenStorage

    monkeypatch.setenv("AGORAS_STORAGE_DIR", str(tmp_path))
    storage = SecureTokenStorage()
    storage.save_token("x", "app1@acct", {"consumer_key": "k"})
    storage.save_token("x", "app2@acct", {"consumer_key": "k"})

    assert resolve_profile("x", "app2@acct") == "app2@acct"


def test_resolve_profile_invalid_selector_fails_fast(monkeypatch, tmp_path, capsys):
    """A --profile that matches no stored profile fails fast with the list."""
    from agoras.cli.base import resolve_profile
    from agoras.core.auth.storage import SecureTokenStorage

    monkeypatch.setenv("AGORAS_STORAGE_DIR", str(tmp_path))
    storage = SecureTokenStorage()
    storage.save_token("x", "app1@acct", {"consumer_key": "k"})

    with pytest.raises(SystemExit) as exc:
        resolve_profile("x", "nope@acct")
    assert exc.value.code == 2
    captured = capsys.readouterr()
    assert "app1@acct" in captured.err


def test_resolve_profile_multi_non_tty_fails_hard(monkeypatch, tmp_path, capsys):
    """Multi-profile + non-tty fails hard with the profile list and exit code 2."""
    from agoras.cli.base import resolve_profile
    from agoras.core.auth.storage import SecureTokenStorage

    monkeypatch.setenv("AGORAS_STORAGE_DIR", str(tmp_path))
    storage = SecureTokenStorage()
    storage.save_token("x", "app1@acct", {"consumer_key": "k"})
    storage.save_token("x", "app2@acct", {"consumer_key": "k"})

    with pytest.raises(SystemExit) as exc:
        resolve_profile("x", None)
    assert exc.value.code == 2
    captured = capsys.readouterr()
    assert "app1@acct" in captured.err
    assert "app2@acct" in captured.err


def test_resolve_profile_skips_legacy_default(monkeypatch, tmp_path):
    """A legacy 'default' token is not surfaced as a selectable profile."""
    from agoras.cli.base import resolve_profile
    from agoras.core.auth.storage import SecureTokenStorage

    monkeypatch.setenv("AGORAS_STORAGE_DIR", str(tmp_path))
    storage = SecureTokenStorage()
    storage.save_token("x", "app@acct", {"consumer_key": "k"})
    # Simulate a legacy pre-refactor token under the reserved 'default' alias
    # by writing the file directly (save_token now rejects reserved names).
    (storage.token_dir / "x-default.token").write_text("legacy")

    # Only the composite profile is selectable; 'default' is filtered out.
    assert resolve_profile("x", None) == "app@acct"


def test_env_credential_state_complete(monkeypatch):
    """A full env set reports complete."""
    from agoras.cli.base import env_credential_state

    monkeypatch.setenv("TWITTER_CONSUMER_KEY", "k")
    monkeypatch.setenv("TWITTER_CONSUMER_SECRET", "s")
    monkeypatch.setenv("TWITTER_OAUTH_TOKEN", "t")
    monkeypatch.setenv("TWITTER_OAUTH_SECRET", "o")

    assert env_credential_state("x") == "complete"


def test_env_credential_state_partial(monkeypatch):
    """A partial env set reports partial."""
    from agoras.cli.base import env_credential_state

    monkeypatch.setenv("TWITTER_CONSUMER_KEY", "k")

    assert env_credential_state("x") == "partial"


def test_env_credential_state_none(monkeypatch):
    """No env vars reports none."""
    from agoras.cli.base import env_credential_state

    monkeypatch.delenv("TWITTER_CONSUMER_KEY", raising=False)
    monkeypatch.delenv("TWITTER_CONSUMER_SECRET", raising=False)
    monkeypatch.delenv("TWITTER_OAUTH_TOKEN", raising=False)
    monkeypatch.delenv("TWITTER_OAUTH_SECRET", raising=False)

    assert env_credential_state("x") == "none"


def test_env_credential_state_linkedin_complete(monkeypatch):
    """LinkedIn env is complete with client id/secret plus a token."""
    from agoras.cli.base import env_credential_state

    monkeypatch.setenv("LINKEDIN_CLIENT_ID", "id")
    monkeypatch.setenv("LINKEDIN_CLIENT_SECRET", "sec")
    monkeypatch.setenv("LINKEDIN_REFRESH_TOKEN", "tok")

    assert env_credential_state("linkedin") == "complete"


def test_env_credential_state_linkedin_partial(monkeypatch):
    """LinkedIn env without a token is partial."""
    from agoras.cli.base import env_credential_state

    monkeypatch.setenv("LINKEDIN_CLIENT_ID", "id")
    monkeypatch.setenv("LINKEDIN_CLIENT_SECRET", "sec")
    monkeypatch.delenv("LINKEDIN_REFRESH_TOKEN", raising=False)
    monkeypatch.delenv("LINKEDIN_ACCESS_TOKEN", raising=False)

    assert env_credential_state("linkedin") == "partial"


def test_resolve_action_profile_complete_env_skips_storage(monkeypatch, tmp_path):
    """A complete env set wins wholesale; no profile is injected."""
    from argparse import Namespace
    from agoras.cli.base import resolve_action_profile
    from agoras.core.auth.storage import SecureTokenStorage

    monkeypatch.setenv("AGORAS_STORAGE_DIR", str(tmp_path))
    storage = SecureTokenStorage()
    storage.save_token("x", "app1@acct", {"consumer_key": "k"})

    monkeypatch.setenv("TWITTER_CONSUMER_KEY", "k")
    monkeypatch.setenv("TWITTER_CONSUMER_SECRET", "s")
    monkeypatch.setenv("TWITTER_OAUTH_TOKEN", "t")
    monkeypatch.setenv("TWITTER_OAUTH_SECRET", "o")

    legacy_args = {}
    resolve_action_profile("x", Namespace(action="post", profile=None), legacy_args)
    assert "profile" not in legacy_args


def test_resolve_action_profile_partial_env_fails_fast(monkeypatch, tmp_path, capsys):
    """A partial env set fails fast rather than blending with storage."""
    from argparse import Namespace
    from agoras.cli.base import resolve_action_profile
    from agoras.core.auth.storage import SecureTokenStorage

    monkeypatch.setenv("AGORAS_STORAGE_DIR", str(tmp_path))
    storage = SecureTokenStorage()
    storage.save_token("x", "app1@acct", {"consumer_key": "k"})

    monkeypatch.setenv("TWITTER_CONSUMER_KEY", "k")
    monkeypatch.delenv("TWITTER_CONSUMER_SECRET", raising=False)
    monkeypatch.delenv("TWITTER_OAUTH_TOKEN", raising=False)
    monkeypatch.delenv("TWITTER_OAUTH_SECRET", raising=False)

    legacy_args = {}
    with pytest.raises(SystemExit) as exc:
        resolve_action_profile("x", Namespace(action="post", profile=None), legacy_args)
    assert exc.value.code == 2
    captured = capsys.readouterr()
    assert "TWITTER_CONSUMER_SECRET" in captured.err


def test_resolve_action_profile_explicit_selector_overrides_env(monkeypatch, tmp_path):
    """An explicit --profile makes the selected profile the sole source."""
    from argparse import Namespace
    from agoras.cli.base import resolve_action_profile
    from agoras.core.auth.storage import SecureTokenStorage

    monkeypatch.setenv("AGORAS_STORAGE_DIR", str(tmp_path))
    storage = SecureTokenStorage()
    storage.save_token("x", "app1@acct", {"consumer_key": "k"})

    monkeypatch.setenv("TWITTER_CONSUMER_KEY", "k")
    monkeypatch.setenv("TWITTER_CONSUMER_SECRET", "s")
    monkeypatch.setenv("TWITTER_OAUTH_TOKEN", "t")
    monkeypatch.setenv("TWITTER_OAUTH_SECRET", "o")

    legacy_args = {}
    resolve_action_profile("x", Namespace(action="post", profile="app1@acct"), legacy_args)
    assert legacy_args["profile"] == "app1@acct"


def test_resolve_action_profile_skips_authorize(monkeypatch, tmp_path):
    """Authorize never resolves a profile (it creates one)."""
    from argparse import Namespace
    from agoras.cli.base import resolve_action_profile

    legacy_args = {}
    resolve_action_profile("x", Namespace(action="authorize", profile=None), legacy_args)
    assert "profile" not in legacy_args
