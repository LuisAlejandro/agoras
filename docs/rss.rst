RSS Feed Automation
===================

.. note::
   **New in version 2.0**: Feed automation now uses ``agoras utils feed-publish`` command.
   See the :doc:`migration guide <migration>` for upgrading from ``agoras publish --action last-from-feed``.

Agoras can automatically publish content from RSS/Atom feeds to any supported social network. This is useful for automatically sharing blog posts, news articles, or other syndicated content.

Feed Format
-----------

Every item of the feed should have the following structure::

      <item>
            <title>
            <![CDATA[ Nuevo blog ]]>
            </title>
            <link>https://luisalejandro.org/blog/posts/nuevo-blog</link>
            <guid>https://luisalejandro.org/blog/posts/nuevo-blog</guid>
            <pubDate>Fri, 18 Aug 2023 23:56:51 GMT</pubDate>
            <enclosure url="https://cdn.cosmicjs.com/ea592bb0-3eb1-11ee-82b2-d53af1858037-Untitled.png" length="0" type="image/png"/>
      </item>

* The ``<title>`` of the item becomes the text content of the post
* The ``<link>`` or ``<guid>`` becomes the URL in the post
* The ``<pubDate>`` determines if the post is new
* The ``<enclosure>`` provides the image for the post

Using Feed Automation
---------------------

Publish Last Entry
~~~~~~~~~~~~~~~~~~

Publish the most recent entry from an RSS feed::

    agoras utils feed-publish \
      --network x \
      --mode last \
      --feed-url "https://blog.example.com/feed.xml" \
      --max-count 1 \
      --post-lookback 3600 \
      --x-consumer-key "${TWITTER_CONSUMER_KEY}" \
      --x-consumer-secret "${TWITTER_CONSUMER_SECRET}" \
      --x-oauth-token "${TWITTER_OAUTH_TOKEN}" \
      --x-oauth-secret "${TWITTER_OAUTH_SECRET}"

.. note::
   The ``--network twitter`` and ``--twitter-*`` parameters are deprecated. Use ``--network x`` and ``--x-*`` parameters instead.

Publish Random Entry
~~~~~~~~~~~~~~~~~~~~

Publish a random entry from an RSS feed::

    agoras utils feed-publish \
      --network facebook \
      --mode random \
      --feed-url "https://blog.example.com/feed.xml" \
      --facebook-access-token "${FACEBOOK_ACCESS_TOKEN}" \
      --facebook-object-id "${FACEBOOK_PAGE_ID}"

Feed Options
------------

* ``--network`` - Target social network (required)
* ``--mode`` - Selection mode: ``last`` or ``random`` (required)
* ``--feed-url`` - URL of the RSS/Atom feed (required)
* ``--max-count`` - Maximum number of posts to publish at once (default: 1)
* ``--post-lookback`` - Only publish posts from the last N seconds
* ``--max-post-age`` - Don't publish posts older than N days

Examples for All Platforms
---------------------------

X (formerly Twitter)::

    agoras utils feed-publish --network x --mode last \
      --feed-url "https://example.com/feed.xml" \
      --x-consumer-key "$KEY" \
      --x-consumer-secret "$SECRET" \
      --x-oauth-token "$TOKEN" \
      --x-oauth-secret "$OAUTH_SECRET"

.. deprecated:: 2.0
   The ``--network twitter`` and ``--twitter-*`` parameters are deprecated. Use ``--network x`` and ``--x-*`` parameters instead.

Facebook::

    agoras utils feed-publish --network facebook --mode last \
      --feed-url "https://example.com/feed.xml" \
      --facebook-access-token "$TOKEN" \
      --facebook-object-id "$PAGE_ID"

Instagram::

    agoras utils feed-publish --network instagram --mode random \
      --feed-url "https://example.com/feed.xml" \
      --instagram-access-token "$TOKEN" \
      --instagram-object-id "$ACCOUNT_ID"

LinkedIn::

    agoras utils feed-publish --network linkedin --mode last \
      --feed-url "https://example.com/feed.xml" \
      --linkedin-client-id "$CLIENT_ID" \
      --linkedin-client-secret "$CLIENT_SECRET"

Discord::

    agoras utils feed-publish --network discord --mode last \
      --feed-url "https://example.com/feed.xml" \
      --discord-bot-token "$BOT_TOKEN" \
      --discord-server-name "MyServer" \
      --discord-channel-name "announcements"

Telegram::

    agoras utils feed-publish --network telegram --mode last \
      --feed-url "https://example.com/feed.xml" \
      --telegram-bot-token "$TOKEN" \
      --telegram-chat-id "$CHAT_ID"

WhatsApp::

    agoras utils feed-publish --network whatsapp --mode last \
      --feed-url "https://example.com/feed.xml" \
      --whatsapp-access-token "$TOKEN" \
      --whatsapp-phone-number-id "$PHONE_NUMBER_ID" \
      --whatsapp-recipient "+1234567890"

YouTube::

    agoras utils feed-publish --network youtube --mode last \
      --feed-url "https://example.com/feed.xml" \
      --youtube-client-id "$CLIENT_ID" \
      --youtube-client-secret "$CLIENT_SECRET"

TikTok::

    agoras utils feed-publish --network tiktok --mode last \
      --feed-url "https://example.com/feed.xml" \
      --tiktok-client-key "$KEY" \
      --tiktok-client-secret "$SECRET" \
      --tiktok-access-token "$TOKEN"

Threads::

    agoras utils feed-publish --network threads --mode last \
      --feed-url "https://example.com/feed.xml" \
      --threads-app-id "$APP_ID" \
      --threads-app-secret "$APP_SECRET" \
      --threads-refresh-token "$TOKEN"

Legacy Format (Deprecated)
---------------------------

.. warning::
   The legacy ``agoras publish --action last-from-feed`` format is deprecated.
   Use ``agoras utils feed-publish`` instead.

Legacy format::

    agoras publish --network x --action last-from-feed \
      --feed-url "https://example.com/feed.xml" \
      --twitter-consumer-key "$KEY"

.. note::
   The ``--network twitter`` parameter is deprecated. Use ``--network x`` instead.

See the :doc:`migration guide <migration>` for more details.
