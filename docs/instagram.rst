



Publish a Facebook post
======================

::
  
python -m agoras.cli publish \
      --network "instagram" \
      --action "post" \
      --instagram-access-token "${INSTAGRAM_ACCESS_TOKEN}" \
      --instagram-object-id "${INSTAGRAM_OBJECT_ID}" \
      --status-text "${STATUS_TEXT}" \
      --status-image-url-1 "${STATUS_IMAGE_URL_1}" \
      --status-image-url-2 "${STATUS_IMAGE_URL_2}" \
      --status-image-url-3 "${STATUS_IMAGE_URL_3}" \
      --status-image-url-4 "${STATUS_IMAGE_URL_4}"



Like a Facebook post
===================

::
  
python -m agoras.cli publish \
      --network "instagram" \
      --action "like" \
      --instagram-access-token "${INSTAGRAM_ACCESS_TOKEN}" \
      --instagram-object-id "${INSTAGRAM_OBJECT_ID}" \
      --instagram-post-id "${INSTAGRAM_POST_ID}"



Share a Facebook post
====================

::
  
python -m agoras.cli publish \
      --network "instagram" \
      --action "share" \
      --instagram-access-token "${INSTAGRAM_ACCESS_TOKEN}" \
      --instagram-profile-id "${INSTAGRAM_PROFILE_ID}" \
      --instagram-object-id "${INSTAGRAM_OBJECT_ID}" \
      --instagram-post-id "${INSTAGRAM_POST_ID}"



Delete a Facebook post
=====================

::
  
python -m agoras.cli publish \
      --network "instagram" \
      --action "delete" \
      --instagram-access-token "${INSTAGRAM_ACCESS_TOKEN}" \
      --instagram-object-id "${INSTAGRAM_OBJECT_ID}" \
      --instagram-post-id "${INSTAGRAM_POST_ID}"



Post the last URL from an atom feed into Facebook
================================================

::
  
python -m agoras.cli publish \
      --network "instagram" \
      --action "last-from-feed" \
      --instagram-access-token "${INSTAGRAM_ACCESS_TOKEN}" \
      --instagram-object-id "${INSTAGRAM_OBJECT_ID}" \
      --feed-url "${FEED_URL}"



Post a random URL from an atom feed into Facebook
================================================

::
  
python -m agoras.cli publish \
      --network "instagram" \
      --action "random-from-feed" \
      --instagram-access-token "${INSTAGRAM_ACCESS_TOKEN}" \
      --instagram-object-id "${INSTAGRAM_OBJECT_ID}" \
      --feed-url "${FEED_URL}"



Schedule a Facebook post
=======================

::
  
python -m agoras.cli publish \
      --network "instagram" \
      --action "schedule" \
      --instagram-access-token "${INSTAGRAM_ACCESS_TOKEN}" \
      --instagram-object-id "${INSTAGRAM_OBJECT_ID}" \
      --google-sheets-id "${GOOGLE_SHEETS_ID}" \
      --google-sheets-name "${GOOGLE_SHEETS_NAME}" \
      --google-sheets-client-email "${GOOGLE_SHEETS_CLIENT_EMAIL}" \
      --google-sheets-private-key "${GOOGLE_SHEETS_PRIVATE_KEY}"

