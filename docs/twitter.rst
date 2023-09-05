Usage for Twitter
=================

Twitter is a social network that allows you to publish short messages (called tweets) of up to 280 characters. Agoras makes use of a popular `twitter API client <https://github.com/tweepy/tweepy>`_ to publish and delete tweets, tweet the last URL from an RSS feed, tweet a random URL from an RSS feed and schedule a tweet (using a google spreadsheet).

**Important**: Twitter now requires a paid subscription for certain parts of the API. The free tier will let you publish and delete twitter posts, but will not allow likes or retweets. For that reason, we've deprecated the ``--action like`` and ``--action share`` commands.

Actions
~~~~~~~

Publish a Twitter post
----------------------

This command will publish a post on the account thats authorized by the provided credentials (read about how to get credentials :doc:`here <credentials/twitter>`). ``--status-text`` is the text of your post and can contain URLs that are going to be formatted into clickable links. A twitter post can have a maximum of 280 characters, so be careful not to exceed it. You can also add up to 4 images in your post using ``--status-image-url-1``, ``--status-image-url-2``, ``--status-image-url-3`` and ``--status-image-url-4``, which must be URLs that point to downloadable images.
::

      agoras publish \
            --network "twitter" \
            --action "post" \
            --twitter-consumer-key "${TWITTER_CONSUMER_KEY}" \
            --twitter-consumer-secret "${TWITTER_CONSUMER_SECRET}" \
            --twitter-oauth-token "${TWITTER_OAUTH_TOKEN}" \
            --twitter-oauth-secret "${TWITTER_OAUTH_SECRET}" \
            --status-text "${STATUS_TEXT}" \
            --status-image-url-1 "${STATUS_IMAGE_URL_1}" \
            --status-image-url-2 "${STATUS_IMAGE_URL_2}" \
            --status-image-url-3 "${STATUS_IMAGE_URL_3}" \
            --status-image-url-4 "${STATUS_IMAGE_URL_4}"



Like a Twitter post
-------------------

Action not supported by Agoras.


Share a Twitter post
--------------------

Action not supported by Agoras.


Delete a Twitter post
---------------------

This command will delete a post identified by ``--tweet-id`` (read about how to get the id of a post :ref:`here <how-to-get-twitter-post-id>`) using the twitter account thats authorized by the provided credentials (read about how to get credentials :doc:`here <credentials/twitter>`). The tweet must have been posted by the same account that is deleting it.
::

      agoras publish \
            --network "twitter" \
            --action "delete" \
            --twitter-consumer-key "${TWITTER_CONSUMER_KEY}" \
            --twitter-consumer-secret "${TWITTER_CONSUMER_SECRET}" \
            --twitter-oauth-token "${TWITTER_OAUTH_TOKEN}" \
            --twitter-oauth-secret "${TWITTER_OAUTH_SECRET}" \
            --tweet-id "${TWEET_ID}"



Post the last URL from an RSS feed into Twitter
------------------------------------------------

This command will parse an RSS feed located at ``--feed-url``, and publish the last ``--max-count`` number of entries published in the last ``--post-lookback`` number of seconds. The post content will consist of the title and the link of the feed entry. The post will be published using the twitter account thats authorized by the provided credentials (read about how to get credentials :doc:`here <credentials/twitter>`).

Please read about how the RSS feed should be structured in the :doc:`RSS feed section <rss>`. This ensures that the feed is correctly parsed and that the post content is properly formatted.
::

      agoras publish \
            --network "twitter" \
            --action "last-from-feed" \
            --twitter-consumer-key "${TWITTER_CONSUMER_KEY}" \
            --twitter-consumer-secret "${TWITTER_CONSUMER_SECRET}" \
            --twitter-oauth-token "${TWITTER_OAUTH_TOKEN}" \
            --twitter-oauth-secret "${TWITTER_OAUTH_SECRET}" \
            --feed-url "${FEED_URL}" \
            --max-count "${MAX_COUNT}" \
            --post-lookback "${POST_LOOKBACK}"



Post a random URL from an RSS feed into Twitter
------------------------------------------------

