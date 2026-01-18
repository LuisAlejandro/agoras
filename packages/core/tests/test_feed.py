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

import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from agoras.core.feed import Feed, FeedItem, FeedManager


# Helper function to create mock feed items
def create_mock_feed_item(title='Title', link='http://link.com',
                          pub_date=None, image_url=None, guid=None):
    """Helper to create mock feed items for testing."""
    mock_raw = MagicMock()
    mock_raw.title = title
    mock_raw.link = link
    mock_raw.guid = guid or link
    mock_raw.pub_date = pub_date
    mock_raw.description = f"Description for {title}"
    mock_raw.enclosures = []
    if image_url:
        mock_enc = MagicMock()
        mock_enc.url = image_url
        mock_raw.enclosures = [mock_enc]
    return FeedItem(mock_raw)


# Feed Class Tests

def test_feed_instantiation():
    """Test Feed can be instantiated with URL."""
    feed = Feed('https://example.com/feed.xml')
    assert feed.url == 'https://example.com/feed.xml'
    assert feed._downloaded is False


def test_feed_has_download_method():
    """Test Feed has download method."""
    feed = Feed('https://example.com/feed.xml')
    assert hasattr(feed, 'download')
    assert callable(getattr(feed, 'download'))


def test_feed_has_filter_methods():
    """Test Feed has filtering methods."""
    feed = Feed('https://example.com/feed.xml')
    assert hasattr(feed, 'get_items_since')
    assert hasattr(feed, 'get_random_item')
    assert hasattr(feed, 'get_latest_items')
    assert hasattr(feed, 'filter_items')


# Download Tests

@pytest.mark.asyncio
@patch('agoras.core.feed.feed.urlopen')
@patch('agoras.core.feed.feed.parse_rss_bytes')
async def test_download_success(mock_parse, mock_urlopen):
    """Test successful feed download and parsing."""
    mock_response = MagicMock()
    mock_response.read.return_value = b'<rss><channel></channel></rss>'
    mock_urlopen.return_value = mock_response

    mock_feed_data = MagicMock()
    mock_feed_data.items = []
    mock_parse.return_value = mock_feed_data

    feed = Feed('http://feed.rss')
    result = await feed.download()

    assert feed._downloaded is True
    assert result is feed  # Returns self for chaining


@pytest.mark.asyncio
async def test_download_no_url_raises_exception():
    """Test download with no URL raises exception."""
    feed = Feed('')

    with pytest.raises(Exception, match='No feed URL provided'):
        await feed.download()


@pytest.mark.asyncio
@patch('agoras.core.feed.feed.urlopen')
@patch('agoras.core.feed.feed.parse_rss_bytes')
async def test_download_caching(mock_parse, mock_urlopen):
    """Test download caching (doesn't re-download if already downloaded)."""
    mock_response = MagicMock()
    mock_response.read.return_value = b'<rss></rss>'
    mock_urlopen.return_value = mock_response

    mock_feed_data = MagicMock()
    mock_feed_data.items = []
    mock_parse.return_value = mock_feed_data

    feed = Feed('http://feed.rss')

    # First download
    await feed.download()
    first_call_count = mock_urlopen.call_count

    # Second download should use cache
    await feed.download()

    # Should not call urlopen again
    assert mock_urlopen.call_count == first_call_count


# Property Tests

def test_items_property_before_download():
    """Test items property raises exception before download."""
    feed = Feed('http://feed.rss')

    with pytest.raises(Exception, match='Feed must be downloaded'):
        _ = feed.items


@pytest.mark.asyncio
@patch('agoras.core.feed.feed.urlopen')
@patch('agoras.core.feed.feed.parse_rss_bytes')
async def test_items_property_after_download(mock_parse, mock_urlopen):
    """Test items property returns list after download."""
    mock_response = MagicMock()
    mock_response.read.return_value = b'<rss></rss>'
    mock_urlopen.return_value = mock_response

    mock_item = MagicMock()
    mock_feed_data = MagicMock()
    mock_feed_data.items = [mock_item]
    mock_parse.return_value = mock_feed_data

    feed = Feed('http://feed.rss')
    await feed.download()

    items = feed.items
    assert isinstance(items, list)
    assert len(items) == 1


