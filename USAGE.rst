Using the application
---------------------

.. note::
   **New in version 2.0**: Agoras introduces a new, intuitive CLI structure.
   Use ``agoras <platform> <action>`` instead of ``agoras publish --network <platform> --action <action>``.

   Example: ``agoras twitter post`` instead of ``agoras publish --network twitter --action post``

   The legacy ``agoras publish`` command still works but is deprecated.

Quick Examples
~~~~~~~~~~~~~~

**Post to Twitter**::

    $ agoras twitter post \
        --consumer-key "${TWITTER_CONSUMER_KEY}" \
        --consumer-secret "${TWITTER_CONSUMER_SECRET}" \
        --oauth-token "${TWITTER_OAUTH_TOKEN}" \
        --oauth-secret "${TWITTER_OAUTH_SECRET}" \
        --text "Hello from Agoras!" \
        --image-1 "https://example.com/image.jpg"

**Post to Facebook**::

    $ agoras facebook post \
        --access-token "${FACEBOOK_ACCESS_TOKEN}" \
        --object-id "${FACEBOOK_PAGE_ID}" \
        --text "Hello from Agoras on Facebook!" \
        --link "https://example.com"

**Upload to YouTube**::

    $ agoras youtube video \
        --client-id "${YOUTUBE_CLIENT_ID}" \
        --client-secret "${YOUTUBE_CLIENT_SECRET}" \
        --video-url "https://example.com/video.mp4" \
        --title "My Video" \
        --privacy "public"

**Automate from RSS feed**::

    $ agoras utils feed-publish \
        --network twitter \
        --mode last \
        --feed-url "https://blog.example.com/feed.xml"

Platform Commands
~~~~~~~~~~~~~~~~~

See available commands for each platform::

    $ agoras --help             # List all platforms
    $ agoras twitter --help     # Twitter actions
    $ agoras facebook --help    # Facebook actions
    $ agoras youtube --help     # YouTube actions

Utils Commands
~~~~~~~~~~~~~~

Cross-platform automation tools::

    $ agoras utils --help              # List utils commands
    $ agoras utils feed-publish --help # Feed automation options
    $ agoras utils schedule-run --help # Schedule automation options


Examples of usage
~~~~~~~~~~~~~~~~~

.. _Using Agoras with Twitter: https://agoras.readthedocs.io/en/latest/twitter.html
.. _Using Agoras with Facebook: https://agoras.readthedocs.io/en/latest/facebook.html
.. _Using Agoras with Instagram: https://agoras.readthedocs.io/en/latest/instagram.html
.. _Using Agoras with LinkedIn: https://agoras.readthedocs.io/en/latest/linkedin.html
.. _Using Agoras with Discord: https://agoras.readthedocs.io/en/latest/discord.html
.. _Using Agoras with YouTube: https://agoras.readthedocs.io/en/latest/youtube.html
.. _Using Agoras with TikTok: https://agoras.readthedocs.io/en/latest/tiktok.html
.. _Using Agoras with Threads: https://agoras.readthedocs.io/en/latest/threads.html
.. _Migration Guide: https://agoras.readthedocs.io/en/latest/migration.html

- `Using Agoras with Twitter`_
- `Using Agoras with Facebook`_
- `Using Agoras with Instagram`_
- `Using Agoras with LinkedIn`_
- `Using Agoras with Discord`_
- `Using Agoras with YouTube`_
- `Using Agoras with TikTok`_
- `Using Agoras with Threads`_
- `Migration Guide`_ (New CLI Format)


Credentials
~~~~~~~~~~~

.. _How to get credentials for Twitter: https://agoras.readthedocs.io/en/latest/credentials/twitter.html
.. _How to get credentials for Facebook: https://agoras.readthedocs.io/en/latest/credentials/facebook.html
.. _How to get credentials for Instagram: https://agoras.readthedocs.io/en/latest/credentials/instagram.html
.. _How to get credentials for LinkedIn: https://agoras.readthedocs.io/en/latest/credentials/linkedin.html
.. _How to get credentials for Discord: https://agoras.readthedocs.io/en/latest/credentials/discord.html
.. _How to get credentials for YouTube: https://agoras.readthedocs.io/en/latest/credentials/youtube.html
.. _How to get credentials for TikTok: https://agoras.readthedocs.io/en/latest/credentials/tiktok.html
.. _How to get credentials for Google spreadsheets: https://agoras.readthedocs.io/en/latest/credentials/google.html

- `How to get credentials for Twitter`_
- `How to get credentials for Facebook`_
- `How to get credentials for Instagram`_
- `How to get credentials for LinkedIn`_
- `How to get credentials for Discord`_
- `How to get credentials for YouTube`_
- `How to get credentials for TikTok`_
- `How to get credentials for Google spreadsheets`_
