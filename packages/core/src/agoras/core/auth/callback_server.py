# -*- coding: utf-8 -*-
#
# Please refer to AUTHORS.md for a complete list of Copyright holders.
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

import asyncio
import ipaddress
import os
import socket
import ssl
import tempfile
from datetime import datetime, timedelta
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Optional
from urllib.parse import parse_qs, urlparse

try:
    from cryptography import x509
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import rsa
    from cryptography.x509.oid import NameOID
    CRYPTOGRAPHY_AVAILABLE = True
except ImportError:
    CRYPTOGRAPHY_AVAILABLE = False


class OAuthCallbackHandler(BaseHTTPRequestHandler):
    """HTTP request handler for OAuth callbacks."""

    def log_message(self, format, *args):
        """Suppress default HTTP server logging."""

    def do_GET(self):
        """Handle GET request from OAuth callback."""
        try:
            # Parse the callback URL
            parsed_url = urlparse(self.path)
            params = parse_qs(parsed_url.query)

            # Check for authorization code (OAuth 2.0)
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
                self.server.oauth_version = '2.0'
                self._send_success_response()

            # Check for OAuth 1.0a callback
            elif 'oauth_token' in params and 'oauth_verifier' in params:
                # Store the full callback URL for OAuth 1.0a parsing
                self.server.callback_url = self.path  # Full path with query string
                self.server.oauth_version = '1.0a'
                self._send_success_response()

            # Check for OAuth 1.0a denial
            elif 'denied' in params:
                self.server.error = 'User denied authorization'
                self.server.oauth_version = '1.0a'
                self._send_error_response('Authorization denied by user')

            # Check for OAuth 1.0a errors
            elif 'oauth_problem' in params:
                oauth_problem = params['oauth_problem'][0]
                self.server.error = f'OAuth 1.0a error: {oauth_problem}'
                self.server.oauth_version = '1.0a'
                self._send_error_response(f'Authorization failed: {oauth_problem}')

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
        except Exception as e:
            # Catch any exceptions to prevent connection reset
            self.server.error = f'Handler error: {str(e)}'
            try:
                self._send_error_response(f'Server error: {str(e)}')
            except Exception:
                # If we can't send error response, at least log it
                pass

    def _send_success_response(self):
        """Send success HTML response to user."""
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.send_header('Connection', 'close')
        self.end_headers()

        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Authorization Successful - Agoras</title>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500&display=swap" rel="stylesheet">
            <style>
                * {
                    margin: 0;
                    padding: 0;
                    box-sizing: border-box;
                }
                body {
                    font-family: 'Roboto', sans-serif;
                    font-weight: 300;
                    background-color: #f8f8f8;
                    color: #333;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    min-height: 100vh;
                    padding: 20px;
                }
                .container {
                    background: white;
                    max-width: 500px;
                    width: 100%;
                    padding: 60px 40px;
                    text-align: center;
                    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
                    border-radius: 4px;
                }
                .success-icon {
                    font-size: 48px;
                    color: #f2545b;
                    margin-bottom: 24px;
                }
                h1 {
                    font-weight: 400;
                    font-size: 28px;
                    color: #333;
                    margin-bottom: 16px;
                }
                p {
                    font-size: 16px;
                    line-height: 1.6;
                    color: #666;
                    margin-bottom: 12px;
                }
                .message {
                    margin-top: 24px;
                    padding-top: 24px;
                    border-top: 1px solid #e8e8e8;
                }
                .message strong {
                    font-weight: 500;
                    color: #333;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="success-icon">✓</div>
                <h1>Authorization Successful</h1>
                <p>You have successfully authorized Agoras to access your account.</p>
                <div class="message">
                    <p><strong>You can close this window and return to the terminal.</strong></p>
                </div>
            </div>
        </body>
        </html>
        """
        self.wfile.write(html.encode())
        self.wfile.flush()

    def _send_error_response(self, message: str):
        """Send error HTML response to user."""
        self.send_response(400)
        self.send_header('Content-type', 'text/html')
        self.send_header('Connection', 'close')
        self.end_headers()

        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Authorization Failed - Agoras</title>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500&display=swap" rel="stylesheet">
            <style>
                * {
                    margin: 0;
                    padding: 0;
                    box-sizing: border-box;
                }
                body {
                    font-family: 'Roboto', sans-serif;
                    font-weight: 300;
                    background-color: #f8f8f8;
                    color: #333;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    min-height: 100vh;
                    padding: 20px;
                }
                .container {
                    background: white;
                    max-width: 500px;
                    width: 100%;
                    padding: 60px 40px;
                    text-align: center;
                    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
                    border-radius: 4px;
                }
                .error-icon {
                    font-size: 48px;
                    color: #db4d58;
                    margin-bottom: 24px;
                }
                h1 {
                    font-weight: 400;
                    font-size: 28px;
                    color: #333;
                    margin-bottom: 16px;
                }
                p {
                    font-size: 16px;
                    line-height: 1.6;
                    color: #666;
                    margin-bottom: 12px;
                }
                .message {
                    margin-top: 24px;
                    padding-top: 24px;
                    border-top: 1px solid #e8e8e8;
                }
                .message strong {
                    font-weight: 500;
                    color: #333;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="error-icon">✗</div>
                <h1>Authorization Failed</h1>
                <div class="message">
                    <p><strong>Please return to the terminal and try again.</strong></p>
                </div>
            </div>
        </body>
        </html>
        """
        self.wfile.write(html.encode())
        self.wfile.flush()


class SSLHTTPServer(HTTPServer):
    """HTTPS server with SSL support."""

    def __init__(self, server_address, RequestHandlerClass, ssl_context):
        super().__init__(server_address, RequestHandlerClass)
        self.ssl_context = ssl_context

    def get_request(self):
        """Override to wrap the socket with SSL."""
        conn, addr = self.socket.accept()
        try:
            # Wrap socket but don't do handshake immediately
            # This allows the browser to show the security warning first
            ssl_conn = self.ssl_context.wrap_socket(
                conn,
                server_side=True,
                do_handshake_on_connect=False,
                suppress_ragged_eofs=True
            )
            # Perform handshake - this may fail if browser rejects cert
            # but we'll let it try and the browser will show the warning
            try:
                ssl_conn.do_handshake()
            except ssl.SSLError as e:
                # If handshake fails due to certificate rejection, close and let browser retry
                # The browser will show the security warning and user can accept
                error_msg = str(e)
                if 'CERTIFICATE' in error_msg.upper() or 'alert' in error_msg.lower():
                    # Browser rejected cert - it will show warning and user can accept
                    # Close this connection and wait for browser to retry after user accepts
                    conn.close()
                    # Re-raise to get a new connection
                    raise
                else:
                    # Other SSL error
                    conn.close()
                    raise
            return ssl_conn, addr
        except ssl.SSLError:
            # Re-raise SSL errors to get a new connection attempt
            raise
        except Exception as e:
            conn.close()
            import sys
            print(f"Connection error from {addr}: {e}", file=sys.stderr, flush=True)
            raise


class OAuthCallbackServer:
    """
    Local HTTPS server for OAuth callbacks.

    This class provides a local callback server that eliminates the need for
    users to manually copy-paste callback URLs during OAuth authorization.
    The server automatically captures the authorization code and validates
    the OAuth state parameter for CSRF protection.

    The server uses HTTPS with a self-signed certificate for localhost,
    which is required by OAuth providers (e.g., Facebook/Instagram).
    """

    def __init__(self, expected_state: Optional[str] = None, port: Optional[int] = None,
                 oauth_version: str = '2.0'):
        """
        Initialize OAuth callback server.

        Args:
            expected_state (str, optional): Expected OAuth state for validation
            port (int, optional): Fixed port number to use. If None, uses dynamic port.
            oauth_version (str): OAuth version ('2.0' or '1.0a'), defaults to '2.0'
        """
        self.expected_state = expected_state
        self.server: Optional[HTTPServer] = None
        self.port: Optional[int] = port
        self.oauth_version = oauth_version
        self._cert_file: Optional[str] = None
        self._key_file: Optional[str] = None

    async def get_available_port(self) -> int:
        """
        Find an available port for the callback server.

        Returns:
            int: Port number (fixed port if set and available, otherwise OS-assigned)
        """
        # If fixed port is set, try to use it
        if self.port is not None:
            # Check if port is available
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                try:
                    s.bind(('localhost', self.port))
                    s.listen(1)
                    return self.port
                except OSError:
                    # Port is in use, fall back to dynamic
                    pass

        # Let the OS assign an available port
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('localhost', 0))
            s.listen(1)
            port = s.getsockname()[1]
        return port

    def _generate_self_signed_cert(self) -> tuple[str, str]:
        """
        Generate a self-signed certificate for localhost.

        Returns:
            tuple: (cert_file_path, key_file_path) temporary file paths
        """
        if not CRYPTOGRAPHY_AVAILABLE:
            raise Exception(
                "cryptography library is required for HTTPS support. "
                "Please install it: pip install cryptography"
            )

        # Generate private key
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
        )

        # Create certificate
        subject = issuer = x509.Name([
            x509.NameAttribute(NameOID.COUNTRY_NAME, "US"),
            x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "Local"),
            x509.NameAttribute(NameOID.LOCALITY_NAME, "Local"),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, "Agoras"),
            x509.NameAttribute(NameOID.COMMON_NAME, "localhost"),
        ])

        now = datetime.utcnow()
        cert = x509.CertificateBuilder().subject_name(
            subject
        ).issuer_name(
            issuer
        ).public_key(
            private_key.public_key()
        ).serial_number(
            x509.random_serial_number()
        ).add_extension(
            x509.SubjectAlternativeName([
                x509.DNSName("localhost"),
                x509.DNSName("*.localhost"),
                x509.IPAddress(ipaddress.IPv4Address("127.0.0.1")),
                x509.IPAddress(ipaddress.IPv6Address("::1")),
            ]),
            critical=False,
        ).not_valid_before(
            now
        ).not_valid_after(
            now + timedelta(days=365)  # 1 year
        ).sign(private_key, hashes.SHA256())

        # Write to temporary files
        cert_file = tempfile.NamedTemporaryFile(mode='wb', delete=False, suffix='.pem')
        key_file = tempfile.NamedTemporaryFile(mode='wb', delete=False, suffix='.pem')

        cert_file.write(cert.public_bytes(serialization.Encoding.PEM))
        key_file.write(private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        ))

        cert_file.close()
        key_file.close()

        return cert_file.name, key_file.name

    async def start_and_wait(self, timeout: int = 300) -> str:
        """
        Start the HTTPS callback server and wait for OAuth callback.

        Args:
            timeout (int): Maximum time to wait for callback in seconds (default: 300)

        Returns:
            str: Authorization code from the callback

        Raises:
            TimeoutError: If no callback received within timeout
            Exception: If callback contains an error or state validation fails
        """
        # Get port (will use fixed port if set, otherwise dynamic)
        if self.port is None:
            self.port = await self.get_available_port()

        # Generate self-signed certificate for localhost (always HTTPS)
        self._cert_file, self._key_file = self._generate_self_signed_cert()

        # Create SSL context
        ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        ssl_context.load_cert_chain(self._cert_file, self._key_file)
        ssl_context.minimum_version = ssl.TLSVersion.MINIMUM_SUPPORTED
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE

        # Create server with SSL support
        self.server = SSLHTTPServer(('localhost', self.port), OAuthCallbackHandler, ssl_context)

        self.server.expected_state = self.expected_state
        self.server.auth_code = None
        self.server.callback_url = None
        self.server.oauth_version = None
        self.server.error = None

        print(f"Waiting for OAuth callback on https://localhost:{self.port}/callback")
        print("Note: Your browser may show a security warning for the self-signed certificate.")
        print("This is normal for localhost - you can safely proceed.")
        print("Listening for authorization...")

        # Handle requests with timeout - keep trying until we get a valid callback
        # The browser may reject the cert first, then retry after user accepts it
        try:
            import time
            start_time = time.time()
            while True:
                elapsed = time.time() - start_time
                if elapsed >= timeout:
                    raise TimeoutError(
                        f"Authorization timeout after {timeout} seconds. "
                        "Please try again and complete the authorization promptly."
                    )

                remaining_timeout = timeout - elapsed
                try:
                    # Try to handle a request with a shorter timeout so we can retry
                    await asyncio.wait_for(
                        asyncio.to_thread(self.server.handle_request),
                        timeout=min(remaining_timeout, 10)  # Check every 10 seconds
                    )
                    # If we got here, we successfully handled a request
                    # Check if we got an auth code, callback URL, or error
                    if self.server.auth_code or self.server.callback_url or self.server.error:
                        break
                    # If no auth code yet, continue waiting
                    continue
                except asyncio.TimeoutError:
                    # No request in this window, continue waiting
                    continue
                except Exception as e:
                    # Any error (including SSL) - log and continue waiting
                    # Browser will retry after user accepts certificate
                    error_str = str(e)
                    if 'SSL' in error_str or 'certificate' in error_str.lower() or 'alert' in error_str.lower():
                        # SSL error - browser will retry after user accepts cert
                        # Don't log this as it's expected behavior
                        pass
                    else:
                        import sys
                        print(f"Connection attempt failed: {e}", file=sys.stderr, flush=True)
                    # Continue waiting for browser retry
                    continue
        finally:
            # Clean up server
            if self.server:
                self.server.server_close()
            # Clean up certificate files (always HTTPS)
            if self._cert_file and os.path.exists(self._cert_file):
                os.unlink(self._cert_file)
            if self._key_file and os.path.exists(self._key_file):
                os.unlink(self._key_file)

        # Check for errors
        if self.server.error:
            raise Exception(f"Authorization failed: {self.server.error}")

        # Return appropriate result based on OAuth version
        if self.server.oauth_version == '1.0a':
            # Return full callback URL for OAuth 1.0a
            if self.server.callback_url:
                return self.server.callback_url
            else:
                raise Exception("No callback URL received")
        else:
            # Return authorization code for OAuth 2.0
            if self.server.auth_code:
                return self.server.auth_code
            else:
                raise Exception("No authorization code received")