def test_title_property_before_download():
    """Test title property raises exception before download."""
    feed = Feed('http://feed.rss')

    with pytest.raises(Exception, match='Feed must be downloaded'):
        _ = feed.title


@pytest.mark.asyncio
@patch('agoras.core.feed.feed.urlopen')
@patch('agoras.core.feed.feed.parse_rss_bytes')
async def test_title_property_after_download(mock_parse, mock_urlopen):
    """Test title property returns title after download."""
    mock_response = MagicMock()
    mock_response.read.return_value = b'<rss></rss>'
    mock_urlopen.return_value = mock_response

    mock_feed_data = MagicMock()
    mock_feed_data.items = []
    mock_feed_data.title = 'Feed Title'
    mock_parse.return_value = mock_feed_data

    feed = Feed('http://feed.rss')
    await feed.download()

    assert feed.title == 'Feed Title'


def test_description_property_before_download():
    """Test description property raises exception before download."""
    feed = Feed('http://feed.rss')

    with pytest.raises(Exception, match='Feed must be downloaded'):
        _ = feed.description


@pytest.mark.asyncio
@patch('agoras.core.feed.feed.urlopen')
@patch('agoras.core.feed.feed.parse_rss_bytes')
async def test_description_property_after_download(mock_parse, mock_urlopen):
    """Test description property returns description after download."""
    mock_response = MagicMock()
    mock_response.read.return_value = b'<rss></rss>'
    mock_urlopen.return_value = mock_response

    mock_feed_data = MagicMock()
    mock_feed_data.items = []
    mock_feed_data.description = 'Feed Description'
    mock_parse.return_value = mock_feed_data

    feed = Feed('http://feed.rss')
    await feed.download()

    assert feed.description == 'Feed Description'


# Filtering Tests

def test_get_items_since_before_download():
    """Test get_items_since raises exception before download."""
    feed = Feed('http://feed.rss')

    with pytest.raises(Exception, match='Feed must be downloaded'):
        feed.get_items_since(3600)


@pytest.mark.asyncio
@patch('agoras.core.feed.feed.urlopen')
@patch('agoras.core.feed.feed.parse_rss_bytes')
async def test_get_items_since_filters_by_timestamp(mock_parse, mock_urlopen):
    """Test get_items_since filters items by timestamp."""
    mock_response = MagicMock()
    mock_response.read.return_value = b'<rss></rss>'
    mock_urlopen.return_value = mock_response

    # Create items with different timestamps
    now = datetime.datetime.now()
    recent_date = now - datetime.timedelta(seconds=1800)  # 30 min ago
    old_date = now - datetime.timedelta(seconds=7200)  # 2 hours ago

    mock_item_recent = MagicMock()
    mock_item_recent.pub_date = recent_date

    mock_item_old = MagicMock()
    mock_item_old.pub_date = old_date

    mock_feed_data = MagicMock()
    mock_feed_data.items = [mock_item_recent, mock_item_old]
    mock_parse.return_value = mock_feed_data

    feed = Feed('http://feed.rss')
    await feed.download()

    # Get items from last hour (3600 seconds)
    recent_items = feed.get_items_since(3600)

    # Should only return the recent item
    assert len(recent_items) == 1


def test_get_items_within_days_before_download():
    """Test get_items_within_days raises exception before download."""
    feed = Feed('http://feed.rss')

    with pytest.raises(Exception, match='Feed must be downloaded'):
        feed.get_items_within_days(7)


