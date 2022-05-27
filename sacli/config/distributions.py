# -*- coding: utf-8 -*-
#
# Please refer to AUTHORS.rst for a complete list of Copyright holders.
# Copyright (C) 2016-2022, Social Actions CLI Developers.

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

from .managers import native_managers, other_managers


distrodata = {
    'arch': {
        'managers': {
            'native': native_managers['pacman'],
            **other_managers,
        }
    },
    'alpine': {
        'managers': {
            'native': native_managers['apk'],
            **other_managers,
        }
    },
    'debian': {
        'managers': {
            'native': native_managers['apt'],
            **other_managers,
        }
    },
    'fedora': {
        'managers': {
            'native': native_managers['yum'],
            **other_managers,
        }
    },
    'centos': {
        'managers': {
            'native': native_managers['yum'],
            **other_managers,
        }
    },
    'gentoo': {
        'managers': {
            'native': native_managers['portage'],
            **other_managers,
        }
    }
}
