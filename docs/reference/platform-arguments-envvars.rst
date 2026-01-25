Platform Arguments and Environment Variables Reference
========================================================

This document provides a comprehensive reference for all CLI arguments and environment variables available for each platform and action in Agoras. It also identifies which platforms support unattended execution (executing actions without requiring prior authorization via ``authorize``).

Introduction
------------

Agoras supports multiple social media platforms, each with different authentication mechanisms and available actions. This document catalogs:

- All CLI arguments for each platform and action
- Corresponding environment variables that can be used instead
- Unattended execution support (bypassing the ``authorize`` step)

**Authorize Action and Credential Storage**

All platforms support an ``authorize`` action that securely stores credentials for future use. After running ``agoras <platform> authorize`` with the required credentials, those credentials are stored securely and automatically loaded for subsequent actions. This means you only need to provide credentials once during authorization, and all future actions (post, video, like, share, delete, etc.) will use the stored credentials automatically.

You can still override stored credentials by providing them via CLI arguments or environment variables if needed. This provides flexibility for using multiple accounts or temporary credential overrides.

Unattended Execution
--------------------

**Unattended execution** means running actions without first running ``agoras <platform> authorize``. This is useful for CI/CD pipelines and automated scripts where you want to skip the authorization step entirely.

For OAuth 2.0 platforms (Facebook, Instagram, LinkedIn, YouTube, TikTok, Threads), unattended execution requires:

- ``AGORAS_{PLATFORM}_REFRESH_TOKEN`` - The refresh token from a previous authorization
- Additional platform-specific credentials (client ID, client secret, object ID, etc.) as shown in the table below

For unattended execution, you need to provide all required credentials (refresh token plus platform-specific credentials) via environment variables or CLI arguments. See the table below for the complete list of required credentials for each platform.

For non-OAuth platforms (X, Discord, Telegram, WhatsApp), unattended execution requires providing all required credentials via CLI arguments or environment variables. Alternatively, you can run ``agoras <platform> authorize`` once to store credentials securely, and subsequent actions will use the stored credentials automatically.

Quick Reference: Unattended Execution
---------------------------------------

+----------------+----------------------------------------+--------------------------------------------------------------------------------------------------------------------------------+
| Platform       | Authentication Type                    | Unattended Execution                                                                                                        |
+================+========================================+================================================================================================================================+
| X              | OAuth 1.0a (API keys + tokens)         | ``TWITTER_CONSUMER_KEY``, ``TWITTER_CONSUMER_SECRET``, ``TWITTER_OAUTH_TOKEN``, ``TWITTER_OAUTH_SECRET``                    |
+----------------+----------------------------------------+--------------------------------------------------------------------------------------------------------------------------------+
| Facebook       | OAuth 2.0                              | ``FACEBOOK_OBJECT_ID``, ``FACEBOOK_CLIENT_ID``, ``FACEBOOK_CLIENT_SECRET``, ``FACEBOOK_REFRESH_TOKEN``               |
+----------------+----------------------------------------+--------------------------------------------------------------------------------------------------------------------------------+
| Instagram      | OAuth 2.0                              | ``INSTAGRAM_OBJECT_ID``, ``INSTAGRAM_CLIENT_ID``, ``INSTAGRAM_CLIENT_SECRET``, ``INSTAGRAM_REFRESH_TOKEN``           |
+----------------+----------------------------------------+--------------------------------------------------------------------------------------------------------------------------------+
| LinkedIn       | OAuth 2.0                              | ``LINKEDIN_OBJECT_ID``, ``LINKEDIN_CLIENT_ID``, ``LINKEDIN_CLIENT_SECRET``, ``LINKEDIN_REFRESH_TOKEN``               |
+----------------+----------------------------------------+--------------------------------------------------------------------------------------------------------------------------------+
| Discord        | Bot Token                              | ``DISCORD_BOT_TOKEN``, ``DISCORD_SERVER_NAME``, ``DISCORD_CHANNEL_NAME``                                                    |
+----------------+----------------------------------------+--------------------------------------------------------------------------------------------------------------------------------+
| YouTube        | OAuth 2.0                              | ``YOUTUBE_CLIENT_ID``, ``YOUTUBE_CLIENT_SECRET``, ``YOUTUBE_REFRESH_TOKEN``                                           |
+----------------+----------------------------------------+--------------------------------------------------------------------------------------------------------------------------------+
| TikTok         | OAuth 2.0                              | ``TIKTOK_USERNAME``, ``TIKTOK_CLIENT_KEY``, ``TIKTOK_CLIENT_SECRET``, ``TIKTOK_REFRESH_TOKEN``                        |
+----------------+----------------------------------------+--------------------------------------------------------------------------------------------------------------------------------+
| Threads        | OAuth 2.0                              | ``THREADS_APP_ID``, ``THREADS_APP_SECRET``, ``THREADS_REFRESH_TOKEN``, ``THREADS_USER_ID`` |
+----------------+----------------------------------------+--------------------------------------------------------------------------------------------------------------------------------+
| Telegram       | Bot Token                              | ``TELEGRAM_BOT_TOKEN``, ``TELEGRAM_CHAT_ID``                                                                                  |
+----------------+----------------------------------------+--------------------------------------------------------------------------------------------------------------------------------+
| WhatsApp       | API Token                              | ``WHATSAPP_ACCESS_TOKEN``, ``WHATSAPP_PHONE_NUMBER_ID``, ``WHATSAPP_RECIPIENT`` (and optionally ``WHATSAPP_BUSINESS_ACCOUNT_ID``) |
+----------------+----------------------------------------+--------------------------------------------------------------------------------------------------------------------------------+

Common Parameters
-----------------

These parameters are standardized across all platforms that support them:

+------------------+----------------------+----------------------------------+
| Parameter        | CLI Argument         | Environment Variable             |
+==================+======================+==================================+
| Text content    | ``--text``           | ``STATUS_TEXT``                  |
+------------------+----------------------+----------------------------------+
| Link            | ``--link``           | ``STATUS_LINK``                  |
+------------------+----------------------+----------------------------------+
| Image 1         | ``--image-1``        | ``STATUS_IMAGE_URL_1``           |
+------------------+----------------------+----------------------------------+
| Image 2         | ``--image-2``       | ``STATUS_IMAGE_URL_2``           |
+------------------+----------------------+----------------------------------+
| Image 3         | ``--image-3``       | ``STATUS_IMAGE_URL_3``           |
+------------------+----------------------+----------------------------------+
| Image 4         | ``--image-4``       | ``STATUS_IMAGE_URL_4``           |
+------------------+----------------------+----------------------------------+
| Video URL       | ``--video-url``      | ``VIDEO_URL`` (platform-specific)|
+------------------+----------------------+----------------------------------+
| Post ID         | ``--post-id``        | Platform-specific (e.g., ``TWEET_ID``) |
+------------------+----------------------+----------------------------------+

X (formerly Twitter)
====================

**Authentication Type**: OAuth 1.0a (API keys + OAuth tokens)

**Actions**: authorize, post, video, like, share, delete

Authorize Action
----------------

**Required Arguments**:

- ``--consumer-key`` (CLI) / ``TWITTER_CONSUMER_KEY`` (ENVVAR) - X API consumer key
- ``--consumer-secret`` (CLI) / ``TWITTER_CONSUMER_SECRET`` (ENVVAR) - X API consumer secret
- ``--oauth-token`` (CLI) / ``TWITTER_OAUTH_TOKEN`` (ENVVAR) - X OAuth token
- ``--oauth-secret`` (CLI) / ``TWITTER_OAUTH_SECRET`` (ENVVAR) - X OAuth secret

**Note**: After running ``authorize``, all credentials are stored securely. Subsequent actions (post, video, like, share, delete) will automatically use the stored credentials and do not require credential parameters.

Post Action
-----------

**Required Arguments**: None (but content is required)

**Optional Arguments**:

- ``--consumer-key`` (CLI) / ``TWITTER_CONSUMER_KEY`` (ENVVAR) - Not needed if ``authorize`` has been run
- ``--consumer-secret`` (CLI) / ``TWITTER_CONSUMER_SECRET`` (ENVVAR) - Not needed if ``authorize`` has been run
- ``--oauth-token`` (CLI) / ``TWITTER_OAUTH_TOKEN`` (ENVVAR) - Not needed if ``authorize`` has been run
- ``--oauth-secret`` (CLI) / ``TWITTER_OAUTH_SECRET`` (ENVVAR) - Not needed if ``authorize`` has been run
- ``--text`` (CLI) / ``STATUS_TEXT`` (ENVVAR) - Text content
- ``--link`` (CLI) / ``STATUS_LINK`` (ENVVAR) - URL to include
- ``--image-1`` (CLI) / ``STATUS_IMAGE_URL_1`` (ENVVAR) - First image URL
- ``--image-2`` (CLI) / ``STATUS_IMAGE_URL_2`` (ENVVAR) - Second image URL
- ``--image-3`` (CLI) / ``STATUS_IMAGE_URL_3`` (ENVVAR) - Third image URL
- ``--image-4`` (CLI) / ``STATUS_IMAGE_URL_4`` (ENVVAR) - Fourth image URL

**Unattended Execution**: Run ``authorize`` once to store credentials, or provide all four credential arguments (consumer-key, consumer-secret, oauth-token, oauth-secret) via CLI or environment variables.

Video Action
------------

**Required Arguments**:

- ``--video-url`` (CLI) / ``TWITTER_VIDEO_URL`` (ENVVAR) - Video file URL

**Optional Arguments**:

- ``--consumer-key`` (CLI) / ``TWITTER_CONSUMER_KEY`` (ENVVAR) - Not needed if ``authorize`` has been run
- ``--consumer-secret`` (CLI) / ``TWITTER_CONSUMER_SECRET`` (ENVVAR) - Not needed if ``authorize`` has been run
- ``--oauth-token`` (CLI) / ``TWITTER_OAUTH_TOKEN`` (ENVVAR) - Not needed if ``authorize`` has been run
- ``--oauth-secret`` (CLI) / ``TWITTER_OAUTH_SECRET`` (ENVVAR) - Not needed if ``authorize`` has been run
- ``--video-title`` (CLI) / ``TWITTER_VIDEO_TITLE`` (ENVVAR) - Video title/description
- ``--text`` (CLI) / ``STATUS_TEXT`` (ENVVAR) - Text content

**Unattended Execution**: Run ``authorize`` once to store credentials, or provide all four credential arguments via CLI or environment variables.

Like Action
-----------

**Required Arguments**:

- ``--post-id`` (CLI) / ``TWEET_ID`` (ENVVAR) - Tweet ID to like

**Optional Arguments**:

- ``--consumer-key`` (CLI) / ``TWITTER_CONSUMER_KEY`` (ENVVAR) - Not needed if ``authorize`` has been run
- ``--consumer-secret`` (CLI) / ``TWITTER_CONSUMER_SECRET`` (ENVVAR) - Not needed if ``authorize`` has been run
- ``--oauth-token`` (CLI) / ``TWITTER_OAUTH_TOKEN`` (ENVVAR) - Not needed if ``authorize`` has been run
- ``--oauth-secret`` (CLI) / ``TWITTER_OAUTH_SECRET`` (ENVVAR) - Not needed if ``authorize`` has been run

**Unattended Execution**: Run ``authorize`` once to store credentials, or provide all four credential arguments via CLI or environment variables.

