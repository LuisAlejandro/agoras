Usage for TikTok
================

TikTok is a short-form video social platform that allows users to create and share videos with various effects, filters, and music. Agoras can publish videos, photo slideshows, and schedule content on TikTok using the official `TikTok for Developers API <https://developers.tiktok.com/>`_.

**Important**: TikTok requires OAuth 2.0 authentication and app approval. You must first create a TikTok for Developers app and get it approved before using these features. Like, share, and delete actions are not supported by the TikTok API.

Required Credentials
--------------------

Before using Agoras with TikTok, you'll need to manually extract the following credentials from your TikTok for Developers app. These credentials are required for OAuth 2.0 authentication and content publishing.

- **Client Key** (``TIKTOK_CLIENT_KEY``): Your TikTok app's client key (App ID), used as the OAuth client identifier
- **Client Secret** (``TIKTOK_CLIENT_SECRET``): Your TikTok app's client secret, used for OAuth authentication
- **Username** (``TIKTOK_USERNAME``): Your TikTok username (handle without the @ symbol) for the account you want to post to

See :doc:`credentials/tiktok` for detailed instructions on how to create a TikTok for Developers app, get it approved, and obtain these credentials.

Available Actions
~~~~~~~~~~~~~~~~~

* ``authorize`` - Set up OAuth 2.0 authentication (required first step)
* ``video`` - Upload videos to TikTok
* ``post`` - Create photo slideshow posts
* ``reply`` - Reply to a comment (CLI only; runtime raises not supported)
* ``get-post`` - Read a post/message by ID (CLI only; runtime raises not supported)
* ``get-reply`` - Read a reply/comment by ID (CLI only; runtime raises not supported)
* ``list-posts`` - List recent posts (CLI only; runtime raises not supported)

.. note::

   ``get-post``, ``get-reply``, and ``list-posts`` subcommands exist for CLI uniformity with other
   platforms, but TikTok has no official arbitrary-post read API. Invoking these
   actions raises a not-supported error at runtime. The ``reply`` action is also
   listed for CLI uniformity but is not implemented at runtime. See :doc:`reference/action-support`.

Authorization
-------------

.. versionadded:: 2.0
   OAuth 2.0 "authorize first" workflow

Before you can publish content to TikTok, you must authorize Agoras to access your TikTok account. This is a one-time setup process that uses OAuth 2.0 authentication. You'll need your TikTok developer app credentials (read about how to get credentials :doc:`here <credentials/tiktok>`).

::

    agoras tiktok authorize \
      --client-key "${TIKTOK_CLIENT_KEY}" \
      --client-secret "${TIKTOK_CLIENT_SECRET}" \
      --username "${TIKTOK_USERNAME}"

This will:

1. Open your browser to TikTok's OAuth authorization page
2. Prompt you to grant permissions to Agoras
3. Automatically capture the authorization code
4. Store encrypted credentials in ``~/.agoras/tokens/``

After successful authorization, your refresh token will be stored locally and used for future requests. Credentials are automatically refreshed when needed.

For CI/CD environments, see :doc:`credentials/tiktok` for unattended execution setup.

Share to TikTok (interactive post and video)
--------------------------------------------

Interactive ``agoras tiktok post`` and ``agoras tiktok video`` (TTY stdin, ``CI`` unset) open a localhost Share-to-TikTok page **before** Direct Post ``init/``. Authorize still uses ``https://localhost:3456/callback`` (HTTPS). The composer binds HTTP on ``127.0.0.1`` with a different ephemeral port and always prints the URL.

On that page you choose privacy (no default), interactions, and commercial disclosure, then confirm. Media URLs stay on the CLI (``PULL_FROM_URL`` or local ``FILE_UPLOAD``); they are not taken from the form. Local video files are previewed from the composer loopback server so Publish can stay enabled.

::

    agoras tiktok video \
      --video-url "${TIKTOK_VIDEO_URL}" \
      --title "${TIKTOK_TITLE}"

::

    agoras tiktok post \
      --title "${TIKTOK_TITLE}" \
      --image-1 "${IMAGE_URL_1}" \
      --image-2 "${IMAGE_URL_2}"

.. note::
   You must run ``agoras tiktok authorize`` first. Piping stdout (for example ``| jq``) does not skip the composer. ``last-from-feed``, ``random-from-feed``, and ``schedule`` never open it.

Unattended private posts
------------------------

When stdin is not a TTY, or ``CI`` is set, Agoras uses the flag path. Only ``SELF_ONLY`` is allowed (omitted ``--privacy`` defaults to ``SELF_ONLY``). Public, friends, and followers fail closed. ``--brand-organic`` and ``--brand-content`` are rejected; commercial disclosure is composer-only.

::

    agoras tiktok post \
      --title "${TIKTOK_TITLE}" \
      --image-1 "${IMAGE_URL_1}" \
      --privacy SELF_ONLY

Privacy values the composer may offer (from live ``creator_info``):

- ``PUBLIC_TO_EVERYONE``: Everyone
- ``MUTUAL_FOLLOW_FRIENDS``: Friends
- ``FOLLOWER_OF_CREATOR``: Followers
- ``SELF_ONLY``: Only me