@pytest.mark.asyncio
@patch('agoras.core.feed.feed.urlopen')
@patch('agoras.core.feed.feed.parse_rss_bytes')
async def test_get_items_within_days_filters_by_age(mock_parse, mock_urlopen):
    """Test get_items_within_days filters items by age in days."""
    mock_response = MagicMock()
    mock_response.read.return_value = b'<rss></rss>'
    mock_urlopen.return_value = mock_response

    now = datetime.datetime.now()
    recent_date = now - datetime.timedelta(days=5)
    old_date = now - datetime.timedelta(days=30)

    mock_item_recent = MagicMock()
    mock_item_recent.pub_date = recent_date

    mock_item_old = MagicMock()
    mock_item_old.pub_date = old_date

    mock_feed_data = MagicMock()
    mock_feed_data.items = [mock_item_recent, mock_item_old]
    mock_parse.return_value = mock_feed_data

    feed = Feed('http://feed.rss')
    await feed.download()

    # Get items from last 7 days
    recent_items = feed.get_items_within_days(7)

    # Should only return the recent item
    assert len(recent_items) == 1


def test_get_random_item_before_download():
    """Test get_random_item raises exception before download."""
    feed = Feed('http://feed.rss')

    with pytest.raises(Exception, match='Feed must be downloaded'):
        feed.get_random_item()


@pytest.mark.asyncio
@patch('agoras.core.feed.feed.urlopen')
@patch('agoras.core.feed.feed.parse_rss_bytes')
async def test_get_random_item(mock_parse, mock_urlopen):
    """Test get_random_item returns a random item."""
    mock_response = MagicMock()
    mock_response.read.return_value = b'<rss></rss>'
    mock_urlopen.return_value = mock_response

    mock_item = MagicMock()
    mock_item.pub_date = datetime.datetime.now()

    mock_feed_data = MagicMock()
    mock_feed_data.items = [mock_item]
    mock_parse.return_value = mock_feed_data

    feed = Feed('http://feed.rss')
    await feed.download()

    item = feed.get_random_item()

    assert isinstance(item, FeedItem)


@pytest.mark.asyncio
@patch('agoras.core.feed.feed.urlopen')
@patch('agoras.core.feed.feed.parse_rss_bytes')
async def test_get_random_item_no_items_available(mock_parse, mock_urlopen):
    """Test get_random_item raises exception when no items available."""
    mock_response = MagicMock()
    mock_response.read.return_value = b'<rss></rss>'
    mock_urlopen.return_value = mock_response

    mock_feed_data = MagicMock()
    mock_feed_data.items = []
    mock_parse.return_value = mock_feed_data

    feed = Feed('http://feed.rss')
    await feed.download()

    with pytest.raises(Exception, match='No suitable items found'):
        feed.get_random_item()


# Advanced Filtering Tests

def test_filter_items_before_download():
    """Test filter_items raises exception before download."""
    feed = Feed('http://feed.rss')

    with pytest.raises(Exception, match='Feed must be downloaded'):
        feed.filter_items()


@pytest.mark.asyncio
@patch('agoras.core.feed.feed.urlopen')
@patch('agoras.core.feed.feed.parse_rss_bytes')
async def test_filter_items_by_title(mock_parse, mock_urlopen):
    """Test filter_items by title_contains."""
    mock_response = MagicMock()
    mock_response.read.return_value = b'<rss></rss>'
    mock_urlopen.return_value = mock_response

    mock_item1 = MagicMock()
    mock_item1.title = 'Python Tutorial'
    mock_item1.pub_date = None

    mock_item2 = MagicMock()
    mock_item2.title = 'JavaScript Guide'
    mock_item2.pub_date = None

    mock_feed_data = MagicMock()
    mock_feed_data.items = [mock_item1, mock_item2]
    mock_parse.return_value = mock_feed_data

    feed = Feed('http://feed.rss')
    await feed.download()

    filtered = feed.filter_items(title_contains='python')

    # Should only return Python item (case insensitive)
    assert len(filtered) == 1
    assert filtered[0].title == 'Python Tutorial'


