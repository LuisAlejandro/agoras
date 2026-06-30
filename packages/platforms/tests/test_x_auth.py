# -*- coding: utf-8 -*-
#
# Please refer to AUTHORS.rst for a complete list of Copyright holders.
# Copyright (C) 2022-2026, Agoras Developers.

import pytest

from agoras.core.auth.exceptions import AuthenticationError
from agoras.core.auth.failure import AuthFailureCategory
from agoras.platforms.x.api import XAPI
from agoras.platforms.x.auth import XAuthManager


@pytest.mark.asyncio
async def test_x_api_authenticate_surfaces_invalid_token(monkeypatch):
    manager = XAuthManager(
        consumer_key="ck",
        consumer_secret="cs",
        oauth_token="ot",
        oauth_secret="os",
    )

    async def fake_client_authenticate():
        raise Exception("missing_token oauth_token is missing")

    class _FakeClient:
        async def authenticate(self):
            return await fake_client_authenticate()

    monkeypatch.setattr(manager, "_create_client", lambda: _FakeClient())

    api = XAPI("ck", "cs", "ot", "os")
    api.auth_manager = manager

    with pytest.raises(AuthenticationError) as exc_info:
        await api.authenticate()

    assert exc_info.value.details is not None
    assert exc_info.value.details.category == AuthFailureCategory.WRONG_TOKEN
    assert "agoras x authorize" in str(exc_info.value)
