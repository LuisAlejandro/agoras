# -*- coding: utf-8 -*-
#
# Please refer to AUTHORS.rst for a complete list of Copyright holders.
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

import pytest
from agoras.core.interfaces import SocialNetwork
from agoras.platforms import (
    Discord,
    Facebook,
    Instagram,
    LinkedIn,
    Telegram,
    Threads,
    TikTok,
    WhatsApp,
    X,
    YouTube,
)


# Test that all platforms inherit from SocialNetwork
@pytest.mark.parametrize("platform_class", [
    Discord, Facebook, Instagram, LinkedIn, Telegram,
    Threads, TikTok, WhatsApp, X, YouTube
])
def test_platform_inherits_socialnetwork(platform_class):
    """Test that platform class inherits from SocialNetwork."""
    assert issubclass(platform_class, SocialNetwork)


# Test that all platforms can be instantiated
def test_facebook_instantiation():
    fb = Facebook(facebook_access_token='test')
    assert fb is not None


def test_instagram_instantiation():
    ig = Instagram(instagram_access_token='test')
    assert ig is not None


def test_linkedin_instantiation():
    li = LinkedIn(linkedin_access_token='test')
    assert li is not None


def test_discord_instantiation():
    dc = Discord(discord_token='test', discord_channel_id='test')
    assert dc is not None


def test_youtube_instantiation():
    yt = YouTube(youtube_client_id='test')
    assert yt is not None


def test_tiktok_instantiation():
    tt = TikTok(tiktok_access_token='test')
    assert tt is not None


def test_telegram_instantiation():
    tg = Telegram(telegram_bot_token='test', telegram_chat_id='test')
    assert tg is not None


def test_threads_instantiation():
    th = Threads(threads_access_token='test')
    assert th is not None


def test_whatsapp_instantiation():
    wa = WhatsApp(whatsapp_access_token='test', whatsapp_phone_number_id='test')
    assert wa is not None


def test_x_instantiation():
    x = X(x_api_key='test', x_api_secret='test')
    assert x is not None


# Test that all platforms have required methods
@pytest.mark.parametrize("platform_class", [
    Facebook, Instagram, LinkedIn, Discord, YouTube,
    TikTok, Telegram, Threads, WhatsApp, X
])
def test_platform_has_required_methods(platform_class):
    """Test that platform has required SocialNetwork methods."""
    assert hasattr(platform_class, '_initialize_client')
    assert hasattr(platform_class, 'disconnect')
    assert hasattr(platform_class, 'post')
