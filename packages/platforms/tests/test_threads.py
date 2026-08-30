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


@pytest.mark.asyncio
@patch('agoras.platforms.threads.api.ThreadsAPI.create_post')
async def test_threads_reply_text_only(mock_create_post, threads_with_real_api):
    """Threads reply with text only posts a text reply."""
    threads, api = threads_with_real_api
    mock_create_post.return_value = 'reply-1'

    with patch.object(threads, '_output_status'):
        result = await threads.reply('post-123', 'A reply')

    assert result == 'reply-1'
    mock_create_post.assert_called_once_with(
        'A reply',
        files=None,
        who_can_reply='everyone',
        reply_to_id='post-123',
    )


@pytest.mark.asyncio
@patch('agoras.platforms.threads.api.ThreadsAPI.create_post')
async def test_threads_reply_with_image(mock_create_post, threads_with_real_api):
    """Threads reply with an image posts a reply with the image."""
    threads, api = threads_with_real_api
    mock_create_post.return_value = 'reply-1'

    with patch.object(threads, '_output_status'):
        result = await threads.reply('post-123', 'A reply', status_image_url_1='http://example.com/a.jpg')

    assert result == 'reply-1'
    mock_create_post.assert_called_once_with(
        'A reply',
        files=['http://example.com/a.jpg'],
        who_can_reply='everyone',
        reply_to_id='post-123',
    )


@pytest.mark.asyncio
@patch('agoras.platforms.threads.api.ThreadsAPI.create_video_post')
async def test_threads_reply_with_video(mock_create_video_post, threads_with_real_api):
    """Threads reply with a video posts a video reply."""
    threads, api = threads_with_real_api
    mock_create_video_post.return_value = 'reply-1'

    with patch.object(threads, '_output_status'):
        result = await threads.reply('post-123', 'A reply', video_url='http://example.com/v.mp4')

    assert result == 'reply-1'
    mock_create_video_post.assert_called_once_with(
        'A reply',
        'http://example.com/v.mp4',
        who_can_reply='everyone',
        reply_to_id='post-123',
    )


@pytest.mark.asyncio
async def test_threads_reply_missing_post_id(threads_with_real_api):
    """Threads reply raises when post_id missing."""
    threads, api = threads_with_real_api

    with pytest.raises(Exception, match='Threads post ID is required for reply action'):
        await threads.reply(None, 'A reply')


@pytest.mark.asyncio
async def test_threads_reply_local_media_raises(threads_with_real_api):
    """Threads reply with a local media path raises the pull-only fast-fail error."""
    threads, api = threads_with_real_api

    with pytest.raises(Exception, match='Threads API does not support local file uploads'):
        await threads.reply('post-123', 'A reply', status_image_url_1='/tmp/local.jpg')

    api.client.create_post.assert_not_called()


@pytest.mark.asyncio
@patch('agoras.platforms.threads.api.ThreadsAPI.create_post')
async def test_threads_execute_action_reply_dispatch(mock_create_post, threads_with_real_api):
    """Threads execute_action with action='reply' dispatches to the wrapper reply."""
    threads, api = threads_with_real_api
    mock_create_post.return_value = 'reply-1'

    threads.config['post_id'] = 'post-123'
    threads.config['status_text'] = 'A reply'

    with (
        patch.object(threads, '_initialize_client', new_callable=AsyncMock),
        patch.object(threads, '_output_status'),
    ):
        await threads.execute_action('reply')

    mock_create_post.assert_called_once_with(
        'A reply',
        files=None,
        who_can_reply='everyone',
        reply_to_id='post-123',
    )


@pytest.mark.asyncio
async def test_threads_extract_reply_params_remap():
    """Threads __init__ remaps threads_post_id and threads_video_url to generic keys."""
    threads = Threads(
        threads_app_id='app_id',
        threads_app_secret='secret',
        threads_refresh_token='token',
        threads_post_id='post-123',
        threads_video_url='http://example.com/v.mp4',
        status_text='A reply',
    )

    post_id, text, media = threads._extract_reply_params()
    assert post_id == 'post-123'
    assert text == 'A reply'
    assert media['video_url'] == 'http://example.com/v.mp4'