This command will parse an RSS feed at ``--feed-url`` and publish one random entry that's not older than ``--max-post-age``. The post content will consist of the title and the link of the feed entry. The post will be published using the twitter account thats authorized by the provided credentials (read about how to get credentials :doc:`here <credentials/twitter>`).

Please read about how the RSS feed should be structured in the :doc:`RSS feed section <rss>`. This ensures that the feed is correctly parsed and that the post content is properly formatted.
::

      agoras publish \
            --network "twitter" \
            --action "random-from-feed" \
            --twitter-consumer-key "${TWITTER_CONSUMER_KEY}" \
            --twitter-consumer-secret "${TWITTER_CONSUMER_SECRET}" \
            --twitter-oauth-token "${TWITTER_OAUTH_TOKEN}" \
            --twitter-oauth-secret "${TWITTER_OAUTH_SECRET}" \
            --feed-url "${FEED_URL}" \
            --max-post-age "${MAX_POST_AGE}"



Schedule a Twitter post
-----------------------

This command will scan a sheet ``--google-sheets-name`` of a google spreadsheet of id ``--google-sheets-id``, thats authorized by ``--google-sheets-client-email`` and ``--google-sheets-private-key``. The post will be published using the twitter account thats authorized by the provided credentials (read about how to get credentials :doc:`here <credentials/twitter>`).

The order of the columns of the spreadsheet is crucial to the correct functioning of the command. Here's how the information should be organized:

+--------------------+--------------------+---------------------------+---------------------------+---------------------------+---------------------------+-------------------------+-------------------+------------------------------+
| ``--status-text``  | ``--status-link``  | ``--status-image-url-1``  | ``--status-image-url-2``  | ``--status-image-url-3``  | ``--status-image-url-4``  | date (%d-%m-%Y format)  | time (%H format)  | status (draft or published)  |
+--------------------+--------------------+---------------------------+---------------------------+---------------------------+---------------------------+-------------------------+-------------------+------------------------------+

As you can see, the first 6 columns correspond to the parameters of the "post" command, the date and time columns correspond to the specific time that you want to publish this post, and the status column tells the script if this post is ready to be published (draft status) or if it was already published and should be skipped (published status). Let's see an example of a working schedule:

+-------------------------------+-------------------------------------------+---------------------------------------------------------+---------------------------------------------------------+---------------------------------------------------------+---------------------------------------------------------+-------------+-----+--------+
| This is a test facebook post  | https://agoras.readthedocs.io/en/latest/  | https://pbs.twimg.com/media/Ej3d42zXsAEfDCr?format=jpg  | https://pbs.twimg.com/media/Ej3d42zXsAEfDCr?format=jpg  | https://pbs.twimg.com/media/Ej3d42zXsAEfDCr?format=jpg  | https://pbs.twimg.com/media/Ej3d42zXsAEfDCr?format=jpg  | 21-11-2022  | 17  | draft  |
+-------------------------------+-------------------------------------------+---------------------------------------------------------+---------------------------------------------------------+---------------------------------------------------------+---------------------------------------------------------+-------------+-----+--------+

This schedule entry would be published at 17:00h of 21-11-2022 with text "This is a test twitter post" and 4 images pointed by those URLs.

For this command to work, it should be executed hourly by a cron script.

::

      agoras publish \
            --network "twitter" \
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

Extracting from Twitter website
--------------------------------

The tweet ID parameter is necessary to delete tweets. You can extract it from the tweet URL::

      https://twitter.com/XXXXX/status/NNNNNNNNNNN

``NNNNNNNNNNN`` is the tweet ID.

Using Agoras
------------

When you create a twitter post with Agoras, it will print the post ID (in json format) in the console. You can copy it from there and use it in other commands. For example::

      $ agoras publish \
            --network twitter \
            --action post \
            --twitter-consumer-key XXXXX \
            --twitter-consumer-secret XXXXX \
            --twitter-oauth-token XXXXX \
            --twitter-oauth-secret XXXXX \
            --status-text "This is a test post"
      $ {"id":"NNNNNNNNNNN"}

``NNNNNNNNNNN`` is the post ID.