**Note**: Duet and stitch options are not available for photo posts.

Post the last video from an RSS feed into TikTok
------------------------------------------------

This command will parse an RSS feed located at ``--feed-url``, and publish the last ``--max-count`` number of entries published in the last ``--post-lookback`` number of seconds. The video content will be extracted from feed enclosures and the title will be used as the TikTok caption.

Please read about how the RSS feed should be structured in the :doc:`RSS feed section <rss>`. This ensures that the feed is correctly parsed and that video content is properly formatted.

**New format** (Agoras 2.0+)::

    agoras utils feed-publish \
      --network tiktok \
      --mode last \
      --feed-url "${FEED_URL}" \
      --max-count "${MAX_COUNT}" \
      --post-lookback "${POST_LOOKBACK}"

Post a random video from an RSS feed into TikTok
------------------------------------------------

This command will parse an RSS feed at ``--feed-url`` and publish one random entry that's not older than ``--max-post-age``. The video content will be extracted from feed enclosures and the title will be used as the TikTok caption.

Please read about how the RSS feed should be structured in the :doc:`RSS feed section <rss>`. This ensures that the feed is correctly parsed and that video content is properly formatted.

**New format** (Agoras 2.0+)::

    agoras utils feed-publish \
      --network tiktok \
      --mode random \
      --feed-url "${FEED_URL}" \
      --max-post-age "${MAX_POST_AGE}"

Google Sheets Scheduling
------------------------

Agoras can schedule TikTok posts using Google Sheets. This allows you to plan and automate video publishing.

Run Scheduled Messages
~~~~~~~~~~~~~~~~~~~~~~

Process scheduled messages from a Google Sheet:

::

    agoras utils schedule-run \
      --network tiktok \
      --sheets-id "${GOOGLE_SHEETS_ID}" \
      --sheets-name "TikTok" \
      --sheets-client-email "${GOOGLE_SHEETS_CLIENT_EMAIL}" \
      --sheets-private-key "${GOOGLE_SHEETS_PRIVATE_KEY}" \
      --tiktok-username "${TIKTOK_USERNAME}"

.. note::
   You must run ``agoras tiktok authorize`` first before using this command.

Sheet Format
~~~~~~~~~~~~

Your Google Sheet should have the following columns:

- ``tiktok_video_url``: URL to the video file
- ``tiktok_title``: Video title/caption
- ``tiktok_privacy_status``: Unattended privacy; only ``SELF_ONLY`` is published without the composer
- ``allow_comments``: Allow comments (``TRUE`` or ``FALSE``)
- ``allow_duet``: Allow duets (``TRUE`` or ``FALSE``)
- ``allow_stitch``: Allow stitches (``TRUE`` or ``FALSE``)
- ``is_brand_organic``: Mark as promotional content (``TRUE`` or ``FALSE``)
- ``is_brand_content``: Mark as paid partnership (``TRUE`` or ``FALSE``)
- ``auto_add_music``: Automatically add music (``TRUE`` or ``FALSE``)
- ``date``: Scheduled date (format: DD-MM-YYYY)
- ``hour``: Scheduled hour (format: HH, 24-hour format)
- ``state``: Post state (``pending``, ``published``, ``error``)

**Example sheet row**:

::

    tiktok_video_url,tiktok_title,tiktok_privacy_status,allow_comments,allow_duet,allow_stitch,is_brand_organic,is_brand_content,auto_add_music,date,hour,state
    "https://example.com/video.mp4","My awesome TikTok video","SELF_ONLY","TRUE","TRUE","TRUE","FALSE","FALSE","FALSE","21-11-2022","17","pending"

Scheduling Logic
~~~~~~~~~~~~~~~~

- Posts with ``state="pending"`` and scheduled time in the past are processed
- Posts are created at the scheduled date and hour
- Sheet state is updated to ``published`` after successful posting
- If posting fails, state is updated to ``error``
- Use ``--network tiktok`` to process TikTok posts from the sheet (required since 2.1.0; one platform per run)

Brand Content and Promotional Content
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Commercial disclosure is set on the interactive Share-to-TikTok page (Your Brand / Branded Content plus TikTok's consent copy). Unattended ``--brand-organic`` and ``--brand-content`` are rejected. Branded content cannot be combined with Only me (``SELF_ONLY``).

Limitations
~~~~~~~~~~~

- **File formats**: Videos must be MP4, MOV, or WebM. Images must be JPEG or PNG.
- **Video duration**: Limited by your account's maximum video duration (varies by account type)
- **No direct interactions**: Like, share, and delete actions are not supported by the TikTok API
- **OAuth required**: All actions require going through the OAuth authorization flow
- **App approval**: Your TikTok developer app must be approved for production use

Getting your post ID
~~~~~~~~~~~~~~~~~~~~

When you create a TikTok post with Agoras, it will print the publish ID (in JSON format) in the console:

::

      $ agoras tiktok video \
            --video-url "https://example.com/video.mp4" \
            --title "My awesome video"
      $ {"id":"NNNNNNNNNNN"}

``NNNNNNNNNNN`` is the publish ID that can be used to track the post status.
