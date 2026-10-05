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
End-to-end integration tests for CLI -> Core -> Platform flow.
"""

import importlib
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# Register namespace subpackages so @patch can resolve dotted targets.
importlib.import_module('agoras.core.interfaces')
importlib.import_module('agoras.platforms.telegram.wrapper')
importlib.import_module('agoras.platforms.x.wrapper')

# Test CLI to Platform Flow


@patch('agoras.cli.platforms.x.x_main')
def test_cli_x_post_local_image_reaches_platform(mock_x_main, tmp_path, monkeypatch):
    """agoras x post --image-1 ./test.jpg resolves cwd and reaches the platform wrapper."""
    from agoras.cli.main import main as cli_main

    monkeypatch.chdir(tmp_path)
    image = tmp_path / "test.jpg"
    image.write_bytes(b"jpeg")
    mock_x_main.return_value = 0

    status = cli_main(
        [
            "x",
            "post",
            "--text",
            "Hello",
            "--image-1",
            "./test.jpg",
        ]
    )

    assert status == 0
    mock_x_main.assert_called_once()
    legacy = mock_x_main.call_args[0][0]
    assert legacy["status_image_url_1"] == str(image.resolve())


@patch('agoras.cli.platforms.youtube.youtube_main')
def test_cli_youtube_video_local_path_reaches_platform(mock_youtube_main, tmp_path, monkeypatch):
    """agoras youtube video --video-url ./clip.mp4 resolves cwd and reaches the wrapper."""
    from agoras.cli.main import main as cli_main

    monkeypatch.chdir(tmp_path)
    # Isolate credential storage so profile resolution does not read real ~/.agoras
    monkeypatch.setenv("AGORAS_STORAGE_DIR", str(tmp_path / "storage"))
    video = tmp_path / "clip.mp4"
    video.write_bytes(b"video")
    mock_youtube_main.return_value = 0

    status = cli_main(
        [
            "youtube",
            "video",
            "--title",
            "Clip",
            "--video-url",
            "./clip.mp4",
        ]
    )

    assert status == 0
    mock_youtube_main.assert_called_once()
    legacy = mock_youtube_main.call_args[0][0]
    assert legacy["youtube_video_url"] == str(video.resolve())
