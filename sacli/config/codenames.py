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

arch_versions = ['rolling']

alpine_version_url = 'http://dl-cdn.alpinelinux.org/alpine'
fedora_version_url = (
    'http://download-ib01.fedoraproject.org'
    '/pub/fedora/linux/releases'
)

olddebian_version_url = 'http://archive.debian.org/debian/dists'
olddebian_release_url_holder = (
    'http://archive.debian.org'
    '/debian/dists/{0}/Release'
)
debian_release_url_holder = (
    'http://deb.debian.org'
    '/debian/dists/{0}/Release'
)
debian_suites = [
    'oldoldoldstable', 'oldoldstable', 'oldstable',
    'stable', 'testing', 'unstable'
]
debian_oldversioning = [
    'buzz', 'rex', 'bo', 'hamm', 'slink',
    'potato', 'woody', 'sarge'
]

base_arch_codename_index = {
    'rolling': ['rolling']
}

base_alpine_codename_index = {
    '2.0': ['v2.0'],
    '2.1': ['v2.1'],
    '2.2': ['v2.2'],
    '2.3': ['v2.3'],
    '2.4': ['v2.4'],
    '2.5': ['v2.5'],
    '2.6': ['v2.6'],
    '2.7': ['v2.7'],
    '3.0': ['v3.0'],
    '3.1': ['v3.1'],
    '3.10': ['v3.10'],
    '3.11': ['v3.11'],
    '3.12': ['v3.12'],
    '3.13': ['v3.13'],
    '3.14': ['v3.14'],
    '3.15': ['v3.15'],
    '3.2': ['v3.2'],
    '3.3': ['v3.3'],
    '3.4': ['v3.4'],
    '3.5': ['v3.5'],
    '3.6': ['v3.6'],
    '3.7': ['v3.7'],
    '3.8': ['v3.8'],
    '3.9': ['v3.9'],
    '1.16': ['v1.16'],
    '1.15': ['v1.15'],
    '1.14': ['v1.14'],
    '1.13': ['v1.13'],
    '1.12': ['v1.12'],
    '1.11': ['v1.11'],
    '1.10': ['v1.10'],
    '1.9': ['v1.9'],
    '1.8': ['v1.8'],
    '1.7': ['v1.7'],
    '1.6': ['v1.6'],
    '1.5': ['v1.5'],
}

base_debian_codename_index = {
    '1.1': ['buzz'],
    '1.2': ['rex'],
    '1.3': ['bo'],
    '2.0': ['hamm'],
    '2.1': ['slink'],
    '2.2': ['potato'],
    '3.0': ['woody'],
    '3.1': ['sarge'],
    '4': ['etch'],
    '5': ['lenny'],
    '6': ['squeeze'],
    '7': ['wheezy'],
    '8': ['jessie'],
}

base_fedora_codename_index = {
    '1': ['yarrow'],
    '2': ['tettnang'],
    '3': ['heidelberg'],
    '4': ['stentz'],
    '5': ['bordeaux'],
    '6': ['zod'],
    '7': ['moonshine'],
    '8': ['werewolf'],
    '9': ['sulphur'],
    '10': ['cambridge'],
    '11': ['leonidas'],
    '12': ['constantine'],
    '13': ['goddard'],
    '14': ['laughlin'],
    '15': ['lovelock'],
    '16': ['verne'],
    '17': ['beefy-miracle'],
    '18': ['spherical-cow'],
    '19': ['schrodingers-cat'],
    '20': ['heisenbug'],
    'unstable': ['rawhide'],
}

base_centos_codename_index = {
    '1': ['1'],
    '2': ['2'],
    '3': ['3'],
    '4': ['4'],
    '5': ['5'],
    '6': ['6'],
    '7': ['7'],
    '8': ['8'],
    'stream8': ['stream8'],
    'stream9': ['stream9'],
}

base_gentoo_codename_index = {
    'rolling': ['rolling']
}
