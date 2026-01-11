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
agoras.core.auth
================

OAuth2 authentication infrastructure for Agoras.

This module provides base classes and utilities for OAuth2 authentication
across all social media platforms.
"""

from .base import BaseAuthManager
from .storage import SecureTokenStorage
from .callback_server import OAuthCallbackServer, OAuthCallbackHandler
from .exceptions import AuthenticationError

__all__ = [
    'BaseAuthManager',
    'SecureTokenStorage',
    'OAuthCallbackServer',
    'OAuthCallbackHandler',
    'AuthenticationError',
]
