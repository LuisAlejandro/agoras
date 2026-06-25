Complete Parameter Reference
============================

This reference documents all parameters available in Agoras CLI commands.

.. note::
   For a comprehensive reference including environment variables and unattended execution parameters, see :doc:`platform-arguments-envvars`.

Platform Commands vs Utils Commands
------------------------------------

**Platform commands** use simplified content parameter names (credentials on ``authorize`` only since 2.1.0)::

    agoras x authorize --consumer-key "$KEY" --consumer-secret "$SECRET"
    agoras x post --text "Hello"

**Utils commands** use feed and Google Sheets flags only. Platform auth comes from ``agoras <platform> authorize`` or environment variables (same as actions since 2.1.0)::

    agoras x authorize --consumer-key "$KEY" --consumer-secret "$SECRET"
    agoras utils feed-publish --network x --mode last --feed-url "https://example.com/feed.xml"

.. note::
   The ``agoras twitter`` command and ``--twitter-*`` parameters are deprecated. Use ``agoras x`` and ``--x-*`` parameters instead.

Authentication Parameters
=========================

X (formerly Twitter)
--------------------

.. versionchanged:: 2.1
   Credential CLI flags are accepted on ``authorize`` only. Action commands load credentials from storage or environment variables.

**``authorize`` action** (``agoras x authorize``):

* ``--consumer-key`` - X API consumer key (required)
* ``--consumer-secret`` - X API consumer secret (required)

**Action commands** (``post``, ``video``, ``like``, ``share``, ``delete``): no credential flags; use content/action parameters such as ``--text``, ``--post-id``, ``--video-url``.

.. deprecated:: 2.0
   The ``--twitter-*`` parameters in utils commands are deprecated. Use ``--x-*`` parameters instead.

.. note::
   The ``agoras twitter`` command is deprecated. Use ``agoras x`` instead.

Facebook
--------

.. versionchanged:: 2.0
   Facebook now uses OAuth 2.0. Token parameters removed. Run ``agoras facebook authorize`` first.

**Platform commands** (``agoras facebook``):

* ``authorize`` - OAuth 2.0 authorization action (required first step)
* ``--client-id`` - Facebook App client ID (required for authorize)
* ``--client-secret`` - Facebook App client secret (required for authorize)
* ``--app-id`` - Facebook App ID (required for authorize)
* ``--object-id`` - Facebook page or profile ID (required for authorize and post/video)

.. note::
   OAuth platforms require authorization via ``agoras <platform> authorize`` before use.

Instagram
---------

.. versionchanged:: 2.0
   Instagram now uses OAuth 2.0. Token parameters removed. Run ``agoras instagram authorize`` first.

**Platform commands** (``agoras instagram``):

* ``authorize`` - OAuth 2.0 authorization action (required first step)
* ``--client-id`` - Facebook App client ID (required for authorize, Instagram uses Facebook OAuth)
* ``--client-secret`` - Facebook App client secret (required for authorize)
* ``--object-id`` - Facebook user ID for Instagram business account (required for authorize and post/video)

.. note::
   OAuth platforms require authorization via ``agoras <platform> authorize`` before use.

LinkedIn
--------

.. versionchanged:: 2.0
   LinkedIn now uses OAuth 2.0. Token parameters removed. Run ``agoras linkedin authorize`` first.

**Platform commands** (``agoras linkedin``):

* ``authorize`` - OAuth 2.0 authorization action (required first step)
* ``--client-id`` - LinkedIn App client ID (required for authorize)
* ``--client-secret`` - LinkedIn App client secret (required for authorize)
* ``--object-id`` - LinkedIn user/organization ID (required for authorize)

.. note::
   OAuth platforms require authorization via ``agoras <platform> authorize`` before use.

Discord
-------

.. versionchanged:: 2.1
   Credential CLI flags are accepted on ``authorize`` only.

**``authorize`` action**:

* ``--bot-token`` - Discord bot token (required)
* ``--server-name`` - Discord server/guild name (required)
* ``--channel-name`` - Discord channel name (required)

**Action commands**: content parameters only (``--text``, ``--video-url``, ``--post-id``).

YouTube
-------

.. versionchanged:: 2.0
   YouTube now uses OAuth 2.0 "authorize first" workflow. Run ``agoras youtube authorize`` first.

**Platform commands** (``agoras youtube``):

* ``authorize`` - OAuth 2.0 authorization action (required first step)
* ``--client-id`` - YouTube (Google) OAuth client ID (required for authorize)
* ``--client-secret`` - YouTube (Google) OAuth client secret (required for authorize)

