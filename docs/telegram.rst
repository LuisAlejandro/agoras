Usage for Telegram
==================

Telegram is a cloud-based instant messaging and voice-over-IP service. Agoras can publish messages, videos, images, documents, audio files, polls, and manage scheduled content on Telegram using the official `python-telegram-bot library <https://python-telegram-bot.org/>`_.

**Important**: Telegram uses bot tokens for authentication. You must create a Telegram bot using @BotFather, obtain a bot token, and find the chat ID (user, group, or channel) before using these features. Like and share functionality are not supported by Agoras for Telegram.

Actions
~~~~~~~

Publish a Telegram message
---------------------------

This command will send a message to a Telegram chat using your bot. The message can include text, links, and up to 4 images. Multiple images will be sent as a media group (album).

::

      agoras publish \
            --network "telegram" \
            --action "post" \
            --telegram-bot-token "${TELEGRAM_BOT_TOKEN}" \
            --telegram-chat-id "${TELEGRAM_CHAT_ID}" \
            --status-text "${STATUS_TEXT}" \
            --status-link "${STATUS_LINK}" \
            --status-image-url-1 "${STATUS_IMAGE_URL_1}" \
            --status-image-url-2 "${STATUS_IMAGE_URL_2}" \
            --status-image-url-3 "${STATUS_IMAGE_URL_3}" \
            --status-image-url-4 "${STATUS_IMAGE_URL_4}"

Parameters:

- ``--telegram-bot-token``: Your Telegram bot token from @BotFather (required)
- ``--telegram-chat-id``: Target chat ID (user, group, or channel) (required)
- ``--status-text``: The text content of your message
- ``--status-link``: A URL to include in the message
- ``--status-image-url-X``: URLs pointing to downloadable images (JPEG, PNG, JPG)

**Note**: You must provide at least one of ``--status-text``, ``--status-link``, or ``--status-image-url-1``.

Publish a Telegram video
-------------------------

This command will upload and send a video file to a Telegram chat. The video can include a caption.

::

      agoras publish \
            --network "telegram" \
            --action "video" \
            --telegram-bot-token "${TELEGRAM_BOT_TOKEN}" \
            --telegram-chat-id "${TELEGRAM_CHAT_ID}" \
            --video-url "${VIDEO_URL}" \
            --video-title "${VIDEO_TITLE}" \
            --status-text "${STATUS_TEXT}"

Parameters:

- ``--video-url``: URL pointing to a downloadable video file (required)
- ``--video-title``: Title for the video (optional, used as caption if status-text not provided)
- ``--status-text``: Caption text for the video (optional)

**Video requirements**:
- **Supported formats**: MP4, MOV, WebM, AVI, MKV
- **File size limit**: 50MB for regular bots
- **File must be accessible**: The URL must point to a downloadable video file

Edit a Telegram message
-----------------------

This command will edit the text of an existing Telegram message. Only text messages can be edited (not media messages).

::

      agoras publish \
            --network "telegram" \
            --action "edit" \
            --telegram-bot-token "${TELEGRAM_BOT_TOKEN}" \
            --telegram-chat-id "${TELEGRAM_CHAT_ID}" \
            --telegram-message-id "${TELEGRAM_MESSAGE_ID}" \
            --status-text "${NEW_TEXT}"

Parameters:

- ``--telegram-message-id``: ID of the message to edit (required)
- ``--status-text``: New message text (required)

**Note**: You can only edit text messages. Media messages (photos, videos, documents) cannot be edited.

Send a Telegram poll
---------------------

This command will create and send a poll to a Telegram chat. Polls can be anonymous or public, and support 2-10 options.

::

      agoras publish \
            --network "telegram" \
            --action "poll" \
            --telegram-bot-token "${TELEGRAM_BOT_TOKEN}" \
            --telegram-chat-id "${TELEGRAM_CHAT_ID}" \
            --telegram-poll-question "${POLL_QUESTION}" \
            --telegram-poll-options "${POLL_OPTIONS}" \
            --telegram-poll-anonymous "${IS_ANONYMOUS}"

Parameters:

- ``--telegram-poll-question``: Poll question (up to 300 characters) (required)
- ``--telegram-poll-options``: Comma-separated list of poll options (2-10 options, each up to 100 characters) (required)
- ``--telegram-poll-anonymous``: Whether poll is anonymous (true/false, default: true)

**Poll requirements**:
- **Question length**: Up to 300 characters
- **Options**: 2-10 options required
- **Option length**: Each option up to 100 characters
- **Example options**: "Red,Blue,Green,Yellow"

