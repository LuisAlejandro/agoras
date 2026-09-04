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
from unittest.mock import MagicMock, patch

import pytest

from agoras.core.feed import Feed, FeedItem

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


@pytest.mark.asyncio
@patch('agoras.core.feed.feed.urlopen')
@patch('agoras.core.feed.feed.parse_rss_bytes')
async def test_get_items_since_handles_tz_aware_and_none_dates(mock_parse, mock_urlopen):
    """Test get_items_since handles tz-aware and None pub_dates without TypeError.

    Comparison is by wall time (tz is stripped, matching the historic
    int-encoded behavior), so tz-aware fixtures are anchored to local wall
    time to stay deterministic on any host TZ.
    """
    mock_response = MagicMock()
    mock_response.read.return_value = b'<rss></rss>'
    mock_urlopen.return_value = mock_response

    naive_now = datetime.datetime.now()
    mock_item_recent = MagicMock()
    mock_item_recent.pub_date = (naive_now - datetime.timedelta(seconds=1800)).replace(
        tzinfo=datetime.timezone.utc
    )
    mock_item_old = MagicMock()
    mock_item_old.pub_date = (naive_now - datetime.timedelta(seconds=7200)).replace(
        tzinfo=datetime.timezone.utc
    )
    mock_item_none = MagicMock()
    mock_item_none.pub_date = None

    mock_feed_data = MagicMock()
    mock_feed_data.items = [mock_item_recent, mock_item_old, mock_item_none]
    mock_parse.return_value = mock_feed_data

    feed = Feed('http://feed.rss')
    await feed.download()

    recent_items = feed.get_items_since(3600)

    assert len(recent_items) == 1
    assert recent_items[0].pub_date == mock_item_recent.pub_date


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


# Latest Items Tests


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




def test_parse_rss_bytes_happy_path():
    """Real RSS 2.0 fixture parses to the same item fields."""
    from agoras.core.feed.feed import parse_rss_bytes

    rss = b"""<?xml version="1.0"?>
<rss version="2.0"><channel>
  <title>Test Feed</title><description>Feed Desc</description>
  <item>
    <title>Item One</title><link>https://a.example/1</link>
    <guid>https://a.example/1</guid><description>Body</description>
    <pubDate>Tue, 02 Oct 2024 13:00:00 GMT</pubDate>
    <enclosure url="https://a.example/img.jpg" type="image/jpeg"/>
  </item>
</channel></rss>"""
    feed = parse_rss_bytes(rss)
    assert feed.title == "Test Feed"
    assert feed.description == "Feed Desc"
    assert len(feed.items) == 1
    item = feed.items[0]
    assert item.title == "Item One"
    assert item.link == "https://a.example/1"
    assert item.description == "Body"
    assert item.pub_date is not None
    assert item.pub_date.tzinfo is not None
    assert item.enclosures[0].url == "https://a.example/img.jpg"

    parsed = FeedItem(item)
    assert parsed.title == "Item One"
    assert parsed.link == "https://a.example/1"
    assert parsed.timestamp is not None
    assert parsed.image_url == "https://a.example/img.jpg"


def test_parse_rss_bytes_iso8601_date_and_garbage():
    """ISO-8601 pubDates parse via fallback; garbage yields pub_date None."""
    from agoras.core.feed.feed import parse_rss_bytes

    rss = b"""<?xml version="1.0"?>
<rss version="2.0"><channel><title>t</title>
  <item><title>a</title><pubDate>2024-10-02T13:00:00Z</pubDate></item>
  <item><title>b</title><pubDate>not a date at all</pubDate></item>
</channel></rss>"""
    feed = parse_rss_bytes(rss)
    assert feed.items[0].pub_date is not None
    assert feed.items[0].pub_date.tzinfo is not None
    assert feed.items[1].pub_date is None


