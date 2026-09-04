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
"""Shared auth-manager fakes for guard and seam tests.

Single source for the stub auth managers used across the platform guard
test files, so guard-behavior assertions stay consistent.
"""

from agoras.core.auth.exceptions import AuthenticationError


class FailingAuthManager:
    """Auth manager whose ensure_authenticated raises the categorized error."""

    access_token = None
    user_info = None
    client = None

    def __init__(self, message="token expired"):
        self._message = message

    def ensure_authenticated(self):
        raise AuthenticationError(self._message)


class CountingOkAuthManager:
    """Auth manager whose ensure_authenticated succeeds, counting calls."""

    access_token = "valid-token"
    user_info = None
    client = None

    def __init__(self):
        self.ensure_calls = 0

    def ensure_authenticated(self):
        self.ensure_calls += 1
