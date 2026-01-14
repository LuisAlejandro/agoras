Usage for TikTok
================

TikTok is a short-form video social platform that allows users to create and share videos with various effects, filters, and music. Agoras can publish videos, photo slideshows, and schedule content on TikTok using the official `TikTok for Developers API <https://developers.tiktok.com/>`_.

**Important**: TikTok requires OAuth 2.0 authentication and app approval. You must first create a TikTok for Developers app and get it approved before using these features. Like, share, and delete actions are not supported by the TikTok API.

Actions
~~~~~~~

* ``authorize`` - Set up OAuth 2.0 authentication (required first step)
* ``video`` - Upload videos to TikTok
* ``post`` - Create photo slideshow posts

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

For CI/CD environments, see :doc:`credentials/tiktok` for headless authorization setup.

Publish a TikTok video
----------------------

This command will upload and publish a video to TikTok. ``--title`` is required and will be the video's caption. ``--video-url`` must point to a downloadable video file in MP4, MOV, or WebM format.

.. note::
   You must run ``agoras tiktok authorize`` first before using this command.

**New format**::

    agoras tiktok video \
      --username "${TIKTOK_USERNAME}" \
      --video-url "${TIKTOK_VIDEO_URL}" \
      --title "${TIKTOK_TITLE}" \
      --privacy-status "${TIKTOK_PRIVACY_STATUS}"

Optional parameters for video posts:

- ``--tiktok-allow-comments``: Allow comments on the video (default: true)
- ``--tiktok-allow-duet``: Allow other users to duet with your video (default: true)
- ``--tiktok-allow-stitch``: Allow other users to stitch your video (default: true)
- ``--brand-organic``: Mark content as promotional (displays "Promotional content" label)
- ``--brand-content``: Mark content as paid partnership (displays "Paid partnership" label)

Privacy status options:
- ``PUBLIC_TO_EVERYONE``: Public to everyone
- ``MUTUAL_FOLLOW_FRIENDS``: Friends only
- ``FOLLOWER_OF_CREATOR``: Followers only
- ``SELF_ONLY``: Private (only you can see it)

Publish a TikTok photo slideshow
--------------------------------

This command will create a photo slideshow post on TikTok. You can include up to 4 images using the ``--image-X`` parameters. TikTok will automatically add music to photo posts.

.. note::
   You must run ``agoras tiktok authorize`` first before using this command.

**New format**::

    agoras tiktok post \
      --username "${TIKTOK_USERNAME}" \
      --title "${TIKTOK_TITLE}" \
      --image-1 "${IMAGE_URL_1}" \
      --image-2 "${IMAGE_URL_2}" \
      --image-3 "${IMAGE_URL_3}" \
      --image-4 "${IMAGE_URL_4}" \
      --privacy-status "${TIKTOK_PRIVACY_STATUS}"

Optional parameters for photo posts:

- ``--tiktok-allow-comments``: Allow comments on the post (default: true)
- ``--tiktok-auto-add-music``: Automatically add music to the slideshow (default: false)
- ``--brand-organic``: Mark content as promotional
- ``--brand-content``: Mark content as paid partnership

**Note**: Duet and stitch options are not available for photo posts.

Post the last video from an RSS feed into TikTok
------------------------------------------------

This command will parse an RSS feed located at ``--feed-url``, and publish the last ``--max-count`` number of video entries published in the last ``--post-lookback`` number of seconds. The video content will be extracted from feed enclosures and the title will be used as the TikTok caption.

Please read about how the RSS feed should be structured in the :doc:`RSS feed section <rss>`. This ensures that the feed is correctly parsed and that video content is properly formatted.

**New format** (Agoras 2.0+)::

    agoras utils feed-publish \
      --network tiktok \
      --mode last \
      --feed-url "${FEED_URL}" \
      --max-count "${MAX_COUNT}" \
      --post-lookback "${POST_LOOKBACK}" \
      --tiktok-username "${TIKTOK_USERNAME}" \
      --tiktok-client-key "${TIKTOK_CLIENT_KEY}" \
      --tiktok-client-secret "${TIKTOK_CLIENT_SECRET}" \
      --tiktok-privacy-status "${TIKTOK_PRIVACY_STATUS}"

Post a random video from an RSS feed into TikTok
------------------------------------------------

