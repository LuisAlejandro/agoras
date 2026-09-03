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
Tests for ParameterConverter.
"""

from argparse import Namespace

import pytest

from agoras.cli.converter import ParameterConverter


def test_convert_x_to_legacy():
    """Test X parameter conversion to legacy format."""
    converter = ParameterConverter('x')
    args = Namespace(
        action='post',
        consumer_key='key123',
        consumer_secret='secret456',
        oauth_token='token789',
        oauth_secret='oauth012',
        text='Hello World',
        image_1='http://example.com/img.jpg',
        handler=None
    )

    legacy = converter.convert_to_legacy(args)

    assert legacy['network'] == 'x'
    assert legacy['action'] == 'post'
    assert legacy['twitter_consumer_key'] == 'key123'
    assert legacy['twitter_consumer_secret'] == 'secret456'
    assert legacy['twitter_oauth_token'] == 'token789'
    assert legacy['twitter_oauth_secret'] == 'oauth012'
    assert legacy['status_text'] == 'Hello World'
    assert legacy['status_image_url_1'] == 'http://example.com/img.jpg'


def test_convert_twitter_to_legacy():
    """Test Twitter alias parameter conversion to legacy format (backward compatibility)."""
    converter = ParameterConverter('twitter')
    args = Namespace(
        action='post',
        consumer_key='key123',
        consumer_secret='secret456',
        oauth_token='token789',
        oauth_secret='oauth012',
        text='Hello World',
        image_1='http://example.com/img.jpg',
        handler=None
    )

    legacy = converter.convert_to_legacy(args)

    # Twitter alias should convert to same legacy format as X
    assert legacy['network'] == 'twitter'
    assert legacy['action'] == 'post'
    assert legacy['twitter_consumer_key'] == 'key123'
    assert legacy['twitter_consumer_secret'] == 'secret456'
    assert legacy['twitter_oauth_token'] == 'token789'
    assert legacy['twitter_oauth_secret'] == 'oauth012'
    assert legacy['status_text'] == 'Hello World'
    assert legacy['status_image_url_1'] == 'http://example.com/img.jpg'


def test_convert_facebook_to_legacy():
    """Test Facebook parameter conversion to legacy format."""
    converter = ParameterConverter('facebook')
    args = Namespace(
        action='video',
        object_id='page456',
        video_url='http://example.com/video.mp4',
        video_title='My Video',
        handler=None
    )

    legacy = converter.convert_to_legacy(args)

    assert legacy['network'] == 'facebook'
    assert legacy['action'] == 'video'
    assert legacy['facebook_object_id'] == 'page456'
    assert legacy['facebook_video_url'] == 'http://example.com/video.mp4'
    assert legacy['facebook_video_title'] == 'My Video'


def test_convert_youtube_to_legacy():
    """Test YouTube parameter conversion with special fields."""
    converter = ParameterConverter('youtube')
    args = Namespace(
        action='video',
        client_id='client123',
        client_secret='secret456',
        video_url='video.mp4',
        title='Video Title',
        description='Video Description',
        privacy='public',
        handler=None
    )

    legacy = converter.convert_to_legacy(args)

    assert legacy['youtube_client_id'] == 'client123'
    assert legacy['youtube_title'] == 'Video Title'
    assert legacy['youtube_description'] == 'Video Description'
    assert legacy['youtube_privacy_status'] == 'public'


def test_convert_all_platforms():
    """Test that all platforms have working converters."""
    platforms = ['x', 'twitter', 'facebook', 'instagram', 'linkedin',
                 'discord', 'youtube', 'tiktok', 'threads', 'telegram', 'whatsapp']

    for platform in platforms:
        converter = ParameterConverter(platform)
        assert converter.platform == platform
        assert isinstance(converter.platform_mapping, dict)


def test_convert_linkedin_reply_to_legacy():
    """Test LinkedIn reply conversion maps post_id and text to native params."""
    converter = ParameterConverter('linkedin')
    args = Namespace(
        action='reply',
        post_id='urn:li:activity:123',
        text='A comment',
        handler=None
    )

    legacy = converter.convert_to_legacy(args)

    assert legacy['network'] == 'linkedin'
    assert legacy['action'] == 'reply'
    assert legacy['linkedin_post_id'] == 'urn:li:activity:123'
    assert legacy['status_text'] == 'A comment'


def test_convert_x_reply_to_legacy():
    """Test X reply conversion maps post_id and text to native params."""
    converter = ParameterConverter('x')
    args = Namespace(
        action='reply',
        post_id='tweet123',
        text='A reply',
        handler=None
    )

    legacy = converter.convert_to_legacy(args)

    assert legacy['network'] == 'x'
    assert legacy['action'] == 'reply'
    assert legacy['tweet_id'] == 'tweet123'
    assert legacy['status_text'] == 'A reply'


def test_convert_threads_reply_media_to_legacy():
    """Test Threads reply conversion maps post_id, text, and media to native params."""
    converter = ParameterConverter('threads')
    args = Namespace(
        action='reply',
        post_id='post123',
        text='A reply',
        image_1='http://example.com/a.jpg',
        video_url='http://example.com/v.mp4',
        handler=None,
    )

    legacy = converter.convert_to_legacy(args)

    assert legacy['network'] == 'threads'
    assert legacy['action'] == 'reply'
    assert legacy['threads_post_id'] == 'post123'
    assert legacy['status_text'] == 'A reply'
    assert legacy['status_image_url_1'] == 'http://example.com/a.jpg'
    assert legacy['threads_video_url'] == 'http://example.com/v.mp4'


def test_convert_facebook_reply_media_to_legacy():
    """Test Facebook reply conversion maps post_id, text, and image to native params."""
    converter = ParameterConverter('facebook')
    args = Namespace(
        action='reply',
        post_id='post123',
        text='A comment',
        image_1='http://example.com/a.jpg',
        handler=None,
    )

    legacy = converter.convert_to_legacy(args)

    assert legacy['network'] == 'facebook'
    assert legacy['action'] == 'reply'
    assert legacy['facebook_post_id'] == 'post123'
    assert legacy['status_text'] == 'A comment'
    assert legacy['status_image_url_1'] == 'http://example.com/a.jpg'


def test_convert_linkedin_reply_media_to_legacy():
    """Test LinkedIn reply conversion maps post_id, text, and image to native params."""
    converter = ParameterConverter('linkedin')
    args = Namespace(
        action='reply',
        post_id='urn:li:activity:123',
        text='A comment',
        image_1='http://example.com/a.jpg',
        handler=None,
    )

    legacy = converter.convert_to_legacy(args)

    assert legacy['network'] == 'linkedin'
    assert legacy['action'] == 'reply'
    assert legacy['linkedin_post_id'] == 'urn:li:activity:123'
    assert legacy['status_text'] == 'A comment'
    assert legacy['status_image_url_1'] == 'http://example.com/a.jpg'


def test_convert_linkedin_get_reply_parent_post_id():
    """Test LinkedIn get-reply maps parent_post_id to linkedin_parent_post_id."""
    converter = ParameterConverter('linkedin')
    args = Namespace(
        action='get-reply',
        post_id='comment123',
        parent_post_id='urn:li:ugcPost:456',
        handler=None,
    )

    legacy = converter.convert_to_legacy(args)

    assert legacy['network'] == 'linkedin'
    assert legacy['action'] == 'get-reply'
    assert legacy['linkedin_post_id'] == 'comment123'
    assert legacy['linkedin_parent_post_id'] == 'urn:li:ugcPost:456'


def test_convert_instagram_reply_to_legacy():
    """Test Instagram reply conversion maps post_id and text to native params."""
    converter = ParameterConverter('instagram')
    args = Namespace(
        action='reply',
        post_id='media123',
        text='A comment',
        handler=None,
    )

    legacy = converter.convert_to_legacy(args)

    assert legacy['network'] == 'instagram'
    assert legacy['action'] == 'reply'
    assert legacy['instagram_post_id'] == 'media123'
    assert legacy['status_text'] == 'A comment'


def test_convert_youtube_reply_to_legacy():
    """Test YouTube reply conversion maps video_id and text to native params."""
    converter = ParameterConverter('youtube')
    args = Namespace(
        action='reply',
        video_id='video123',
        text='A comment',
        handler=None,
    )

    legacy = converter.convert_to_legacy(args)

    assert legacy['network'] == 'youtube'
    assert legacy['action'] == 'reply'
    assert legacy['youtube_video_id'] == 'video123'
    assert legacy['status_text'] == 'A comment'