@pytest.mark.asyncio
@patch('agoras.core.feed.feed.urlopen')
@patch('agoras.core.feed.feed.parse_rss_bytes')
async def test_filter_items_by_has_image_true(mock_parse, mock_urlopen):
    """Test filter_items by has_image=True."""
    mock_response = MagicMock()
    mock_response.read.return_value = b'<rss></rss>'
    mock_urlopen.return_value = mock_response

    mock_item_with_img = MagicMock()
    mock_item_with_img.title = 'Item 1'
    mock_item_with_img.pub_date = None
    mock_enc = MagicMock()
    mock_enc.url = 'img.jpg'
    mock_item_with_img.enclosures = [mock_enc]

    mock_item_no_img = MagicMock()
    mock_item_no_img.title = 'Item 2'
    mock_item_no_img.pub_date = None
    mock_item_no_img.enclosures = []

    mock_feed_data = MagicMock()
    mock_feed_data.items = [mock_item_with_img, mock_item_no_img]
    mock_parse.return_value = mock_feed_data

    feed = Feed('http://feed.rss')
    await feed.download()

    filtered = feed.filter_items(has_image=True)

    # Should only return item with image
    assert len(filtered) == 1


@pytest.mark.asyncio
@patch('agoras.core.feed.feed.urlopen')
@patch('agoras.core.feed.feed.parse_rss_bytes')
async def test_filter_items_by_has_image_false(mock_parse, mock_urlopen):
    """Test filter_items by has_image=False."""
    mock_response = MagicMock()
    mock_response.read.return_value = b'<rss></rss>'
    mock_urlopen.return_value = mock_response

    mock_item_with_img = MagicMock()
    mock_item_with_img.title = 'Item 1'
    mock_item_with_img.pub_date = None
    mock_enc = MagicMock()
    mock_enc.url = 'img.jpg'
    mock_item_with_img.enclosures = [mock_enc]

    mock_item_no_img = MagicMock()
    mock_item_no_img.title = 'Item 2'
    mock_item_no_img.pub_date = None
    mock_item_no_img.enclosures = []

    mock_feed_data = MagicMock()
    mock_feed_data.items = [mock_item_with_img, mock_item_no_img]
    mock_parse.return_value = mock_feed_data

    feed = Feed('http://feed.rss')
    await feed.download()

    filtered = feed.filter_items(has_image=False)

    # Should only return item without image
    assert len(filtered) == 1


@pytest.mark.asyncio
@patch('agoras.core.feed.feed.urlopen')
@patch('agoras.core.feed.feed.parse_rss_bytes')
async def test_filter_items_custom_filter(mock_parse, mock_urlopen):
    """Test filter_items with custom filter function."""
    mock_response = MagicMock()
    mock_response.read.return_value = b'<rss></rss>'
    mock_urlopen.return_value = mock_response

    mock_item1 = MagicMock()
    mock_item1.title = 'Short'
    mock_item1.pub_date = None

    mock_item2 = MagicMock()
    mock_item2.title = 'Very Long Title Here'
    mock_item2.pub_date = None

    mock_feed_data = MagicMock()
    mock_feed_data.items = [mock_item1, mock_item2]
    mock_parse.return_value = mock_feed_data

    feed = Feed('http://feed.rss')
    await feed.download()

    # Filter items with title length > 10
    filtered = feed.filter_items(custom_filter=lambda item: len(item.title) > 10)

    assert len(filtered) == 1
    assert filtered[0].title == 'Very Long Title Here'


# Latest Items Tests

def test_get_latest_items_before_download():
    """Test get_latest_items raises exception before download."""
    feed = Feed('http://feed.rss')

    with pytest.raises(Exception, match='Feed must be downloaded'):
        feed.get_latest_items()


