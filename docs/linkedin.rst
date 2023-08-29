Usage for LinkedIn
==================

How to get ``--linkedin-post-id`` parameter
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The LinkedIn post ID parameter is necessary to like, share and delete posts. You can extract it from the post URL::

      https://www.linkedin.com/feed/update/urn:li:activity:NNNNNNNNNNN

"NNNNNNNNNNN" is the post ID.

How to get google spreadsheets credentials
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

We'll need a google spreadsheet for the schedule action. Read how to create one and obtain credentials :doc:`here <credentials/google>`.

Actions
~~~~~~~

Publish a LinkedIn post
-----------------------

This command will publish a post on the account identified by ``--linkedin-username`` and ``--linkedin-password``. ``--status-text`` is the text of your post and can contain URLs that are going to be formatted into clickable links. A instagram post can have a maximum of 3000 characters, so be careful not to exceed it. You can also add up to 4 images in your post using ``--status-image-url-1``, ``--status-image-url-2``, ``--status-image-url-3`` and ``--status-image-url-4``, which must be URLs that point to downloadable images.
::

      agoras publish \
            --network "linkedin" \
            --action "post" \
            --linkedin-username "${LINKEDIN_USERNAME}" \
            --linkedin-password "${LINKEDIN_PASSWORD}" \
            --status-text "${STATUS_TEXT}" \
            --status-image-url-1 "${STATUS_IMAGE_URL_1}" \
            --status-image-url-2 "${STATUS_IMAGE_URL_2}" \
            --status-image-url-3 "${STATUS_IMAGE_URL_3}" \
            --status-image-url-4 "${STATUS_IMAGE_URL_4}"



Like a LinkedIn post
--------------------

This command will "like" a post identified by ``--linkedin-post-id`` with your account identified by ``--linkedin-username`` and ``--linkedin-password``.
::

      agoras publish \
            --network "linkedin" \
            --action "like" \
            --linkedin-username "${LINKEDIN_USERNAME}" \
            --linkedin-password "${LINKEDIN_PASSWORD}" \
            --linkedin-post-id "${LINKEDIN_POST_ID}"



Share a LinkedIn post
---------------------

This command will grab a post identified by ``--linkedin-post-id`` and share it with your account identified by ``--linkedin-username`` and ``--linkedin-password``.
::

      agoras publish \
            --network "linkedin" \
            --action "share" \
            --linkedin-username "${LINKEDIN_USERNAME}" \
            --linkedin-password "${LINKEDIN_PASSWORD}" \
            --linkedin-post-id "${LINKEDIN_POST_ID}"



Delete a LinkedIn post
----------------------

This command will delete a post identified by ``--linkedin-post-id`` with your account identified by ``--linkedin-username`` and ``--linkedin-password``.
::

      agoras publish \
            --network "linkedin" \
            --action "delete" \
            --linkedin-username "${LINKEDIN_USERNAME}" \
            --linkedin-password "${LINKEDIN_PASSWORD}" \
            --linkedin-post-id "${LINKEDIN_POST_ID}"



Post the last URL from an RSS feed into LinkedIn
-------------------------------------------------

This command will parse an RSS feed located at ``--feed-url``, and publish the last ``--max-count`` number of entries published in the last ``--post-lookback`` number of seconds. The post content will consist of the title and the link of the feed entry. The post will be published with your account identified by ``--linkedin-username`` and ``--linkedin-password``.

Please read about how the RSS feed should be structured in the :doc:`RSS feed section <rss>`. This ensures that the feed is correctly parsed and that the post content is properly formatted.
::

      agoras publish \
            --network "linkedin" \
            --action "last-from-feed" \
            --linkedin-username "${LINKEDIN_USERNAME}" \
            --linkedin-password "${LINKEDIN_PASSWORD}" \
            --feed-url "${FEED_URL}" \
            --max-count "${MAX_COUNT}" \
            --post-lookback "${POST_LOOKBACK}"



Post a random URL from an RSS feed into LinkedIn
-------------------------------------------------

This command will parse an RSS feed at ``--feed-url`` and publish one random entry that's not older than ``--max-post-age``. The post content will consist of the title and the link of the feed entry. The post will be published with your account identified by ``--linkedin-username`` and ``--linkedin-password``.

Please read about how the RSS feed should be structured in the :doc:`RSS feed section <rss>`. This ensures that the feed is correctly parsed and that the post content is properly formatted.
::

      agoras publish \
            --network "linkedin" \
            --action "random-from-feed" \
            --linkedin-username "${LINKEDIN_USERNAME}" \
            --linkedin-password "${LINKEDIN_PASSWORD}" \
            --feed-url "${FEED_URL}" \
            --max-post-age "${MAX_POST_AGE}"



Schedule a LinkedIn post
------------------------

This command will scan a sheet ``--google-sheets-name`` of a google spreadsheet of id ``--google-sheets-id``, thats authorized by ``--google-sheets-client-email`` and ``--google-sheets-private-key``. The post will be published with your account identified by ``--linkedin-username`` and ``--linkedin-password``.

The order of the columns of the spreadsheet is crucial to the correct functioning of the command. Here's how the information should be organized:

+--------------------+---------------------------+---------------------------+---------------------------+---------------------------+-------------------------+-------------------+------------------------------+
| ``--status-text``  | ``--status-image-url-1``  | ``--status-image-url-2``  | ``--status-image-url-3``  | ``--status-image-url-4``  | date (%d-%m-%Y format)  | time (%H format)  | status (draft or published)  |
+--------------------+---------------------------+---------------------------+---------------------------+---------------------------+-------------------------+-------------------+------------------------------+

As you can see, the first 5 columns correspond to the parameters of the "post" command, the date and time columns correspond to the specific time that you want to publish this post, and the status column tells the script if this post is ready to be published (draft status) or if it was already published and should be skipped (published status). Let's see an example of a working schedule:

+-------------------------------+---------------------------------------------------------+---------------------------------------------------------+---------------------------------------------------------+---------------------------------------------------------+-------------+-----+--------+
| This is a test linkedin post  | https://pbs.twimg.com/media/Ej3d42zXsAEfDCr?format=jpg  | https://pbs.twimg.com/media/Ej3d42zXsAEfDCr?format=jpg  | https://pbs.twimg.com/media/Ej3d42zXsAEfDCr?format=jpg  | https://pbs.twimg.com/media/Ej3d42zXsAEfDCr?format=jpg  | 21-11-2022  | 17  | draft  |
+-------------------------------+---------------------------------------------------------+---------------------------------------------------------+---------------------------------------------------------+---------------------------------------------------------+-------------+-----+--------+

This schedule entry would be published at 17:00h of 21-11-2022 with text "This is a test linkedin post" and 4 images pointed by those URLs.

For this command to work, it should be executed hourly by a cron script.
::

      agoras publish \
            --network "linkedin" \
            --action "schedule" \
            --linkedin-username "${LINKEDIN_USERNAME}" \
            --linkedin-password "${LINKEDIN_PASSWORD}" \
            --google-sheets-id "${GOOGLE_SHEETS_ID}" \
            --google-sheets-name "${GOOGLE_SHEETS_NAME}" \
            --google-sheets-client-email "${GOOGLE_SHEETS_CLIENT_EMAIL}" \
            --google-sheets-private-key "${GOOGLE_SHEETS_PRIVATE_KEY}"

