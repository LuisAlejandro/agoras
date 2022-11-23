



Like a Facebook post
===================

::
  
python -m agoras.cli publish \
      --network "facebook" \
      --action "like" \
      --facebook-access-token "${FACEBOOK_ACCESS_TOKEN}" \
      --facebook-object-id "${FACEBOOK_OBJECT_ID}" \
      --facebook-post-id "${FACEBOOK_POST_ID}"



Share a Facebook post
====================

::
  
python -m agoras.cli publish \
      --network "facebook" \
      --action "share" \
      --facebook-access-token "${FACEBOOK_ACCESS_TOKEN}" \
      --facebook-profile-id "${FACEBOOK_PROFILE_ID}" \
      --facebook-object-id "${FACEBOOK_OBJECT_ID}" \
      --facebook-post-id "${FACEBOOK_POST_ID}"



Delete a Facebook post
=====================

::
  
python -m agoras.cli publish \
      --network "facebook" \
      --action "delete" \
      --facebook-access-token "${FACEBOOK_ACCESS_TOKEN}" \
      --facebook-object-id "${FACEBOOK_OBJECT_ID}" \
      --facebook-post-id "${FACEBOOK_POST_ID}"



Post the last URL from an atom feed into Facebook
================================================

::
  
python -m agoras.cli publish \
      --network "facebook" \
      --action "last-from-feed" \
      --facebook-access-token "${FACEBOOK_ACCESS_TOKEN}" \
      --facebook-object-id "${FACEBOOK_OBJECT_ID}" \
      --feed-url "${FEED_URL}"



Post a random URL from an atom feed into Facebook
================================================

::
  
python -m agoras.cli publish \
      --network "facebook" \
      --action "random-from-feed" \
      --facebook-access-token "${FACEBOOK_ACCESS_TOKEN}" \
      --facebook-object-id "${FACEBOOK_OBJECT_ID}" \
      --feed-url "${FEED_URL}"



Publish a Facebook post
======================

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



Schedule a Facebook post
=======================

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

