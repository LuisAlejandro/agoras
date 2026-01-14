Using Agoras
============

.. note::
   **New in version 2.0**: Agoras introduces a new, more intuitive CLI structure.
   **New in version 2.0**: OAuth 2.0 "authorize first" workflow for enhanced security.
   See the :doc:`migration guide <migration>` for upgrading from the legacy ``agoras publish`` command.

Command Overview
----------------

Agoras provides three types of commands:

1. **Platform Commands**: Direct operations on specific social networks
2. **Utils Commands**: Cross-platform automation tools
3. **Legacy Command**: Deprecated ``publish`` command (maintained for backward compatibility)

OAuth 2.0 Authentication Workflow
----------------------------------

.. versionadded:: 2.0

For OAuth 2.0 platforms (Facebook, Instagram, LinkedIn, YouTube, TikTok, Threads), you must authorize Agoras before performing any actions:

1. **Authorize once**: Run ``agoras <platform> authorize`` with your app credentials
2. **Credentials stored**: Encrypted tokens are saved in ``~/.agoras/tokens/``
3. **Use actions**: Run actions without providing tokens - credentials refresh automatically

**Example workflow**::

    # Step 1: Authorize (one-time setup)
    agoras facebook authorize \
      --client-id "$CLIENT_ID" \
      --client-secret "$CLIENT_SECRET" \
      --app-id "$APP_ID" \
      --object-id "$OBJECT_ID"

    # Step 2: Use actions (no tokens needed)
    agoras facebook post --text "Hello World"
    agoras facebook video --video-url "video.mp4"

**Benefits**:
- No manual token handling
- Automatic token refresh
- Secure encrypted storage
- CI/CD support via environment variables

See platform-specific credential guides for detailed setup instructions.

Error Handling
--------------

.. versionadded:: 2.0

Agoras v2.0 provides clearer error messages and validation:

**Example - Missing required parameter**::

    $ agoras x post --text "Hello"
    Error: Missing required parameter: --consumer-key

**Example - Invalid action**::

    $ agoras x invalid-action
    Error: Unknown action 'invalid-action' for platform 'x'.
    Available actions: authorize, post, video, like, share, delete

Automatic Token Refresh
-----------------------

.. versionadded:: 2.0

OAuth 2.0 platforms automatically refresh expired tokens::

    # Tokens are automatically refreshed when needed
    agoras facebook post --text "Hello"  # Uses stored credentials
    # If token expired, it's automatically refreshed

CI/CD Integration
-----------------

.. versionadded:: 2.0

Agoras supports environment variables for CI/CD pipelines::

    # Set environment variables
    export FACEBOOK_CLIENT_ID="your_id"
    export FACEBOOK_CLIENT_SECRET="your_secret"

    # Use in commands (parameters can be omitted if env vars are set)
    agoras facebook authorize \
      --app-id "$FACEBOOK_APP_ID" \
      --object-id "$FACEBOOK_OBJECT_ID"

Platform Commands
~~~~~~~~~~~~~~~~~

Post directly to social networks with intuitive, platform-first commands::

    agoras <platform> <action> [options]

**Supported platforms**: x (formerly Twitter), facebook, instagram, linkedin, discord, youtube, tiktok, threads, telegram, whatsapp

**Example**::

    # Post to X (formerly Twitter)
    agoras x post --consumer-key "$KEY" --text "Hello World!"

    # Upload to YouTube
    agoras youtube video --client-id "$ID" --video-url "video.mp4"

See the full list of available platforms::

    $ agoras --help

See platform-specific actions::

    $ agoras x --help

.. note::
   The ``agoras twitter`` command is deprecated but still works for backward compatibility. Use ``agoras x`` instead.

Utils Commands
~~~~~~~~~~~~~~

Automate posting from RSS/Atom feeds or Google Sheets schedules::

    agoras utils feed-publish --network <platform> --mode <last|random> [options]
    agoras utils schedule-run [options]

**Example**::

    # Publish last entry from RSS feed to X
    agoras utils feed-publish \
      --network x \
      --mode last \
      --feed-url "https://example.com/feed.xml" \
      --x-consumer-key "$TWITTER_CONSUMER_KEY" \
      --x-consumer-secret "$TWITTER_CONSUMER_SECRET" \
      --x-oauth-token "$TWITTER_OAUTH_TOKEN" \
      --x-oauth-secret "$TWITTER_OAUTH_SECRET"

