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
"""agoras.platforms.whatsapp.client module."""

from typing import Any, Dict, List, Optional

from pyfacebook import GraphAPI


class WhatsAppAPIClient:
    """
    WhatsApp API client that centralizes WhatsApp Business API operations.

    Handles all WhatsApp API interactions through Meta's GraphAPI,
    including message sending, media uploads, and business profile management.
    Uses the same GraphAPI as Facebook and Instagram since WhatsApp is part of Meta's ecosystem.
    """

    def __init__(self, access_token: str, phone_number_id: str):
        """
        Initialize WhatsApp API client.

        Args:
            access_token (str): Meta Graph API access token
            phone_number_id (str): WhatsApp Business phone number ID
        """
        self.access_token = access_token
        self.phone_number_id = phone_number_id
        self.graph_api: Optional[GraphAPI] = None
        self.api_version = "v23.0"
        self._authenticated = False

    async def authenticate(self) -> bool:
        """
        Authenticate and initialize GraphAPI client.

        Returns:
            bool: True if authentication successful

        Raises:
            Exception: If authentication fails
        """
        if self._authenticated:
            return True

        if not self.access_token:
            raise Exception("WhatsApp access token is required")

        try:
            self.graph_api = GraphAPI(access_token=self.access_token, version=self.api_version)
            self._authenticated = True
            return True
        except Exception as e:
            raise Exception(f"WhatsApp client authentication failed: {str(e)}")

    def disconnect(self):
        """
        Disconnect and clean up client resources.
        """
        self.graph_api = None
        self._authenticated = False

    def get_object(self, object_id: str, fields: Optional[str] = None) -> Dict[str, Any]:
        """
        Get a WhatsApp/Graph API object.

        Args:
            object_id (str): Object ID (e.g., phone number ID)
            fields (str, optional): Fields to retrieve

        Returns:
            dict: Object data from Graph API

        Raises:
            Exception: If get fails
        """
        if not self.graph_api:
            raise Exception("WhatsApp GraphAPI not initialized")

        try:
            if fields:
                return self.graph_api.get_object(object_id=object_id, fields=fields)
            else:
                return self.graph_api.get_object(object_id=object_id)
        except Exception as e:
            raise Exception(f"WhatsApp get_object failed: {str(e)}")

    def post_object(self, object_id: str, connection: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Post to a WhatsApp/Graph API object connection using direct HTTP request.

        Args:
            object_id (str): Object ID (e.g., phone number ID)
            connection (str): Connection type (messages, etc.)
            data (dict, optional): Data to post

        Returns:
            dict: Response from Graph API

        Raises:
            Exception: If post fails
        """
        if not self.access_token:
            raise Exception("WhatsApp access token not available")

        import requests

        url = f"https://graph.facebook.com/{self.api_version}/{object_id}"
        if connection:
            url += f"/{connection}"

        headers = {"Authorization": f"Bearer {self.access_token}", "Content-Type": "application/json"}

        try:
            response = requests.post(url, json=data or {}, headers=headers, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            # Include response body in error for debugging
            try:
                error_data = response.json()
                raise Exception(f"WhatsApp post_object failed: {response.status_code} {response.reason} - {error_data}")
            except BaseException:
                raise Exception(f"WhatsApp post_object failed: {str(e)}")
        except requests.exceptions.RequestException as e:
            raise Exception(f"WhatsApp post_object failed: {str(e)}")

    def send_message(self, to: str, text: str, buttons: Optional[List] = None) -> Dict[str, Any]:
        """
        Send text message via Graph API.

        Args:
            to (str): Recipient phone number in E.164 format (e.g., +1234567890)
            text (str): Message text content
            buttons (list, optional): Interactive buttons (not implemented in Phase 2)

        Returns:
            dict: Response with message_id and status

        Raises:
            Exception: If message sending fails
        """
        if not self.graph_api:
            raise Exception("WhatsApp GraphAPI not initialized")

        payload = {"messaging_product": "whatsapp", "to": to, "type": "text", "text": {"body": text}}

        # Note: Interactive buttons support will be added in future phases
        if buttons:
            payload["type"] = "interactive"
            payload["interactive"] = {"type": "button", "body": {"text": text}, "action": {"buttons": buttons}}

        try:
            response = self.post_object(object_id=self.phone_number_id, connection="messages", data=payload)

            if response and response.get("messages"):
                return {"message_id": response["messages"][0]["id"], "status": "sent"}
            else:
                raise Exception(f"WhatsApp API error: {response}")
        except Exception as e:
            raise Exception(f"WhatsApp send_message failed: {str(e)}")

    def upload_media(self, file_bytes: bytes, mime_type: str, filename: str = "media") -> str:
        """
        Upload media bytes to WhatsApp Cloud API.

        Args:
            file_bytes (bytes): Raw media content
            mime_type (str): MIME type of the media
            filename (str): Filename for multipart upload

        Returns:
            str: Uploaded media ID

        Raises:
            Exception: If upload fails
        """
        if not self.access_token:
            raise Exception("WhatsApp access token not available")

        import requests

        url = f"https://graph.facebook.com/{self.api_version}/{self.phone_number_id}/media"
        headers = {"Authorization": f"Bearer {self.access_token}"}
        files = {"file": (filename, file_bytes, mime_type)}
        data = {"messaging_product": "whatsapp", "type": mime_type}

        try:
            response = requests.post(url, headers=headers, files=files, data=data, timeout=60)
            response.raise_for_status()
            media_id = response.json().get("id")
            if not media_id:
                raise Exception(f"WhatsApp media upload missing id: {response.text}")
            return str(media_id)
        except requests.exceptions.HTTPError as e:
            try:
                error_data = response.json()
                raise Exception(
                    f"WhatsApp upload_media failed: {response.status_code} {response.reason} - {error_data}"
                )
            except BaseException:
                raise Exception(f"WhatsApp upload_media failed: {str(e)}")
        except requests.exceptions.RequestException as e:
            raise Exception(f"WhatsApp upload_media failed: {str(e)}")

    def send_image(
        self,
        to: str,
        image_url: Optional[str] = None,
        caption: Optional[str] = None,
        image_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Send image message via Graph API.

        Args:
            to (str): Recipient phone number in E.164 format (e.g., +1234567890)
            image_url (str, optional): Publicly accessible HTTPS URL of the image
            caption (str, optional): Image caption text
            image_id (str, optional): Uploaded WhatsApp media ID

        Returns:
            dict: Response with message_id and status

        Raises:
            Exception: If image sending fails
        """
        if not self.graph_api:
            raise Exception("WhatsApp GraphAPI not initialized")

        if image_id:
            image_payload: Dict[str, Any] = {"id": image_id}
        elif image_url:
            image_payload = {"link": image_url}
        else:
            raise Exception("WhatsApp send_image requires image_url or image_id")

        payload = {"messaging_product": "whatsapp", "to": to, "type": "image", "image": image_payload}

        if caption:
            payload["image"]["caption"] = caption

        try:
            response = self.post_object(object_id=self.phone_number_id, connection="messages", data=payload)

            if response and response.get("messages"):
                return {"message_id": response["messages"][0]["id"], "status": "sent"}
            else:
                raise Exception(f"WhatsApp API error: {response}")
        except Exception as e:
            raise Exception(f"WhatsApp send_image failed: {str(e)}")

    def send_video(
        self,
        to: str,
        video_url: Optional[str] = None,
        caption: Optional[str] = None,
        video_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Send video message via Graph API.

        Args:
            to (str): Recipient phone number in E.164 format (e.g., +1234567890)
            video_url (str, optional): Publicly accessible HTTPS URL of the video
            caption (str, optional): Video caption text
            video_id (str, optional): Uploaded WhatsApp media ID

        Returns:
            dict: Response with message_id and status

        Raises:
            Exception: If video sending fails
        """
        if not self.graph_api:
            raise Exception("WhatsApp GraphAPI not initialized")

        if video_id:
            video_payload: Dict[str, Any] = {"id": video_id}
        elif video_url:
            video_payload = {"link": video_url}
        else:
            raise Exception("WhatsApp send_video requires video_url or video_id")

        payload = {"messaging_product": "whatsapp", "to": to, "type": "video", "video": video_payload}

        if caption:
            payload["video"]["caption"] = caption

        try:
            response = self.post_object(object_id=self.phone_number_id, connection="messages", data=payload)

            if response and response.get("messages"):
                return {"message_id": response["messages"][0]["id"], "status": "sent"}
            else:
                raise Exception(f"WhatsApp API error: {response}")
        except Exception as e:
            raise Exception(f"WhatsApp send_video failed: {str(e)}")

    def send_template(
        self, to: str, template_name: str, language_code: str = "en", components: Optional[List[Dict]] = None
    ) -> Dict[str, Any]:
        """
        Send template message via Graph API.

        Args:
            to (str): Recipient phone number in E.164 format (e.g., +1234567890)
            template_name (str): Name of the pre-approved template
            language_code (str): Language code (ISO 639-1 format, default: "en")
            components (list, optional): Template components (parameters, buttons, etc.)

        Returns:
            dict: Response with message_id and status

        Raises:
            Exception: If template sending fails
        """
        if not self.graph_api:
            raise Exception("WhatsApp GraphAPI not initialized")

        payload = {
            "messaging_product": "whatsapp",
            "to": to,
            "type": "template",
            "template": {"name": template_name, "language": {"code": language_code}},
        }

        if components:
            payload["template"]["components"] = components

        try:
            response = self.post_object(object_id=self.phone_number_id, connection="messages", data=payload)

            if response and response.get("messages"):
                return {"message_id": response["messages"][0]["id"], "status": "sent"}
            else:
                raise Exception(f"WhatsApp API error: {response}")
        except Exception as e:
            raise Exception(f"WhatsApp send_template failed: {str(e)}")
