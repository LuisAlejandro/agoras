RSS feed format
===============

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

* The ``<title>`` of the item is going to be the text content of the post.
* The ``<link>`` or ``<guid>`` of the item is going to be the url of the post.
* The ``<pubDate>`` of the item is going to be used to determine if the post is new or not.
* The ``<enclosure>`` of the item is going to be used to include the image of the post.