.. note::
   The ``--network twitter`` and ``--twitter-*`` parameters are deprecated. Use ``--network x`` and ``--x-*`` parameters instead.

See utils commands::

    $ agoras utils --help

Quick Start Examples
--------------------

X (formerly Twitter)
~~~~~~~~~~~~~~~~~~~~

Post a tweet with an image::

    agoras x post \
      --consumer-key "$TWITTER_CONSUMER_KEY" \
      --consumer-secret "$TWITTER_CONSUMER_SECRET" \
      --oauth-token "$TWITTER_OAUTH_TOKEN" \
      --oauth-secret "$TWITTER_OAUTH_SECRET" \
      --text "Hello from Agoras!" \
      --image-1 "https://example.com/image.jpg"

Like a tweet::

    agoras x like \
      --consumer-key "$TWITTER_CONSUMER_KEY" \
      --consumer-secret "$TWITTER_CONSUMER_SECRET" \
      --oauth-token "$TWITTER_OAUTH_TOKEN" \
      --oauth-secret "$TWITTER_OAUTH_SECRET" \
      --post-id "1234567890"

.. deprecated:: 2.0
   The ``agoras twitter`` command is deprecated. Use ``agoras x`` instead.

Facebook
~~~~~~~~

First, authorize Agoras to access your Facebook account::

    agoras facebook authorize \
      --client-id "$FACEBOOK_CLIENT_ID" \
      --client-secret "$FACEBOOK_CLIENT_SECRET" \
      --app-id "$FACEBOOK_APP_ID" \
      --object-id "$FACEBOOK_PAGE_ID"

Then post to a Facebook page::

    agoras facebook post \
      --object-id "$FACEBOOK_PAGE_ID" \
      --text "Hello from Agoras!"

Upload a video::

    agoras facebook video \
      --object-id "$FACEBOOK_PAGE_ID" \
      --video-url "https://example.com/video.mp4" \
      --video-title "My Video"

YouTube
~~~~~~~

First, authorize Agoras to access your YouTube account::

    agoras youtube authorize \
      --client-id "$YOUTUBE_CLIENT_ID" \
      --client-secret "$YOUTUBE_CLIENT_SECRET"

Then upload a video::

    agoras youtube video \
      --video-url "https://example.com/video.mp4" \
      --title "My YouTube Video" \
      --description "Video description" \
      --privacy "public"

Discord
~~~~~~~

Send a message to a Discord channel::

    agoras discord post \
      --bot-token "$DISCORD_BOT_TOKEN" \
      --server-name "My Server" \
      --channel-name "general" \
      --text "Hello from Agoras!"

Instagram
~~~~~~~~~

First, authorize Agoras to access your Instagram account::

    agoras instagram authorize \
      --client-id "$INSTAGRAM_CLIENT_ID" \
      --client-secret "$INSTAGRAM_CLIENT_SECRET" \
      --object-id "$INSTAGRAM_ACCOUNT_ID"

Then post to Instagram::

    agoras instagram post \
      --object-id "$INSTAGRAM_ACCOUNT_ID" \
      --image-1 "https://example.com/image.jpg" \
      --text "Hello from Agoras!"

Upload a video::

    agoras instagram video \
      --object-id "$INSTAGRAM_ACCOUNT_ID" \
      --video-url "https://example.com/video.mp4" \
      --text "My Instagram video"

LinkedIn
~~~~~~~~

First, authorize Agoras to access your LinkedIn account::

    agoras linkedin authorize \
      --client-id "$LINKEDIN_CLIENT_ID" \
      --client-secret "$LINKEDIN_CLIENT_SECRET"

Then post to LinkedIn::

    agoras linkedin post \
      --text "Hello from Agoras on LinkedIn!" \
      --link "https://example.com"

Upload a video::

    agoras linkedin video \
      --video-url "https://example.com/video.mp4" \
      --text "My LinkedIn video"

TikTok
~~~~~~

First, authorize Agoras to access your TikTok account::

    agoras tiktok authorize \
      --client-id "$TIKTOK_CLIENT_ID" \
      --client-secret "$TIKTOK_CLIENT_SECRET"

Then upload a video::

    agoras tiktok video \
      --video-url "https://example.com/video.mp4" \
      --privacy "PUBLIC_TO_EVERYONE" \
      --text "My TikTok video"

Threads
~~~~~~~

