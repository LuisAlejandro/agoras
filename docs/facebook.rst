Usage for Facebook
==================

.. note::
   **New in version 2.0**: Facebook commands now use the intuitive ``agoras facebook`` format.
   See the :doc:`migration guide <migration>` for upgrading from ``agoras publish``.

Facebook is a social network that allows you to share text, images and videos with your friends, family and followers. Agoras can publish posts, like posts, share posts and delete posts on Facebook by using a popular `Facebook Graph API client <https://github.com/sns-sdks/python-facebook>`_.

Available Actions
~~~~~~~~~~~~~~~~~

* ``authorize`` - Set up OAuth 2.0 authentication (required first step)
* ``post`` - Create text and image posts (up to 4 images)
* ``video`` - Upload videos
* ``like`` - Like posts
* ``share`` - Share posts to your profile
* ``delete`` - Delete your own posts

Authorization
-------------

.. versionadded:: 2.0
   OAuth 2.0 "authorize first" workflow

Before performing any actions, you must authorize Agoras to access your Facebook account::

    agoras facebook authorize \
      --client-id "${FACEBOOK_CLIENT_ID}" \
      --client-secret "${FACEBOOK_CLIENT_SECRET}" \
      --app-id "${FACEBOOK_APP_ID}" \
      --object-id "${FACEBOOK_OBJECT_ID}"

This will:

1. Open your browser to the Facebook OAuth authorization page
2. Prompt you to grant permissions to Agoras
3. Automatically capture the authorization code
4. Store encrypted credentials in ``~/.agoras/tokens/``

After authorization, you can perform actions without providing tokens. Credentials are automatically refreshed when needed.

For CI/CD environments, see :doc:`credentials/facebook` for unattended execution setup.

Post to Facebook
----------------

**New format**::

    agoras facebook post \
      --object-id "${FACEBOOK_OBJECT_ID}" \
      --text "${STATUS_TEXT}" \
      --link "${STATUS_LINK}" \
      --image-1 "${IMAGE_URL_1}" \
      --image-2 "${IMAGE_URL_2}"

.. note::
   You must run ``agoras facebook authorize`` first before using this command.

.. versionchanged:: 2.0
   Parameters simplified: ``--text`` instead of ``--status-text``, ``--image-1`` instead of ``--status-image-url-1``

.. note::
   If you add a link using ``--link`` and also add images, the images may be ignored depending on Facebook's API behavior.

Upload a Video
--------------

**New format**::

    agoras facebook video \
      --object-id "${FACEBOOK_OBJECT_ID}" \
      --video-url "${VIDEO_URL}" \
      --video-title "${VIDEO_TITLE}" \
      --video-description "${VIDEO_DESCRIPTION}"

.. note::
   You must run ``agoras facebook authorize`` first before using this command.

Like a Post
-----------

**New format**::

    agoras facebook like \
      --post-id "${FACEBOOK_POST_ID}"

.. note::
   You must run ``agoras facebook authorize`` first before using this command.

Share a Post
------------

This command will grab a post identified by ``--post-id`` that is currently published on ``--object-id`` (read about how to get the id of an account :ref:`here <how-to-get-facebook-account-id>`), and share it on a ``--profile-id``.

.. note::
   You must run ``agoras facebook authorize`` first before using this command.

**New format**::

    agoras facebook share \
      --object-id "${FACEBOOK_OBJECT_ID}" \
      --post-id "${FACEBOOK_POST_ID}" \
      --profile-id "${FACEBOOK_PROFILE_ID}"



Delete a Facebook post
----------------------

This command will delete a post identified by ``--post-id`` that is currently published on ``--object-id`` (read about how to get the id of an account :ref:`here <how-to-get-facebook-account-id>`).

.. note::
   You must run ``agoras facebook authorize`` first before using this command.

**New format**::

    agoras facebook delete \
      --object-id "${FACEBOOK_OBJECT_ID}" \
      --post-id "${FACEBOOK_POST_ID}"



Post the last URL from an RSS feed into Facebook
-------------------------------------------------

This command will parse an RSS feed located at ``--feed-url``, and publish the last ``--max-count`` number of entries published in the last ``--post-lookback`` number of seconds. The post content will consist of the title and the link of the feed entry. The post will be published on ``--facebook-object-id`` (read about how to get the id of an account :ref:`here <how-to-get-facebook-account-id>`).

.. note::
   You must run ``agoras facebook authorize`` first before using this command.

Please read about how the RSS feed should be structured in the :doc:`RSS feed section <rss>`. This ensures that the feed is correctly parsed and that the post content is properly formatted.
::

      agoras utils feed-publish \
            --network "facebook" \
            --mode "last" \
            --facebook-object-id "${FACEBOOK_OBJECT_ID}" \
            --feed-url "${FEED_URL}" \
            --max-count "${MAX_COUNT}" \
            --post-lookback "${POST_LOOKBACK}"



Post a random URL from an RSS feed into Facebook
-------------------------------------------------

This command will parse an RSS feed at ``--feed-url`` and publish one random entry that's not older than ``--max-post-age``. The post content will consist of the title and the link of the feed entry. The post will be published on ``--facebook-object-id`` (read about how to get the id of an account :ref:`here <how-to-get-facebook-account-id>`).

.. note::
   You must run ``agoras facebook authorize`` first before using this command.

