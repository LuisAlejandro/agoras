Usage for Telegram
==================

.. note::
   **New in version 2.0**: Telegram commands now use the intuitive ``agoras telegram`` format.
   See the :doc:`migration guide <migration>` for upgrading from ``agoras publish``.

Telegram is a cloud-based instant messaging and voice-over-IP service. Agoras can publish messages, videos, images, and manage scheduled content on Telegram using the official `python-telegram-bot library <https://python-telegram-bot.org/>`_.

**Important**: Telegram uses bot tokens for authentication. You must create a Telegram bot using @BotFather, obtain a bot token, and find the chat ID (user, group, or channel) before using these features. Like and share functionality are not supported by Agoras for Telegram.

Required Credentials
--------------------

Before using Agoras with Telegram, you'll need to manually extract the following credentials. These credentials are required for bot authentication and chat access.

- **Bot Token** (``TELEGRAM_BOT_TOKEN``): Your Telegram bot's authentication token, obtained from @BotFather
- **Chat ID** (``TELEGRAM_CHAT_ID``): The unique identifier for the chat (user, group, or channel) where you want to send messages

See :doc:`credentials/telegram` for detailed instructions on how to create a Telegram bot using @BotFather, obtain the bot token, and find your chat ID.

For CI/CD environments, see :doc:`credentials/telegram` for unattended execution setup.

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

Before performing any actions, you must authorize Agoras to access your Telegram chat::

    agoras telegram authorize \
      --bot-token "${TELEGRAM_BOT_TOKEN}" \
      --chat-id "${TELEGRAM_CHAT_ID}"

This will:

1. Validate your bot token and chat access
2. Store encrypted credentials in ``~/.agoras/tokens/``

After authorization, you can perform actions without providing credentials. Credentials are automatically loaded from storage.

For CI/CD environments, see :doc:`credentials/telegram` for unattended execution setup.

Publish a Telegram message
---------------------------

This command will send a message to a Telegram chat using your bot. The message can include text, links, and up to 4 images. Multiple images will be sent as a media group (album).

**New format** (Agoras 2.0+)::

    agoras telegram post \
      --text "${STATUS_TEXT}" \
      --link "${STATUS_LINK}" \
      --image-1 "${STATUS_IMAGE_URL_1}" \
      --image-2 "${STATUS_IMAGE_URL_2}" \
      --image-3 "${STATUS_IMAGE_URL_3}" \
      --image-4 "${STATUS_IMAGE_URL_4}"

Parameters:

- ``--bot-token``: Your Telegram bot token from @BotFather (optional if already authorized)
- ``--chat-id``: Target chat ID (user, group, or channel) (optional if already authorized)
- ``--text``: The text content of your message
- ``--link``: A URL to include in the message
- ``--image-X``: URLs pointing to downloadable images (JPEG, PNG, JPG)

**Note**: You must provide at least one of ``--text``, ``--link``, or ``--image-1``.

.. deprecated:: 2.0
   The ``agoras publish --network "telegram"`` command is deprecated. Use ``agoras telegram post`` instead.

Publish a Telegram video
-------------------------

This command will upload and send a video file to a Telegram chat. The video can include a caption.

**New format** (Agoras 2.0+)::

    agoras telegram video \
      --video-url "${VIDEO_URL}" \
      --video-title "${VIDEO_TITLE}" \
      --text "${STATUS_TEXT}"

Parameters:

- ``--bot-token``: Your Telegram bot token from @BotFather (optional if already authorized)
- ``--chat-id``: Target chat ID (user, group, or channel) (optional if already authorized)
- ``--video-url``: URL pointing to a downloadable video file (required)
- ``--video-title``: Title for the video (optional, used as caption if text not provided)
- ``--text``: Caption text for the video (optional)

**Video requirements**:
- **Supported formats**: MP4, MOV, WebM, AVI, MKV
- **File size limit**: 50MB for regular bots
- **File must be accessible**: The URL must point to a downloadable video file

Delete a Telegram message
--------------------------

This command will delete an existing Telegram message. The bot must have permission to delete messages in the chat.

**New format** (Agoras 2.0+)::

    agoras telegram delete \
      --post-id "${TELEGRAM_MESSAGE_ID}"

Parameters:

- ``--bot-token``: Your Telegram bot token from @BotFather (optional if already authorized)
- ``--chat-id``: Target chat ID (user, group, or channel) (optional if already authorized)
- ``--post-id``: ID of the message to delete (required)

**Note**: Like and share functionality are not supported for Telegram.

Post the last URL from an RSS feed into Telegram
-------------------------------------------------

This command will parse an RSS feed located at ``--feed-url``, and publish the last ``--max-count`` number of entries published in the last ``--post-lookback`` number of seconds. The post content will consist of the title and the link of the feed entry.

Please read about how the RSS feed should be structured in the :doc:`RSS feed section <rss>`. This ensures that the feed is correctly parsed and that the post content is properly formatted.

