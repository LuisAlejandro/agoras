Usage for LinkedIn
==================

LinkedIn is a social network for professionals. It's a great place to share your content and to connect with other professionals. Agoras makes use of the `official LinkedIn API client <https://github.com/linkedin-developers/linkedin-api-python-client#linkedin-api-python-client>`_ to publish content on your behalf. Currently, Agoras supports the following actions: authorize, publish a post, like a post, share a post, delete a post, post the last URL from an RSS feed, post a random URL from an RSS feed and schedule a post (using a google spreadsheet).

Actions
~~~~~~~

* ``authorize`` - Set up OAuth 2.0 authentication (required first step)
* ``post`` - Create text and image posts (up to 4 images)
* ``like`` - Like posts
* ``share`` - Share posts
* ``delete`` - Delete your own posts

Authorization
-------------

.. versionadded:: 2.0
   OAuth 2.0 "authorize first" workflow

Before performing any actions, you must authorize Agoras to access your LinkedIn account::

    agoras linkedin authorize \
      --client-id "${LINKEDIN_CLIENT_ID}" \
      --client-secret "${LINKEDIN_CLIENT_SECRET}" \
      --object-id "${LINKEDIN_OBJECT_ID}"

This will:

1. Open your browser to LinkedIn's OAuth authorization page
2. Prompt you to grant permissions to Agoras
3. Automatically capture the authorization code
4. Store encrypted credentials in ``~/.agoras/tokens/``

After authorization, you can perform actions without providing tokens. Credentials are automatically refreshed when needed.

For CI/CD environments, see :doc:`credentials/linkedin` for headless authorization setup.

Publish a LinkedIn post
-----------------------

This command will publish a post on your LinkedIn account. ``--text`` is the text of your post and can contain URLs that are going to be formatted into clickable links. A LinkedIn post can have a maximum of 3000 characters, so be careful not to exceed it. You can also add up to 4 images in your post using ``--image-1``, ``--image-2``, ``--image-3`` and ``--image-4``, which must be URLs that point to downloadable images.

.. versionchanged:: 1.1.1
   Added support for ``--link`` parameter. If you want to add a link to your post, you can use this parameter. A preview of the link will be embedded in the post. If you want to add a link without a preview, you can add it to the ``--text`` parameter. Warning: if you add a link using ``--link`` and also add images using any of the ``--image-X`` parameters, the images will be ignored.

.. note::
   You must run ``agoras linkedin authorize`` first before using this command.

**New format**::

    agoras linkedin post \
      --text "${STATUS_TEXT}" \
      --link "${STATUS_LINK}" \
      --image-1 "${IMAGE_URL_1}" \
      --image-2 "${IMAGE_URL_2}" \
      --image-3 "${IMAGE_URL_3}" \
      --image-4 "${IMAGE_URL_4}"


Like a LinkedIn post
--------------------

This command will "like" a post identified by ``--post-id`` (read about how to get the id of a post :ref:`here <how-to-get-linkedin-post-id>`).

.. note::
   You must run ``agoras linkedin authorize`` first before using this command.

**New format**::

    agoras linkedin like \
      --post-id "${LINKEDIN_POST_ID}"



Share a LinkedIn post
---------------------

This command will grab a post identified by ``--post-id`` (read about how to get the id of a post :ref:`here <how-to-get-linkedin-post-id>`) and share it with your account.

.. note::
   You must run ``agoras linkedin authorize`` first before using this command.

**New format**::

    agoras linkedin share \
      --post-id "${LINKEDIN_POST_ID}"



Delete a LinkedIn post
----------------------

This command will delete a post identified by ``--post-id`` (read about how to get the id of a post :ref:`here <how-to-get-linkedin-post-id>`). Please note that you can only delete posts that you published.

.. note::
   You must run ``agoras linkedin authorize`` first before using this command.

**New format**::

    agoras linkedin delete \
      --post-id "${LINKEDIN_POST_ID}"



Post the last URL from an RSS feed into LinkedIn
-------------------------------------------------

This command will parse an RSS feed located at ``--feed-url``, and publish the last ``--max-count`` number of entries published in the last ``--post-lookback`` number of seconds. The post content will consist of the title and the link of the feed entry.

.. note::
   You must run ``agoras linkedin authorize`` first before using this command.

Please read about how the RSS feed should be structured in the :doc:`RSS feed section <rss>`. This ensures that the feed is correctly parsed and that the post content is properly formatted.
::

      agoras utils feed-publish \
            --network "linkedin" \
            --mode "last" \
            --feed-url "${FEED_URL}" \
            --max-count "${MAX_COUNT}" \
            --post-lookback "${POST_LOOKBACK}"



