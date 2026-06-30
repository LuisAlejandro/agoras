# -*- coding: utf-8 -*-
"""Shared credentials and auth mocks for platform wrapper tests."""

from unittest.mock import AsyncMock, MagicMock

INSTAGRAM_KWARGS = {
    'instagram_access_token': 'token',
    'instagram_object_id': 'user123',
    'instagram_client_id': 'client_id',
    'instagram_client_secret': 'client_secret',
    'instagram_refresh_token': 'refresh_token',
}

LINKEDIN_KWARGS = {
    'linkedin_access_token': 'token',
    'linkedin_object_id': 'user123',
    'linkedin_client_id': 'client_id',
    'linkedin_client_secret': 'client_secret',
    'linkedin_refresh_token': 'refresh_token',
}

YOUTUBE_KWARGS = {
    'youtube_client_id': 'client_id',
    'youtube_client_secret': 'client_secret',
    'youtube_refresh_token': 'refresh_token',
}

SAMPLE_IMAGE_URL = 'http://example.com/image.jpg'


def configure_instagram_auth_mock(mock_auth_manager_class, access_token='token'):
    """Wire InstagramAuthManager mock for _initialize_client tests."""
    mock_auth = MagicMock()
    mock_auth.authenticate = AsyncMock(return_value=True)
    mock_auth.access_token = access_token
    mock_auth._load_credentials_from_storage = MagicMock(return_value=False)
    mock_auth_manager_class.return_value = mock_auth
    return mock_auth


def configure_linkedin_auth_mock(mock_auth_manager_class, access_token='token'):
    """Wire LinkedInAuthManager mock for _initialize_client tests."""
    mock_auth = MagicMock()
    mock_auth.authenticate = AsyncMock(return_value=True)
    mock_auth.access_token = access_token
    mock_auth._load_credentials_from_storage = MagicMock(return_value=False)
    mock_auth_manager_class.return_value = mock_auth
    return mock_auth
