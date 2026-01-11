# -*- coding: utf-8 -*-
#
# Please refer to AUTHORS.md for a complete list of Copyright holders.
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
import socket
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Optional
from urllib.parse import parse_qs, urlparse


class OAuthCallbackHandler(BaseHTTPRequestHandler):
    """HTTP request handler for OAuth callbacks."""

    def log_message(self, format, *args):
        """Suppress default HTTP server logging."""
        pass

    def do_GET(self):
        """Handle GET request from OAuth callback."""
        # Parse the callback URL
        parsed_url = urlparse(self.path)
        params = parse_qs(parsed_url.query)

        # Check for authorization code
        if 'code' in params:
            code = params['code'][0]
            state = params.get('state', [None])[0]

            # Validate state if expected_state is set
            if hasattr(self.server, 'expected_state') and self.server.expected_state:
                if state != self.server.expected_state:
                    self.server.error = 'State mismatch - possible CSRF attack'
                    self._send_error_response('Authorization failed: State validation error')
                    return

            # Store the authorization code
            self.server.auth_code = code
            self._send_success_response()

        elif 'error' in params:
            # OAuth error from provider
            error = params['error'][0]
            error_description = params.get('error_description', [''])[0]
            self.server.error = f"{error}: {error_description}"
            self._send_error_response(f'Authorization failed: {error}')

        else:
            # Unknown callback format
            self.server.error = 'Invalid callback URL'
            self._send_error_response('Invalid callback URL')

    def _send_success_response(self):
        """Send success HTML response to user."""
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Authorization Successful</title>
            <style>
                body {
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    height: 100vh;
                    margin: 0;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                }
                .container {
                    background: white;
                    padding: 40px;
                    border-radius: 10px;
                    box-shadow: 0 10px 40px rgba(0,0,0,0.2);
                    text-align: center;
                }
                h1 {
                    color: #333;
                    margin-bottom: 20px;
                }
                p {
                    color: #666;
                    margin-bottom: 10px;
                }
                .checkmark {
                    font-size: 60px;
                    color: #28a745;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="checkmark">✓</div>
                <h1>Authorization Successful!</h1>
                <p>You have successfully authorized the application.</p>
                <p><strong>You can close this window and return to the terminal.</strong></p>
            </div>
        </body>
        </html>
        """
        self.wfile.write(html.encode())

    def _send_error_response(self, message: str):
        """Send error HTML response to user."""
        self.send_response(400)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Authorization Failed</title>
            <style>
                body {{
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    height: 100vh;
                    margin: 0;
                    background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
                }}
                .container {{
                    background: white;
                    padding: 40px;
                    border-radius: 10px;
                    box-shadow: 0 10px 40px rgba(0,0,0,0.2);
                    text-align: center;
                }}
                h1 {{
                    color: #dc3545;
                    margin-bottom: 20px;
                }}
                p {{
                    color: #666;
                    margin-bottom: 10px;
                }}
                .error-icon {{
                    font-size: 60px;
                    color: #dc3545;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="error-icon">✗</div>
                <h1>Authorization Failed</h1>
                <p>{message}</p>
                <p>Please return to the terminal and try again.</p>
            </div>
        </body>
        </html>
        """
        self.wfile.write(html.encode())


class OAuthCallbackServer:
    """
    Local HTTP server for OAuth callbacks.

    This class provides a local callback server that eliminates the need for
    users to manually copy-paste callback URLs during OAuth authorization.
    The server automatically captures the authorization code and validates
    the OAuth state parameter for CSRF protection.
    """

    def __init__(self, expected_state: Optional[str] = None):
        """
        Initialize OAuth callback server.

        Args:
            expected_state (str, optional): Expected OAuth state for validation
        """
        self.expected_state = expected_state
        self.server: Optional[HTTPServer] = None
        self.port: Optional[int] = None

    async def get_available_port(self) -> int:
        """
        Find an available port for the callback server.

        Returns:
            int: Available port number
        """
        # Let the OS assign an available port
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('localhost', 0))
            s.listen(1)
            port = s.getsockname()[1]
        return port

    async def start_and_wait(self, timeout: int = 300) -> str:
        """
        Start the callback server and wait for OAuth callback.

        Args:
            timeout (int): Maximum time to wait for callback in seconds (default: 300)

        Returns:
            str: Authorization code from the callback

        Raises:
            TimeoutError: If no callback received within timeout
            Exception: If callback contains an error or state validation fails
        """
        # Get an available port
        self.port = await self.get_available_port()

        # Create server
        self.server = HTTPServer(('localhost', self.port), OAuthCallbackHandler)
        self.server.expected_state = self.expected_state
        self.server.auth_code = None
        self.server.error = None

        print(f"Waiting for OAuth callback on http://localhost:{self.port}/callback")
        print("Listening for authorization...")

        # Handle one request with timeout
        try:
            await asyncio.wait_for(
                asyncio.to_thread(self.server.handle_request),
                timeout=timeout
            )
        except asyncio.TimeoutError:
            raise TimeoutError(
                f"Authorization timeout after {timeout} seconds. "
                "Please try again and complete the authorization promptly."
            )
        finally:
            # Clean up server
            if self.server:
                self.server.server_close()

        # Check for errors
        if self.server.error:
            raise Exception(f"Authorization failed: {self.server.error}")

        # Return authorization code
        if self.server.auth_code:
            return self.server.auth_code
        else:
            raise Exception("No authorization code received")

    def get_redirect_uri(self) -> str:
        """
        Get the redirect URI for this callback server.

        Returns:
            str: Redirect URI (e.g., http://localhost:3456/callback)

        Raises:
            Exception: If server hasn't been started yet
        """
        if not self.port:
            raise Exception("Server not started yet. Call start_and_wait() first.")
        return f"http://localhost:{self.port}/callback"