This command will parse an RSS feed at ``--feed-url`` and publish one random video entry that's not older than ``--max-post-age`` days. The video content will be extracted from feed enclosures and the title will be used as the TikTok caption.

Please read about how the RSS feed should be structured in the :doc:`RSS feed section <rss>`. This ensures that the feed is correctly parsed and that video content is properly formatted.

**New format** (Agoras 2.0+)::

    agoras utils feed-publish \
      --network tiktok \
      --mode random \
      --feed-url "${FEED_URL}" \
      --max-post-age "${MAX_POST_AGE}" \
      --tiktok-username "${TIKTOK_USERNAME}" \
      --tiktok-client-key "${TIKTOK_CLIENT_KEY}" \
      --tiktok-client-secret "${TIKTOK_CLIENT_SECRET}" \
      --tiktok-privacy-status "${TIKTOK_PRIVACY_STATUS}"

Schedule a TikTok post
---------------------

This command will scan a sheet ``--sheets-name`` of a Google spreadsheet with id ``--sheets-id``, that's authorized by ``--sheets-client-email`` and ``--sheets-private-key``. Videos will be published using the TikTok account authorized by your credentials.

The order of the columns of the spreadsheet is crucial to the correct functioning of the command. Here's how the information should be organized:

+---------------------+-------------------+-----------------------------+---------------------+--------------------+----------------------+---------------------+---------------------+---------------------+-------------------------+-------------------+------------------------------+
| ``tiktok_video_url``| ``tiktok_title``  | ``tiktok_privacy_status``   | ``allow_comments``  | ``allow_duet``     | ``allow_stitch``     | ``is_brand_organic``| ``is_brand_content``| ``auto_add_music``  | date (%d-%m-%Y format)  | time (%H format)  | status (draft or published)  |
+---------------------+-------------------+-----------------------------+---------------------+--------------------+----------------------+---------------------+---------------------+---------------------+-------------------------+-------------------+------------------------------+

The boolean columns (``allow_comments``, ``allow_duet``, ``allow_stitch``, ``is_brand_organic``, ``is_brand_content``, ``auto_add_music``) should contain ``TRUE`` or ``FALSE`` values.

Example of a working schedule:

+-----------------------------------------------+-------------------------+---------------------+------------------+---------------+------------------+------------------+------------------+------------------+-------------+-----+--------+
| https://example.com/video.mp4                | My awesome TikTok video | PUBLIC_TO_EVERYONE  | TRUE             | TRUE          | TRUE             | FALSE            | FALSE            | FALSE            | 21-11-2022  | 17  | draft  |
+-----------------------------------------------+-------------------------+---------------------+------------------+---------------+------------------+------------------+------------------+------------------+-------------+-----+--------+

This schedule entry would be published at 17:00h of 21-11-2022 with the specified video and settings.

For this command to work, it should be executed hourly by a cron script.

**New format** (Agoras 2.0+)::

    agoras utils schedule-run \
      --network tiktok \
      --sheets-id "${GOOGLE_SHEETS_ID}" \
      --sheets-name "${GOOGLE_SHEETS_NAME}" \
      --sheets-client-email "${GOOGLE_SHEETS_CLIENT_EMAIL}" \
      --sheets-private-key "${GOOGLE_SHEETS_PRIVATE_KEY}" \
      --tiktok-username "${TIKTOK_USERNAME}" \
      --tiktok-client-key "${TIKTOK_CLIENT_KEY}" \
      --tiktok-client-secret "${TIKTOK_CLIENT_SECRET}"

Brand Content and Promotional Content
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

TikTok requires proper labeling of commercial content:

**Promotional Content** (``--brand-organic``):
  - Use when featuring your own products/services
  - Displays "Promotional content" label
  - Requires agreement to TikTok's Music Usage Confirmation

**Paid Partnership** (``--brand-content``):
  - Use when content is sponsored by another brand
  - Displays "Paid partnership" label
  - Requires agreement to TikTok's Branded Content Policy and Music Usage Confirmation

**Combined** (both flags):
  - Displays "Paid partnership" label
  - Requires agreement to both policies

**Important**: You cannot use ``--brand-content`` with ``--tiktok-privacy-status SELF_ONLY`` (private posts).

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
            --username myusername \
            --video-url "https://example.com/video.mp4" \
            --title "My awesome video"
      $ {"id":"NNNNNNNNNNN"}

``NNNNNNNNNNN`` is the publish ID that can be used to track the post status.