.. note::
   OAuth platforms require authorization via ``agoras <platform> authorize`` before use.

TikTok
------

.. versionchanged:: 2.0
   TikTok now uses OAuth 2.0. Token parameters removed. Run ``agoras tiktok authorize`` first.

**Platform commands** (``agoras tiktok``):

* ``authorize`` - OAuth 2.0 authorization action (required first step)
* ``--client-key`` - TikTok client key (required for authorize)
* ``--client-secret`` - TikTok client secret (required for authorize)
* ``--username`` - TikTok username (required for authorize)

.. note::
   OAuth platforms require authorization via ``agoras <platform> authorize`` before use.

Threads
-------

.. versionchanged:: 2.0
   Threads now uses OAuth 2.0. Token parameters removed. Run ``agoras threads authorize`` first.

**Platform commands** (``agoras threads``):

* ``authorize`` - OAuth 2.0 authorization action (required first step)
* ``--app-id`` - Threads (Meta) App ID (required for authorize)
* ``--app-secret`` - Threads (Meta) App secret (required for authorize)

.. note::
   OAuth platforms require authorization via ``agoras <platform> authorize`` before use.

Telegram
--------

.. versionchanged:: 2.1
   ``--bot-token`` and ``--chat-id`` are accepted on ``authorize`` only. ``--parse-mode`` remains on ``post`` and ``video``.

**``authorize`` action**:

* ``--bot-token`` - Telegram bot token from @BotFather (required)
* ``--chat-id`` - Target chat ID (user, group, or channel) (required)

**Action commands**:

* ``--parse-mode`` - Message parse mode: ``HTML``, ``Markdown``, ``MarkdownV2``, or ``None`` (default: HTML; ``post``/``video`` only)
* ``--post-id`` - Message ID for delete action (required for delete)

WhatsApp
--------

.. versionchanged:: 2.1
   ``--access-token`` and ``--phone-number-id`` are accepted on ``authorize`` only. ``--recipient`` remains on action commands.

**``authorize`` action**:

* ``--access-token`` - Meta Graph API access token (required)
* ``--phone-number-id`` - WhatsApp Business phone number ID (required)
* ``--business-account-id`` - WhatsApp Business Account ID (optional)

**Action commands**:

* ``--recipient`` - Target recipient phone number in E.164 format (required on post/video/template)
* ``--template-name`` - Template name (for template action)
* ``--language-code`` - Template language code (ISO 639-1 format, default: en, for template action)
* ``--template-components`` - Template components as JSON string (optional, for template action)

Content Parameters
==================

These parameters are standardized across all platforms.

Text and Links
--------------

* ``--text`` - Text content of the post (replaces ``--status-text``)
* ``--link`` - URL to include in post (replaces ``--status-link``)

Images
------

* ``--image-1`` - First image URL (replaces ``--status-image-url-1``)
* ``--image-2`` - Second image URL (replaces ``--status-image-url-2``)
* ``--image-3`` - Third image URL (replaces ``--status-image-url-3``)
* ``--image-4`` - Fourth image URL (replaces ``--status-image-url-4``)

.. note::
   Not all platforms support 4 images. Check platform-specific documentation.

Video
-----

* ``--video-url`` - URL of video file to upload (required for video actions)
* ``--video-title`` - Video title or caption
* ``--video-description`` - Video description (YouTube, Facebook)
* ``--video-caption`` - Video caption (Instagram)
* ``--video-type`` - Video type (Instagram, Facebook)

Post Interaction
----------------

* ``--post-id`` - Post ID for like/share/delete actions (standardized across platforms)

  Replaces platform-specific IDs:

  * ``--tweet-id`` (X, legacy format)
  * ``--facebook-post-id`` (Facebook)
  * ``--instagram-post-id`` (Instagram)
  * ``--linkedin-post-id`` (LinkedIn)

Platform-Specific Parameters
=============================

YouTube
-------

* ``--video-id`` - YouTube video ID (for like/delete actions)
* ``--title`` - Video title (maps to ``youtube_title``)
* ``--description`` - Video description (maps to ``youtube_description``)
* ``--category-id`` - YouTube category ID
* ``--privacy`` - Privacy status: ``public``, ``private``, or ``unlisted`` (default: ``private``)
* ``--keywords`` - Comma-separated keywords

TikTok
------

