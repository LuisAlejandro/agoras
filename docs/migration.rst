==========================================
Migration Guide: Legacy to New CLI
==========================================

.. note::
   **v2.0 Package Split**: This guide covers CLI migration (v2.0+). For v2.0 package split and import path changes, see the sections below on "Package Installation" and "Import Path Changes".

Overview
========

Agoras 2.0+ introduces a new CLI structure that's more intuitive, discoverable, and aligned with how users think about social media operations. This guide helps you migrate from the legacy ``agoras publish`` command to the new platform-first command structure.

Package Installation (v2.0+)
==============================

Starting with v2.0, Agoras is split into 5 separate PyPI packages. The main CLI package automatically installs all dependencies.

**Full Installation (Recommended for Most Users):**

.. code-block:: bash

    $ pip install agoras  # Installs all 5 packages including CLI

This installs:
- ``agoras-common``: Utilities, logging, shared constants
- ``agoras-media``: Image and video processing
- ``agoras-core``: Abstract interfaces, Feed, Sheet logic
- ``agoras-platforms``: Platform implementations
- ``agoras``: Command-line interface

**Selective Installation (Advanced Users):**

Install only the packages you need:

.. code-block:: bash

    # Just utilities and logging
    $ pip install agoras-common

    # Media processing (includes common)
    $ pip install agoras-media

    # Core interfaces and business logic (includes common + media)
    $ pip install agoras-core

    # Platform implementations (includes all above)
    $ pip install agoras-platforms

    # CLI tool (includes everything)
    $ pip install agoras

**Package Dependencies:**

The packages follow a layered dependency structure:

.. code-block:: text

   agoras (CLI)
   └── agoras-platforms
       └── agoras-core
           ├── agoras-media
           └── agoras-common

**When to Use Each Package:**

- **Most users**: ``pip install agoras`` (full CLI installation)
- **Python integrations**: ``pip install agoras-platforms`` (no CLI, all platforms)
- **Custom platforms**: ``pip install agoras-core`` (interfaces only)
- **Media processing**: ``pip install agoras-media`` (no social features)
- **Utilities only**: ``pip install agoras-common`` (minimal dependencies)

**Breaking Change:** The monolithic ``agoras`` package structure has been removed. You must install from the new package structure.

Import Path Changes (v2.0)
===========================

All import paths have changed due to the package split. This section provides a comprehensive mapping of old v1.x imports to new v2.0 imports.

Common Utilities
----------------

.. list-table::
   :header-rows: 1
   :widths: 50 50

   * - v1.x Import
     - v2.0 Import
   * - ``from agoras.core.logger import logger``
     - ``from agoras.common.logger import logger``
   * - ``from agoras.core.utils import parse_metatags``
     - ``from agoras.common.utils import parse_metatags``
   * - ``from agoras import __version__``
     - ``from agoras.common.version import __version__``

Media Processing
---------------

.. list-table::
   :header-rows: 1
   :widths: 50 50

   * - v1.x Import
     - v2.0 Import
   * - ``from agoras.core.media import MediaFactory``
     - ``from agoras.media import MediaFactory``
   * - ``from agoras.core.media.image import Image``
     - ``from agoras.media.image import Image``
   * - ``from agoras.core.media.video import Video``
     - ``from agoras.media.video import Video``
   * - ``from agoras.core.media.factory import MediaFactory``
     - ``from agoras.media.factory import MediaFactory``

Core Interfaces
---------------

.. list-table::
   :header-rows: 1
   :widths: 50 50

   * - v1.x Import
     - v2.0 Import
   * - ``from agoras.core.base import SocialNetwork``
     - ``from agoras.core.interfaces import SocialNetwork``
   * - ``from agoras.core.api.base import BaseAPI``
     - ``from agoras.core.api_base import BaseAPI``

Platform Implementations
------------------------