def test_parse_rss_bytes_naive_dates_normalized_and_sort_safe():
    """Mixed naive/aware pubDates sort without TypeError."""
    from agoras.core.feed.feed import parse_rss_bytes

    rss = b"""<?xml version="1.0"?>
<rss version="2.0"><channel><title>t</title>
  <item><title>a</title><pubDate>Tue, 02 Oct 2024 13:00:00 GMT</pubDate></item>
  <item><title>b</title><pubDate>Wed, 02 Oct 2024 13:00:00</pubDate></item>
</channel></rss>"""
    feed = parse_rss_bytes(rss)
    items = [FeedItem(i) for i in feed.items]
    sorted_items = sorted(items, key=lambda x: x.pub_date or datetime.datetime.min, reverse=True)
    assert len(sorted_items) == 2
    assert sorted_items[0].title == "a"


def test_parse_rss_bytes_rejects_entities():
    """Feeds with entity definitions are rejected before parsing."""
    from agoras.core.feed.feed import FeedParseError, parse_rss_bytes

    rss = b'<?xml version="1.0"?><!DOCTYPE rss [<!ENTITY x "y">]><rss/>'
    with pytest.raises(FeedParseError):
        parse_rss_bytes(rss)


def test_parse_rss_bytes_accepts_entity_less_doctype():
    """Entity-less DOCTYPE declarations (legacy RSS 0.91) still parse."""
    from agoras.core.feed.feed import parse_rss_bytes

    rss = b'<?xml version="1.0"?><!DOCTYPE rss><rss version="2.0"><channel><title>t</title></channel></rss>'
    feed = parse_rss_bytes(rss)
    assert feed.title == "t"


def test_parse_rss_bytes_rejects_utf16_entities():
    """UTF-16 encoded entity feeds cannot evade the rejection."""
    from agoras.core.feed.feed import FeedParseError, parse_rss_bytes

    rss = '<?xml version="1.0" encoding="UTF-16"?><!DOCTYPE rss [<!ENTITY x "y">]><rss/>'.encode("utf-16")
    with pytest.raises(FeedParseError):
        parse_rss_bytes(rss)


def test_parse_rss_bytes_invalid_xml_raises():
    """Malformed XML raises FeedParseError (per-feed isolation preserved)."""
    from agoras.core.feed.feed import FeedParseError, parse_rss_bytes

    with pytest.raises(FeedParseError):
        parse_rss_bytes(b"<rss><channel>")


def test_parse_rss_bytes_strips_padded_text():
    """Whitespace-padded element text is stripped (atoma parity)."""
    from agoras.core.feed.feed import parse_rss_bytes

    rss = b"""<?xml version="1.0"?>
<rss version="2.0"><channel><title>  Padded  </title>
  <item><title>  Item  </title><link>  https://a.example/1  </link></item>
</channel></rss>"""
    feed = parse_rss_bytes(rss)
    assert feed.title == "Padded"
    assert feed.items[0].title == "Item"
    assert feed.items[0].link == "https://a.example/1"


def test_parse_rss_bytes_ampm_date():
    """AM/PM pubDates parse with the correct 12-hour shift."""
    from agoras.core.feed.feed import parse_rss_bytes

    rss = b"""<?xml version="1.0"?>
<rss version="2.0"><channel><title>t</title>
  <item><title>a</title><pubDate>Tue, 02 Oct 2024 1:30:00 PM GMT</pubDate></item>
</channel></rss>"""
    feed = parse_rss_bytes(rss)
    assert feed.items[0].pub_date is not None
    assert feed.items[0].pub_date.hour == 13
    assert feed.items[0].pub_date.tzinfo is not None


def test_parse_rss_bytes_entity_marker_in_comment_not_rejected():
    """A comment merely mentioning <!ENTITY is not an entity definition."""
    from agoras.core.feed.feed import parse_rss_bytes

    rss = b"""<?xml version="1.0"?>
<rss version="2.0"><channel><title>t</title>
  <item><title>a</title><description><!-- this doc mentions <!ENTITY in prose -->body</description></item>
</channel></rss>"""
    feed = parse_rss_bytes(rss)
    assert len(feed.items) == 1
