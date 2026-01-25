agoras-common
=============

Low-level utilities, logging, and shared constants for the Agoras ecosystem.

Installation
------------

.. code-block:: bash

   pip install agoras-common

Contents
--------

- **Version Info**: ``__version__``, ``__author__``, ``__email__``, ``__url__``, ``__description__``
- **Utilities**: Helper functions for URL manipulation, metadata parsing
- **Logger**: Centralized logging configuration

Usage
-----

.. code-block:: python

   from agoras.common import __version__, logger, add_url_timestamp, parse_metatags

   # Version info
   print(f"Agoras version: {__version__}")

   # Logger
   logger.start()
   logger.loglevel('INFO')
   logger.info("Hello from Agoras!")

   # URL utilities
   timestamped_url = add_url_timestamp('https://example.com', '20260110')
   print(timestamped_url)  # https://example.com?t=20260110

   # Metatag parsing
   metatags = parse_metatags('https://example.com')
   print(metatags['title'], metatags['image'])

Dependencies
------------

None (pure Python utilities)
