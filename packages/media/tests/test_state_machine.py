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
"""Media lifecycle state machine: one state, one writer, derived flags."""

import os
from unittest.mock import MagicMock, mock_open, patch

import pytest
from PIL import Image as PILImage

from agoras.media.base import MediaState
from agoras.media.errors import MediaValidationError
from agoras.media.factory import create_image, create_video
from agoras.media.image import Image

MISSING_TMP = "/tmp/agoras-state-machine-absent.bin"


def _kind(mime, extension):
    """Build a filetype.guess() result stub."""
    stub = MagicMock()
    stub.mime = mime
    stub.extension = extension
    return stub


def test_new_media_derives_its_flags_from_one_state():
    """NEW implies not downloaded and not local; flags are never stored."""
    remote = Image("https://example.com/a.jpg")
    assert remote._state is MediaState.NEW
    assert remote._downloaded is False
    assert remote._is_local is False
    assert "downloaded" not in vars(remote)


def test_is_local_is_derived_from_the_url(tmp_path):
    """Local detection reads the source, so it cannot go stale after cleanup."""
    local = Image(str(tmp_path / "a.jpg"))
    assert local._is_local is True
    assert local.is_local is True


def test_downloaded_shim_moves_the_state():
    """The migration shim maps the old boolean onto the single state."""
    image = Image("https://example.com/a.jpg")
    image._downloaded = True
    assert image._state is MediaState.DOWNLOADED
    image.cleanup()
    assert image._state is MediaState.CLEANED
    assert image._downloaded is False


@pytest.mark.asyncio
@patch("agoras.media.video.cv2.VideoCapture")
@patch("agoras.media.base.filetype.guess")
@patch("agoras.media.base.urlopen")
@patch("agoras.media.base.tempfile.mkstemp")
@patch("builtins.open", new_callable=mock_open)
async def test_download_enforces_video_duration_limit(mock_file, mock_mkstemp, mock_urlopen, mock_filetype, mock_capture):
    """Duration limits must apply on the real download path, not only when probed by hand."""
    mock_mkstemp.return_value = (1, MISSING_TMP)
    mock_urlopen.return_value = MagicMock(read=MagicMock(return_value=b"fake_mp4"))
    mock_filetype.return_value = _kind("video/mp4", "mp4")
    mock_capture.return_value.get.side_effect = [30.0, 30.0 * 700, 640, 480]  # 700s, tiktok max 600

    video = create_video("https://example.com/video.mp4", "tiktok")

    with pytest.raises(MediaValidationError, match="exceeds tiktok limit"):
        await video.download()

    assert video._state is MediaState.CLEANED


@pytest.mark.asyncio
@patch("agoras.media.image.Image.get_dimensions", return_value=(2000, 1000))
@patch("agoras.media.base.filetype.guess")
@patch("agoras.media.base.urlopen")
@patch("agoras.media.base.tempfile.mkstemp")
@patch("builtins.open", new_callable=mock_open)
async def test_download_enforces_image_dimension_limit(mock_file, mock_mkstemp, mock_urlopen, mock_filetype, _dims):
    """Image dimension limits must apply on the real download path (threads max 1440)."""
    mock_mkstemp.return_value = (1, MISSING_TMP)
    mock_urlopen.return_value = MagicMock(read=MagicMock(return_value=b"fake_jpeg"))
    mock_filetype.return_value = _kind("image/jpeg", "jpg")

    image = create_image("https://example.com/a.jpg", platform="threads")

    with pytest.raises(MediaValidationError, match="max_width"):
        await image.download()

    assert image._state is MediaState.CLEANED


@pytest.mark.asyncio
async def test_local_download_reaches_downloaded_then_cleans_without_deleting(tmp_path):
    """A local source is read, validated, and released without touching the user's file."""
    image_path = tmp_path / "keep.jpg"
    PILImage.new("RGB", (8, 8), color="green").save(image_path, format="JPEG")

    image = create_image(str(image_path))
    await image.download()
    assert image._state is MediaState.DOWNLOADED

    image.cleanup()
    assert image._state is MediaState.CLEANED
    assert image.temp_file is None
    assert image.content is None
    assert os.path.exists(image_path)


@pytest.mark.asyncio
async def test_second_download_is_a_no_op_in_downloaded_state(tmp_path):
    """DOWNLOADED is terminal for the read step."""
    image_path = tmp_path / "twice.jpg"
    PILImage.new("RGB", (8, 8), color="red").save(image_path, format="JPEG")

    image = create_image(str(image_path))
    first = await image.download()
    second = await image.download()

    assert first == second
    assert image._state is MediaState.DOWNLOADED
