# -*- coding: utf-8 -*-

from io import StringIO
from unittest.mock import patch

from agoras.cli.utils.media_limits import _handle_media_limits
from argparse import Namespace


def test_media_limits_stdout_contains_discord_8mb():
    with patch('sys.stdout', new_callable=StringIO) as stdout:
        _handle_media_limits(Namespace(platform='discord', kind='video', json=False))
        output = stdout.getvalue()
    assert 'discord' in output
    assert '8MB' in output
    assert 'video/mp4' in output
