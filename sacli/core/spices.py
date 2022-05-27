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

from .errors import sacliAreEmpty, ThereAreNoCommands
from .managers import Script, Yum, Apt, Pacman, Portage, Apk, \
    Npm, Yarn, Pip, Bundler


class sacli(object):

    native_managers_map = {
        'apt-get': Apt,
        'apt': Apt,
        'yum': Yum,
        'apk': Apk,
        'pacman': Pacman,
        'emerge': Portage,
        'portage': Portage,
        'custom': Script
    }

    distribution_map = {
        'debian': Apt,
        'fedora': Yum,
        'alpine': Apk,
        'arch': Pacman,
        'gentoo': Portage,
        'centos': Yum
    }

    other_managers_map = {
        'npm': Npm,
        'yarn': Yarn,
        'pip': Pip,
        'bundler': Bundler,
    }

    def __init__(self, content):
        eqmap = {
            **self.native_managers_map,
            **self.distribution_map,
            **self.other_managers_map,
        }
        allowed_managers = eqmap.keys()

        self.__eqmap = eqmap
        self.__allowed_managers = allowed_managers

        if not content:
            raise sacliAreEmpty()

        self.content = content
        self.commandlist = []

        self.generate_commandlist()

        if not self.commandlist:
            raise ThereAreNoCommands()

    def generate_commandlist(self):
        for manager, data in self.content['managers'].items():
            if manager not in self.__allowed_managers:
                continue
            if 'dependencies' in data:
                Manager = self.__eqmap[manager]
                d = manager if manager in self.distribution_map else None
                self.commandlist.append(Manager(data['dependencies'], d))
            if 'postinstall' in data:
                self.commandlist.append(Script(data['postinstall']))
