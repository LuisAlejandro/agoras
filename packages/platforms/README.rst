agoras-platforms
================

Platform-specific implementations for social networks.

Installation
------------

.. code-block:: bash

   pip install agoras-platforms

Supported Platforms (10)
-------------------------

All platforms are fully extracted and functional:

- ✅ **Discord** - Gaming and community platform
- ✅ **Facebook** - Social network
- ✅ **Instagram** - Photo and video sharing
- ✅ **LinkedIn** - Professional network
- ✅ **Telegram** - Messaging platform
- ✅ **Threads** - Text-based conversations (Meta)
- ✅ **TikTok** - Short-form video
- ✅ **WhatsApp** - Messaging platform
- ✅ **X** - Social network (formerly Twitter)
- ✅ **YouTube** - Video platform

Usage
-----

.. code-block:: python

   import asyncio
   from agoras.platforms.facebook import Facebook

   async def post_to_facebook():
       fb = Facebook(facebook_access_token='...')
       await fb._initialize_client()
       try:
           post_id = await fb.post(
               status_text='Hello World',
               status_link='https://example.com'
           )
           print(f'Posted: {post_id}')
       finally:
           await fb.disconnect()

   asyncio.run(post_to_facebook())

Dependencies
------------

- agoras-core>=2.0.0
- Platform-specific SDKs:

  - tweepy (X/Twitter)
  - python-facebook-api (Facebook)
  - linkedin-api-client (LinkedIn)
  - discord.py (Discord)
  - google-api-python-client (YouTube)
  - python-telegram-bot (Telegram)
  - And more...
