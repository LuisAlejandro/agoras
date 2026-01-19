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

from agoras.platforms.linkedin import LinkedIn
from agoras.platforms.linkedin.api import LinkedInAPI

# LinkedIn Wrapper Tests


@pytest.mark.asyncio
@patch('agoras.platforms.linkedin.wrapper.LinkedInAPI')
@patch('agoras.platforms.linkedin.auth.LinkedInAuthManager._load_credentials_from_storage', return_value=False)
async def test_linkedin_initialize_client(mock_load_credentials, mock_api_class):
    """Test LinkedIn _initialize_client extracts config and creates API."""
    mock_api = MagicMock()
    mock_api.authenticate = AsyncMock()
    mock_api_class.return_value = mock_api

    linkedin = LinkedIn(
        linkedin_access_token='test_token'
    )

    await linkedin._initialize_client()

    assert linkedin.linkedin_access_token == 'test_token'
    assert linkedin.api is mock_api
    mock_api.authenticate.assert_called_once()


@pytest.mark.asyncio
@patch('agoras.platforms.linkedin.auth.LinkedInAuthManager._load_credentials_from_storage', return_value=False)
async def test_linkedin_initialize_client_missing_credentials(mock_load_credentials):
    """Test LinkedIn _initialize_client raises exception without credentials."""
    linkedin = LinkedIn()

    with pytest.raises(Exception, match="Not authenticated"):
        await linkedin._initialize_client()


@pytest.mark.asyncio
@patch('agoras.platforms.linkedin.wrapper.LinkedInAPI')
@patch('agoras.platforms.linkedin.auth.LinkedInAuthManager')
async def test_linkedin_initialize_client_loads_from_storage(mock_auth_manager_class, mock_api_class):
    """Test LinkedIn _initialize_client loads credentials from storage when not provided."""
    # Mock auth manager that loads from storage
    mock_auth_manager = MagicMock()
    mock_auth_manager.user_id = 'stored_user_id'
    mock_auth_manager.client_id = 'stored_client_id'
    mock_auth_manager.client_secret = 'stored_client_secret'
    mock_auth_manager.refresh_token = 'stored_refresh_token'
    mock_auth_manager.access_token = 'stored_access_token'
    mock_auth_manager._load_credentials_from_storage = MagicMock(return_value=True)
    mock_auth_manager.authenticate = AsyncMock(return_value=True)
    mock_auth_manager_class.return_value = mock_auth_manager

    # Mock API
    mock_api = MagicMock()
    mock_api.authenticate = AsyncMock()
    mock_api_class.return_value = mock_api

    # Create LinkedIn instance with NO credentials
    linkedin = LinkedIn()

    await linkedin._initialize_client()

    # Verify credentials were loaded from storage
    assert linkedin.linkedin_object_id == 'stored_user_id'
    assert linkedin.linkedin_client_id == 'stored_client_id'
    assert linkedin.linkedin_client_secret == 'stored_client_secret'
    assert linkedin.linkedin_refresh_token == 'stored_refresh_token'
    assert linkedin.linkedin_access_token == 'stored_access_token'
    assert linkedin.api is mock_api
    mock_api.authenticate.assert_called_once()


@pytest.mark.asyncio
@patch('agoras.platforms.linkedin.auth.LinkedInAuthManager')
async def test_linkedin_authorize_credentials(mock_auth_manager_class):
    """Test LinkedIn authorize_credentials method."""
    mock_auth_manager = MagicMock()
    mock_auth_manager.authorize = AsyncMock(return_value="Authorization successful. Credentials stored securely.")
    mock_auth_manager_class.return_value = mock_auth_manager

    linkedin = LinkedIn(
        linkedin_object_id='user123',
        linkedin_client_id='client123',
        linkedin_client_secret='secret123'
    )

    with patch('builtins.print'):
        result = await linkedin.authorize_credentials()

    assert result is True
    mock_auth_manager.authorize.assert_called_once()


