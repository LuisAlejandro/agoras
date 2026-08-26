Usage for YouTube
=================

YouTube is a video sharing platform that allows users to upload, view, and share videos. Agoras provides full support for uploading videos to YouTube, as well as liking and deleting videos via the YouTube Data API v3.

.. note::

   Agoras uses ``agoras youtube`` for YouTube operations.
   See the :doc:`migration guide <migration/index>` for upgrading from ``agoras publish``.

.. versionadded:: 2.0
   OAuth 2.0 "authorize first" workflow

Required Credentials
--------------------

Before using Agoras with YouTube, you'll need to obtain the following credentials from the Google Cloud Console:

- **Client ID** (``YOUTUBE_CLIENT_ID``): Your Google OAuth 2.0 Client ID
- **Client Secret** (``YOUTUBE_CLIENT_SECRET``): Your Google OAuth 2.0 Client Secret

See :doc:`credentials/youtube` for detailed instructions on how to set up your Google Cloud project, enable the YouTube Data API v3, and obtain these credentials.

Available Actions
~~~~~~~~~~~~~~~~~

* ``authorize`` - Set up OAuth 2.0 authentication (required first step)
* ``video`` - Upload and publish a video to YouTube
* ``like`` - Like a YouTube video
* ``delete`` - Delete a YouTube video

Authorization
-------------

Before performing any actions, you must authorize Agoras to access your YouTube account::

    agoras youtube authorize \
      --client-id "${YOUTUBE_CLIENT_ID}" \
      --client-secret "${YOUTUBE_CLIENT_SECRET}"

This will:

1. Open your browser to Google's OAuth 2.0 authorization page
2. Prompt you to grant permissions to Agoras
3. Automatically capture the authorization code
4. Store encrypted credentials in ``~/.agoras/tokens/``

After authorization, you can perform actions without providing credentials. They are automatically refreshed when needed.

For CI/CD environments, see :doc:`credentials/youtube` for unattended execution setup.

Upload a video to YouTube
-------------------------

This command uploads a video file from a local path or a remote URL to your YouTube channel.

.. note::

   You must run ``agoras youtube authorize`` first before using this command.

**New format**::

    agoras youtube video \
      --video-url "${VIDEO_URL}" \
      --title "My Awesome Video" \
      --description "This is a video description" \
      --category-id "22" \
      --privacy "public" \
      --keywords "awesome,video,agoras"

**Parameters**:

* ``--video-url`` (required): Local file path or public URL of the video to upload.
* ``--title`` (optional): The title of the video.
* ``--description`` (optional): The description of the video.
* ``--category-id`` (optional): The numeric YouTube category ID (e.g., ``22`` for People & Blogs, ``28`` for Science & Technology).
* ``--privacy`` (optional): Video privacy status. Choices are ``public``, ``private``, or ``unlisted`` (default: ``private``).
* ``--keywords`` (optional): Comma-separated list of keywords/tags for the video.

Like a YouTube video
--------------------

You can like a specific video on YouTube by providing its video ID.

.. note::

   You must run ``agoras youtube authorize`` first before using this command.

**New format**::

    agoras youtube like \
      --video-id "${VIDEO_ID}"

Delete a YouTube video
----------------------

You can delete a specific video from your channel by providing its video ID.

.. note::

   You must run ``agoras youtube authorize`` first before using this command.

**New format**::

    agoras youtube delete \
      --video-id "${VIDEO_ID}"

Post the last video from an RSS feed into YouTube
--------------------------------------------------

This command will parse an RSS feed located at ``--feed-url``, extract video URLs from the feed entries, and upload them to YouTube.

.. note::

   You must run ``agoras youtube authorize`` first before using this command.

Please read about how the RSS feed should be structured in the :doc:`RSS feed section <rss>`.
::

      agoras utils feed-publish \
            --network "youtube" \
            --mode "last" \
            --feed-url "${FEED_URL}" \
            --max-count "${MAX_COUNT}" \
            --post-lookback "${POST_LOOKBACK}"

Scheduling YouTube video publishing
------------------------------------

You can schedule video publishing from a Google Sheet that contains video paths/URLs and descriptions.

.. note::

   You must run ``agoras youtube authorize`` first before using this command.

See :doc:`usage` and :doc:`credentials/google` for how to configure and authorize Google Sheets.
::

      agoras utils schedule \
            --spreadsheet-id "${SPREADSHEET_ID}" \
            --sheet-name "${SHEET_NAME}" \
            --youtube-client-id "${YOUTUBE_CLIENT_ID}" \
            --youtube-client-secret "${YOUTUBE_CLIENT_SECRET}"