@pytest.mark.asyncio
@patch('agoras.core.feed.feed.urlopen')
@patch('agoras.core.feed.feed.parse_rss_bytes')
async def test_get_latest_items_sorted(mock_parse, mock_urlopen):
    """Test get_latest_items returns items sorted by date."""
    mock_response = MagicMock()
    mock_response.read.return_value = b'<rss></rss>'
    mock_urlopen.return_value = mock_response

    now = datetime.datetime.now()
    date1 = now - datetime.timedelta(days=1)
    date2 = now - datetime.timedelta(days=2)
    date3 = now - datetime.timedelta(days=3)

    mock_item1 = MagicMock()
    mock_item1.pub_date = date2
    mock_item1.title = 'Item 1'

    mock_item2 = MagicMock()
    mock_item2.pub_date = date1  # Newest
    mock_item2.title = 'Item 2'

    mock_item3 = MagicMock()
    mock_item3.pub_date = date3  # Oldest
    mock_item3.title = 'Item 3'

    mock_feed_data = MagicMock()
    mock_feed_data.items = [mock_item1, mock_item2, mock_item3]
    mock_parse.return_value = mock_feed_data

    feed = Feed('http://feed.rss')
    await feed.download()

    latest = feed.get_latest_items(count=3)

    # Should return in newest-first order
    assert len(latest) == 3
    assert latest[0].pub_date == date1


@pytest.mark.asyncio
@patch('agoras.core.feed.feed.urlopen')
@patch('agoras.core.feed.feed.parse_rss_bytes')
async def test_get_latest_items_respects_count(mock_parse, mock_urlopen):
    """Test get_latest_items respects count parameter."""
    mock_response = MagicMock()
    mock_response.read.return_value = b'<rss></rss>'
    mock_urlopen.return_value = mock_response

    now = datetime.datetime.now()
    mock_items = []
    for i in range(5):
        item = MagicMock()
        item.pub_date = now - datetime.timedelta(days=i)
        item.title = f'Item {i}'
        mock_items.append(item)

    mock_feed_data = MagicMock()
    mock_feed_data.items = mock_items
    mock_parse.return_value = mock_feed_data

    feed = Feed('http://feed.rss')
    await feed.download()

    latest = feed.get_latest_items(count=2)

    # Should only return 2 items
    assert len(latest) == 2


# to_dict Tests

def test_to_dict_before_download():
    """Test to_dict raises exception before download."""
    feed = Feed('http://feed.rss')

    with pytest.raises(Exception, match='Feed must be downloaded'):
        feed.to_dict()


@pytest.mark.asyncio
@patch('agoras.core.feed.feed.urlopen')
@patch('agoras.core.feed.feed.parse_rss_bytes')
async def test_to_dict_returns_complete_dictionary(mock_parse, mock_urlopen):
    """Test to_dict returns complete dictionary representation."""
    mock_response = MagicMock()
    mock_response.read.return_value = b'<rss></rss>'
    mock_urlopen.return_value = mock_response

    mock_item = MagicMock()
    mock_item.pub_date = None
    mock_item.title = 'Item Title'

    mock_feed_data = MagicMock()
    mock_feed_data.items = [mock_item]
    mock_feed_data.title = 'Feed Title'
    mock_feed_data.description = 'Feed Description'
    mock_parse.return_value = mock_feed_data

    feed = Feed('http://feed.rss')
    await feed.download()

    feed_dict = feed.to_dict()

    assert feed_dict['url'] == 'http://feed.rss'
    assert feed_dict['title'] == 'Feed Title'
    assert feed_dict['description'] == 'Feed Description'
    assert feed_dict['item_count'] == 1
    assert 'items' in feed_dict


# FeedItem Tests

def test_feeditem_instantiation():
    """Test FeedItem can be instantiated."""
    mock_raw = MagicMock()
    item = FeedItem(mock_raw)
    assert item.raw_item is mock_raw
    assert item._processed is False