**New format** (Agoras 2.0+)::

    agoras utils feed-publish \
      --network telegram \
      --mode last \
      --feed-url "${FEED_URL}" \
      --max-count "${MAX_COUNT}" \
      --post-lookback "${POST_LOOKBACK}"

Post a random URL from an RSS feed into Telegram
--------------------------------------------------

This command will parse an RSS feed at ``--feed-url`` and publish one random entry that's not older than ``--max-post-age``. The post content will consist of the title and the link of the feed entry.

Please read about how the RSS feed should be structured in the :doc:`RSS feed section <rss>`. This ensures that the feed is correctly parsed and that the post content is properly formatted.

**New format** (Agoras 2.0+)::

    agoras utils feed-publish \
      --network telegram \
      --mode random \
      --feed-url "${FEED_URL}" \
      --max-post-age "${MAX_POST_AGE}"

Google Sheets Scheduling
------------------------

Agoras can schedule Telegram messages using Google Sheets. This allows you to plan and automate message sending.

Run Scheduled Messages
~~~~~~~~~~~~~~~~~~~~~~

Process scheduled messages from a Google Sheet:

::

    agoras utils schedule-run \
      --network telegram \
      --sheets-id "${GOOGLE_SHEETS_ID}" \
      --sheets-name "Telegram" \
      --sheets-client-email "${GOOGLE_SHEETS_CLIENT_EMAIL}" \
      --sheets-private-key "${GOOGLE_SHEETS_PRIVATE_KEY}"

.. note::
   You must run ``agoras telegram authorize`` first before using this command.

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
    "This is a test Telegram post","https://agoras.readthedocs.io/en/latest/","https://example.com/image1.jpg","https://example.com/image2.jpg","","","21-11-2022","17","pending"

Scheduling Logic
~~~~~~~~~~~~~~~~

- Posts with ``state="pending"`` and scheduled time in the past are processed
- Posts are created at the scheduled date and hour
- Sheet state is updated to ``published`` after successful posting
- If posting fails, state is updated to ``error``
- Use ``--network telegram`` to process only Telegram posts, or omit to process all networks

Telegram Features and Limitations
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Message Formatting**:
  - Supports HTML, Markdown, and MarkdownV2 parse modes
  - Rich text formatting (bold, italic, links, code blocks)
  - Default parse mode is HTML

**Media Groups**:
  - Multiple images can be sent as an album (media group)
  - Up to 10 items per media group
  - All items must be the same type (all photos or all videos)
  - Caption only on first item

**File Upload Limits**:
  - **Maximum file size**: 50MB for all file types
  - **Supported video formats**: MP4, MOV, WebM, AVI, MKV
  - **Supported image formats**: JPEG, PNG, JPG, GIF

**Bot Permissions Required**:
  - **Send Messages**: To post text content (required for all actions)
  - **Send Media**: To upload photos and videos (required for media actions)
  - **Delete Messages**: To delete messages (required for delete action)

**Chat Types**:
  - **Private chats**: Direct messages to users
  - **Groups**: Up to 200,000 members
  - **Channels**: Unlimited subscribers
  - **Supergroups**: Advanced features and unlimited members

**Limitations**:
  - Like/reaction functionality is not supported
  - Share/repost functionality is not supported
  - Bot must be added to groups/channels and have appropriate permissions
  - File URLs must be publicly accessible for download
  - Rate limiting: 30 messages/second to different chats, 1 message/second to same chat

Getting your message ID
~~~~~~~~~~~~~~~~~~~~~~~

**From Agoras output**:

When you create a Telegram message with Agoras, it will print the message ID (in JSON format) in the console:

::

      $ agoras telegram post \
            --text "This is a test post"
      $ {"id":"123456789"}

``123456789`` is the message ID.

**From Telegram client**:

1. Forward a message from the chat to @userinfobot or @getidsbot
2. The bot will reply with the chat ID and message ID
3. Use the message ID with ``--post-id``

Chat ID Discovery
~~~~~~~~~~~~~~~~~~

**For Private Chats**:
  - Start a conversation with @userinfobot
  - The bot will reply with your user ID
  - Use this ID as ``--chat-id``

**For Groups**:
  - Add @getidsbot to your group
  - Send any message in the group
  - The bot will reply with the group ID
  - Use this ID as ``--chat-id``

**For Channels**:
  - Add @getidsbot to your channel as an administrator
  - Post any message in the channel
  - The bot will reply with the channel ID
  - Use this ID as ``--chat-id``

**Note**: Channel IDs start with ``-100``, group IDs start with ``-``, and user IDs are positive numbers.

Parse Modes
~~~~~~~~~~~

Telegram supports three parse modes for message formatting:

- **HTML**: Use HTML tags for formatting (default)
  - Example: ``<b>bold</b>``, ``<i>italic</i>``, ``<a href="url">link</a>``
- **Markdown**: Use Markdown syntax
  - Example: ``*bold*``, ``_italic_``, ``[link](url)``
- **MarkdownV2**: Enhanced Markdown with more features
  - Example: ``*bold*``, ``_italic_``, ``[link](url)``

Set the parse mode using ``--parse-mode`` parameter (default: HTML).
