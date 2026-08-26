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

from agoras.platforms.linkedin.auth import LinkedInAuthManager


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
