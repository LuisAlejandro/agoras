#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Please refer to AUTHORS.rst for a complete list of Copyright holders.
# Copyright (C) 2022-2026, Agoras Developers.

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

from setuptools import find_namespace_packages, setup

setup(
    name='agoras',
    version='2.0.0',
    author='Luis Alejandro Martínez Faneyth',
    author_email='luis@luisalejandro.org',
    url='https://github.com/LuisAlejandro/agoras',
    description=('A command line python utility to manage your social networks '
                 '(X, Facebook, Instagram, LinkedIn, Discord, YouTube, TikTok, '
                 'Telegram, Threads and WhatsApp)'),
    long_description=open('README.rst').read(),
    long_description_content_type='text/x-rst',
    packages=find_namespace_packages(where='src'),
    package_dir={'': 'src'},
    python_requires='>=3.10',
    install_requires=[
        'agoras-platforms>=2.0.0',
    ],
    entry_points={
        'console_scripts': [
            'agoras=agoras.cli.main:main',
        ],
    },
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Programming Language :: Python :: 3.13',
        'Programming Language :: Python :: 3.14',
        'Environment :: Console',
        'Topic :: Utilities',
    ],
    keywords=[
        'social networks', 'twitter', 'facebook', 'instagram', 'linkedin',
        'discord', 'youtube', 'tiktok', 'telegram', 'threads', 'whatsapp', 'x',
        'cli', 'command-line'
    ],
    zip_safe=False,
)
