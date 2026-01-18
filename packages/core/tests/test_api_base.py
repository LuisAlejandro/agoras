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

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from agoras.core.api_base import BaseAPI


# Concrete implementation for testing
class TestAPI(BaseAPI):
    """Concrete implementation of BaseAPI for testing purposes."""

    async def authenticate(self):
        """Authenticate implementation."""
        self._authenticated = True
        return self

    async def disconnect(self):
        """Disconnect implementation."""
        self._authenticated = False

    async def post(self, *args, **kwargs):
        """Post implementation."""
        return "post-123"

    async def like(self, post_id, *args, **kwargs):
        """Like implementation."""
        return post_id

    async def delete(self, post_id, *args, **kwargs):
        """Delete implementation."""
        return post_id

    async def share(self, post_id, *args, **kwargs):
        """Share implementation."""
        return post_id


def test_baseapi_is_abstract():
    """Test that BaseAPI cannot be instantiated directly."""
    with pytest.raises(TypeError):
        BaseAPI()


def test_baseapi_required_methods():
    """Test that BaseAPI defines required abstract methods."""
    assert hasattr(BaseAPI, 'authenticate')
    assert hasattr(BaseAPI, 'disconnect')


def test_baseapi_rate_limiting():
    """Test that rate limiting structure exists."""
    assert hasattr(BaseAPI, '_rate_limit_check')


def test_baseapi_error_handling():
    """Test that error handling method exists."""
    assert hasattr(BaseAPI, '_handle_api_error')


# Initialization Tests

def test_initialization_with_credentials():
    """Test BaseAPI initialization with credentials."""
    api = TestAPI(api_key='test_key', api_secret='test_secret')

    assert api.credentials == {'api_key': 'test_key', 'api_secret': 'test_secret'}
    assert api.client is None
    assert api._authenticated is False
    assert api._rate_limit_cache == {}
    assert api._last_request_time == 0


def test_initialization_without_credentials():
    """Test BaseAPI initialization without credentials."""
    api = TestAPI()

    assert api.credentials == {}
    assert api._authenticated is False


# Authentication Tests

@pytest.mark.asyncio
async def test_is_authenticated_initial_state():
    """Test is_authenticated returns False initially."""
    api = TestAPI()

    assert api.is_authenticated() is False


@pytest.mark.asyncio
async def test_is_authenticated_after_auth():
    """Test is_authenticated returns True after authentication."""
    api = TestAPI()

    await api.authenticate()

    assert api.is_authenticated() is True


# Rate Limiting Tests

@pytest.mark.asyncio
async def test_rate_limit_check_updates_cache():
    """Test rate_limit_check updates cache after operation."""
    api = TestAPI()

    # First call should update cache
    await api._rate_limit_check(operation_type='test_op', min_interval=0.1)

    assert 'test_op' in api._rate_limit_cache
    assert api._rate_limit_cache['test_op'] > 0


@pytest.mark.asyncio
async def test_rate_limit_check_separate_operations():
    """Test rate_limit_check tracks different operations separately."""
    api = TestAPI()

    await api._rate_limit_check(operation_type='read', min_interval=0.1)
    await api._rate_limit_check(operation_type='write', min_interval=0.1)

    # Both operation types should be in cache
    assert 'read' in api._rate_limit_cache
    assert 'write' in api._rate_limit_cache


# Error Handling Tests

def test_handle_api_error_formats_message():
    """Test _handle_api_error formats error message correctly."""
    api = TestAPI()
    original_error = ValueError("API returned 404")

    with pytest.raises(Exception) as exc_info:
        api._handle_api_error(original_error, "post_creation")

    assert "post_creation failed" in str(exc_info.value)
    assert "API returned 404" in str(exc_info.value)


def test_handle_api_error_chains_exception():
    """Test _handle_api_error chains original exception."""
    api = TestAPI()
    original_error = ConnectionError("Network timeout")

    with pytest.raises(Exception) as exc_info:
        api._handle_api_error(original_error, "authentication")

    # Verify exception chaining
    assert exc_info.value.__cause__ is original_error
    assert "authentication failed" in str(exc_info.value)