Share Action
------------

**Required Arguments**:

- ``--post-id`` (CLI) / ``TWEET_ID`` (ENVVAR) - Tweet ID to retweet/share

**Optional Arguments**:

- ``--consumer-key`` (CLI) / ``TWITTER_CONSUMER_KEY`` (ENVVAR) - Not needed if ``authorize`` has been run
- ``--consumer-secret`` (CLI) / ``TWITTER_CONSUMER_SECRET`` (ENVVAR) - Not needed if ``authorize`` has been run
- ``--oauth-token`` (CLI) / ``TWITTER_OAUTH_TOKEN`` (ENVVAR) - Not needed if ``authorize`` has been run
- ``--oauth-secret`` (CLI) / ``TWITTER_OAUTH_SECRET`` (ENVVAR) - Not needed if ``authorize`` has been run

**Unattended Execution**: Run ``authorize`` once to store credentials, or provide all four credential arguments via CLI or environment variables.

Delete Action
-------------

**Required Arguments**:

- ``--post-id`` (CLI) / ``TWEET_ID`` (ENVVAR) - Tweet ID to delete

**Optional Arguments**:

- ``--consumer-key`` (CLI) / ``TWITTER_CONSUMER_KEY`` (ENVVAR) - Not needed if ``authorize`` has been run
- ``--consumer-secret`` (CLI) / ``TWITTER_CONSUMER_SECRET`` (ENVVAR) - Not needed if ``authorize`` has been run
- ``--oauth-token`` (CLI) / ``TWITTER_OAUTH_TOKEN`` (ENVVAR) - Not needed if ``authorize`` has been run
- ``--oauth-secret`` (CLI) / ``TWITTER_OAUTH_SECRET`` (ENVVAR) - Not needed if ``authorize`` has been run

**Unattended Execution**: Run ``authorize`` once to store credentials, or provide all four credential arguments via CLI or environment variables.

Facebook
========

**Authentication Type**: OAuth 2.0

**Actions**: authorize, post, video, like, share, delete

Authorize Action
----------------

**Required Arguments**:

- ``--client-id`` (CLI) / ``FACEBOOK_CLIENT_ID`` (ENVVAR) - Facebook App client ID
- ``--client-secret`` (CLI) / ``FACEBOOK_CLIENT_SECRET`` (ENVVAR) - Facebook App client secret
- ``--app-id`` (CLI) / ``FACEBOOK_APP_ID`` (ENVVAR) - Facebook App ID
- ``--object-id`` (CLI) / ``FACEBOOK_OBJECT_ID`` (ENVVAR) - Facebook user/page ID

Post Action
-----------

**Required Arguments**:

- ``--object-id`` (CLI) / ``FACEBOOK_OBJECT_ID`` (ENVVAR) - Facebook page or profile ID

**Optional Arguments**:

- ``--text`` (CLI) / ``STATUS_TEXT`` (ENVVAR) - Text content
- ``--link`` (CLI) / ``STATUS_LINK`` (ENVVAR) - URL to include
- ``--image-1`` (CLI) / ``STATUS_IMAGE_URL_1`` (ENVVAR) - First image URL
- ``--image-2`` (CLI) / ``STATUS_IMAGE_URL_2`` (ENVVAR) - Second image URL
- ``--image-3`` (CLI) / ``STATUS_IMAGE_URL_3`` (ENVVAR) - Third image URL
- ``--image-4`` (CLI) / ``STATUS_IMAGE_URL_4`` (ENVVAR) - Fourth image URL

**Unattended Execution**: Set ``FACEBOOK_OBJECT_ID``, ``FACEBOOK_CLIENT_ID``, ``FACEBOOK_CLIENT_SECRET``, and ``AGORAS_FACEBOOK_REFRESH_TOKEN`` environment variables.

Video Action
------------

**Required Arguments**:

- ``--object-id`` (CLI) / ``FACEBOOK_OBJECT_ID`` (ENVVAR) - Facebook page or profile ID
- ``--video-url`` (CLI) / ``FACEBOOK_VIDEO_URL`` (ENVVAR) - Video file URL

**Optional Arguments**:

- ``--video-title`` (CLI) / ``FACEBOOK_VIDEO_TITLE`` (ENVVAR) - Video title
- ``--video-description`` (CLI) / ``FACEBOOK_VIDEO_DESCRIPTION`` (ENVVAR) - Video description
- ``--video-type`` (CLI) / ``FACEBOOK_VIDEO_TYPE`` (ENVVAR) - Video type

**Unattended Execution**: Set ``FACEBOOK_OBJECT_ID``, ``FACEBOOK_CLIENT_ID``, ``FACEBOOK_CLIENT_SECRET``, and ``AGORAS_FACEBOOK_REFRESH_TOKEN`` environment variables.

Like Action
------------

**Required Arguments**:

- ``--post-id`` (CLI) / ``FACEBOOK_POST_ID`` (ENVVAR) - Facebook post ID

**Optional Arguments**: None

**Unattended Execution**: Set ``FACEBOOK_OBJECT_ID``, ``FACEBOOK_CLIENT_ID``, ``FACEBOOK_CLIENT_SECRET``, and ``AGORAS_FACEBOOK_REFRESH_TOKEN`` environment variables.

Share Action
------------

**Required Arguments**:

- ``--post-id`` (CLI) / ``FACEBOOK_POST_ID`` (ENVVAR) - Facebook post ID

**Optional Arguments**:

- ``--profile-id`` (CLI) / ``FACEBOOK_PROFILE_ID`` (ENVVAR) - Facebook profile ID where post will be shared

