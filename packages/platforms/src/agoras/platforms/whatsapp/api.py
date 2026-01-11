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
from typing import Any, Dict, List, Optional

from .auth import WhatsAppAuthManager
from agoras.core.api_base import BaseAPI
from agoras.media.factory import MediaFactory


class WhatsAppAPI(BaseAPI):
    """
    WhatsApp API handler that centralizes WhatsApp Business API operations.

    Provides methods for WhatsApp authentication, token management,
    and all WhatsApp API operations including message sending, media messages,
    and business profile management.
    """

    def __init__(self, access_token: str, phone_number_id: str,
                 business_account_id: Optional[str] = None):
        """
        Initialize WhatsApp API instance.

        Args:
            access_token (str): Meta Graph API access token
            phone_number_id (str): WhatsApp Business phone number ID
            business_account_id (str, optional): WhatsApp Business Account ID
        """
        super().__init__(
            access_token=access_token,
            phone_number_id=phone_number_id,
            business_account_id=business_account_id
        )

        # Initialize the authentication manager
        self.auth_manager = WhatsAppAuthManager(
            access_token=access_token,
            phone_number_id=phone_number_id,
            business_account_id=business_account_id
        )

    async def authenticate(self):
        """
        Authenticate with WhatsApp API using the auth manager.

        Returns:
            WhatsAppAPI: Self for method chaining

        Raises:
            Exception: If authentication fails
        """
        if self._authenticated:
            return self

        success = await self.auth_manager.authenticate()
        if not success:
            raise Exception('WhatsApp authentication failed')

        # Set the client from auth manager for BaseAPI compatibility
        self.client = self.auth_manager.client
        self._authenticated = True
        return self

    async def disconnect(self):
        """
        Disconnect from WhatsApp API and clean up resources.
        """
        # Disconnect the client first
        if self.client:
            self.client.disconnect()

        # Clear auth manager tokens
        if self.auth_manager:
            self.auth_manager.access_token = None

        # Clear BaseAPI client
        self.client = None
        self._authenticated = False

    async def post(self, to: str, text: Optional[str] = None,
                   image_url: Optional[str] = None,
                   video_url: Optional[str] = None) -> str:
        """
        Create a WhatsApp message (text, image, or video).

        Args:
            to (str): Recipient phone number in E.164 format (e.g., +1234567890)
            text (str, optional): Message text content
            image_url (str, optional): Image URL to send
            video_url (str, optional): Video URL to send

        Returns:
            str: Message ID

        Raises:
            Exception: If message creation fails
        """
        self.auth_manager.ensure_authenticated()

        if not self.client:
            raise Exception('WhatsApp API not authenticated')

        await self._rate_limit_check('post', 1.0)

        try:
            # Handle video message
            if video_url:
                # Download and validate video using Media system
                video = MediaFactory.create_video(video_url, platform='whatsapp')
                try:
                    await video.download()
                    if video.content and video.file_type:
                        # Use original URL (WhatsApp handles URL downloads)
                        validated_url = video.url
                        # Send video message
                        message_id = await self.send_video(to, validated_url, text)
                        return message_id
                    else:
                        raise Exception(f'Failed to validate video: {video.url}')
                finally:
                    video.cleanup()

            # Handle image message
            elif image_url:
                # Download and validate image using Media system
                images = await MediaFactory.download_images([image_url])
                try:
                    if images and images[0].content and images[0].file_type:
                        # Use original URL (WhatsApp handles URL downloads)
                        validated_url = images[0].url
                        # Send image message
                        message_id = await self.send_image(to, validated_url, text)
                        return message_id
                    else:
                        raise Exception(f'Failed to validate image: {image_url}')
                finally:
                    for image in images:
                        image.cleanup()

            # Handle text-only message
            elif text:
                message_id = await self.send_message(to, text)
                return message_id

            else:
                raise Exception('No text, image, or video provided for WhatsApp message')

        except Exception as e:
            self._handle_api_error(e, 'WhatsApp post creation')
            raise

    async def send_message(self, to: str, text: str, buttons: Optional[List] = None) -> str:
        """
        Send a text message via WhatsApp.

        Args:
            to (str): Recipient phone number in E.164 format (e.g., +1234567890)
            text (str): Message text content
            buttons (list, optional): Interactive buttons (not fully implemented in Phase 2)

        Returns:
            str: Message ID

        Raises:
            Exception: If message sending fails
        """
        self.auth_manager.ensure_authenticated()

        if not self.client:
            raise Exception('WhatsApp API not authenticated')

        await self._rate_limit_check('send_message', 1.0)

        try:
            def _sync_send():
                response = self.client.send_message(to, text, buttons=buttons)
                return response['message_id']

            return await asyncio.to_thread(_sync_send)
        except Exception as e:
            self._handle_api_error(e, 'WhatsApp send_message')
            raise

    async def send_image(self, to: str, image_url: str, caption: Optional[str] = None) -> str:
        """
        Send an image message via WhatsApp.

        Args:
            to (str): Recipient phone number in E.164 format (e.g., +1234567890)
            image_url (str): Publicly accessible HTTPS URL of the image
            caption (str, optional): Image caption text

        Returns:
            str: Message ID

        Raises:
            Exception: If image sending fails
        """
        self.auth_manager.ensure_authenticated()

        if not self.client:
            raise Exception('WhatsApp API not authenticated')

        await self._rate_limit_check('send_image', 1.0)

        try:
            def _sync_send():
                response = self.client.send_image(to, image_url, caption=caption)
                return response['message_id']

            return await asyncio.to_thread(_sync_send)
        except Exception as e:
            self._handle_api_error(e, 'WhatsApp send_image')
            raise

    async def send_video(self, to: str, video_url: str, caption: Optional[str] = None) -> str:
        """
        Send a video message via WhatsApp.

        Args:
            to (str): Recipient phone number in E.164 format (e.g., +1234567890)
            video_url (str): Publicly accessible HTTPS URL of the video
            caption (str, optional): Video caption text

        Returns:
            str: Message ID

        Raises:
            Exception: If video sending fails
        """
        self.auth_manager.ensure_authenticated()

        if not self.client:
            raise Exception('WhatsApp API not authenticated')

        await self._rate_limit_check('send_video', 1.0)

        try:
            def _sync_send():
                response = self.client.send_video(to, video_url, caption=caption)
                return response['message_id']

            return await asyncio.to_thread(_sync_send)
        except Exception as e:
            self._handle_api_error(e, 'WhatsApp send_video')
            raise

    async def get_business_profile(self) -> Dict[str, Any]:
        """
        Get WhatsApp Business profile information.

        Returns:
            dict: Business profile data

        Raises:
            Exception: If profile retrieval fails
        """
        self.auth_manager.ensure_authenticated()

        if not self.client:
            raise Exception('WhatsApp API not authenticated')

        await self._rate_limit_check('get_business_profile', 1.0)

        try:
            def _sync_get_profile():
                endpoint = f"{self.client.phone_number_id}/whatsapp_business_profile"
                response = self.client.get_object(endpoint)
                if response and response.get("data"):
                    return response["data"][0]
                else:
                    raise Exception(f"Failed to get business profile: {response}")

            return await asyncio.to_thread(_sync_get_profile)
        except Exception as e:
            self._handle_api_error(e, 'WhatsApp get_business_profile')
            raise

    async def like(self, message_id: str) -> str:
        """
        Like a WhatsApp message (not supported).

        Args:
            message_id (str): Message ID to like

        Raises:
            Exception: Like not supported for WhatsApp
        """
        raise Exception('Like not supported for WhatsApp')

    async def delete(self, message_id: str) -> str:
        """
        Delete a WhatsApp message (not supported via API).

        Args:
            message_id (str): Message ID to delete

        Raises:
            Exception: Delete not supported for WhatsApp
        """
        raise Exception('Delete not supported for WhatsApp')

    async def share(self, message_id: str) -> str:
        """
        Share a WhatsApp message (not supported via API).

        Args:
            message_id (str): Message ID to share

        Raises:
            Exception: Share not supported for WhatsApp
        """
        raise Exception('Share not supported for WhatsApp')

    async def send_document(self, to: str, document_url: str, caption: Optional[str] = None, filename: Optional[str] = None) -> str:
        """
        Send a document message via WhatsApp.

        Args:
            to (str): Recipient phone number in E.164 format (e.g., +1234567890)
            document_url (str): Publicly accessible HTTPS URL of the document
            caption (str, optional): Document caption text
            filename (str, optional): Document filename

        Returns:
            str: Message ID

        Raises:
            Exception: If document sending fails
        """
        self.auth_manager.ensure_authenticated()

        if not self.client:
            raise Exception('WhatsApp API not authenticated')

        await self._rate_limit_check('send_document', 1.0)

        try:
            def _sync_send():
                response = self.client.send_document(to, document_url, caption=caption, filename=filename)
                return response['message_id']

            return await asyncio.to_thread(_sync_send)
        except Exception as e:
            self._handle_api_error(e, 'WhatsApp send_document')
            raise

    async def send_audio(self, to: str, audio_url: str) -> str:
        """
        Send an audio message via WhatsApp.

        Args:
            to (str): Recipient phone number in E.164 format (e.g., +1234567890)
            audio_url (str): Publicly accessible HTTPS URL of the audio file

        Returns:
            str: Message ID

        Raises:
            Exception: If audio sending fails
        """
        self.auth_manager.ensure_authenticated()

        if not self.client:
            raise Exception('WhatsApp API not authenticated')

        await self._rate_limit_check('send_audio', 1.0)

        try:
            def _sync_send():
                response = self.client.send_audio(to, audio_url)
                return response['message_id']

            return await asyncio.to_thread(_sync_send)
        except Exception as e:
            self._handle_api_error(e, 'WhatsApp send_audio')
            raise

    async def send_contact(self, to: str, contact_name: str, phone_number: str) -> str:
        """
        Send a contact card message via WhatsApp.

        Args:
            to (str): Recipient phone number in E.164 format (e.g., +1234567890)
            contact_name (str): Name of the contact
            phone_number (str): Phone number of the contact (E.164 format)

        Returns:
            str: Message ID

        Raises:
            Exception: If contact sending fails
        """
        self.auth_manager.ensure_authenticated()

        if not self.client:
            raise Exception('WhatsApp API not authenticated')

        await self._rate_limit_check('send_contact', 1.0)

        try:
            def _sync_send():
                # Format contact data for WhatsApp API
                # Extract first name from full name (simple approach)
                first_name = contact_name.split()[0] if contact_name else ""
                contacts = [{
                    "name": {
                        "formatted_name": contact_name,
                        "first_name": first_name
                    },
                    "phones": [{
                        "phone": phone_number,
                        "type": "CELL"
                    }]
                }]
                response = self.client.send_contact(to, contacts)
                return response['message_id']

            return await asyncio.to_thread(_sync_send)
        except Exception as e:
            self._handle_api_error(e, 'WhatsApp send_contact')
            raise

    async def send_location(self, to: str, latitude: float, longitude: float, name: Optional[str] = None, address: Optional[str] = None) -> str:
        """
        Send a location message via WhatsApp.

        Args:
            to (str): Recipient phone number in E.164 format (e.g., +1234567890)
            latitude (float): Latitude coordinate (-90 to 90)
            longitude (float): Longitude coordinate (-180 to 180)
            name (str, optional): Location name
            address (str, optional): Location address

        Returns:
            str: Message ID

        Raises:
            Exception: If location sending fails
        """
        self.auth_manager.ensure_authenticated()

        if not self.client:
            raise Exception('WhatsApp API not authenticated')

        # Validate coordinates
        if not (-90 <= latitude <= 90):
            raise Exception(f'Invalid latitude: {latitude}. Must be between -90 and 90.')
        if not (-180 <= longitude <= 180):
            raise Exception(f'Invalid longitude: {longitude}. Must be between -180 and 180.')

        await self._rate_limit_check('send_location', 1.0)

        try:
            def _sync_send():
                response = self.client.send_location(to, latitude, longitude, name=name, address=address)
                return response['message_id']

            return await asyncio.to_thread(_sync_send)
        except Exception as e:
            self._handle_api_error(e, 'WhatsApp send_location')
            raise

    async def send_template(self, to: str, template_name: str, language_code: str = "en", components: Optional[List[Dict]] = None) -> str:
        """
        Send a template message via WhatsApp.

        Args:
            to (str): Recipient phone number in E.164 format (e.g., +1234567890)
            template_name (str): Name of the pre-approved template
            language_code (str): Language code (ISO 639-1 format, default: "en")
            components (list, optional): Template components (parameters, buttons, etc.)

        Returns:
            str: Message ID

        Raises:
            Exception: If template sending fails
        """
        self.auth_manager.ensure_authenticated()

        if not self.client:
            raise Exception('WhatsApp API not authenticated')

        if not template_name:
            raise Exception('Template name is required.')

        await self._rate_limit_check('send_template', 1.0)

        try:
            def _sync_send():
                response = self.client.send_template(to, template_name, language_code=language_code, components=components)
                return response['message_id']

            return await asyncio.to_thread(_sync_send)
        except Exception as e:
            self._handle_api_error(e, 'WhatsApp send_template')
            raise
