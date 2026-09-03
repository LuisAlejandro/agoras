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

import doctest
import sys
import unittest
from unittest.mock import Mock, patch

from agoras.common.utils import add_url_timestamp, find_metatags, metatag, parse_metatags


class TestAddUrlTimestamp(unittest.TestCase):
    """Tests for add_url_timestamp function."""

    def test_add_timestamp_to_url_without_query(self):
        """Test adding timestamp to URL without query parameters."""
        url = "https://example.com"
        timestamp = 12345
        result = add_url_timestamp(url, timestamp)
        self.assertIn("t=12345", result)
        self.assertTrue(result.startswith("https://example.com?"))

    def test_add_timestamp_to_url_with_existing_query(self):
        """Test adding timestamp to URL with existing query parameters."""
        url = "https://example.com?foo=bar"
        timestamp = 67890
        result = add_url_timestamp(url, timestamp)
        # parse_qs returns lists, so foo will be encoded as ['bar']
        self.assertIn("foo=", result)
        self.assertIn("t=67890", result)
        self.assertTrue(result.startswith("https://example.com?"))

    def test_replace_existing_timestamp(self):
        """Test replacing existing timestamp parameter."""
        url = "https://example.com?t=111&foo=bar"
        timestamp = 999
        result = add_url_timestamp(url, timestamp)
        self.assertIn("t=999", result)
        self.assertIn("foo=", result)
        self.assertNotIn("t=111", result)

    def test_url_with_fragment(self):
        """Test URL with fragment."""
        url = "https://example.com#section"
        timestamp = 55555
        result = add_url_timestamp(url, timestamp)
        self.assertIn("t=55555", result)
        self.assertIn("#section", result)


class _FakeMetaTag:
    """Minimal tag stand-in for testing the metatag filter."""

    def __init__(self, name, attrs):
        self.name = name
        self._attrs = attrs

    def has_attr(self, key):
        return key in self._attrs


class TestMetatag(unittest.TestCase):
    """Tests for metatag function."""

    def test_valid_meta_tag_with_property(self):
        """Test with valid meta tag that has property attribute."""
        tag = _FakeMetaTag("meta", {"property": "og:title", "content": "Test"})
        self.assertTrue(metatag(tag))

    def test_valid_meta_tag_with_name(self):
        """Test with valid meta tag that has name attribute."""
        tag = _FakeMetaTag("meta", {"name": "description", "content": "Test"})
        self.assertTrue(metatag(tag))

    def test_invalid_tag_not_meta(self):
        """Test with invalid tag (not meta)."""
        tag = _FakeMetaTag("div", {"content": "Test"})
        self.assertFalse(metatag(tag))

    def test_meta_tag_without_content(self):
        """Test with meta tag without content attribute."""
        tag = _FakeMetaTag("meta", {"property": "og:title"})
        self.assertFalse(metatag(tag))

    def test_meta_tag_without_property_or_name(self):
        """Test with meta tag without property or name attribute."""
        tag = _FakeMetaTag("meta", {"content": "Test"})
        self.assertFalse(metatag(tag))


class TestFindMetatags(unittest.TestCase):
    """Tests for find_metatags function."""

    @patch('agoras.common.utils.requests.get')
    def test_successful_meta_tag_extraction(self, mock_get):
        """Test successful meta tag extraction."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = '<html><meta property="og:title" content="My Title"></html>'
        mock_get.return_value = mock_response

        result = find_metatags('https://example.com', ['og:title'])
        self.assertEqual(result, {'og:title': 'My Title'})

    @patch('agoras.common.utils.requests.get')
    def test_multiple_meta_tags(self, mock_get):
        """Test extraction of multiple meta tags."""
        html = '''<html>
            <meta property="og:title" content="Title">
            <meta property="og:image" content="image.jpg">
            <meta name="twitter:description" content="Description">
        </html>'''
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = html
        mock_get.return_value = mock_response

        result = find_metatags('https://example.com',
                               ['og:title', 'og:image', 'twitter:description'])
        self.assertEqual(result['og:title'], 'Title')
        self.assertEqual(result['og:image'], 'image.jpg')
        self.assertEqual(result['twitter:description'], 'Description')

    @patch('agoras.common.utils.requests.get')
    def test_non_200_status_code(self, mock_get):
        """Test with non-200 status code."""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response

        result = find_metatags('https://example.com', ['og:title'])
        self.assertEqual(result, {})

    @patch('agoras.common.utils.requests.get')
    def test_html_without_matching_meta_tags(self, mock_get):
        """Test HTML without matching meta tags."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = '<html><p>No meta tags here</p></html>'
        mock_get.return_value = mock_response

        result = find_metatags('https://example.com', ['og:title'])
        self.assertEqual(result, {})

    @patch('agoras.common.utils.requests.get')
    def test_meta_tags_with_name_attribute(self, mock_get):
        """Test meta tags with name attribute."""
        html = '<html><meta name="twitter:title" content="Twitter Title"></html>'
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = html
        mock_get.return_value = mock_response

        result = find_metatags('https://example.com', ['twitter:title'])
        self.assertEqual(result, {'twitter:title': 'Twitter Title'})


