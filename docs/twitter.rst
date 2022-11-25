



Publish a Twitter post
======================

::
  
python -m agoras.cli publish \
      --network "twitter" \
      --action "post" \
      --twitter-consumer-key "${TWITTER_CONSUMER_KEY}" \
      --twitter-consumer-secret "${TWITTER_CONSUMER_SECRET}" \
      --twitter-oauth-token "${TWITTER_OAUTH_TOKEN}" \
      --twitter-oauth-secret "${TWITTER_OAUTH_SECRET}" \
      --status-text "${STATUS_TEXT}" \
      --status-image-url-1 "${STATUS_IMAGE_URL_1}" \
      --status-image-url-2 "${STATUS_IMAGE_URL_2}" \
      --status-image-url-3 "${STATUS_IMAGE_URL_3}" \
      --status-image-url-4 "${STATUS_IMAGE_URL_4}"



Like a Twitter post
===================

::
  
python -m agoras.cli publish \
      --network "twitter" \
      --action "like" \
      --twitter-consumer-key "${TWITTER_CONSUMER_KEY}" \
      --twitter-consumer-secret "${TWITTER_CONSUMER_SECRET}" \
      --twitter-oauth-token "${TWITTER_OAUTH_TOKEN}" \
      --twitter-oauth-secret "${TWITTER_OAUTH_SECRET}" \
      --tweet-id "${TWEET_ID}"



Share a Twitter post
====================

::
  
python -m agoras.cli publish \
      --network "twitter" \
      --action "share" \
      --twitter-consumer-key "${TWITTER_CONSUMER_KEY}" \
      --twitter-consumer-secret "${TWITTER_CONSUMER_SECRET}" \
      --twitter-oauth-token "${TWITTER_OAUTH_TOKEN}" \
      --twitter-oauth-secret "${TWITTER_OAUTH_SECRET}" \
      --tweet-id "${TWEET_ID}"



Delete a Twitter post
=====================

::
  
python -m agoras.cli publish \
      --network "twitter" \
      --action "delete" \
      --twitter-consumer-key "${TWITTER_CONSUMER_KEY}" \
      --twitter-consumer-secret "${TWITTER_CONSUMER_SECRET}" \
      --twitter-oauth-token "${TWITTER_OAUTH_TOKEN}" \
      --twitter-oauth-secret "${TWITTER_OAUTH_SECRET}" \
      --tweet-id "${TWEET_ID}"



Post the last URL from an atom feed into Twitter
================================================

::
  
python -m agoras.cli publish \
      --network "twitter" \
      --action "last-from-feed" \
      --twitter-consumer-key "${TWITTER_CONSUMER_KEY}" \
      --twitter-consumer-secret "${TWITTER_CONSUMER_SECRET}" \
      --twitter-oauth-token "${TWITTER_OAUTH_TOKEN}" \
      --twitter-oauth-secret "${TWITTER_OAUTH_SECRET}" \
      --feed-url "${FEED_URL}"



Post a random URL from an atom feed into Twitter
================================================

::
  
python -m agoras.cli publish \
      --network "twitter" \
      --action "random-from-feed" \
      --twitter-consumer-key "${TWITTER_CONSUMER_KEY}" \
      --twitter-consumer-secret "${TWITTER_CONSUMER_SECRET}" \
      --twitter-oauth-token "${TWITTER_OAUTH_TOKEN}" \
      --twitter-oauth-secret "${TWITTER_OAUTH_SECRET}" \
      --feed-url "${FEED_URL}"



Schedule a Twitter post
=======================

::
  
python -m agoras.cli publish \
      --network "twitter" \
      --action "schedule" \
      --twitter-consumer-key "${TWITTER_CONSUMER_KEY}" \
      --twitter-consumer-secret "${TWITTER_CONSUMER_SECRET}" \
      --twitter-oauth-token "${TWITTER_OAUTH_TOKEN}" \
      --twitter-oauth-secret "${TWITTER_OAUTH_SECRET}" \
      --google-sheets-id "${GOOGLE_SHEETS_ID}" \
      --google-sheets-name "${GOOGLE_SHEETS_NAME}" \
      --google-sheets-client-email "${GOOGLE_SHEETS_CLIENT_EMAIL}" \
      --google-sheets-private-key "${GOOGLE_SHEETS_PRIVATE_KEY}"