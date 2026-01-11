# -*- coding: utf-8 -*-
#
# Please refer to AUTHORS.rst for a complete list of Copyright holders.
# Copyright (C) 2022-2023, Agoras Developers.

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
"""
agoras.core
===========

Core interfaces, Feed, Sheet, and Base API/Auth classes for Agoras.

This package provides the foundation for all Agoras platform implementations:
- SocialNetwork interface that all platforms must implement
- BaseAPI for API client implementations
- Authentication infrastructure (OAuth2, token storage, callback server)
- Feed management for RSS feeds
- Sheet management for Google Sheets scheduling
"""

from .interfaces import SocialNetwork
from .api_base import BaseAPI
from .auth import (
    BaseAuthManager,
    SecureTokenStorage,
    OAuthCallbackServer,
    AuthenticationError,
)
from .feed import Feed, FeedItem
from .sheet import ScheduleSheet, Sheet

__all__ = [
    'SocialNetwork',
    'BaseAPI',
    'BaseAuthManager',
    'SecureTokenStorage',
    'OAuthCallbackServer',
    'AuthenticationError',
    'Feed',
    'FeedItem',
    'ScheduleSheet',
    'Sheet',
]
