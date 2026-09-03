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
"""agoras.core.api_base module."""

import asyncio
import functools
import re
import time
from abc import ABC, abstractmethod
from typing import Any, Awaitable, Callable, Concatenate, NoReturn, ParamSpec, Protocol, TypeVar

P = ParamSpec("P")
R = TypeVar("R")


class GuardableAPI(Protocol):
    """
    Structural contract the guard decorators operate on.

    Any platform api class (BaseAPI subclass or test stub) that provides
    the guarded attributes and methods satisfies this protocol, so the
    decorators can be typed against a bound TypeVar and pyright verifies
    attribute access without runtime checks.
    """

    _authenticated: bool
    client: Any
    auth_manager: Any
    _not_authenticated_message: str
    _client_not_available_message: str

    async def authenticate(self) -> "GuardableAPI":
        """Authenticate and return self for chaining."""
        ...

    async def _rate_limit_check(self, operation_type: str = "default", min_interval: float = 1.0) -> None: ...

    def _handle_api_error(self, error, operation_name) -> NoReturn: ...


T = TypeVar("T", bound=GuardableAPI)


def guard_auth_attempt(func: Callable[Concatenate[T, P], Awaitable[R]]) -> Callable[Concatenate[T, P], Awaitable[R]]:
    """
    Guard decorator: attempt authentication when the instance is not authenticated.

    Applies the auto-auth dialect: if ``self._authenticated`` is false,
    ``self.authenticate()`` is awaited first. Guard-phase errors propagate
    unmodified (never wrapped), preserving the categorized auth error.

    The authenticate section runs under a per-instance non-reentrant
    ``asyncio.Lock``: ``authenticate()`` and ``_post_authenticate`` must
    never call a guard_auth_attempt-decorated method on the same instance,
    or the same task deadlocks.
    """

    @functools.wraps(func)
    async def wrapper(self: T, *args: P.args, **kwargs: P.kwargs) -> R:
        if not self._authenticated:
            lock = getattr(self, "_auth_lock", None)
            if lock is None:
                lock = asyncio.Lock()
                setattr(self, "_auth_lock", lock)
            async with lock:
                if not self._authenticated:
                    await self.authenticate()
        return await func(self, *args, **kwargs)

    return wrapper


def guard_assert_auth(func: Callable[Concatenate[T, P], Awaitable[R]]) -> Callable[Concatenate[T, P], Awaitable[R]]:
    """
    Guard decorator: raise the platform's not-authenticated message when unauthenticated.

    Applies the assert-or-raise dialect: if ``self._authenticated`` is false
    or ``self.client`` is missing, raise without attempting authentication.
    """

    @functools.wraps(func)
    async def wrapper(self: T, *args: P.args, **kwargs: P.kwargs) -> R:
        if not self._authenticated or not self.client:
            raise Exception(self._not_authenticated_message)
        return await func(self, *args, **kwargs)

    return wrapper


def guard_ensure_auth_manager(
    func: Callable[Concatenate[T, P], Awaitable[R]],
) -> Callable[Concatenate[T, P], Awaitable[R]]:
    """
    Guard decorator: ensure the auth manager's token is current before operations.

    Applies the auth-manager-ensure dialect: ``self.auth_manager.ensure_authenticated()``
    is invoked first. The categorized ``AuthenticationError`` it raises on
    failure propagates unmodified, never wrapped.
    """

    @functools.wraps(func)
    async def wrapper(self: T, *args: P.args, **kwargs: P.kwargs) -> R:
        self.auth_manager.ensure_authenticated()
        return await func(self, *args, **kwargs)

    return wrapper


