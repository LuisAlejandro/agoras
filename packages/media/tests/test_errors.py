# -*- coding: utf-8 -*-

from agoras.media.errors import MediaValidationError, format_limit_error


def test_format_limit_error_mime_types():
    msg = format_limit_error('discord', 'video', 'mime_types', 'video/avi', ['video/mp4'])
    assert 'discord' in msg
    assert 'video/avi' in msg
    assert 'video/mp4' in msg


def test_format_limit_error_max_bytes():
    msg = format_limit_error('discord', 'video', 'max_bytes', 20_000_000, 8_388_608)
    assert '20' in msg
    assert '8388608' in msg


def test_media_validation_error_attributes():
    err = MediaValidationError('twitter', 'video', 'max_bytes', 100, 50)
    assert err.platform == 'twitter'
    assert err.kind == 'video'
    assert err.field == 'max_bytes'
    assert '100' in str(err)
