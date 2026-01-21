Usage for WhatsApp
==================

.. note::
   **New in version 2.0**: WhatsApp commands now use the intuitive ``agoras whatsapp`` format.
   See the :doc:`migration guide <migration>` for upgrading from ``agoras publish``.

WhatsApp Business API is Meta's official API for sending messages via WhatsApp. Agoras can send text messages, images, videos, and template messages to WhatsApp recipients using the official `Meta Graph API <https://developers.facebook.com/docs/graph-api>`_.

**Important**: WhatsApp Business API requires a Meta Developer Account, WhatsApp Business Account, and phone number verification. For production use, business verification is required. You must specify a recipient phone number in E.164 format for all message sending operations. Like, share, and delete functionality are not supported by Agoras for WhatsApp.

For CI/CD environments, see :doc:`credentials/whatsapp` for unattended execution setup.

Actions
~~~~~~~

Send a WhatsApp text message
-----------------------------

This command will send a text message to a WhatsApp recipient. The message can include text and a link.

::

    agoras whatsapp post \
      --access-token "${WHATSAPP_ACCESS_TOKEN}" \
      --phone-number-id "${WHATSAPP_PHONE_NUMBER_ID}" \
      --recipient "${WHATSAPP_RECIPIENT}" \
      --text "Hello from Agoras!" \
      --link "https://example.com"

Parameters:

- ``--access-token``: Meta Graph API access token (required)
- ``--phone-number-id``: WhatsApp Business phone number ID (required)
- ``--recipient``: Target recipient phone number in E.164 format, e.g., +1234567890 (required)
- ``--text``: The text content of your message
- ``--link``: A URL to include in the message

**Note**: You must provide at least ``--text`` or ``--link``. The recipient phone number must be in E.164 format (starts with +, includes country code).

Send a WhatsApp message with image
-----------------------------------

This command will send an image message to a WhatsApp recipient. The image can include a caption.

::

    agoras whatsapp post \
      --access-token "${WHATSAPP_ACCESS_TOKEN}" \
      --phone-number-id "${WHATSAPP_PHONE_NUMBER_ID}" \
      --recipient "${WHATSAPP_RECIPIENT}" \
      --text "Check this out!" \
      --link "https://example.com" \
      --image-1 "https://example.com/image.jpg"

Parameters:

- ``--image-1`` through ``--image-4``: URLs pointing to publicly accessible images (JPEG, PNG, GIF)
- ``--text``: Caption text for the image (optional)

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
      --access-token "${WHATSAPP_ACCESS_TOKEN}" \
      --phone-number-id "${WHATSAPP_PHONE_NUMBER_ID}" \
      --recipient "${WHATSAPP_RECIPIENT}" \
      --video-url "https://example.com/video.mp4" \
      --video-title "My Video" \
      --text "Check out this video!"

Parameters:

- ``--video-url``: URL pointing to a publicly accessible video file (required)
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
      --access-token "${WHATSAPP_ACCESS_TOKEN}" \
      --phone-number-id "${WHATSAPP_PHONE_NUMBER_ID}" \
      --recipient "${WHATSAPP_RECIPIENT}" \
      --template-name "hello_world" \
      --language-code "en"

Parameters:

- ``--template-name``: Name of the pre-approved template (required)
- ``--language-code``: Language code in ISO 639-1 format, e.g., "en", "es", "fr" (default: "en")
- ``--template-components``: Template components as JSON string (optional, for parameters, buttons, etc.)

**Template requirements**:
- Templates must be pre-approved by Meta before use
- Template approval can take several days
- Templates are used for notifications and marketing messages
- Language code must match an approved template language
- Template components can include parameters, buttons, and other interactive elements

**Note**: Template messages are required when sending to recipients who haven't messaged you in the last 24 hours. For recipients within the 24-hour window, you can use regular text messages.

RSS Feed Integration
---------------------

Agoras can automatically publish content from RSS/Atom feeds to WhatsApp. This is useful for automatically sharing blog posts, news articles, or other syndicated content.

Publish Last Entry
~~~~~~~~~~~~~~~~~~

Publish the most recent entry from an RSS feed:

::

    agoras utils feed-publish \
      --network whatsapp \
      --mode last \
      --feed-url "https://blog.example.com/feed.xml" \
      --max-count 1 \
      --post-lookback 3600 \
      --whatsapp-access-token "${WHATSAPP_ACCESS_TOKEN}" \
      --whatsapp-phone-number-id "${WHATSAPP_PHONE_NUMBER_ID}" \
      --whatsapp-recipient "${WHATSAPP_RECIPIENT}"

