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
"""Pins the facebook wrapper split guards (api vs object-id branches).

The historical compound guard raised "Facebook API not initialized" when
either api or object id was missing; the split now raises "Facebook object
ID is required." when the api is present but the object id is missing.
This is the accepted, documented message improvement from the hoist.
"""

import pytest
from unittest.mock import MagicMock

from agoras.platforms.facebook.wrapper import Facebook


def _facebook():
    fb = Facebook()
    fb.api = MagicMock()
    fb.facebook_object_id = None
    return fb


@pytest.mark.asyncio
async def test_page_local_images_requires_object_id():
    fb = _facebook()
    with pytest.raises(Exception, match="Facebook object ID is required."):
        await fb._post_page_local_images_only([], "status")


@pytest.mark.asyncio
async def test_page_mixed_images_requires_object_id():
    fb = _facebook()
    with pytest.raises(Exception, match="Facebook object ID is required."):
        await fb._post_page_mixed_images([], [], "status", "link")


@pytest.mark.asyncio
async def test_profile_images_requires_object_id():
    fb = _facebook()
    with pytest.raises(Exception, match="Facebook object ID is required."):
        await fb._post_profile_images([], "status", "link")


@pytest.mark.asyncio
async def test_helpers_raise_not_initialized_when_api_missing():
    fb = Facebook()
    fb.api = None
    with pytest.raises(Exception, match="Facebook API not initialized"):
        await fb._post_page_local_images_only([], "status")
    with pytest.raises(Exception, match="Facebook API not initialized"):
        await fb._post_page_mixed_images([], [], "status", "link")
    with pytest.raises(Exception, match="Facebook API not initialized"):
        await fb._post_profile_images([], "status", "link")