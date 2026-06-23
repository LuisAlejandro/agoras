Platform-by-Platform Migration
==============================

X (formerly Twitter)
--------------------

.. note::
   **X Rebrand**: Twitter has been rebranded to X. Use ``agoras x`` instead of ``agoras twitter``. The ``agoras twitter`` command still works but shows a deprecation warning.

**Posting a Tweet**

Legacy::

    agoras publish --network twitter --action post \
      --twitter-consumer-key "$TWITTER_CONSUMER_KEY" \
      --twitter-consumer-secret "$TWITTER_CONSUMER_SECRET" \
      --twitter-oauth-token "$TWITTER_OAUTH_TOKEN" \
      --twitter-oauth-secret "$TWITTER_OAUTH_SECRET" \
      --status-text "Hello World!" \
      --status-image-url-1 "https://example.com/image.jpg"

New::

    agoras x post \
      --consumer-key "$TWITTER_CONSUMER_KEY" \
      --consumer-secret "$TWITTER_CONSUMER_SECRET" \
      --oauth-token "$TWITTER_OAUTH_TOKEN" \
      --oauth-secret "$TWITTER_OAUTH_SECRET" \
      --text "Hello World!" \
      --image-1 "https://example.com/image.jpg"

.. deprecated:: 2.0
   The ``agoras twitter`` command is deprecated. Use ``agoras x`` instead.

**Uploading a Video**

Legacy::

    agoras publish --network twitter --action video \
      --twitter-consumer-key "$KEY" \
      --twitter-video-url "video.mp4" \
      --twitter-video-title "My Video"

New::

    agoras x video \
      --consumer-key "$KEY" \
      --consumer-secret "$SECRET" \
      --oauth-token "$TOKEN" \
      --oauth-secret "$OAUTH_SECRET" \
      --video-url "video.mp4" \
      --video-title "My Video"

**Authorization Flow**

Legacy::

    agoras publish --network twitter --action authorize \
      --twitter-consumer-key "$KEY" \
      --twitter-consumer-secret "$SECRET"

New::

    agoras x authorize \
      --consumer-key "$KEY" \
      --consumer-secret "$SECRET"

Facebook
--------

**Creating a Post**

.. versionchanged:: 2.0
   Facebook now requires OAuth 2.0 authorization first.

Legacy::

    agoras publish --network facebook --action post \
      --facebook-access-token "$TOKEN" \
      --facebook-object-id "$PAGE_ID" \
      --status-text "Hello Facebook"

New (v2.0+)::

    # First, authorize (one-time setup)
    agoras facebook authorize \
      --client-id "$CLIENT_ID" \
      --client-secret "$CLIENT_SECRET" \
      --app-id "$APP_ID" \
      --object-id "$PAGE_ID"

    # Then post (no tokens needed)
    agoras facebook post \
      --object-id "$PAGE_ID" \
      --text "Hello Facebook"

**Uploading a Video**

Legacy::

    agoras publish --network facebook --action video \
      --facebook-access-token "$TOKEN" \
      --facebook-object-id "$PAGE_ID" \
      --facebook-video-url "video.mp4" \
      --facebook-video-title "My Video"

New (v2.0+)::

    # After authorization
    agoras facebook video \
      --object-id "$PAGE_ID" \
      --video-url "video.mp4" \
      --video-title "My Video"

Instagram
---------

**Creating a Post**

.. versionchanged:: 2.0
   Instagram now requires OAuth 2.0 authorization first.

Legacy::

    agoras publish --network instagram --action post \
      --instagram-access-token "$TOKEN" \
      --instagram-object-id "$ACCOUNT_ID" \
      --status-text "Hello Instagram"

New (v2.0+)::

    # First, authorize (one-time setup)
    agoras instagram authorize \
      --client-id "$CLIENT_ID" \
      --client-secret "$CLIENT_SECRET" \
      --object-id "$ACCOUNT_ID"

    # Then post (no tokens needed)
    agoras instagram post \
      --object-id "$ACCOUNT_ID" \
      --text "Hello Instagram"

LinkedIn
--------

**Creating a Post**

.. versionchanged:: 2.0
   LinkedIn now requires OAuth 2.0 authorization first.

Legacy::

    agoras publish --network linkedin --action post \
      --linkedin-access-token "$TOKEN" \
      --status-text "Hello LinkedIn"

New (v2.0+)::

    # First, authorize (one-time setup)
    agoras linkedin authorize \
      --client-id "$CLIENT_ID" \
      --client-secret "$CLIENT_SECRET" \
      --object-id "$OBJECT_ID"

    # Then post (no tokens needed)
    agoras linkedin post \
      --text "Hello LinkedIn"

Discord
-------

**Sending a Message**

Legacy::

    agoras publish --network discord --action post \
      --discord-bot-token "$BOT_TOKEN" \
      --discord-server-name "MyServer" \
      --discord-channel-name "general" \
      --status-text "Hello Discord"

New::

    agoras discord post \
      --bot-token "$BOT_TOKEN" \
      --server-name "MyServer" \
      --channel-name "general" \
      --text "Hello Discord"

