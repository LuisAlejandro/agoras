Usage for Discord
================

.. note::
   **New in version 2.0**: Discord commands now use the intuitive ``agoras discord`` format.
   See the :doc:`migration guide <migration>` for upgrading from ``agoras publish``.

Discord is a communication platform designed for creating communities. It features text channels, voice channels, and rich media sharing capabilities. Agoras can publish messages, videos, images, and manage scheduled content on Discord using the official `Discord.py library <https://discordpy.readthedocs.io/>`_.

**Important**: Discord uses bot tokens for authentication. You must create a Discord application and bot, then invite it to your server with appropriate permissions before using these features. Share functionality is not supported by Agoras for Discord.

For CI/CD environments, see :doc:`credentials/discord` for unattended execution setup.

Actions
~~~~~~~

Publish a Discord message
------------------------

This command will send a message to a Discord channel using your bot. The message can include text, links, and up to 4 images. Links will automatically generate rich embeds with previews when possible.

**New format** (Agoras 2.0+)::

    agoras discord post \
      --bot-token "${DISCORD_BOT_TOKEN}" \
      --server-name "${DISCORD_SERVER_NAME}" \
      --channel-name "${DISCORD_CHANNEL_NAME}" \
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
----------------------

This command will upload and send a video file to a Discord channel. The video can include a title and description that will be displayed in a rich embed alongside the video file.

**New format** (Agoras 2.0+)::

    agoras discord video \
      --bot-token "${DISCORD_BOT_TOKEN}" \
      --server-name "${DISCORD_SERVER_NAME}" \
      --channel-name "${DISCORD_CHANNEL_NAME}" \
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

Like a Discord message
---------------------

This command will add a heart reaction (❤️) to an existing Discord message. You need the message ID to perform this action.

**New format** (Agoras 2.0+)::

    agoras discord like \
      --bot-token "${DISCORD_BOT_TOKEN}" \
      --server-name "${DISCORD_SERVER_NAME}" \
      --channel-name "${DISCORD_CHANNEL_NAME}" \
      --post-id "${DISCORD_POST_ID}"

Delete a Discord message
-----------------------

This command will delete an existing Discord message. The bot must have permission to delete messages and the message must be in the specified channel.

**New format** (Agoras 2.0+)::

    agoras discord delete \
      --bot-token "${DISCORD_BOT_TOKEN}" \
      --server-name "${DISCORD_SERVER_NAME}" \
      --channel-name "${DISCORD_CHANNEL_NAME}" \
      --post-id "${DISCORD_POST_ID}"

**Note**: Share functionality is not supported for Discord.

Post the last content from an RSS feed into Discord
---------------------------------------------------

This command will parse an RSS feed located at ``--feed-url``, and publish the last ``--max-count`` number of entries published in the last ``--post-lookback`` number of seconds. The message content will consist of the title and link of the feed entry. If the feed entry has media enclosures, the first image will be included.

Please read about how the RSS feed should be structured in the :doc:`RSS feed section <rss>`. This ensures that the feed is correctly parsed and that the post content is properly formatted.

**New format** (Agoras 2.0+)::

    agoras utils feed-publish \
      --network discord \
      --mode last \
      --feed-url "${FEED_URL}" \
      --max-count "${MAX_COUNT}" \
      --post-lookback "${POST_LOOKBACK}" \
      --discord-bot-token "${DISCORD_BOT_TOKEN}" \
      --discord-server-name "${DISCORD_SERVER_NAME}" \
      --discord-channel-name "${DISCORD_CHANNEL_NAME}"

Post a random content from an RSS feed into Discord
---------------------------------------------------

This command will parse an RSS feed at ``--feed-url`` and publish one random entry that's not older than ``--max-post-age`` days. The message content will consist of the title and link of the feed entry. If the feed entry has media enclosures, the first image will be included.

Please read about how the RSS feed should be structured in the :doc:`RSS feed section <rss>`. This ensures that the feed is correctly parsed and that the post content is properly formatted.

**New format** (Agoras 2.0+)::

    agoras utils feed-publish \
      --network discord \
      --mode random \
      --feed-url "${FEED_URL}" \
      --max-post-age "${MAX_POST_AGE}" \
      --discord-bot-token "${DISCORD_BOT_TOKEN}" \
      --discord-server-name "${DISCORD_SERVER_NAME}" \
      --discord-channel-name "${DISCORD_CHANNEL_NAME}"

Schedule a Discord post
-----------------------

This command will scan a sheet ``--sheets-name`` of a Google spreadsheet with id ``--sheets-id``, that's authorized by ``--sheets-client-email`` and ``--sheets-private-key``. Messages will be published to the Discord channel using your bot.

The order of the columns of the spreadsheet is crucial to the correct functioning of the command. Here's how the information should be organized:

+-------------+------------+------------+------------+------------+------------+-------------------------+-------------------+------------------------------+
| ``--text``  | ``--link`` | ``--image-1`` | ``--image-2`` | ``--image-3`` | ``--image-4`` | date (%d-%m-%Y format)  | time (%H format)  | status (draft or published)  |
+-------------+------------+------------+------------+------------+------------+-------------------------+-------------------+------------------------------+

As you can see, the first 6 columns correspond to the parameters of the "post" command, the date and time columns correspond to the specific time that you want to publish this message, and the status column tells the script if this message is ready to be published (draft status) or if it was already published and should be skipped (published status).

Example of a working schedule:

+-------------------------------+-------------------------------------------+---------------------------------------------------------+---------------------------------------------------------+---------------------------------------------------------+---------------------------------------------------------+-------------+-----+--------+
| This is a test Discord post   | https://agoras.readthedocs.io/en/latest/  | https://example.com/image1.jpg                         | https://example.com/image2.jpg                         |                                                         |                                                         | 21-11-2022  | 17  | draft  |
+-------------------------------+-------------------------------------------+---------------------------------------------------------+---------------------------------------------------------+---------------------------------------------------------+---------------------------------------------------------+-------------+-----+--------+

This schedule entry would be published at 17:00h of 21-11-2022 with text "This is a test Discord post", a link, and 2 images.

For this command to work, it should be executed hourly by a cron script.

**New format** (Agoras 2.0+)::

    agoras utils schedule-run \
      --network discord \
      --sheets-id "${GOOGLE_SHEETS_ID}" \
      --sheets-name "${GOOGLE_SHEETS_NAME}" \
      --sheets-client-email "${GOOGLE_SHEETS_CLIENT_EMAIL}" \
      --sheets-private-key "${GOOGLE_SHEETS_PRIVATE_KEY}" \
      --discord-bot-token "${DISCORD_BOT_TOKEN}" \
      --discord-server-name "${DISCORD_SERVER_NAME}" \
      --discord-channel-name "${DISCORD_CHANNEL_NAME}"

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
  - **Add Reactions**: To like messages (add reactions)
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
            --bot-token XXXXX \
            --server-name "My Server" \
            --channel-name "general" \
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