def test_feeditem_title_with_html_entities():
    """Test FeedItem title property unescapes HTML entities."""
    mock_raw = MagicMock()
    mock_raw.title = 'Test &amp; Title &lt;tag&gt;'
    mock_raw.link = 'http://link.com'
    mock_raw.guid = 'http://link.com'
    mock_raw.pub_date = None
    mock_raw.enclosures = []

    item = FeedItem(mock_raw)

    assert item.title == 'Test & Title <tag>'


def test_feeditem_link_fallback_to_guid():
    """Test FeedItem link falls back to guid when link is None."""
    mock_raw = MagicMock()
    mock_raw.title = 'Title'
    mock_raw.link = None
    mock_raw.guid = 'http://guid-link.com'
    mock_raw.pub_date = None
    mock_raw.enclosures = []

    item = FeedItem(mock_raw)

    assert item.link == 'http://guid-link.com'


def test_feeditem_description():
    """Test FeedItem description property."""
    mock_raw = MagicMock()
    mock_raw.title = 'Title'
    mock_raw.link = 'http://link.com'
    mock_raw.guid = 'http://link.com'
    mock_raw.description = 'Item description'
    mock_raw.pub_date = None
    mock_raw.enclosures = []

    item = FeedItem(mock_raw)

    assert item.description == 'Item description'


def test_feeditem_pub_date():
    """Test FeedItem pub_date property."""
    pub_date = datetime.datetime(2024, 1, 15, 12, 30, 0)
    mock_raw = MagicMock()
    mock_raw.title = 'Title'
    mock_raw.link = 'http://link.com'
    mock_raw.guid = 'http://link.com'
    mock_raw.pub_date = pub_date
    mock_raw.enclosures = []

    item = FeedItem(mock_raw)

    assert item.pub_date == pub_date


def test_feeditem_timestamp_conversion():
    """Test FeedItem timestamp property converts pub_date."""
    pub_date = datetime.datetime(2024, 1, 15, 12, 30, 45)
    mock_raw = MagicMock()
    mock_raw.title = 'Title'
    mock_raw.link = 'http://link.com'
    mock_raw.guid = 'http://link.com'
    mock_raw.pub_date = pub_date
    mock_raw.enclosures = []

    item = FeedItem(mock_raw)

    assert item.timestamp == 20240115123045


def test_feeditem_image_url_from_enclosures():
    """Test FeedItem image_url from enclosures."""
    mock_raw = MagicMock()
    mock_raw.title = 'Title'
    mock_raw.link = 'http://link.com'
    mock_raw.guid = 'http://link.com'
    mock_raw.pub_date = None

    mock_enc = MagicMock()
    mock_enc.url = 'http://image.jpg'
    mock_raw.enclosures = [mock_enc]

    item = FeedItem(mock_raw)

    assert item.image_url == 'http://image.jpg'


def test_feeditem_image_url_no_enclosures():
    """Test FeedItem image_url when no enclosures."""
    mock_raw = MagicMock()
    mock_raw.title = 'Title'
    mock_raw.link = 'http://link.com'
    mock_raw.guid = 'http://link.com'
    mock_raw.pub_date = None
    mock_raw.enclosures = []

    item = FeedItem(mock_raw)

    assert item.image_url == ''


def test_feeditem_process_only_once():
    """Test _process_item only runs once."""
    mock_raw = MagicMock()
    mock_raw.title = 'Title'
    mock_raw.link = 'http://link.com'
    mock_raw.guid = 'http://link.com'
    mock_raw.pub_date = None
    mock_raw.enclosures = []

    item = FeedItem(mock_raw)

    # Access multiple properties
    _ = item.title
    _ = item.link
    _ = item.description

    # _processed should be True and only set once
    assert item._processed is True


