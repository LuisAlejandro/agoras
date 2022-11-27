



Publish a LinkedIn post
======================

::
  
python -m agoras.cli publish \
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
===================

::
  
python -m agoras.cli publish \
      --network "linkedin" \
      --action "like" \
      --linkedin-username "${LINKEDIN_USERNAME}" \
      --linkedin-password "${LINKEDIN_PASSWORD}" \
      --linkedin-post-id "${LINKEDIN_POST_ID}"



Share a LinkedIn post
====================

::
  
python -m agoras.cli publish \
      --network "linkedin" \
      --action "share" \
      --linkedin-username "${LINKEDIN_USERNAME}" \
      --linkedin-password "${LINKEDIN_PASSWORD}" \
      --linkedin-post-id "${LINKEDIN_POST_ID}"



Delete a LinkedIn post
=====================

::
  
python -m agoras.cli publish \
      --network "linkedin" \
      --action "delete" \
      --linkedin-username "${LINKEDIN_USERNAME}" \
      --linkedin-password "${LINKEDIN_PASSWORD}" \
      --linkedin-post-id "${LINKEDIN_POST_ID}"



Post the last URL from an atom feed into LinkedIn
================================================

::
  
python -m agoras.cli publish \
      --network "linkedin" \
      --action "last-from-feed" \
      --linkedin-username "${LINKEDIN_USERNAME}" \
      --linkedin-password "${LINKEDIN_PASSWORD}" \
      --feed-url "${FEED_URL}"



Post a random URL from an atom feed into LinkedIn
================================================

::
  
python -m agoras.cli publish \
      --network "linkedin" \
      --action "random-from-feed" \
      --linkedin-username "${LINKEDIN_USERNAME}" \
      --linkedin-password "${LINKEDIN_PASSWORD}" \
      --feed-url "${FEED_URL}"



Schedule a LinkedIn post
=======================

::
  
python -m agoras.cli publish \
      --network "linkedin" \
      --action "schedule" \
      --linkedin-username "${LINKEDIN_USERNAME}" \
      --linkedin-password "${LINKEDIN_PASSWORD}" \
      --google-sheets-id "${GOOGLE_SHEETS_ID}" \
      --google-sheets-name "${GOOGLE_SHEETS_NAME}" \
      --google-sheets-client-email "${GOOGLE_SHEETS_CLIENT_EMAIL}" \
      --google-sheets-private-key "${GOOGLE_SHEETS_PRIVATE_KEY}"