def guard_token_presence(
    token_attr: str | None = None,
) -> Callable[[Callable[Concatenate[T, P], Awaitable[R]]], Callable[Concatenate[T, P], Awaitable[R]]]:
    """
    Guard decorator: raise the platform's not-authenticated message when no token is present.

    Applies the token-presence check used by tiktok and threads. ``token_attr``
    is the attribute path on the instance (dotted paths supported, e.g.
    ``auth_manager.access_token``), so the check reads the token source
    directly rather than through a credential forwarder.
    """
    resolved_token_attr = token_attr if token_attr is not None else "access_token"

    def resolve_token(instance: T) -> Any:
        current = instance
        for part in resolved_token_attr.split("."):
            try:
                current = getattr(current, part)
            except AttributeError:
                return None
        return current

    def decorate(func: Callable[Concatenate[T, P], Awaitable[R]]) -> Callable[Concatenate[T, P], Awaitable[R]]:
        @functools.wraps(func)
        async def wrapper(self: T, *args: P.args, **kwargs: P.kwargs) -> R:
            if not resolve_token(self):
                raise Exception(self._not_authenticated_message)
            return await func(self, *args, **kwargs)

        return wrapper

    return decorate


def guard_client_presence(func: Callable[Concatenate[T, P], Awaitable[R]]) -> Callable[Concatenate[T, P], Awaitable[R]]:
    """
    Guard decorator: raise the platform's not-available message when the client is missing.

    Applies the client-check dialect: if ``self.client`` is absent, raise
    ``self._client_not_available_message`` without attempting authentication.
    """

    @functools.wraps(func)
    async def wrapper(self: T, *args: P.args, **kwargs: P.kwargs) -> R:
        if not self.client:
            raise Exception(self._client_not_available_message)
        return await func(self, *args, **kwargs)

    return wrapper


def guard_rate_limit(
    operation_key: str,
    min_interval: float,
) -> Callable[[Callable[Concatenate[T, P], Awaitable[R]]], Callable[Concatenate[T, P], Awaitable[R]]]:
    """
    Guard decorator: wait the operation's minimum interval before the client call.

    ``operation_key`` is the literal bucket key shared by methods that throttle
    together (e.g. x ``post`` and ``reply`` share the ``"post"`` bucket).
    """

    def decorate(func: Callable[Concatenate[T, P], Awaitable[R]]) -> Callable[Concatenate[T, P], Awaitable[R]]:
        @functools.wraps(func)
        async def wrapper(self: T, *args: P.args, **kwargs: P.kwargs) -> R:
            await self._rate_limit_check(operation_key, min_interval)
            return await func(self, *args, **kwargs)

        return wrapper

    return decorate


def guard_error_wrap(
    operation_name: str,
) -> Callable[[Callable[Concatenate[T, P], Awaitable[R]]], Callable[Concatenate[T, P], Awaitable[R]]]:
    """
    Guard decorator: normalize and sanitize exceptions from the client-call segment.

    Covers only the client call — guard-phase errors (auth attempt, auth
    manager ensure, client presence) are raised before this decorator's
    scope and propagate unmodified, preserving the categorized auth error
    and the not-supported error shapes.
    """

    def decorate(func: Callable[Concatenate[T, P], Awaitable[R]]) -> Callable[Concatenate[T, P], Awaitable[R]]:
        @functools.wraps(func)
        async def wrapper(self: T, *args: P.args, **kwargs: P.kwargs) -> R:
            try:
                return await func(self, *args, **kwargs)
            except Exception as e:
                self._handle_api_error(e, operation_name)
                # Fail-safe: _handle_api_error is declared NoReturn and must
                # raise. If an override ever returns, degrade to a sanitized
                # error instead of re-raising the raw token-bearing exception.
                raise Exception(f"{operation_name} failed: {sanitize_error_text(str(e))}") from None

        return wrapper

    return decorate


