Complete Parameter Reference
==============================

.. note::
   In the **New (Platform)** column, credential parameters refer to ``agoras <platform> authorize`` only since 2.1.0. Platform action commands use content parameters; utils commands use prefixed columns in **New (Utils)**.

X (formerly Twitter) Parameters
--------------------------------

.. list-table::
   :header-rows: 1

   * - Legacy
     - New (Platform)
     - New (Utils)
   * - ``--twitter-consumer-key``
     - ``--consumer-key``
     - (use platform ``authorize`` or env vars)
   * - ``--twitter-consumer-secret``
     - ``--consumer-secret``
     - (use platform ``authorize`` or env vars)
   * - ``--twitter-oauth-token``
     - (env var ``TWITTER_OAUTH_TOKEN``; not a CLI flag)
     - (use platform ``authorize`` or env vars)
   * - ``--twitter-oauth-secret``
     - (env var ``TWITTER_OAUTH_SECRET``; not a CLI flag)
     - (use platform ``authorize`` or env vars)
   * - ``--tweet-id``
     - ``--post-id``
     - ``--post-id``

.. note::
   Utils commands accept no credential flags; run ``agoras x authorize`` or set
   the ``TWITTER_*`` environment variables. The legacy ``--twitter-*`` credential
   parameters applied to the removed ``agoras publish`` command only.

   Since 2.1.0, ``--consumer-key`` and ``--consumer-secret`` in the **New
   (Platform)** column apply to ``agoras x authorize`` only, not to action
   commands. OAuth token/secret are set via the ``TWITTER_OAUTH_TOKEN`` and
   ``TWITTER_OAUTH_SECRET`` environment variables, not CLI flags.

Facebook Parameters
-------------------

.. list-table::
   :header-rows: 1

   * - Legacy
     - New (Platform)
     - New (Utils)
   * - ``--facebook-access-token``
     - (Removed in v2.0 - use ``agoras facebook authorize`` first)
     - (Removed in v2.0)
   * - ``--facebook-object-id``
     - ``--object-id``
     - (use platform ``authorize`` or env vars)
   * - ``--facebook-post-id``
     - ``--post-id``
     - ``--post-id``
   * - ``--facebook-app-id``
     - ``--app-id``
     - (use platform ``authorize`` or env vars)

Discord Parameters
------------------

.. list-table::
   :header-rows: 1

   * - Legacy
     - New (Platform, authorize only since 2.1.0)
     - New (Utils)
   * - ``--discord-bot-token``
     - ``--bot-token``
     - (use platform ``authorize`` or env vars)
   * - ``--discord-server-name``
     - ``--server-name``
     - (use platform ``authorize`` or env vars)
   * - ``--discord-channel-name``
     - ``--channel-name``
     - (use platform ``authorize`` or env vars)

Telegram Parameters
-------------------

.. list-table::
   :header-rows: 1

   * - Legacy
     - New (Platform, authorize only since 2.1.0)
     - New (Utils)
   * - ``--telegram-bot-token``
     - ``--bot-token``
     - (use platform ``authorize`` or env vars)
   * - ``--telegram-chat-id``
     - ``--chat-id``
     - (use platform ``authorize`` or env vars)

WhatsApp Parameters
-------------------

.. list-table::
   :header-rows: 1

   * - Legacy
     - New (Platform, authorize only since 2.1.0)
     - New (Utils)
   * - ``--whatsapp-access-token``
     - ``--access-token``
     - (use platform ``authorize`` or env vars)
   * - ``--whatsapp-phone-number-id``
     - ``--phone-number-id``
     - (use platform ``authorize`` or env vars)

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
