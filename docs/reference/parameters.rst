Complete Parameter Reference
============================

This reference documents all parameters available in Agoras CLI commands.

Platform Commands vs Utils Commands
------------------------------------

**Platform commands** use simplified parameter names::

    agoras x post --consumer-key "$KEY" --text "Hello"

**Utils commands** use prefixed parameter names to support multiple platforms::

    agoras utils feed-publish --network x --x-consumer-key "$KEY"

.. note::
   The ``agoras twitter`` command and ``--twitter-*`` parameters are deprecated. Use ``agoras x`` and ``--x-*`` parameters instead.

Authentication Parameters
=========================

X (formerly Twitter)
--------------------

**Platform commands** (``agoras x``):

* ``--consumer-key`` - X API consumer key (required)
* ``--consumer-secret`` - X API consumer secret (required)
* ``--oauth-token`` - X OAuth token (required for most actions)
* ``--oauth-secret`` - X OAuth secret (required for most actions)

**Utils commands**:

* ``--x-consumer-key`` (primary)
* ``--x-consumer-secret`` (primary)
* ``--x-oauth-token`` (primary)
* ``--x-oauth-secret`` (primary)

.. deprecated:: 1.5
   The ``--twitter-*`` parameters in utils commands are deprecated. Use ``--x-*`` parameters instead.

.. note::
   The ``agoras twitter`` command is deprecated. Use ``agoras x`` instead.

Facebook
--------

.. versionchanged:: 1.6
   Facebook now uses OAuth 2.0. Token parameters removed. Run ``agoras facebook authorize`` first.

**Platform commands** (``agoras facebook``):

* ``authorize`` - OAuth 2.0 authorization action (required first step)
* ``--client-id`` - Facebook App client ID (required for authorize)
* ``--client-secret`` - Facebook App client secret (required for authorize)
* ``--app-id`` - Facebook App ID (required for authorize)
* ``--object-id`` - Facebook page or profile ID (required for authorize and post/video)

**Utils commands**:

* ``--facebook-object-id``
* ``--facebook-app-id``

.. note::
   OAuth platforms require authorization via ``agoras <platform> authorize`` before use.

Instagram
---------

.. versionchanged:: 1.6
   Instagram now uses OAuth 2.0. Token parameters removed. Run ``agoras instagram authorize`` first.

**Platform commands** (``agoras instagram``):

* ``authorize`` - OAuth 2.0 authorization action (required first step)
* ``--client-id`` - Facebook App client ID (required for authorize, Instagram uses Facebook OAuth)
* ``--client-secret`` - Facebook App client secret (required for authorize)
* ``--object-id`` - Facebook user ID for Instagram business account (required for authorize and post/video)

**Utils commands**:

* ``--instagram-object-id``

.. note::
   OAuth platforms require authorization via ``agoras <platform> authorize`` before use.

LinkedIn
--------

.. versionchanged:: 1.6
   LinkedIn now uses OAuth 2.0. Token parameters removed. Run ``agoras linkedin authorize`` first.

**Platform commands** (``agoras linkedin``):

* ``authorize`` - OAuth 2.0 authorization action (required first step)
* ``--client-id`` - LinkedIn App client ID (required for authorize)
* ``--client-secret`` - LinkedIn App client secret (required for authorize)
* ``--object-id`` - LinkedIn user/organization ID (required for authorize)

**Utils commands**:

* (No platform-specific parameters needed after authorization)

.. note::
   OAuth platforms require authorization via ``agoras <platform> authorize`` before use.

Discord
-------

**Platform commands** (``agoras discord``):

* ``--bot-token`` - Discord bot token (required)
* ``--server-name`` - Discord server/guild name (required)
* ``--channel-name`` - Discord channel name (required)

**Utils commands**:

* ``--discord-bot-token``
* ``--discord-server-name``
* ``--discord-channel-name``

YouTube
-------

.. versionchanged:: 1.6
   YouTube now uses OAuth 2.0 "authorize first" workflow. Run ``agoras youtube authorize`` first.

**Platform commands** (``agoras youtube``):

* ``authorize`` - OAuth 2.0 authorization action (required first step)
* ``--client-id`` - YouTube (Google) OAuth client ID (required for authorize)
* ``--client-secret`` - YouTube (Google) OAuth client secret (required for authorize)

**Utils commands**:

* (No platform-specific parameters needed after authorization)

.. note::
   OAuth platforms require authorization via ``agoras <platform> authorize`` before use.

TikTok
------

.. versionchanged:: 1.6
   TikTok now uses OAuth 2.0. Token parameters removed. Run ``agoras tiktok authorize`` first.

**Platform commands** (``agoras tiktok``):

* ``authorize`` - OAuth 2.0 authorization action (required first step)
* ``--client-key`` - TikTok client key (required for authorize)
* ``--client-secret`` - TikTok client secret (required for authorize)
* ``--username`` - TikTok username (required for authorize)

**Utils commands**:

* ``--tiktok-username``

.. note::
   OAuth platforms require authorization via ``agoras <platform> authorize`` before use.

Threads
-------

.. versionchanged:: 1.6
   Threads now uses OAuth 2.0. Token parameters removed. Run ``agoras threads authorize`` first.

**Platform commands** (``agoras threads``):

* ``authorize`` - OAuth 2.0 authorization action (required first step)
* ``--app-id`` - Threads (Meta) App ID (required for authorize)
* ``--app-secret`` - Threads (Meta) App secret (required for authorize)
* ``--redirect-uri`` - OAuth redirect URI (required for authorize, default: ``http://localhost:3456/callback``)

**Threads-specific parameters**:

* ``--threads-post-id`` - Threads post ID (for share action)
* ``--threads-who-can-reply`` - Who can reply to post: ``everyone``, ``following``, ``mentioned`` (for post action)

**Utils commands**:

* ``--threads-app-id``
* ``--threads-app-secret``
* ``--threads-refresh-token``
* ``--redirect-uri`` - OAuth redirect URI (required for authorize, e.g., http://localhost:3456/callback)

**Utils commands**:

* (No platform-specific parameters needed after authorization)

.. note::
   OAuth platforms require authorization via ``agoras <platform> authorize`` before use.

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

* ``--network`` - Target network (optional; if omitted, processes all networks from sheet)
* ``--sheets-id`` - Google Sheets document ID (required)
* ``--sheets-name`` - Sheet name within document (required)
* ``--sheets-client-email`` - Google service account email (required)
* ``--sheets-private-key`` - Google service account private key (required)

Legacy Parameters
=================

The legacy ``agoras publish`` command uses the original parameter names with platform prefixes. These are maintained for backward compatibility but are deprecated.

See the :doc:`migration guide <../migration>` for a complete mapping of legacy to new parameters.
