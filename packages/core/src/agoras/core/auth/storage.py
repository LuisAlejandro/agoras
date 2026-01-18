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

import json
import os
from pathlib import Path
from typing import Any, Dict, Optional

from cryptography.fernet import Fernet


class SecureTokenStorage:
    """
    Secure encrypted token storage for OAuth credentials.

    This class provides encrypted storage for OAuth tokens and related metadata
    using Fernet symmetric encryption. Tokens are stored in ~/.agoras/tokens/
    with file permissions set to 600 (owner read/write only).
    """

    def __init__(self):
        """Initialize secure token storage."""
        self.token_dir = Path.home() / '.agoras' / 'tokens'
        self.key_file = Path.home() / '.agoras' / '.key'

        # Create directories if they don't exist
        self.token_dir.mkdir(parents=True, exist_ok=True)

        # Get or create encryption key
        self.key = self._get_or_create_key()
        self.cipher = Fernet(self.key)

    def _get_or_create_key(self) -> bytes:
        """
        Get existing encryption key or create a new one.

        Returns:
            bytes: Fernet encryption key
        """
        if self.key_file.exists():
            # Load existing key
            with open(self.key_file, 'rb') as f:
                return f.read()
        else:
            # Generate new key
            key = Fernet.generate_key()

            # Save key with secure permissions
            with open(self.key_file, 'wb') as f:
                f.write(key)

            # Set file permissions to 600 (owner read/write only)
            self.key_file.chmod(0o600)

            return key

    def save_token(self, platform: str, identifier: str, token_data: Dict[str, Any]):
        """
        Save encrypted token and metadata.

        Args:
            platform (str): Platform name (e.g., 'facebook', 'instagram')
            identifier (str): Unique identifier (e.g., user_id, username)
            token_data (dict): Token data including:
                - refresh_token: The refresh token
                - expires_at: Optional expiry timestamp
                - scopes: Optional list of scopes
                - Any other platform-specific metadata
        """
        filename = f"{platform}-{identifier}.token"
        filepath = self.token_dir / filename

        # Serialize token data to JSON
        json_data = json.dumps(token_data)

        # Encrypt the data
        encrypted_data = self.cipher.encrypt(json_data.encode())

        # Write encrypted data to file
        filepath.write_bytes(encrypted_data)

        # Set file permissions to 600 (owner read/write only)
        filepath.chmod(0o600)

    def load_token(self, platform: str, identifier: str) -> Optional[Dict[str, Any]]:
        """
        Load and decrypt token data.

        Args:
            platform (str): Platform name (e.g., 'facebook', 'instagram')
            identifier (str): Unique identifier (e.g., user_id, username)

        Returns:
            dict or None: Decrypted token data if found, None otherwise
        """
        filename = f"{platform}-{identifier}.token"
        filepath = self.token_dir / filename

        if not filepath.exists():
            return None

        try:
            # Read encrypted data
            encrypted_data = filepath.read_bytes()

            # Decrypt the data
            decrypted_data = self.cipher.decrypt(encrypted_data)

            # Parse JSON
            token_data = json.loads(decrypted_data.decode())

            return token_data
        except Exception:
            # If decryption or parsing fails, return None
            return None

    def delete_token(self, platform: str, identifier: str) -> bool:
        """
        Delete stored token.

        Args:
            platform (str): Platform name (e.g., 'facebook', 'instagram')
            identifier (str): Unique identifier (e.g., user_id, username)

        Returns:
            bool: True if token was deleted, False if it didn't exist
        """
        filename = f"{platform}-{identifier}.token"
        filepath = self.token_dir / filename

        if filepath.exists():
            filepath.unlink()
            return True

        return False

    def list_tokens(self, platform: Optional[str] = None) -> list:
        """
        List all stored tokens, optionally filtered by platform.

        Args:
            platform (str, optional): Filter by platform name

        Returns:
            list: List of (platform, identifier) tuples
        """
        # Known platform names for proper parsing
        known_platforms = [
            'facebook',
            'instagram',
            'linkedin',
            'discord',
            'telegram',
            'threads',
            'whatsapp',
            'x',
            'youtube',
            'tiktok']

        tokens = []

        for token_file in self.token_dir.glob('*.token'):
            stem = token_file.stem

            # Try to identify the platform by checking known platform prefixes
            file_platform = None
            identifier = None

            for known_platform in known_platforms:
                if stem.startswith(known_platform + '-'):
                    file_platform = known_platform
                    identifier = stem[len(known_platform) + 1:]  # Remove platform prefix and dash
                    break

            if file_platform and identifier:
                if platform is None or file_platform == platform:
                    tokens.append((file_platform, identifier))

        return tokens

    def seed_from_environment(self, platform: str, identifier: str) -> bool:
        """
        Seed storage from environment variables (CI/CD support).

        Checks for AGORAS_{PLATFORM}_REFRESH_TOKEN environment variable
        and saves it to storage if found. This enables CI/CD pipelines to
        inject credentials without requiring interactive OAuth flows.

        Args:
            platform (str): Platform name (e.g., 'facebook', 'instagram')
            identifier (str): Unique identifier (e.g., user_id, username)

        Returns:
            bool: True if token was seeded from environment, False otherwise
        """
        env_key = f'AGORAS_{platform.upper()}_REFRESH_TOKEN'
        refresh_token = os.environ.get(env_key)

        if refresh_token:
            token_data = {'refresh_token': refresh_token}
            self.save_token(platform, identifier, token_data)
            return True

        return False