.. list-table::
   :header-rows: 1
   :widths: 50 50

   * - v1.x Import
     - v2.0 Import
   * - ``from agoras.core.facebook import Facebook``
     - ``from agoras.platforms.facebook import Facebook``
   * - ``from agoras.core.api.facebook import FacebookAPI``
     - ``from agoras.platforms.facebook.api import FacebookAPI``
   * - ``from agoras.core.twitter import Twitter``
     - ``from agoras.platforms.x import X``
   * - ``from agoras.core.api.twitter import TwitterAPI``
     - ``from agoras.platforms.x.api import XAPI``
   * - ``from agoras.core.instagram import Instagram``
     - ``from agoras.platforms.instagram import Instagram``
   * - ``from agoras.core.linkedin import LinkedIn``
     - ``from agoras.platforms.linkedin import LinkedIn``
   * - ``from agoras.core.discord import Discord``
     - ``from agoras.platforms.discord import Discord``
   * - ``from agoras.core.youtube import YouTube``
     - ``from agoras.platforms.youtube import YouTube``
   * - ``from agoras.core.tiktok import TikTok``
     - ``from agoras.platforms.tiktok import TikTok``

**New Platforms (v2.0 only):**

.. code-block:: python

    from agoras.platforms.telegram import Telegram
    from agoras.platforms.threads import Threads
    from agoras.platforms.whatsapp import WhatsApp
    from agoras.platforms.x import X  # Twitter rebrand

Core Business Logic (Unchanged)
--------------------------------

These imports remain the same in v2.0:

.. code-block:: python

    from agoras.core.feed import Feed
    from agoras.core.feed.manager import FeedManager
    from agoras.core.sheet import Sheet
    from agoras.core.sheet.manager import SheetManager

CLI Commands
------------

.. list-table::
   :header-rows: 1
   :widths: 50 50

   * - v1.x Import
     - v2.0 Import
   * - ``from agoras.commands.publish import PublishCommand``
     - ``from agoras.cli.commands.publish import PublishCommand``
   * - ``from agoras.cli import main``
     - ``from agoras.cli.main import main``

Authentication
--------------

.. list-table::
   :header-rows: 1
   :widths: 50 50

   * - v1.x Import
     - v2.0 Import
   * - ``from agoras.core.api.auth.base import BaseAuthManager``
     - ``from agoras.core.auth.base import BaseAuthManager``
   * - ``from agoras.core.api.auth.storage import TokenStorage``
     - ``from agoras.core.auth.storage import TokenStorage``
   * - ``from agoras.core.api.auth.callback_server import CallbackServer``
     - ``from agoras.core.auth.callback_server import CallbackServer``

Understanding the Package Split
================================

Why Split the Package?
----------------------

The monolithic package structure in v1.x had several limitations:

- **Heavy Dependencies**: All users had to install media processing libraries even if they only needed basic posting
- **Tight Coupling**: Platform implementations were mixed with core interfaces
- **Large Install Size**: Single package contained everything
- **Hard to Extend**: Difficult to build custom integrations without pulling in all dependencies

The v2.0 modular architecture addresses these issues:

- **Selective Installation**: Install only what you need
- **Clear Boundaries**: Each package has a well-defined purpose
- **Smaller Footprint**: Minimal installations for specific use cases
- **Better Extensibility**: Easy to build custom platforms using just ``agoras-core``

Package Responsibilities
------------------------

**agoras-common** (Foundation)
  - Shared utilities and helper functions
  - Logging configuration
  - Version information
  - No external dependencies beyond Python standard library

**agoras-media** (Media Processing)
  - Image processing (Pillow)
  - Video processing (moviepy)
  - Media factory for creating media objects
  - Depends on: ``agoras-common``

**agoras-core** (Business Logic)
  - Abstract ``SocialNetwork`` interface
  - Base API classes
  - Authentication infrastructure
  - Feed automation logic
  - Google Sheets integration
  - Depends on: ``agoras-common``, ``agoras-media``

**agoras-platforms** (Platform Implementations)
  - Concrete platform implementations (Facebook, Twitter, etc.)
  - Platform-specific API clients
  - Platform authentication handlers
  - Depends on: ``agoras-core`` (which includes media and common)

