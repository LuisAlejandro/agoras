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

import asyncio
import datetime
import random
from urllib.request import Request, urlopen

from atoma import parse_rss_bytes

from agoras.common import __version__

from .item import FeedItem


class Feed:
    """
    RSS feed handler that centralizes feed operations.

    Provides methods for downloading, parsing, and processing RSS feeds
    with filtering and selection capabilities.
    """

    def __init__(self, url):
        """
        Initialize feed instance.

        Args:
            url (str): RSS feed URL
        """
        self.url = url
        self._feed_data = None
        self._items = None
        self._downloaded = False

    async def download(self):
        """
        Download and parse RSS feed asynchronously.

        Returns:
            Feed: Self for method chaining

        Raises:
            Exception: If feed URL is not provided or parsing fails
        """
        if self._downloaded:
            return self

        if not self.url:
            raise Exception('No feed URL provided.')

        def _sync_download():
            request = Request(url=self.url, headers={'User-Agent': f'Agoras/{__version__}'})
            return parse_rss_bytes(urlopen(request).read())

        self._feed_data = await asyncio.to_thread(_sync_download)
        self._items = [FeedItem(item) for item in self._feed_data.items]
        self._downloaded = True

        return self

    @property
    def items(self):
        """
        Get all feed items.

        Returns:
            list: List of FeedItem instances

        Raises:
            Exception: If feed hasn't been downloaded
        """
        if not self._downloaded:
            raise Exception('Feed must be downloaded before accessing items')
        return self._items or []

    @property
    def title(self):
        """Get feed title."""
        if not self._downloaded:
            raise Exception('Feed must be downloaded before accessing title')
        return getattr(self._feed_data, 'title', '') or ''

    @property
    def description(self):
        """Get feed description."""
        if not self._downloaded:
            raise Exception('Feed must be downloaded before accessing description')
        return getattr(self._feed_data, 'description', '') or ''

    def get_items_since(self, lookback_seconds):
        """
        Get items published within the lookback period.

        Args:
            lookback_seconds (int): Number of seconds to look back

        Returns:
            list: List of FeedItem instances within the time range
        """
        if not self._downloaded:
            raise Exception('Feed must be downloaded before filtering items')

        now = datetime.datetime.now()
        cutoff = now - datetime.timedelta(seconds=lookback_seconds)
        cutoff_timestamp = int(cutoff.strftime('%Y%m%d%H%M%S'))

        recent_items = []
        for item in self.items:
            if item.pub_date and item.timestamp is not None and item.timestamp >= cutoff_timestamp:
                recent_items.append(item)

        return recent_items

    def get_items_within_days(self, max_age_days):
        """
        Get items published within the specified number of days.

        Args:
            max_age_days (int): Maximum age in days

        Returns:
            list: List of FeedItem instances within the age range
        """
        if not self._downloaded:
            raise Exception('Feed must be downloaded before filtering items')

        now = datetime.datetime.now()
        cutoff = now - datetime.timedelta(days=max_age_days)
        cutoff_timestamp = int(cutoff.strftime('%Y%m%d%H%M%S'))

        valid_items = []
        for item in self.items:
            if item.pub_date and item.timestamp is not None and item.timestamp >= cutoff_timestamp:
                valid_items.append(item)

        return valid_items

    def get_random_item(self, max_age_days=None):
        """
        Get a random item from the feed.

        Args:
            max_age_days (int, optional): Maximum age in days. If None, no age filter.

        Returns:
            FeedItem: Random feed item

        Raises:
            Exception: If no items are available
        """
        if not self._downloaded:
            raise Exception('Feed must be downloaded before selecting items')

        available_items = self.items

        if max_age_days is not None:
            available_items = self.get_items_within_days(max_age_days)

        if not available_items:
            raise Exception('No suitable items found in feed')

        return random.choice(available_items)

    def get_latest_items(self, count=1):
        """
        Get the most recent items from the feed.

        Args:
            count (int): Number of items to return

        Returns:
            list: List of the most recent FeedItem instances
        """
        if not self._downloaded:
            raise Exception('Feed must be downloaded before selecting items')

        # Sort by publication date (newest first), handling None values
        items_with_dates = [item for item in self.items if item.pub_date]
        sorted_items = sorted(
            items_with_dates,
            key=lambda x: x.pub_date or datetime.datetime.min,
            reverse=True
        )

        return sorted_items[:count]

    def filter_items(self, title_contains=None, has_image=None, custom_filter=None):
        """
        Filter items based on various criteria.

        Args:
            title_contains (str, optional): Filter by title content
            has_image (bool, optional): Filter by presence of image
            custom_filter (callable, optional): Custom filter function

        Returns:
            list: List of filtered FeedItem instances
        """
        if not self._downloaded:
            raise Exception('Feed must be downloaded before filtering items')

        filtered_items = self.items

        if title_contains:
            filtered_items = [
                item for item in filtered_items
                if title_contains.lower() in item.title.lower()
            ]

        if has_image is not None:
            if has_image:
                filtered_items = [item for item in filtered_items if item.image_url]
            else:
                filtered_items = [item for item in filtered_items if not item.image_url]

        if custom_filter:
            filtered_items = [item for item in filtered_items if custom_filter(item)]

        return filtered_items

    def to_dict(self):
        """
        Convert feed to dictionary representation.

        Returns:
            dict: Feed data including items
        """
        if not self._downloaded:
            raise Exception('Feed must be downloaded before converting to dict')

        return {
            'url': self.url,
            'title': self.title,
            'description': self.description,
            'item_count': len(self.items),
            'items': [item.to_dict() for item in self.items]
        }
