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


def test_convert_from_legacy_x():
    """Test converting legacy X args to new format."""
    converter = ParameterConverter('x')
    legacy_args = {
        'twitter_consumer_key': 'key123',
        'twitter_consumer_secret': 'secret456',
        'status_text': 'Test post',
        'status_image_url_1': 'img.jpg',
    }

    new_args = converter.convert_from_legacy(legacy_args)

    assert new_args['consumer_key'] == 'key123'
    assert new_args['consumer_secret'] == 'secret456'
    assert new_args['text'] == 'Test post'
    assert new_args['image_1'] == 'img.jpg'


def test_convert_from_legacy_twitter():
    """Test converting legacy Twitter args to new format (backward compatibility)."""
    converter = ParameterConverter('twitter')
    legacy_args = {
        'twitter_consumer_key': 'key123',
        'twitter_consumer_secret': 'secret456',
        'status_text': 'Test post',
        'status_image_url_1': 'img.jpg',
    }

    new_args = converter.convert_from_legacy(legacy_args)

    assert new_args['consumer_key'] == 'key123'
    assert new_args['consumer_secret'] == 'secret456'
    assert new_args['text'] == 'Test post'
    assert new_args['image_1'] == 'img.jpg'


def test_bidirectional_conversion_x():
    """Test that bidirectional conversion preserves values for X."""
    converter = ParameterConverter('x')

    # Start with new format
    original_args = Namespace(
        action='post',
        consumer_key='key123',
        text='Hello',
        handler=None
    )

    # Convert to legacy
    legacy = converter.convert_to_legacy(original_args)

    # Convert back to new
    new_again = converter.convert_from_legacy(legacy)

    # Values should be preserved
    assert new_again['consumer_key'] == 'key123'
    assert new_again['text'] == 'Hello'


def test_bidirectional_conversion_twitter():
    """Test that bidirectional conversion preserves values for Twitter alias."""
    converter = ParameterConverter('twitter')

    # Start with new format
    original_args = Namespace(
        action='post',
        consumer_key='key123',
        text='Hello',
        handler=None
    )

    # Convert to legacy
    legacy = converter.convert_to_legacy(original_args)

    # Convert back to new
    new_again = converter.convert_from_legacy(legacy)

    # Values should be preserved
    assert new_again['consumer_key'] == 'key123'
    assert new_again['text'] == 'Hello'


def test_validate_legacy_args_valid():
    """Test validation passes for valid legacy args."""
    converter = ParameterConverter('twitter')
    legacy_args = {'network': 'twitter', 'action': 'post'}

    # Should not raise
    converter.validate_legacy_args(legacy_args)


def test_validate_legacy_args_missing_network():
    """Test validation fails when network is missing."""
    converter = ParameterConverter('twitter')
    legacy_args = {'action': 'post'}

    with pytest.raises(ValueError) as exc_info:
        converter.validate_legacy_args(legacy_args)

    assert 'network' in str(exc_info.value).lower()


def test_validate_legacy_args_missing_action():
    """Test validation fails when action is missing."""
    converter = ParameterConverter('twitter')
    legacy_args = {'network': 'twitter'}

    with pytest.raises(ValueError) as exc_info:
        converter.validate_legacy_args(legacy_args)

    assert 'action' in str(exc_info.value).lower()


def test_get_unmapped_parameters():
    """Test detection of unmapped parameters."""
    converter = ParameterConverter('twitter')
    args = Namespace(
        action='post',
        consumer_key='key',
        unknown_param='value',
        handler=None
    )

    unmapped = converter.get_unmapped_parameters(args)

    assert 'unknown_param' in unmapped
    assert 'consumer_key' not in unmapped
    assert 'action' not in unmapped


def test_get_conversion_report():
    """Test conversion report generation."""
    converter = ParameterConverter('twitter')
    args = Namespace(
        action='post',
        consumer_key='key123',
        text='Hello',
        handler=None
    )

    report = converter.get_conversion_report(args)

    assert report['platform'] == 'twitter'
    assert report['action'] == 'post'
    assert len(report['platform_conversions']) > 0
    assert len(report['common_conversions']) > 0
    assert 'legacy_args' in report


def test_get_all_mappings():
    """Test getting all mapping information."""
    # Get all mappings
    all_mappings = ParameterConverter.get_all_mappings()

    assert 'all_platforms' in all_mappings
    assert 'common_mappings' in all_mappings
    assert 'x' in all_mappings['all_platforms']
    assert 'twitter' in all_mappings['all_platforms']  # Backward compatibility

    # Get specific platform
    x_mappings = ParameterConverter.get_all_mappings('x')

    assert x_mappings['platform'] == 'x'
    assert 'platform_mappings' in x_mappings
    assert 'consumer_key' in x_mappings['platform_mappings']

    # Get Twitter alias mappings
    twitter_mappings = ParameterConverter.get_all_mappings('twitter')

    assert twitter_mappings['platform'] == 'twitter'
    assert 'platform_mappings' in twitter_mappings
    assert 'consumer_key' in twitter_mappings['platform_mappings']


def test_convert_all_platforms():
    """Test that all platforms have working converters."""
    platforms = ['x', 'twitter', 'facebook', 'instagram', 'linkedin',
                 'discord', 'youtube', 'tiktok', 'threads']

    for platform in platforms:
        converter = ParameterConverter(platform)
        assert converter.platform == platform
        assert isinstance(converter.platform_mapping, dict)
