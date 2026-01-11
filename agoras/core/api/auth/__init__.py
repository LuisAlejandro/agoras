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

"""
Authentication module v2 using Authlib for social network integrations.

This module provides authentication management using the Authlib package
to replace custom OAuth implementations with standardized OAuth flows.

Currently supported platforms:
- Discord: DiscordAuthManager (Bot Token Authentication)
- Facebook: FacebookAuthManager (OAuth 2.0 with compliance fixes)
- Instagram: InstagramAuthManager (OAuth 2.0 via Facebook)
- LinkedIn: LinkedInAuthManager (OAuth 2.0)
- Telegram: TelegramAuthManager (Bot Token Authentication)
- Threads: ThreadsAuthManager (OAuth 2.0 via Meta)
- TikTok: TikTokAuthManager (OAuth 2.0 with PKCE and compliance fixes)
- WhatsApp: WhatsAppAuthManager (Direct Access Token via Meta Graph API)
- X: XAuthManager (OAuth 1.0a)
- YouTube: YouTubeAuthManager (OAuth 2.0 via Google)
"""

from .base import BaseAuthManager
from .callback_server import OAuthCallbackServer
from .discord import DiscordAuthManager
from .exceptions import AuthenticationError
from .facebook import FacebookAuthManager
from .instagram import InstagramAuthManager
from .linkedin import LinkedInAuthManager
from .storage import SecureTokenStorage
from .telegram import TelegramAuthManager
from .threads import ThreadsAuthManager
from .tiktok import TikTokAuthManager
from .whatsapp import WhatsAppAuthManager
from .x import XAuthManager
from .youtube import YouTubeAuthManager

__all__ = [
    'AuthenticationError',
    'BaseAuthManager',
    'DiscordAuthManager',
    'FacebookAuthManager',
    'InstagramAuthManager',
    'LinkedInAuthManager',
    'OAuthCallbackServer',
    'SecureTokenStorage',
    'TelegramAuthManager',
    'ThreadsAuthManager',
    'TikTokAuthManager',
    'WhatsAppAuthManager',
    'XAuthManager',
    'YouTubeAuthManager',
]