First, authorize Agoras to access your Threads account::

    agoras threads authorize \
      --client-id "$THREADS_CLIENT_ID" \
      --client-secret "$THREADS_CLIENT_SECRET"

Then post to Threads::

    agoras threads post \
      --text "Hello from Agoras on Threads!"

Share a post::

    agoras threads share \
      --post-id "1234567890"

Telegram
~~~~~~~~

Send a message to a Telegram channel::

    agoras telegram post \
      --bot-token "$TELEGRAM_BOT_TOKEN" \
      --chat-id "$TELEGRAM_CHAT_ID" \
      --text "Hello from Agoras!"

WhatsApp
~~~~~~~~

Send a message via WhatsApp Business API::

    agoras whatsapp post \
      --access-token "$WHATSAPP_ACCESS_TOKEN" \
      --phone-number-id "$WHATSAPP_PHONE_NUMBER_ID" \
      --to "$RECIPIENT_PHONE_NUMBER" \
      --text "Hello from Agoras!"

Feed Automation
~~~~~~~~~~~~~~~

Publish the latest entry from an RSS feed::

    agoras utils feed-publish \
      --network x \
      --mode last \
      --feed-url "https://blog.example.com/feed.xml" \
      --max-count 1 \
      --x-consumer-key "$TWITTER_CONSUMER_KEY" \
      --x-consumer-secret "$TWITTER_CONSUMER_SECRET" \
      --x-oauth-token "$TWITTER_OAUTH_TOKEN" \
      --x-oauth-secret "$TWITTER_OAUTH_SECRET"

Schedule Automation
~~~~~~~~~~~~~~~~~~~

Run scheduled posts from Google Sheets::

    agoras utils schedule-run \
      --network x \
      --sheets-id "$GOOGLE_SHEETS_ID" \
      --sheets-name "Schedule" \
      --sheets-client-email "$GOOGLE_SERVICE_ACCOUNT_EMAIL" \
      --sheets-private-key "$GOOGLE_PRIVATE_KEY" \
      --x-consumer-key "$TWITTER_CONSUMER_KEY" \
      --x-consumer-secret "$TWITTER_CONSUMER_SECRET" \
      --x-oauth-token "$TWITTER_OAUTH_TOKEN" \
      --x-oauth-secret "$TWITTER_OAUTH_SECRET"

Detailed Platform Guides
-------------------------

- :doc:`X (formerly Twitter) <x>` - Full action set (post, video, like, share, delete)
- :doc:`Facebook <facebook>` - Full action set (post, video, like, share, delete)
- :doc:`Instagram <instagram>` - Limited actions (post, video)
- :doc:`LinkedIn <linkedin>` - Full action set (post, video, like, share, delete)
- :doc:`Discord <discord>` - Bot-based messaging (post, video, delete)
- :doc:`YouTube <youtube>` - Video platform (video, like, delete)
- :doc:`TikTok <tiktok>` - Video platform (video, delete)
- :doc:`Threads <threads>` - Meta's text platform (post, video, share)
- :doc:`Telegram <telegram>` - Bot-based messaging (post, video, delete)
- :doc:`WhatsApp <whatsapp>` - Business API messaging (post, video)

Feed Automation
---------------

- :doc:`RSS/Atom Feed Publishing <rss>` - Automated content publishing from feeds

Credentials Setup
-----------------

- :doc:`X (formerly Twitter) Credentials <credentials/x>`
- :doc:`Facebook Credentials <credentials/facebook>`
- :doc:`Instagram Credentials <credentials/instagram>`
- :doc:`LinkedIn Credentials <credentials/linkedin>`
- :doc:`YouTube Credentials <credentials/youtube>`
- :doc:`TikTok Credentials <credentials/tiktok>`
- :doc:`Discord Credentials <credentials/discord>`
- :doc:`Google Sheets Credentials <credentials/google>`

Legacy Format (Deprecated)
---------------------------

.. warning::
   The ``agoras publish`` command is deprecated in Agoras 2.0.
   Please migrate to the new platform-first commands.

The legacy command format is still supported with deprecation warnings::

    agoras publish --network x --action post \
      --twitter-consumer-key "$KEY" \
      --status-text "Hello"

.. note::
   The ``--network twitter`` parameter is deprecated. Use ``--network x`` instead.

See the :doc:`migration guide <migration>` for converting legacy commands to the new format.
