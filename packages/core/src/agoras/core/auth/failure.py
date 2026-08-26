# -*- coding: utf-8 -*-
#
# Please refer to AUTHORS.md for a complete list of Copyright holders.
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
"""Auth failure taxonomy and OAuth error classification."""

from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass
from enum import Enum
from typing import TYPE_CHECKING, Any, Optional

if TYPE_CHECKING:
    from .base import BaseAuthManager

ALLOWLISTED_PROVIDER_CODES = frozenset(
    {
        "invalid_grant",
        "invalid_token",
        "invalid_client",
        "unauthorized_client",
        "access_denied",
        "invalid_request",
        "unsupported_grant_type",
        "expired_token",
        "token_expired",
    }
)

_REVOCATION_ONLY_RE = re.compile(r"\brevok", re.IGNORECASE)
_EXPIRED_OR_REVOKED_RE = re.compile(r"expired\s+or\s+revoked", re.IGNORECASE)
_HTTP_REFRESH_RE = re.compile(
    r"(?:Token refresh failed|OAuth).*?(?P<status>\d{3})\s*(?P<body>.*)$",
    re.IGNORECASE | re.DOTALL,
)


class AuthFailureCategory(str, Enum):
    """Normalized auth failure categories for operator-facing messages."""

    MISSING = "missing"
    EXPIRED = "expired"
    REVOKED = "revoked"
    EXPIRED_OR_REVOKED = "expired_or_revoked"
    WRONG_TOKEN = "wrong_token"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class AuthFailureDetails:
    """Structured auth failure for message formatting."""

    platform: str
    category: AuthFailureCategory
    provider_code: Optional[str] = None


def _sanitize_provider_code(code: Optional[str]) -> Optional[str]:
    if not code:
        return None
    normalized = code.strip().lower()
    if normalized in ALLOWLISTED_PROVIDER_CODES:
        return normalized
    return None


def _category_phrase(category: AuthFailureCategory) -> str:
    phrases = {
        AuthFailureCategory.MISSING: "credentials are not available",
        AuthFailureCategory.EXPIRED: "refresh token expired",
        AuthFailureCategory.REVOKED: "refresh token was revoked",
        AuthFailureCategory.EXPIRED_OR_REVOKED: "refresh token expired or revoked",
        AuthFailureCategory.WRONG_TOKEN: "token is invalid",
        AuthFailureCategory.UNKNOWN: "authentication failed",
    }
    return phrases[category]


def format_auth_failure_message(details: AuthFailureDetails) -> str:
    """Format a user-facing auth failure message (no token values)."""
    platform = details.platform
    phrase = _category_phrase(details.category)
    code = _sanitize_provider_code(details.provider_code)
    code_suffix = f" ({code})" if code else ""
    return (
        f"{platform.capitalize()} authentication failed: {phrase}{code_suffix}. "
        f"Run 'agoras {platform} authorize' first."
    )


def _parse_oauth_json(body: str) -> dict[str, Any]:
    body = body.strip()
    if not body:
        return {}
    try:
        payload = json.loads(body)
    except json.JSONDecodeError:
        return {}
    if isinstance(payload, dict):
        return payload
    return {}


def _category_from_oauth_payload(payload: dict[str, Any]) -> AuthFailureCategory:
    error = str(payload.get("error", "")).lower()
    description = str(payload.get("error_description", ""))

    if error == "invalid_grant":
        if _EXPIRED_OR_REVOKED_RE.search(description):
            return AuthFailureCategory.EXPIRED_OR_REVOKED
        if _REVOCATION_ONLY_RE.search(description) and "expired" not in description.lower():
            return AuthFailureCategory.REVOKED
        if "expired" in description.lower() and not _REVOCATION_ONLY_RE.search(description):
            return AuthFailureCategory.EXPIRED
        return AuthFailureCategory.EXPIRED_OR_REVOKED

    if error in {"invalid_token", "expired_token", "token_expired"}:
        return AuthFailureCategory.WRONG_TOKEN

    if error in {"invalid_client", "unauthorized_client", "access_denied"}:
        return AuthFailureCategory.WRONG_TOKEN

    return AuthFailureCategory.UNKNOWN


def classify_http_oauth_response(
    status: int,
    body: str,
    platform: str,
) -> AuthFailureDetails:
    """Classify an OAuth HTTP error response body."""
    payload = _parse_oauth_json(body)
    if payload:
        category = _category_from_oauth_payload(payload)
        code = _sanitize_provider_code(str(payload.get("error", "")))
        return AuthFailureDetails(platform=platform, category=category, provider_code=code)

    if status in {401, 403}:
        return AuthFailureDetails(platform=platform, category=AuthFailureCategory.WRONG_TOKEN)

    return AuthFailureDetails(platform=platform, category=AuthFailureCategory.UNKNOWN)


def classify_oauth_error(exc: Exception, platform: str) -> AuthFailureDetails:
    """Classify an OAuth-related exception (HTTP text or Authlib wrapper)."""
    message = str(exc)
    match = _HTTP_REFRESH_RE.search(message)
    if match:
        status = int(match.group("status"))
        body = match.group("body").strip()
        return classify_http_oauth_response(status, body, platform)

    payload = _parse_oauth_json(message)
    if payload:
        category = _category_from_oauth_payload(payload)
        code = _sanitize_provider_code(str(payload.get("error", "")))
        return AuthFailureDetails(platform=platform, category=category, provider_code=code)

    lowered = message.lower()
    if "invalid_grant" in lowered:
        return AuthFailureDetails(
            platform=platform,
            category=AuthFailureCategory.EXPIRED_OR_REVOKED,
            provider_code="invalid_grant",
        )
    if "invalid_token" in lowered:
        return AuthFailureDetails(
            platform=platform,
            category=AuthFailureCategory.WRONG_TOKEN,
            provider_code="invalid_token",
        )
    if "missing_token" in lowered or "oauth_token is missing" in lowered:
        return AuthFailureDetails(
            platform=platform,
            category=AuthFailureCategory.WRONG_TOKEN,
        )

    return AuthFailureDetails(platform=platform, category=AuthFailureCategory.UNKNOWN)


def record_auth_failure(auth_manager: BaseAuthManager, exc: Exception) -> bool:
    """Set last_auth_failure from an exception and signal authenticate() failure."""
    platform = auth_manager._get_platform_name()
    auth_manager.last_auth_failure = classify_oauth_error(exc, platform)
    return False


def raise_authentication_error_from_manager(auth_manager: BaseAuthManager) -> None:
    """Raise AuthenticationError using the manager's last failure or missing creds."""
    from .exceptions import AuthenticationError

    platform = auth_manager._get_platform_name()
    failure = auth_manager.last_auth_failure
    if failure is not None:
        raise AuthenticationError(details=failure)

    if not auth_manager._has_stored_or_env_credentials():
        raise AuthenticationError(details=AuthFailureDetails(platform=platform, category=AuthFailureCategory.MISSING))

    raise AuthenticationError(details=AuthFailureDetails(platform=platform, category=AuthFailureCategory.UNKNOWN))


def env_has_refresh_token(platform: str) -> bool:
    """Return True when the platform refresh-token env var is set."""
    return bool(os.environ.get(f"{platform.upper()}_REFRESH_TOKEN"))