Send a Telegram document
--------------------------

This command will send a document file to a Telegram chat. Documents can include PDFs, Word documents, spreadsheets, and other file types.

::

      agoras publish \
            --network "telegram" \
            --action "document" \
            --telegram-bot-token "${TELEGRAM_BOT_TOKEN}" \
            --telegram-chat-id "${TELEGRAM_CHAT_ID}" \
            --telegram-document-url "${DOCUMENT_URL}" \
            --status-text "${CAPTION}"

Parameters:

- ``--telegram-document-url``: URL of document file to send (required)
- ``--status-text``: Document caption (optional, up to 1024 characters)

**Document requirements**:
- **File size limit**: 50MB
- **Supported formats**: PDF, DOCX, XLSX, PPTX, ZIP, and other file types
- **File must be accessible**: The URL must point to a downloadable file

Send a Telegram audio file
---------------------------

This command will send an audio file to a Telegram chat. Audio files can include MP3, OGG, and other audio formats.

::

      agoras publish \
            --network "telegram" \
            --action "audio" \
            --telegram-bot-token "${TELEGRAM_BOT_TOKEN}" \
            --telegram-chat-id "${TELEGRAM_CHAT_ID}" \
            --telegram-audio-url "${AUDIO_URL}" \
            --status-text "${CAPTION}" \
            --telegram-audio-duration "${DURATION}" \
            --telegram-audio-performer "${PERFORMER}" \
            --telegram-audio-title "${TITLE}"

Parameters:

- ``--telegram-audio-url``: URL of audio file to send (required)
- ``--status-text``: Audio caption (optional, up to 1024 characters)
- ``--telegram-audio-duration``: Audio duration in seconds (optional)
- ``--telegram-audio-performer``: Performer name (optional)
- ``--telegram-audio-title``: Track title (optional)

**Audio requirements**:
- **File size limit**: 50MB
- **Supported formats**: MP3, OGG, WAV, M4A
- **File must be accessible**: The URL must point to a downloadable audio file

Delete a Telegram message
--------------------------

This command will delete an existing Telegram message. The bot must have permission to delete messages in the chat.

::

      agoras publish \
            --network "telegram" \
            --action "delete" \
            --telegram-bot-token "${TELEGRAM_BOT_TOKEN}" \
            --telegram-chat-id "${TELEGRAM_CHAT_ID}" \
            --telegram-message-id "${TELEGRAM_MESSAGE_ID}"

Parameters:

- ``--telegram-message-id``: ID of the message to delete (required)

**Note**: Like and share functionality are not supported for Telegram.

Post the last content from an RSS feed into Telegram
-----------------------------------------------------

This command will parse an RSS feed located at ``--feed-url``, and publish the last ``--max-count`` number of entries published in the last ``--post-lookback`` number of seconds. The message content will consist of the title and link of the feed entry. If the feed entry has media enclosures, the first image will be included.

Please read about how the RSS feed should be structured in the :doc:`RSS feed section <rss>`. This ensures that the feed is correctly parsed and that the post content is properly formatted.

::

      agoras publish \
            --network "telegram" \
            --action "last-from-feed" \
            --telegram-bot-token "${TELEGRAM_BOT_TOKEN}" \
            --telegram-chat-id "${TELEGRAM_CHAT_ID}" \
            --feed-url "${FEED_URL}" \
            --max-count "${MAX_COUNT}" \
            --post-lookback "${POST_LOOKBACK}"

Post a random content from an RSS feed into Telegram
-----------------------------------------------------

This command will parse an RSS feed at ``--feed-url`` and publish one random entry that's not older than ``--max-post-age`` days. The message content will consist of the title and link of the feed entry. If the feed entry has media enclosures, the first image will be included.

Please read about how the RSS feed should be structured in the :doc:`RSS feed section <rss>`. This ensures that the feed is correctly parsed and that the post content is properly formatted.

::

      agoras publish \
            --network "telegram" \
            --action "random-from-feed" \
            --telegram-bot-token "${TELEGRAM_BOT_TOKEN}" \
            --telegram-chat-id "${TELEGRAM_CHAT_ID}" \
            --feed-url "${FEED_URL}" \
            --max-post-age "${MAX_POST_AGE}"

Schedule a Telegram post
-------------------------

This command will scan a sheet ``--google-sheets-name`` of a Google spreadsheet with id ``--google-sheets-id``, that's authorized by ``--google-sheets-client-email`` and ``--google-sheets-private-key``. Messages will be published to the Telegram chat using your bot.

