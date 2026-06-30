CLI Commands Migration
======================

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
   **X Rebrand**: In Agoras 2.0+, Twitter has been rebranded to X. Use ``agoras x`` instead of ``agoras twitter``. The ``agoras twitter`` command still works but is deprecated.

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
     - ``agoras utils schedule-run --network <platform>``

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
     - (Removed in v2.0 - use ``agoras facebook authorize`` first)
   * - Instagram
     - ``--instagram-object-id``
     - ``--object-id``
   * - Discord
     - ``--discord-bot-token``
     - ``--bot-token``
   * - Discord
     - ``--discord-server-name``
     - ``--server-name``
   * - Discord
     - ``--discord-channel-name``
     - ``--channel-name``
   * - Telegram
     - ``--telegram-bot-token``
     - ``--bot-token``
   * - Telegram
     - ``--telegram-chat-id``
     - ``--chat-id``
   * - WhatsApp
     - ``--whatsapp-access-token``
     - ``--access-token``
   * - WhatsApp
     - ``--whatsapp-phone-number-id``
     - ``--phone-number-id``
   * - YouTube
     - ``--youtube-client-id``
     - ``--client-id``

.. versionchanged:: 2.1
   Credential parameters in the table above apply to ``agoras <platform> authorize`` only.
   Platform action commands no longer accept credential or identity CLI flags.

**Note**: Utils commands use the same auth model as platform actions since 2.1.0. Run ``agoras <platform> authorize`` or set environment variables; credential CLI flags are not accepted on utils. Legacy ``agoras publish`` still accepts prefixed credential flags until 3.0.

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

Async/Await Pattern (v2.0)
===========================

All platform methods now use async/await instead of synchronous calls.

**Before (v1.x - synchronous):**

.. code-block:: python

    from agoras.core.facebook import Facebook

    fb = Facebook(facebook_access_token='...')
    fb.post(status_text='Hello', status_link='https://example.com')

**After (v2.0 - asynchronous):**

.. code-block:: python

    import asyncio
    from agoras.platforms.facebook import Facebook

    async def post_to_facebook():
        fb = Facebook(facebook_access_token='...')
        await fb._initialize_client()
        try:
            await fb.post(status_text='Hello', status_link='https://example.com')
        finally:
            await fb.disconnect()

    asyncio.run(post_to_facebook())

**Key Changes:**

- All platform methods are now ``async``
- You must ``await`` all platform operations
- Always call ``await fb._initialize_client()`` before using the platform
- Always call ``await fb.disconnect()`` when done (use ``try/finally`` to ensure cleanup)
- Use ``asyncio.run()`` to execute async functions from synchronous code

**Migration Example:**

.. code-block:: python

    # Before (v1.x)
    def post_content():
        fb = Facebook(facebook_access_token='...')
        fb.post(status_text='Hello', status_link='https://example.com')

    # After (v2.0)
    import asyncio

    async def post_content():
        fb = Facebook(facebook_access_token='...')
        await fb._initialize_client()
        try:
            await fb.post(status_text='Hello', status_link='https://example.com')
        finally:
            await fb.disconnect()

    # Run it
    asyncio.run(post_content())
