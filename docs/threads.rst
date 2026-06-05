Usage for Threads
==========================

.. note::
   **New in version 2.0**: Threads platform support added to Agoras CLI.

Threads is Meta's text-based conversation platform. Agoras provides full CLI support for posting, sharing, and managing Threads content.

Required Credentials
--------------------

Before using Agoras with Threads, you'll need to manually extract the following credentials from your Meta App in the Meta Developer Console. These credentials are required for OAuth 2.0 authentication.

- **App ID** (``THREADS_APP_ID``): Your Meta Developer App ID, used as the OAuth client identifier
- **App Secret** (``THREADS_APP_SECRET``): Your Meta Developer App Secret, used for OAuth authentication

See :doc:`credentials/threads` for detailed instructions on how to create a Meta App, enable the Threads API product, and obtain these credentials.

Available Actions
~~~~~~~~~~~~~~~~~

The Threads platform supports the following actions:

* ``authorize`` - Set up OAuth 2.0 authentication (required first step)
* ``post`` - Create text and image posts
* ``video`` - Upload videos
* ``share`` - Share/repost existing content

Authorization
-------------

.. versionadded:: 2.0
   OAuth 2.0 "authorize first" workflow

Before performing any actions, you must authorize Agoras to access your Threads account.

Authorize Agoras to access your Threads account::

    agoras threads authorize \
      --app-id "$THREADS_APP_ID" \
      --app-secret "$THREADS_APP_SECRET"

This will:

1. Open your browser to Meta's OAuth authorization page
2. Prompt you to grant permissions to Agoras
3. Automatically capture the authorization code
4. Store encrypted credentials in ``~/.agoras/tokens/``

After authorization, you can perform actions without providing tokens. Credentials are automatically refreshed when needed.

For CI/CD environments, see :doc:`credentials/threads` for unattended execution setup.

Creating a Post
---------------

Post text to Threads::

    agoras threads post \
      --text "Hello from Agoras on Threads!"

Post with an image::

    agoras threads post \
      --text "Check out this image!" \
      --image-1 "https://example.com/image.jpg"

.. note::
   You must run ``agoras threads authorize`` first before using these commands.

Uploading a Video
------------------

Upload a video to Threads::

    agoras threads video \
      --video-url "https://example.com/video.mp4" \
      --video-title "My Threads Video"

.. note::
   You must run ``agoras threads authorize`` first before using this command.

Sharing a Post
---------------

Share/repost a Threads post::

    agoras threads share \
      --post-id "threads_post_id"

.. note::
   You must run ``agoras threads authorize`` first before using this command.

Post the last URL from an RSS feed into Threads
------------------------------------------------

This command will parse an RSS feed located at ``--feed-url``, and publish the last ``--max-count`` number of entries published in the last ``--post-lookback`` number of seconds. The post content will consist of the title and the link of the feed entry.

.. note::
   You must run ``agoras threads authorize`` first before using this command.

Please read about how the RSS feed should be structured in the :doc:`RSS feed section <rss>`. This ensures that the feed is correctly parsed and that the post content is properly formatted.
::

    agoras utils feed-publish \
      --network threads \
      --mode last \
      --feed-url "${FEED_URL}" \
      --max-count "${MAX_COUNT}" \
      --post-lookback "${POST_LOOKBACK}"


Post a random URL from an RSS feed into Threads
------------------------------------------------

This command will parse an RSS feed at ``--feed-url`` and publish one random entry that's not older than ``--max-post-age``. The post content will consist of the title and the link of the feed entry.

.. note::
   You must run ``agoras threads authorize`` first before using this command.

Please read about how the RSS feed should be structured in the :doc:`RSS feed section <rss>`. This ensures that the feed is correctly parsed and that the post content is properly formatted.
::

    agoras utils feed-publish \
      --network threads \
      --mode random \
      --feed-url "${FEED_URL}" \
      --max-post-age "${MAX_POST_AGE}"

Google Sheets Scheduling
------------------------

Agoras can schedule Threads posts using Google Sheets. This allows you to plan and automate post publishing.

Run Scheduled Messages
~~~~~~~~~~~~~~~~~~~~~~

Process scheduled messages from a Google Sheet:

::

    agoras utils schedule-run \
      --network threads \
      --sheets-id "${GOOGLE_SHEETS_ID}" \
      --sheets-name "Threads" \
      --sheets-client-email "${GOOGLE_SHEETS_CLIENT_EMAIL}" \
      --sheets-private-key "${GOOGLE_SHEETS_PRIVATE_KEY}"

.. note::
   You must run ``agoras threads authorize`` first before using this command.

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
    "Hello Threads!","https://example.com","https://img1.jpg","","","","21-11-2024","17","pending"

Scheduling Logic
~~~~~~~~~~~~~~~~

- Posts with ``state="pending"`` and scheduled time in the past are processed
- Posts are created at the scheduled date and hour
- Sheet state is updated to ``published`` after successful posting
- If posting fails, state is updated to ``error``
- Use ``--network threads`` to process only Threads posts, or omit to process all networks
