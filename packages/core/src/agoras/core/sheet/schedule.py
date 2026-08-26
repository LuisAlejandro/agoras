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
"""agoras.core.sheet.schedule module."""

import datetime

from dateutil import parser

from .sheet import Sheet


class ScheduleSheet(Sheet):
    """
    Specialized sheet class for social media scheduling.

    Provides methods specifically for handling scheduled posts with
    automatic state management and date/time processing.
    """

    def __init__(self, sheet_id, client_email, private_key, sheet_name=None):
        """Initialize schedule sheet."""
        super().__init__(sheet_id, client_email, private_key, sheet_name)

    async def process_scheduled_posts(self, max_count=None):
        """
        Select due scheduled posts without marking them published.

        Rows are left unpublished here so callers can mark published only
        after a successful post (avoids ghost "published" on failure).

        Args:
            max_count (int, optional): Maximum number of posts to select

        Returns:
            list: List of posts ready for publishing. Each dict includes
                ``_sheet_row`` (1-indexed worksheet row) for mark_as_published.
        """
        all_rows = await self.read_all(has_headers=False)
        current_time = datetime.datetime.now()

        posts_to_publish = []
        count = 0

        for row_index, row_data in enumerate(all_rows):
            if max_count and count >= max_count:
                break

            if len(row_data.data) < 9:
                # Skip rows that don't have enough columns
                continue

            (
                status_text,
                status_link,
                status_image_url_1,
                status_image_url_2,
                status_image_url_3,
                status_image_url_4,
                date,
                hour,
                state,
            ) = row_data.data[:9]

            # Skip already published posts
            if state == "published":
                continue

            try:
                # Parse the scheduled date
                row_date = parser.parse(date)
                normalized_current = parser.parse(current_time.strftime("%d-%m-%Y"))
                normalized_row = parser.parse(row_date.strftime("%d-%m-%Y"))

                # Skip past dates (not due / expired relative to today)
                if normalized_row < normalized_current:
                    continue

                # For today's posts, check the hour
                if (
                    current_time.strftime("%d-%m-%Y") == row_date.strftime("%d-%m-%Y")
                    and current_time.strftime("%H") != hour
                ):
                    continue

                # This post should be published (caller marks after success)
                sheet_row = row_index + 1  # gspread update_cell is 1-indexed
                post_data = {
                    "status_text": status_text,
                    "status_link": status_link,
                    "status_image_url_1": status_image_url_1,
                    "status_image_url_2": status_image_url_2,
                    "status_image_url_3": status_image_url_3,
                    "status_image_url_4": status_image_url_4,
                    "_sheet_row": sheet_row,
                }

                posts_to_publish.append(post_data)
                count += 1

            except Exception:
                # Skip rows with invalid dates
                continue

        return posts_to_publish

    async def mark_as_published(self, sheet_row):
        """
        Mark a schedule row as published after a successful post.

        Args:
            sheet_row (int): 1-indexed worksheet row number
        """
        # Column 9 is the state field (status_text…hour, state)
        await self.update_cell(sheet_row, 9, "published")
