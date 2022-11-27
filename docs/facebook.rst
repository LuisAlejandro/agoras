Agoras usage for Facebook network
=================================

How to get ``--facebook-access-token`` parameter
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. _here: credentials/facebook.rst

We'll need a permanent access token with appropiate permissions to be able to use de Facebook Graph API. Read the tutorial here_.

How to get ``--facebook-object-id`` parameter
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

With Agoras you can use the facebook network to post to pages, profiles and groups, but for simplicity sake we're going to only explain how to get the object ID of a page.

To find your Page ID go to the following URL, replacing ``{page_name}`` with the pretty name of your page url. For example, in https://www.facebook.com/LuisDevelops, the ``{page_name}`` is ``LuisDevelops``.::

      https://developers.facebook.com/tools/explorer/?method=GET&path={page_name}

Then click on submit and you'll see a response like this::

      {
            "name": "Luis Develops",
            "id": "ZZZZZZZ"
      }

"ZZZZZZZ" is your page ID.

.. image:: credentials/images/facebook-6.png

Publish a Facebook post
-----------------------

::
  
python -m agoras.cli publish \
      --network "facebook" \
      --action "post" \
      --facebook-access-token "${FACEBOOK_ACCESS_TOKEN}" \
      --facebook-object-id "${FACEBOOK_OBJECT_ID}" \
      --status-text "${STATUS_TEXT}" \
      --status-image-url-1 "${STATUS_IMAGE_URL_1}" \
      --status-image-url-2 "${STATUS_IMAGE_URL_2}" \
      --status-image-url-3 "${STATUS_IMAGE_URL_3}" \
      --status-image-url-4 "${STATUS_IMAGE_URL_4}"



Like a Facebook post
--------------------

::
  
python -m agoras.cli publish \
      --network "facebook" \
      --action "like" \
      --facebook-access-token "${FACEBOOK_ACCESS_TOKEN}" \
      --facebook-object-id "${FACEBOOK_OBJECT_ID}" \
      --facebook-post-id "${FACEBOOK_POST_ID}"



Share a Facebook post
---------------------

::
  
python -m agoras.cli publish \
      --network "facebook" \
      --action "share" \
      --facebook-access-token "${FACEBOOK_ACCESS_TOKEN}" \
      --facebook-profile-id "${FACEBOOK_PROFILE_ID}" \
      --facebook-object-id "${FACEBOOK_OBJECT_ID}" \
      --facebook-post-id "${FACEBOOK_POST_ID}"



Delete a Facebook post
----------------------

::
  
python -m agoras.cli publish \
      --network "facebook" \
      --action "delete" \
      --facebook-access-token "${FACEBOOK_ACCESS_TOKEN}" \
      --facebook-object-id "${FACEBOOK_OBJECT_ID}" \
      --facebook-post-id "${FACEBOOK_POST_ID}"



Post the last URL from an atom feed into Facebook
-------------------------------------------------

::
  
python -m agoras.cli publish \
      --network "facebook" \
      --action "last-from-feed" \
      --facebook-access-token "${FACEBOOK_ACCESS_TOKEN}" \
      --facebook-object-id "${FACEBOOK_OBJECT_ID}" \
      --feed-url "${FEED_URL}"



Post a random URL from an atom feed into Facebook
-------------------------------------------------

::
  
python -m agoras.cli publish \
      --network "facebook" \
      --action "random-from-feed" \
      --facebook-access-token "${FACEBOOK_ACCESS_TOKEN}" \
      --facebook-object-id "${FACEBOOK_OBJECT_ID}" \
      --feed-url "${FEED_URL}"



Schedule a Facebook post
------------------------

::
  
python -m agoras.cli publish \
      --network "facebook" \
      --action "schedule" \
      --facebook-access-token "${FACEBOOK_ACCESS_TOKEN}" \
      --facebook-object-id "${FACEBOOK_OBJECT_ID}" \
      --google-sheets-id "${GOOGLE_SHEETS_ID}" \
      --google-sheets-name "${GOOGLE_SHEETS_NAME}" \
      --google-sheets-client-email "${GOOGLE_SHEETS_CLIENT_EMAIL}" \
      --google-sheets-private-key "${GOOGLE_SHEETS_PRIVATE_KEY}"