@pytest.mark.asyncio
@patch('agoras.platforms.linkedin.auth.LinkedInAuthManager')
async def test_linkedin_authorize_credentials_failure(mock_auth_manager_class):
    """Test LinkedIn authorize_credentials method when authorization fails."""
    mock_auth_manager = MagicMock()
    mock_auth_manager.authorize = AsyncMock(return_value=None)
    mock_auth_manager_class.return_value = mock_auth_manager

    linkedin = LinkedIn(
        linkedin_object_id='user123',
        linkedin_client_id='client123',
        linkedin_client_secret='secret123'
    )

    result = await linkedin.authorize_credentials()

    assert result is False
    mock_auth_manager.authorize.assert_called_once()


@pytest.mark.asyncio
@patch('agoras.platforms.linkedin.wrapper.LinkedInAPI')
async def test_linkedin_post(mock_api_class):
    """Test LinkedIn post method."""
    mock_api = MagicMock()
    mock_api.authenticate = AsyncMock()
    mock_api.post = AsyncMock(return_value='post-123')
    mock_api_class.return_value = mock_api

    linkedin = LinkedIn(linkedin_access_token='token')

    await linkedin._initialize_client()

    with patch.object(linkedin, '_output_status'):
        result = await linkedin.post('Hello LinkedIn', 'http://link.com')

    assert result == 'post-123'


@pytest.mark.asyncio
@patch('agoras.platforms.linkedin.wrapper.LinkedInAPI')
async def test_linkedin_like(mock_api_class):
    """Test LinkedIn like method."""
    mock_api = MagicMock()
    mock_api.authenticate = AsyncMock()
    mock_api.like = AsyncMock(return_value='post-123')
    mock_api_class.return_value = mock_api

    linkedin = LinkedIn(linkedin_access_token='token')

    await linkedin._initialize_client()

    with patch.object(linkedin, '_output_status'):
        result = await linkedin.like('post-123')

    assert result == 'post-123'


@pytest.mark.asyncio
@patch('agoras.platforms.linkedin.wrapper.LinkedInAPI')
async def test_linkedin_share(mock_api_class):
    """Test LinkedIn share method."""
    mock_api = MagicMock()
    mock_api.authenticate = AsyncMock()
    mock_api.share = AsyncMock(return_value='share-456')
    mock_api_class.return_value = mock_api

    linkedin = LinkedIn(linkedin_access_token='token')

    await linkedin._initialize_client()

    with patch.object(linkedin, '_output_status'):
        result = await linkedin.share('post-123')

    assert result == 'share-456'


@pytest.mark.asyncio
@patch('agoras.platforms.linkedin.wrapper.LinkedInAPI')
async def test_linkedin_delete(mock_api_class):
    """Test LinkedIn delete method."""
    mock_api = MagicMock()
    mock_api.authenticate = AsyncMock()
    mock_api.delete = AsyncMock(return_value='post-123')
    mock_api_class.return_value = mock_api

    linkedin = LinkedIn(linkedin_access_token='token')

    await linkedin._initialize_client()

    with patch.object(linkedin, '_output_status'):
        result = await linkedin.delete('post-123')

    assert result == 'post-123'


@pytest.mark.asyncio
@patch('agoras.platforms.linkedin.wrapper.LinkedInAPI')
async def test_linkedin_disconnect(mock_api_class):
    """Test LinkedIn disconnect method."""
    mock_api = MagicMock()
    mock_api.authenticate = AsyncMock()
    mock_api.disconnect = AsyncMock()
    mock_api_class.return_value = mock_api

    linkedin = LinkedIn(linkedin_access_token='token')

    await linkedin._initialize_client()
    await linkedin.disconnect()

    mock_api.disconnect.assert_called_once()


# LinkedIn API Tests

def test_linkedin_api_class_exists():
    """Test LinkedInAPI class exists."""
    assert LinkedInAPI is not None
