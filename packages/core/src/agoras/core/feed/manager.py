# -*- coding: utf-8 -*-
#
# Please refer to AUTHORS.md for a complete list of Copyright holders.
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

import asyncio
import datetime
import random

from .feed import Feed


class FeedManager:
    """
    Manager class for handling multiple feeds.
    """

    def __init__(self):
        """Initialize feed manager."""
        self.feeds = {}

    async def add_feed(self, name, url):
        """
        Add and download a feed.

        Args:
            name (str): Feed identifier
            url (str): RSS feed URL

        Returns:
            Feed: Downloaded feed instance
        """
        feed = Feed(url)
        await feed.download()
        self.feeds[name] = feed
        return feed

    def get_feed(self, name):
        """
        Get feed by name.

        Args:
            name (str): Feed identifier

        Returns:
            Feed: Feed instance or None if not found
        """
        return self.feeds.get(name)

    async def download_all(self):
        """
        Download all feeds concurrently.

        Returns:
            dict: Dictionary of feed names to download results
        """
        download_tasks = []
        feed_names = []

        for name, feed in self.feeds.items():
            download_tasks.append(feed.download())
            feed_names.append(name)

        results = await asyncio.gather(*download_tasks, return_exceptions=True)
        return dict(zip(feed_names, results))

    def get_all_recent_items(self, lookback_seconds):
        """
        Get recent items from all feeds.

        Args:
            lookback_seconds (int): Lookback period in seconds

        Returns:
            list: List of tuples (feed_name, FeedItem)
        """
        all_items = []
        for name, feed in self.feeds.items():
            recent_items = feed.get_items_since(lookback_seconds)
            for item in recent_items:
                all_items.append((name, item))

        # Sort by publication date (newest first)
        all_items.sort(key=lambda x: x[1].pub_date or datetime.datetime.min, reverse=True)
        return all_items

    def get_random_item_from_any_feed(self, max_age_days=None):
        """
        Get a random item from any feed.

        Args:
            max_age_days (int, optional): Maximum age in days

        Returns:
            tuple: (feed_name, FeedItem) or None if no items available
        """
        all_items = []

        for name, feed in self.feeds.items():
            try:
                if max_age_days is not None:
                    items = feed.get_items_within_days(max_age_days)
                else:
                    items = feed.items

                for item in items:
                    all_items.append((name, item))
            except Exception:
                continue

        if not all_items:
            return None

        return random.choice(all_items)
