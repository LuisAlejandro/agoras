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

from setuptools import setup, find_namespace_packages


setup(
    name='agoras-platforms',
    version='2.0.0',
    author='Luis Alejandro Martínez Faneyth',
    author_email='luis@luisalejandro.org',
    url='https://github.com/LuisAlejandro/agoras',
    description='Platform-specific implementations for Agoras social networks',
    long_description=open('README.rst').read(),
    long_description_content_type='text/x-rst',
    packages=find_namespace_packages(where='src'),
    package_dir={'': 'src'},
    python_requires='>=3.9',
    install_requires=[
        'agoras-core>=2.0.0',
        'tweepy==4.16.0',
        'python-facebook-api==0.20.1',
        'linkedin-api-client==0.3.0',
        'beautifulsoup4==4.13.4',
        'discord.py==2.6.4',
        'google-api-python-client==2.188.0',
        'google-api-core>=2.0.0',
        'google-auth==2.47.0',
        'google-auth-oauthlib>=1.2.0',
        'google-auth-httplib2==0.3.0',
        'oauth2client==4.1.3',
        'platformdirs==4.4.0',
        'authlib==1.6.6',
        'threadspipepy>=0.4.5',
        'cryptography>=42.0.0',
        'python-telegram-bot>=22.1',
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
        'Programming Language :: Python :: 3.12',
    ],
    keywords=[
        'social networks', 'twitter', 'facebook', 'instagram', 'linkedin',
        'discord', 'youtube', 'tiktok', 'telegram', 'threads', 'whatsapp', 'x'
    ],
    zip_safe=False,
)
