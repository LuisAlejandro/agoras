Action Support Matrix
=====================

Not all platforms support all actions. This reference shows which actions are available for each platform.

Complete Support Matrix
------------------------

.. list-table::
   :header-rows: 1
   :widths: 20 10 10 10 10 10 10

   * - Platform
     - post
     - video
     - like
     - share
     - delete
     - authorize
   * - Twitter
     - ✓
     - ✓
     - ✓
     - ✓
     - ✓
     - ✓
   * - Facebook
     - ✓
     - ✓
     - ✓
     - ✓
     - ✓
     - ✓
   * - Instagram
     - ✓
     - ✓
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
     - ✓
   * - Discord
     - ✓
     - ✓
     - ✗ [1]
     - ✗
     - ✓
     - ✓
   * - YouTube
     - ✗ [2]
     - ✓
     - ✓
     - ✗
     - ✓
     - ✓
   * - TikTok
     - ✗ [2]
     - ✓
     - ✗
     - ✗
     - ✗
     - ✓
   * - Threads
     - ✓
     - ✓
     - ✗
     - ✓
     - ✗
     - ✓

**Notes:**

[1] Discord uses reactions, not traditional "likes". Use Discord's native reaction system instead.

[2] YouTube and TikTok are video-only platforms. Text-only posts are not supported.

Platform Categories
-------------------

Full-Featured Platforms
~~~~~~~~~~~~~~~~~~~~~~~

These platforms support all standard actions:

* **Twitter**: Complete social network features
* **Facebook**: Complete social network features
* **LinkedIn**: Complete professional network features

Video-Only Platforms
~~~~~~~~~~~~~~~~~~~~

These platforms only support video content:

* **YouTube**: Video sharing and management
* **TikTok**: Short-form video content

Limited Action Platforms
~~~~~~~~~~~~~~~~~~~~~~~~

These platforms have specific limitations:

* **Instagram**: Post and video only (API limitations for likes/shares/deletes)
* **Discord**: Bot-based messaging (no traditional likes)
* **Threads**: Post, video, and share only. Like and delete actions are not supported by the API.

Feed and Schedule Support
--------------------------

All platforms support feed automation and schedule commands:

* ``agoras utils feed-publish --network <platform>`` - Works with all 8 platforms
* ``agoras utils schedule-run`` - Works with all 8 platforms

These are orchestration commands that work uniformly across platforms.

Checking Platform Support
--------------------------

To see which actions a platform supports, use the help command::

    agoras twitter --help
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
