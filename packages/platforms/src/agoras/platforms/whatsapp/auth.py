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
import os
from typing import Any, Dict, Optional

from agoras.core.auth import BaseAuthManager
from agoras.core.auth.exceptions import AuthenticationError

from .client import WhatsAppAPIClient


class WhatsAppAuthManager(BaseAuthManager):
    """WhatsApp authentication manager using Meta Graph API with direct access token authentication."""

    def __init__(self, access_token: Optional[str] = None, phone_number_id: Optional[str] = None,
                 business_account_id: Optional[str] = None):
        """
        Initialize WhatsApp authentication manager.

        Args:
            access_token (str, optional): Meta Graph API access token
            phone_number_id (str, optional): WhatsApp Business phone number ID
            business_account_id (str, optional): WhatsApp Business Account ID
        """
        super().__init__()
        # Try loading from storage first if credentials not provided
        if not access_token or not phone_number_id:
            loaded = self._load_credentials_from_storage()
            if loaded:
                if not access_token:
                    access_token = getattr(self, 'access_token', None)
                if not phone_number_id:
                    phone_number_id = getattr(self, 'phone_number_id', None)
                if not business_account_id:
                    business_account_id = getattr(self, 'business_account_id', None)

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
        Authorize WhatsApp by validating and storing access token credentials.

        Accepts credentials from parameters or environment variables, validates them,
        and stores them securely for future use.

        Returns:
            str: Success message if authorization successful, None otherwise
        """
        # Get credentials from parameters or environment variables
        access_token = self.access_token or os.environ.get('WHATSAPP_ACCESS_TOKEN')
        phone_number_id = self.phone_number_id or os.environ.get('WHATSAPP_PHONE_NUMBER_ID')
        business_account_id = self.business_account_id or os.environ.get('WHATSAPP_BUSINESS_ACCOUNT_ID')

        if not access_token or not phone_number_id:
            raise Exception('WhatsApp access token and phone number ID are required. '
                            'Provide via parameters or environment variables (WHATSAPP_ACCESS_TOKEN, '
                            'WHATSAPP_PHONE_NUMBER_ID).')

        # Set credentials for validation
        self.access_token = access_token
        self.phone_number_id = phone_number_id
        self.business_account_id = business_account_id

        # Validate credentials
        if not await self._validate_access_token():
            raise Exception('WhatsApp access token validation failed. Please check your credentials.')

        # Save credentials to secure storage
        self._save_credentials_to_storage(access_token, phone_number_id, business_account_id)

        return "Authorization successful. Credentials stored securely."

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
        if self.phone_number_id:
            return self.phone_number_id
        return "default"

    def _save_credentials_to_storage(self, access_token: str, phone_number_id: str,
                                     business_account_id: Optional[str] = None):
        """
        Save WhatsApp credentials to secure storage.

        Args:
            access_token (str): Meta Graph API access token
            phone_number_id (str): WhatsApp Business phone number ID
            business_account_id (str, optional): WhatsApp Business Account ID
        """
        platform_name = self._get_platform_name()
        identifier = phone_number_id

        token_data = {
            'access_token': access_token,
            'phone_number_id': phone_number_id,
            'business_account_id': business_account_id
        }

        self.token_storage.save_token(platform_name, identifier, token_data)

    def _load_credentials_from_storage(self) -> bool:
        """
        Load WhatsApp credentials from secure storage.

        Returns:
            bool: True if credentials were loaded, False otherwise
        """
        platform_name = self._get_platform_name()

        # Try to load with default identifier first
        identifier = "default"
        token_data = self.token_storage.load_token(platform_name, identifier)

        if not token_data:
            # If no default, try to find any stored token
            tokens = self.token_storage.list_tokens(platform_name)
            if tokens:
                # Use the first available token
                identifier = tokens[0][1]
                token_data = self.token_storage.load_token(platform_name, identifier)

        if token_data:
            self.access_token = token_data.get('access_token')
            self.phone_number_id = token_data.get('phone_number_id')
            self.business_account_id = token_data.get('business_account_id')
            return bool(self.access_token and self.phone_number_id)

        return False
