# -*- coding: utf-8 -*-
"""Tests for platform_runner.execute_platform_action."""

from io import StringIO
from pathlib import Path
from unittest.mock import patch

import pytest
from agoras.cli.platform_runner import execute_platform_action

NETWORK_WRAPPER_PATCHES = {
    'x': 'agoras.cli.platform_runner.x',
    'facebook': 'agoras.cli.platform_runner.facebook',
    'instagram': 'agoras.cli.platform_runner.instagram',
    'linkedin': 'agoras.cli.platform_runner.linkedin',
    'discord': 'agoras.cli.platform_runner.discord',
    'youtube': 'agoras.cli.platform_runner.youtube',
    'tiktok': 'agoras.cli.platform_runner.tiktok',
    'threads': 'agoras.cli.platform_runner.threads',
    'telegram': 'agoras.cli.platform_runner.telegram',
    'whatsapp': 'agoras.cli.platform_runner.whatsapp',
}


@pytest.mark.parametrize('network,patch_target', NETWORK_WRAPPER_PATCHES.items())
def test_execute_platform_action_dispatches_to_wrapper(network, patch_target):
    with patch(patch_target) as mock_wrapper:
        kwargs = {'network': network, 'action': 'post'}
        execute_platform_action(**kwargs)
        mock_wrapper.assert_called_once_with(kwargs)


@patch('agoras.cli.platform_runner.x')
def test_execute_platform_action_twitter_silent_alias(mock_x):
    kwargs = {'network': 'twitter', 'action': 'post'}
    execute_platform_action(**kwargs)
    mock_x.assert_called_once()
    call_kwargs = mock_x.call_args[0][0]
    assert call_kwargs['network'] == 'x'


def test_execute_platform_action_empty_network_raises():
    with pytest.raises(Exception, match='required argument'):
        execute_platform_action(network='', action='post')


def test_execute_platform_action_unsupported_network_raises():
    with pytest.raises(Exception, match='not supported'):
        execute_platform_action(network='myspace', action='post')


def test_execute_platform_action_none_network_raises():
    with pytest.raises(Exception, match='required argument'):
        execute_platform_action(network=None, action='post')


def test_platform_runner_does_not_import_validator():
    import agoras.cli.platform_runner as module

    source = Path(module.__file__).read_text(encoding='utf-8')
    assert 'ActionValidator' not in source
    assert 'ParameterConverter' not in source


@patch('agoras.cli.commands.publish.execute_platform_action')
@patch('sys.stderr', new_callable=StringIO)
def test_publish_main_twitter_warns_then_delegates(mock_stderr, mock_execute):
    from agoras.cli.commands.publish import main as publish_main

    publish_main(network='twitter', action='post')

    stderr_output = mock_stderr.getvalue()
    assert 'deprecated' in stderr_output.lower()
    mock_execute.assert_called_once()
    assert mock_execute.call_args[1]['network'] == 'twitter'
