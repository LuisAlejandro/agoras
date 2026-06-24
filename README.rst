.. image:: https://raw.githubusercontent.com/LuisAlejandro/agoras/develop/docs/_static/banner.svg

..

    A command line python utility to manage your social networks (X, Facebook, Instagram, LinkedIn, Discord, YouTube, TikTok, Threads, Telegram, and WhatsApp)

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

|
|

.. _GitHub actions: https://github.com/LuisAlejandro/agoras-actions
.. _full documentation: https://agoras.luisalejandro.org
.. _migration guide: https://agoras.luisalejandro.org/en/latest/migration.html

Current version: 2.0.4

.. note::

   Agoras 2.0 uses a **modular architecture** (five PyPI packages), a **platform-first CLI**, and an **OAuth callback server** for supported networks.

   Upgrading from Agoras 1.x? Import paths and CLI syntax changed — see the `migration guide`_.

Agoras is a python utility that helps publish and delete posts on the most
popular social networks (X (formerly Twitter), Facebook, Instagram, LinkedIn, Discord, YouTube, TikTok, Threads, Telegram, and WhatsApp).

This repository stores the application. There's also `GitHub actions`_
that you can incorporate into your workflows.

For more information, please read the `full documentation`_.

Architecture
============

Agoras is split into five coordinated PyPI packages:

- **agoras-common**: Shared utilities, logging, and constants
- **agoras-media**: Image and video processing
- **agoras-core**: Abstract interfaces (SocialNetwork), Feed, and Sheet logic
- **agoras-platforms**: Platform implementations (X, Facebook, etc.)
- **agoras**: Command-line interface (depends on all above)

**Key capabilities:**

- **Platforms**: X, Facebook, Instagram, LinkedIn, Discord, YouTube, TikTok, Threads, Telegram, and WhatsApp
- **OAuth callback server**: Automatic local server for easier authentication on supported networks
- **Platform-first CLI**: ``agoras x post`` instead of ``agoras publish --network x --action post``
- **Modular installation**: Install only what you need, or use ``pip install agoras`` for everything

Upgrading from 1.x? Import paths and CLI commands changed. See the `migration guide`_.

Getting started
===============

Local development
-----------------

Clone the repository and use Docker-backed ``make`` targets for linting and tests::

    $ git clone https://github.com/LuisAlejandro/agoras.git
    $ cd agoras
    $ git checkout develop
    $ cp .env.example .env   # optional: platform credentials for integration tests
    $ make image
    $ make start
    $ make console           # interactive shell inside the container
    $ make lint
    $ make test

For a host virtualenv without Docker, run ``make virtualenv`` then activate ``./virtualenv/bin/activate``.
See CONTRIBUTING.rst for monorepo package layout and contributor workflows.

Installation
------------

.. _PyPI: https://pypi.org/project/agoras

The ``agoras`` program is written in python and hosted on PyPI_.
Therefore, you can use pip to install the stable version::

    $ pip install --upgrade agoras

If you want to install the development version (not recommended), you can
install directly from GitHub like this::

    $ pip install --upgrade https://github.com/LuisAlejandro/agoras/archive/develop.tar.gz

Modular Installation (v2.0+)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Starting with v2.0, Agoras is split into 5 separate packages for better modularity.
The main CLI package automatically installs all dependencies::

    $ pip install agoras  # Installs all 5 packages

For selective installation (advanced users only)::

    $ pip install agoras-common     # Just utilities and logging
    $ pip install agoras-media      # Common + media processing
    $ pip install agoras-core       # Common + media + core interfaces
    $ pip install agoras-platforms  # All above + platform implementations
    $ pip install agoras            # Everything including CLI

**Package Architecture:**

- ``agoras-common``: Utilities, logging, shared constants
- ``agoras-media``: Image and video processing
- ``agoras-core``: Abstract interfaces (SocialNetwork), Feed, Sheet logic
- ``agoras-platforms``: Platform implementations (X, Facebook, etc.)
- ``agoras``: Command-line interface (depends on all above)

**When to use each package:**

- Most users: ``pip install agoras`` (installs everything including CLI)
- Python integrations: ``pip install agoras-platforms`` (no CLI, all platforms)
- Custom platforms: ``pip install agoras-core`` (interfaces only)
- Media processing: ``pip install agoras-media`` (no social features)
- Utilities only: ``pip install agoras-common`` (minimal dependencies)

Using the application
---------------------

Quick Start
~~~~~~~~~~~

Post to X with the platform-first CLI::

    $ agoras x post \
        --consumer-key "${TWITTER_CONSUMER_KEY}" \
        --consumer-secret "${TWITTER_CONSUMER_SECRET}" \
        --oauth-token "${TWITTER_OAUTH_TOKEN}" \
        --oauth-secret "${TWITTER_OAUTH_SECRET}" \
        --text "Hello from Agoras!" \
        --image-1 "https://example.com/image.jpg"

See all available platforms::

    $ agoras --help

See platform-specific commands::

    $ agoras x --help
    $ agoras facebook --help
    $ agoras youtube --help

Supported Platforms
~~~~~~~~~~~~~~~~~~~

Agoras supports 10 social networks with intuitive platform-first commands:

- **X (formerly Twitter)**: ``agoras x <action>`` - Full action set (post, video, like, share, delete)
- **Facebook**: ``agoras facebook <action>`` - Full action set (post, video, like, share, delete)
- **Instagram**: ``agoras instagram <action>`` - Post and video actions
- **LinkedIn**: ``agoras linkedin <action>`` - Full action set (post, video, like, share, delete)
- **Discord**: ``agoras discord <action>`` - Bot-based messaging (post, video, delete)
- **YouTube**: ``agoras youtube <action>`` - Video platform (video, like, delete)
- **TikTok**: ``agoras tiktok <action>`` - Photo slideshow posts and video uploads
- **Threads**: ``agoras threads <action>`` - Post, video, share, and delete
- **Telegram**: ``agoras telegram <action>`` - Post, video, and delete
- **WhatsApp**: ``agoras whatsapp <action>`` - Post, video, and template messages

Automation Commands
~~~~~~~~~~~~~~~~~~~

Publish from RSS/Atom feeds::

    $ agoras utils feed-publish \
        --network x \
        --mode last \
        --feed-url "https://blog.example.com/feed.xml"

Run scheduled posts from Google Sheets::

    $ agoras utils schedule-run \
        --sheets-id "${GOOGLE_SHEETS_ID}" \
        --sheets-name "Schedule"


Examples of usage
~~~~~~~~~~~~~~~~~

.. _Using Agoras with X: https://agoras.luisalejandro.org/en/latest/x.html
.. _Using Agoras with Facebook: https://agoras.luisalejandro.org/en/latest/facebook.html
.. _Using Agoras with Instagram: https://agoras.luisalejandro.org/en/latest/instagram.html
.. _Using Agoras with LinkedIn: https://agoras.luisalejandro.org/en/latest/linkedin.html
.. _Using Agoras with Discord: https://agoras.luisalejandro.org/en/latest/discord.html
.. _Using Agoras with YouTube: https://agoras.luisalejandro.org/en/latest/youtube.html
.. _Using Agoras with TikTok: https://agoras.luisalejandro.org/en/latest/tiktok.html
.. _Using Agoras with Threads: https://agoras.luisalejandro.org/en/latest/threads.html
.. _Using Agoras with Telegram: https://agoras.luisalejandro.org/en/latest/telegram.html
.. _Using Agoras with WhatsApp: https://agoras.luisalejandro.org/en/latest/whatsapp.html
.. _Migration Guide: https://agoras.luisalejandro.org/en/latest/migration.html

- `Using Agoras with X`_
- `Using Agoras with Facebook`_
- `Using Agoras with Instagram`_
- `Using Agoras with LinkedIn`_
- `Using Agoras with Discord`_
- `Using Agoras with YouTube`_
- `Using Agoras with TikTok`_
- `Using Agoras with Threads`_
- `Using Agoras with Telegram`_
- `Using Agoras with WhatsApp`_
- `Migration Guide`_ (upgrading from 1.x)


Credentials
~~~~~~~~~~~

.. _How to get credentials for X: https://agoras.luisalejandro.org/en/latest/credentials/x.html
.. _How to get credentials for Facebook: https://agoras.luisalejandro.org/en/latest/credentials/facebook.html
.. _How to get credentials for Instagram: https://agoras.luisalejandro.org/en/latest/credentials/instagram.html
.. _How to get credentials for LinkedIn: https://agoras.luisalejandro.org/en/latest/credentials/linkedin.html
.. _How to get credentials for Discord: https://agoras.luisalejandro.org/en/latest/credentials/discord.html
.. _How to get credentials for YouTube: https://agoras.luisalejandro.org/en/latest/credentials/youtube.html
.. _How to get credentials for TikTok: https://agoras.luisalejandro.org/en/latest/credentials/tiktok.html
.. _How to get credentials for Threads: https://agoras.luisalejandro.org/en/latest/credentials/threads.html
.. _How to get credentials for Telegram: https://agoras.luisalejandro.org/en/latest/credentials/telegram.html
.. _How to get credentials for WhatsApp: https://agoras.luisalejandro.org/en/latest/credentials/whatsapp.html
.. _How to get credentials for Google spreadsheets: https://agoras.luisalejandro.org/en/latest/credentials/google.html

- `How to get credentials for X`_
- `How to get credentials for Facebook`_
- `How to get credentials for Instagram`_
- `How to get credentials for LinkedIn`_
- `How to get credentials for Discord`_
- `How to get credentials for YouTube`_
- `How to get credentials for TikTok`_
- `How to get credentials for Threads`_
- `How to get credentials for Telegram`_
- `How to get credentials for WhatsApp`_
- `How to get credentials for Google spreadsheets`_

Getting help
============

.. _Discord server: https://discord.gg/GRnq3qQ9SB
.. _StackOverflow: http://stackoverflow.com/questions/ask

If you have any doubts or problems, subscribe to our `Discord server`_ and ask for help. You can also
ask your question on StackOverflow_ (tag it ``agoras``) or drop me an email at luis@luisalejandro.org.

Contributing
============

.. _CONTRIBUTING: CONTRIBUTING.rst

See CONTRIBUTING_ for details.

Release history
===============

.. _HISTORY: HISTORY.rst

See HISTORY_ for details.

License
=======

.. _AUTHORS: AUTHORS.rst
.. _GPL-3 License: LICENSE

Copyright (C) 2022-2026, Agoras Developers (read AUTHORS_ for a full list of copyright holders).

Released under a `GPL-3 License`_.

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

