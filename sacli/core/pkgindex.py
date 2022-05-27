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

import re
from contextlib import closing
from urllib.request import urlopen, Request

import lxml.html
from packaging.version import Version

from .logger import logger
from ..config.codenames import debian_suites, fedora_version_url, \
    alpine_version_url, debian_release_url_holder, \
    olddebian_version_url, base_debian_codename_index, \
    olddebian_release_url_holder, debian_oldversioning, \
    base_arch_codename_index, base_fedora_codename_index, \
    base_alpine_codename_index, base_gentoo_codename_index, \
    base_centos_codename_index


def request_first_bytes(debian_release_url):

    req = Request(debian_release_url)
    req.add_header('Range', 'bytes={0}-{1}'.format(0, 256))

    try:
        with closing(urlopen(req)) as d:
            return str(d.read())
    except Exception:
        return ''


def get_curr_debian_codename_index(suites, url_holder):
    logger.debug('Getting Debian versions')
    idx = {}

    for debian_suite in suites:
        debian_release_url = url_holder.format(debian_suite)

        debian_release_content = request_first_bytes(debian_release_url)

        codename = re.findall(r'Codename: (\w*)', debian_release_content)
        version = re.findall(r'Version: (\d*\.?\d*)', debian_release_content)

        if debian_suite in ['testing', 'unstable']:
            idx[debian_suite] = list(set([codename[0], debian_suite]))
            continue

        if not (codename and version):
            continue

        v = Version(version[0])
        if codename[0] in debian_oldversioning:
            version = f'{v.major}.{v.minor}'
        else:
            version = f'{v.major}'

        idx[version] = list(set([codename[0], debian_suite]))

    return idx


def get_archive_debian_codename_index():
    olddebian_version_url_html = \
        lxml.html.parse(olddebian_version_url).getroot()
    links = olddebian_version_url_html.cssselect('a')
    debian_versions = [
        e.get('href')
        for e in links
        if e.text_content() not in
        ['Name', 'Last modified', 'Size', 'Parent Directory']
    ]
    debian_versions = [
        e.strip('/')
        for e in debian_versions
        if len(e.split('-')) == 1
    ]
    return debian_versions


def get_fedora_versions():
    logger.debug('Getting Mongo versions')
    fedora_version_url_html = lxml.html.parse(fedora_version_url).getroot()
    links = fedora_version_url_html.cssselect('a')
    fedora_versions = [
        e.get('href')
        for e in links
        if e.text_content() not in
        ['Name', 'Last modified', 'Size',
         'Description', 'Parent Directory', 'test/']
    ]
    fedora_versions = [
        e.strip('/')
        for e in fedora_versions
        if len(e.split('-')) == 1
    ]
    return fedora_versions


def get_alpine_versions():
    logger.debug('Getting Mongo versions')
    alpine_version_url_html = lxml.html.parse(alpine_version_url).getroot()
    links = alpine_version_url_html.cssselect('a')
    alpine_versions = [
        e.get('href')
        for e in links
        if e.text_content() not in
        ['latest-stable/', 'MIRRORS.txt', 'last-updated', '../']
    ]
    alpine_versions = [
        e.strip('/')
        for e in alpine_versions
        if len(e.split('-')) == 1
    ]
    return alpine_versions


def debian_codename_index():
    old_debian_suites = get_archive_debian_codename_index()
    olddebians = get_curr_debian_codename_index(old_debian_suites,
                                                olddebian_release_url_holder)
    currdebians = get_curr_debian_codename_index(debian_suites,
                                                 debian_release_url_holder)
    return {
        **base_debian_codename_index,
        **olddebians,
        **currdebians
    }


def fedora_codename_index():
    fedora_versions = {f: [f] for f in get_fedora_versions()}
    return {
        **fedora_versions,
        **base_fedora_codename_index
    }


def alpine_codename_index():
    alpine_versions = {f: [f] for f in get_alpine_versions()}
    return {
        **base_alpine_codename_index,
        **alpine_versions
    }


def arch_codename_index():
    return {**base_arch_codename_index}


def gentoo_codename_index():
    return {**base_gentoo_codename_index}


def centos_codename_index():
    return {**base_centos_codename_index}
