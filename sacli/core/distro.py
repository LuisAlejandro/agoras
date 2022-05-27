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

from .errors import UnsupportedDistribution
from .sacli import sacli
from .logger import logger


class Distribution(object):

    derivatives = {
        'ubuntu': 'debian'
    }

    def __init__(self, distname, codename, version, data, distributions):
        self.distributions = distributions
        self.distname = distname
        self.codename = codename
        self.version = version
        self.command_config = {}
        self.distro_manager_map = {}
        self.allowed_managers = []
        self.sacli = sacli(data)
        self.metadistro = self.get_metadistro()

    def get_metadistro(self):
        if self.distname not in self.derivatives:
            raise UnsupportedDistribution()
        return self.metadistro[self.distname]

    def update_package_db(self):
        for cmd in self.sacli.commandlist:
            enabled_distros = cmd.get_enabled_distros()
            if self.distname in enabled_distros or \
               self.metadistro in enabled_distros:
                cmd.update()

    def install(self):
        for cmd in self.sacli.commandlist:
            enabled_distros = cmd.get_enabled_distros()
            if self.distname in enabled_distros or \
               self.metadistro in enabled_distros:
                cmd.install()
