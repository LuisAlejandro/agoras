==========================================
Migration Guide: Legacy to New CLI
==========================================

Overview
========

Agoras 1.5+ introduces a new CLI structure that's more intuitive, discoverable, and aligned with how users think about social media operations. This guide helps you migrate from the legacy ``agoras publish`` command to the new platform-first command structure.

Why the Change?
---------------

**Problems with the old format:**

* Verbose: ``agoras publish --network twitter --action post`` is unnecessarily long
* Poor discoverability: Hard to find which actions a platform supports
* Mixed concerns: Feed automation mixed with direct platform operations
* Redundant: ``publish`` command doesn't add semantic value

**Benefits of the new format:**

* **Shorter commands**: ``agoras x post`` instead of ``agoras publish --network twitter --action post``
* **Better help**: ``agoras x --help`` shows only X-supported actions
* **Clearer structure**: Platform commands vs utils commands
* **Simplified parameters**: ``--consumer-key`` instead of ``--twitter-consumer-key``
* **Tab completion**: Better shell completion support

.. note::
   **X Rebrand**: In Agoras 1.5+, Twitter has been rebranded to X. Use ``agoras x`` instead of ``agoras twitter``. The ``agoras twitter`` command still works but is deprecated.

Quick Reference
===============

Platform Commands
-----------------

.. list-table::
   :header-rows: 1
   :widths: 50 50

   * - Legacy Format
     - New Format
   * - ``agoras publish --network twitter --action post``
     - ``agoras x post``
   * - ``agoras publish --network facebook --action video``
     - ``agoras facebook video``
   * - ``agoras publish --network youtube --action video``
     - ``agoras youtube video``
   * - ``agoras publish --network instagram --action post``
     - ``agoras instagram post``

Automation Commands
-------------------

.. list-table::
   :header-rows: 1
   :widths: 50 50

   * - Legacy Format
     - New Format
   * - ``agoras publish --network twitter --action last-from-feed``
     - ``agoras utils feed-publish --network x --mode last``
   * - ``agoras publish --network facebook --action random-from-feed``
     - ``agoras utils feed-publish --network facebook --mode random``
   * - ``agoras publish --action schedule``
     - ``agoras utils schedule-run``

Parameter Changes
=================

Authentication Parameters
-------------------------

Within platform commands, platform prefixes are removed:

.. list-table::
   :header-rows: 1
   :widths: 30 30 40

   * - Platform
     - Legacy Parameter
     - New Parameter
   * - X (formerly Twitter)
     - ``--twitter-consumer-key``
     - ``--consumer-key``
   * - X (formerly Twitter)
     - ``--twitter-oauth-token``
     - ``--oauth-token``
   * - Facebook
     - ``--facebook-access-token``
     - (Removed in v1.6 - use ``agoras facebook authorize`` first)
   * - Instagram
     - ``--instagram-object-id``
     - ``--object-id``
   * - Discord
     - ``--discord-bot-token``
     - ``--bot-token``
   * - YouTube
     - ``--youtube-client-id``
     - ``--client-id``

**Note**: Utils commands use prefixed parameters. For X, use ``--x-consumer-key`` (``--twitter-consumer-key`` is deprecated but still works).

Content Parameters
------------------

.. list-table::
   :header-rows: 1
   :widths: 40 60

   * - Legacy Parameter
     - New Parameter
   * - ``--status-text``
     - ``--text``
   * - ``--status-link``
     - ``--link``
   * - ``--status-image-url-1``
     - ``--image-1``
   * - ``--status-image-url-2``
     - ``--image-2``
   * - ``--tweet-id``
     - ``--post-id`` (standardized across platforms)

Platform-by-Platform Migration
================================

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

.. deprecated:: 1.5
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

.. versionchanged:: 1.6
   Facebook now requires OAuth 2.0 authorization first.

Legacy::

    agoras publish --network facebook --action post \
      --facebook-access-token "$TOKEN" \
      --facebook-object-id "$PAGE_ID" \
      --status-text "Hello Facebook"

New (v1.6+)::

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

New (v1.6+)::

    # After authorization
    agoras facebook video \
      --object-id "$PAGE_ID" \
      --video-url "video.mp4" \
      --video-title "My Video"

Instagram
---------

**Creating a Post**

.. versionchanged:: 1.6
   Instagram now requires OAuth 2.0 authorization first.

Legacy::

    agoras publish --network instagram --action post \
      --instagram-access-token "$TOKEN" \
      --instagram-object-id "$ACCOUNT_ID" \
      --status-text "Hello Instagram"

New (v1.6+)::

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

.. versionchanged:: 1.6
   LinkedIn now requires OAuth 2.0 authorization first.