The order of the columns of the spreadsheet is crucial to the correct functioning of the command. Here's how the information should be organized:

+--------------------+--------------------+---------------------------+---------------------------+---------------------------+---------------------------+-------------------------+-------------------+------------------------------+
| ``--status-text``  | ``--status-link``  | ``--status-image-url-1``  | ``--status-image-url-2``  | ``--status-image-url-3``  | ``--status-image-url-4``  | date (%d-%m-%Y format)  | time (%H format)  | status (draft or published)  |
+--------------------+--------------------+---------------------------+---------------------------+---------------------------+---------------------------+-------------------------+-------------------+------------------------------+

As you can see, the first 6 columns correspond to the parameters of the "post" command, the date and time columns correspond to the specific time that you want to publish this message, and the status column tells the script if this message is ready to be published (draft status) or if it was already published and should be skipped (published status).

Example of a working schedule:

+-------------------------------+-------------------------------------------+---------------------------------------------------------+---------------------------------------------------------+---------------------------------------------------------+---------------------------------------------------------+-------------+-----+--------+
| This is a test Telegram post | https://agoras.readthedocs.io/en/latest/  | https://example.com/image1.jpg                         | https://example.com/image2.jpg                         |                                                         |                                                         | 21-11-2022  | 17  | draft  |
+-------------------------------+-------------------------------------------+---------------------------------------------------------+---------------------------------------------------------+---------------------------------------------------------+---------------------------------------------------------+-------------+-----+--------+

This schedule entry would be published at 17:00h of 21-11-2022 with text "This is a test Telegram post", a link, and 2 images.

For this command to work, it should be executed hourly by a cron script.

::

      agoras publish \
            --network "telegram" \
            --action "schedule" \
            --telegram-bot-token "${TELEGRAM_BOT_TOKEN}" \
            --telegram-chat-id "${TELEGRAM_CHAT_ID}" \
            --google-sheets-id "${GOOGLE_SHEETS_ID}" \
            --google-sheets-name "${GOOGLE_SHEETS_NAME}" \
            --google-sheets-client-email "${GOOGLE_SHEETS_CLIENT_EMAIL}" \
            --google-sheets-private-key "${GOOGLE_SHEETS_PRIVATE_KEY}"

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
  - **Supported audio formats**: MP3, OGG, WAV, M4A
  - **Supported document formats**: PDF, DOCX, XLSX, PPTX, ZIP, and more

**Bot Permissions Required**:
  - **Send Messages**: To post text content (required for all actions)
  - **Send Media**: To upload photos, videos, documents, audio (required for media actions)
  - **Delete Messages**: To delete messages (required for delete action)
  - **Send Polls**: To create polls (required for poll action)

**Chat Types**:
  - **Private chats**: Direct messages to users
  - **Groups**: Up to 200,000 members
  - **Channels**: Unlimited subscribers
  - **Supergroups**: Advanced features and unlimited members

**Limitations**:
  - Like/reaction functionality is not supported
  - Share/repost functionality is not supported
  - Message editing only works for text messages (not media)
  - Bot must be added to groups/channels and have appropriate permissions
  - File URLs must be publicly accessible for download
  - Rate limiting: 30 messages/second to different chats, 1 message/second to same chat

Getting your message ID
~~~~~~~~~~~~~~~~~~~~~~~

**From Agoras output**:

When you create a Telegram message with Agoras, it will print the message ID (in JSON format) in the console:

::

      $ agoras publish \
            --network telegram \
            --action post \
            --telegram-bot-token XXXXX \
            --telegram-chat-id YYYYY \
            --status-text "This is a test post"
      $ {"id":"123456789"}

``123456789`` is the message ID.

**From Telegram client**:

1. Forward a message from the chat to @userinfobot or @getidsbot
2. The bot will reply with the chat ID and message ID
3. Use the message ID with ``--telegram-message-id``

Chat ID Discovery
~~~~~~~~~~~~~~~~~~

**For Private Chats**:
  - Start a conversation with @userinfobot
  - The bot will reply with your user ID
  - Use this ID as ``--telegram-chat-id``

**For Groups**:
  - Add @getidsbot to your group
  - Send any message in the group
  - The bot will reply with the group ID
  - Use this ID as ``--telegram-chat-id``

**For Channels**:
  - Add @getidsbot to your channel as an administrator
  - Post any message in the channel
  - The bot will reply with the channel ID
  - Use this ID as ``--telegram-chat-id``

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
