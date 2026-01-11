.. image:: https://raw.githubusercontent.com/LuisAlejandro/agoras/develop/docs/_static/banner.svg

..

    A command line python utility to manage your social networks (Twitter, Facebook, Instagram, LinkedIn, Discord, YouTube, TikTok, and Threads)

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
.. _full documentation: https://agoras.readthedocs.org

Current version: 1.1.3

Agoras is a python utility that helps publish and delete posts on the most
popular social networks (Twitter, Facebook, Instagram, LinkedIn, Discord, YouTube, TikTok, and Threads).

This repository stores the application. There's also `GitHub actions`_
that you can incorporate into your workflows.

For more information, please read the `full documentation`_.

Getting started
===============

Installation
------------

.. _PyPI: https://pypi.org/project/agoras

The ``agoras`` program is written in python and hosted on PyPI_.
Therefore, you can use pip to install the stable version::

    $ pip install --upgrade agoras

If you want to install the development version (not recomended), you can
install directlty from GitHub like this::

    $ pip install --upgrade https://github.com/LuisAlejandro/agoras/archive/develop.tar.gz

Using the application
---------------------

Quick Start
~~~~~~~~~~~

Post to Twitter with the new intuitive CLI::

    $ agoras twitter post \
        --consumer-key "${TWITTER_CONSUMER_KEY}" \
        --consumer-secret "${TWITTER_CONSUMER_SECRET}" \
        --oauth-token "${TWITTER_OAUTH_TOKEN}" \
        --oauth-secret "${TWITTER_OAUTH_SECRET}" \
        --text "Hello from Agoras!" \
        --image-1 "https://example.com/image.jpg"

See all available platforms::

    $ agoras --help

See platform-specific commands::

    $ agoras twitter --help
    $ agoras facebook --help
    $ agoras youtube --help

Supported Platforms
~~~~~~~~~~~~~~~~~~~

Agoras supports 8 social networks with intuitive platform-first commands:

- **Twitter**: ``agoras twitter <action>`` - Full action set (post, video, like, share, delete)
- **Facebook**: ``agoras facebook <action>`` - Full action set (post, video, like, share, delete)
- **Instagram**: ``agoras instagram <action>`` - Post and video actions
- **LinkedIn**: ``agoras linkedin <action>`` - Full action set (post, video, like, share, delete)
- **Discord**: ``agoras discord <action>`` - Bot-based messaging (post, video, delete)
- **YouTube**: ``agoras youtube <action>`` - Video platform (video, like, delete)
- **TikTok**: ``agoras tiktok <action>`` - Video platform (video, delete)
- **Threads**: ``agoras threads <action>`` - Meta's platform (post, video, share, reply, analytics, moderation)

Automation Commands
~~~~~~~~~~~~~~~~~~~

Publish from RSS/Atom feeds::

    $ agoras utils feed-publish \
        --network twitter \
        --mode last \
        --feed-url "https://blog.example.com/feed.xml"

Run scheduled posts from Google Sheets::

    $ agoras utils schedule-run \
        --sheets-id "${GOOGLE_SHEETS_ID}" \
        --sheets-name "Schedule"


Examples of usage
~~~~~~~~~~~~~~~~~

.. _Using Agoras with Twitter: https://agoras.readthedocs.io/en/latest/twitter.html
.. _Using Agoras with Facebook: https://agoras.readthedocs.io/en/latest/facebook.html
.. _Using Agoras with Instagram: https://agoras.readthedocs.io/en/latest/instagram.html
.. _Using Agoras with LinkedIn: https://agoras.readthedocs.io/en/latest/linkedin.html
.. _Using Agoras with Discord: https://agoras.readthedocs.io/en/latest/discord.html
.. _Using Agoras with YouTube: https://agoras.readthedocs.io/en/latest/youtube.html
.. _Using Agoras with TikTok: https://agoras.readthedocs.io/en/latest/tiktok.html
.. _Using Agoras with Threads: https://agoras.readthedocs.io/en/latest/threads.html
.. _Migration Guide: https://agoras.readthedocs.io/en/latest/migration.html

- `Using Agoras with Twitter`_
- `Using Agoras with Facebook`_
- `Using Agoras with Instagram`_
- `Using Agoras with LinkedIn`_
- `Using Agoras with Discord`_
- `Using Agoras with YouTube`_
- `Using Agoras with TikTok`_
- `Using Agoras with Threads`_
- `Migration Guide`_ (New CLI Format)


Credentials
~~~~~~~~~~~

.. _How to get credentials for Twitter: https://agoras.readthedocs.io/en/latest/credentials/twitter.html
.. _How to get credentials for Facebook: https://agoras.readthedocs.io/en/latest/credentials/facebook.html
.. _How to get credentials for Instagram: https://agoras.readthedocs.io/en/latest/credentials/instagram.html
.. _How to get credentials for LinkedIn: https://agoras.readthedocs.io/en/latest/credentials/linkedin.html
.. _How to get credentials for Discord: https://agoras.readthedocs.io/en/latest/credentials/discord.html
.. _How to get credentials for YouTube: https://agoras.readthedocs.io/en/latest/credentials/youtube.html
.. _How to get credentials for TikTok: https://agoras.readthedocs.io/en/latest/credentials/tiktok.html
.. _How to get credentials for Google spreadsheets: https://agoras.readthedocs.io/en/latest/credentials/google.html

- `How to get credentials for Twitter`_
- `How to get credentials for Facebook`_
- `How to get credentials for Instagram`_
- `How to get credentials for LinkedIn`_
- `How to get credentials for Discord`_
- `How to get credentials for YouTube`_
- `How to get credentials for TikTok`_
- `How to get credentials for Google spreadsheets`_

Getting help
============

.. _Discord server: https://discord.gg/GRnq3qQ9SB
.. _StackOverflow: http://stackoverflow.com/questions/ask

If you have any doubts or problems, suscribe to our `Discord server`_ and ask for help. You can also
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

Copyright 2022-2023, agoras Developers (read AUTHORS_ for a full list of copyright holders).

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
