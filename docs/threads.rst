Using Agoras with Threads
==========================

.. note::
   **New in version 2.0**: Threads platform support added to Agoras CLI.

Threads is Meta's text-based conversation platform. Agoras provides full CLI support for posting, sharing, and managing Threads content.

Available Actions
-----------------

The Threads platform supports the following actions:

* ``authorize`` - Set up OAuth 2.0 authentication (required first step)
* ``post`` - Create text and image posts
* ``video`` - Upload videos
* ``share`` - Share/repost existing content

.. note::
   Threads API is still maturing. Some features may have limitations or require specific API access levels.

Prerequisites
-------------

Before using Agoras with Threads, you need:

1. A Meta (Facebook) Developer account
2. A registered Meta app with Threads API access
3. App ID and App Secret from your Meta app
4. A redirect URI for OAuth callbacks

See :doc:`credentials/threads` for detailed setup instructions.

Quick Start
-----------

Authorization
~~~~~~~~~~~~~

.. versionadded:: 2.0
   OAuth 2.0 "authorize first" workflow

Before performing any actions, you must authorize Agoras to access your Threads account::

    agoras threads authorize \
      --app-id "$THREADS_APP_ID" \
      --app-secret "$THREADS_APP_SECRET" \
      --redirect-uri "http://localhost:3456/callback"

This will:

1. Open your browser to Meta's OAuth authorization page
2. Prompt you to grant permissions to Agoras
3. Automatically capture the authorization code
4. Store encrypted credentials in ``~/.agoras/tokens/``

After authorization, you can perform actions without providing tokens. Credentials are automatically refreshed when needed.

For CI/CD environments, see :doc:`credentials/threads` for headless authorization setup.

Creating a Post
~~~~~~~~~~~~~~~

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
~~~~~~~~~~~~~~~~~

Upload a video to Threads::

    agoras threads video \
      --video-url "https://example.com/video.mp4" \
      --video-title "My Threads Video"

.. note::
   You must run ``agoras threads authorize`` first before using this command.

Sharing a Post
~~~~~~~~~~~~~~

Share/repost a Threads post::

    agoras threads share \
      --post-id "threads_post_id"

.. note::
   You must run ``agoras threads authorize`` first before using this command.

Using Environment Variables
----------------------------

.. versionchanged:: 2.0
   Environment variables are no longer needed for OAuth platforms after authorization.

After running ``agoras threads authorize``, credentials are stored securely and you can use shorter commands::

    agoras threads post --text "Hello Threads!"

Feed Automation
---------------

Publish content from RSS/Atom feeds to Threads::

    agoras utils feed-publish \
      --network threads \
      --mode last \
      --feed-url "https://blog.example.com/feed.xml" \
      --max-count 1 \
      --post-lookback 3600

Publish a random item from an RSS feed::

    agoras utils feed-publish \
      --network threads \
      --mode random \
      --feed-url "https://blog.example.com/feed.xml" \
      --max-post-age 365

The feed should include:
- ``<title>`` - Used as post text
- ``<link>`` or ``<guid>`` - Included in post
- ``<enclosure>`` - Image URL for the post

Please read about how the RSS feed should be structured in the :doc:`RSS feed section <rss>`.

.. note::
   You must run ``agoras threads authorize`` first before using these commands.

Scheduling Posts
----------------

Schedule Threads posts using Google Sheets integration::

    agoras utils schedule-run \
      --network threads \
      --sheets-id "${GOOGLE_SHEETS_ID}" \
      --sheets-name "Threads" \
      --sheets-client-email "${GOOGLE_SHEETS_CLIENT_EMAIL}" \
      --sheets-private-key "${GOOGLE_SHEETS_PRIVATE_KEY}"

.. note::
   You must run ``agoras threads authorize`` first before using this command.

The Google Sheets format for Threads posts should have the following columns in order:

+---------------------+-------------------+---------------------+---------------------+---------------------+-------------------------+-------------------+------------------------------+
| ``status_text``     | ``status_link``   | ``status_image_url_1`` | ``status_image_url_2`` | ``status_image_url_3`` | ``status_image_url_4`` | date (%d-%m-%Y)   | time (%H) | status (draft/published) |
+---------------------+-------------------+---------------------+---------------------+---------------------+-------------------------+-------------------+------------------------------+

Example schedule row:

+------------------+-------------------+---------------------+---------------------+---------------------+-------------------------+-------------+------+----------+
| Hello Threads!   | https://example.com | https://img1.jpg  |                     |                     |                         | 21-11-2024  | 17   | draft    |
+------------------+-------------------+---------------------+---------------------+---------------------+-------------------------+-------------+------+----------+

This would create a post at 17:00 on November 21, 2024 with the text "Hello Threads!" and one image.

For this command to work, it should be executed hourly by a cron script.

Limitations
-----------

The Threads platform has the following limitations:

1. **Like and Delete**: Like and delete actions are not supported by the Threads API
2. **API Access**: Threads API may require specific access levels from Meta
3. **Rate Limits**: Threads API has rate limits that may affect automation
4. **Business Account**: Some features (like analytics/insights) may require a verified Meta Business account
5. **App Review**: Production use may require app review and approval from Meta
6. **Media Formats**: Images must be JPEG or PNG format

Troubleshooting
---------------

Common Issues and Solutions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**"Threads API not authenticated" error**:
- Make sure you've run ``agoras threads authorize`` first
- Verify your app credentials are correct
- Check that your refresh token hasn't expired (tokens last 60 days)
- Re-run authorization if needed

**"Business account required" error**:
- Some features (like analytics) require a verified Meta Business account
- Link your business account to your app in Meta Developer Console
- Complete business verification if not already done
- See :doc:`credentials/threads` for business account setup

**"Rate limit exceeded" error**:
- Threads API has rate limits that vary by account type
- Wait before retrying the request
- Consider implementing delays between automated posts
- Check Meta's rate limit documentation

**"Media validation failed" error**:
- Ensure images are in JPEG or PNG format
- Verify image URLs are accessible and valid
- Check that image files aren't corrupted
- Ensure image URLs use HTTPS (recommended)

**"Post ID is required" error**:
- Make sure you're providing the correct post ID for share actions
- Post IDs are returned when you create posts
- Verify the post ID format matches Threads' expected format

**"Redirect URI mismatch" error**:
- Ensure the redirect URI in your command exactly matches the one in Meta app settings
- Check for trailing slashes or protocol differences
- Verify the redirect URI is added to your app's allowed list

**OAuth authorization fails**:
- Make sure you're logged into the correct Facebook/Threads account
- Check that your app has the required permissions enabled
- Verify your redirect URI is correctly configured
- Clear browser cache and try again

Getting Help
------------

* Run ``agoras threads --help`` to see all available actions
* Run ``agoras threads post --help`` for detailed post options
* See :doc:`credentials/threads` for credential setup
* See the `Threads API documentation <https://developers.facebook.com/docs/threads>`_
* Report issues at https://github.com/LuisAlejandro/agoras/issues
