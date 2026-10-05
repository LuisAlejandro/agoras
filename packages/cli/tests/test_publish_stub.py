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
"""Tests for the legacy publish pointer stub (removed in 3.0)."""

import pytest

from agoras.cli.main import main
from agoras.cli.publish_stub import REMOVED_MESSAGE


def test_publish_plain_invocation_prints_message_and_exits_nonzero(capsys):
    status = main(["publish"])
    captured = capsys.readouterr()
    assert status == 1
    assert REMOVED_MESSAGE in captured.err
    assert "Traceback" not in captured.err


def test_publish_help_prints_message_and_exits_nonzero(capsys):
    with pytest.raises(SystemExit) as excinfo:
        main(["publish", "--help"])
    captured = capsys.readouterr()
    assert excinfo.value.code == 1
    assert REMOVED_MESSAGE in captured.err
    assert "Traceback" not in captured.err


def test_publish_with_legacy_flags_prints_message(capsys):
    status = main(["publish", "-mc", "5", "-ta", "token"])
    captured = capsys.readouterr()
    assert status == 1
    assert REMOVED_MESSAGE in captured.err


def test_publish_arbitrary_arguments_absorbed(capsys):
    status = main(["publish", "x", "post", "--foo", "bar"])
    captured = capsys.readouterr()
    assert status == 1
    assert REMOVED_MESSAGE in captured.err


def test_platform_commands_still_parse():
    with pytest.raises(SystemExit) as excinfo:
        main(["x", "--help"])
    assert excinfo.value.code == 0
    with pytest.raises(SystemExit) as excinfo:
        main(["-V"])
    assert excinfo.value.code == 0

def test_publish_process_level_exit_codes():
    """Process-level exit-code contract for every legacy publish shape."""
    import subprocess
    import sys

    shapes = [
        ["publish"],
        ["publish", "--help"],
        ["publish", "-h"],
        ["publish", "-mc", "5"],
        ["publish", "-l", "DEBUG"],
        ["publish", "--"],
        ["publish", "foo", "--help"],
    ]
    for shape in shapes:
        result = subprocess.run(
            [sys.executable, "-m", "agoras.cli.main"] + shape,
            capture_output=True,
            text=True,
        )
        assert result.returncode == 1, f"{shape}: rc={result.returncode}"
        assert "removed in Agoras 3.0" in result.stderr, f"{shape}: no pointer"
        assert "Traceback" not in result.stderr, f"{shape}: traceback"


def test_publish_listed_in_parent_help_with_pointer(capsys):
    with pytest.raises(SystemExit) as excinfo:
        main(["--help"])
    captured = capsys.readouterr()
    assert excinfo.value.code == 0
    assert "publish" in captured.out
    assert "Removed in Agoras 3.0" in captured.out


def test_message_pins_literal_text():
    assert "removed in Agoras 3.0" in REMOVED_MESSAGE
    assert "agoras.readthedocs.io/en/latest/migration/" in REMOVED_MESSAGE
    assert "agoras <platform>" in REMOVED_MESSAGE
