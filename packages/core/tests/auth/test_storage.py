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

import os
import stat
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from agoras.core.auth.storage import SecureTokenStorage, build_composite_key, validate_identifier


@pytest.fixture
def temp_storage():
    """Fixture to create storage with temporary directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        temp_path = Path(tmpdir)

        with patch('agoras.core.auth.storage.Path.home', return_value=temp_path):
            storage = SecureTokenStorage()
            yield storage


# Basic Instantiation Tests

def test_tokenstorage_instantiation(temp_storage):
    """Test SecureTokenStorage can be instantiated."""
    assert temp_storage is not None
    assert temp_storage.token_dir.exists()


def test_securetokenstorage_instantiation(temp_storage):
    """Test SecureTokenStorage can be instantiated."""
    assert temp_storage is not None


# Key Management Tests

def test_key_file_created(temp_storage):
    """Test key file is created on initialization."""
    assert temp_storage.key_file.exists()


def test_key_file_permissions(temp_storage):
    """Test key file has secure permissions (0o600)."""
    key_file = temp_storage.key_file
    assert key_file.exists()

    mode = key_file.stat().st_mode
    # Should be 0o600 (owner read/write only)
    assert stat.S_IMODE(mode) == 0o600


def test_key_generation_creates_new_key():
    """Test key generation creates new key when no key exists."""
    with tempfile.TemporaryDirectory() as tmpdir:
        temp_path = Path(tmpdir)

        with patch('agoras.core.auth.storage.Path.home', return_value=temp_path):
            storage = SecureTokenStorage()

            # Key file should be created
            assert storage.key_file.exists()
            assert len(storage.key) > 0


def test_key_loading_from_existing_file():
    """Test key is loaded from existing file."""
    with tempfile.TemporaryDirectory() as tmpdir:
        temp_path = Path(tmpdir)

        with patch('agoras.core.auth.storage.Path.home', return_value=temp_path):
            # Create first storage instance
            storage1 = SecureTokenStorage()
            key1 = storage1.key

            # Create second storage instance (should load same key)
            storage2 = SecureTokenStorage()
            key2 = storage2.key

            assert key1 == key2


def test_key_file_location(temp_storage):
    """Test key file is stored in correct location."""
    # Should be in ~/.agoras/.key
    assert temp_storage.key_file.name == '.key'
    assert temp_storage.key_file.parent.name == '.agoras'


# Enhanced Save/Load Tests

def test_tokenstorage_save_and_load(temp_storage):
    """Test SecureTokenStorage save and load methods."""
    test_tokens = {'access_token': 'test123', 'refresh_token': 'refresh456'}

    # Save tokens
    temp_storage.save_token('test_platform', 'test_user', test_tokens)

    # Load tokens
    loaded = temp_storage.load_token('test_platform', 'test_user')
    assert loaded == test_tokens


def test_save_creates_encrypted_file(temp_storage):
    """Test save creates encrypted file (not plaintext)."""
    token_data = {'secret': 'very_secret_value'}
    temp_storage.save_token('test', 'user', token_data)

    # File should exist
    token_file = temp_storage.token_dir / 'test-user.token'
    assert token_file.exists()

    # Read raw file
    raw_data = token_file.read_bytes()

    # Should not contain plaintext secret
    assert b'very_secret_value' not in raw_data
    assert b'secret' not in raw_data


def test_save_sets_file_permissions(temp_storage):
    """Test save sets secure file permissions."""
    temp_storage.save_token('test', 'user', {'token': 'value'})

    token_file = temp_storage.token_dir / 'test-user.token'
    mode = token_file.stat().st_mode

    # Should be 0o600
    assert stat.S_IMODE(mode) == 0o600


def test_load_with_corrupted_data(temp_storage):
    """Test load_token returns None with corrupted data."""
    token_file = temp_storage.token_dir / 'corrupted-user.token'

    # Write invalid encrypted data
    token_file.write_bytes(b'invalid encrypted data')

    # Should return None, not raise exception
    result = temp_storage.load_token('corrupted', 'user')

    assert result is None


def test_load_with_non_existent_token(temp_storage):
    """Test load_token returns None for non-existent token."""
    result = temp_storage.load_token('nonexistent', 'user')

    assert result is None


def test_securetokenstorage_encryption(temp_storage):
    """Test SecureTokenStorage encrypts tokens."""
    test_tokens = {'access_token': 'secret123'}

    temp_storage.save_token('test_platform', 'test_user', test_tokens)
    loaded = temp_storage.load_token('test_platform', 'test_user')

    # Should decrypt correctly
    assert loaded == test_tokens


# List Tokens Tests

def test_list_tokens_returns_all(temp_storage):
    """Test list_tokens returns all tokens."""
    temp_storage.save_token('facebook', 'user1', {'token': 'fb1'})
    temp_storage.save_token('instagram', 'user2', {'token': 'ig1'})
    temp_storage.save_token('twitter', 'user3', {'token': 'tw1'})

    tokens = temp_storage.list_tokens()

    assert len(tokens) == 3
    assert ('facebook', 'user1') in tokens
    assert ('instagram', 'user2') in tokens
    assert ('twitter', 'user3') in tokens


def test_list_tokens_filters_by_platform(temp_storage):
    """Test list_tokens filters by platform."""
    temp_storage.save_token('facebook', 'user1', {'token': 'fb1'})
    temp_storage.save_token('facebook', 'user2', {'token': 'fb2'})
    temp_storage.save_token('instagram', 'user3', {'token': 'ig1'})

    tokens = temp_storage.list_tokens(platform='facebook')

    assert len(tokens) == 2
    assert all(plat == 'facebook' for plat, _ in tokens)


def test_list_tokens_empty(temp_storage):
    """Test list_tokens returns empty list when no tokens."""
    tokens = temp_storage.list_tokens()

    assert tokens == []


def test_list_tokens_with_hyphen_in_identifier(temp_storage):
    """Test list_tokens parses filename with hyphen in identifier correctly."""
    temp_storage.save_token('facebook', 'user-with-hyphens', {'token': 'value'})

    tokens = temp_storage.list_tokens()

    assert len(tokens) == 1
    # Should correctly identify platform and identifier even with hyphens
    assert tokens[0] == ('facebook', 'user-with-hyphens')


def test_list_tokens_skips_invalid_files(temp_storage):
    """Test list_tokens skips files without proper format."""
    # Create file without proper format (no hyphen)
    invalid_file = temp_storage.token_dir / 'invalidfile.token'
    invalid_file.write_text('invalid')

    # Should not raise exception
    tokens = temp_storage.list_tokens()

    # Should be empty or not include invalid file
    assert all(isinstance(t, tuple) and len(t) == 2 for t in tokens)


# Environment Seeding Tests

def test_seed_from_environment_with_env_var(temp_storage):
    """Test seed_from_environment saves token from env var."""
    with patch.dict(os.environ, {'FACEBOOK_REFRESH_TOKEN': 'env_refresh_token'}):
        result = temp_storage.seed_from_environment('facebook', 'user1')

        assert result is True

        # Verify token saved
        loaded = temp_storage.load_token('facebook', 'user1')
        assert loaded is not None
        assert loaded['refresh_token'] == 'env_refresh_token'


def test_seed_from_environment_returns_false_when_no_env(temp_storage):
    """Test seed_from_environment returns False when no env var."""
    result = temp_storage.seed_from_environment('facebook', 'user1')

    assert result is False


def test_seed_from_environment_uppercase_conversion(temp_storage):
    """Test seed_from_environment converts platform to uppercase for env var."""
    with patch.dict(os.environ, {'INSTAGRAM_REFRESH_TOKEN': 'ig_token'}):
        result = temp_storage.seed_from_environment('instagram', 'user1')

        assert result is True


def test_seed_from_environment_mixed_case_platform(temp_storage):
    """Test seed_from_environment handles mixed case platform names."""
    with patch.dict(os.environ, {'LINKEDIN_REFRESH_TOKEN': 'li_token'}):
        # Platform name in mixed case should be uppercased
        result = temp_storage.seed_from_environment('LinkedIn', 'user1')

        assert result is True


def test_seeded_token_can_be_loaded(temp_storage):
    """Test token seeded from environment can be loaded."""
    with patch.dict(os.environ, {'TWITTER_REFRESH_TOKEN': 'twitter_refresh'}):
        temp_storage.seed_from_environment('twitter', 'user1')

        loaded = temp_storage.load_token('twitter', 'user1')

        assert loaded is not None
        assert 'refresh_token' in loaded
        assert loaded['refresh_token'] == 'twitter_refresh'


# Additional Edge Case Tests

def test_save_load_complex_token_data(temp_storage):
    """Test save/load with complex token data structure."""
    complex_data = {
        'access_token': 'access123',
        'refresh_token': 'refresh456',
        'expires_at': 1234567890,
        'scopes': ['read', 'write', 'admin'],
        'metadata': {
            'user_id': '12345',
            'username': 'testuser'
        }
    }

    temp_storage.save_token('complex', 'user', complex_data)
    loaded = temp_storage.load_token('complex', 'user')

    assert loaded == complex_data
    assert loaded['metadata']['user_id'] == '12345'


def test_multiple_identifiers_same_platform(temp_storage):
    """Test multiple identifiers for same platform."""
    temp_storage.save_token('facebook', 'user1', {'token': 'tok1'})
    temp_storage.save_token('facebook', 'user2', {'token': 'tok2'})
    temp_storage.save_token('facebook', 'user3', {'token': 'tok3'})

    # Each should be stored separately
    assert temp_storage.load_token('facebook', 'user1')['token'] == 'tok1'
    assert temp_storage.load_token('facebook', 'user2')['token'] == 'tok2'
    assert temp_storage.load_token('facebook', 'user3')['token'] == 'tok3'

    # List should show all three
    tokens = temp_storage.list_tokens(platform='facebook')
    assert len(tokens) == 3


# Composite Profile Key Tests (U1)

def test_build_composite_key_joins_app_and_account():
    """Test build_composite_key joins app and account with the delimiter."""
    assert build_composite_key("app123", "user456") == "app123@user456"


def test_build_composite_key_rejects_reserved_component():
    """Test build_composite_key rejects the reserved 'default' component."""
    with pytest.raises(ValueError):
        build_composite_key("default", "user456")
    with pytest.raises(ValueError):
        build_composite_key("app123", "default")


def test_build_composite_key_rejects_path_separators():
    """Test build_composite_key rejects path separators and dot components."""
    for bad in ("../evil", "a/b", "a\\b", ".", ".."):
        with pytest.raises(ValueError):
            build_composite_key(bad, "user456")
        with pytest.raises(ValueError):
            build_composite_key("app123", bad)


def test_build_composite_key_rejects_delimiter_in_component():
    """Test build_composite_key rejects a component containing the delimiter."""
    with pytest.raises(ValueError):
        build_composite_key("app@x", "user456")


def test_validate_identifier_rejects_reserved_and_paths():
    """Test validate_identifier rejects reserved names and path separators."""
    for bad in ("default", "../evil", "a/b", "a\\b", ".", "..", ""):
        with pytest.raises(ValueError):
            validate_identifier(bad)


def test_validate_identifier_allows_composite_delimiter():
    """Test validate_identifier allows the composite delimiter inside a key."""
    assert validate_identifier("app123@user456") == "app123@user456"


def test_composite_keyed_token_round_trip(temp_storage):
    """Test save/load/delete/list a composite-keyed token round-trips."""
    composite = build_composite_key("app123", "user456")
    temp_storage.save_token("linkedin", composite, {"refresh_token": "tok"})

    assert temp_storage.load_token("linkedin", composite)["refresh_token"] == "tok"

    tokens = temp_storage.list_tokens(platform="linkedin")
    assert (("linkedin", composite)) in tokens


def test_list_tokens_parses_composite_delimiter(temp_storage):
    """Test list_tokens parses a composite containing '@' without mis-splitting."""
    temp_storage.save_token("linkedin", "app123@user456", {"refresh_token": "tok"})
    temp_storage.save_token("linkedin", "app789@user456", {"refresh_token": "tok2"})

    tokens = temp_storage.list_tokens(platform="linkedin")
    assert len(tokens) == 2
    assert ("linkedin", "app123@user456") in tokens
    assert ("linkedin", "app789@user456") in tokens


def test_default_identifier_rejected_on_save(temp_storage):
    """Test saving under the reserved 'default' identifier is rejected."""
    with pytest.raises(ValueError):
        temp_storage.save_token("linkedin", "default", {"refresh_token": "tok"})
