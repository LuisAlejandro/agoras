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

"""
Pytest configuration and global test fixtures.

This module provides global test configuration and HTTP call blocking
for unit tests to prevent accidental real network requests.
"""

from unittest.mock import patch

import pytest


@pytest.fixture(autouse=True)
def block_http_requests(request):
    """
    Global fixture that blocks HTTP requests during unit tests.

    This fixture patches urllib.request.urlopen and requests.Session.request
    to prevent real network calls during unit testing. Tests that need to make
    real HTTP calls should be marked with @pytest.mark.integration and handle
    their own mocking or use real network calls appropriately.

    The fixture is automatically applied to all tests except those marked
    with @pytest.mark.integration.
    """
    # Skip blocking for integration tests
    if request.node.get_closest_marker('integration'):
        yield
        return

    # Block urllib requests
    with patch('urllib.request.urlopen') as mock_urlopen:
        mock_urlopen.side_effect = RuntimeError(
            "Real HTTP call blocked! Use @pytest.mark.integration for tests that need real network access, "
            "or mock the HTTP call in your test."
        )

        # Block requests library HTTP calls
        with patch('requests.Session.request') as mock_request:
            mock_request.side_effect = RuntimeError(
                "Real HTTP call blocked! Use @pytest.mark.integration for tests that need real network access, "
                "or mock the HTTP call in your test."
            )

            yield


# Custom markers
def pytest_configure(config):
    """Configure custom pytest markers."""
    config.addinivalue_line(
        "markers",
        "integration: marks tests that make real HTTP/network calls (deselect with '-m \"not integration\"')"
    )
    config.addinivalue_line(
        "markers",
        "unit: marks tests as pure unit tests that should not make network calls"
    )