_REDACT_PATTERNS = (
    (re.compile(r"Bearer\s+\S+", re.I), "Bearer [REDACTED]"),
    (re.compile(r"Bot\s+\S+", re.I), "Bot [REDACTED]"),
    (re.compile(r"bot\d+:[A-Za-z0-9_-]+", re.I), "bot[REDACTED]"),
    (re.compile(r"access_token[=:]\s*\S+", re.I), "access_token=[REDACTED]"),
    (re.compile(r"refresh_token[=:]\s*\S+", re.I), "refresh_token=[REDACTED]"),
    (re.compile(r"client_secret[=:]\s*\S+", re.I), "client_secret=[REDACTED]"),
    (re.compile(r"oauth_token[=:]\s*\S+", re.I), "oauth_token=[REDACTED]"),
    (re.compile(r"app_secret[=:]\s*\S+", re.I), "app_secret=[REDACTED]"),
    (re.compile(r"(?<![a-z0-9])token\s*[=:]\s*\S+", re.I), "token=[REDACTED]"),
    (re.compile(r"key=AIza[0-9A-Za-z_-]{20,}", re.I), "key=[REDACTED]"),
    (re.compile(r"X-API-Key:\s*\S+", re.I), "X-API-Key: [REDACTED]"),
    (re.compile(r"(?<![A-Za-z0-9_-])api[_-]?key[=:]\s*\S+", re.I), "api_key=[REDACTED]"),
    (re.compile(r"Basic\s+[A-Za-z0-9+/=]{8,}", re.I), "Basic [REDACTED]"),
    (re.compile(r"Authorization:\s*(?:Basic\s+[A-Za-z0-9+/=]+|\S+)", re.I), "Authorization: [REDACTED]"),
    (
        re.compile(
            r"[?&](?:X-Amz-Signature|Signature|sig|AWSAccessKeyId|X-Goog-Signature|GoogleAccessId|Policy|X-Amz-Credential|Expires)=[^&\s]+",
            re.I,
        ),
        "[REDACTED]",
    ),
    (
        re.compile(
            r"(?:X-Amz-Signature|Signature|sig|AWSAccessKeyId|X-Goog-Signature|GoogleAccessId|Policy|X-Amz-Credential|Expires)[\s'\"]*[=:][\s'\"]*[\"'][^\"']*[\"']",
            re.I,
        ),
        "[REDACTED]",
    ),
)


def sanitize_error_text(text: str) -> str:
    """
    Redact credential-bearing shapes from error text.

    Single source of truth for the redaction patterns; used by
    ``BaseAPI._handle_api_error`` and by the wrapper re-chain sites.
    """
    sanitized = text
    for pattern, replacement in _REDACT_PATTERNS:
        sanitized = pattern.sub(replacement, sanitized)
    return sanitized


