agoras (CLI)
============

Command-line interface for managing social network posts.

Installation
------------

.. code-block:: bash

   pip install agoras

This automatically installs all dependencies:

- agoras-common
- agoras-media
- agoras-core
- agoras-platforms

Usage
-----

.. code-block:: bash

   # Authorize Facebook (one-time OAuth setup)
   agoras facebook authorize \
       --client-id "$CLIENT_ID" \
       --client-secret "$CLIENT_SECRET" \
       --app-id "$APP_ID" \
       --object-id "$OBJECT_ID"

   # Post to Facebook (after authorize)
   agoras facebook post \
       --text "Hello World" \
       --link "https://example.com"

   # Post to X (after authorize, or with TWITTER_* env vars set)
   agoras x post \
       --text "Hello X!"

   # See all commands
   agoras --help

Dependencies
------------

- agoras-platforms (and all its dependencies)
