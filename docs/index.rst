.. image:: https://raw.githubusercontent.com/LuisAlejandro/agoras/develop/docs/_static/title.svg

-----

.. image:: https://img.shields.io/pypi/v/agoras.svg
   :target: https://pypi.org/project/agoras/
   :alt: PyPI Package

.. image:: https://img.shields.io/github/release/LuisAlejandro/agoras.svg
   :target: https://github.com/LuisAlejandro/agoras/releases
   :alt: Github Releases

.. image:: https://img.shields.io/github/issues/LuisAlejandro/agoras
   :target: https://github.com/LuisAlejandro/agoras/issues?q=is%3Aopen
   :alt: Github Issues

.. image:: https://img.shields.io/github/actions/workflow/status/LuisAlejandro/agoras/push.yml?branch=master
   :target: https://github.com/LuisAlejandro/agoras/actions/workflows/push.yml
   :alt: Push

.. image:: https://coveralls.io/repos/github/LuisAlejandro/agoras/badge.svg?branch=develop
   :target: https://coveralls.io/github/LuisAlejandro/agoras?branch=develop
   :alt: Coverage

.. image:: https://cla-assistant.io/readme/badge/LuisAlejandro/agoras
   :target: https://cla-assistant.io/LuisAlejandro/agoras
   :alt: Contributor License Agreement

.. image:: https://readthedocs.org/projects/agoras/badge/?version=latest
   :target: https://readthedocs.org/projects/agoras/?badge=latest
   :alt: Read The Docs

.. image:: https://img.shields.io/discord/809504357359157288.svg?label=&logo=discord&logoColor=ffffff&color=7389D8&labelColor=6A7EC2
   :target: https://discord.gg/GRnq3qQ9SB
   :alt: Discord Channel

.. _GitHub actions: https://github.com/LuisAlejandro/agoras-actions
.. _full documentation: https://agoras.readthedocs.org

Agoras is a python utility that helps publish and delete posts on the most
popular social networks (X (formerly Twitter), Facebook, Instagram, LinkedIn, Discord, YouTube, TikTok, Threads, Telegram, and WhatsApp).

This repository stores the application. There's also `GitHub actions`_
that you can incorporate into your workflows.

For more information, please read the `full documentation`_.

What's New in v2.0
==================

Agoras v2.0 represents a major architectural shift from a monolithic package to a modular 5-package structure. This allows you to install only the components you need.

**Package Structure:**

.. code-block:: text

   agoras (CLI)
   └── agoras-platforms
       └── agoras-core
           ├── agoras-media
           └── agoras-common

**Key Improvements:**

- **Modular Architecture**: Install only what you need (e.g., ``agoras-core`` for custom integrations)
- **New Platforms**: Telegram, WhatsApp, Threads, and X support
- **Better Authentication**: Built-in OAuth 2.0 callback server
- **Improved CLI**: Platform-first commands (``agoras x post``)

For detailed migration instructions, see :doc:`migration`.

.. note::

   **Agoras v2.0 Now Available!**

   Version 2.0 introduces a modular architecture with 5 separate packages for better maintainability and flexibility.

   **What's New:**

   - Modular package structure (agoras-common, agoras-media, agoras-core, agoras-platforms, agoras)
   - New platforms: Telegram, WhatsApp, Threads, and X (Twitter rebrand)
   - OAuth 2.0 callback server for easier authentication
   - Enhanced CLI with platform-first commands

   **Breaking Changes:** Import paths and CLI syntax have changed. See :doc:`migration` for upgrade instructions.

Table of Contents
-----------------

Getting Started
~~~~~~~~~~~~~~~

.. toctree::
   :maxdepth: 2

   installation
   usage
   migration

Platform Guides
~~~~~~~~~~~~~~~

.. toctree::
   :maxdepth: 2

   x
   facebook
   instagram
   linkedin
   discord
   youtube
   tiktok
   threads
   telegram
   whatsapp

Getting Credentials
~~~~~~~~~~~~~~~~~~

.. toctree::
   :maxdepth: 2

   credentials/x
   credentials/facebook
   credentials/instagram
   credentials/linkedin
   credentials/discord
   credentials/youtube
   credentials/tiktok
   credentials/threads
   credentials/telegram
   credentials/whatsapp
   credentials/google

Advanced Topics
~~~~~~~~~~~~~~~

.. toctree::
   :maxdepth: 2

   rss
   api

Developer Documentation
~~~~~~~~~~~~~~~~~~~~~~

.. toctree::
   :maxdepth: 2

   contributing
   authors
   history
   maintainer

Made with 💖 and 🍔
====================

.. image:: https://raw.githubusercontent.com/LuisAlejandro/LuisAlejandro/master/images/author-banner.svg

.. _LuisAlejandroTwitter: https://twitter.com/LuisAlejandro
.. _LuisAlejandroGitHub: https://github.com/LuisAlejandro
.. _luisalejandro.org: https://luisalejandro.org

|

    Web luisalejandro.org_ · GitHub `@LuisAlejandro`__ · Twitter `@LuisAlejandro`__

__ LuisAlejandroGitHub_
__ LuisAlejandroTwitter_
