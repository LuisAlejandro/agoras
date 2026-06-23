Usage for X (formerly Twitter)
==============================

.. note::

   Agoras uses ``agoras x`` for X (formerly Twitter) operations.
   See the :doc:`migration guide <migration/index>` for upgrading from ``agoras publish``.

.. deprecated:: 2.0
   The ``agoras twitter`` command is deprecated. Use ``agoras x`` instead.

X (formerly Twitter) is a social network that allows you to publish short messages (called posts) of up to 280 characters. Agoras provides full CLI support for posting, liking, sharing, and deleting X content.

**Important**: X now requires a paid subscription for certain parts of the API. The free tier will let you publish and delete X posts, but may have limitations on likes or retweets depending on your API access level.

Required Credentials
--------------------

Before using Agoras with X, you'll need to manually extract the following credentials from your X Developer account. These credentials are required for authentication and API access.

- **API Key** (``TWITTER_CONSUMER_KEY``): Your X app's API key, also known as consumer key
- **API Secret Key** (``TWITTER_CONSUMER_SECRET``): Your X app's API secret key, also known as consumer secret

See :doc:`credentials/x` for detailed instructions on how to obtain these credentials from the X Developer Portal.

Available Actions
~~~~~~~~~~~~~~~~~

* ``authorize`` - Set up OAuth 1.0a authentication (required first step)
* ``post`` - Create text and image posts (up to 4 images)
* ``video`` - Upload videos
* ``like`` - Like posts
* ``share`` - Retweet/share posts
* ``delete`` - Delete your own posts

Authorization
-------------

.. versionadded:: 2.0
   OAuth 1.0a "authorize first" workflow

Before performing any actions, you must authorize Agoras to access your X account::

    agoras x authorize \
      --consumer-key "${TWITTER_CONSUMER_KEY}" \
      --consumer-secret "${TWITTER_CONSUMER_SECRET}"

This will:

1. Open your browser to the X OAuth authorization page
2. Prompt you to grant permissions to Agoras
3. Store encrypted credentials in ``~/.agoras/tokens/``

After authorization, you can perform actions without providing OAuth tokens. Credentials are automatically loaded from storage.

For CI/CD environments, see :doc:`credentials/x` for unattended execution setup.

Post a Tweet
------------

**New format** (Agoras 2.0+)::

    agoras x post \
      --text "${STATUS_TEXT}" \
      --image-1 "${IMAGE_URL_1}" \
      --image-2 "${IMAGE_URL_2}"

.. note::
   You must run ``agoras x authorize`` first before using this command.

Like a Tweet
------------

**New format**::

    agoras x like \
      --post-id "${TWEET_ID}"

.. note::
   You must run ``agoras x authorize`` first before using this command.

Share a Tweet (Retweet)
-----------------------

**New format**::

    agoras x share \
      --post-id "${TWEET_ID}"

.. note::
   You must run ``agoras x authorize`` first before using this command.

Delete a Tweet
--------------

**New format**::

    agoras x delete \
      --post-id "${TWEET_ID}"

.. note::
   You must run ``agoras x authorize`` first before using this command.

Upload a Video
--------------

**New format**::

    agoras x video \
      --video-url "${VIDEO_URL}" \
      --video-title "${VIDEO_TITLE}"

.. note::
   You must run ``agoras x authorize`` first before using this command.



Post the last URL from an RSS feed into X
-----------------------------------------

This command will parse an RSS feed located at ``--feed-url``, and publish the last ``--max-count`` number of entries published in the last ``--post-lookback`` number of seconds. The post content will consist of the title and the link of the feed entry.

.. note::
   You must run ``agoras x authorize`` first before using this command.

Please read about how the RSS feed should be structured in the :doc:`RSS feed section <rss>`. This ensures that the feed is correctly parsed and that the post content is properly formatted.
::

    agoras utils feed-publish \
      --network x \
      --mode last \
      --feed-url "${FEED_URL}" \
      --max-count "${MAX_COUNT}" \
      --post-lookback "${POST_LOOKBACK}"

.. note::
   The ``--network twitter`` and ``--twitter-*`` parameters are deprecated. Use ``--network x`` and ``--x-*`` parameters instead.



Post a random URL from an RSS feed into X
------------------------------------------

This command will parse an RSS feed at ``--feed-url`` and publish one random entry that's not older than ``--max-post-age``. The post content will consist of the title and the link of the feed entry.

.. note::
   You must run ``agoras x authorize`` first before using this command.

Please read about how the RSS feed should be structured in the :doc:`RSS feed section <rss>`. This ensures that the feed is correctly parsed and that the post content is properly formatted.
::

    agoras utils feed-publish \
      --network x \
      --mode random \
      --feed-url "${FEED_URL}" \
      --max-post-age "${MAX_POST_AGE}"

.. note::
   The ``--network twitter`` and ``--twitter-*`` parameters are deprecated. Use ``--network x`` and ``--x-*`` parameters instead.



Google Sheets Scheduling
------------------------

Agoras can schedule X posts using Google Sheets. This allows you to plan and automate post publishing.

Run Scheduled Messages
~~~~~~~~~~~~~~~~~~~~~~

Process scheduled messages from a Google Sheet:

::

    agoras utils schedule-run \
      --network x \
      --sheets-id "${GOOGLE_SHEETS_ID}" \
      --sheets-name "X" \
      --sheets-client-email "${GOOGLE_SHEETS_CLIENT_EMAIL}" \
      --sheets-private-key "${GOOGLE_SHEETS_PRIVATE_KEY}"

.. note::
   You must run ``agoras x authorize`` first before using this command.

Sheet Format
~~~~~~~~~~~~

Your Google Sheet should have the following columns:

- ``status_text``: Post text content
- ``status_link``: URL to include in post
- ``status_image_url_1`` through ``status_image_url_4``: Image URLs (optional)
- ``date``: Scheduled date (format: DD-MM-YYYY)
- ``hour``: Scheduled hour (format: HH, 24-hour format)
- ``state``: Post state (``pending``, ``published``, ``error``)

**Example sheet row**:

::

    status_text,status_link,status_image_url_1,status_image_url_2,status_image_url_3,status_image_url_4,date,hour,state
    "This is a test X post","https://agoras.luisalejandro.org/en/latest/","https://pbs.twimg.com/media/Ej3d42zXsAEfDCr?format=jpg","https://pbs.twimg.com/media/Ej3d42zXsAEfDCr?format=jpg","","","21-11-2022","17","pending"

Scheduling Logic
~~~~~~~~~~~~~~~~

- Posts with ``state="pending"`` and scheduled time in the past are processed
- Posts are created at the scheduled date and hour
- Sheet state is updated to ``published`` after successful posting
- If posting fails, state is updated to ``error``
- Use ``--network x`` to process only X posts, or omit to process all networks


.. _how-to-get-twitter-post-id:

How to get ``--post-id`` parameter
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Extracting from X website
-------------------------

The post ID parameter is necessary to delete posts. You can extract it from the post URL::

      https://twitter.com/XXXXX/status/NNNNNNNNNNN

``NNNNNNNNNNN`` is the post ID.

Using Agoras
------------

When you create an X post with Agoras, it will print the post ID (in json format) in the console. You can copy it from there and use it in other commands. For example::

      $ agoras x post --text "This is a test post"
      $ {"id":"NNNNNNNNNNN"}

``NNNNNNNNNNN`` is the post ID.
