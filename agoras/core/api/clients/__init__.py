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

"""
API Clients Package

This package contains specialized HTTP clients for different social media platforms.
Each client handles the platform-specific API communication, request formatting,
and response parsing.
"""

from .instagram import InstagramAPIClient
from .linkedin import LinkedInAPIClient
from .threads import ThreadsAPIClient
from .tiktok import TikTokAPIClient
from .twitter import TwitterAPIClient
from .youtube import YouTubeAPIClient

__all__ = [
    'InstagramAPIClient',
    'LinkedInAPIClient',
    'ThreadsAPIClient',
    'TikTokAPIClient',
    'TwitterAPIClient',
    'YouTubeAPIClient']