def test_feeditem_get_timestamped_link_custom():
    """Test get_timestamped_link with custom timestamp."""
    mock_raw = MagicMock()
    mock_raw.title = 'Title'
    mock_raw.link = 'http://link.com'
    mock_raw.guid = 'http://link.com'
    mock_raw.pub_date = None
    mock_raw.enclosures = []

    item = FeedItem(mock_raw)

    result = item.get_timestamped_link('20240115120000')

    assert 't=20240115120000' in result
    assert 'http://link.com' in result


def test_feeditem_get_timestamped_link_auto():
    """Test get_timestamped_link with auto timestamp."""
    mock_raw = MagicMock()
    mock_raw.title = 'Title'
    mock_raw.link = 'http://link.com'
    mock_raw.guid = 'http://link.com'
    mock_raw.pub_date = None
    mock_raw.enclosures = []

    item = FeedItem(mock_raw)

    result = item.get_timestamped_link()

    assert 't=' in result
    assert 'http://link.com' in result


def test_feeditem_get_timestamped_link_no_link():
    """Test get_timestamped_link returns empty when no link."""
    mock_raw = MagicMock()
    mock_raw.title = 'Title'
    mock_raw.link = None
    mock_raw.guid = None
    mock_raw.pub_date = None
    mock_raw.enclosures = []

    item = FeedItem(mock_raw)

    result = item.get_timestamped_link()

    assert result == ''


def test_feeditem_to_dict():
    """Test FeedItem to_dict returns complete dictionary."""
    pub_date = datetime.datetime(2024, 1, 15, 12, 0, 0)
    mock_raw = MagicMock()
    mock_raw.title = 'Title'
    mock_raw.link = 'http://link.com'
    mock_raw.guid = 'http://link.com'
    mock_raw.pub_date = pub_date
    mock_raw.description = 'Description'
    mock_raw.enclosures = []

    item = FeedItem(mock_raw)

    item_dict = item.to_dict()

    assert item_dict['title'] == 'Title'
    assert item_dict['link'] == 'http://link.com'
    assert item_dict['description'] == 'Description'
    assert item_dict['pub_date'] == pub_date
    assert item_dict['timestamp'] == 20240115120000


# FeedManager Tests

def test_feedmanager_instantiation():
    """Test FeedManager can be instantiated."""
    manager = FeedManager()
    assert manager.feeds == {}


@pytest.mark.asyncio
@patch('agoras.core.feed.manager.Feed')
async def test_add_feed(mock_feed_class):
    """Test add_feed downloads and stores feed."""
    mock_feed = MagicMock()
    mock_feed.download = AsyncMock()
    mock_feed_class.return_value = mock_feed

    manager = FeedManager()

    result = await manager.add_feed('test_feed', 'http://feed.rss')

    assert 'test_feed' in manager.feeds
    assert manager.feeds['test_feed'] is mock_feed
    mock_feed.download.assert_called_once()


def test_get_feed():
    """Test get_feed retrieves stored feed."""
    manager = FeedManager()
    mock_feed = MagicMock()
    manager.feeds['my_feed'] = mock_feed

    result = manager.get_feed('my_feed')

    assert result is mock_feed


def test_get_feed_unknown_returns_none():
    """Test get_feed returns None for unknown feed."""
    manager = FeedManager()

    result = manager.get_feed('nonexistent')

    assert result is None


@pytest.mark.asyncio
async def test_download_all():
    """Test download_all downloads all feeds concurrently."""
    manager = FeedManager()

    mock_feed1 = MagicMock()
    mock_feed1.download = AsyncMock()
    mock_feed2 = MagicMock()
    mock_feed2.download = AsyncMock()

    manager.feeds['feed1'] = mock_feed1
    manager.feeds['feed2'] = mock_feed2

    results = await manager.download_all()

    assert 'feed1' in results
    assert 'feed2' in results
    mock_feed1.download.assert_called_once()
    mock_feed2.download.assert_called_once()


