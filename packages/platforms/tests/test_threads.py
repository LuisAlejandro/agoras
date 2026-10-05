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
@patch('agoras.platforms.threads.api.create_video', new_callable=MagicMock)
async def test_threads_video_rejects_local_video_path(mock_media_factory, threads_with_real_api):
    """Local video paths are rejected before download or Threads client calls."""
    threads, api = threads_with_real_api

    with pytest.raises(
        Exception,
        match='Threads API does not support local file uploads',
    ):
        await threads.video('E2E test video', '/tmp/clip.mp4', 'E2E test video')

    mock_media_factory.assert_not_called()
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
async def test_threads_execute_action_delete_reply_dispatch(threads_with_real_api):
    """Threads execute_action override dispatches 'delete-reply' to delete_reply."""
    threads, api = threads_with_real_api
    threads.config['post_id'] = 'reply-1'

    with (
        patch.object(threads, '_initialize_client', new_callable=AsyncMock),
        patch.object(threads, 'delete_reply', new_callable=AsyncMock) as mock_delete_reply,
        patch.object(threads, '_output_status'),
    ):
        await threads.execute_action('delete-reply')

    mock_delete_reply.assert_called_once_with('reply-1')


@pytest.mark.asyncio
async def test_threads_execute_action_get_post_dispatch(threads_with_real_api):
    """Threads execute_action override dispatches 'get-post' to get_post."""
    threads, api = threads_with_real_api
    threads.config['post_id'] = 'post-1'

    with (
        patch.object(threads, '_initialize_client', new_callable=AsyncMock),
        patch.object(threads, 'get_post', new_callable=AsyncMock) as mock_get_post,
    ):
        await threads.execute_action('get-post')

    mock_get_post.assert_called_once_with('post-1')


@pytest.mark.asyncio
async def test_threads_execute_action_get_reply_dispatch(threads_with_real_api):
    """Threads execute_action override dispatches 'get-reply' to get_reply."""
    threads, api = threads_with_real_api
    threads.config['post_id'] = 'reply-1'

    with (
        patch.object(threads, '_initialize_client', new_callable=AsyncMock),
        patch.object(threads, 'get_reply', new_callable=AsyncMock) as mock_get_reply,
    ):
        await threads.execute_action('get-reply')

    mock_get_reply.assert_called_once_with('reply-1')


@pytest.mark.asyncio
async def test_threads_execute_action_list_posts_dispatch(threads_with_real_api):
    """Threads execute_action override dispatches 'list-posts' to list_posts."""
    threads, api = threads_with_real_api
    threads.config['limit'] = 5

    with (
        patch.object(threads, '_initialize_client', new_callable=AsyncMock),
        patch.object(threads, 'list_posts', new_callable=AsyncMock) as mock_list_posts,
    ):
        await threads.execute_action('list-posts')

    mock_list_posts.assert_called_once_with(5)


@pytest.mark.asyncio
async def test_threads_get_post_requires_explicit_post_id(threads_with_real_api):
    """Test Threads get_post does not fall back to instance threads_post_id."""
    threads, api = threads_with_real_api
    threads.threads_post_id = 'stale-post-id'
    api.get_post = AsyncMock()

    with pytest.raises(Exception, match='Post ID is required'):
        await threads.get_post(None)

    api.get_post.assert_not_called()


@pytest.mark.asyncio
async def test_threads_get_reply_proxies_get_post(threads_with_real_api):
    """Test Threads get_reply delegates to get_post."""
    threads, _api = threads_with_real_api

    with patch.object(threads, 'get_post', new_callable=AsyncMock) as mock_get_post:
        mock_get_post.return_value = {'id': 'reply-1', 'text': 'hi'}
        result = await threads.get_reply('reply-1')

    assert result['id'] == 'reply-1'
    mock_get_post.assert_called_once_with('reply-1')


@pytest.mark.asyncio
async def test_threads_get_post_maps_video_media(threads_with_real_api):
    """Test Threads get_post maps VIDEO media type."""
    threads, api = threads_with_real_api
    api.get_post = AsyncMock(
        return_value={
            "id": "post-v",
            "text": "video post",
            "media_url": "https://example.com/v.mp4",
            "media_type": "VIDEO",
            "username": "alice",
            "timestamp": "2026-01-01T00:00:00Z",
        }
    )

    with patch.object(threads, '_output_content'):
        result = await threads.get_post('post-v')

    assert result['media'] == [{'type': 'video', 'url': 'https://example.com/v.mp4'}]


@pytest.mark.asyncio
async def test_threads_list_posts_returns_normalized_items(threads_with_real_api):
    """Test Threads list_posts emits normalized items via api.list_posts."""
    threads, api = threads_with_real_api
    api.list_posts = AsyncMock(
        return_value=[
            {
                "id": "1",
                "text": "hello",
                "media_url": "https://example.com/a.jpg",
                "media_type": "IMAGE",
                "username": "alice",
                "timestamp": "2026-01-01T00:00:00Z",
                "permalink": "https://threads.net/1",
            },
            {"id": "2", "text": "world", "media_url": None, "media_type": "TEXT", "username": "alice"},
        ]
    )

    with patch.object(threads, '_output_list') as mock_out:
        result = await threads.list_posts(2)

    assert len(result) == 2
    assert result[0]["id"] == "1"
    assert result[0]["media"] == [{"type": "image", "url": "https://example.com/a.jpg"}]
    assert result[0]["author"]["name"] == "alice"
    assert result[0]["metadata"] == {"permalink": "https://threads.net/1"}
    assert result[1]["id"] == "2"
    assert result[1]["media"] == []
    api.list_posts.assert_called_once_with(2)
    mock_out.assert_called_once()


@pytest.mark.asyncio
async def test_threads_list_posts_limit_zero_returns_empty(threads_with_real_api):
    """Test Threads list_posts with limit=0 returns an empty list without an API call."""
    threads, api = threads_with_real_api
    api.list_posts = AsyncMock()

    with patch.object(threads, '_output_list') as mock_out:
        result = await threads.list_posts(0)

    assert result == []
    api.list_posts.assert_not_called()
    mock_out.assert_called_once_with([])


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


@pytest.mark.asyncio
async def test_threads_delete_reply_proxies_delete(threads_with_real_api):
    """Threads delete_reply delegates to the api.delete path."""
    threads, api = threads_with_real_api
    api.client.delete_post = MagicMock(return_value={'id': 'reply-1'})

    with patch.object(threads, '_output_status'):
        result = await threads.delete_reply('reply-1')

    assert result == 'reply-1'
    api.client.delete_post.assert_called_once_with(post_id='reply-1')
