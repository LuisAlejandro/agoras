# -*- coding: utf-8 -*-
#
# Please refer to AUTHORS.rst for a complete list of Copyright holders.
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
"""
Parameter converter for CLI.

This module converts between new and legacy parameter formats.
This is a skeleton implementation to be fully populated in later phases.
"""

from argparse import Namespace
from typing import Any, Dict


class ParameterConverter:
    """Convert between new and legacy parameter formats."""

    # Platform-specific parameter mappings
    # To be fully populated in Phase 3 (Week 5)
    PLATFORM_MAPPINGS: Dict[str, Dict[str, str]] = {
        "x": {
            # Auth
            "consumer_key": "twitter_consumer_key",
            "consumer_secret": "twitter_consumer_secret",
            "oauth_token": "twitter_oauth_token",
            "oauth_secret": "twitter_oauth_secret",
            # Content
            "post_id": "tweet_id",
            "video_url": "twitter_video_url",
            "video_title": "twitter_video_title",
        },
        "twitter": {
            # Auth
            "consumer_key": "twitter_consumer_key",
            "consumer_secret": "twitter_consumer_secret",
            "oauth_token": "twitter_oauth_token",
            "oauth_secret": "twitter_oauth_secret",
            # Content
            "post_id": "tweet_id",
            "video_url": "twitter_video_url",
            "video_title": "twitter_video_title",
        },
        "facebook": {
            "client_id": "facebook_client_id",
            "client_secret": "facebook_client_secret",
            "app_id": "facebook_app_id",
            "object_id": "facebook_object_id",
            "post_id": "facebook_post_id",
            "profile_id": "facebook_profile_id",
            "video_url": "facebook_video_url",
            "video_title": "facebook_video_title",
            "video_description": "facebook_video_description",
            "video_type": "facebook_video_type",
        },
        "instagram": {
            "client_id": "instagram_client_id",
            "client_secret": "instagram_client_secret",
            "object_id": "instagram_object_id",
            "post_id": "instagram_post_id",
            "video_url": "instagram_video_url",
            "video_caption": "instagram_video_caption",
            "video_type": "instagram_video_type",
        },
        "linkedin": {
            "client_id": "linkedin_client_id",
            "client_secret": "linkedin_client_secret",
            "object_id": "linkedin_object_id",
            "post_id": "linkedin_post_id",
            "parent_post_id": "linkedin_parent_post_id",
            "video_url": "linkedin_video_url",
            "video_title": "linkedin_video_title",
        },
        "discord": {
            "bot_token": "discord_bot_token",
            "server_name": "discord_server_name",
            "channel_name": "discord_channel_name",
            "post_id": "discord_post_id",
            "video_url": "discord_video_url",
            "video_title": "discord_video_title",
        },
        "youtube": {
            "client_id": "youtube_client_id",
            "client_secret": "youtube_client_secret",
            "video_id": "youtube_video_id",
            "post_id": "youtube_video_id",
            "video_url": "youtube_video_url",
            "title": "youtube_title",
            "description": "youtube_description",
            "category_id": "youtube_category_id",
            "privacy": "youtube_privacy_status",
            "keywords": "youtube_keywords",
        },
        "tiktok": {
            "client_key": "tiktok_client_key",
            "client_secret": "tiktok_client_secret",
            "username": "tiktok_username",
            "video_url": "tiktok_video_url",
            "title": "tiktok_title",
            "privacy": "tiktok_privacy_status",
            "allow_comments": "tiktok_allow_comments",
            "allow_duet": "tiktok_allow_duet",
            "allow_stitch": "tiktok_allow_stitch",
            "auto_add_music": "tiktok_auto_add_music",
            "brand_organic": "tiktok_brand_organic",
            "brand_content": "tiktok_brand_content",
            "description": "tiktok_description",
        },
        "threads": {
            "app_id": "threads_app_id",
            "app_secret": "threads_app_secret",
            "post_id": "threads_post_id",
            "video_url": "threads_video_url",
            "video_title": "threads_video_title",
            "who_can_reply": "threads_who_can_reply",
        },
        "telegram": {
            "bot_token": "telegram_bot_token",
            "chat_id": "telegram_chat_id",
            "parse_mode": "telegram_parse_mode",
            "message_id": "telegram_message_id",
            "post_id": "telegram_message_id",
            "video_url": "video_url",
            "video_title": "video_title",
        },
        "whatsapp": {
            "access_token": "whatsapp_access_token",
            "phone_number_id": "whatsapp_phone_number_id",
            "business_account_id": "whatsapp_business_account_id",
            "recipient": "whatsapp_recipient",
            "message_id": "whatsapp_message_id",
            "template_name": "whatsapp_template_name",
            "language_code": "whatsapp_template_language",
            "template_components": "whatsapp_template_components",
            "video_url": "video_url",
            "video_title": "video_title",
        },
    }

    # Common parameter mappings (apply to all platforms)
    COMMON_MAPPINGS = {
        # Content parameters
        "text": "status_text",
        "link": "status_link",
        "image_1": "status_image_url_1",
        "image_2": "status_image_url_2",
        "image_3": "status_image_url_3",
        "image_4": "status_image_url_4",
        # Feed parameters
        "feed_url": "feed_url",
        # Google Sheets parameters
        "sheets_id": "google_sheets_id",
        "sheets_name": "google_sheets_name",
        "sheets_client_email": "google_sheets_client_email",
        "sheets_private_key": "google_sheets_private_key",
        # System parameters
        "loglevel": "loglevel",
    }

    def __init__(self, platform: str):
        """
        Initialize parameter converter for a specific platform.

        Args:
            platform: Platform name
        """
        self.platform = platform
        self.platform_mapping = self.PLATFORM_MAPPINGS.get(platform, {})

    def convert_to_legacy(self, args: Namespace) -> Dict[str, Any]:
        """
        Convert new CLI args to legacy format for core modules.

        Args:
            args: Parsed arguments from new CLI

        Returns:
            Dictionary of legacy-format arguments
        """
        legacy_args = {
            "network": self.platform,
            "action": getattr(args, "action", None),
        }

        # Convert platform-specific parameters
        skip_params = {
            "command",
            "content",
            "help",
        }
        for new_param, value in vars(args).items():
            if new_param in skip_params:
                continue
            # Skip None values
            if value is None:
                continue

            # Preserve explicit False / 0; only skip blank strings
            if isinstance(value, str) and value.strip() == "":
                continue

            # Check platform-specific mapping
            if new_param in self.platform_mapping:
                legacy_param = self.platform_mapping[new_param]
                legacy_args[legacy_param] = value
            # Check common mapping
            elif new_param in self.COMMON_MAPPINGS:
                legacy_param = self.COMMON_MAPPINGS[new_param]
                legacy_args[legacy_param] = value
            # Pass through unchanged (entries, embeds, provenance, …)
            else:
                legacy_args[new_param] = value

        return legacy_args