**agoras** (CLI Tool)
  - Command-line interface
  - Platform command handlers
  - Utility commands (feed, schedule)
  - Depends on: ``agoras-platforms`` (which includes all others)

Migration Strategy
------------------

1. **Update Installation**: Change ``pip install agoras`` to ensure you get v2.0+ (or use specific packages)

2. **Update Imports**: Use the import mapping table above to update all Python imports

3. **Test Incrementally**: Start with non-critical scripts, then migrate production code

4. **Update CI/CD**: Ensure build pipelines install the correct packages

5. **Check Dependencies**: If you only need specific functionality, consider installing only relevant packages

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
     - (Removed in v2.0 - use ``agoras facebook authorize`` first)
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
      --app-secret "$APP_SECRET" \
      --redirect-uri "http://localhost:3456/callback"

    # Then post (no tokens needed)
    agoras threads post \
      --text "Hello Threads!"

**Sharing a Post**

New command (v2.0+)::

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

New (v2.0+)::

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
     - (Removed in v2.0 - use ``agoras facebook authorize`` first)
     - (Removed in v2.0)
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

Frequently Asked Questions
===========================

Installation & Packages
-----------------------

Q: Do I need to install all 5 packages separately?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A: No. Installing ``pip install agoras`` automatically installs all 5 packages as dependencies. You only need to install packages separately if you want to use Agoras as a Python library without the CLI.

Q: Can I install only specific packages?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A: Yes, for advanced use cases. See :doc:`installation` for details. Most users should install the main ``agoras`` package.

Q: What's the difference between ``agoras`` and ``agoras-platforms``?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A: The ``agoras`` package includes the CLI tool and all dependencies. The ``agoras-platforms`` package includes all platform implementations but no CLI - use it if you're building Python integrations without the command-line interface.

CLI Commands
------------

Q: Why did the command format change?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A: The new format is more intuitive and discoverable. Instead of ``agoras publish --network twitter --action post``, you now use ``agoras x post``. This makes it easier to discover what actions each platform supports and reduces command length.

Q: Can I still use ``agoras publish``?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A: Yes, the legacy ``agoras publish`` command still works but shows deprecation warnings. It will be supported for 12 months from the v2.0 release. We recommend migrating to the new format as soon as possible.

Q: What's the difference between platform commands and utils commands?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A: **Platform commands** (e.g., ``agoras x post``) are for direct platform operations and use simplified parameter names (``--consumer-key`` instead of ``--x-consumer-key``). **Utils commands** (e.g., ``agoras utils feed-publish``) are for automation tasks and use prefixed parameters to support multiple platforms in one command.

Q: Why do utils commands use prefixed parameters?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A: Utils commands need to support multiple platforms, so they use prefixed parameters (e.g., ``--x-consumer-key``, ``--facebook-object-id``) to avoid conflicts when specifying credentials for different platforms in the same command.

OAuth 2.0 Authentication
------------------------

Q: Why do I need to run ``authorize`` first for some platforms?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A: OAuth 2.0 platforms (Facebook, Instagram, LinkedIn, YouTube, TikTok, Threads) require a one-time authorization step. This is more secure than passing tokens directly and allows automatic token refresh. Bot-based platforms (Discord, Telegram) and API key platforms (X) don't require this step.

Q: Do I need to re-authorize if I upgrade?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A: No. Once you've authorized, your tokens are stored securely and persist across upgrades. You only need to re-authorize if you revoke access or if your tokens expire.

Q: Where are tokens stored?
~~~~~~~~~~~~~~~~~~~~~~~~~~

A: Tokens are stored in a secure location on your system. The exact location depends on your operating system. See :doc:`../api/core_api` for details on token storage. For more information, check the authentication documentation in the API reference.

Q: How do I revoke authorization?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A: You can revoke authorization through the platform's developer console (Facebook Developer Portal, Google Cloud Console, etc.). Agoras will automatically detect revoked tokens and prompt you to re-authorize.

