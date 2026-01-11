Using Agoras
============

.. note::
   **New in version 1.5**: Agoras introduces a new, more intuitive CLI structure.
   **New in version 1.6**: OAuth 2.0 "authorize first" workflow for enhanced security.
   See the :doc:`migration guide <migration>` for upgrading from the legacy ``agoras publish`` command.

Command Overview
----------------

Agoras provides three types of commands:

1. **Platform Commands**: Direct operations on specific social networks
2. **Utils Commands**: Cross-platform automation tools
3. **Legacy Command**: Deprecated ``publish`` command (maintained for backward compatibility)

OAuth 2.0 Authentication Workflow
----------------------------------

.. versionadded:: 1.6

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

Platform Commands
~~~~~~~~~~~~~~~~~

Post directly to social networks with intuitive, platform-first commands::

    agoras <platform> <action> [options]

**Supported platforms**: x (formerly Twitter), facebook, instagram, linkedin, discord, youtube, tiktok, threads

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

.. deprecated:: 1.5
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
   The ``agoras publish`` command is deprecated and will be removed in Agoras 2.0.
   Please migrate to the new platform-first commands.

The legacy command format is still supported with deprecation warnings::

    agoras publish --network x --action post \
      --twitter-consumer-key "$KEY" \
      --status-text "Hello"

.. note::
   The ``--network twitter`` parameter is deprecated. Use ``--network x`` instead.

See the :doc:`migration guide <migration>` for converting legacy commands to the new format.