Legacy::

    agoras publish --network linkedin --action post \
      --linkedin-access-token "$TOKEN" \
      --status-text "Hello LinkedIn"

New (v1.6+)::

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

.. versionchanged:: 1.6
   YouTube now requires OAuth 2.0 authorization first.

Legacy::

    agoras publish --network youtube --action video \
      --youtube-client-id "$CLIENT_ID" \
      --youtube-client-secret "$CLIENT_SECRET" \
      --youtube-video-url "video.mp4" \
      --youtube-title "My Video" \
      --youtube-description "Description" \
      --youtube-privacy-status "public"

New (v1.6+)::

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

.. versionchanged:: 1.6
   TikTok now requires OAuth 2.0 authorization first.

Legacy::

    agoras publish --network tiktok --action video \
      --tiktok-client-key "$KEY" \
      --tiktok-client-secret "$SECRET" \
      --tiktok-access-token "$TOKEN" \
      --tiktok-video-url "video.mp4" \
      --tiktok-title "My TikTok" \
      --tiktok-privacy-status "PUBLIC_TO_EVERYONE"

New (v1.6+)::

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

.. versionchanged:: 1.6
   Threads now requires OAuth 2.0 authorization first.

New command (v1.6+)::

    # First, authorize (one-time setup)
    agoras threads authorize \
      --app-id "$APP_ID" \
      --app-secret "$APP_SECRET" \
      --redirect-uri "http://localhost:3456/callback"

    # Then post (no tokens needed)
    agoras threads post \
      --text "Hello Threads!"

**Sharing a Post**

New command (v1.6+)::

    # After authorization
    agoras threads share \
      --post-id "POST_123"

Automation Commands Migration
==============================

Feed Automation
---------------

**Publishing Last Entry from Feed**

Legacy::

    agoras publish --network twitter --action last-from-feed \
      --feed-url "https://example.com/feed.xml" \
      --feed-max-count 1 \
      --twitter-consumer-key "$KEY" \
      --twitter-consumer-secret "$SECRET" \
      --twitter-oauth-token "$TOKEN" \
      --twitter-oauth-secret "$OAUTH_SECRET"

New::

    agoras utils feed-publish \
      --network x \
      --mode last \
      --feed-url "https://example.com/feed.xml" \
      --max-count 1 \
      --x-consumer-key "$KEY" \
      --x-consumer-secret "$SECRET" \
      --x-oauth-token "$TOKEN" \
      --x-oauth-secret "$OAUTH_SECRET"

.. note::
   The ``--network twitter`` and ``--twitter-*`` parameters are deprecated. Use ``--network x`` and ``--x-*`` parameters instead.

**Publishing Random Entry from Feed**

Legacy::

    agoras publish --network facebook --action random-from-feed \
      --feed-url "https://example.com/feed.xml" \
      --facebook-access-token "$TOKEN"

New (v1.6+)::

    # After authorization
    agoras utils feed-publish \
      --network facebook \
      --mode random \
      --feed-url "https://example.com/feed.xml"

Schedule Automation
-------------------

**Running Scheduled Posts**

Legacy::

    agoras publish --network twitter --action schedule \
      --google-sheets-id "$SHEET_ID" \
      --google-sheets-name "Schedule" \
      --google-sheets-client-email "$EMAIL" \
      --google-sheets-private-key "$KEY" \
      --twitter-consumer-key "$KEY"

New::

    agoras utils schedule-run \
      --network x \
      --sheets-id "$SHEET_ID" \
      --sheets-name "Schedule" \
      --sheets-client-email "$EMAIL" \
      --sheets-private-key "$KEY" \
      --x-consumer-key "$KEY"

.. note::
   The ``--network twitter`` and ``--twitter-*`` parameters are deprecated. Use ``--network x`` and ``--x-*`` parameters instead.

Common Migration Pitfalls
==========================

1. **Forgetting to remove platform prefix**

   Wrong::

       agoras x post --twitter-consumer-key "$KEY"

   Correct::

       agoras x post --consumer-key "$KEY"

2. **Using old parameter names**

   Wrong::

       agoras x post --status-text "Hello"

   Correct::

       agoras x post --text "Hello"

3. **Using deprecated twitter command**

   Wrong::

       agoras twitter post --consumer-key "$KEY"

   Correct::

       agoras x post --consumer-key "$KEY"

4. **Using platform command for feed automation**

   Wrong::

       agoras x last-from-feed --feed-url "feed.xml"

   Correct::

       agoras utils feed-publish --network x --mode last --feed-url "feed.xml"

5. **Forgetting --network in utils commands**

   Wrong::

       agoras utils feed-publish --mode last --feed-url "feed.xml"

   Correct::

       agoras utils feed-publish --network x --mode last --feed-url "feed.xml"

