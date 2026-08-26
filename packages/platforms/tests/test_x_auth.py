# -*- coding: utf-8 -*-
#
# Please refer to AUTHORS.rst for a complete list of Copyright holders.
# Copyright (C) 2022-2026, Agoras Developers.

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from agoras.core.auth.exceptions import AuthenticationError
from agoras.core.auth.failure import AuthFailureCategory
from agoras.platforms.x.api import XAPI
from agoras.platforms.x.auth import XAuthManager
from agoras.platforms.x.wrapper import X


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


@pytest.mark.asyncio
async def test_refresh_subscription_keeps_prior_on_fetch_failure(monkeypatch):
    manager = XAuthManager(
        consumer_key="ck",
        consumer_secret="cs",
        oauth_token="ot",
        oauth_secret="os",
    )
    manager.subscription_type = "Premium"

    class _FailingClient:
        async def authenticate(self):
            return None

        async def get_subscription_type(self):
            raise Exception("network down")

        def disconnect(self):
            return None

    monkeypatch.setattr(manager, "_create_client", lambda: _FailingClient())
    await manager._refresh_and_store_subscription_type()
    assert manager.subscription_type == "Premium"


@pytest.mark.asyncio
async def test_refresh_subscription_none_when_no_prior(monkeypatch):
    manager = XAuthManager(
        consumer_key="ck",
        consumer_secret="cs",
        oauth_token="ot",
        oauth_secret="os",
    )
    manager.subscription_type = None
    monkeypatch.setattr(manager, "load_subscription_type_from_storage", lambda: None)

    class _FailingClient:
        async def authenticate(self):
            return None

        async def get_subscription_type(self):
            raise Exception("network down")

        def disconnect(self):
            return None

    monkeypatch.setattr(manager, "_create_client", lambda: _FailingClient())
    await manager._refresh_and_store_subscription_type()
    assert manager.subscription_type is None


@pytest.mark.asyncio
async def test_authorize_message_warns_when_subscription_none(monkeypatch):
    manager = XAuthManager(
        consumer_key="ck",
        consumer_secret="cs",
        oauth_token="ot",
        oauth_secret="os",
    )

    async def fake_refresh():
        manager.subscription_type = None

    monkeypatch.setattr(manager, "_refresh_and_store_subscription_type", fake_refresh)
    monkeypatch.setattr(manager, "_save_credentials_to_storage", lambda: None)
    monkeypatch.setattr(manager, "_validate_basic_credentials", lambda: True)

    msg = await manager.authorize()
    assert "Authorization successful" in msg
    assert "Premium subscription was not detected" in msg
    assert "280" in msg


@pytest.mark.asyncio
async def test_authorize_save_includes_subscription_type(monkeypatch):
    manager = XAuthManager(
        consumer_key="ck",
        consumer_secret="cs",
        oauth_token="ot",
        oauth_secret="os",
    )
    saved = {}

    async def fake_refresh():
        manager.subscription_type = "Premium"

    def fake_save():
        saved["subscription_type"] = manager.subscription_type
        saved["oauth_token"] = manager.oauth_token

    monkeypatch.setattr(manager, "_refresh_and_store_subscription_type", fake_refresh)
    monkeypatch.setattr(manager, "_save_credentials_to_storage", fake_save)
    monkeypatch.setattr(manager, "_validate_basic_credentials", lambda: True)

    msg = await manager.authorize()
    assert "Premium subscription was not detected" not in msg
    assert saved["subscription_type"] == "Premium"
    assert saved["oauth_token"] == "ot"


def test_load_subscription_type_bound_to_active_oauth(monkeypatch):
    manager = XAuthManager(
        consumer_key="ck",
        consumer_secret="cs",
        oauth_token="active-ot",
        oauth_secret="active-os",
    )

    class _Storage:
        def load_token(self, platform, identifier):
            if identifier == "default":
                return {
                    "oauth_token": "other-ot",
                    "oauth_secret": "other-os",
                    "subscription_type": "Premium",
                }
            return {
                "oauth_token": "active-ot",
                "oauth_secret": "active-os",
                "subscription_type": "Basic",
            }

    manager.token_storage = _Storage()
    monkeypatch.setattr(manager, "_get_token_identifier", lambda: "id1")
    assert manager.load_subscription_type_for_active_oauth() == "Basic"


def test_load_subscription_type_mismatch_fail_closed(monkeypatch):
    manager = XAuthManager(
        consumer_key="ck",
        consumer_secret="cs",
        oauth_token="active-ot",
        oauth_secret="active-os",
    )

    class _Storage:
        def load_token(self, platform, identifier):
            return {
                "oauth_token": "other-ot",
                "oauth_secret": "other-os",
                "subscription_type": "Premium",
            }

        def list_tokens(self, platform):
            return [("x", "unrelated")]

    manager.token_storage = _Storage()
    monkeypatch.setattr(manager, "_get_token_identifier", lambda: "id1")
    assert manager.load_subscription_type_for_active_oauth() is None


def test_wrapper_load_subscription_ignores_unrelated_tokens(monkeypatch):
    x = X()
    x.twitter_consumer_key = "ck"
    x.twitter_consumer_secret = "cs"
    x.twitter_oauth_token = "ot"
    x.twitter_oauth_secret = "os"

    class _Storage:
        def load_token(self, platform, identifier):
            return {
                "oauth_token": "other",
                "oauth_secret": "other-sec",
                "subscription_type": "Premium",
            }

        def list_tokens(self, platform):
            return [("x", "default")]

    def fake_init(self, **kwargs):
        self.consumer_key = kwargs.get("consumer_key")
        self.consumer_secret = kwargs.get("consumer_secret")
        self.oauth_token = kwargs.get("oauth_token")
        self.oauth_secret = kwargs.get("oauth_secret")
        self.subscription_type = None
        self.token_storage = _Storage()

    monkeypatch.setattr("agoras.platforms.x.auth.XAuthManager.__init__", fake_init)
    monkeypatch.setattr(
        "agoras.platforms.x.auth.XAuthManager._get_token_identifier",
        lambda self: "id1",
    )
    assert x._load_subscription_type() is None
