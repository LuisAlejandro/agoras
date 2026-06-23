Usage for WhatsApp
==================

.. note::

   Agoras uses ``agoras whatsapp`` for WhatsApp Business API operations.
   See the :doc:`migration guide <migration/index>` for upgrading from ``agoras publish``.

WhatsApp Business API is Meta's official API for sending messages via WhatsApp. Agoras can send text messages, images, videos, and template messages to WhatsApp recipients using the official `Meta Graph API <https://developers.facebook.com/docs/graph-api>`_.

**Important**: WhatsApp Business API requires a Meta Developer Account, WhatsApp Business Account, and phone number verification. For production use, business verification is required. You must specify a recipient phone number in E.164 format for all message sending operations. Like, share, and delete functionality are not supported by Agoras for WhatsApp.

Required Credentials
--------------------

Before using Agoras with WhatsApp, you'll need to manually extract the following credentials from your Meta Developer Account and WhatsApp Business Account. These credentials are required for API authentication and message sending.

- **Access Token** (``WHATSAPP_ACCESS_TOKEN``): Meta Graph API access token for WhatsApp Business API, obtained from your Meta app dashboard
- **Phone Number ID** (``WHATSAPP_PHONE_NUMBER_ID``): The unique identifier for your registered WhatsApp Business phone number
- **Recipient** (``WHATSAPP_RECIPIENT``): The target recipient phone number in E.164 format (e.g., +1234567890) - required for each message
- **Business Account ID** (``WHATSAPP_BUSINESS_ACCOUNT_ID``): Optional identifier for your WhatsApp Business Account, required for some advanced features

See :doc:`credentials/whatsapp` for detailed instructions on how to set up a Meta Developer Account, create a WhatsApp Business Account, register a phone number, and obtain these credentials.

For CI/CD environments, see :doc:`credentials/whatsapp` for unattended execution setup.

Available Actions
~~~~~~~~~~~~~~~~~

* ``authorize`` - Set up API authentication (required first step)
* ``post`` - Send text messages with links and images (up to 4 images)
* ``video`` - Send video messages
* ``template`` - Send pre-approved template messages

Authorization
-------------

.. versionadded:: 2.0
   Access token "authorize first" workflow

Before performing any actions, you must authorize Agoras to access your WhatsApp Business API::

    agoras whatsapp authorize \
      --access-token "${WHATSAPP_ACCESS_TOKEN}" \
      --phone-number-id "${WHATSAPP_PHONE_NUMBER_ID}"

This will:

1. Validate your access token and phone number ID
2. Store encrypted credentials in ``~/.agoras/tokens/``

After authorization, you can perform actions without providing access token and phone number ID. The recipient phone number must still be provided with each message.

For CI/CD environments, see :doc:`credentials/whatsapp` for unattended execution setup.

Send a WhatsApp text message
-----------------------------

This command will send a text message to a WhatsApp recipient. The message can include text and a link.

::

    agoras whatsapp post \
      --recipient "${WHATSAPP_RECIPIENT}" \
      --text "Hello from Agoras!" \
      --link "https://example.com"

Parameters:

- ``--recipient``: Target recipient phone number in E.164 format, e.g., +1234567890 (required)
- ``--access-token``: Meta Graph API access token (optional if already authorized)
- ``--phone-number-id``: WhatsApp Business phone number ID (optional if already authorized)
- ``--text``: The text content of your message (optional)
- ``--link``: A URL to include in the message (optional)

**Note**: You must provide at least ``--text``, ``--link``, or an image (``--image-1`` through ``--image-4``). The recipient phone number must be in E.164 format (starts with +, includes country code).

Send a WhatsApp message with image
-----------------------------------

This command will send an image message to a WhatsApp recipient. The image can include a caption.

::

    agoras whatsapp post \
      --recipient "${WHATSAPP_RECIPIENT}" \
      --text "Check this out!" \
      --link "https://example.com" \
      --image-1 "https://example.com/image.jpg"

Parameters:

- ``--recipient``: Target recipient phone number in E.164 format (required)
- ``--access-token``: Meta Graph API access token (optional if already authorized)
- ``--phone-number-id``: WhatsApp Business phone number ID (optional if already authorized)
- ``--image-1`` through ``--image-4``: URLs pointing to publicly accessible images (JPEG, PNG, GIF)
- ``--text``: Caption text for the image (optional)
- ``--link``: A URL to include in the message (optional)

**Image requirements**:
- **Supported formats**: JPEG, PNG, GIF
- **Max size**: 5MB per image
- **URL must be publicly accessible**: Images must be hosted on HTTPS URLs
- **Multiple images**: If multiple images are provided, they are sent sequentially (not as a group)

**Note**: WhatsApp downloads images from the provided URLs. The URLs must be publicly accessible via HTTPS.

Send a WhatsApp video message
------------------------------

This command will send a video message to a WhatsApp recipient. The video can include a caption.