@pytest.mark.asyncio
async def test_download_all_handles_exceptions():
    """Test download_all handles exceptions with return_exceptions=True."""
    manager = FeedManager()

    mock_feed_success = MagicMock()
    mock_feed_success.download = AsyncMock()

    mock_feed_fail = MagicMock()
    mock_feed_fail.download = AsyncMock(side_effect=Exception('Download failed'))

    manager.feeds['success'] = mock_feed_success
    manager.feeds['failure'] = mock_feed_fail

    results = await manager.download_all()

    # Should return results for both, with exception for failure
    assert 'success' in results
    assert 'failure' in results
    assert isinstance(results['failure'], Exception)


@pytest.mark.asyncio
@patch('agoras.core.feed.manager.Feed')
async def test_get_all_recent_items(mock_feed_class):
    """Test get_all_recent_items from multiple feeds."""
    manager = FeedManager()

    now = datetime.datetime.now()
    recent_date = now - datetime.timedelta(seconds=1800)

    # Create mock feeds with items
    feed1 = MagicMock()
    feed1.get_items_since = MagicMock(return_value=[
        create_mock_feed_item('Feed1 Item', pub_date=recent_date)
    ])

    feed2 = MagicMock()
    feed2.get_items_since = MagicMock(return_value=[
        create_mock_feed_item('Feed2 Item', pub_date=recent_date)
    ])

    manager.feeds['feed1'] = feed1
    manager.feeds['feed2'] = feed2

    items = manager.get_all_recent_items(3600)

    assert len(items) == 2
    # Items should be tuples of (feed_name, item)
    assert items[0][0] in ['feed1', 'feed2']
    assert isinstance(items[0][1], FeedItem)


@pytest.mark.asyncio
@patch('agoras.core.feed.manager.Feed')
async def test_get_random_item_from_any_feed(mock_feed_class):
    """Test get_random_item_from_any_feed returns random item."""
    manager = FeedManager()

    feed1 = MagicMock()
    feed1.items = [create_mock_feed_item('Item 1')]

    manager.feeds['feed1'] = feed1

    result = manager.get_random_item_from_any_feed()

    assert result is not None
    assert isinstance(result, tuple)
    assert result[0] == 'feed1'
    assert isinstance(result[1], FeedItem)


@pytest.mark.asyncio
@patch('agoras.core.feed.manager.Feed')
async def test_get_random_item_from_any_feed_with_max_age(mock_feed_class):
    """Test get_random_item_from_any_feed with max_age filters items."""
    manager = FeedManager()

    now = datetime.datetime.now()
    recent_date = now - datetime.timedelta(days=5)

    feed1 = MagicMock()
    feed1.get_items_within_days = MagicMock(return_value=[
        create_mock_feed_item('Recent Item', pub_date=recent_date)
    ])

    manager.feeds['feed1'] = feed1

    result = manager.get_random_item_from_any_feed(max_age_days=7)

    assert result is not None
    feed1.get_items_within_days.assert_called_once_with(7)


def test_get_random_item_from_any_feed_no_items():
    """Test get_random_item_from_any_feed returns None when no items."""
    manager = FeedManager()

    feed1 = MagicMock()
    feed1.items = []

    manager.feeds['feed1'] = feed1

    result = manager.get_random_item_from_any_feed()

    assert result is None


@pytest.mark.asyncio
@patch('agoras.core.feed.manager.Feed')
async def test_get_random_item_from_any_feed_handles_exceptions(mock_feed_class):
    """Test get_random_item_from_any_feed handles feed exceptions."""
    manager = FeedManager()

    feed_fail = MagicMock()
    feed_fail.items = MagicMock(side_effect=Exception('Feed error'))

    feed_ok = MagicMock()
    feed_ok.items = [create_mock_feed_item('OK Item')]

    manager.feeds['fail'] = feed_fail
    manager.feeds['ok'] = feed_ok

    result = manager.get_random_item_from_any_feed()

    # Should skip failed feed and return from ok feed
    assert result is not None
    assert result[0] == 'ok'