Publish Random Entry
~~~~~~~~~~~~~~~~~~~~

Publish a random entry from an RSS feed:

::

    agoras utils feed-publish \
      --network whatsapp \
      --mode random \
      --feed-url "https://blog.example.com/feed.xml" \
      --max-post-age 30 \
      --whatsapp-access-token "${WHATSAPP_ACCESS_TOKEN}" \
      --whatsapp-phone-number-id "${WHATSAPP_PHONE_NUMBER_ID}" \
      --whatsapp-recipient "${WHATSAPP_RECIPIENT}"

Feed Options:

- ``--network``: Set to ``whatsapp`` (required)
- ``--mode``: Selection mode: ``last`` or ``random`` (required)
- ``--feed-url``: URL of the RSS/Atom feed (required)
- ``--max-count``: Maximum number of posts to publish at once (default: 1)
- ``--post-lookback``: Only publish posts from the last N seconds
- ``--max-post-age``: Don't publish posts older than N days

**Feed format requirements**:
- Feed items should have ``<title>``, ``<link>``, and optionally ``<enclosure>`` for images
- Images from feed enclosures will be sent with the message
- Text and links are combined into the WhatsApp message

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
      --whatsapp-access-token "${WHATSAPP_ACCESS_TOKEN}" \
      --whatsapp-phone-number-id "${WHATSAPP_PHONE_NUMBER_ID}" \
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

    status_text,status_link,status_image_url_1,date,hour,state
    "Hello World","https://example.com","https://example.com/image.jpg","25-12-2024","14","pending"

Scheduling Logic
~~~~~~~~~~~~~~~~

- Posts with ``state="pending"`` and scheduled time in the past are processed
- Posts are created at the scheduled date and hour
- Sheet state is updated to ``published`` after successful posting
- If posting fails, state is updated to ``error``
- Use ``--network whatsapp`` to process only WhatsApp posts, or omit to process all networks

Configuration
-------------

Environment Variables
~~~~~~~~~~~~~~~~~~~~~

For security, store credentials in environment variables:

::

    export WHATSAPP_ACCESS_TOKEN="your_access_token_here"
    export WHATSAPP_PHONE_NUMBER_ID="your_phone_number_id_here"
    export WHATSAPP_BUSINESS_ACCOUNT_ID="your_business_account_id_here"  # Optional
    export WHATSAPP_RECIPIENT="+1234567890"  # E.164 format

Then use Agoras without specifying credentials in commands:

::

    agoras whatsapp post \
      --text "Hello from Agoras!" \
      --link "https://example.com"

Parameter Precedence
~~~~~~~~~~~~~~~~~~~~

1. Command-line arguments (highest priority)
2. Environment variables
3. Configuration files (if supported)

Security Recommendations
~~~~~~~~~~~~~~~~~~~~~~~~

- **Never commit credentials to version control**: Use `.gitignore` for credential files
- **Use environment variables**: Store credentials in environment variables, not in code
- **Use secrets managers**: For production, use AWS Secrets Manager, HashiCorp Vault, etc.
- **Rotate tokens periodically**: Generate new tokens and revoke old ones
- **Limit token permissions**: Only grant necessary permissions
- **Monitor token usage**: Regularly check for unauthorized access

Troubleshooting
---------------

Common Errors and Solutions
~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Error**: "WhatsApp access token and phone number ID are required"
- **Solution**: Ensure you've provided both ``--access-token`` and ``--phone-number-id`` parameters or set the corresponding environment variables.

**Error**: "WhatsApp recipient phone number is required"
- **Solution**: Provide ``--recipient`` parameter with a phone number in E.164 format (e.g., +1234567890).

**Error**: "Invalid phone number format"
- **Solution**: Ensure phone number is in E.164 format: starts with +, includes country code, no spaces or special characters except +.

**Error**: "WhatsApp API error: Invalid access token"
- **Solution**: Generate a new access token. Temporary tokens expire in 24 hours. Check token permissions in Meta Business Manager.

**Error**: "WhatsApp API error: Phone number not found"
- **Solution**: Verify the Phone Number ID is correct. Check your app dashboard for the correct ID.

