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

"""
agoras.common.utils.

This module contains common and low level functions to all modules in agoras.
"""

import re
from html.parser import HTMLParser
from urllib.parse import parse_qs, urlencode, urlparse

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


def add_url_timestamp(url, timestamp):
    """Append a cache-busting timestamp query parameter to a URL."""
    parsed = urlparse(url)
    query = dict(parse_qs(str(parsed.query)))
    query["t"] = timestamp
    parsed = parsed._replace(query=urlencode(query))
    return parsed.geturl()


def metatag(tag):
    """Return whether a tag (duck-typed: name + has_attr) is a content-bearing meta tag."""
    return tag.name == "meta" and tag.has_attr("content") and (tag.has_attr("property") or tag.has_attr("name"))


class _MetaTagParser(HTMLParser):
    """Collect content-bearing meta tags from an HTML document."""

    def __init__(self):
        super().__init__()
        self.meta_tags = []

    def handle_starttag(self, tag, attrs):
        if tag == "meta":
            attrs_dict = dict(attrs)
            if metatag(_MetaTag(attrs_dict)):
                self.meta_tags.append(attrs_dict)


class _MetaTag:
    """Minimal tag stand-in for the metatag filter."""

    def __init__(self, attrs):
        self.name = "meta"
        self._attrs = attrs

    def has_attr(self, key):
        return key in self._attrs


def build_upload_session(max_attempts, retry_statuses, allowed_methods):
    """
    Build a requests session whose upload retries match the hand-rolled loops this replaces.

    Response-status retries only (the given 429/5xx set): connect and read
    retries are disabled so non-idempotent full-body uploads never re-send
    on a lost connection, and Retry-After headers are ignored. ``raise_on_status``
    is False so retry exhaustion returns the last response and callers surface
    the real HTTP status themselves. Note urllib3's backoff (1s, 2s, 4s, ...)
    is unbounded, so parity with the old min(2**(n-1), 4) cap holds exactly
    at the current 3-attempt constants and only there.
    """
    retry = Retry(
        total=max_attempts - 1,
        connect=0,
        read=0,
        status=max_attempts - 1,
        status_forcelist=sorted(retry_statuses),
        allowed_methods=allowed_methods,
        backoff_factor=1.0,
        respect_retry_after_header=False,
        raise_on_status=False,
    )
    session = requests.Session()
    session.mount("https://", HTTPAdapter(max_retries=retry))
    return session


def _decode_html_content(content):
    """
    Decode HTML bytes for parsing.

    Meta-charset declaration wins (the BeautifulSoup behavior this
    replaces); otherwise UTF-8 with replacement, never the ISO-8859-1
    default requests would apply to charset-less text/html.
    """
    head = content[:2048]
    match = re.search(rb"<meta[^>]+charset=[\"']?([a-zA-Z0-9_\-:]+)", head, re.I)
    if match:
        try:
            return content.decode(match.group(1).decode("ascii"))
        except (LookupError, UnicodeDecodeError):
            pass
    return content.decode("utf-8", errors="replace")


def find_metatags(url, search):
    """Fetch a URL and return matching Open Graph or Twitter meta tag values."""
    found = {}

    response = requests.get(url, timeout=20)

    if response.status_code != 200:
        return found

    parser = _MetaTagParser()
    parser.feed(_decode_html_content(response.content))

    for target in search:
        for meta_tag in parser.meta_tags:
            prop = meta_tag.get("property", "")
            name = meta_tag.get("name", "")

            if prop == target or name == target:
                found[target] = meta_tag.get("content", "")

    return found


def parse_metatags(url):
    """Parse common social preview meta tags from a URL."""
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
