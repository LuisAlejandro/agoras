.. image:: https://raw.githubusercontent.com/LuisAlejandro/sacli/develop/docs/_static/title.svg

-----

.. image:: https://img.shields.io/pypi/v/sacli.svg
   :target: https://pypi.org/project/sacli
   :alt: PyPI Package

.. image:: https://img.shields.io/github/release/LuisAlejandro/sacli.svg
   :target: https://github.com/LuisAlejandro/sacli/releases
   :alt: Github Releases

.. image:: https://img.shields.io/github/issues/LuisAlejandro/sacli
   :target: https://github.com/LuisAlejandro/sacli/issues?q=is%3Aopen
   :alt: Github Issues

.. image:: https://github.com/LuisAlejandro/sacli/workflows/Push/badge.svg
   :target: https://github.com/LuisAlejandro/sacli/actions?query=workflow%3APush
   :alt: Push

.. image:: https://readthedocs.org/projects/sacli/badge/?version=latest
   :target: https://readthedocs.org/projects/sacli/?badge=latest
   :alt: Read The Docs

.. image:: https://img.shields.io/discord/809504357359157288.svg?label=&logo=discord&logoColor=ffffff&color=7389D8&labelColor=6A7EC2
   :target: https://discord.gg/M36s8tTnYS
   :alt: Discord Channel

.. _different repository: https://github.com/LuisAlejandro/sacli-build
.. _sacli: https://github.com/LuisAlejandro/sacli
.. _Contents: https://www.debian.org/distrib/packages#search_contents

sacli is an application that generates a Module Index from the
Python Package Index (PyPI) and also from various versions of
the Python Standard Library.

sacli generates a configurable index written in ``JSON`` format that
serves as a database for applications like `sacli`_. It can be configured
to process only a range of packages (by initial letter) and to have
memory, time or log size limits. It basically aims to mimic what the
`Contents`_ file means for a Debian based package repository, but for the
Python Package Index.

This repository stores the application. The actual index lives in a `different
repository`_ and is rebuilt weekly via Github Actions.

* Free software: GPL-3
* Documentation: https://sacli.readthedocs.org

Table of Contents
-----------------

.. toctree::
   :maxdepth: 2

   installation
   usage
   api
   contributing
   authors
   history
   maintainer

Made with 💖 and 🍔
====================

.. image:: https://raw.githubusercontent.com/LuisAlejandro/sacli/develop/docs/_static/author-banner.svg

.. _LuisAlejandroTwitter: https://twitter.com/LuisAlejandro
.. _LuisAlejandroGitHub: https://github.com/LuisAlejandro
.. _luisalejandro.org: https://luisalejandro.org

|

    Web luisalejandro.org_ · GitHub `@LuisAlejandro`__ · Twitter `@LuisAlejandro`__

__ LuisAlejandroGitHub_
__ LuisAlejandroTwitter_
