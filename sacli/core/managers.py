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

import os
from io import BytesIO
from tempfile import mkstemp
from subprocess import Popen, PIPE

from .logger import logger
from ..config.distributions import distrodata, native_managers, \
    other_managers


class Script(object):

    def __init__(self, content):
        self.content = content
        self.scriptpath = ''

    def get_execute_command(self):
        return ['bash', self.scriptpath]

    def create(self):
        _, self.scriptpath = mkstemp(suffix='.sh', prefix='sacli-script')
        with open(self.scriptpath, 'w') as script:
            script.write(self.content)

    def execute(self):
        result = Popen(args=self.get_execute_command(),
                       stdout=PIPE, stderr=PIPE,
                       close_fds=True)

        for line in iter((result.stdout or BytesIO(b'')).readline, ''):
            if line:
                logger.info(str(line).strip('\n'))
            else:
                break

    def delete(self):
        os.remove(self.scriptpath)

    def install(self):
        self.create()
        self.execute()
        self.delete()


class PackageManager(object):

    def __init__(self, dependencies, distro):
        self.dependencies = dependencies
        self.distro = distro
        self.manager = {}
        self.enabled_distros = []

    def get_enabled_distros(self):
        if self.distro:
            return [self.distro]
        return self.get_distros_per_command()

    def get_distros_per_command(self):
        distros_per_command = []
        for distro, ddata in distrodata.items():
            if 'managers' not in ddata:
                continue
            for mdata in ddata['managers'].values():
                if 'command' not in mdata or \
                   mdata['command'] != self.manager['command']:
                    continue
                distros_per_command.append(distro)
        return list(set(distros_per_command))

    def get_execute_command(self):
        cmd = []
        cmd.extend([self.manager.get('command')])
        cmd.extend([self.manager.get('install')])
        cmd.extend(self.manager.get('args'))
        cmd.extend(self.dependencies)
        return cmd

    def get_update_command(self):
        cmd = []
        cmd.extend([self.manager.get('command')])
        cmd.extend([self.manager.get('update')])
        return cmd

    def execute(self):
        result = Popen(args=self.get_execute_command(),
                       stdout=PIPE, stderr=PIPE,
                       env=self.manager['env'],
                       close_fds=True)

        for line in iter((result.stdout or BytesIO(b'')).readline, ''):
            if line:
                logger.info(str(line).strip('\n'))
            else:
                break

    def update(self):
        result = Popen(args=self.get_update_command(),
                       stdout=PIPE, stderr=PIPE,
                       env=self.manager['env'],
                       close_fds=True)

        for line in iter((result.stdout or BytesIO(b'')).readline, ''):
            if line:
                logger.info(str(line).strip('\n'))
            else:
                break

    def install(self):
        self.update()
        self.execute()


class Apt(PackageManager):

    def __init__(self, dependencies, distro):
        super().__init__(dependencies, distro)
        self.manager = native_managers['apt']


class Yum(PackageManager):

    def __init__(self, dependencies, distro):
        super().__init__(dependencies, distro)
        self.manager = native_managers['yum']


class Apk(PackageManager):

    def __init__(self, dependencies, distro):
        super().__init__(dependencies, distro)
        self.manager = native_managers['apk']


class Pacman(PackageManager):

    def __init__(self, dependencies, distro):
        super().__init__(dependencies, distro)
        self.manager = native_managers['pacman']


class Portage(PackageManager):

    def __init__(self, dependencies, distro):
        super().__init__(dependencies, distro)
        self.manager = native_managers['portage']


class Npm(PackageManager):

    def __init__(self, dependencies, distro):
        super().__init__(dependencies, distro)
        self.manager = other_managers['npm']


class Yarn(PackageManager):

    def __init__(self, dependencies, distro):
        super().__init__(dependencies, distro)
        self.manager = other_managers['yarn']


class Pip(PackageManager):

    def __init__(self, dependencies, distro):
        super().__init__(dependencies, distro)
        self.manager = other_managers['pip']


class Bundler(PackageManager):

    def __init__(self, dependencies, distro):
        super().__init__(dependencies, distro)
        self.manager = other_managers['bundler']
