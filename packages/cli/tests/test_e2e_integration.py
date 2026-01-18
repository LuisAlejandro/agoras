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
End-to-end integration tests for CLI -> Core -> Platform flow.
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# Test CLI to Platform Flow


@patch('agoras.cli.commands.publish.x')
def test_cli_to_platform_x_flow(mock_x):
    """Test CLI parser to X platform execution flow."""
    from agoras.cli.commands.publish import main

    mock_x.return_value = None

    # Simulate CLI arguments for X post
    result = main(
        network='x',
        action='post',
        twitter_consumer_key='key',
        twitter_consumer_secret='secret',
        twitter_oauth_token='token',
        twitter_oauth_secret='token_secret',
        status_text='Test post',
        status_link='http://link.com'
    )

    mock_x.assert_called_once()


@patch('agoras.cli.commands.publish.facebook')
def test_cli_to_platform_facebook_flow(mock_facebook):
    """Test CLI parser to Facebook platform execution flow."""
    from agoras.cli.commands.publish import main

    mock_facebook.return_value = None

    result = main(
        network='facebook',
        action='post',
        facebook_access_token='token',
        facebook_object_id='page123',
        status_text='Test post',
        status_link='http://link.com'
    )

    mock_facebook.assert_called_once()


# Test Feed Integration

@patch('agoras.core.interfaces.Feed')
@patch('agoras.platforms.x.wrapper.X._initialize_client', new_callable=AsyncMock)
@patch('agoras.platforms.x.wrapper.X.post', new_callable=AsyncMock)
def test_feed_integration_flow(mock_post, mock_init_client, mock_feed_class):
    """Test CLI feed command through Core Feed to Platform post."""
    from agoras.cli.commands.publish import main

    # Mock feed
    mock_item = MagicMock()
    mock_item.link = 'http://item.com'
    mock_item.title = 'Feed Item'
    mock_item.image_url = 'img.jpg'
    mock_item.get_timestamped_link = MagicMock(return_value='http://item.com?t=123')

    mock_feed = MagicMock()
    # Make download return the mock_feed instance (for method chaining)
    mock_feed.download = AsyncMock(return_value=mock_feed)
    mock_feed.get_items_since = MagicMock(return_value=[mock_item])
    mock_feed_class.return_value = mock_feed

    # Mock platform methods (already AsyncMock from new_callable)

    result = main(
        network='x',
        action='last-from-feed',
        twitter_consumer_key='key',
        twitter_consumer_secret='secret',
        twitter_oauth_token='token',
        twitter_oauth_secret='token_secret',
        feed_url='http://feed.rss',
        max_count=1,
        post_lookback=3600
    )

    mock_feed.download.assert_called_once()
    mock_post.assert_called_once()


# Test Error Propagation

@patch('agoras.cli.commands.publish.discord')
def test_platform_error_propagates_to_cli(mock_discord):
    """Test platform errors propagate correctly to CLI."""
    from agoras.cli.commands.publish import main

    mock_discord.side_effect = Exception('Platform error')

    with pytest.raises(Exception, match='Platform error'):
        main(
            network='discord',
            action='post',
            discord_bot_token='token',
            discord_server_name='Server',
            discord_channel_name='Channel',
            status_text='Test',
            status_link=''
        )


@patch('agoras.core.interfaces.Feed')
@patch('agoras.platforms.telegram.wrapper.Telegram._initialize_client', new_callable=AsyncMock)
def test_invalid_feed_url_handling(mock_init_client, mock_feed_class):
    """Test graceful handling of invalid feed URL."""
    from agoras.cli.commands.publish import main

    # Mock feed download failure
    mock_feed = MagicMock()

    async def download_side_effect(*args, **kwargs):
        raise Exception('Invalid feed URL')
    mock_feed.download = AsyncMock(side_effect=download_side_effect)
    mock_feed_class.return_value = mock_feed

    # Mock platform initialization (already AsyncMock from new_callable)

    with pytest.raises(Exception, match='Invalid feed URL'):
        main(
            network='telegram',
            action='last-from-feed',
            telegram_bot_token='token',
            telegram_chat_id='123',
            feed_url='invalid://feed',
            max_count=1
        )
