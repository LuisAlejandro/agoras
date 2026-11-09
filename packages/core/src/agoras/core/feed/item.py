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
from dataclasses import dataclass
from html import unescape
from typing import Optional

from agoras.common.utils import add_url_timestamp


@dataclass(frozen=True)
class _ParsedItem:
    """Cleaned fields extracted from one raw RSS item."""

    title: str
    link: str
    pub_date: Optional[datetime.datetime]
    image_url: str


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
        self._parsed: Optional[_ParsedItem] = None

    def _set_parsed(self, parsed):
        """Record the parsed fields. The only writer of the parsed value."""
        self._parsed = parsed

    @property
    def _processed(self) -> bool:
        """True once the raw item has been cleaned (derived, never stored)."""
        return self._parsed is not None

    def _field(self, name):
        """Return one parsed field, parsing the raw item on first access."""
        if self._parsed is None:
            self._process_item()
        return getattr(self._parsed, name)

    @property
    def title(self):
        """Get cleaned title."""
        return self._field("title")

    @property
    def link(self):
        """Get link URL."""
        return self._field("link")

    @property
    def pub_date(self):
        """Get publication date."""
        return self._field("pub_date")

    @property
    def image_url(self):
        """Get image URL from enclosures."""
        return self._field("image_url")

    def _process_item(self):
        """Process raw RSS item into cleaned properties."""
        if self._parsed is not None:
            return

        title = unescape(self.raw_item.title) if self.raw_item.title else ""
        link = self.raw_item.link or self.raw_item.guid or ""
        pub_date = self.raw_item.pub_date

        image_url = ""
        try:
            if self.raw_item.enclosures and len(self.raw_item.enclosures) > 0:
                image_url = self.raw_item.enclosures[0].url
        except (AttributeError, IndexError):
            pass

        self._set_parsed(
            _ParsedItem(
                title=title or "",
                link=link or "",
                pub_date=pub_date,
                image_url=image_url or "",
            )
        )

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
