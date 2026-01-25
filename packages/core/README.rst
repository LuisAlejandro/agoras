agoras-core
===========

Core interfaces, Feed management, Sheet management, and Base API/Auth classes.

Installation
------------

.. code-block:: bash

   pip install agoras-core

Contents
--------

- **SocialNetwork Interface**: Abstract base class for all platforms
- **Feed**: RSS feed parsing and management
- **Sheet**: Google Sheets integration for scheduled posts
- **BaseAPI**: Base API client with rate limiting
- **BaseAuthManager**: OAuth2 authentication base
- **OAuthCallbackServer**: Local callback server for OAuth flows
- **TokenStorage**: Secure token storage

Usage
-----

.. code-block:: python

   import asyncio
   from agoras.core.interfaces import SocialNetwork
   from agoras.core.feed import Feed
   from agoras.core.sheet import ScheduleSheet
   from agoras.core.auth import OAuthCallbackServer

   # Download RSS feed
   async def get_feed_items():
       feed = Feed('https://example.com/feed.xml')
       await feed.download()
       items = feed.get_latest_items(5)
       return items

   # Use OAuth callback server
   async def oauth_flow():
       server = OAuthCallbackServer(expected_state='random_state')
       # Server will capture authorization code automatically
       code = await server.start_and_wait()
       return code

   asyncio.run(get_feed_items())

Dependencies
------------

- agoras-common
- agoras-media
- feedparser (RSS parsing)
- gspread (Google Sheets)
