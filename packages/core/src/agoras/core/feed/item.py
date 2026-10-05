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
"""agoras.core.feed.item module."""

import datetime
from html import unescape

from agoras.common.utils import add_url_timestamp


class FeedItem:
    """
    Represents a single item from an RSS feed.

    Provides convenient access to common feed item properties.
    """

    def __init__(self, item):
        """
        Initialize feed item from RSS item.

        Args:
            item: Parsed RSS item from the feed parser
        """
        self.raw_item = item
        self._processed = False
        self._title = None
        self._link = None
        self._pub_date = None
        self._image_url = None

    @property
    def title(self):
        """Get cleaned title."""
        if not self._processed:
            self._process_item()
        return self._title or ""

    @property
    def link(self):
        """Get link URL."""
        if not self._processed:
            self._process_item()
        return self._link or ""

    @property
    def pub_date(self):
        """Get publication date."""
        if not self._processed:
            self._process_item()
        return self._pub_date

    @property
    def image_url(self):
        """Get image URL from enclosures."""
        if not self._processed:
            self._process_item()
        return self._image_url or ""

    def _process_item(self):
        """Process raw RSS item into cleaned properties."""
        if self._processed:
            return

        # Clean title
        if self.raw_item.title:
            self._title = unescape(self.raw_item.title)

        # Get link
        self._link = self.raw_item.link or self.raw_item.guid or ""

        # Get publication date
        self._pub_date = self.raw_item.pub_date

        # Get image URL from enclosures
        try:
            if self.raw_item.enclosures and len(self.raw_item.enclosures) > 0:
                self._image_url = self.raw_item.enclosures[0].url
        except (AttributeError, IndexError):
            pass

        self._processed = True

    def get_timestamped_link(self, timestamp=None):
        """
        Get link with timestamp parameter.

        Args:
            timestamp (str, optional): Timestamp to add. If None, uses current time.

        Returns:
            str: Link with timestamp parameter
        """
        if not self.link:
            return ""

        if timestamp is None:
            timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")

        return add_url_timestamp(self.link, timestamp)
