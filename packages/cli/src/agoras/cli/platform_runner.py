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
"""Dispatch CLI actions to platform wrappers."""

from agoras.platforms.discord.wrapper import main as discord
from agoras.platforms.facebook.wrapper import main as facebook
from agoras.platforms.instagram.wrapper import main as instagram
from agoras.platforms.linkedin.wrapper import main as linkedin
from agoras.platforms.telegram.wrapper import main as telegram
from agoras.platforms.threads.wrapper import main as threads
from agoras.platforms.tiktok.wrapper import main as tiktok
from agoras.platforms.whatsapp.wrapper import main as whatsapp
from agoras.platforms.x.wrapper import main as x
from agoras.platforms.youtube.wrapper import main as youtube


def execute_platform_action(**kwargs):
    """
    Route a legacy-shaped kwargs dict to the correct platform wrapper.

    Deprecation warnings for the twitter network alias belong in publish_main
    (legacy publish only); this function maps twitter to x silently.
    """
    network = kwargs.get("network")

    if network == "x":
        return x(kwargs)
    if network == "twitter":
        kwargs["network"] = "x"
        return x(kwargs)
    if network == "facebook":
        return facebook(kwargs)
    if network == "instagram":
        return instagram(kwargs)
    if network == "linkedin":
        return linkedin(kwargs)
    if network == "discord":
        return discord(kwargs)
    if network == "youtube":
        return youtube(kwargs)
    if network == "tiktok":
        return tiktok(kwargs)
    if network == "threads":
        return threads(kwargs)
    if network == "telegram":
        return telegram(kwargs)
    if network == "whatsapp":
        return whatsapp(kwargs)
    if not network:
        raise Exception("--network is a required argument.")
    raise Exception(f'"{network}" network not supported.')
