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

from agoras.platforms.x.wrapper import main as x
from agoras.platforms.facebook.wrapper import main as facebook
from agoras.platforms.instagram.wrapper import main as instagram
from agoras.platforms.linkedin.wrapper import main as linkedin
from agoras.platforms.discord.wrapper import main as discord
from agoras.platforms.youtube.wrapper import main as youtube
from agoras.platforms.tiktok.wrapper import main as tiktok
from agoras.platforms.threads.wrapper import main as threads
from agoras.platforms.telegram.wrapper import main as telegram
from agoras.platforms.whatsapp.wrapper import main as whatsapp


def main(**kwargs):
    import sys
    import warnings

    network = kwargs.get('network')

    if network == 'x':
        x(kwargs)
    elif network == 'twitter':
        print("Warning: The 'twitter' network name is deprecated. Use 'x' instead.", file=sys.stderr)
        warnings.warn(
            "The 'twitter' network name is deprecated. Use 'x' instead.",
            DeprecationWarning,
            stacklevel=2
        )
        x(kwargs)
    elif network == 'facebook':
        facebook(kwargs)
    elif network == 'instagram':
        instagram(kwargs)
    elif network == 'linkedin':
        linkedin(kwargs)
    elif network == 'discord':
        discord(kwargs)
    elif network == 'youtube':
        youtube(kwargs)
    elif network == 'tiktok':
        tiktok(kwargs)
    elif network == 'threads':
        threads(kwargs)
    elif network == 'telegram':
        telegram(kwargs)
    elif network == 'whatsapp':
        whatsapp(kwargs)
    elif network == '':
        raise Exception('--network is a required argument.')
    else:
        raise Exception(f'"{network}" network not supported.')
