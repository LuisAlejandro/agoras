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
        Process scheduled posts and update the sheet.

        Args:
            max_count (int, optional): Maximum number of posts to process

        Returns:
            list: List of posts ready for publishing
        """
        all_rows = await self.read_all(has_headers=False)
        current_time = datetime.datetime.now()

        posts_to_publish = []
        updated_rows = []
        count = 0

        for row_data in all_rows:
            if len(row_data.data) < 9:
                # Skip rows that don't have enough columns
                updated_rows.append(row_data.to_list())
                continue

            status_text, status_link, status_image_url_1, status_image_url_2, \
                status_image_url_3, status_image_url_4, \
                date, hour, state = row_data.data[:9]

            # Add row to updated list
            updated_row = [
                status_text, status_link, status_image_url_1, status_image_url_2,
                status_image_url_3, status_image_url_4,
                date, hour, state
            ]

            # Check if we've reached the limit
            if max_count and count >= max_count:
                updated_rows.append(updated_row)
                continue

            # Skip already published posts
            if state == 'published':
                updated_rows.append(updated_row)
                continue

            try:
                # Parse the scheduled date
                row_date = parser.parse(date)
                normalized_current = parser.parse(current_time.strftime('%d-%m-%Y'))
                normalized_row = parser.parse(row_date.strftime('%d-%m-%Y'))

                # Skip future dates
                if normalized_row < normalized_current:
                    updated_rows.append(updated_row)
                    continue

                # For today's posts, check the hour
                if (current_time.strftime('%d-%m-%Y') == row_date.strftime('%d-%m-%Y') and
                        current_time.strftime('%H') != hour):
                    updated_rows.append(updated_row)
                    continue

                # This post should be published
                post_data = {
                    'status_text': status_text,
                    'status_link': status_link,
                    'status_image_url_1': status_image_url_1,
                    'status_image_url_2': status_image_url_2,
                    'status_image_url_3': status_image_url_3,
                    'status_image_url_4': status_image_url_4
                }

                posts_to_publish.append(post_data)
                updated_row[-1] = 'published'  # Mark as published
                count += 1

            except Exception:
                # Skip rows with invalid dates
                pass

            updated_rows.append(updated_row)

        # Update the sheet with new states
        await self.write_all(updated_rows, clear_first=True)

        return posts_to_publish