Post a random URL from an RSS feed into LinkedIn
-------------------------------------------------

This command will parse an RSS feed at ``--feed-url`` and publish one random entry that's not older than ``--max-post-age``. The post content will consist of the title and the link of the feed entry.

.. note::
   You must run ``agoras linkedin authorize`` first before using this command.

Please read about how the RSS feed should be structured in the :doc:`RSS feed section <rss>`. This ensures that the feed is correctly parsed and that the post content is properly formatted.
::

      agoras utils feed-publish \
            --network "linkedin" \
            --mode "random" \
            --feed-url "${FEED_URL}" \
            --max-post-age "${MAX_POST_AGE}"



Schedule a LinkedIn post
------------------------

This command will scan a sheet ``--sheets-name`` of a google spreadsheet of id ``--sheets-id``, thats authorized by ``--sheets-client-email`` and ``--sheets-private-key`` (read about how to get google credentials :doc:`here <credentials/google>`).

.. note::
   You must run ``agoras linkedin authorize`` first before using this command.

The order of the columns of the spreadsheet is crucial to the correct functioning of the command. Here's how the information should be organized:

+--------------------+--------------------+---------------------------+---------------------------+---------------------------+---------------------------+-------------------------+-------------------+------------------------------+
| ``--status-text``  | ``--status-link``  | ``--status-image-url-1``  | ``--status-image-url-2``  | ``--status-image-url-3``  | ``--status-image-url-4``  | date (%d-%m-%Y format)  | time (%H format)  | status (draft or published)  |
+--------------------+--------------------+---------------------------+---------------------------+---------------------------+---------------------------+-------------------------+-------------------+------------------------------+

As you can see, the first 6 columns correspond to the parameters of the "post" command, the date and time columns correspond to the specific time that you want to publish this post, and the status column tells the script if this post is ready to be published (draft status) or if it was already published and should be skipped (published status). Let's see an example of a working schedule:

+-------------------------------+-------------------------------------------+---------------------------------------------------------+---------------------------------------------------------+---------------------------------------------------------+---------------------------------------------------------+-------------+-----+--------+
| This is a test facebook post  | https://agoras.readthedocs.io/en/latest/  | https://pbs.twimg.com/media/Ej3d42zXsAEfDCr?format=jpg  | https://pbs.twimg.com/media/Ej3d42zXsAEfDCr?format=jpg  | https://pbs.twimg.com/media/Ej3d42zXsAEfDCr?format=jpg  | https://pbs.twimg.com/media/Ej3d42zXsAEfDCr?format=jpg  | 21-11-2022  | 17  | draft  |
+-------------------------------+-------------------------------------------+---------------------------------------------------------+---------------------------------------------------------+---------------------------------------------------------+---------------------------------------------------------+-------------+-----+--------+

This schedule entry would be published at 17:00h of 21-11-2022 with text "This is a test linkedin post" and 4 images pointed by those URLs.

For this command to work, it should be executed hourly by a cron script.
::

      agoras utils schedule-run \
            --network "linkedin" \
            --sheets-id "${GOOGLE_SHEETS_ID}" \
            --sheets-name "${GOOGLE_SHEETS_NAME}" \
            --sheets-client-email "${GOOGLE_SHEETS_CLIENT_EMAIL}" \
            --sheets-private-key "${GOOGLE_SHEETS_PRIVATE_KEY}"


.. _how-to-get-linkedin-post-id:

How to get ``--linkedin-post-id`` parameter
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The LinkedIn post ID parameter is necessary to like, share and delete posts. There are two ways to get it, one going directly to the LinkedIn website and the other using agoras. Notice that there are two forms of post IDs, one has the form ``urn:li:activity:NNNNNNNNNNN`` and the other has the form ``urn:li:share:NNNNNNNNNNN``. Both are valid and can be used in agoras.

Extracting from LinkedIn website
--------------------------------

You can extract it from the post URL::

      https://www.linkedin.com/feed/update/urn:li:activity:NNNNNNNNNNN

``urn:li:activity:NNNNNNNNNNN`` is the post ID.

Using Agoras
------------

When you create a LinkedIn post with Agoras, it will print the post ID (in json format) in the console. You can copy it from there and use it in other commands. For example::

      $ agoras linkedin post \
            --text "This is a test post"
      $ {"id":"urn:li:share:NNNNNNNNNNN"}

``urn:li:share:NNNNNNNNNNN`` is the post ID.
