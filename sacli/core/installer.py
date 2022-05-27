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
import re
from subprocess import Popen, PIPE
from distutils.spawn import find_executable

from dotenv import dotenv_values
from packaging.version import Version
from slugify import slugify

from .distro import Distribution
from .errors import (CannotIdentifyDistribution,
                     UnsupportedDistribution)
from .utils import flatten_list
from .logger import logger
from .pkgindex import debian_codename_index, arch_codename_index, \
    fedora_codename_index, alpine_codename_index, gentoo_codename_index, \
    centos_codename_index
from ..config.distributions import distrodata


class Installer(object):

    def __init__(self, sacli):

        self.distname = ''
        self.codename = ''
        self.version = ''
        self.metadistname = ''
        self.metacodename = ''
        # self.release_data = {}
        # self.dpkg_origins_data = {}
        # self.apt_policy_data = []
        self.lsb_release_command = find_executable('lsb_release')
        self.os_release = '/etc/os-release'
        self.lsb_release = '/etc/lsb-release'
        self.dpkg_origins = '/etc/dpkg/origins/default'
        self.debian_release = '/etc/debian_version'
        self.fedora_release = '/etc/fedora-release'
        self.alpine_release = '/etc/alpine-release'
        self.arch_release = '/etc/arch-release'
        self.gentoo_release = '/etc/gentoo-release'
        self.centos_release = '/etc/centos-release'
        self.env = os.environ.copy()
        self.env['LC_ALL'] = 'C'

        self.longnames = {
            'v': 'version',
            'o': 'origin',
            'a': 'suite',
            'c': 'component',
            'l': 'label'
        }

        self.saclidata = sacli
        self.distributions = distrodata
        self.codenames = {}
        self.revcodenames = {}

        self.populate_codename_index()
        # self.get_distro_data()
        # self.normalize_distro_data()

    def populate_codename_index(self):
        logger.info('Generating distributions database')
        self.distributions['debian']['codenames'] = \
            debian_codename_index()
        self.distributions['arch']['codenames'] = \
            arch_codename_index()
        self.distributions['fedora']['codenames'] = \
            fedora_codename_index()
        self.distributions['alpine']['codenames'] = \
            alpine_codename_index()
        self.distributions['centos']['codenames'] = \
            centos_codename_index()
        self.distributions['gentoo']['codenames'] = \
            gentoo_codename_index()

    def codename_index(self, x):

        suite = x[1].get('suite')
        order = list(self.distributions[self.distname]['codenames'].items())
        order.sort()
        order = list(flatten_list(list(zip(*order))[1]))

        if suite:
            if suite in order:
                return int(len(order) - order.index(suite))
            else:
                return suite
        return 0

    def parse_apt_policy(self):

        retval = {}
        policy = Popen(args=['apt-cache', 'policy'],
                       stdout=PIPE, stderr=PIPE, env=self.env,
                       close_fds=True).communicate()[0].decode('utf-8')

        for line in policy.split('\n'):
            line = line.strip()
            m = re.match(r'(-?\d+)', line)

            if m:
                priority = int(m.group(1))

            if line.startswith('release'):
                bits = line.split(' ', 1)

                if len(bits) > 1:

                    for bit in bits[1].split(','):
                        kv = bit.split('=', 1)

                        if len(kv) > 1:
                            k, v = kv[:2]

                            if k in self.longnames:
                                retval[self.longnames[k]] = v

                    self.apt_policy_data.append((priority, retval))
        return self.apt_policy_data

    def get_codename_from_apt(self, origin, component='main'):

        releases = self.parse_apt_policy()
        releases = [x for x in releases if (
            x[1].get('origin', '').lower() == origin and
            x[1].get('component', '').lower() == component and
            x[1].get('label', '').lower() == origin)]

        releases.sort(key=lambda tuple: tuple[0], reverse=True)

        max_priority = releases[0][0]
        releases = [x for x in releases if x[0] == max_priority]
        releases.sort(key=self.codename_index)

        return releases[0][1]['suite']

    def parse_os_release(self, release):
        return dotenv_values(release)

    def cat_file(self, release):
        with open(release) as content:
            return content.read()

    def parse_dpkg_origins(self, origins):
        dpkg_origins_data = {}
        with open(origins) as content:
            contentlist = content.read()
        for j in contentlist.split('\n'):
            keyvalue = j.split(':')
            if len(keyvalue) > 1:
                dpkg_origins_data[keyvalue[0].strip()] = keyvalue[1].strip()
        return dpkg_origins_data

    def cmd_return_full(self, args, env):
        return Popen(
            args=args, stdout=PIPE, stderr=PIPE,
            env=env, close_fds=True
        ).communicate()[0].decode('utf-8')

    def cmd_return_first_line(self, args, env):
        return Popen(
            args=args, stdout=PIPE, stderr=PIPE,
            env=env, close_fds=True
        ).communicate()[0].decode('utf-8').split('\n')[0]

    def try_lsb_release_command(self):
        if (not self.distname) and self.lsb_release_command:
            self.distname = self.cmd_return_first_line(
                [self.lsb_release_command, '-is'], self.env)
            self.codename = self.cmd_return_first_line(
                [self.lsb_release_command, '-cs'], self.env)
            self.version = self.cmd_return_first_line(
                [self.lsb_release_command, '-rs'], self.env)

    def try_arch_release_file(self):
        if (not self.distname) and os.path.exists(self.arch_release):
            self.distname = 'arch'
            self.codename = 'rolling'
            self.version = 'rolling'

    def try_gentoo_release_file(self):
        if (not self.distname) and os.path.exists(self.gentoo_release):
            self.distname = 'gentoo'
            self.codename = 'rolling'
            self.version = 'rolling'

    def try_fedora_release_file(self):
        if (not self.distname) and os.path.exists(self.fedora_release):
            relstr = self.cat_file(self.fedora_release)
            relarray = relstr.split()
            version = Version(relarray[2])
            self.distname = relarray[0]
            self.version = f'{version.major}'
            codename = re.match(r'^.*\((.*)\)$', relstr)
            if codename:
                self.codename = codename.groups()[0]

    def try_alpine_release_file(self):
        if (not self.distname) and os.path.exists(self.alpine_release):
            relstr = self.cat_file(self.alpine_release)
            relarray = relstr.split()
            version = Version(relarray[2])
            self.distname = relarray[0]
            self.version = f'{version.major}'
            codename = re.match(r'^.*\((.*)\)$', relstr)
            if codename:
                self.codename = codename.groups()[0]

    def try_centos_release_file(self):
        if (not self.distname) and os.path.exists(self.centos_release):
            relstr = self.cat_file(self.centos_release)
            relarray = relstr.split()
            stream = 'stream' if relarray[1].lower() == 'stream' else ''
            version = Version(relarray[3])
            self.distname = relarray[0]
            self.codename = f'{stream}{version.major}'

    def try_lsb_release_file(self):
        if (not self.distname) and os.path.exists(self.lsb_release):
            rel = self.parse_os_release(self.lsb_release)
            self.distname = rel['DISTRIB_ID'] \
                if 'DISTRIB_ID' in rel else ''
            self.codename = rel['DISTRIB_CODENAME'] \
                if 'DISTRIB_CODENAME' in rel else ''
            self.version = rel['DISTRIB_RELEASE'] \
                if 'DISTRIB_RELEASE' in rel else ''

    def try_os_release_file(self):
        if (not self.distname) and os.path.exists(self.os_release):
            rel = self.parse_os_release(self.os_release)
            self.distname = rel['ID'] if 'ID' in rel else ''
            self.codename = rel['VERSION_CODENAME'] \
                if 'VERSION_CODENAME' in rel else ''
            self.version = rel['VERSION_ID'] if 'VERSION_ID' in rel else ''

    def try_dpkg_origins(self):
        if (not self.distname) and os.path.exists(self.dpkg_origins):
            origins = self.parse_dpkg_origins(self.dpkg_origins)
            self.distname = origins['VENDOR'] if 'VENDOR' in origins else ''

    def try_apt(self):
        if self.distname and (not self.codename) \
           and os.path.exists(self.debian_release):
            rel = self.cat_file(self.debian_release)

            if re.findall(r'.*/.*', rel):
                self.codename = self.get_codename_from_apt(self.distname)
            else:
                self.codename = rel

    def get_distro_data(self):

        logger.info('Attempting to identify your distribution')

        self.try_lsb_release_command()
        self.try_arch_release_file()
        self.try_gentoo_release_file()
        self.try_fedora_release_file()
        self.try_centos_release_file()
        self.try_lsb_release_file()
        self.try_os_release_file()
        self.try_dpkg_origins()
        self.try_apt()

        if not (self.distname and self.codename):
            raise CannotIdentifyDistribution()

        self.codenames = self.distributions[self.distname]['codenames']

        for k, v in self.codenames.items():
            if len(v) > 1:
                for j in v:
                    self.revcodenames[j] = k
            else:
                self.revcodenames[v[0]] = k

    def normalize_distro_data(self):

        regex = re.compile(r'^(\d+)\.(\d+)(\.(\d+))?([ab](\d+))?$', re.VERBOSE)
        codematch = regex.match(self.codename)

        if not codematch:
            self.version = self.revcodenames[self.codename]
        else:
            (major, minor, patch, pre, prenum) = codematch.group(1, 2, 4, 5, 6)
            self.version = '.'.join(list(filter(None, [major, minor, patch,
                                                       pre, prenum])))
        vermatch = regex.match(self.version)
        # if self.distname == 'ubuntu':
        #     self.codename = self.codenames['.'.join(vermatch.group(1, 2))][0]

        # else:
        self.codename = self.codenames[str(float(vermatch.group(1)))][0]

        if self.is_supported_codename():
            logger.info('You are using %s (%s).' % (self.distname, self.codename))
            self.distribution = Distribution(self.distname,
                                             self.codename,
                                             self.version,
                                             self.saclidata,
                                             self.distributions)
        else:
            raise UnsupportedDistribution()

    def is_supported_distname(self):
        if self.distname in self.distributions:
            return True
        return False

    def is_supported_codename(self):
        if self.is_supported_distname():
            if (self.codename in
               self.distributions[self.distname][self.version]):
                return True
        return False

    def execute(self):
        logger.info('Installing missing dependencies ...')
        self.add_trusted_keys()
        self.add_manager_sources()
        self.update_package_db()
        self.install()

    def add_trusted_keys(self):
        self.distribution.add_trusted_keys()

    def add_manager_sources(self):
        self.distribution.add_manager_sources()

    def update_package_db(self):
        self.distribution.update_package_db()

    def install(self):
        self.distribution.install()
