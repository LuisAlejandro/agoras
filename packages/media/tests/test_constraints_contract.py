# -*- coding: utf-8 -*-

import pytest

from agoras.media.constraints import (
    IMAGE,
    REGISTRY_MEDIA_PLATFORM_KEYS,
    VIDEO,
    image_limits,
    resolve_platform,
    transfer_mode,
    video_limits,
)
from agoras.media.factory import MediaFactory


@pytest.mark.parametrize('alias,expected', [
    ('X', 'twitter'),
    ('x', 'twitter'),
    ('Discord', 'discord'),
    ('generic', 'generic'),
])
def test_resolve_platform(alias, expected):
    assert resolve_platform(alias) == expected


def test_registry_media_platform_keys_have_contract_rows():
    for platform in REGISTRY_MEDIA_PLATFORM_KEYS:
        assert platform in IMAGE or platform in VIDEO


def test_video_limits_discord():
    limits = video_limits('discord')
    assert limits.max_bytes == 8 * 1024 * 1024


def test_video_limits_x_alias():
    limits = video_limits('X')
    assert limits.max_bytes == 512 * 1024 * 1024


def test_transfer_mode_tiktok_image():
    assert transfer_mode('tiktok', 'image') == 'url_pull'


def test_transfer_mode_tiktok_video_defaults_upload():
    assert transfer_mode('tiktok', 'video') == 'upload_bytes'


def test_factory_video_matches_contract():
    video = MediaFactory.create_video('https://example.com/v.mp4', 'discord')
    assert video.max_size == video_limits('discord').max_bytes
    assert video.platform_key == 'discord'


def test_factory_video_x_uses_twitter_limits():
    video = MediaFactory.create_video('https://example.com/v.mp4', 'X')
    assert video.max_size == video_limits('twitter').max_bytes


def test_factory_image_linkedin_limits():
    image = MediaFactory.create_image('https://example.com/i.jpg', 'linkedin')
    assert image.constraints.max_bytes == 5 * 1024 * 1024


def test_video_limits_linkedin():
    limits = video_limits('linkedin')
    assert limits.max_bytes == 500 * 1024 * 1024
    assert limits.mime_types == frozenset({'video/mp4'})
