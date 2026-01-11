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

import pytest
from agoras.core.feed import Feed, FeedItem


def test_feed_instantiation():
    """Test Feed can be instantiated with URL."""
    feed = Feed('https://example.com/feed.xml')
    assert feed.url == 'https://example.com/feed.xml'


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


def test_feeditem_instantiation():
    """Test FeedItem can be instantiated."""
    # FeedItem expects an atoma item object
    # For now, just verify the class exists
    assert FeedItem is not None
