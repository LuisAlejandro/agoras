Usage for X (formerly Twitter)
==============================

.. note::
   **New in version 1.5**: X commands now use the intuitive ``agoras x`` format.
   See the :doc:`migration guide <migration>` for upgrading from ``agoras publish``.

.. deprecated:: 1.5
   The ``agoras twitter`` command is deprecated. Use ``agoras x`` instead.

X (formerly Twitter) is a social network that allows you to publish short messages (called tweets) of up to 280 characters. Agoras provides full CLI support for posting, liking, sharing, and managing X content.

**Important**: X now requires a paid subscription for certain parts of the API. The free tier will let you publish and delete X posts, but may have limitations on likes or retweets depending on your API access level.

Available Actions
~~~~~~~~~~~~~~~~~

* ``authorize`` - Set up OAuth 1.0a authentication
* ``post`` - Create text and image tweets (up to 4 images)
* ``video`` - Upload videos
* ``like`` - Like tweets
* ``share`` - Retweet/share tweets
* ``delete`` - Delete your own tweets

Quick Start
~~~~~~~~~~~

See all X commands::

    agoras x --help

.. note::
   The ``agoras twitter`` command still works for backward compatibility but shows a deprecation warning. Use ``agoras x`` instead.

Post a Tweet
------------

**New format** (Agoras 1.5+)::

    agoras x post \
      --consumer-key "${TWITTER_CONSUMER_KEY}" \
      --consumer-secret "${TWITTER_CONSUMER_SECRET}" \
      --oauth-token "${TWITTER_OAUTH_TOKEN}" \
      --oauth-secret "${TWITTER_OAUTH_SECRET}" \
      --text "${STATUS_TEXT}" \
      --image-1 "${IMAGE_URL_1}" \
      --image-2 "${IMAGE_URL_2}"

.. deprecated:: 1.5
   The ``agoras twitter`` command is deprecated. Use ``agoras x`` instead.

**Legacy format** (deprecated)::

    agoras publish \
      --network "x" \
      --action "post" \
      --twitter-consumer-key "${TWITTER_CONSUMER_KEY}" \
      --twitter-consumer-secret "${TWITTER_CONSUMER_SECRET}" \
      --twitter-oauth-token "${TWITTER_OAUTH_TOKEN}" \
      --twitter-oauth-secret "${TWITTER_OAUTH_SECRET}" \
      --status-text "${STATUS_TEXT}" \
      --status-image-url-1 "${IMAGE_URL_1}"



Like a Tweet
------------

**New format**::

    agoras x like \
      --consumer-key "${TWITTER_CONSUMER_KEY}" \
      --consumer-secret "${TWITTER_CONSUMER_SECRET}" \
      --oauth-token "${TWITTER_OAUTH_TOKEN}" \
      --oauth-secret "${TWITTER_OAUTH_SECRET}" \
      --post-id "${TWEET_ID}"

Share a Tweet (Retweet)
-----------------------

**New format**::

    agoras x share \
      --consumer-key "${TWITTER_CONSUMER_KEY}" \
      --consumer-secret "${TWITTER_CONSUMER_SECRET}" \
      --oauth-token "${TWITTER_OAUTH_TOKEN}" \
      --oauth-secret "${TWITTER_OAUTH_SECRET}" \
      --post-id "${TWEET_ID}"

Delete a Tweet
--------------

**New format**::

    agoras x delete \
      --consumer-key "${TWITTER_CONSUMER_KEY}" \
      --consumer-secret "${TWITTER_CONSUMER_SECRET}" \
      --oauth-token "${TWITTER_OAUTH_TOKEN}" \
      --oauth-secret "${TWITTER_OAUTH_SECRET}" \
      --post-id "${TWEET_ID}"

Upload a Video
--------------

**New format**::

    agoras x video \
      --consumer-key "${TWITTER_CONSUMER_KEY}" \
      --consumer-secret "${TWITTER_CONSUMER_SECRET}" \
      --oauth-token "${TWITTER_OAUTH_TOKEN}" \
      --oauth-secret "${TWITTER_OAUTH_SECRET}" \
      --video-url "${VIDEO_URL}" \
      --video-title "${VIDEO_TITLE}"



Feed Automation
---------------

Publish the last URL from an RSS feed to X::

    agoras utils feed-publish \
      --network x \
      --mode last \
      --feed-url "${FEED_URL}" \
      --max-count "${MAX_COUNT}" \
      --post-lookback "${POST_LOOKBACK}" \
      --x-consumer-key "${TWITTER_CONSUMER_KEY}" \
      --x-consumer-secret "${TWITTER_CONSUMER_SECRET}" \
      --x-oauth-token "${TWITTER_OAUTH_TOKEN}" \
      --x-oauth-secret "${TWITTER_OAUTH_SECRET}"

.. note::
   The ``--network twitter`` and ``--twitter-*`` parameters are deprecated. Use ``--network x`` and ``--x-*`` parameters instead.

