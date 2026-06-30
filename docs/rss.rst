RSS Feed Automation
===================

.. note::

   Feed automation uses ``agoras utils feed-publish``.
   See the :doc:`migration guide <migration/index>` for upgrading from ``agoras publish --action last-from-feed``.

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

Publish the most recent entry from an RSS feed (run ``agoras x authorize`` first, or set ``TWITTER_*`` env vars)::

    agoras utils feed-publish \
      --network x \
      --mode last \
      --feed-url "https://blog.example.com/feed.xml" \
      --max-count 1 \
      --post-lookback 3600

.. note::
   The ``--network twitter`` alias is deprecated. Use ``--network x`` instead.

Publish Random Entry
~~~~~~~~~~~~~~~~~~~~

Publish a random entry from an RSS feed::

    agoras utils feed-publish \
      --network facebook \
      --mode random \
      --feed-url "https://blog.example.com/feed.xml"

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

Run ``agoras <platform> authorize`` once (or set platform env vars), then::

    agoras utils feed-publish --network <platform> --mode last \
      --feed-url "https://example.com/feed.xml"

Replace ``<platform>`` with ``x``, ``facebook``, ``instagram``, ``linkedin``, ``discord``, ``telegram``, ``whatsapp``, ``youtube``, ``tiktok``, or ``threads``.

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

See the :doc:`migration guide <migration/index>` for more details.