**Unattended Execution**: Set ``FACEBOOK_OBJECT_ID``, ``FACEBOOK_CLIENT_ID``, ``FACEBOOK_CLIENT_SECRET``, and ``AGORAS_FACEBOOK_REFRESH_TOKEN`` environment variables.

Delete Action
-------------

**Required Arguments**:

- ``--post-id`` (CLI) / ``FACEBOOK_POST_ID`` (ENVVAR) - Facebook post ID

**Optional Arguments**: None

**Unattended Execution**: Set ``FACEBOOK_OBJECT_ID``, ``FACEBOOK_CLIENT_ID``, ``FACEBOOK_CLIENT_SECRET``, and ``AGORAS_FACEBOOK_REFRESH_TOKEN`` environment variables.

Instagram
=========

**Authentication Type**: OAuth 2.0 (uses Facebook OAuth)

**Actions**: authorize, post, video

Authorize Action
----------------

**Required Arguments**:

- ``--client-id`` (CLI) / ``INSTAGRAM_CLIENT_ID`` (ENVVAR) - Facebook App client ID (Instagram uses Facebook OAuth)
- ``--client-secret`` (CLI) / ``INSTAGRAM_CLIENT_SECRET`` (ENVVAR) - Facebook App client secret
- ``--object-id`` (CLI) / ``INSTAGRAM_OBJECT_ID`` (ENVVAR) - Facebook user ID for Instagram business account

Post Action
-----------

**Required Arguments**:

- ``--object-id`` (CLI) / ``INSTAGRAM_OBJECT_ID`` (ENVVAR) - Instagram business account ID

**Optional Arguments**:

- ``--image-1`` (CLI) / ``STATUS_IMAGE_URL_1`` (ENVVAR) - Image URL (required for photo posts)

**Unattended Execution**: Set ``INSTAGRAM_OBJECT_ID``, ``INSTAGRAM_CLIENT_ID``, ``INSTAGRAM_CLIENT_SECRET``, and ``AGORAS_INSTAGRAM_REFRESH_TOKEN`` environment variables.

Video Action
------------

**Required Arguments**:

- ``--object-id`` (CLI) / ``INSTAGRAM_OBJECT_ID`` (ENVVAR) - Instagram business account ID
- ``--video-url`` (CLI) / ``INSTAGRAM_VIDEO_URL`` (ENVVAR) - Video file URL

**Optional Arguments**:

- ``--video-caption`` (CLI) / ``INSTAGRAM_VIDEO_CAPTION`` (ENVVAR) - Video caption
- ``--video-type`` (CLI) / ``INSTAGRAM_VIDEO_TYPE`` (ENVVAR) - Video type (e.g., REELS, STORIES)

**Unattended Execution**: Set ``INSTAGRAM_OBJECT_ID``, ``INSTAGRAM_CLIENT_ID``, ``INSTAGRAM_CLIENT_SECRET``, and ``AGORAS_INSTAGRAM_REFRESH_TOKEN`` environment variables.

LinkedIn
========

**Authentication Type**: OAuth 2.0

**Actions**: authorize, post, video, like, share, delete

Authorize Action
----------------

**Required Arguments**:

- ``--client-id`` (CLI) / ``LINKEDIN_CLIENT_ID`` (ENVVAR) - LinkedIn App client ID
- ``--client-secret`` (CLI) / ``LINKEDIN_CLIENT_SECRET`` (ENVVAR) - LinkedIn App client secret
- ``--object-id`` (CLI) / ``LINKEDIN_OBJECT_ID`` (ENVVAR) - LinkedIn user/organization ID

Post Action
-----------

**Optional Arguments**:

- ``--text`` (CLI) / ``STATUS_TEXT`` (ENVVAR) - Text content
- ``--link`` (CLI) / ``STATUS_LINK`` (ENVVAR) - URL to include
- ``--image-1`` (CLI) / ``STATUS_IMAGE_URL_1`` (ENVVAR) - First image URL

**Unattended Execution**: Set ``LINKEDIN_OBJECT_ID``, ``LINKEDIN_CLIENT_ID``, ``LINKEDIN_CLIENT_SECRET``, and ``AGORAS_LINKEDIN_REFRESH_TOKEN`` environment variables.

Video Action
------------

**Required Arguments**:

- ``--video-url`` (CLI) / ``LINKEDIN_VIDEO_URL`` (ENVVAR) - Video file URL

**Optional Arguments**:

- ``--video-title`` (CLI) / ``LINKEDIN_VIDEO_TITLE`` (ENVVAR) - Video title

**Unattended Execution**: Set ``LINKEDIN_OBJECT_ID``, ``LINKEDIN_CLIENT_ID``, ``LINKEDIN_CLIENT_SECRET``, and ``AGORAS_LINKEDIN_REFRESH_TOKEN`` environment variables.

Like Action
-----------

**Required Arguments**:

- ``--post-id`` (CLI) / ``LINKEDIN_POST_ID`` (ENVVAR) - LinkedIn post ID

**Unattended Execution**: Set ``LINKEDIN_OBJECT_ID``, ``LINKEDIN_CLIENT_ID``, ``LINKEDIN_CLIENT_SECRET``, and ``AGORAS_LINKEDIN_REFRESH_TOKEN`` environment variables.

Share Action
------------

**Required Arguments**:

- ``--post-id`` (CLI) / ``LINKEDIN_POST_ID`` (ENVVAR) - LinkedIn post ID

**Unattended Execution**: Set ``LINKEDIN_OBJECT_ID``, ``LINKEDIN_CLIENT_ID``, ``LINKEDIN_CLIENT_SECRET``, and ``AGORAS_LINKEDIN_REFRESH_TOKEN`` environment variables.

Delete Action
-------------

**Required Arguments**:

- ``--post-id`` (CLI) / ``LINKEDIN_POST_ID`` (ENVVAR) - LinkedIn post ID