::

    agoras whatsapp video \
      --recipient "${WHATSAPP_RECIPIENT}" \
      --video-url "https://example.com/video.mp4" \
      --video-title "My Video" \
      --text "Check out this video!"

Parameters:

- ``--recipient``: Target recipient phone number in E.164 format (required)
- ``--video-url``: URL pointing to a publicly accessible video file (required)
- ``--access-token``: Meta Graph API access token (optional if already authorized)
- ``--phone-number-id``: WhatsApp Business phone number ID (optional if already authorized)
- ``--video-title``: Title for the video (optional, not used by WhatsApp but kept for compatibility)
- ``--text``: Caption text for the video (optional)

**Video requirements**:
- **Supported formats**: MP4, 3GP
- **Max size**: 16MB
- **URL must be publicly accessible**: Videos must be hosted on HTTPS URLs
- **Codec**: H.264 video codec recommended

**Note**: WhatsApp downloads videos from the provided URLs. The URLs must be publicly accessible via HTTPS.

Send a WhatsApp template message
--------------------------------

This command will send a pre-approved template message to a WhatsApp recipient. Template messages are required for sending messages outside the 24-hour messaging window.

::

    agoras whatsapp template \
      --recipient "${WHATSAPP_RECIPIENT}" \
      --template-name "hello_world" \
      --language-code "en"

Parameters:

- ``--recipient``: Target recipient phone number in E.164 format (required)
- ``--template-name``: Name of the pre-approved template (required)
- ``--access-token``: Meta Graph API access token (optional if already authorized)
- ``--phone-number-id``: WhatsApp Business phone number ID (optional if already authorized)
- ``--language-code``: Language code in ISO 639-1 format, e.g., "en", "es", "fr" (default: "en")
- ``--template-components``: Template components as JSON string (optional, for parameters, buttons, etc.)

**Template requirements**:
- Templates must be pre-approved by Meta before use
- Template approval can take several days
- Templates are used for notifications and marketing messages
- Language code must match an approved template language
- Template components can include parameters, buttons, and other interactive elements

**Note**: Template messages are required when sending to recipients who haven't messaged you in the last 24 hours. For recipients within the 24-hour window, you can use regular text messages.

Post the last URL from an RSS feed into WhatsApp
-------------------------------------------------

This command will parse an RSS feed located at ``--feed-url``, and publish the last ``--max-count`` number of entries published in the last ``--post-lookback`` number of seconds. The post content will consist of the title and the link of the feed entry.

.. note::
   You must run ``agoras whatsapp authorize`` first before using this command.

Please read about how the RSS feed should be structured in the :doc:`RSS feed section <rss>`. This ensures that the feed is correctly parsed and that the post content is properly formatted.
::

    agoras utils feed-publish \
      --network whatsapp \
      --mode last \
      --feed-url "${FEED_URL}" \
      --max-count "${MAX_COUNT}" \
      --post-lookback "${POST_LOOKBACK}" \
      --whatsapp-recipient "${WHATSAPP_RECIPIENT}"



Post a random URL from an RSS feed into WhatsApp
-------------------------------------------------

This command will parse an RSS feed at ``--feed-url`` and publish one random entry that's not older than ``--max-post-age``. The post content will consist of the title and the link of the feed entry.

.. note::
   You must run ``agoras whatsapp authorize`` first before using this command.

Please read about how the RSS feed should be structured in the :doc:`RSS feed section <rss>`. This ensures that the feed is correctly parsed and that the post content is properly formatted.
::

    agoras utils feed-publish \
      --network whatsapp \
      --mode random \
      --feed-url "${FEED_URL}" \
      --max-post-age "${MAX_POST_AGE}" \
      --whatsapp-recipient "${WHATSAPP_RECIPIENT}"

Google Sheets Scheduling
------------------------

Agoras can schedule WhatsApp messages using Google Sheets. This allows you to plan and automate message sending.

Run Scheduled Messages
~~~~~~~~~~~~~~~~~~~~~~

Process scheduled messages from a Google Sheet:

::

    agoras utils schedule-run \
      --network whatsapp \
      --sheets-id "${GOOGLE_SHEETS_ID}" \
      --sheets-name "WhatsApp" \
      --sheets-client-email "${GOOGLE_SHEETS_CLIENT_EMAIL}" \
      --sheets-private-key "${GOOGLE_SHEETS_PRIVATE_KEY}" \
      --whatsapp-recipient "${WHATSAPP_RECIPIENT}"

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
    "Hello World","https://example.com","https://example.com/image.jpg","","","","25-12-2024","14","pending"

Scheduling Logic
~~~~~~~~~~~~~~~~

- Posts with ``state="pending"`` and scheduled time in the past are processed
- Posts are created at the scheduled date and hour
- Sheet state is updated to ``published`` after successful posting
- If posting fails, state is updated to ``error``
- Use ``--network whatsapp`` to process only WhatsApp posts, or omit to process all networks
