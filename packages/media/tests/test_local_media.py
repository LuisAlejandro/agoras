# -*- coding: utf-8 -*-
#
# Please refer to AUTHORS.rst for a complete list of Copyright holders.
# Copyright (C) 2022-2026, Agoras Developers.

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import os
from unittest.mock import patch

import pytest
from PIL import Image as PILImage

from agoras.media.constraints import MediaConstraints
from agoras.media.errors import MediaValidationError
from agoras.media import create_image, create_video, download_images, download_video_and_images
from agoras.media.image import Image
from agoras.media.paths import is_local_media_source, media_is_local, normalize_media_path
from agoras.media.preflight import preflight_url_for_platform


def test_is_local_media_source_http_false():
    assert is_local_media_source("https://example.com/a.jpg") is False
    assert is_local_media_source("http://example.com/a.jpg") is False


def test_is_local_media_source_local_true():
    assert is_local_media_source("/tmp/a.jpg") is True
    assert is_local_media_source("./clip.mp4") is True
    assert is_local_media_source("../media/a.png") is True
    assert is_local_media_source("file:///tmp/a.jpg") is True
    assert is_local_media_source("relative/path.jpg") is True


def test_normalize_media_path_relative_with_base_dir(tmp_path):
    base = tmp_path / "posts"
    base.mkdir()
    media = tmp_path / "videos" / "demo.mp4"
    media.parent.mkdir()
    media.write_bytes(b"video")

    resolved = normalize_media_path("../videos/demo.mp4", base_dir=str(base))
    assert resolved == str(media.resolve())


@pytest.mark.asyncio
async def test_local_image_download_reads_from_disk(tmp_path):
    image_path = tmp_path / "test.jpg"
    PILImage.new("RGB", (32, 32), color="red").save(image_path, format="JPEG")

    image = create_image(str(image_path))
    temp_file, content, file_type = await image.download()

    assert image._is_local is True
    assert image._downloaded is True
    assert temp_file == str(image_path)
    assert content
    assert file_type.mime == "image/jpeg"


@pytest.mark.asyncio
async def test_local_image_file_uri_download(tmp_path):
    image_path = tmp_path / "test.jpg"
    PILImage.new("RGB", (16, 16), color="blue").save(image_path, format="JPEG")

    image = create_image(f"file://{image_path}")
    await image.download()

    assert image._is_local is True
    assert image.temp_file == str(image_path.resolve())


@pytest.mark.asyncio
async def test_local_image_missing_file_raises(tmp_path):
    image = create_image(str(tmp_path / "missing.jpg"))
    with pytest.raises(FileNotFoundError):
        await image.download()


@pytest.mark.asyncio
async def test_local_image_cleanup_preserves_source(tmp_path):
    image_path = tmp_path / "keep.jpg"
    PILImage.new("RGB", (8, 8), color="green").save(image_path, format="JPEG")

    image = create_image(str(image_path))
    await image.download()
    image.cleanup()

    assert os.path.exists(image_path)


def test_preflight_skips_local_sources():
    with patch("agoras.media.preflight.urlopen") as mock_urlopen:
        preflight_url_for_platform("/tmp/local.jpg", "tiktok", kind="image")
        preflight_url_for_platform("file:///tmp/local.jpg", "tiktok", kind="image")
        preflight_url_for_platform("./clip.mp4", "tiktok", kind="video")
        mock_urlopen.assert_not_called()


def test_media_is_local_uses_strict_bool():
    class _Remote:
        url = "https://example.com/a.jpg"
        _is_local = False

    class _Local:
        url = "/tmp/a.jpg"
        _is_local = True

    assert media_is_local(_Remote()) is False
    assert media_is_local(_Local()) is True
    assert media_is_local(_Remote(), "/tmp/b.jpg") is True


@pytest.mark.asyncio
async def test_local_image_oversize_rejected_before_full_type_guess(tmp_path):
    image_path = tmp_path / "too-big.bin"
    image_path.write_bytes(b"x" * 50)
    image = Image(
        str(image_path),
        constraints=MediaConstraints(mime_types=frozenset({"image/jpeg"}), max_bytes=10),
    )
    with pytest.raises(MediaValidationError):
        await image.download()


@pytest.mark.asyncio
async def test_local_image_guesses_type_from_bytes(tmp_path):
    """Local downloads guess MIME from in-memory bytes, not a second disk read."""
    image_path = tmp_path / "test.jpg"
    PILImage.new("RGB", (8, 8), color="red").save(image_path, format="JPEG")
    content = image_path.read_bytes()

    image = create_image(str(image_path))
    with patch("agoras.media.base.filetype.guess") as mock_guess:
        mock_type = mock_guess.return_value
        mock_type.mime = "image/jpeg"
        mock_type.extension = "jpg"
        await image.download()
        mock_guess.assert_called()
        guessed = mock_guess.call_args[0][0]
        assert guessed == content
        assert not isinstance(guessed, str)
