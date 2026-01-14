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

import asyncio
from io import BytesIO
from unittest.mock import MagicMock, patch

import pytest

from agoras.core.auth.callback_server import OAuthCallbackHandler, OAuthCallbackServer


# Helper class for testing
class MockServer:
    """Mock server object for testing handler."""

    def __init__(self):
        self.auth_code = None
        self.error = None
        self.expected_state = None


def test_callback_server_instantiation():
    """Test OAuthCallbackServer can be instantiated."""
    server = OAuthCallbackServer()
    assert server is not None


def test_callback_server_with_state():
    """Test OAuthCallbackServer with expected state."""
    server = OAuthCallbackServer(expected_state='test_state_123')
    assert server.expected_state == 'test_state_123'


@pytest.mark.asyncio
async def test_callback_server_get_available_port():
    """Test that callback server can find an available port."""
    server = OAuthCallbackServer()
    port = await server.get_available_port()
    assert isinstance(port, int)
    assert 1024 <= port <= 65535


def test_callback_handler_exists():
    """Test that OAuthCallbackHandler class exists."""
    assert OAuthCallbackHandler is not None
    assert hasattr(OAuthCallbackHandler, 'do_GET')


# OAuthCallbackHandler Tests

def test_do_GET_with_auth_code():
    """Test do_GET with successful auth code callback."""
    handler = OAuthCallbackHandler.__new__(OAuthCallbackHandler)
    handler.path = '/callback?code=abc123'
    handler.server = MockServer()
    handler.wfile = BytesIO()

    handler.send_response = MagicMock()
    handler.send_header = MagicMock()
    handler.end_headers = MagicMock()

    handler.do_GET()

    assert handler.server.auth_code == 'abc123'
    handler.send_response.assert_called_with(200)


def test_do_GET_with_state_validation_success():
    """Test do_GET with successful state validation."""
    handler = OAuthCallbackHandler.__new__(OAuthCallbackHandler)
    handler.path = '/callback?code=abc123&state=valid_state'
    handler.server = MockServer()
    handler.server.expected_state = 'valid_state'
    handler.wfile = BytesIO()

    handler.send_response = MagicMock()
    handler.send_header = MagicMock()
    handler.end_headers = MagicMock()

    handler.do_GET()

    assert handler.server.auth_code == 'abc123'
    handler.send_response.assert_called_with(200)


def test_do_GET_with_state_mismatch():
    """Test do_GET with state validation failure."""
    handler = OAuthCallbackHandler.__new__(OAuthCallbackHandler)
    handler.path = '/callback?code=abc123&state=wrong_state'
    handler.server = MockServer()
    handler.server.expected_state = 'expected_state'
    handler.wfile = BytesIO()

    handler.send_response = MagicMock()
    handler.send_header = MagicMock()
    handler.end_headers = MagicMock()

    handler.do_GET()

    assert 'State mismatch' in handler.server.error
    handler.send_response.assert_called_with(400)


def test_do_GET_with_oauth_error():
    """Test do_GET with OAuth error from provider."""
    handler = OAuthCallbackHandler.__new__(OAuthCallbackHandler)
    handler.path = '/callback?error=access_denied&error_description=User+cancelled'
    handler.server = MockServer()
    handler.wfile = BytesIO()

    handler.send_response = MagicMock()
    handler.send_header = MagicMock()
    handler.end_headers = MagicMock()

    handler.do_GET()

    assert 'access_denied' in handler.server.error
    handler.send_response.assert_called_with(400)


def test_do_GET_with_invalid_callback():
    """Test do_GET with invalid callback format."""
    handler = OAuthCallbackHandler.__new__(OAuthCallbackHandler)
    handler.path = '/callback?unknown=param'
    handler.server = MockServer()
    handler.wfile = BytesIO()

    handler.send_response = MagicMock()
    handler.send_header = MagicMock()
    handler.end_headers = MagicMock()

    handler.do_GET()

    assert 'Invalid callback URL' in handler.server.error
    handler.send_response.assert_called_with(400)


