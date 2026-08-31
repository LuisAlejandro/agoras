Action Support Matrix
=====================

Not all platforms support all actions. This reference shows which actions are available for each platform.

Complete Support Matrix
------------------------

.. list-table::
   :header-rows: 1
   :widths: 12 6 6 6 5 5 6 7 7 7 7 6

   * - Platform
     - post
     - video
     - thread
     - like
     - share
     - delete
     - delete-reply
     - get-post
     - get-reply
     - template
     - authorize
   * - X
     - ✓
     - ✓
     - ✓ [4]
     - ✓
     - ✓
     - ✓
     - ✓
     - ✓
     - ✓
     - ✗
     - ✓
   * - Facebook
     - ✓
     - ✓
     - ✗
     - ✓
     - ✓
     - ✓
     - ✓
     - ✓
     - ✓
     - ✗
     - ✓
   * - Instagram
     - ✓
     - ✓
     - ✗
     - ✗
     - ✗
     - ✗
     - ✓
     - ✓
     - ✓
     - ✗
     - ✓
   * - LinkedIn
     - ✓
     - ✓
     - ✗
     - ✓
     - ✓
     - ✓
     - ✓
     - ✓
     - ✓
     - ✗
     - ✓
   * - Discord
     - ✓
     - ✓
     - ✓ [4]
     - ✗ [1]
     - ✗
     - ✓
     - ✓
     - ✓
     - ✓
     - ✗
     - ✓
   * - YouTube
     - ✗ [2]
     - ✓
     - ✗
     - ✓
     - ✗
     - ✓
     - ✓
     - ✓
     - ✓
     - ✗
     - ✓
   * - TikTok
     - ✓ [3]
     - ✓
     - ✗
     - ✗
     - ✗
     - ✗
     - ✗
     - ✗ [5]
     - ✗ [5]
     - ✗
     - ✓
   * - Threads
     - ✓
     - ✓
     - ✓ [4]
     - ✗
     - ✓
     - ✓
     - ✓
     - ✓
     - ✓
     - ✗
     - ✓
   * - Telegram
     - ✓
     - ✓
     - ✗
     - ✗
     - ✗
     - ✓
     - ✓
     - ✗ [5]
     - ✗ [5]
     - ✗
     - ✓
   * - WhatsApp
     - ✓
     - ✓
     - ✗
     - ✗
     - ✗
     - ✗
     - ✗
     - ✗ [5]
     - ✗ [5]
     - ✓
     - ✓

**Notes:**

[1] Discord uses reactions, not traditional "likes". Use Discord's native reaction system instead.

[2] YouTube does not support text-only posts; use ``video`` for uploads.

[3] TikTok ``post`` creates photo slideshow posts; ``video`` uploads video content.

[4] ``thread`` is YAML-only via ``--content``. See :doc:`../content-files`.

[5] CLI subcommands exist for uniformity, but the runtime raises "not supported"
   (TikTok has no official arbitrary-post read API; Telegram Bot API has no
   arbitrary-message-by-ID read; WhatsApp Cloud API does not read messages by ID).

[6] Mutating actions (``post``, ``reply``, ``delete``, etc.) print a compact
   status object ``{"id": "<id>"}``. Read actions ``get-post`` and ``get-reply``
   print the full normalized six-key content object (``id``, ``text``, ``media``,
   ``author``, ``created_at``, ``metadata``) via ``_output_content``. Automation
   must branch on action type when parsing stdout.

.. note::
   The deprecated ``twitter`` CLI alias exposes the same actions as ``x``.

Platform Categories
-------------------

Full-Featured Platforms
~~~~~~~~~~~~~~~~~~~~~~~

These platforms support the full social action set (post, video, like, share, delete):

* **X**: Complete social network features (plus YAML ``thread``)
* **Facebook**: Complete social network features
* **LinkedIn**: Complete professional network features

Video-Focused Platforms
~~~~~~~~~~~~~~~~~~~~~~~

* **YouTube**: Video uploads, likes, and deletes
* **TikTok**: Video uploads and photo slideshow posts

Limited Action Platforms
~~~~~~~~~~~~~~~~~~~~~~~~

These platforms have specific API limitations:

* **Instagram**: Post and video only (no like, share, or delete via API)
* **Discord**: Bot-based messaging (post, video, thread, delete; no traditional likes)
* **Threads**: Post, video, thread, share, and delete (no like via CLI)
* **Telegram**: Post, video, and delete (messaging platform)
* **WhatsApp**: Post, video, and template messages (Business API)

Feed and Schedule Support
--------------------------

Feed automation and schedule commands work with all 10 platforms:

* ``agoras utils feed-publish --network <platform>`` — all platforms (``twitter`` accepted as deprecated alias for ``x``)
* ``agoras utils schedule-run --network <platform>`` — all platforms (one platform per run; required since 2.1.0)

These are orchestration commands that delegate to each platform's supported actions.

Checking Platform Support
--------------------------

To see which actions a platform supports, use the help command::

    agoras x --help
    agoras youtube --help
    agoras instagram --help

The help output will only show actions that the platform supports.

Action Validation
-----------------

Agoras automatically validates that the requested action is supported by the platform. If you try an unsupported action, you'll get a clear error message::

    $ agoras youtube post --help
    Error: Action 'post' is not supported by youtube.
    Supported actions: authorize, video, like, delete

This prevents wasted API calls and provides immediate feedback.
