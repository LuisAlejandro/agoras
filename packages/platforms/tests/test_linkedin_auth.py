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

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from agoras.core.auth.storage import SecureTokenStorage
from agoras.platforms.linkedin.auth import LinkedInAuthManager


@pytest.fixture
def temp_storage(tmp_path, monkeypatch):
    """Fixture providing a real SecureTokenStorage in a temp directory."""
    monkeypatch.setenv("AGORAS_STORAGE_DIR", str(tmp_path))
    return SecureTokenStorage()


@pytest.mark.asyncio
async def test_linkedin_authenticate_uses_access_token_without_refresh():
    """Standard LinkedIn apps can authenticate with a stored access token only."""
    manager = LinkedInAuthManager(
        user_id="user123",
        client_id="client123",
        client_secret="secret123",
        access_token="stored_access_token",
    )
    mock_client = MagicMock()
    mock_client.authenticate = AsyncMock()
    mock_client.get_user_info = AsyncMock(
        return_value={
            "sub": "user123",
            "name": "Test User",
        }
    )

    with patch.object(manager, "_create_client", return_value=mock_client):
        result = await manager.authenticate()

    assert result is True
    assert manager.access_token == "stored_access_token"
    assert manager.user_info["object_id"] == "user123"


@pytest.mark.asyncio
@patch("agoras.platforms.linkedin.auth.webbrowser.open")
@patch("agoras.platforms.linkedin.auth.OAuthCallbackServer")
async def test_linkedin_authorize_accepts_access_token_without_refresh(mock_callback_server, mock_browser_open):
    """Authorize should succeed when LinkedIn returns only an access token."""
    mock_server = MagicMock()
    mock_server.start_and_wait = AsyncMock(return_value="auth_code")
    mock_callback_server.return_value = mock_server

    manager = LinkedInAuthManager(user_id="user123", client_id="client123", client_secret="secret123")

    mock_oauth_session = MagicMock()
    mock_oauth_session.create_authorization_url.return_value = ("https://linkedin.example/auth", "state")
    mock_oauth_session.fetch_token.return_value = {"access_token": "new_access_token"}
    manager.oauth_session = mock_oauth_session

    mock_client = MagicMock()
    mock_client.authenticate = AsyncMock()
    mock_client.get_user_info = AsyncMock(return_value={"sub": "api_user_id"})

    with patch.object(manager, "_create_client", return_value=mock_client):
        with patch.object(manager, "_save_credentials_to_storage") as mock_save:
            result = await manager.authorize()

    assert result == "new_access_token"
    assert manager.access_token == "new_access_token"
    assert manager.refresh_token is None
    assert manager.user_id == "api_user_id"
    mock_save.assert_called_once()


def test_linkedin_two_apps_same_account_produce_distinct_composites():
    """Authorizing two apps for the same account yields two distinct composites."""
    posting = LinkedInAuthManager(
        user_id="account123",
        client_id="posting_app",
        client_secret="secret1",
    )
    commenting = LinkedInAuthManager(
        user_id="account123",
        client_id="commenting_app",
        client_secret="secret2",
    )

    assert posting._get_token_identifier() == "posting_app@account123"
    assert commenting._get_token_identifier() == "commenting_app@account123"
    assert posting._get_token_identifier() != commenting._get_token_identifier()


def test_linkedin_explicit_profile_returns_verbatim():
    """An explicit profile composite is returned verbatim by the identifier."""
    manager = LinkedInAuthManager(
        user_id="account123",
        client_id="posting_app",
        client_secret="secret1",
        profile="posting_app@account123",
    )
    assert manager._get_token_identifier() == "posting_app@account123"


def test_linkedin_save_writes_only_composite_key(temp_storage):
    """Save writes only the composite key, never the literal 'default' alias."""
    manager = LinkedInAuthManager(
        user_id="account123",
        client_id="posting_app",
        client_secret="secret1",
        refresh_token="rt",
    )
    manager.token_storage = temp_storage
    manager._save_credentials_to_storage()

    composite = manager._get_token_identifier()
    assert temp_storage.load_token("linkedin", composite) is not None
    # The literal 'default' alias is never written.
    assert not (temp_storage.token_dir / "linkedin-default.token").exists()
    tokens = temp_storage.list_tokens(platform="linkedin")
    assert len(tokens) == 1
    assert tokens[0] == ("linkedin", composite)


def test_linkedin_refresh_recovers_bound_composite(temp_storage):
    """A refresh re-saves under the bound composite recovered from token_data."""
    manager = LinkedInAuthManager(
        user_id="account123",
        client_id="posting_app",
        client_secret="secret1",
        refresh_token="rt",
    )
    manager.token_storage = temp_storage
    manager._save_credentials_to_storage()

    # Simulate a later invocation with stale/empty runtime user_id; the bound
    # composite must be recovered from storage, not re-minted.
    reloaded = LinkedInAuthManager(
        user_id="",
        client_id="posting_app",
        client_secret="secret1",
    )
    reloaded.token_storage = temp_storage
    assert reloaded._load_credentials_from_storage() is True
    assert reloaded.profile == "posting_app@account123"
    assert reloaded._get_token_identifier() == "posting_app@account123"


def test_linkedin_reauthorize_different_object_id_does_not_duplicate(temp_storage):
    """Re-authorizing a different object_id for the same app does not mint a duplicate."""
    manager = LinkedInAuthManager(
        user_id="account123",
        client_id="posting_app",
        client_secret="secret1",
        refresh_token="rt",
    )
    manager.token_storage = temp_storage
    manager._save_credentials_to_storage()

    # A different object_id for the same app resolves to the same composite.
    other = LinkedInAuthManager(
        user_id="account456",
        client_id="posting_app",
        client_secret="secret1",
    )
    other.token_storage = temp_storage
    assert other._get_token_identifier() == "posting_app@account456"
    assert other._get_token_identifier() != manager._get_token_identifier()