class TestParseMetatags(unittest.TestCase):
    """Tests for parse_metatags function."""

    @patch('agoras.common.utils.find_metatags')
    def test_with_open_graph_tags(self, mock_find):
        """Test with Open Graph tags."""
        mock_find.return_value = {
            'og:title': 'OG Title',
            'og:image': 'og.jpg',
            'og:description': 'OG Desc'
        }

        result = parse_metatags('https://example.com')
        self.assertEqual(result, {
            'title': 'OG Title',
            'image': 'og.jpg',
            'description': 'OG Desc'
        })

    @patch('agoras.common.utils.find_metatags')
    def test_with_twitter_tags_fallback(self, mock_find):
        """Test with Twitter tags as fallback."""
        mock_find.return_value = {
            'twitter:title': 'Twitter Title',
            'twitter:image': 'twitter.jpg',
            'twitter:description': 'Twitter Desc'
        }

        result = parse_metatags('https://example.com')
        self.assertEqual(result, {
            'title': 'Twitter Title',
            'image': 'twitter.jpg',
            'description': 'Twitter Desc'
        })

    @patch('agoras.common.utils.find_metatags')
    def test_with_mixed_tags(self, mock_find):
        """Test with mixed OG and Twitter tags."""
        mock_find.return_value = {
            'og:title': 'OG Title',
            'twitter:image': 'twitter.jpg',
            'og:description': 'OG Desc'
        }

        result = parse_metatags('https://example.com')
        self.assertEqual(result['title'], 'OG Title')
        self.assertEqual(result['image'], 'twitter.jpg')
        self.assertEqual(result['description'], 'OG Desc')

    @patch('agoras.common.utils.find_metatags')
    def test_with_no_tags_found(self, mock_find):
        """Test with no tags found."""
        mock_find.return_value = {}

        result = parse_metatags('https://example.com')
        self.assertEqual(result, {
            'title': '',
            'image': '',
            'description': ''
        })

    @patch('agoras.common.utils.find_metatags')
    def test_exception_handling(self, mock_find):
        """Test exception handling."""
        mock_find.side_effect = Exception('Network error')

        result = parse_metatags('https://example.com')
        self.assertEqual(result, {
            'title': '',
            'image': '',
            'description': ''
        })


def load_tests(loader, tests, pattern):
    tests.addTests(doctest.DocTestSuite('agoras.common.utils'))
    return tests


if __name__ == '__main__':
    sys.exit(unittest.main())


class TestFindMetatagsParserEdgeCases(unittest.TestCase):
    """Parser edge cases: attribute order, case, malformed HTML."""

    @patch('agoras.common.utils.requests.get')
    def test_attribute_order_variation(self, mock_get):
        """Attribute order does not affect extraction."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = '<html><meta content="Ordered" property="og:title"></html>'
        mock_get.return_value = mock_response
        result = find_metatags('https://example.com', ['og:title'])
        self.assertEqual(result, {'og:title': 'Ordered'})

    @patch('agoras.common.utils.requests.get')
    def test_uppercase_attribute_names(self, mock_get):
        """Uppercase attribute names are lowercased by the parser."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = '<html><meta PROPERTY="og:title" CONTENT="Upper"></html>'
        mock_get.return_value = mock_response
        result = find_metatags('https://example.com', ['og:title'])
        self.assertEqual(result, {'og:title': 'Upper'})

    @patch('agoras.common.utils.requests.get')
    def test_malformed_html_does_not_raise(self, mock_get):
        """Malformed HTML parses without raising."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = '<html><meta property="og:title" content="Broken"<div>'
        mock_get.return_value = mock_response
        result = find_metatags('https://example.com', ['og:title'])
        self.assertEqual(result, {'og:title': 'Broken'})

    @patch('agoras.common.utils.requests.get')
    def test_meta_without_content_not_collected(self, mock_get):
        """Meta tags without content are ignored (metatag filter parity)."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = '<html><meta property="og:title"><meta property="og:image" content="img.jpg"></html>'
        mock_get.return_value = mock_response
        result = find_metatags('https://example.com', ['og:title', 'og:image'])
        self.assertEqual(result, {'og:image': 'img.jpg'})