**Unattended Execution**: Set ``LINKEDIN_OBJECT_ID``, ``LINKEDIN_CLIENT_ID``, ``LINKEDIN_CLIENT_SECRET``, and ``AGORAS_LINKEDIN_REFRESH_TOKEN`` environment variables.

Discord
=======

**Authentication Type**: Bot Token

**Actions**: authorize, post, video, delete

Authorize Action
----------------

**Required Arguments**:

- ``--bot-token`` (CLI) / ``DISCORD_BOT_TOKEN`` (ENVVAR) - Discord bot token
- ``--server-name`` (CLI) / ``DISCORD_SERVER_NAME`` (ENVVAR) - Discord server (guild) name
- ``--channel-name`` (CLI) / ``DISCORD_CHANNEL_NAME`` (ENVVAR) - Discord channel name

**Note**: After running ``authorize``, all credentials are stored securely. Subsequent actions (post, video, delete) will automatically use the stored credentials and do not require credential parameters.

Post Action
-----------

**Optional Arguments**:

- ``--bot-token`` (CLI) / ``DISCORD_BOT_TOKEN`` (ENVVAR) - Not needed if ``authorize`` has been run
- ``--server-name`` (CLI) / ``DISCORD_SERVER_NAME`` (ENVVAR) - Not needed if ``authorize`` has been run
- ``--channel-name`` (CLI) / ``DISCORD_CHANNEL_NAME`` (ENVVAR) - Not needed if ``authorize`` has been run
- ``--text`` (CLI) / ``STATUS_TEXT`` (ENVVAR) - Text content
- ``--link`` (CLI) / ``STATUS_LINK`` (ENVVAR) - URL to include
- ``--image-1`` (CLI) / ``STATUS_IMAGE_URL_1`` (ENVVAR) - First image URL
- ``--image-2`` (CLI) / ``STATUS_IMAGE_URL_2`` (ENVVAR) - Second image URL
- ``--image-3`` (CLI) / ``STATUS_IMAGE_URL_3`` (ENVVAR) - Third image URL
- ``--image-4`` (CLI) / ``STATUS_IMAGE_URL_4`` (ENVVAR) - Fourth image URL

**Unattended Execution**: Run ``authorize`` once to store credentials, or provide ``DISCORD_BOT_TOKEN``, ``DISCORD_SERVER_NAME``, and ``DISCORD_CHANNEL_NAME`` via CLI or environment variables.

Video Action
------------

**Required Arguments**:

- ``--video-url`` (CLI) / ``DISCORD_VIDEO_URL`` (ENVVAR) - Video file URL

**Optional Arguments**:

- ``--bot-token`` (CLI) / ``DISCORD_BOT_TOKEN`` (ENVVAR) - Not needed if ``authorize`` has been run
- ``--server-name`` (CLI) / ``DISCORD_SERVER_NAME`` (ENVVAR) - Not needed if ``authorize`` has been run
- ``--channel-name`` (CLI) / ``DISCORD_CHANNEL_NAME`` (ENVVAR) - Not needed if ``authorize`` has been run
- ``--video-title`` (CLI) / ``DISCORD_VIDEO_TITLE`` (ENVVAR) - Video title/description

**Unattended Execution**: Run ``authorize`` once to store credentials, or provide ``DISCORD_BOT_TOKEN``, ``DISCORD_SERVER_NAME``, and ``DISCORD_CHANNEL_NAME`` via CLI or environment variables.

Delete Action
-------------

**Required Arguments**:

- ``--post-id`` (CLI) / ``DISCORD_POST_ID`` (ENVVAR) - Discord message ID

**Optional Arguments**:

- ``--bot-token`` (CLI) / ``DISCORD_BOT_TOKEN`` (ENVVAR) - Not needed if ``authorize`` has been run
- ``--server-name`` (CLI) / ``DISCORD_SERVER_NAME`` (ENVVAR) - Not needed if ``authorize`` has been run
- ``--channel-name`` (CLI) / ``DISCORD_CHANNEL_NAME`` (ENVVAR) - Not needed if ``authorize`` has been run

**Unattended Execution**: Run ``authorize`` once to store credentials, or provide ``DISCORD_BOT_TOKEN``, ``DISCORD_SERVER_NAME``, and ``DISCORD_CHANNEL_NAME`` via CLI or environment variables.

YouTube
=======

**Authentication Type**: OAuth 2.0

**Actions**: authorize, video, like, delete

Authorize Action
----------------

**Required Arguments**:

- ``--client-id`` (CLI) / ``YOUTUBE_CLIENT_ID`` (ENVVAR) - YouTube (Google) OAuth client ID
- ``--client-secret`` (CLI) / ``YOUTUBE_CLIENT_SECRET`` (ENVVAR) - YouTube (Google) OAuth client secret

Video Action
------------

**Required Arguments**:

- ``--video-url`` (CLI) / ``YOUTUBE_VIDEO_URL`` (ENVVAR) - Video file URL

**Optional Arguments**:

- ``--title`` (CLI) / ``YOUTUBE_TITLE`` (ENVVAR) - Video title
- ``--description`` (CLI) / ``YOUTUBE_DESCRIPTION`` (ENVVAR) - Video description
- ``--category-id`` (CLI) / ``YOUTUBE_CATEGORY_ID`` (ENVVAR) - YouTube category ID
- ``--privacy`` (CLI) / ``YOUTUBE_PRIVACY_STATUS`` (ENVVAR) - Privacy status: ``public``, ``private``, or ``unlisted`` (default: ``private``)
- ``--keywords`` (CLI) / ``YOUTUBE_KEYWORDS`` (ENVVAR) - Comma-separated keywords