YouTube
-------

**Uploading a Video** (YouTube is video-only)

.. versionchanged:: 2.0
   YouTube now requires OAuth 2.0 authorization first.

Legacy::

    agoras publish --network youtube --action video \
      --youtube-client-id "$CLIENT_ID" \
      --youtube-client-secret "$CLIENT_SECRET" \
      --youtube-video-url "video.mp4" \
      --youtube-title "My Video" \
      --youtube-description "Description" \
      --youtube-privacy-status "public"

New (v2.0+)::

    # First, authorize (one-time setup)
    agoras youtube authorize \
      --client-id "$CLIENT_ID" \
      --client-secret "$CLIENT_SECRET"

    # Then upload (no tokens needed)
    agoras youtube video \
      --video-url "video.mp4" \
      --title "My Video" \
      --description "Description" \
      --privacy "public"

TikTok
------

**Uploading a Video** (TikTok is video-only)

.. versionchanged:: 2.0
   TikTok now requires OAuth 2.0 authorization first.

Legacy::

    agoras publish --network tiktok --action video \
      --tiktok-client-key "$KEY" \
      --tiktok-client-secret "$SECRET" \
      --tiktok-access-token "$TOKEN" \
      --tiktok-video-url "video.mp4" \
      --tiktok-title "My TikTok" \
      --tiktok-privacy-status "PUBLIC_TO_EVERYONE"

New (v2.0+)::

    # First, authorize (one-time setup)
    agoras tiktok authorize \
      --client-key "$KEY" \
      --client-secret "$SECRET" \
      --username "$USERNAME"

    # Then upload (no tokens needed)
    agoras tiktok video \
      --username "$USERNAME" \
      --video-url "video.mp4" \
      --title "My TikTok" \
      --privacy "PUBLIC_TO_EVERYONE"

Threads
-------

**Creating a Post** (New platform in CLI)

.. versionchanged:: 2.0
   Threads now requires OAuth 2.0 authorization first.

New command (v2.0+)::

    # First, authorize (one-time setup)
    agoras threads authorize \
      --app-id "$APP_ID" \
      --app-secret "$APP_SECRET"

    # Then post (no tokens needed)
    agoras threads post \
      --text "Hello Threads!"

**Sharing a Post**

New command (v2.0+)::

    # After authorization
    agoras threads share \
      --post-id "POST_123"

Platform-Specific Notes
========================

This section highlights platform-specific improvements and changes in v2.0.

Facebook
--------

- OAuth2 callback server now available (no manual URL copy-paste)
- Support for Reels and Stories
- Enhanced video upload
- Requires OAuth 2.0 authorization (use ``agoras facebook authorize``)

Instagram
---------

- OAuth2 improvements
- Better media validation
- Requires OAuth 2.0 authorization (use ``agoras instagram authorize``)

LinkedIn
--------

- OAuth2 callback server
- Enhanced post formatting
- Requires OAuth 2.0 authorization (use ``agoras linkedin authorize``)

TikTok
------

- Improved video handling
- OAuth2 support
- Requires OAuth 2.0 authorization (use ``agoras tiktok authorize``)

YouTube
-------

- Better video upload flow
- OAuth2 enhancements
- Requires OAuth 2.0 authorization (use ``agoras youtube authorize``)

New Platforms (v2.0)
--------------------

The following platforms are new in v2.0:

Telegram
^^^^^^^^

.. code-block:: python

    from agoras.platforms.telegram import Telegram

    async def post_to_telegram():
        tg = Telegram(telegram_bot_token='...', telegram_chat_id='...')
        await tg._initialize_client()
        try:
            await tg.post(status_text='Hello Telegram!', status_link='https://example.com')
        finally:
            await tg.disconnect()

Threads
^^^^^^^

.. code-block:: python

    from agoras.platforms.threads import Threads

    async def post_to_threads():
        th = Threads(threads_access_token='...')
        await th._initialize_client()
        try:
            await th.post(status_text='Hello Threads!', status_link='https://example.com')
        finally:
            await th.disconnect()

WhatsApp
^^^^^^^^

.. code-block:: python

    from agoras.platforms.whatsapp import WhatsApp

    async def send_to_whatsapp():
        wa = WhatsApp(whatsapp_access_token='...', whatsapp_phone_number_id='...')
        await wa._initialize_client()
        try:
            await wa.post(status_text='Hello WhatsApp!', status_link='https://example.com')
        finally:
            await wa.disconnect()

X (Twitter)
^^^^^^^^^^^

X is the rebranded name for Twitter. Use ``agoras x`` instead of ``agoras twitter``.

.. code-block:: python

    from agoras.platforms.x import X

    async def post_to_x():
        x_platform = X(x_api_key='...', x_api_secret='...', x_access_token='...', x_access_token_secret='...')
        await x_platform._initialize_client()
        try:
            await x_platform.post(status_text='Hello X!', status_link='https://example.com')
        finally:
            await x_platform.disconnect()
