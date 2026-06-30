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


import pytest

from agoras.core.auth.exceptions import AuthenticationError
from agoras.core.auth.failure import (
    AuthFailureCategory,
    AuthFailureDetails,
    classify_http_oauth_response,
    classify_oauth_error,
    format_auth_failure_message,
    raise_authentication_error_from_manager,
)


def test_format_missing_credentials_message():
    details = AuthFailureDetails(platform="youtube", category=AuthFailureCategory.MISSING)
    message = format_auth_failure_message(details)
    assert "credentials are not available" in message
    assert "agoras youtube authorize" in message
    assert "ya29." not in message


def test_format_expired_or_revoked_with_code():
    details = AuthFailureDetails(
        platform="youtube",
        category=AuthFailureCategory.EXPIRED_OR_REVOKED,
        provider_code="invalid_grant",
    )
    message = format_auth_failure_message(details)
    assert "expired or revoked" in message
    assert "(invalid_grant)" in message
    assert "FEED_URL" not in message


def test_format_wrong_token_quotes_nothing_sensitive():
    token = "rft.C1j!6464.s1"
    details = AuthFailureDetails(
        platform="tiktok",
        category=AuthFailureCategory.WRONG_TOKEN,
        provider_code="invalid_token",
    )
    message = format_auth_failure_message(details)
    assert token not in message
    assert "(invalid_token)" in message


def test_classify_invalid_grant_json():
    body = '{"error":"invalid_grant","error_description":"Token has been expired or revoked."}'
    details = classify_http_oauth_response(400, body, "youtube")
    assert details.category == AuthFailureCategory.EXPIRED_OR_REVOKED
    assert details.provider_code == "invalid_grant"


def test_classify_revocation_only_description():
    body = '{"error":"invalid_grant","error_description":"User revoked access."}'
    details = classify_http_oauth_response(400, body, "youtube")
    assert details.category == AuthFailureCategory.REVOKED


def test_classify_expired_only_description():
    body = '{"error":"invalid_grant","error_description":"Token expired."}'
    details = classify_http_oauth_response(400, body, "youtube")
    assert details.category == AuthFailureCategory.EXPIRED


def test_classify_threads_refresh_exception_format():
    exc = Exception('Token refresh failed: 400 {"error":"invalid_grant"}')
    details = classify_oauth_error(exc, "threads")
    assert details.category == AuthFailureCategory.EXPIRED_OR_REVOKED


def test_format_expired_category_message():
    details = AuthFailureDetails(platform="youtube", category=AuthFailureCategory.EXPIRED)
    message = format_auth_failure_message(details)
    assert "refresh token expired" in message
    assert "revoked" not in message


def test_classify_invalid_token_wrong_token():
    body = '{"error":"invalid_token","error_description":"Malformed token"}'
    details = classify_http_oauth_response(401, body, "tiktok")
    assert details.category == AuthFailureCategory.WRONG_TOKEN
    assert details.provider_code == "invalid_token"


def test_classify_http_exception_message():
    exc = Exception('Token refresh failed: 400 {"error":"invalid_grant"}')
    details = classify_oauth_error(exc, "youtube")
    assert details.category == AuthFailureCategory.EXPIRED_OR_REVOKED
    assert details.provider_code == "invalid_grant"


def test_classify_missing_token_from_exception_message():
    exc = Exception("missing_token oauth_token is missing")
    details = classify_oauth_error(exc, "x")
    assert details.category == AuthFailureCategory.WRONG_TOKEN


def test_classify_unknown_unrecognized_code():
    body = '{"error":"weird_provider_code"}'
    details = classify_http_oauth_response(400, body, "youtube")
    assert details.category == AuthFailureCategory.UNKNOWN
    assert details.provider_code is None


def test_authentication_error_from_details():
    details = AuthFailureDetails(
        platform="youtube",
        category=AuthFailureCategory.EXPIRED_OR_REVOKED,
        provider_code="invalid_grant",
    )
    err = AuthenticationError(details=details)
    assert "invalid_grant" in str(err)
    assert err.details == details


def test_raise_authentication_error_from_manager_missing_creds():
    class _StubManager:
        last_auth_failure = None

        def _get_platform_name(self):
            return "youtube"

        def _has_stored_or_env_credentials(self):
            return False

    with pytest.raises(AuthenticationError) as exc_info:
        raise_authentication_error_from_manager(_StubManager())

    assert exc_info.value.details is not None
    assert exc_info.value.details.category == AuthFailureCategory.MISSING