**Unattended Execution**: Set ``YOUTUBE_CLIENT_ID``, ``YOUTUBE_CLIENT_SECRET``, and ``AGORAS_YOUTUBE_REFRESH_TOKEN`` environment variables.

Like Action
-----------

**Required Arguments**:

- ``--video-id`` (CLI) / ``YOUTUBE_VIDEO_ID`` (ENVVAR) - YouTube video ID

**Unattended Execution**: Set ``YOUTUBE_CLIENT_ID``, ``YOUTUBE_CLIENT_SECRET``, and ``AGORAS_YOUTUBE_REFRESH_TOKEN`` environment variables.

Delete Action
-------------

**Required Arguments**:

- ``--video-id`` (CLI) / ``YOUTUBE_VIDEO_ID`` (ENVVAR) - YouTube video ID

**Unattended Execution**: Set ``YOUTUBE_CLIENT_ID``, ``YOUTUBE_CLIENT_SECRET``, and ``AGORAS_YOUTUBE_REFRESH_TOKEN`` environment variables.

TikTok
======

**Authentication Type**: OAuth 2.0

**Actions**: authorize, post, video

Authorize Action
----------------

**Required Arguments**:

- ``--client-key`` (CLI) / ``TIKTOK_CLIENT_KEY`` (ENVVAR) - TikTok App client key
- ``--client-secret`` (CLI) / ``TIKTOK_CLIENT_SECRET`` (ENVVAR) - TikTok App client secret
- ``--username`` (CLI) / ``TIKTOK_USERNAME`` (ENVVAR) - TikTok username

Post Action
-----------

**Required Arguments**:

- At least one image URL using ``--image-1``, ``--image-2``, ``--image-3``, or ``--image-4``

**Optional Arguments**:

- ``--text`` (CLI) / ``STATUS_TEXT`` (ENVVAR) - Text content of the post
- ``--link`` (CLI) / ``STATUS_LINK`` (ENVVAR) - URL to include in post
- ``--image-1`` (CLI) / ``STATUS_IMAGE_URL_1`` (ENVVAR) - First image URL
- ``--image-2`` (CLI) / ``STATUS_IMAGE_URL_2`` (ENVVAR) - Second image URL
- ``--image-3`` (CLI) / ``STATUS_IMAGE_URL_3`` (ENVVAR) - Third image URL
- ``--image-4`` (CLI) / ``STATUS_IMAGE_URL_4`` (ENVVAR) - Fourth image URL
- ``--title`` (CLI) / ``TIKTOK_TITLE`` (ENVVAR) - Post title/caption
- ``--privacy`` (CLI) / ``TIKTOK_PRIVACY_STATUS`` (ENVVAR) - Privacy status: ``PUBLIC_TO_EVERYONE``, ``MUTUAL_FOLLOW_FRIENDS``, ``FOLLOWER_OF_CREATOR``, or ``SELF_ONLY`` (default: ``SELF_ONLY``)
- ``--allow-comments`` (CLI) / ``TIKTOK_ALLOW_COMMENTS`` (ENVVAR) - Allow comments on the post (default: true)
- ``--auto-add-music`` (CLI) / ``TIKTOK_AUTO_ADD_MUSIC`` (ENVVAR) - Automatically add music to the slideshow (default: false)
- ``--brand-organic`` (CLI) / ``TIKTOK_BRAND_ORGANIC`` (ENVVAR) - Mark content as promotional (displays "Promotional content" label)
- ``--brand-content`` (CLI) / ``TIKTOK_BRAND_CONTENT`` (ENVVAR) - Mark content as paid partnership (displays "Paid partnership" label)

Video Action
------------

**Required Arguments**:

- ``--video-url`` (CLI) / ``TIKTOK_VIDEO_URL`` (ENVVAR) - Video file URL

**Optional Arguments**:

- ``--title`` (CLI) / ``TIKTOK_TITLE`` (ENVVAR) - Video title/caption
- ``--privacy`` (CLI) / ``TIKTOK_PRIVACY_STATUS`` (ENVVAR) - Privacy status: ``PUBLIC_TO_EVERYONE``, ``MUTUAL_FOLLOW_FRIENDS``, ``FOLLOWER_OF_CREATOR``, or ``SELF_ONLY`` (default: ``SELF_ONLY``)
- ``--allow-comments`` (CLI) / ``TIKTOK_ALLOW_COMMENTS`` (ENVVAR) - Allow comments on the video (default: true)
- ``--allow-duet`` (CLI) / ``TIKTOK_ALLOW_DUET`` (ENVVAR) - Allow other users to duet with your video (default: true)
- ``--allow-stitch`` (CLI) / ``TIKTOK_ALLOW_STITCH`` (ENVVAR) - Allow other users to stitch your video (default: true)
- ``--brand-organic`` (CLI) / ``TIKTOK_BRAND_ORGANIC`` (ENVVAR) - Mark content as promotional (displays "Promotional content" label)
- ``--brand-content`` (CLI) / ``TIKTOK_BRAND_CONTENT`` (ENVVAR) - Mark content as paid partnership (displays "Paid partnership" label)

**Unattended Execution**: Set ``TIKTOK_USERNAME``, ``TIKTOK_CLIENT_KEY``, ``TIKTOK_CLIENT_SECRET``, and ``AGORAS_TIKTOK_REFRESH_TOKEN`` environment variables.

Threads
=======

**Authentication Type**: OAuth 2.0

**Actions**: authorize, post, video, share

Authorize Action
----------------

**Required Arguments**:

- ``--app-id`` (CLI) / ``THREADS_APP_ID`` (ENVVAR) - Threads (Meta) App ID
- ``--app-secret`` (CLI) / ``THREADS_APP_SECRET`` (ENVVAR) - Threads (Meta) App secret

Post Action
-----------

**Optional Arguments**:

- ``--text`` (CLI) / ``STATUS_TEXT`` (ENVVAR) - Text content
- ``--link`` (CLI) / ``STATUS_LINK`` (ENVVAR) - URL to include
- ``--image-1`` (CLI) / ``STATUS_IMAGE_URL_1`` (ENVVAR) - First image URL
- ``--image-2`` (CLI) / ``STATUS_IMAGE_URL_2`` (ENVVAR) - Second image URL
- ``--image-3`` (CLI) / ``STATUS_IMAGE_URL_3`` (ENVVAR) - Third image URL
- ``--image-4`` (CLI) / ``STATUS_IMAGE_URL_4`` (ENVVAR) - Fourth image URL

**Unattended Execution**: Set ``THREADS_APP_ID``, ``THREADS_APP_SECRET``, ``AGORAS_THREADS_REFRESH_TOKEN``, and ``AGORAS_THREADS_USER_ID`` environment variables.

Video Action
------------

**Required Arguments**:

- ``--video-url`` (CLI) / ``THREADS_VIDEO_URL`` (ENVVAR) - Video file URL

**Optional Arguments**:

- ``--video-title`` (CLI) / ``THREADS_VIDEO_TITLE`` (ENVVAR) - Video caption/description

**Unattended Execution**: Set ``THREADS_APP_ID``, ``THREADS_APP_SECRET``, ``AGORAS_THREADS_REFRESH_TOKEN``, and ``AGORAS_THREADS_USER_ID`` environment variables.

Share Action
------------

**Required Arguments**:

- ``--post-id`` (CLI) / ``THREADS_POST_ID`` (ENVVAR) - Threads post ID

**Unattended Execution**: Set ``THREADS_APP_ID``, ``THREADS_APP_SECRET``, ``AGORAS_THREADS_REFRESH_TOKEN``, and ``AGORAS_THREADS_USER_ID`` environment variables.

Telegram
========

**Authentication Type**: Bot Token

**Actions**: authorize, post, video, delete

Authorize Action
----------------

**Required Arguments**:

- ``--bot-token`` (CLI) / ``TELEGRAM_BOT_TOKEN`` (ENVVAR) - Telegram bot token from @BotFather
- ``--chat-id`` (CLI) / ``TELEGRAM_CHAT_ID`` (ENVVAR) - Target chat ID (user, group, or channel)

**Note**: After running ``authorize``, all credentials are stored securely. Subsequent actions (post, video, delete) will automatically use the stored credentials and do not require credential parameters.

Post Action
-----------

**Optional Arguments**:

- ``--bot-token`` (CLI) / ``TELEGRAM_BOT_TOKEN`` (ENVVAR) - Not needed if ``authorize`` has been run
- ``--chat-id`` (CLI) / ``TELEGRAM_CHAT_ID`` (ENVVAR) - Not needed if ``authorize`` has been run
- ``--parse-mode`` (CLI) / ``TELEGRAM_PARSE_MODE`` (ENVVAR) - Message parse mode: ``HTML``, ``Markdown``, ``MarkdownV2``, or ``None`` (default: ``HTML``)
- ``--text`` (CLI) / ``STATUS_TEXT`` (ENVVAR) - Text content
- ``--link`` (CLI) / ``STATUS_LINK`` (ENVVAR) - URL to include
- ``--image-1`` (CLI) / ``STATUS_IMAGE_URL_1`` (ENVVAR) - First image URL
- ``--image-2`` (CLI) / ``STATUS_IMAGE_URL_2`` (ENVVAR) - Second image URL
- ``--image-3`` (CLI) / ``STATUS_IMAGE_URL_3`` (ENVVAR) - Third image URL
- ``--image-4`` (CLI) / ``STATUS_IMAGE_URL_4`` (ENVVAR) - Fourth image URL

**Unattended Execution**: Run ``authorize`` once to store credentials, or provide ``TELEGRAM_BOT_TOKEN`` and ``TELEGRAM_CHAT_ID`` via CLI or environment variables.

Video Action
------------

**Required Arguments**:

- ``--video-url`` (CLI) / ``VIDEO_URL`` (ENVVAR) - Video file URL

**Optional Arguments**:

- ``--bot-token`` (CLI) / ``TELEGRAM_BOT_TOKEN`` (ENVVAR) - Not needed if ``authorize`` has been run
- ``--chat-id`` (CLI) / ``TELEGRAM_CHAT_ID`` (ENVVAR) - Not needed if ``authorize`` has been run
- ``--video-title`` (CLI) / ``VIDEO_TITLE`` (ENVVAR) - Video title/description

**Unattended Execution**: Run ``authorize`` once to store credentials, or provide ``TELEGRAM_BOT_TOKEN`` and ``TELEGRAM_CHAT_ID`` via CLI or environment variables.

Delete Action
-------------

**Required Arguments**:

- ``--post-id`` (CLI) / ``TELEGRAM_MESSAGE_ID`` (ENVVAR) - Telegram message ID

**Optional Arguments**:

- ``--bot-token`` (CLI) / ``TELEGRAM_BOT_TOKEN`` (ENVVAR) - Not needed if ``authorize`` has been run
- ``--chat-id`` (CLI) / ``TELEGRAM_CHAT_ID`` (ENVVAR) - Not needed if ``authorize`` has been run

**Unattended Execution**: Run ``authorize`` once to store credentials, or provide ``TELEGRAM_BOT_TOKEN`` and ``TELEGRAM_CHAT_ID`` via CLI or environment variables.

WhatsApp
========

**Authentication Type**: API Token

**Actions**: authorize, post, video, template

Authorize Action
----------------

**Required Arguments**:

- ``--access-token`` (CLI) / ``WHATSAPP_ACCESS_TOKEN`` (ENVVAR) - Meta Graph API access token
- ``--phone-number-id`` (CLI) / ``WHATSAPP_PHONE_NUMBER_ID`` (ENVVAR) - WhatsApp Business phone number ID

**Optional Arguments**:

- ``--business-account-id`` (CLI) / ``WHATSAPP_BUSINESS_ACCOUNT_ID`` (ENVVAR) - WhatsApp Business Account ID

**Note**: After running ``authorize``, credentials (access-token, phone-number-id, business-account-id) are stored securely. Subsequent actions will automatically use the stored credentials. However, ``--recipient`` is still required for messaging actions as it varies per message and is not stored during authorization.

Post Action
-----------

**Required Arguments**:

- ``--recipient`` (CLI) / ``WHATSAPP_RECIPIENT`` (ENVVAR) - Target recipient phone number in E.164 format (e.g., +1234567890)

**Optional Arguments**:

- ``--access-token`` (CLI) / ``WHATSAPP_ACCESS_TOKEN`` (ENVVAR) - Not needed if ``authorize`` has been run
- ``--phone-number-id`` (CLI) / ``WHATSAPP_PHONE_NUMBER_ID`` (ENVVAR) - Not needed if ``authorize`` has been run
- ``--business-account-id`` (CLI) / ``WHATSAPP_BUSINESS_ACCOUNT_ID`` (ENVVAR) - Not needed if ``authorize`` has been run
- ``--text`` (CLI) / ``STATUS_TEXT`` (ENVVAR) - Text content
- ``--link`` (CLI) / ``STATUS_LINK`` (ENVVAR) - URL to include
- ``--image-1`` (CLI) / ``STATUS_IMAGE_URL_1`` (ENVVAR) - First image URL
- ``--image-2`` (CLI) / ``STATUS_IMAGE_URL_2`` (ENVVAR) - Second image URL
- ``--image-3`` (CLI) / ``STATUS_IMAGE_URL_3`` (ENVVAR) - Third image URL
- ``--image-4`` (CLI) / ``STATUS_IMAGE_URL_4`` (ENVVAR) - Fourth image URL

**Unattended Execution**: Run ``authorize`` once to store credentials, or provide ``WHATSAPP_ACCESS_TOKEN``, ``WHATSAPP_PHONE_NUMBER_ID``, and ``WHATSAPP_RECIPIENT`` via CLI or environment variables.

Video Action
------------

**Required Arguments**:

- ``--recipient`` (CLI) / ``WHATSAPP_RECIPIENT`` (ENVVAR) - Target recipient phone number in E.164 format
- ``--video-url`` (CLI) / ``VIDEO_URL`` (ENVVAR) - Video file URL

**Optional Arguments**:

- ``--access-token`` (CLI) / ``WHATSAPP_ACCESS_TOKEN`` (ENVVAR) - Not needed if ``authorize`` has been run
- ``--phone-number-id`` (CLI) / ``WHATSAPP_PHONE_NUMBER_ID`` (ENVVAR) - Not needed if ``authorize`` has been run
- ``--business-account-id`` (CLI) / ``WHATSAPP_BUSINESS_ACCOUNT_ID`` (ENVVAR) - Not needed if ``authorize`` has been run
- ``--video-title`` (CLI) / ``VIDEO_TITLE`` (ENVVAR) - Video title/description

**Unattended Execution**: Run ``authorize`` once to store credentials, or provide ``WHATSAPP_ACCESS_TOKEN``, ``WHATSAPP_PHONE_NUMBER_ID``, and ``WHATSAPP_RECIPIENT`` via CLI or environment variables.

Template Action
--------------

**Required Arguments**:

- ``--recipient`` (CLI) / ``WHATSAPP_RECIPIENT`` (ENVVAR) - Target recipient phone number in E.164 format
- ``--template-name`` (CLI) / ``WHATSAPP_TEMPLATE_NAME`` (ENVVAR) - Name of the pre-approved template

**Optional Arguments**:

- ``--access-token`` (CLI) / ``WHATSAPP_ACCESS_TOKEN`` (ENVVAR) - Not needed if ``authorize`` has been run
- ``--phone-number-id`` (CLI) / ``WHATSAPP_PHONE_NUMBER_ID`` (ENVVAR) - Not needed if ``authorize`` has been run
- ``--business-account-id`` (CLI) / ``WHATSAPP_BUSINESS_ACCOUNT_ID`` (ENVVAR) - Not needed if ``authorize`` has been run
- ``--language-code`` (CLI) / ``WHATSAPP_TEMPLATE_LANGUAGE`` (ENVVAR) - Language code (ISO 639-1 format, default: en)
- ``--template-components`` (CLI) / ``WHATSAPP_TEMPLATE_COMPONENTS`` (ENVVAR) - Template components as JSON string

**Unattended Execution**: Run ``authorize`` once to store credentials, or provide all required arguments via CLI or environment variables.

Environment Variable Naming Patterns
====================================

Environment variables follow these patterns:

- **OAuth 2.0 Refresh Tokens**: ``AGORAS_{PLATFORM}_REFRESH_TOKEN``
- **Platform Credentials**: ``{PLATFORM}_{CREDENTIAL_TYPE}`` (e.g., ``TWITTER_CONSUMER_KEY``, ``DISCORD_BOT_TOKEN``)
- **Common Content**: ``STATUS_TEXT``, ``STATUS_LINK``, ``STATUS_IMAGE_URL_1``, etc.
- **Platform-Specific**: Platform-specific parameters use platform prefix (e.g., ``YOUTUBE_TITLE``, ``TIKTOK_PRIVACY_STATUS``)

See Also
========

- :doc:`parameters` - Complete parameter reference
- :doc:`action-support` - Platform action support matrix
- Platform-specific credential guides in :doc:`../credentials/index`
