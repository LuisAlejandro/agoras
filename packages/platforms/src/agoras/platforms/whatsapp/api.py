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
"""agoras.platforms.whatsapp.api module."""

import asyncio
from typing import Any, Dict, List, Optional

from agoras.core.api_base import (
    BaseAPI,
    guard_client_presence,
    guard_ensure_auth_manager,
    guard_error_wrap,
    guard_rate_limit,
)
from agoras.core.auth import raise_authentication_error_from_manager
from agoras.media import create_video, download_images

from .auth import WhatsAppAuthManager


class WhatsAppAPI(BaseAPI):
    """
    WhatsApp API handler that centralizes WhatsApp Business API operations.

    Provides methods for WhatsApp authentication, token management,
    and all WhatsApp API operations including message sending, media messages,
    and business profile management.
    """

    # Guard message templates (read by the composable guard decorators)
    _not_authenticated_message = "WhatsApp API not authenticated"
    _client_not_available_message = "WhatsApp API not authenticated"

    def __init__(self, access_token: str, phone_number_id: str, business_account_id: Optional[str] = None):
        """
        Initialize WhatsApp API instance.

        Args:
            access_token (str): Meta Graph API access token
            phone_number_id (str): WhatsApp Business phone number ID
            business_account_id (str, optional): WhatsApp Business Account ID
        """
        super().__init__(
            access_token=access_token, phone_number_id=phone_number_id, business_account_id=business_account_id
        )

        # Initialize the authentication manager
        self.auth_manager = WhatsAppAuthManager(
            access_token=access_token, phone_number_id=phone_number_id, business_account_id=business_account_id
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
            raise_authentication_error_from_manager(self.auth_manager)

        return await super().authenticate()

    @guard_ensure_auth_manager
    @guard_client_presence
    @guard_rate_limit("post", 1.0)
    @guard_error_wrap("WhatsApp post creation")
    async def post(
        self, to: str, text: Optional[str] = None, image_url: Optional[str] = None, video_url: Optional[str] = None
    ) -> str:
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
        # Handle video message
        if video_url:
            # Download and validate video using Media system
            video = create_video(video_url, platform="whatsapp")
            try:
                await video.download()
                if video.content and video.file_type:
                    # Use original URL (WhatsApp handles URL downloads)
                    validated_url = video.url
                    # Send video message
                    message_id = await self.send_video(to, validated_url, text)
                    return message_id
                else:
                    raise Exception(f"Failed to validate video: {video.url}")
            finally:
                video.cleanup()

        # Handle image message
        elif image_url:
            # Download and validate image using Media system
            images = await download_images(
                [image_url],
                platform="whatsapp",
            )
            try:
                if images and images[0].content and images[0].file_type:
                    # Use original URL (WhatsApp handles URL downloads)
                    validated_url = images[0].url
                    # Send image message
                    message_id = await self.send_image(to, validated_url, text)
                    return message_id
                else:
                    raise Exception(f"Failed to validate image: {image_url}")
            finally:
                for image in images:
                    image.cleanup()

        # Handle text-only message
        elif text:
            message_id = await self.send_message(to, text)
            return message_id

        else:
            raise Exception("No text, image, or video provided for WhatsApp message")

    @guard_ensure_auth_manager
    @guard_client_presence
    @guard_rate_limit("send_message", 1.0)
    @guard_error_wrap("WhatsApp send_message")
    async def send_message(
        self, to: str, text: str, buttons: Optional[List] = None, context: Optional[Dict] = None
    ) -> str:
        """
        Send a text message via WhatsApp.

        Args:
            to (str): Recipient phone number in E.164 format (e.g., +1234567890)
            text (str): Message text content
            buttons (list, optional): Interactive buttons (not fully implemented in Phase 2)
            context (dict, optional): Reply context (e.g. {"message_id": <id>})

        Returns:
            str: Message ID

        Raises:
            Exception: If message sending fails
        """
        client = self.client
        assert client is not None

        def _sync_send():
            response = client.send_message(to, text, buttons=buttons, context=context)
            return response["message_id"]

        return await asyncio.to_thread(_sync_send)

    @guard_ensure_auth_manager
    @guard_client_presence
    @guard_rate_limit("upload_media", 1.0)
    @guard_error_wrap("WhatsApp upload_media")
    async def upload_media(self, file_bytes: bytes, mime_type: str, filename: str = "media") -> str:
        """
        Upload media bytes to WhatsApp and return a media ID.

        Args:
            file_bytes (bytes): Raw media content
            mime_type (str): MIME type
            filename (str): Multipart filename

        Returns:
            str: Uploaded media ID
        """
        client = self.client
        assert client is not None

        def _sync_upload():
            return client.upload_media(file_bytes, mime_type, filename=filename)

        return await asyncio.to_thread(_sync_upload)

    @guard_ensure_auth_manager
    @guard_client_presence
    @guard_rate_limit("send_image", 1.0)
    @guard_error_wrap("WhatsApp send_image")
    async def send_image(
        self,
        to: str,
        image_url: Optional[str] = None,
        caption: Optional[str] = None,
        image_id: Optional[str] = None,
        context: Optional[Dict] = None,
    ) -> str:
        """
        Send an image message via WhatsApp.

        Args:
            to (str): Recipient phone number in E.164 format (e.g., +1234567890)
            image_url (str): Publicly accessible HTTPS URL of the image
            caption (str, optional): Image caption text
            image_id (str, optional): Uploaded WhatsApp media ID
            context (dict, optional): Reply context (e.g. {"message_id": <id>})

        Returns:
            str: Message ID

        Raises:
            Exception: If image sending fails
        """
        client = self.client
        assert client is not None

        def _sync_send():
            response = client.send_image(to, image_url=image_url, caption=caption, image_id=image_id, context=context)
            return response["message_id"]

        return await asyncio.to_thread(_sync_send)

    @guard_ensure_auth_manager
    @guard_client_presence
    @guard_rate_limit("send_video", 1.0)
    @guard_error_wrap("WhatsApp send_video")
    async def send_video(
        self,
        to: str,
        video_url: Optional[str] = None,
        caption: Optional[str] = None,
        video_id: Optional[str] = None,
        context: Optional[Dict] = None,
    ) -> str:
        """
        Send a video message via WhatsApp.

        Args:
            to (str): Recipient phone number in E.164 format (e.g., +1234567890)
            video_url (str): Publicly accessible HTTPS URL of the video
            caption (str, optional): Video caption text
            video_id (str, optional): Uploaded WhatsApp media ID
            context (dict, optional): Reply context (e.g. {"message_id": <id>})

        Returns:
            str: Message ID

        Raises:
            Exception: If video sending fails
        """
        client = self.client
        assert client is not None

        def _sync_send():
            response = client.send_video(to, video_url=video_url, caption=caption, video_id=video_id, context=context)
            return response["message_id"]

        return await asyncio.to_thread(_sync_send)

    async def reply(
        self,
        to: str,
        post_id: str,
        text: Optional[str] = None,
        image_url: Optional[str] = None,
        image_id: Optional[str] = None,
        video_url: Optional[str] = None,
        video_id: Optional[str] = None,
    ) -> str:
        """
        Reply to a WhatsApp message with optional media.

        Args:
            to (str): Recipient phone number in E.164 format (e.g., +1234567890)
            post_id (str): Message ID to reply to
            text (str, optional): Reply text/caption
            image_url (str, optional): Image URL to send
            image_id (str, optional): Uploaded WhatsApp media ID
            video_url (str, optional): Video URL to send
            video_id (str, optional): Uploaded WhatsApp media ID

        Returns:
            str: Reply message ID

        Raises:
            Exception: If reply sending fails
        """
        context = {"message_id": post_id}
        if image_id or image_url:
            return await self.send_image(to, image_url=image_url, caption=text, image_id=image_id, context=context)
        if video_id or video_url:
            return await self.send_video(to, video_url=video_url, caption=text, video_id=video_id, context=context)
        return await self.send_message(to, text or "", context=context)

    @guard_ensure_auth_manager
    @guard_client_presence
    @guard_rate_limit("get_business_profile", 1.0)
    @guard_error_wrap("WhatsApp get_business_profile")
    async def get_business_profile(self) -> Dict[str, Any]:
        """
        Get WhatsApp Business profile information.

        Returns:
            dict: Business profile data

        Raises:
            Exception: If profile retrieval fails
        """
        client = self.client
        assert client is not None

        def _sync_get_profile():
            endpoint = f"{client.phone_number_id}/whatsapp_business_profile"
            response = client.get_object(endpoint)
            if response and response.get("data"):
                return response["data"][0]
            else:
                raise Exception(f"Failed to get business profile: {response}")

        return await asyncio.to_thread(_sync_get_profile)

    async def like(self, message_id: str) -> str:
        """
        Like a WhatsApp message (not supported).

        Args:
            message_id (str): Message ID to like

        Raises:
            Exception: Like not supported for WhatsApp
        """
        raise Exception("Like not supported for WhatsApp")

    async def delete(self, message_id: str) -> str:
        """
        Delete a WhatsApp message (not supported via API).

        Args:
            message_id (str): Message ID to delete

        Raises:
            Exception: Delete not supported for WhatsApp
        """
        raise Exception("Delete not supported for WhatsApp")

    async def share(self, message_id: str) -> str:
        """
        Share a WhatsApp message (not supported via API).

        Args:
            message_id (str): Message ID to share

        Raises:
            Exception: Share not supported for WhatsApp
        """
        raise Exception("Share not supported for WhatsApp")

    @guard_ensure_auth_manager
    @guard_client_presence
    async def send_template(
        self, to: str, template_name: str, language_code: str = "en", components: Optional[List[Dict]] = None
    ) -> str:
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
        client = self.client
        assert client is not None
        if not template_name:
            raise Exception("Template name is required.")

        await self._rate_limit_check("send_template", 1.0)

        def _sync_send():
            response = client.send_template(to, template_name, language_code=language_code, components=components)
            return response["message_id"]

        try:
            return await asyncio.to_thread(_sync_send)
        except Exception as e:
            self._handle_api_error(e, "WhatsApp send_template")
            raise
