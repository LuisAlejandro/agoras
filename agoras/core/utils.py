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

"""

agoras.common.utils
===================

This module contains common and low level functions to all modules in agoras.

"""


from urllib.parse import parse_qs, urlencode, urlparse

import requests
from bs4 import BeautifulSoup


def add_url_timestamp(url, timestamp):
    parsed = urlparse(url)
    query = dict(parse_qs(str(parsed.query)))
    query['t'] = timestamp
    parsed = parsed._replace(query=urlencode(query))
    return parsed.geturl()


def metatag(tag):
    return tag.name == "meta" \
        and tag.has_attr("content") \
        and (tag.has_attr("property") or tag.has_attr("name"))


def find_metatags(url, search):
    found = {}

    response = requests.get(url, timeout=20)

    if response.status_code != 200:
        return found

    soup = BeautifulSoup(response.content, 'html.parser')

    for target in search:
        found_meta_tag = soup.find_all(metatag)

        if not found_meta_tag:
            continue

        for meta_tag in found_meta_tag:

            prop = meta_tag.get("property", "")
            name = meta_tag.get("name", "")

            if prop == target or name == target:
                found[target] = meta_tag.get("content", "")

    return found


def parse_metatags(url):

    KNOWN_TAGS = [
        "og:title",
        "og:image",
        "og:description",
        "twitter:title",
        "twitter:image",
        "twitter:description",
    ]

    try:
        data = find_metatags(url, KNOWN_TAGS)
    except Exception:
        data = {}

    return {
        "title": data.get("og:title", data.get("twitter:title", "")),
        "image": data.get("og:image", data.get("twitter:image", "")),
        "description": data.get("og:description", data.get("twitter:description", "")),
    }