class BaseAPI(ABC):
    """
    Abstract base class for social network API implementations.

    Provides common functionality and patterns for API interactions
    including authentication, rate limiting, and error handling.
    """

    @classmethod
    def _sanitize_error_message(cls, message: str) -> str:
        """Redact credential shapes from error text (delegates to the module sanitizer)."""
        return sanitize_error_text(message)

    def __init__(self, **credentials):
        """
        Initialize API instance with credentials.

        Args:
            **credentials: API-specific authentication credentials
        """
        self.credentials = credentials
        self.client: Any = None
        self.auth_manager: Any = None
        self._authenticated = False
        self._rate_limit_cache = {}
        self._last_request_time = 0

    async def authenticate(self):
        """
        Complete the shared authentication lifecycle.

        Runs the platform-specific post-authentication steps
        (``_post_authenticate``), wires the auth manager's client, and marks
        the instance authenticated. Subclasses run the auth-manager attempt
        and raise the categorized ``AuthenticationError`` on failure in their
        override of this method, then delegate the shared tail here via
        ``super().authenticate()``.

        Returns:
            BaseAPI: Self for method chaining

        Raises:
            Exception: If authentication fails
        """
        await self._post_authenticate()
        self.client = self.auth_manager.client
        self._authenticated = True
        return self

    async def _post_authenticate(self):
        """
        Hook for platform-specific post-authentication steps.

        Called by ``authenticate`` after the auth-manager attempt succeeds and
        before the client is wired. The default does nothing; platforms with
        extra post-auth checks (e.g. discord, telegram) override this.
        """

    async def disconnect(self):
        """
        Disconnect from the API and clean up resources.

        Acquires the auth lock when one exists so a disconnect cannot
        interleave with an in-flight ``authenticate()`` and leave the
        instance half-authenticated (flag set with a torn-down client).
        Like the guard, ``disconnect`` must not be called from inside
        ``authenticate()`` or ``_post_authenticate`` on the same instance.
        """
        lock = getattr(self, "_auth_lock", None)
        if lock is None:
            return await self._disconnect_locked()
        async with lock:
            return await self._disconnect_locked()

    async def _disconnect_locked(self):
        """Run the disconnect hook and reset auth state; caller holds the lock."""
        try:
            self._disconnect_hook()
        finally:
            self.client = None
            self._authenticated = False

    def _disconnect_hook(self):
        """
        Hook for platform-specific disconnect teardown.

        The default disconnects the client and clears the auth manager's
        access token. Platforms that must not disconnect the client (tiktok,
        telegram, threads) or clear different auth-manager state override
        this.
        """
        if self.client:
            self.client.disconnect()
        if self.auth_manager:
            self.auth_manager.access_token = None

    async def _rate_limit_check(self, operation_type="default", min_interval=1.0):
        """
        Perform rate limiting check before API operations.

        Args:
            operation_type (str): Type of operation for specific limits
            min_interval (float): Minimum interval between requests in seconds
        """
        current_time = time.time()
        last_time = self._rate_limit_cache.get(operation_type, 0)

        # Reserve the next slot before sleeping so concurrent callers claim
        # successive windows instead of firing at the same boundary.
        next_slot = max(current_time, last_time + min_interval)
        self._rate_limit_cache[operation_type] = next_slot

        if next_slot - current_time > 0:
            try:
                await asyncio.sleep(next_slot - current_time)
            except asyncio.CancelledError:
                if self._rate_limit_cache.get(operation_type) == next_slot:
                    self._rate_limit_cache[operation_type] = last_time
                raise

    # Guard message templates, overridden per platform. Read by the guard
    # decorators so the not-authenticated and not-available messages stay
    # platform-specific without repeating the guard shape.
    _not_authenticated_message = "API not authenticated"
    _client_not_available_message = "API client not available"

    def _handle_api_error(self, error, operation_name) -> NoReturn:
        """
        Handle API errors with consistent error messages.

        Args:
            error: The exception that occurred
            operation_name (str): Name of the operation that failed

        Raises:
            Exception: Formatted exception with context
        """
        error_msg = f"{operation_name} failed: {sanitize_error_text(str(error))}"
        exc = Exception(error_msg)
        exc.__suppress_context__ = True
        raise exc from None

    @abstractmethod
    async def post(self, *args, **kwargs):
        """
        Create a post on the social media platform.

        Returns:
            str: Post ID

        Raises:
            Exception: If posting fails
        """

    @abstractmethod
    async def like(self, post_id, *args, **kwargs):
        """
        Like/react to a post on the social media platform.

        Args:
            post_id (str): ID of the post to like

        Returns:
            str: Post ID

        Raises:
            Exception: If liking fails or not supported
        """

    @abstractmethod
    async def delete(self, post_id, *args, **kwargs):
        """
        Delete a post from the social media platform.

        Args:
            post_id (str): ID of the post to delete

        Returns:
            str: Post ID

        Raises:
            Exception: If deletion fails or not supported
        """

    @abstractmethod
    async def share(self, post_id, *args, **kwargs):
        """
        Share/repost a post on the social media platform.

        Args:
            post_id (str): ID of the post to share

        Returns:
            str: Share/Post ID

        Raises:
            Exception: If sharing fails or not supported
        """
