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

from agoras.platforms.threads import Threads
from agoras.platforms.threads.api import ThreadsAPI
from agoras.platforms.threads.auth import ThreadsAuthManager
from agoras.platforms.threads.client import ThreadsAPIClient

# Threads Wrapper Tests


@pytest.mark.asyncio
@patch('agoras.platforms.threads.wrapper.ThreadsAPI')
async def test_threads_initialize_client(mock_api_class):
    """Test Threads _initialize_client extracts config and creates API."""
    mock_api = MagicMock()
    mock_api.authenticate = AsyncMock()
    mock_api_class.return_value = mock_api

    threads = Threads(
        threads_app_id='app_id',
        threads_app_secret='app_secret',
        threads_refresh_token='test_token'
    )

    await threads._initialize_client()

    assert threads.threads_refresh_token == 'test_token'
    assert threads.api is mock_api
    mock_api.authenticate.assert_called_once()


@pytest.mark.asyncio
@patch('agoras.platforms.threads.auth.ThreadsAuthManager')
@patch('agoras.platforms.threads.wrapper.Threads._get_config_value')
async def test_threads_initialize_client_missing_credentials(mock_get_config, mock_auth_manager_class):
    """Test Threads _initialize_client raises exception without credentials."""
    # Mock _get_config_value to return None (no credentials available)
    mock_get_config.return_value = None

    # Mock auth manager to not load from storage
    mock_auth_manager = MagicMock()
    mock_auth_manager._load_credentials_from_storage = MagicMock(return_value=False)
    mock_auth_manager_class.return_value = mock_auth_manager

    threads = Threads()

    with pytest.raises(Exception, match="Not authenticated"):
        await threads._initialize_client()


@pytest.mark.asyncio
@patch('agoras.platforms.threads.wrapper.ThreadsAPI')
@patch('agoras.platforms.threads.auth.ThreadsAuthManager')
async def test_threads_initialize_client_loads_from_storage(mock_auth_manager_class, mock_api_class):
    """Test Threads _initialize_client loads credentials from storage when not provided."""
    # Mock auth manager that loads from storage
    mock_auth_manager = MagicMock()
    mock_auth_manager.app_id = 'stored_app_id'
    mock_auth_manager.app_secret = 'stored_app_secret'
    mock_auth_manager.redirect_uri = 'stored_redirect_uri'
    mock_auth_manager.refresh_token = 'stored_refresh_token'
    mock_auth_manager._load_credentials_from_storage = MagicMock(return_value=True)
    mock_auth_manager_class.return_value = mock_auth_manager

    # Mock API
    mock_api = MagicMock()
    mock_api.authenticate = AsyncMock()
    mock_api_class.return_value = mock_api

    # Create Threads instance with NO credentials
    threads = Threads()

    await threads._initialize_client()

    # Verify credentials were loaded from storage
    assert threads.threads_app_id == 'stored_app_id'
    assert threads.threads_app_secret == 'stored_app_secret'
    assert threads.threads_refresh_token == 'stored_refresh_token'
    assert threads.api is mock_api
    mock_api.authenticate.assert_called_once()


@pytest.mark.asyncio
@patch('agoras.platforms.threads.auth.ThreadsAuthManager')
async def test_threads_authorize_credentials(mock_auth_manager_class):
    """Test Threads authorize_credentials method."""
    mock_auth_manager = MagicMock()
    mock_auth_manager.authorize = AsyncMock(return_value="Authorization successful. Credentials stored securely.")
    mock_auth_manager_class.return_value = mock_auth_manager

    threads = Threads(
        threads_app_id='app123',
        threads_app_secret='secret123',
    )

    with patch('builtins.print'):
        result = await threads.authorize_credentials()

    assert result is True
    mock_auth_manager.authorize.assert_called_once()


@pytest.mark.asyncio
@patch('agoras.platforms.threads.auth.ThreadsAuthManager')
async def test_threads_authorize_credentials_failure(mock_auth_manager_class):
    """Test Threads authorize_credentials method when authorization fails."""
    mock_auth_manager = MagicMock()
    mock_auth_manager.authorize = AsyncMock(return_value=None)
    mock_auth_manager_class.return_value = mock_auth_manager

    threads = Threads(
        threads_app_id='app123',
        threads_app_secret='secret123',
    )

    result = await threads.authorize_credentials()

    assert result is False
    mock_auth_manager.authorize.assert_called_once()


@pytest.mark.asyncio
@patch('agoras.platforms.threads.wrapper.ThreadsAPI')
async def test_threads_post(mock_api_class):
    """Test Threads post method."""
    mock_api = MagicMock()
    mock_api.authenticate = AsyncMock()
    mock_api.create_post = AsyncMock(return_value='post-999')
    mock_api_class.return_value = mock_api

    threads = Threads(
        threads_app_id='app_id',
        threads_app_secret='secret',
        threads_access_token='token'
    )

    await threads._initialize_client()

    with patch.object(threads, '_output_status'):
        result = await threads.post('Hello Threads', 'http://link.com')

    assert result == 'post-999'
    mock_api.create_post.assert_called_once()


@pytest.mark.asyncio
@patch('agoras.platforms.threads.wrapper.ThreadsAPI')
async def test_threads_disconnect(mock_api_class):
    """Test Threads disconnect method."""
    mock_api = MagicMock()
    mock_api.authenticate = AsyncMock()
    mock_api.disconnect = AsyncMock()
    mock_api_class.return_value = mock_api

    threads = Threads(
        threads_app_id='app_id',
        threads_app_secret='secret',
        threads_access_token='token'
    )

    await threads._initialize_client()
    await threads.disconnect()

    mock_api.disconnect.assert_called_once()


# Threads API Tests (Skip complex instantiation)

def test_threads_api_class_exists():
    """Test ThreadsAPI class exists."""
    assert ThreadsAPI is not None


# Threads Auth Tests (Abstract - test via concrete usage)

def test_threads_auth_class_exists():
    """Test ThreadsAuthManager class exists."""
    assert ThreadsAuthManager is not None


# Threads Client Tests (Skip complex instantiation)

def test_threads_client_class_exists():
    """Test ThreadsAPIClient class exists."""
    assert ThreadsAPIClient is not None
