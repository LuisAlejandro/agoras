# -*- coding: utf-8 -*-
#
# Please refer to AUTHORS.rst for a complete list of Copyright holders.
# Copyright (C) 2022-2026, Agoras Developers.

import pytest

from agoras.core.auth.exceptions import AuthenticationError
from agoras.core.auth.failure import AuthFailureCategory
from agoras.platforms.youtube.api import YouTubeAPI
from agoras.platforms.youtube.auth import YouTubeAuthManager


@pytest.mark.asyncio
async def test_youtube_api_authenticate_surfaces_invalid_grant(monkeypatch):
    manager = YouTubeAuthManager(
        client_id="client",
        client_secret="secret",
        refresh_token="stale-token",
    )

    async def fake_refresh():
        raise Exception('Token refresh failed: 400 {"error":"invalid_grant"}')

    monkeypatch.setattr(manager, "_refresh_access_token_with_authlib", fake_refresh)

    api = YouTubeAPI(client_id="client", client_secret="secret", refresh_token="stale-token")
    api.auth_manager = manager

    with pytest.raises(AuthenticationError) as exc_info:
        await api.authenticate()

    assert exc_info.value.details is not None
    assert exc_info.value.details.category == AuthFailureCategory.EXPIRED_OR_REVOKED
    assert exc_info.value.details.provider_code == "invalid_grant"
    assert "invalid_grant" in str(exc_info.value)
