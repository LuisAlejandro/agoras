#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re

from setuptools import setup

from sacli import (__author__, __email__, __version__, __url__,
                   __description__)


def read_requirements(reqfile):
    with open(reqfile, 'r') as r:
        reqs = filter(None, r.read().split('\n'))
    return [re.sub(r'\t*# pyup.*', r'', x) for x in reqs]


install_requires = read_requirements('requirements.txt')
tests_require = read_requirements('requirements.txt') + \
    read_requirements('requirements-dev.txt')

setup(
    name='sacli',
    version=__version__,
    author=__author__,
    author_email=__email__,
    url=__url__,
    description=__description__,
    long_description=open('README.short.rst').read(),
    packages=['sacli', 'sacli.api', 'sacli.core'],
    package_dir={'sacli': 'sacli'},
    include_package_data=True,
    install_requires=install_requires,
    entry_points={
        'console_scripts': ('sacli = sacli.cli:main',),
    },
    # license='GPLv3',
    zip_safe=False,
    keywords=['odoo', 'requirements'],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
    ],
    test_suite='tests',
    tests_require=tests_require
)
