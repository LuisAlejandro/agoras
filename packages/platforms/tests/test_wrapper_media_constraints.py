# -*- coding: utf-8 -*-

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from agoras.media.constraints import image_limits, video_limits
from agoras.media.errors import MediaValidationError
from agoras.platforms.facebook.wrapper import Facebook
from agoras.platforms.instagram.wrapper import Instagram
from agoras.platforms.linkedin.wrapper import LinkedIn
from agoras.platforms.threads.api import ThreadsAPI
from agoras.platforms.tiktok.wrapper import TikTok
from agoras.platforms.whatsapp.wrapper import WhatsApp
from agoras.platforms.x.wrapper import X
from agoras.platforms.youtube.wrapper import YouTube


def _mock_video(mime: str):
    video = MagicMock()
    video.content = b'video'
    video.file_type = MagicMock()
    video.file_type.mime = mime
    video.cleanup = MagicMock()
    return video


@pytest.mark.parametrize('wrapper_cls,platform_key,invalid_mime,setup,video_args', [
    (X, 'twitter', 'video/avi', lambda w: None, ('text', 'https://example.com/v', 'title')),
    (Facebook, 'facebook', 'video/webm',
     lambda w: setattr(w, 'facebook_object_id', 'page1'),
     ('desc', 'https://example.com/v', 'title')),
    (Instagram, 'instagram', 'video/webm',
     lambda w: setattr(w, 'instagram_object_id', 'ig1'),
     ('caption', 'https://example.com/v', 'title')),
    (YouTube, 'youtube', 'video/mpeg', lambda w: None, ('title', 'https://example.com/v', 'title')),
    (WhatsApp, 'whatsapp', 'video/webm', lambda w: None, ('caption', 'https://example.com/v', 'title')),
    (LinkedIn, 'linkedin', 'video/webm', lambda w: None, ('text', 'https://example.com/v', 'title')),
])
@pytest.mark.asyncio
async def test_video_wrapper_rejects_mime_outside_contract(
    wrapper_cls, platform_key, invalid_mime, setup, video_args,
):
    """Wrapper MIME checks must match video_limits().mime_types."""
    allowed = video_limits(platform_key).mime_types
    assert invalid_mime not in allowed

    wrapper = wrapper_cls()
    wrapper.api = MagicMock()
    setup(wrapper)
    mock_video = _mock_video(invalid_mime)

    with patch.object(wrapper, 'download_video', new=AsyncMock(return_value=mock_video)):
        with pytest.raises(MediaValidationError, match=platform_key):
            await wrapper.video(*video_args)

    mock_video.cleanup.assert_called()


@pytest.mark.asyncio
async def test_tiktok_image_wrapper_rejects_mime_outside_contract():
    allowed = image_limits('tiktok').mime_types
    invalid = 'image/gif'
    assert invalid not in allowed

    tiktok = TikTok()
    tiktok.api = MagicMock()
    image = MagicMock()
    image.content = b'img'
    image.file_type = MagicMock()
    image.file_type.mime = invalid
    image.url = 'https://example.com/x.gif'
    image.cleanup = MagicMock()

    with patch.object(tiktok, 'download_images', new=AsyncMock(return_value=[image])):
        with pytest.raises(MediaValidationError, match='tiktok'):
            await tiktok.post('title', None, image.url)

    image.cleanup.assert_called()


@pytest.mark.asyncio
@patch('agoras.platforms.threads.api.ThreadsAuthManager')
async def test_threads_api_video_rejects_mime_outside_contract(mock_auth_class):
    """ThreadsAPI video MIME check must match video_limits().mime_types."""
    mock_auth = MagicMock()
    mock_auth.authenticate = AsyncMock()
    mock_auth.ensure_authenticated = MagicMock()
    mock_auth_class.return_value = mock_auth

    api = ThreadsAPI('app_id', 'app_secret', 'refresh_token')
    api._authenticated = True
    mock_auth.access_token = 'token'
    api.auth_manager = mock_auth
    api.client = MagicMock()
    api._rate_limit_check = AsyncMock()

    allowed = video_limits('threads').mime_types
    invalid = 'video/mpeg'
    assert invalid not in allowed

    mock_video = _mock_video(invalid)
    mock_video.url = 'https://example.com/v.mp4'
    mock_video.download = AsyncMock()

    with patch('agoras.platforms.threads.api.MediaFactory') as mock_factory:
        mock_factory.create_video.return_value = mock_video
        with pytest.raises(MediaValidationError, match='threads'):
            await api.create_video_post('caption', 'https://example.com/v.mp4')