**Error**: "WhatsApp API error: Rate limit exceeded"
- **Solution**: You've exceeded the rate limit (1000 messages/day for free tier). Wait for the limit to reset or complete business verification for higher limits.

**Error**: "Failed to validate image/video/document"
- **Solution**: Ensure the URL is publicly accessible via HTTPS. Check that the file format is supported and file size is within limits.

**Error**: "Template not found"
- **Solution**: Ensure the template name is correct and the template is approved in your Meta Business Manager.

Rate Limiting Issues
~~~~~~~~~~~~~~~~~~~~

- **Free tier limit**: 1,000 messages per day
- **Limit reset**: Daily at midnight UTC
- **Per recipient limits**: Additional limits apply per recipient
- **Business verification**: Increases limits significantly
- **Error handling**: Agoras will show clear error messages when rate limits are exceeded

Business Verification Problems
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- **Verification pending**: Business verification can take 3-7 business days
- **Documentation required**: Submit all required business documents
- **Status check**: Monitor verification status in Meta Business Manager
- **Support contact**: Contact Meta support if verification is delayed

Token Expiration Handling
~~~~~~~~~~~~~~~~~~~~~~~~~~

- **Temporary tokens**: Expire in 24 hours - generate new token before expiration
- **Permanent tokens**: Don't expire unless revoked - store securely
- **Token refresh**: Not supported for WhatsApp (unlike OAuth refresh tokens)
- **Error messages**: Agoras will show clear error messages if token is invalid

Message Delivery Issues
~~~~~~~~~~~~~~~~~~~~~~~

- **24-hour window**: Can only send free-form messages within 24 hours of recipient's last message
- **Template messages**: Required for messages outside 24-hour window
- **Recipient opt-out**: Recipients can opt-out at any time
- **Delivery status**: Check message delivery status in Meta Business Manager
- **Test numbers**: Use test phone numbers during development

Best Practices
--------------

Message Formatting Tips
~~~~~~~~~~~~~~~~~~~~~~~

- **Keep messages concise**: WhatsApp messages work best when brief and clear
- **Use formatting**: WhatsApp supports basic text formatting (bold, italic, etc.)
- **Include links**: Use ``--link`` parameter to include URLs in messages
- **Image captions**: Use ``--text`` parameter to add captions to images
- **Multiple images**: Send multiple images sequentially for better delivery

Media Optimization
~~~~~~~~~~~~~~~~~~

- **Image formats**: Use JPEG or PNG for best compatibility
- **Image size**: Keep images under 5MB for faster delivery
- **Video formats**: Use MP4 with H.264 codec
- **Video size**: Keep videos under 16MB
- **Document formats**: Use common formats (PDF, DOCX, etc.)
- **URL accessibility**: Ensure all media URLs are publicly accessible via HTTPS

Rate Limit Management
~~~~~~~~~~~~~~~~~~~~~

- **Plan message sending**: Distribute messages throughout the day
- **Monitor usage**: Track daily message counts
- **Business verification**: Complete verification for higher limits
- **Batch sending**: Use scheduling for planned message campaigns
- **Error handling**: Implement retry logic for rate limit errors

Compliance Guidelines
~~~~~~~~~~~~~~~~~~~~~

- **WhatsApp Business Policy**: Follow Meta's WhatsApp Business Policy
- **Message templates**: Use pre-approved templates for notifications
- **Opt-in requirements**: Ensure recipients have opted in to receive messages
- **Data privacy**: Comply with GDPR and local data protection laws
- **Content guidelines**: Follow WhatsApp's content and spam policies
- **Recipient management**: Respect opt-outs immediately

Security Recommendations
~~~~~~~~~~~~~~~~~~~~~~~~~

- **Token security**: Store tokens in environment variables or secrets managers
- **Token rotation**: Rotate tokens periodically for security
- **Access control**: Limit who has access to WhatsApp credentials
- **Monitoring**: Monitor for unauthorized access or unusual activity
- **Backup credentials**: Keep backup tokens in secure storage
- **Revocation**: Immediately revoke compromised tokens

Additional Resources
---------------------

- :doc:`WhatsApp Credentials Setup <credentials/whatsapp>`
- `WhatsApp Business API Documentation <https://developers.facebook.com/docs/whatsapp>`_
- `Meta for Developers <https://developers.facebook.com/>`_
- `WhatsApp Business Policy <https://www.whatsapp.com/legal/business-policy>`_
- `Graph API Reference <https://developers.facebook.com/docs/graph-api>`_
