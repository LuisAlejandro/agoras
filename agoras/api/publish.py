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

from ..core.twitter import main as twitter
from ..core.facebook import main as facebook
from ..core.instagram import main as instagram
from ..core.linkedin import main as linkedin


def main(**kwargs):

    network = kwargs.get('network')

    if network == 'twitter':
        twitter(kwargs)
    elif network == 'facebook':
        facebook(kwargs)
    elif network == 'instagram':
        instagram(kwargs)
    elif network == 'linkedin':
        linkedin(kwargs)
    elif network == '':
        raise Exception('--network is a required argument.')
    else:
        raise Exception(f'"{network}" network not supported.')
