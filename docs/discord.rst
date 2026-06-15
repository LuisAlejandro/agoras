Usage for Discord
=================

.. note::

   Agoras uses ``agoras discord`` for Discord operations.
   See the :doc:`migration guide <migration/index>` for upgrading from ``agoras publish``.

Discord is a communication platform designed for creating communities. It features text channels, voice channels, and rich media sharing capabilities. Agoras can publish messages, videos, images, and manage scheduled content on Discord using the official `Discord.py library <https://discordpy.readthedocs.io/>`_.

**Important**: Discord uses bot tokens for authentication. You must create a Discord application and bot, then invite it to your server with appropriate permissions before using these features. Share functionality is not supported by Agoras for Discord.

Required Credentials
--------------------

Before using Agoras with Discord, you'll need to manually extract the following credentials from your Discord Application in the Discord Developer Portal. These credentials are required for bot authentication and server access.

- **Bot Token** (``DISCORD_BOT_TOKEN``): Your Discord bot's authentication token, obtained from the Discord Developer Portal
- **Server Name** (``DISCORD_SERVER_NAME``): The exact name of the Discord server where your bot is a member
- **Channel Name** (``DISCORD_CHANNEL_NAME``): The exact name of the text channel where you want to post (without the # symbol)

See :doc:`credentials/discord` for detailed instructions on how to create a Discord application, set up a bot, invite it to your server, and obtain these credentials.

For CI/CD environments, see :doc:`credentials/discord` for unattended execution setup.

Available Actions
~~~~~~~~~~~~~~~~~

* ``authorize`` - Set up bot authentication (required first step)
* ``post`` - Send text messages with links and images (up to 4 images)
* ``video`` - Upload and send video files
* ``delete`` - Delete messages

Authorization
-------------

.. versionadded:: 2.0
   Bot token "authorize first" workflow

Before performing any actions, you must authorize Agoras to access your Discord server::

    agoras discord authorize \
      --bot-token "${DISCORD_BOT_TOKEN}" \
      --server-name "${DISCORD_SERVER_NAME}" \
      --channel-name "${DISCORD_CHANNEL_NAME}"

This will:

1. Validate your bot token and server/channel access
2. Store encrypted credentials in ``~/.agoras/tokens/``

After authorization, you can perform actions without providing credentials. Credentials are automatically loaded from storage.

For CI/CD environments, see :doc:`credentials/discord` for unattended execution setup.

Publish a Discord message
-------------------------

This command will send a message to a Discord channel using your bot. The message can include text, links, and up to 4 images. Links will automatically generate rich embeds with previews when possible.

**New format** (Agoras 2.0+)::

    agoras discord post \
      --text "${STATUS_TEXT}" \
      --link "${STATUS_LINK}" \
      --image-1 "${STATUS_IMAGE_URL_1}" \
      --image-2 "${STATUS_IMAGE_URL_2}" \
      --image-3 "${STATUS_IMAGE_URL_3}" \
      --image-4 "${STATUS_IMAGE_URL_4}"

Parameters:

- ``--text``: The text content of your message
- ``--link``: A URL that will be embedded as a rich preview
- ``--image-X``: URLs pointing to downloadable images (JPEG, PNG, JPG)

**Note**: You must provide at least one of ``--text``, ``--link``, or ``--image-1``.

.. deprecated:: 2.0
   The ``agoras publish --network "discord"`` command is deprecated. Use ``agoras discord post`` instead.

Publish a Discord video
-----------------------

This command will upload and send a video file to a Discord channel. The video can include a title and description that will be displayed in a rich embed alongside the video file.

**New format** (Agoras 2.0+)::

    agoras discord video \
      --video-url "${DISCORD_VIDEO_URL}" \
      --video-title "${DISCORD_VIDEO_TITLE}" \
      --text "${STATUS_TEXT}"

Parameters:

- ``--video-url``: URL pointing to a downloadable video file (required)
- ``--video-title``: Title for the video (optional)
- ``--text``: Additional description text (optional)

**Video requirements**:
- **Supported formats**: MP4, MOV, WebM, AVI
- **File size limit**: 8MB for regular Discord users, 50MB for Nitro users
- **File must be accessible**: The URL must point to a downloadable video file

Delete a Discord message
------------------------

This command will delete an existing Discord message. The bot must have permission to delete messages and the message must be in the specified channel.

**New format** (Agoras 2.0+)::

    agoras discord delete \
      --post-id "${DISCORD_POST_ID}"

**Note**: Share functionality is not supported for Discord.

Post the last URL from an RSS feed into Discord
------------------------------------------------

This command will parse an RSS feed located at ``--feed-url``, and publish the last ``--max-count`` number of entries published in the last ``--post-lookback`` number of seconds. The post content will consist of the title and the link of the feed entry.

Please read about how the RSS feed should be structured in the :doc:`RSS feed section <rss>`. This ensures that the feed is correctly parsed and that the post content is properly formatted.

**New format** (Agoras 2.0+)::

    agoras utils feed-publish \
      --network discord \
      --mode last \
      --feed-url "${FEED_URL}" \
      --max-count "${MAX_COUNT}" \
      --post-lookback "${POST_LOOKBACK}"

Post a random URL from an RSS feed into Discord
------------------------------------------------

This command will parse an RSS feed at ``--feed-url`` and publish one random entry that's not older than ``--max-post-age``. The post content will consist of the title and the link of the feed entry.

Please read about how the RSS feed should be structured in the :doc:`RSS feed section <rss>`. This ensures that the feed is correctly parsed and that the post content is properly formatted.

**New format** (Agoras 2.0+)::

    agoras utils feed-publish \
      --network discord \
      --mode random \
      --feed-url "${FEED_URL}" \
      --max-post-age "${MAX_POST_AGE}"

Google Sheets Scheduling
------------------------

Agoras can schedule Discord messages using Google Sheets. This allows you to plan and automate message sending.

Run Scheduled Messages
~~~~~~~~~~~~~~~~~~~~~~

Process scheduled messages from a Google Sheet:

::

    agoras utils schedule-run \
      --network discord \
      --sheets-id "${GOOGLE_SHEETS_ID}" \
      --sheets-name "Discord" \
      --sheets-client-email "${GOOGLE_SHEETS_CLIENT_EMAIL}" \
      --sheets-private-key "${GOOGLE_SHEETS_PRIVATE_KEY}"

.. note::
   You must run ``agoras discord authorize`` first before using this command.

Sheet Format
~~~~~~~~~~~~

Your Google Sheet should have the following columns:

- ``status_text``: Message text content
- ``status_link``: URL to include in message
- ``status_image_url_1`` through ``status_image_url_4``: Image URLs (optional)
- ``date``: Scheduled date (format: DD-MM-YYYY)
- ``hour``: Scheduled hour (format: HH, 24-hour format)
- ``state``: Post state (``pending``, ``published``, ``error``)

**Example sheet row**:

::

    status_text,status_link,status_image_url_1,status_image_url_2,status_image_url_3,status_image_url_4,date,hour,state
    "This is a test Discord post","https://agoras.readthedocs.io/en/latest/","https://example.com/image1.jpg","https://example.com/image2.jpg","","","21-11-2022","17","pending"

Scheduling Logic
~~~~~~~~~~~~~~~~

- Posts with ``state="pending"`` and scheduled time in the past are processed
- Posts are created at the scheduled date and hour
- Sheet state is updated to ``published`` after successful posting
- If posting fails, state is updated to ``error``
- Use ``--network discord`` to process only Discord posts, or omit to process all networks

Discord Features and Limitations
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Rich Embeds**:
  - Links automatically generate rich previews with title, description, and images
  - Multiple embeds are supported for multiple images
  - Video uploads include custom embed with title and description

**File Upload Limits**:
  - **Regular users**: 8MB maximum file size
  - **Nitro users**: 50MB maximum file size
  - **Supported video formats**: MP4, MOV, WebM, AVI
  - **Supported image formats**: JPEG, PNG, JPG

**Bot Permissions Required**:
  - **Send Messages**: To post text content
  - **Embed Links**: To create rich embeds
  - **Attach Files**: To upload videos and images
  - **Manage Messages**: To delete messages (if using delete action)

**Limitations**:
  - Share/repost functionality is not supported
  - Bot must be invited to the server and have access to the target channel
  - Message content follows Discord's community guidelines and character limits
  - File URLs must be publicly accessible for download

Getting your message ID
~~~~~~~~~~~~~~~~~~~~~~~

**From Agoras output**:

When you create a Discord message with Agoras, it will print the message ID (in JSON format) in the console:

::

      $ agoras discord post \
            --text "This is a test post"
      $ {"id":"NNNNNNNNNNN"}

``NNNNNNNNNNN`` is the message ID.

**From Discord client**:

1. Enable Developer Mode in Discord (User Settings → Advanced → Developer Mode)
2. Right-click on any message
3. Select "Copy Message ID"
4. The copied value is the message ID you can use with ``--post-id``

Server and Channel Names
~~~~~~~~~~~~~~~~~~~~~~~~

**Server Name** (``--server-name``):
  - Use the exact server name as it appears in Discord
  - Case-sensitive
  - Must be a server where your bot is a member

**Channel Name** (``--channel-name``):
  - Use the channel name without the # symbol
  - Case-sensitive
  - Bot must have access to read and send messages in this channel

For example, if you see "#general" in Discord, use ``general`` as the channel name.
