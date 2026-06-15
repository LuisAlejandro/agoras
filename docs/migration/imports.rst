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
     - ``from agoras.core.auth.storage import SecureTokenStorage``
   * - ``from agoras.core.api.auth.callback_server import CallbackServer``
     - ``from agoras.core.auth.callback_server import OAuthCallbackServer``
