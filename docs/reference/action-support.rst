Action Support Matrix
=====================

Not all platforms support all actions. This reference shows which actions are available for each platform.

Complete Support Matrix
------------------------

.. list-table::
   :header-rows: 1
   :widths: 16 8 8 8 8 8 8 8

   * - Platform
     - post
     - video
     - like
     - share
     - delete
     - template
     - authorize
   * - X
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
   * - LinkedIn
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
     - ✗ [1]
     - ✗
     - ✓
     - ✗
     - ✓
   * - YouTube
     - ✗ [2]
     - ✓
     - ✓
     - ✗
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
     - ✓
   * - Threads
     - ✓
     - ✓
     - ✗
     - ✓
     - ✓
     - ✗
     - ✓
   * - Telegram
     - ✓
     - ✓
     - ✗
     - ✗
     - ✓
     - ✗
     - ✓
   * - WhatsApp
     - ✓
     - ✓
     - ✗
     - ✗
     - ✗
     - ✓
     - ✓

**Notes:**

[1] Discord uses reactions, not traditional "likes". Use Discord's native reaction system instead.

[2] YouTube does not support text-only posts; use ``video`` for uploads.

[3] TikTok ``post`` creates photo slideshow posts; ``video`` uploads video content.

.. note::
   The deprecated ``twitter`` CLI alias exposes the same actions as ``x``.

Platform Categories
-------------------

Full-Featured Platforms
~~~~~~~~~~~~~~~~~~~~~~~

These platforms support the full social action set (post, video, like, share, delete):

* **X**: Complete social network features
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
* **Discord**: Bot-based messaging (post, video, delete; no traditional likes)
* **Threads**: Post, video, share, and delete (no like via CLI)
* **Telegram**: Post, video, and delete (messaging platform)
* **WhatsApp**: Post, video, and template messages (Business API)

Feed and Schedule Support
--------------------------

Feed automation and schedule commands work with all 10 platforms:

* ``agoras utils feed-publish --network <platform>`` — all platforms (``twitter`` accepted as deprecated alias for ``x``)
* ``agoras utils schedule-run`` — all platforms

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