def test_send_success_response():
    """Test _send_success_response sends HTML."""
    handler = OAuthCallbackHandler.__new__(OAuthCallbackHandler)
    handler.wfile = BytesIO()

    handler.send_response = MagicMock()
    handler.send_header = MagicMock()
    handler.end_headers = MagicMock()

    handler._send_success_response()

    handler.send_response.assert_called_with(200)
    handler.send_header.assert_called_with('Content-type', 'text/html')

    written_data = handler.wfile.getvalue()
    assert b'Authorization Successful' in written_data
    assert b'<!DOCTYPE html>' in written_data


def test_send_error_response():
    """Test _send_error_response sends error HTML."""
    handler = OAuthCallbackHandler.__new__(OAuthCallbackHandler)
    handler.wfile = BytesIO()

    handler.send_response = MagicMock()
    handler.send_header = MagicMock()
    handler.end_headers = MagicMock()

    handler._send_error_response('Test error message')

    handler.send_response.assert_called_with(400)
    handler.send_header.assert_called_with('Content-type', 'text/html')

    written_data = handler.wfile.getvalue()
    assert b'Authorization Failed' in written_data
    assert b'Test error message' in written_data


def test_log_message_suppresses_output():
    """Test log_message suppresses default HTTP logging."""
    handler = OAuthCallbackHandler.__new__(OAuthCallbackHandler)
    handler.log_message("Test log message")


# OAuthCallbackServer Tests

@pytest.mark.asyncio
async def test_get_available_port_range():
    """Test get_available_port returns port in valid range."""
    server = OAuthCallbackServer()
    port = await server.get_available_port()

    assert 1024 <= port <= 65535


@pytest.mark.asyncio
@patch('builtins.print')
@patch('agoras.core.auth.callback_server.HTTPServer')
async def test_start_and_wait_success(mock_httpserver_class, mock_print):
    """Test start_and_wait with successful authorization."""
    mock_server = MagicMock()
    mock_server.server_close = MagicMock()
    mock_server.handle_request = MagicMock()

    def side_effect_set_auth_code():
        mock_server.auth_code = 'auth_code_123'
        mock_server.error = None

    mock_server.handle_request.side_effect = side_effect_set_auth_code
    mock_httpserver_class.return_value = mock_server

    server = OAuthCallbackServer()

    result = await server.start_and_wait(timeout=1)

    assert result == 'auth_code_123'
    mock_server.server_close.assert_called_once()


@pytest.mark.asyncio
@patch('builtins.print')
@patch('agoras.core.auth.callback_server.HTTPServer')
async def test_start_and_wait_timeout(mock_httpserver_class, mock_print):
    """Test start_and_wait raises TimeoutError on timeout."""
    mock_server = MagicMock()
    mock_server.server_close = MagicMock()
    mock_httpserver_class.return_value = mock_server

    async def slow_request(*args):
        await asyncio.sleep(10)

    with patch('agoras.core.auth.callback_server.asyncio.to_thread', side_effect=slow_request):
        server = OAuthCallbackServer()

        with pytest.raises(TimeoutError, match='Authorization timeout'):
            await server.start_and_wait(timeout=0.1)

        mock_server.server_close.assert_called_once()


@pytest.mark.asyncio
@patch('builtins.print')
@patch('agoras.core.auth.callback_server.HTTPServer')
async def test_start_and_wait_with_error(mock_httpserver_class, mock_print):
    """Test start_and_wait raises exception when server.error is set."""
    mock_server = MagicMock()
    mock_server.server_close = MagicMock()
    mock_server.handle_request = MagicMock()

    def side_effect_set_error():
        mock_server.auth_code = None
        mock_server.error = 'State validation error'

    mock_server.handle_request.side_effect = side_effect_set_error
    mock_httpserver_class.return_value = mock_server

    server = OAuthCallbackServer()

    with pytest.raises(Exception, match='State validation error'):
        await server.start_and_wait(timeout=1)


@pytest.mark.asyncio
@patch('builtins.print')
@patch('agoras.core.auth.callback_server.HTTPServer')
async def test_start_and_wait_no_auth_code(mock_httpserver_class, mock_print):
    """Test start_and_wait raises exception when no auth code received."""
    mock_server = MagicMock()
    mock_server.server_close = MagicMock()
    mock_server.handle_request = MagicMock()

    def side_effect_no_code():
        mock_server.auth_code = None
        mock_server.error = None

    mock_server.handle_request.side_effect = side_effect_no_code
    mock_httpserver_class.return_value = mock_server

    server = OAuthCallbackServer()

    with pytest.raises(Exception, match='No authorization code received'):
        await server.start_and_wait(timeout=1)