Please read about how the RSS feed should be structured in the :doc:`RSS feed section <rss>`. This ensures that the feed is correctly parsed and that the post content is properly formatted.
::

      agoras utils feed-publish \
            --network "facebook" \
            --mode "random" \
            --facebook-object-id "${FACEBOOK_OBJECT_ID}" \
            --feed-url "${FEED_URL}" \
            --max-post-age "${MAX_POST_AGE}"



Schedule a Facebook post
------------------------

This command will scan a sheet ``--sheets-name`` of a google spreadsheet of id ``--sheets-id``, thats authorized by ``--sheets-client-email`` and ``--sheets-private-key``. The post will be published on ``--facebook-object-id`` (read about how to get the id of an account :ref:`here <how-to-get-facebook-account-id>`).

.. note::
   You must run ``agoras facebook authorize`` first before using this command.

The order of the columns of the spreadsheet is crucial to the correct functioning of the command. Here's how the information should be organized:

+--------------------+--------------------+---------------------------+---------------------------+---------------------------+---------------------------+-------------------------+-------------------+------------------------------+
| ``--status-text``  | ``--status-link``  | ``--status-image-url-1``  | ``--status-image-url-2``  | ``--status-image-url-3``  | ``--status-image-url-4``  | date (%d-%m-%Y format)  | time (%H format)  | status (draft or published)  |
+--------------------+--------------------+---------------------------+---------------------------+---------------------------+---------------------------+-------------------------+-------------------+------------------------------+

As you can see, the first 6 columns correspond to the parameters of the "post" command, the date and time columns correspond to the specific time that you want to publish this post, and the status column tells the script if this post is ready to be published (draft status) or if it was already published and should be skipped (published status). Let's see an example of a working schedule:

+-------------------------------+-------------------------------------------+---------------------------------------------------------+---------------------------------------------------------+---------------------------------------------------------+---------------------------------------------------------+-------------+-----+--------+
| This is a test facebook post  | https://agoras.readthedocs.io/en/latest/  | https://pbs.twimg.com/media/Ej3d42zXsAEfDCr?format=jpg  | https://pbs.twimg.com/media/Ej3d42zXsAEfDCr?format=jpg  | https://pbs.twimg.com/media/Ej3d42zXsAEfDCr?format=jpg  | https://pbs.twimg.com/media/Ej3d42zXsAEfDCr?format=jpg  | 21-11-2022  | 17  | draft  |
+-------------------------------+-------------------------------------------+---------------------------------------------------------+---------------------------------------------------------+---------------------------------------------------------+---------------------------------------------------------+-------------+-----+--------+

This schedule entry would be published at 17:00h of 21-11-2022 with text "This is a test facebook post" and 4 images pointed by those URLs.

For this command to work, it should be executed hourly by a cron script.
::

      agoras utils schedule-run \
            --network "facebook" \
            --facebook-object-id "${FACEBOOK_OBJECT_ID}" \
            --sheets-id "${GOOGLE_SHEETS_ID}" \
            --sheets-name "${GOOGLE_SHEETS_NAME}" \
            --sheets-client-email "${GOOGLE_SHEETS_CLIENT_EMAIL}" \
            --sheets-private-key "${GOOGLE_SHEETS_PRIVATE_KEY}"


.. _how-to-get-facebook-account-id:

How to get ``--facebook-object-id`` parameter
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

With Agoras you can use the facebook network to post to pages, profiles and groups, but for simplicity sake we're going to only explain how to get the object ID of a page.

To find your Page ID go to the following URL, replacing ``{page_name}`` with the pretty name of your page url. For example, in https://www.facebook.com/LuisDevelops, the ``{page_name}`` is ``LuisDevelops``. Put the URL in your browser and hit enter.
::

      https://developers.facebook.com/tools/explorer/?method=GET&path={page_name}

Then click on submit and you'll see a response like this::

      {
            "name": "Luis Develops",
            "id": "ZZZZZZZ"
      }

`ZZZZZZZ` is your page ID.

.. image:: credentials/images/facebook-6.png


.. _how-to-get-facebook-post-id:

How to get ``--facebook-post-id`` parameter
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Extracting from Facebook website
--------------------------------

The post ID parameter is necessary to like, share and delete posts. You can extract it from the post URL::

      https://www.facebook.com/XXXXX/posts/NNNNNNNNNNN

If ``NNNNNNNNNNN`` consists only of numbers, then that's the post ID. If it contains other characters, then it's not the post ID and you'll need to do an extra step.

Copy the entire post URL and paste it in the following URL, replacing ``{post_url}`` with the URL you just copied. Put the URL in your browser and hit enter.

::

      https://www.facebook.com/plugins/post.php?href={post_url}

You'll see a page like the one in the image:

.. image:: credentials/images/facebook-7.png

Click on the timestamp of the post (highlighted in red) and you'll be redirected to a page like this::

      https://www.facebook.com/XXXXX/posts/NNNNNNNNNNN

Now you can copy the post ID (``NNNNNNNNNNN``) from the URL.

Using Agoras
------------

When you create a facebook post with Agoras, it will print the post ID (in json format) in the console. You can copy it from there and use it in other commands. For example::

      $ agoras facebook post \
            --object-id XXXXX \
            --text "This is a test post"
      $ {"id":"NNNNNNNNNNN"}

``NNNNNNNNNNN`` is the post ID.
