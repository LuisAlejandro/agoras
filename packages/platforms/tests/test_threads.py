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

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from agoras.platforms.threads import Threads
from agoras.platforms.threads.api import ThreadsAPI


@pytest.fixture
def threads_with_real_api():
    """Threads wrapper wired to a real ThreadsAPI with mocked auth/client."""
    with patch('agoras.platforms.threads.api.ThreadsAuthManager') as mock_auth_class:
        mock_auth = MagicMock()
        mock_auth.authenticate = AsyncMock()
        mock_auth.access_token = 'token'
        mock_auth.user_id = 'user123'
        mock_auth.ensure_authenticated = MagicMock()
        mock_auth_class.return_value = mock_auth

        api = ThreadsAPI('app_id', 'app_secret', 'refresh_token')
        api._authenticated = True
        api.client = MagicMock()
        api.client.create_video_post = MagicMock(return_value={'id': 'video-999'})

        threads = Threads(
            threads_app_id='app_id',
            threads_app_secret='secret',
            threads_refresh_token='token',
        )
        threads.api = api
        yield threads, api


@pytest.mark.asyncio
@patch('agoras.platforms.threads.api.MediaFactory')
async def test_threads_video_rejects_local_video_path(mock_media_factory, threads_with_real_api):
    """Local video paths are rejected before download or Threads client calls."""
    threads, api = threads_with_real_api

    with pytest.raises(
        Exception,
        match='Threads API does not support local file uploads',
    ):
        await threads.video('E2E test video', '/tmp/clip.mp4', 'E2E test video')

    mock_media_factory.create_video.assert_not_called()
    api.client.create_video_post.assert_not_called()