See :doc:`RSS feed section <rss>` for more details on feed automation.



Post a random URL from an RSS feed into X
------------------------------------------

This command will parse an RSS feed at ``--feed-url`` and publish one random entry that's not older than ``--max-post-age``. The post content will consist of the title and the link of the feed entry. The post will be published using the X account thats authorized by the provided credentials (read about how to get credentials :doc:`here <credentials/x>`).

Please read about how the RSS feed should be structured in the :doc:`RSS feed section <rss>`. This ensures that the feed is correctly parsed and that the post content is properly formatted.
::

      agoras publish \
            --network "x" \
            --action "random-from-feed" \
            --twitter-consumer-key "${TWITTER_CONSUMER_KEY}" \
            --twitter-consumer-secret "${TWITTER_CONSUMER_SECRET}" \
            --twitter-oauth-token "${TWITTER_OAUTH_TOKEN}" \
            --twitter-oauth-secret "${TWITTER_OAUTH_SECRET}" \
            --feed-url "${FEED_URL}" \
            --max-post-age "${MAX_POST_AGE}"



Schedule an X post
------------------

This command will scan a sheet ``--google-sheets-name`` of a google spreadsheet of id ``--google-sheets-id``, thats authorized by ``--google-sheets-client-email`` and ``--google-sheets-private-key``. The post will be published using the X account thats authorized by the provided credentials (read about how to get credentials :doc:`here <credentials/x>`).

The order of the columns of the spreadsheet is crucial to the correct functioning of the command. Here's how the information should be organized:

+--------------------+--------------------+---------------------------+---------------------------+---------------------------+---------------------------+-------------------------+-------------------+------------------------------+
| ``--status-text``  | ``--status-link``  | ``--status-image-url-1``  | ``--status-image-url-2``  | ``--status-image-url-3``  | ``--status-image-url-4``  | date (%d-%m-%Y format)  | time (%H format)  | status (draft or published)  |
+--------------------+--------------------+---------------------------+---------------------------+---------------------------+---------------------------+-------------------------+-------------------+------------------------------+

As you can see, the first 6 columns correspond to the parameters of the "post" command, the date and time columns correspond to the specific time that you want to publish this post, and the status column tells the script if this post is ready to be published (draft status) or if it was already published and should be skipped (published status). Let's see an example of a working schedule:

+-------------------------------+-------------------------------------------+---------------------------------------------------------+---------------------------------------------------------+---------------------------------------------------------+---------------------------------------------------------+-------------+-----+--------+
| This is a test facebook post  | https://agoras.readthedocs.io/en/latest/  | https://pbs.twimg.com/media/Ej3d42zXsAEfDCr?format=jpg  | https://pbs.twimg.com/media/Ej3d42zXsAEfDCr?format=jpg  | https://pbs.twimg.com/media/Ej3d42zXsAEfDCr?format=jpg  | https://pbs.twimg.com/media/Ej3d42zXsAEfDCr?format=jpg  | 21-11-2022  | 17  | draft  |
+-------------------------------+-------------------------------------------+---------------------------------------------------------+---------------------------------------------------------+---------------------------------------------------------+---------------------------------------------------------+-------------+-----+--------+

This schedule entry would be published at 17:00h of 21-11-2022 with text "This is a test X post" and 4 images pointed by those URLs.

For this command to work, it should be executed hourly by a cron script.

::

      agoras publish \
            --network "x" \
            --action "schedule" \
            --twitter-consumer-key "${TWITTER_CONSUMER_KEY}" \
            --twitter-consumer-secret "${TWITTER_CONSUMER_SECRET}" \
            --twitter-oauth-token "${TWITTER_OAUTH_TOKEN}" \
            --twitter-oauth-secret "${TWITTER_OAUTH_SECRET}" \
            --google-sheets-id "${GOOGLE_SHEETS_ID}" \
            --google-sheets-name "${GOOGLE_SHEETS_NAME}" \
            --google-sheets-client-email "${GOOGLE_SHEETS_CLIENT_EMAIL}" \
            --google-sheets-private-key "${GOOGLE_SHEETS_PRIVATE_KEY}"


.. _how-to-get-twitter-post-id:

How to get ``--tweet-id`` parameter
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Extracting from X website
-------------------------

The tweet ID parameter is necessary to delete tweets. You can extract it from the tweet URL::

      https://twitter.com/XXXXX/status/NNNNNNNNNNN

``NNNNNNNNNNN`` is the tweet ID.

Using Agoras
------------

When you create an X post with Agoras, it will print the post ID (in json format) in the console. You can copy it from there and use it in other commands. For example::

      $ agoras x post \
            --consumer-key XXXXX \
            --consumer-secret XXXXX \
            --oauth-token XXXXX \
            --oauth-secret XXXXX \
            --text "This is a test post"
      $ {"id":"NNNNNNNNNNN"}

``NNNNNNNNNNN`` is the post ID.
