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

import os
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from agoras.core.interfaces import SocialNetwork


# Concrete implementation for testing
class TestSocialNetwork(SocialNetwork):
    """Concrete implementation of SocialNetwork for testing purposes."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.posts_created = []

    async def _initialize_client(self):
        """Initialize client implementation."""
        self.client = "test_client"

    async def disconnect(self):
        """Disconnect implementation."""
        self.client = None

    async def post(self, status_text, status_link,
                   status_image_url_1=None, status_image_url_2=None,
                   status_image_url_3=None, status_image_url_4=None):
        """Post implementation."""
        post_id = f"post-{len(self.posts_created)}"
        self.posts_created.append({
            'text': status_text, 'link': status_link,
            'images': [status_image_url_1, status_image_url_2,
                       status_image_url_3, status_image_url_4]
        })
        return post_id

    async def like(self, post_id):
        """Like implementation."""
        return post_id

    async def delete(self, post_id):
        """Delete implementation."""
        return post_id

    async def share(self, post_id):
        """Share implementation."""
        return post_id


class TestSocialNetworkWithSuffix(SocialNetwork):
    """Test class with 'Network' suffix for platform name testing."""

    async def _initialize_client(self):
        self.client = "test"

    async def disconnect(self):
        pass

    async def post(self, *args, **kwargs):
        return "post-1"

    async def like(self, post_id):
        return post_id

    async def delete(self, post_id):
        return post_id

    async def share(self, post_id):
        return post_id


def test_socialnetwork_is_abstract():
    """Test that SocialNetwork cannot be instantiated directly."""
    with pytest.raises(TypeError):
        SocialNetwork()


def test_socialnetwork_required_methods():
    """Test that SocialNetwork defines required abstract methods."""
    assert hasattr(SocialNetwork, '_initialize_client')
    assert hasattr(SocialNetwork, 'disconnect')
    assert hasattr(SocialNetwork, 'post')
    assert hasattr(SocialNetwork, 'like')
    assert hasattr(SocialNetwork, 'delete')
    assert hasattr(SocialNetwork, 'share')


def test_socialnetwork_execute_action_exists():
    """Test that execute_action method exists."""
    assert hasattr(SocialNetwork, 'execute_action')
    assert callable(getattr(SocialNetwork, 'execute_action'))


def test_socialnetwork_media_methods():
    """Test that media helper methods exist."""
    assert hasattr(SocialNetwork, 'download_images')
    assert hasattr(SocialNetwork, 'download_video')
    assert hasattr(SocialNetwork, 'download_feed')


# Helper Method Tests

def test_get_platform_name_without_suffix():
    """Test get_platform_name with class name without 'Network' suffix."""
    network = TestSocialNetwork()

    platform_name = network.get_platform_name()

    # 'TestSocialNetwork' ends with 'Network' so last 7 chars removed -> 'TestSocial'
    assert platform_name == 'TestSocial'


def test_get_platform_name_with_suffix():
    """Test get_platform_name removes 'Network' suffix."""
    network = TestSocialNetworkWithSuffix()

    platform_name = network.get_platform_name()

    assert platform_name == 'TestSocialNetworkWithSuffix'


@pytest.mark.asyncio
async def test_video_method_default_raises_exception():
    """Test video method raises not supported exception by default."""
    network = TestSocialNetwork()

    with pytest.raises(Exception, match='Video posting not supported'):
        await network.video('Text', 'http://video.mp4', 'Title')


def test_get_config_value_from_config():
    """Test _get_config_value retrieves from config dict."""
    network = TestSocialNetwork(api_key='config_key', secret='config_secret')

    value = network._get_config_value('api_key')

    assert value == 'config_key'


@patch.dict(os.environ, {'API_KEY': 'env_key'})
def test_get_config_value_from_environment():
    """Test _get_config_value retrieves from environment variable."""
    network = TestSocialNetwork()

    value = network._get_config_value('api_key', 'API_KEY')

    assert value == 'env_key'


@patch.dict(os.environ, {'API_KEY': 'env_key'})
def test_get_config_value_config_overrides_env():
    """Test _get_config_value prefers config over environment."""
    network = TestSocialNetwork(api_key='config_key')

    value = network._get_config_value('api_key', 'API_KEY')

    assert value == 'config_key'


def test_get_config_value_returns_none_when_missing():
    """Test _get_config_value returns None when value not found."""
    network = TestSocialNetwork()

    value = network._get_config_value('missing_key')

    assert value is None


@patch('builtins.print')
def test_output_status(mock_print):
    """Test _output_status prints JSON formatted status."""
    network = TestSocialNetwork()

    network._output_status('post-123')

    mock_print.assert_called_once()
    output = mock_print.call_args[0][0]
    assert '"id":"post-123"' in output or '"id": "post-123"' in output


# Media Method Tests

@pytest.mark.asyncio
@patch('agoras.core.interfaces.MediaFactory.download_images')
async def test_download_images(mock_download):
    """Test download_images calls MediaFactory."""
    mock_download.return_value = AsyncMock()
    network = TestSocialNetwork()

    image_urls = ['url1.jpg', 'url2.jpg']
    await network.download_images(image_urls)

    mock_download.assert_called_once_with(image_urls)


@pytest.mark.asyncio
@patch('agoras.core.interfaces.MediaFactory.create_video')
async def test_download_video(mock_create_video):
    """Test download_video creates and downloads video with platform name."""
    mock_video = MagicMock()
    mock_video.download = AsyncMock()
    mock_create_video.return_value = mock_video

    network = TestSocialNetwork()

    result = await network.download_video('http://video.mp4')

    # TestSocialNetwork -> TestSocial (Network suffix removed)
    mock_create_video.assert_called_once_with('http://video.mp4', 'TestSocial')
    mock_video.download.assert_called_once()


@pytest.mark.asyncio
@patch('agoras.core.interfaces.Feed')
async def test_download_feed(mock_feed_class):
    """Test download_feed creates and downloads feed."""
    mock_feed = MagicMock()
    mock_feed.download = AsyncMock()
    mock_feed_class.return_value = mock_feed

    network = TestSocialNetwork()

    result = await network.download_feed('http://feed.rss')

    mock_feed_class.assert_called_once_with('http://feed.rss')
    mock_feed.download.assert_called_once()
    assert result is mock_feed


@pytest.mark.asyncio
@patch('agoras.core.interfaces.ScheduleSheet')
async def test_create_schedule_sheet(mock_sheet_class):
    """Test create_schedule_sheet with proper configuration."""
    mock_sheet = MagicMock()
    mock_sheet.authenticate = AsyncMock()
    mock_sheet.get_worksheet = AsyncMock()
    mock_sheet_class.return_value = mock_sheet

    network = TestSocialNetwork()

    result = await network.create_schedule_sheet(
        'sheet-id', 'Sheet1',
        'email@example.com', 'private-key'
    )

    mock_sheet_class.assert_called_once_with(
        'sheet-id', 'email@example.com', 'private-key', 'Sheet1'
    )
    mock_sheet.authenticate.assert_called_once()
    mock_sheet.get_worksheet.assert_called_once()


@pytest.mark.asyncio
@patch('agoras.core.interfaces.ScheduleSheet')
async def test_create_schedule_sheet_replaces_newlines(mock_sheet_class):
    """Test create_schedule_sheet replaces \\n with actual newlines."""
    mock_sheet = MagicMock()
    mock_sheet.authenticate = AsyncMock()
    mock_sheet.get_worksheet = AsyncMock()
    mock_sheet_class.return_value = mock_sheet

    network = TestSocialNetwork()

    await network.create_schedule_sheet(
        'sheet-id', 'Sheet1',
        'email@example.com', 'line1\\nline2\\nline3'
    )

    # Check that private key had \\n replaced with \n
    call_args = mock_sheet_class.call_args[0]
    assert '\n' in call_args[2]
    assert '\\n' not in call_args[2]


# Execute Action Router Tests

@pytest.mark.asyncio
async def test_execute_action_empty_raises_exception():
    """Test execute_action with empty action raises exception."""
    network = TestSocialNetwork()

    with pytest.raises(Exception, match='Action is a required argument'):
        await network.execute_action('')


@pytest.mark.asyncio
async def test_execute_action_unknown_raises_exception():
    """Test execute_action with unknown action raises exception."""
    network = TestSocialNetwork()

    with pytest.raises(Exception, match='action not supported'):
        await network.execute_action('unknown_action')


@pytest.mark.asyncio
async def test_execute_action_initializes_client():
    """Test execute_action initializes client before action."""
    network = TestSocialNetwork(status_text='Test', status_link='')

    assert network.client is None

    await network.execute_action('post')

    assert network.client == 'test_client'


@pytest.mark.asyncio
async def test_execute_action_post():
    """Test execute_action routes 'post' action correctly."""
    network = TestSocialNetwork(
        status_text='Test post',
        status_link='http://link.com',
        status_image_url_1='img1.jpg'
    )

    await network.execute_action('post')

    assert len(network.posts_created) == 1
    assert network.posts_created[0]['text'] == 'Test post'


@pytest.mark.asyncio
async def test_execute_action_like():
    """Test execute_action routes 'like' action correctly."""
    network = TestSocialNetwork(post_id='post-123')

    with patch.object(network, 'like', new_callable=AsyncMock) as mock_like:
        await network.execute_action('like')
        mock_like.assert_called_once_with('post-123')


@pytest.mark.asyncio
async def test_execute_action_share():
    """Test execute_action routes 'share' action correctly."""
    network = TestSocialNetwork(post_id='post-456')

    with patch.object(network, 'share', new_callable=AsyncMock) as mock_share:
        await network.execute_action('share')
        mock_share.assert_called_once_with('post-456')


@pytest.mark.asyncio
async def test_execute_action_delete():
    """Test execute_action routes 'delete' action correctly."""
    network = TestSocialNetwork(post_id='post-789')

    with patch.object(network, 'delete', new_callable=AsyncMock) as mock_delete:
        await network.execute_action('delete')
        mock_delete.assert_called_once_with('post-789')


@pytest.mark.asyncio
async def test_execute_action_video():
    """Test execute_action routes 'video' action correctly."""
    network = TestSocialNetwork(
        status_text='Video post',
        video_url='http://video.mp4',
        video_title='My Video'
    )

    with patch.object(network, 'video', new_callable=AsyncMock) as mock_video:
        await network.execute_action('video')
        mock_video.assert_called_once_with('Video post', 'http://video.mp4', 'My Video')


@pytest.mark.asyncio
@patch('agoras.core.interfaces.Feed')
async def test_execute_action_last_from_feed(mock_feed_class):
    """Test execute_action routes 'last-from-feed' action correctly."""
    mock_feed = MagicMock()
    mock_feed.download = AsyncMock()
    mock_feed.get_items_since = MagicMock(return_value=[])
    mock_feed_class.return_value = mock_feed

    network = TestSocialNetwork(feed_url='http://feed.rss')

    await network.execute_action('last-from-feed')

    mock_feed_class.assert_called_once()


@pytest.mark.asyncio
@patch('agoras.core.interfaces.Feed')
async def test_execute_action_random_from_feed(mock_feed_class):
    """Test execute_action routes 'random-from-feed' action correctly."""
    mock_feed = MagicMock()
    mock_feed.download = AsyncMock()
    mock_item = MagicMock()
    mock_item.link = 'http://item.com'
    mock_item.title = 'Item Title'
    mock_item.image_url = 'img.jpg'
    mock_item.get_timestamped_link = MagicMock(return_value='http://item.com?t=123')
    mock_feed.get_random_item = MagicMock(return_value=mock_item)
    mock_feed_class.return_value = mock_feed

    network = TestSocialNetwork(feed_url='http://feed.rss')

    await network.execute_action('random-from-feed')

    assert len(network.posts_created) == 1


@pytest.mark.asyncio
@patch('agoras.core.interfaces.ScheduleSheet')
async def test_execute_action_schedule(mock_sheet_class):
    """Test execute_action routes 'schedule' action correctly."""
    mock_sheet = MagicMock()
    mock_sheet.authenticate = AsyncMock()
    mock_sheet.get_worksheet = AsyncMock()
    mock_sheet.process_scheduled_posts = AsyncMock(return_value=[])
    mock_sheet_class.return_value = mock_sheet

    network = TestSocialNetwork(
        google_sheets_id='sheet-id',
        google_sheets_name='Sheet1',
        google_sheets_client_email='email@example.com',
        google_sheets_private_key='key'
    )

    await network.execute_action('schedule')

    mock_sheet.authenticate.assert_called_once()


# Action Handler Tests

@pytest.mark.asyncio
async def test_handle_post_action():
    """Test _handle_post_action extracts config values."""
    network = TestSocialNetwork(
        status_text='Post text',
        status_link='http://link.com',
        status_image_url_1='img1.jpg',
        status_image_url_2='img2.jpg'
    )

    await network._handle_post_action()

    assert len(network.posts_created) == 1
    post = network.posts_created[0]
    assert post['text'] == 'Post text'
    assert post['link'] == 'http://link.com'
    assert post['images'][0] == 'img1.jpg'
    assert post['images'][1] == 'img2.jpg'


@pytest.mark.asyncio
async def test_handle_post_action_from_env():
    """Test _handle_post_action uses environment variables as fallback."""
    with patch.dict(os.environ, {'STATUS_TEXT': 'Env text', 'STATUS_LINK': 'http://env.com'}):
        network = TestSocialNetwork()

        await network._handle_post_action()

        assert len(network.posts_created) == 1
        post = network.posts_created[0]
        assert post['text'] == 'Env text'
        assert post['link'] == 'http://env.com'


@pytest.mark.asyncio
async def test_handle_like_action():
    """Test _handle_like_action requires post_id."""
    network = TestSocialNetwork(post_id='like-123')

    with patch.object(network, 'like', new_callable=AsyncMock) as mock_like:
        await network._handle_like_action()
        mock_like.assert_called_once_with('like-123')


@pytest.mark.asyncio
async def test_handle_like_action_missing_post_id():
    """Test _handle_like_action raises exception when post_id missing."""
    network = TestSocialNetwork()

    with pytest.raises(Exception, match='Post ID is required for like'):
        await network._handle_like_action()


@pytest.mark.asyncio
async def test_handle_share_action():
    """Test _handle_share_action requires post_id."""
    network = TestSocialNetwork(post_id='share-456')

    with patch.object(network, 'share', new_callable=AsyncMock) as mock_share:
        await network._handle_share_action()
        mock_share.assert_called_once_with('share-456')


@pytest.mark.asyncio
async def test_handle_share_action_missing_post_id():
    """Test _handle_share_action raises exception when post_id missing."""
    network = TestSocialNetwork()

    with pytest.raises(Exception, match='Post ID is required for share'):
        await network._handle_share_action()


@pytest.mark.asyncio
async def test_handle_delete_action():
    """Test _handle_delete_action requires post_id."""
    network = TestSocialNetwork(post_id='delete-789')

    with patch.object(network, 'delete', new_callable=AsyncMock) as mock_delete:
        await network._handle_delete_action()
        mock_delete.assert_called_once_with('delete-789')


@pytest.mark.asyncio
async def test_handle_delete_action_missing_post_id():
    """Test _handle_delete_action raises exception when post_id missing."""
    network = TestSocialNetwork()

    with pytest.raises(Exception, match='Post ID is required for delete'):
        await network._handle_delete_action()


@pytest.mark.asyncio
async def test_handle_video_action():
    """Test _handle_video_action requires video_url."""
    network = TestSocialNetwork(
        status_text='Video text',
        video_url='http://video.mp4',
        video_title='Video Title'
    )

    with patch.object(network, 'video', new_callable=AsyncMock) as mock_video:
        await network._handle_video_action()
        mock_video.assert_called_once_with('Video text', 'http://video.mp4', 'Video Title')


@pytest.mark.asyncio
async def test_handle_video_action_missing_url():
    """Test _handle_video_action raises exception when video_url missing."""
    network = TestSocialNetwork(status_text='Text')

    with pytest.raises(Exception, match='Video URL is required'):
        await network._handle_video_action()


@pytest.mark.asyncio
@patch('agoras.core.interfaces.Feed')
async def test_handle_last_from_feed_action(mock_feed_class):
    """Test _handle_last_from_feed_action with defaults."""
    mock_feed = MagicMock()
    mock_feed.download = AsyncMock()
    mock_feed.get_items_since = MagicMock(return_value=[])
    mock_feed_class.return_value = mock_feed

    network = TestSocialNetwork(feed_url='http://feed.rss')

    with patch.object(network, 'last_from_feed', new_callable=AsyncMock) as mock_last:
        await network._handle_last_from_feed_action()
        mock_last.assert_called_once_with('http://feed.rss', 1, 3600)


@pytest.mark.asyncio
@patch('agoras.core.interfaces.Feed')
async def test_handle_last_from_feed_action_custom_values(mock_feed_class):
    """Test _handle_last_from_feed_action with custom values."""
    mock_feed = MagicMock()
    mock_feed.download = AsyncMock()
    mock_feed.get_items_since = MagicMock(return_value=[])
    mock_feed_class.return_value = mock_feed

    network = TestSocialNetwork(
        feed_url='http://feed.rss',
        max_count='5',
        post_lookback='7200'
    )

    with patch.object(network, 'last_from_feed', new_callable=AsyncMock) as mock_last:
        await network._handle_last_from_feed_action()
        mock_last.assert_called_once_with('http://feed.rss', 5, 7200)


@pytest.mark.asyncio
async def test_handle_random_from_feed_action():
    """Test _handle_random_from_feed_action with defaults."""
    network = TestSocialNetwork(feed_url='http://feed.rss')

    with patch.object(network, 'random_from_feed', new_callable=AsyncMock) as mock_random:
        await network._handle_random_from_feed_action()
        mock_random.assert_called_once_with('http://feed.rss', 365)


@pytest.mark.asyncio
async def test_handle_random_from_feed_action_custom_age():
    """Test _handle_random_from_feed_action with custom max_post_age."""
    network = TestSocialNetwork(
        feed_url='http://feed.rss',
        max_post_age='30'
    )

    with patch.object(network, 'random_from_feed', new_callable=AsyncMock) as mock_random:
        await network._handle_random_from_feed_action()
        mock_random.assert_called_once_with('http://feed.rss', 30)


@pytest.mark.asyncio
async def test_handle_schedule_action():
    """Test _handle_schedule_action extracts values."""
    network = TestSocialNetwork(
        google_sheets_id='sheet-id',
        google_sheets_name='Sheet1',
        google_sheets_client_email='email@example.com',
        google_sheets_private_key='key',
        max_count='3'
    )

    with patch.object(network, 'schedule', new_callable=AsyncMock) as mock_schedule:
        await network._handle_schedule_action()
        mock_schedule.assert_called_once_with(
            'sheet-id', 'Sheet1', 'email@example.com', 'key', 3
        )


# Feed and Schedule Method Tests

@pytest.mark.asyncio
@patch('agoras.core.interfaces.Feed')
async def test_last_from_feed(mock_feed_class):
    """Test last_from_feed posts recent items."""
    # Create mock feed items
    mock_item1 = MagicMock()
    mock_item1.link = 'http://item1.com'
    mock_item1.title = 'Title 1'
    mock_item1.image_url = 'img1.jpg'
    mock_item1.get_timestamped_link = MagicMock(return_value='http://item1.com?t=123')

    mock_item2 = MagicMock()
    mock_item2.link = 'http://item2.com'
    mock_item2.title = 'Title 2'
    mock_item2.image_url = None
    mock_item2.get_timestamped_link = MagicMock(return_value='http://item2.com?t=456')

    mock_feed = MagicMock()
    mock_feed.download = AsyncMock()
    mock_feed.get_items_since = MagicMock(return_value=[mock_item1, mock_item2])
    mock_feed_class.return_value = mock_feed

    network = TestSocialNetwork()

    await network.last_from_feed('http://feed.rss', max_count=2, post_lookback=3600)

    assert len(network.posts_created) == 2
    assert network.posts_created[0]['text'] == 'Title 1'
    assert network.posts_created[1]['text'] == 'Title 2'


@pytest.mark.asyncio
@patch('agoras.core.interfaces.Feed')
async def test_last_from_feed_respects_max_count(mock_feed_class):
    """Test last_from_feed respects max_count parameter."""
    mock_items = [MagicMock() for _ in range(5)]
    for i, item in enumerate(mock_items):
        item.link = f'http://item{i}.com'
        item.title = f'Title {i}'
        item.image_url = None
        item.get_timestamped_link = MagicMock(return_value=f'http://item{i}.com?t=123')

    mock_feed = MagicMock()
    mock_feed.download = AsyncMock()
    mock_feed.get_items_since = MagicMock(return_value=mock_items)
    mock_feed_class.return_value = mock_feed

    network = TestSocialNetwork()

    await network.last_from_feed('http://feed.rss', max_count=3, post_lookback=3600)

    # Should only create 3 posts, not 5
    assert len(network.posts_created) == 3


@pytest.mark.asyncio
@patch('agoras.core.interfaces.Feed')
async def test_random_from_feed(mock_feed_class):
    """Test random_from_feed posts random item."""
    mock_item = MagicMock()
    mock_item.link = 'http://random.com'
    mock_item.title = 'Random Title'
    mock_item.image_url = 'random.jpg'
    mock_item.get_timestamped_link = MagicMock(return_value='http://random.com?t=999')

    mock_feed = MagicMock()
    mock_feed.download = AsyncMock()
    mock_feed.get_random_item = MagicMock(return_value=mock_item)
    mock_feed_class.return_value = mock_feed

    network = TestSocialNetwork()

    await network.random_from_feed('http://feed.rss', max_post_age=30)

    assert len(network.posts_created) == 1
    assert network.posts_created[0]['text'] == 'Random Title'


@pytest.mark.asyncio
@patch('agoras.core.interfaces.ScheduleSheet')
async def test_schedule(mock_sheet_class):
    """Test schedule processes posts from sheet."""
    # Mock sheet with posts
    post_data = [
        {
            'status_text': 'Scheduled 1',
            'status_link': 'http://link1.com',
            'status_image_url_1': 'img1.jpg',
            'status_image_url_2': None,
            'status_image_url_3': None,
            'status_image_url_4': None
        },
        {
            'status_text': 'Scheduled 2',
            'status_link': 'http://link2.com',
            'status_image_url_1': None,
            'status_image_url_2': None,
            'status_image_url_3': None,
            'status_image_url_4': None
        }
    ]

    mock_sheet = MagicMock()
    mock_sheet.authenticate = AsyncMock()
    mock_sheet.get_worksheet = AsyncMock()
    mock_sheet.process_scheduled_posts = AsyncMock(return_value=post_data)
    mock_sheet_class.return_value = mock_sheet

    network = TestSocialNetwork()

    await network.schedule(
        'sheet-id', 'Sheet1',
        'email@example.com', 'private-key',
        max_count=5
    )

    assert len(network.posts_created) == 2
    assert network.posts_created[0]['text'] == 'Scheduled 1'
    assert network.posts_created[1]['text'] == 'Scheduled 2'