* ``--title`` - Video title/caption (maps to ``tiktok_title``)
* ``--privacy`` - Privacy status (default: ``SELF_ONLY``):

  * ``PUBLIC_TO_EVERYONE``
  * ``MUTUAL_FOLLOW_FRIENDS``
  * ``FOLLOWER_OF_CREATOR``
  * ``SELF_ONLY``

Facebook
--------

* ``--profile-id`` - Facebook profile ID (for share action)

Utils Command Parameters
========================

Platform Authentication (legacy utils reference)
------------------------------------------------

.. versionchanged:: 2.1
   Prefixed platform credential flags (``--x-consumer-key``, ``--facebook-access-token``, etc.) were removed from utils commands. Use ``authorize`` or environment variables; see :doc:`platform-arguments-envvars`.

The following applied before 2.1.0 and remain valid on legacy ``agoras publish`` until 3.0:

X (formerly Twitter)
~~~~~~~~~~~~~~~~~~~~

* ``--x-consumer-key`` - X API consumer key (legacy publish / pre-2.1 utils)
* ``--x-consumer-secret`` - X API consumer secret
* ``--x-oauth-token`` - X OAuth token
* ``--x-oauth-secret`` - X OAuth secret

.. deprecated:: 2.0
   The ``--twitter-*`` parameters in utils commands are deprecated. Use ``--x-*`` parameters instead.

Facebook
~~~~~~~~

* ``--facebook-access-token`` - Facebook access token
* ``--facebook-object-id`` - Facebook page or profile ID
* ``--facebook-app-id`` - Facebook App ID

Instagram
~~~~~~~~~

* ``--instagram-access-token`` - Instagram access token
* ``--instagram-object-id`` - Instagram business account ID
* ``--instagram-client-id`` - Facebook App client ID (Instagram uses Facebook OAuth)
* ``--instagram-client-secret`` - Facebook App client secret

LinkedIn
~~~~~~~~

* ``--linkedin-client-id`` - LinkedIn App client ID
* ``--linkedin-client-secret`` - LinkedIn App client secret
* ``--linkedin-refresh-token`` - LinkedIn refresh token (optional, can be loaded from storage)

Discord
~~~~~~~

* ``--discord-bot-token`` - Discord bot token
* ``--discord-server-name`` - Discord server/guild name
* ``--discord-channel-name`` - Discord channel name

YouTube
~~~~~~~

* ``--youtube-client-id`` - YouTube (Google) OAuth client ID
* ``--youtube-client-secret`` - YouTube (Google) OAuth client secret

TikTok
~~~~~~

* ``--tiktok-client-key`` - TikTok App client key
* ``--tiktok-client-secret`` - TikTok App client secret
* ``--tiktok-access-token`` - TikTok access token
* ``--tiktok-refresh-token`` - TikTok refresh token
* ``--tiktok-username`` - TikTok username

Threads
~~~~~~~

* ``--threads-app-id`` - Threads (Meta) App ID
* ``--threads-app-secret`` - Threads (Meta) App secret
* ``--threads-refresh-token`` - Threads refresh token

Telegram
~~~~~~~~

* ``--telegram-bot-token`` - Telegram bot token from @BotFather
* ``--telegram-chat-id`` - Target chat ID (user, group, or channel)

WhatsApp
~~~~~~~~

* ``--whatsapp-access-token`` - Meta Graph API access token
* ``--whatsapp-phone-number-id`` - WhatsApp Business phone number ID
* ``--whatsapp-business-account-id`` - WhatsApp Business Account ID
* ``--whatsapp-recipient`` - Target recipient phone number in E.164 format

Feed Automation
---------------

* ``--network`` - Target social network (required)
* ``--mode`` - Feed mode: ``last`` or ``random`` (required)
* ``--feed-url`` - URL of RSS/Atom feed (required)
* ``--max-count`` - Maximum posts to publish at once
* ``--post-lookback`` - Only posts within last N seconds
* ``--max-post-age`` - Maximum post age in days

Schedule Automation
-------------------

* ``--network`` - Target network (required since 2.1.0; one platform per run)
* ``--sheets-id`` - Google Sheets document ID (required)
* ``--sheets-name`` - Sheet name within document (required)
* ``--sheets-client-email`` - Google service account email (required)
* ``--sheets-private-key`` - Google service account private key (required)

Legacy Parameters
=================

The legacy ``agoras publish`` command uses the original parameter names with platform prefixes. These are maintained for backward compatibility but are deprecated.

See the :doc:`../migration/index` for a complete mapping of legacy to new parameters.