@pytest.mark.asyncio
@patch('builtins.print')
@patch('agoras.core.auth.callback_server.HTTPServer')
async def test_start_and_wait_cleanup_on_exception(mock_httpserver_class, mock_print):
    """Test start_and_wait cleans up server on exception."""
    mock_server = MagicMock()
    mock_server.server_close = MagicMock()
    mock_httpserver_class.return_value = mock_server

    with patch('agoras.core.auth.callback_server.asyncio.to_thread', side_effect=RuntimeError('Test exception')):
        server = OAuthCallbackServer()

        with pytest.raises(RuntimeError):
            await server.start_and_wait(timeout=1)

        mock_server.server_close.assert_called_once()


@pytest.mark.asyncio
@patch('builtins.print')
@patch('agoras.core.auth.callback_server.HTTPServer')
async def test_start_and_wait_prints_callback_url(mock_httpserver, mock_print):
    """Test start_and_wait prints callback URL."""
    mock_srv = MagicMock()
    mock_srv.server_close = MagicMock()
    mock_srv.handle_request = MagicMock()

    def side_effect_success():
        mock_srv.auth_code = 'code123'
        mock_srv.error = None

    mock_srv.handle_request.side_effect = side_effect_success
    mock_httpserver.return_value = mock_srv

    server = OAuthCallbackServer()
    await server.start_and_wait(timeout=1)

    assert mock_print.call_count >= 1
    calls = [str(call) for call in mock_print.call_args_list]
    assert any('localhost' in call for call in calls)


def test_get_redirect_uri_before_start():
    """Test get_redirect_uri raises exception before server start."""
    server = OAuthCallbackServer()

    with pytest.raises(Exception, match='Server not started yet'):
        server.get_redirect_uri()


def test_get_redirect_uri_after_port_assigned():
    """Test get_redirect_uri returns correct URI format."""
    server = OAuthCallbackServer()
    server.port = 8080

    uri = server.get_redirect_uri()

    assert uri == 'http://localhost:8080/callback'


@pytest.mark.asyncio
async def test_get_available_port_multiple_calls():
    """Test get_available_port can be called multiple times."""
    server = OAuthCallbackServer()

    port1 = await server.get_available_port()
    port2 = await server.get_available_port()

    assert isinstance(port1, int)
    assert isinstance(port2, int)


def test_success_response_contains_success_message():
    """Test success response contains success indicators."""
    handler = OAuthCallbackHandler.__new__(OAuthCallbackHandler)
    handler.wfile = BytesIO()
    handler.send_response = MagicMock()
    handler.send_header = MagicMock()
    handler.end_headers = MagicMock()

    handler._send_success_response()

    content = handler.wfile.getvalue().decode()
    assert 'Authorization Successful' in content
    assert 'close this window' in content


def test_error_response_contains_error_message():
    """Test error response contains error message."""
    handler = OAuthCallbackHandler.__new__(OAuthCallbackHandler)
    handler.wfile = BytesIO()
    handler.send_response = MagicMock()
    handler.send_header = MagicMock()
    handler.end_headers = MagicMock()

    handler._send_error_response('Custom error message')

    content = handler.wfile.getvalue().decode()
    assert 'Authorization Failed' in content
    assert 'Custom error message' in content


def test_do_GET_extracts_state_parameter():
    """Test do_GET correctly extracts state parameter."""
    handler = OAuthCallbackHandler.__new__(OAuthCallbackHandler)
    handler.path = '/callback?code=abc&state=xyz123'
    handler.server = MockServer()
    handler.wfile = BytesIO()

    handler.send_response = MagicMock()
    handler.send_header = MagicMock()
    handler.end_headers = MagicMock()

    handler.do_GET()

    assert handler.server.auth_code == 'abc'


def test_do_GET_with_error_description():
    """Test do_GET extracts error description."""
    handler = OAuthCallbackHandler.__new__(OAuthCallbackHandler)
    handler.path = '/callback?error=invalid_request&error_description=Missing+parameter'
    handler.server = MockServer()
    handler.wfile = BytesIO()

    handler.send_response = MagicMock()
    handler.send_header = MagicMock()
    handler.end_headers = MagicMock()

    handler.do_GET()

    assert 'invalid_request' in handler.server.error