6. **Using deprecated parameters in utils commands**

   Wrong::

       agoras utils feed-publish --network twitter --twitter-consumer-key "$KEY"

   Correct::

       agoras utils feed-publish --network x --x-consumer-key "$KEY"

Testing Your Migration
=======================

Preview Mode
------------

Use the ``--show-migration`` flag to preview the new command without executing::

    agoras publish --network twitter --action post \
      --twitter-consumer-key "$KEY" \
      --status-text "Test" \
      --show-migration

This will show::

    Migration Preview:
      Old: agoras publish --network twitter --action post [options]
      New: agoras x post --consumer-key "$KEY" --text "Test"

    No action executed (preview mode)

Platform-Specific Help
----------------------

Explore new commands using help::

    # See all platforms
    agoras --help

    # See X actions
    agoras x --help

    # See X post options
    agoras x post --help

    # See utils commands
    agoras utils --help

    # See feed-publish options
    agoras utils feed-publish --help

Gradual Migration Strategy
===========================

1. **Week 1**: Test migration using ``--show-migration`` flag
2. **Week 2**: Migrate non-critical scripts to new format
3. **Week 3**: Update CI/CD pipelines with new commands
4. **Week 4**: Migrate production scripts
5. **Ongoing**: Keep legacy as fallback until comfortable

Remember: The legacy ``agoras publish`` command will continue to work with deprecation warnings for 12 months.

Complete Parameter Reference
=============================

X (formerly Twitter) Parameters
--------------------------------

.. list-table::
   :header-rows: 1

   * - Legacy
     - New (Platform)
     - New (Utils)
   * - ``--twitter-consumer-key``
     - ``--consumer-key``
     - ``--x-consumer-key`` (``--twitter-consumer-key`` deprecated)
   * - ``--twitter-consumer-secret``
     - ``--consumer-secret``
     - ``--x-consumer-secret`` (``--twitter-consumer-secret`` deprecated)
   * - ``--twitter-oauth-token``
     - ``--oauth-token``
     - ``--x-oauth-token`` (``--twitter-oauth-token`` deprecated)
   * - ``--twitter-oauth-secret``
     - ``--oauth-secret``
     - ``--x-oauth-secret`` (``--twitter-oauth-secret`` deprecated)
   * - ``--tweet-id``
     - ``--post-id``
     - ``--post-id``

.. note::
   For utils commands, use ``--x-*`` parameters. The ``--twitter-*`` parameters are deprecated but still work with deprecation warnings.

Facebook Parameters
-------------------

.. list-table::
   :header-rows: 1

   * - Legacy
     - New (Platform)
     - New (Utils)
   * - ``--facebook-access-token``
     - (Removed in v1.6 - use ``agoras facebook authorize`` first)
     - (Removed in v1.6)
   * - ``--facebook-object-id``
     - ``--object-id``
     - ``--facebook-object-id``
   * - ``--facebook-post-id``
     - ``--post-id``
     - ``--post-id``
   * - ``--facebook-app-id``
     - ``--app-id``
     - ``--facebook-app-id``

Content Parameters (All Platforms)
-----------------------------------

.. list-table::
   :header-rows: 1

   * - Legacy
     - New
   * - ``--status-text``
     - ``--text``
   * - ``--status-link``
     - ``--link``
   * - ``--status-image-url-1``
     - ``--image-1``
   * - ``--status-image-url-2``
     - ``--image-2``
   * - ``--status-image-url-3``
     - ``--image-3``
   * - ``--status-image-url-4``
     - ``--image-4``

Feed Parameters
---------------

.. list-table::
   :header-rows: 1

   * - Legacy
     - New
   * - ``--feed-url``
     - ``--feed-url`` (unchanged)
   * - ``--feed-max-count``
     - ``--max-count``
   * - ``--feed-post-lookback``
     - ``--post-lookback``
   * - ``--feed-max-post-age``
     - ``--max-post-age``

Google Sheets Parameters
------------------------

.. list-table::
   :header-rows: 1

   * - Legacy
     - New
   * - ``--google-sheets-id``
     - ``--sheets-id``
   * - ``--google-sheets-name``
     - ``--sheets-name``
   * - ``--google-sheets-client-email``
     - ``--sheets-client-email``
   * - ``--google-sheets-private-key``
     - ``--sheets-private-key``

Getting Help
============

* **Documentation**: https://docs.agoras.io
* **Migration Issues**: https://github.com/LuisAlejandro/agoras/issues
* **Community**: https://github.com/LuisAlejandro/agoras/discussions

The legacy ``agoras publish`` command will be supported with deprecation warnings until Agoras 2.0 (12 months from the 1.5 release).
