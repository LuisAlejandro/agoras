#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os

from setuptools import find_namespace_packages, setup

# Define the source directories for each sub-package
PACKAGE_ROOTS = {
    'cli': 'packages/cli/src',
    'common': 'packages/common/src',
    'core': 'packages/core/src',
    'media': 'packages/media/src',
    'platforms': 'packages/platforms/src',
}


def find_monorepo_packages():
    packages = []
    package_dir = {}

    for name, root in PACKAGE_ROOTS.items():
        if not os.path.exists(root):
            continue

        # Find all namespace packages in this root
        found = find_namespace_packages(where=root)
        packages.extend(found)

        for pkg in found:
            # Map the package name to its directory
            # e.g. 'agoras.cli' -> 'packages/cli/src/agoras/cli'
            path = pkg.replace('.', '/')
            package_dir[pkg] = os.path.join(root, path)

    return list(set(packages)), package_dir


packages, package_dir = find_monorepo_packages()

setup(
    name='agoras',
    version='2.0.0',
    author='Luis Alejandro Martínez Faneyth',
    author_email='luis@luisalejandro.org',
    url='https://github.com/LuisAlejandro/agoras',
    description='Agoras Social Media Manager (Monorepo Install)',
    long_description=open('README.rst').read() if os.path.exists('README.rst') else '',
    long_description_content_type='text/x-rst',

    # Package discovery
    packages=packages,
    package_dir=package_dir,

    # Combined dependencies from all sub-packages
    install_requires=[
        # From agoras-common
        'requests==2.32.5',
        'beautifulsoup4==4.14.3',

        # From agoras-media
        'filetype==1.2.0',
        'opencv-python-headless==4.12.0.88',
        'Pillow>=10.0.0',

        # From agoras-core
        'atoma==0.0.17',
        'gspread==6.2.1',
        'python-dateutil==2.9.0.post0',

        # From agoras-platforms
        'tweepy==4.16.0',
        'python-facebook-api==0.20.1',
        'linkedin-api-client==0.3.0',
        'discord.py==2.6.4',
        'google-api-python-client==2.188.0',
        'google-api-core>=2.0.0',
        'google-auth==2.47.0',
        'google-auth-oauthlib>=1.2.0',
        'google-auth-httplib2==0.3.0',
        'oauth2client==4.1.3',
        'platformdirs==4.4.0',
        'authlib==1.6.6',
        'cryptography>=42.0.0',
        'python-telegram-bot>=22.1',
    ],

    # CLI Entry point
    entry_points={
        'console_scripts': [
            'agoras=agoras.cli.main:main',
        ],
    },

    python_requires='>=3.10',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Programming Language :: Python :: 3.13',
        'Programming Language :: Python :: 3.14',
    ],
)