Parameter Names
---------------

Q: Why did parameter names change?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A: Parameter names were simplified for better usability. For example, ``--status-text`` became ``--text``, and ``--twitter-consumer-key`` became ``--consumer-key`` in platform commands. This makes commands shorter and easier to remember.

Q: Can I still use old parameter names?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A: In platform commands, old parameter names are not supported. In utils commands, some deprecated parameter names (like ``--twitter-*``) still work but show deprecation warnings. See :doc:`../reference/parameters` for the complete parameter reference.

Q: Why are some parameters different in utils commands?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A: Utils commands support multiple platforms, so they use prefixed parameters (e.g., ``--x-consumer-key``) to avoid conflicts. Platform commands only work with one platform, so they use simplified names (e.g., ``--consumer-key``).

Import Paths (Python)
---------------------

Q: Do I need to update my Python imports?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A: Yes, if you're using Agoras as a Python library. All import paths have changed due to the package split. See the "Import Path Changes" section above for a complete mapping.

Q: Where can I find the import mapping?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A: See the "Import Path Changes" section in this migration guide. It provides comprehensive tables mapping old v1.x imports to new v2.0 imports.

Q: What if my imports don't work?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A: First, ensure you've installed the correct packages. If you're using ``agoras-platforms``, make sure it's installed. If you're using ``agoras-core``, ensure all dependencies are installed. Check the import mapping table and verify your import paths match the new structure. If issues persist, open an issue on GitHub.

Migration Timeline
------------------

Q: How long will legacy commands be supported?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A: The legacy ``agoras publish`` command will be supported with deprecation warnings for 12 months from the v2.0 release. After that, it will be removed. We recommend migrating as soon as possible.

Q: When should I migrate?
~~~~~~~~~~~~~~~~~~~~~~~~

A: You can migrate at any time. The legacy commands still work, so you can migrate gradually. We recommend starting with non-critical scripts, then moving to production code once you're comfortable with the new format.

Q: Can I migrate gradually?
~~~~~~~~~~~~~~~~~~~~~~~~~~~

A: Yes! You can use both old and new commands during the transition period. Start by migrating new scripts to the new format, then gradually update existing scripts. The ``--show-migration`` flag can help you preview the new command format.

Troubleshooting
--------------

Q: I get "command not found" errors
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A: Ensure Agoras is installed correctly: ``pip install agoras``. Verify the installation: ``agoras --version``. If using a virtual environment, make sure it's activated. Check that the ``agoras`` command is in your PATH.

Q: My old scripts don't work
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A: Old scripts using ``agoras publish`` should still work but may show deprecation warnings. If they fail completely, check:
- Are you using the correct parameter names?
- Have you updated to v2.0+?
- Are all required parameters provided?
- For OAuth platforms, have you run ``authorize`` first?

Q: I see deprecation warnings
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A: Deprecation warnings indicate you're using old commands or parameters that will be removed in the future. Update your commands to the new format. The warnings won't break your scripts, but you should migrate to avoid issues when legacy support is removed.

Q: OAuth authorization fails
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A: Check that:
- Your app credentials (client ID, client secret) are correct
- Your redirect URI matches what's configured in the platform's developer console
- You have the necessary permissions/scopes enabled in your app
- Your app is approved for production use (if required by the platform)

Q: Platform command says "not authorized"
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A: For OAuth platforms, you must run ``agoras <platform> authorize`` first. After authorization, tokens are stored and you don't need to authorize again unless you revoke access.

Q: Utils command fails with "network not specified"
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A: Utils commands require the ``--network`` parameter to specify which platform to use. For example: ``agoras utils feed-publish --network x --mode last ...``

Getting Help
============

* **Documentation**: https://docs.agoras.io
* **Migration Issues**: https://github.com/LuisAlejandro/agoras/issues
* **Community**: https://github.com/LuisAlejandro/agoras/discussions

The legacy ``agoras publish`` command will be supported with deprecation warnings until Agoras 2.0 (12 months from the 2.0 release).
