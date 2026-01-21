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

from unittest.mock import MagicMock, Mock, patch

import pytest

from agoras.platforms.x.client import XAPIClient


class TestXAPIClient:
    """Test XAPIClient class."""

    def test_x_client_init(self):
        """Test XAPIClient __init__ stores credentials and initializes state."""
        client = XAPIClient(
            consumer_key='ck',
            consumer_secret='cs',
            oauth_token='ot',
            oauth_secret='os'
        )

        assert client.consumer_key == 'ck'
        assert client.consumer_secret == 'cs'
        assert client.oauth_token == 'ot'
        assert client.oauth_secret == 'os'
        assert client.client_v1 is None
        assert client.client_v2 is None
        assert client._authenticated is False

    @patch('agoras.platforms.x.client.OAuth1UserHandler')
    @patch('agoras.platforms.x.client.API')
    @patch('agoras.platforms.x.client.Client')
    @pytest.mark.asyncio
    async def test_x_client_authenticate_success(self, mock_client_class, mock_api_class, mock_oauth_class):
        """Test authenticate success."""
        mock_oauth = MagicMock()
        mock_oauth_class.return_value = mock_oauth

        mock_client_v1 = MagicMock()
        mock_api_class.return_value = mock_client_v1

        mock_client_v2 = MagicMock()
        mock_client_class.return_value = mock_client_v2

        client = XAPIClient('ck', 'cs', 'ot', 'os')
        result = await client.authenticate()

        assert result is True
        assert client._authenticated is True
        assert client.client_v1 is mock_client_v1
        assert client.client_v2 is mock_client_v2
        mock_oauth_class.assert_called_once_with('ck', 'cs', access_token='ot', access_token_secret='os')
        mock_api_class.assert_called_once_with(mock_oauth, wait_on_rate_limit=False)
        mock_client_class.assert_called_once()

    @pytest.mark.asyncio
    async def test_x_client_authenticate_already(self):
        """Test authenticate when already authenticated."""
        client = XAPIClient('ck', 'cs', 'ot', 'os')
        client._authenticated = True

        result = await client.authenticate()

        assert result is True
        # Should not attempt to create new clients

    @pytest.mark.asyncio
    async def test_x_client_authenticate_missing_creds(self):
        """Test authenticate with missing credentials."""
        client = XAPIClient('', 'cs', 'ot', 'os')  # empty consumer_key

        with pytest.raises(Exception, match="All X OAuth credentials are required"):
            await client.authenticate()

    @patch('agoras.platforms.x.client.OAuth1UserHandler')
    @pytest.mark.asyncio
    async def test_x_client_authenticate_missing_token_error(self, mock_oauth_class):
        """Test authenticate with missing token error."""
        mock_oauth_class.side_effect = Exception("missing_token oauth_token is missing")

        client = XAPIClient('ck', 'cs', 'ot', 'os')

        with pytest.raises(Exception, match=r'X authentication failed: Invalid or expired access tokens.*agoras x authorize'):
            await client.authenticate()

    @patch('agoras.platforms.x.client.OAuth1UserHandler')
    @pytest.mark.asyncio
    async def test_x_client_authenticate_generic_error(self, mock_oauth_class):
        """Test authenticate with generic error."""
        mock_oauth_class.side_effect = Exception('some error')

        client = XAPIClient('ck', 'cs', 'ot', 'os')

        with pytest.raises(Exception, match="X authentication failed: some error"):
            await client.authenticate()

    def test_x_client_disconnect(self):
        """Test disconnect method."""
        client = XAPIClient('ck', 'cs', 'ot', 'os')
        client.client_v1 = MagicMock()
        client.client_v2 = MagicMock()
        client._authenticated = True

        client.disconnect()

        assert client.client_v1 is None
        assert client.client_v2 is None
        assert client._authenticated is False

    def test_x_client_verify_credentials_no_client(self):
        """Test _verify_credentials with no client_v1."""
        client = XAPIClient('ck', 'cs', 'ot', 'os')
        client.client_v1 = None

        with pytest.raises(Exception, match='X v1 client not initialized'):
            client._verify_credentials()

    @patch('agoras.platforms.x.client.API')
    def test_x_client_verify_credentials_success(self, mock_api_class):
        """Test _verify_credentials success."""
        mock_client_v1 = MagicMock()
        mock_user = MagicMock()
        mock_client_v1.verify_credentials.return_value = mock_user
        mock_api_class.return_value = mock_client_v1

        client = XAPIClient('ck', 'cs', 'ot', 'os')
        client.client_v1 = mock_client_v1

        # Should not raise
        client._verify_credentials()

        mock_client_v1.verify_credentials.assert_called_once()

    @patch('agoras.platforms.x.client.API')
    def test_x_client_verify_credentials_missing_token(self, mock_api_class):
        """Test _verify_credentials with missing token error."""
        mock_client_v1 = MagicMock()
        mock_client_v1.verify_credentials.side_effect = Exception("missing_token")
        mock_api_class.return_value = mock_client_v1

        client = XAPIClient('ck', 'cs', 'ot', 'os')
        client.client_v1 = mock_client_v1

        with pytest.raises(Exception, match='X credential verification failed.*Error: missing_token'):
            client._verify_credentials()

    @patch('agoras.platforms.x.client.API')
    def test_x_client_verify_credentials_other(self, mock_api_class):
        """Test _verify_credentials with other error."""
        mock_client_v1 = MagicMock()
        mock_client_v1.verify_credentials.side_effect = Exception("other error")
        mock_api_class.return_value = mock_client_v1

        client = XAPIClient('ck', 'cs', 'ot', 'os')
        client.client_v1 = mock_client_v1

        with pytest.raises(Exception, match='other error'):
            client._verify_credentials()

    @patch('asyncio.to_thread')
    @pytest.mark.asyncio
    async def test_x_client_get_user_info_no_client(self, mock_to_thread):
        """Test get_user_info with no client_v1."""
        client = XAPIClient('ck', 'cs', 'ot', 'os')
        client.client_v1 = None

        with pytest.raises(Exception, match='X v1 client not initialized'):
            await client.get_user_info()

        mock_to_thread.assert_not_called()

    @patch('asyncio.to_thread')
    @pytest.mark.asyncio
    async def test_x_client_get_user_info_success(self, mock_to_thread):
        """Test get_user_info success."""
        # Create mock user object
        mock_user = MagicMock()
        mock_user.id = 12345
        mock_user.screen_name = 'testuser'
        mock_user.name = 'Test User'
        mock_user.description = 'Test description'
        mock_user.followers_count = 100
        mock_user.friends_count = 50
        mock_user.statuses_count = 200
        mock_user.verified = True

        # Mock the inner function that asyncio.to_thread will call
        def mock_inner():
            return mock_user

        mock_to_thread.side_effect = lambda func: func()  # Run the function immediately

        client = XAPIClient('ck', 'cs', 'ot', 'os')
        client.client_v1 = MagicMock()
        client.client_v1.verify_credentials.return_value = mock_user

        result = await client.get_user_info()

        assert result == {
            'user_id': '12345',
            'screen_name': 'testuser',
            'name': 'Test User',
            'description': 'Test description',
            'followers_count': 100,
            'friends_count': 50,
            'statuses_count': 200,
            'verified': True
        }

    @patch('asyncio.to_thread')
    @pytest.mark.asyncio
    async def test_x_client_upload_media_no_client(self, mock_to_thread):
        """Test upload_media with no client_v1."""
        client = XAPIClient('ck', 'cs', 'ot', 'os')
        client.client_v1 = None

        with pytest.raises(Exception, match='X v1 client not initialized'):
            await client.upload_media(b'test', 'image/png')

        mock_to_thread.assert_not_called()

    @patch('asyncio.to_thread')
    @patch('os.unlink')
    @patch('os.path.exists')
    @patch('builtins.open')
    @patch('tempfile.mkstemp')
    @pytest.mark.asyncio
    async def test_x_client_upload_media_success(self, mock_mkstemp, mock_open, mock_exists, mock_unlink, mock_to_thread):
        """Test upload_media success."""
        # Mock tempfile operations
        mock_mkstemp.return_value = (42, '/tmp/test_file')
        mock_file = MagicMock()
        mock_open.return_value.__enter__.return_value = mock_file
        mock_exists.return_value = True  # File exists, so unlink will be called

        # Mock the media upload response
        mock_media = MagicMock()
        mock_media.media_id = 'media123'

        # Mock the inner function
        def mock_inner():
            return mock_media

        mock_to_thread.side_effect = lambda func: func()

        client = XAPIClient('ck', 'cs', 'ot', 'os')
        client.client_v1 = MagicMock()
        client.client_v1.media_upload.return_value = mock_media

        result = await client.upload_media(b'test content', 'image/png')

        assert result == 'media123'
        mock_mkstemp.assert_called_once()
        mock_open.assert_called_once_with('/tmp/test_file', 'wb')
        mock_file.write.assert_called_once_with(b'test content')
        mock_exists.assert_called_once_with('/tmp/test_file')
        mock_unlink.assert_called_once_with('/tmp/test_file')

    @pytest.mark.asyncio
    async def test_x_client_create_tweet_no_client(self):
        """Test create_tweet with no client_v2."""
        client = XAPIClient('ck', 'cs', 'ot', 'os')
        client.client_v2 = None

        with pytest.raises(Exception, match='X v2 client not initialized'):
            await client.create_tweet('test')

    @patch('asyncio.to_thread')
    @pytest.mark.asyncio
    async def test_x_client_create_tweet_text_only(self, mock_to_thread):
        """Test create_tweet with text only."""
        mock_response = MagicMock()
        mock_response.data = {'id': 'tweet123'}

        def mock_inner():
            return mock_response

        mock_to_thread.side_effect = lambda func: func()

        client = XAPIClient('ck', 'cs', 'ot', 'os')
        client.client_v2 = MagicMock()
        client.client_v2.create_tweet.return_value = mock_response

        result = await client.create_tweet('Hello world')

        assert result == 'tweet123'
        client.client_v2.create_tweet.assert_called_once_with(text='Hello world')

    @patch('asyncio.to_thread')
    @pytest.mark.asyncio
    async def test_x_client_create_tweet_with_media(self, mock_to_thread):
        """Test create_tweet with media."""
        mock_response = MagicMock()
        mock_response.data = {'id': 'tweet456'}

        def mock_inner():
            return mock_response

        mock_to_thread.side_effect = lambda func: func()

        client = XAPIClient('ck', 'cs', 'ot', 'os')
        client.client_v2 = MagicMock()
        client.client_v2.create_tweet.return_value = mock_response

        result = await client.create_tweet('Hello with media', ['media1', 'media2'])

        assert result == 'tweet456'
        client.client_v2.create_tweet.assert_called_once_with(text='Hello with media', media_ids=['media1', 'media2'])

    @patch('asyncio.to_thread')
    @pytest.mark.asyncio
    async def test_x_client_create_tweet_invalid_response(self, mock_to_thread):
        """Test create_tweet with invalid response."""
        mock_response = MagicMock()
        mock_response.data = None  # Invalid response

        def mock_inner():
            return mock_response

        mock_to_thread.side_effect = lambda func: func()

        client = XAPIClient('ck', 'cs', 'ot', 'os')
        client.client_v2 = MagicMock()
        client.client_v2.create_tweet.return_value = mock_response

        with pytest.raises(Exception, match='Invalid response from X API'):
            await client.create_tweet('test')

    @patch('asyncio.to_thread')
    @pytest.mark.asyncio
    async def test_x_client_create_tweet_api_error(self, mock_to_thread):
        """Test create_tweet with API error."""
        def mock_inner():
            raise Exception('API error')

        mock_to_thread.side_effect = lambda func: func()

        client = XAPIClient('ck', 'cs', 'ot', 'os')
        client.client_v2 = MagicMock()
        client.client_v2.create_tweet.side_effect = Exception('API error')

        with pytest.raises(Exception, match='X API error: API error'):
            await client.create_tweet('test')

    @pytest.mark.asyncio
    async def test_x_client_like_tweet_no_client(self):
        """Test like_tweet with no client_v2."""
        client = XAPIClient('ck', 'cs', 'ot', 'os')
        client.client_v2 = None

        with pytest.raises(Exception, match='X v2 client not initialized'):
            await client.like_tweet('tweet123')

    @patch('asyncio.to_thread')
    @pytest.mark.asyncio
    async def test_x_client_like_tweet_success(self, mock_to_thread):
        """Test like_tweet success."""
        def mock_inner():
            return None

        mock_to_thread.side_effect = lambda func: func()

        client = XAPIClient('ck', 'cs', 'ot', 'os')
        client.client_v2 = MagicMock()

        result = await client.like_tweet('tweet123')

        assert result == 'tweet123'
        client.client_v2.like.assert_called_once_with('tweet123')

    @pytest.mark.asyncio
    async def test_x_client_retweet_no_client(self):
        """Test retweet with no client_v2."""
        client = XAPIClient('ck', 'cs', 'ot', 'os')
        client.client_v2 = None

        with pytest.raises(Exception, match='X v2 client not initialized'):
            await client.retweet('tweet123')

    @patch('asyncio.to_thread')
    @pytest.mark.asyncio
    async def test_x_client_retweet_success(self, mock_to_thread):
        """Test retweet success."""
        def mock_inner():
            return None

        mock_to_thread.side_effect = lambda func: func()

        client = XAPIClient('ck', 'cs', 'ot', 'os')
        client.client_v2 = MagicMock()

        result = await client.retweet('tweet123')

        assert result == 'tweet123'
        client.client_v2.retweet.assert_called_once_with('tweet123')

    @pytest.mark.asyncio
    async def test_x_client_delete_tweet_no_client(self):
        """Test delete_tweet with no client_v2."""
        client = XAPIClient('ck', 'cs', 'ot', 'os')
        client.client_v2 = None

        with pytest.raises(Exception, match='X v2 client not initialized'):
            await client.delete_tweet('tweet123')

    @patch('asyncio.to_thread')
    @pytest.mark.asyncio
    async def test_x_client_delete_tweet_success(self, mock_to_thread):
        """Test delete_tweet success."""
        def mock_inner():
            return None

        mock_to_thread.side_effect = lambda func: func()

        client = XAPIClient('ck', 'cs', 'ot', 'os')
        client.client_v2 = MagicMock()

        result = await client.delete_tweet('tweet123')

        assert result == 'tweet123'
        client.client_v2.delete_tweet.assert_called_once_with('tweet123')