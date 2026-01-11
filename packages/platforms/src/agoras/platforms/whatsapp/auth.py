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
from typing import Any, Dict, Optional

from agoras.core.auth import BaseAuthManager
from .client import WhatsAppAPIClient


class WhatsAppAuthManager(BaseAuthManager):
    """WhatsApp authentication manager using Meta Graph API with direct access token authentication."""

    def __init__(self, access_token: str, phone_number_id: str,
                 business_account_id: Optional[str] = None):
        """
        Initialize WhatsApp authentication manager.

        Args:
            access_token (str): Meta Graph API access token
            phone_number_id (str): WhatsApp Business phone number ID
            business_account_id (str, optional): WhatsApp Business Account ID
        """
        super().__init__()
        self.access_token = access_token
        self.phone_number_id = phone_number_id
        self.business_account_id = business_account_id

    async def authenticate(self) -> bool:
        """
        Authenticate with WhatsApp Business API using Meta Graph API.

        Returns:
            bool: True if authentication successful, False otherwise
        """
        if not self._validate_credentials():
            return False

        try:
            # Validate access token and phone number access
            if not await self._validate_access_token():
                return False

            # Create client, authenticate it, and get phone number info
            if self.access_token:
                self.client = self._create_client(self.access_token)
                await self.client.authenticate()
                self.user_info = await self._get_user_info()

            return True
        except Exception:
            return False

    async def authorize(self) -> Optional[str]:
        """
        WhatsApp Business API uses direct access tokens (no OAuth flow).

        For WhatsApp, tokens are obtained from Meta Business Manager.
        This method is provided for interface compatibility but does not
        perform OAuth authorization.

        Returns:
            str or None: Access token if provided, None otherwise
        """
        if not self._validate_credentials():
            raise Exception('WhatsApp credentials are required for authorization.')

        # WhatsApp uses direct access tokens, so we just validate and return
        if await self._validate_access_token():
            return self.access_token
        return None

    async def _validate_access_token(self) -> bool:
        """
        Validate access token and phone number access via Graph API.

        Returns:
            bool: True if token is valid and phone number is accessible
        """
        try:
            from pyfacebook import GraphAPI
            graph_api = GraphAPI(access_token=self.access_token, version="23.0")
            response = graph_api.get_object(self.phone_number_id)
            return bool(response and response.get("verified_name"))
        except Exception:
            return False

    async def get_phone_info(self) -> Dict[str, Any]:
        """
        Retrieve phone number details via Graph API.

        Returns:
            dict: Phone number information from Graph API

        Raises:
            Exception: If phone info retrieval fails
        """
        def _sync_get_phone_info():
            from pyfacebook import GraphAPI
            graph_api = GraphAPI(access_token=self.access_token, version="23.0")
            return graph_api.get_object(self.phone_number_id)

        return await asyncio.to_thread(_sync_get_phone_info)

    def _create_client(self, access_token: str) -> WhatsAppAPIClient:
        """
        Create WhatsApp API client instance.

        Args:
            access_token (str): Access token for the client

        Returns:
            WhatsAppAPIClient: API client instance
        """
        return WhatsAppAPIClient(access_token=access_token, phone_number_id=self.phone_number_id)

    async def _get_user_info(self) -> Dict[str, Any]:
        """
        Get phone number/business information from WhatsApp API.

        Returns:
            dict: Phone number and business information

        Raises:
            Exception: If user info retrieval fails
        """
        if not self.client:
            raise Exception('No client available')

        def _sync_get_info():
            if not self.client:
                raise Exception('No client available')

            # Get phone number details
            phone_data = self.client.get_object(object_id=self.phone_number_id)

            # Verify phone number ID matches
            if phone_data.get('id') != self.phone_number_id:
                raise Exception(f"Phone number ID mismatch: {phone_data.get('id')} != {self.phone_number_id}")

            return phone_data

        return await asyncio.to_thread(_sync_get_info)

    def _validate_credentials(self) -> bool:
        """
        Validate that all required credentials are present.

        Returns:
            bool: True if all required credentials are present
        """
        return bool(self.access_token and self.phone_number_id)

    def _get_cache_filename(self) -> str:
        """
        Get cache filename for storing refresh token. DEPRECATED.

        Returns:
            str: Cache filename
        """
        return f'whatsapp-{self.phone_number_id}.json'

    def _get_platform_name(self) -> str:
        """
        Get the platform name for this auth manager.

        Returns:
            str: Platform name ('whatsapp')
        """
        return 'whatsapp'

    def _get_token_identifier(self) -> str:
        """
        Get unique identifier for token storage.

        Returns:
            str: Phone number ID as unique identifier
        """
        return self.phone_number_id
