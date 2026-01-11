#!/usr/bin/env python
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

from setuptools import setup

from agoras import (__author__, __email__, __version__, __url__,
                    __description__)


def read_requirements(reqfile):
    with open(reqfile, 'r') as r:
        reqs = list(filter(None, r.read().split('\n')))
    return reqs


install_requires = read_requirements('requirements.txt')
tests_require = read_requirements('requirements.txt') + \
    read_requirements('requirements-dev.txt')

setup(
    name='agoras',
    version=__version__,
    author=__author__,
    author_email=__email__,
    url=__url__,
    description=__description__,
    long_description=open('README.short.rst').read(),
    packages=['agoras', 'agoras.api', 'agoras.core'],
    package_dir={'agoras': 'agoras'},
    include_package_data=True,
    install_requires=install_requires,
    entry_points={
        'console_scripts': ('agoras = agoras.cli:main',),
    },
    zip_safe=False,
    keywords=[
        'social networks', 'twitter', 'facebook',
        'instagram', 'linkedin'
    ],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
    ],
    test_suite='tests',
    tests_require=tests_require
)
