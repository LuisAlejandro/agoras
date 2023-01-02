#!/usr/bin/env bash


if [ "${1}" == "twitter-post" ]; then
    python -m agoras.cli publish \
        --network twitter \
        --action post \
        --twitter-consumer-key "${TWITTER_CONSUMER_KEY}" \
        --twitter-consumer-secret "${TWITTER_CONSUMER_SECRET}" \
        --twitter-oauth-token "${TWITTER_OAUTH_TOKEN}" \
        --twitter-oauth-secret "${TWITTER_OAUTH_SECRET}" \
        --status-text "${STATUS_TEXT}" \
        --status-image-url-1 "${STATUS_IMAGE_URL_1}" \
        --status-image-url-2 "${STATUS_IMAGE_URL_2}" \
        --status-image-url-3 "${STATUS_IMAGE_URL_3}" \
        --status-image-url-4 "${STATUS_IMAGE_URL_4}" \

elif [ "${1}" == "twitter-like" ]; then
    python -m agoras.cli publish \
        --network twitter \
        --action like \
        --twitter-consumer-key "${TWITTER_CONSUMER_KEY}" \
        --twitter-consumer-secret "${TWITTER_CONSUMER_SECRET}" \
        --twitter-oauth-token "${TWITTER_OAUTH_TOKEN}" \
        --twitter-oauth-secret "${TWITTER_OAUTH_SECRET}" \
        --tweet-id "${TWEET_ID}" \

elif [ "${1}" == "twitter-share" ]; then
    python -m agoras.cli publish \
        --network twitter \
        --action share \
        --twitter-consumer-key "${TWITTER_CONSUMER_KEY}" \
        --twitter-consumer-secret "${TWITTER_CONSUMER_SECRET}" \
        --twitter-oauth-token "${TWITTER_OAUTH_TOKEN}" \
        --twitter-oauth-secret "${TWITTER_OAUTH_SECRET}" \
        --tweet-id "${TWEET_ID}" \

elif [ "${1}" == "twitter-delete" ]; then
    python -m agoras.cli publish \
        --network twitter \
        --action delete \
        --twitter-consumer-key "${TWITTER_CONSUMER_KEY}" \
        --twitter-consumer-secret "${TWITTER_CONSUMER_SECRET}" \
        --twitter-oauth-token "${TWITTER_OAUTH_TOKEN}" \
        --twitter-oauth-secret "${TWITTER_OAUTH_SECRET}" \
        --tweet-id "${TWEET_ID}" \

elif [ "${1}" == "twitter-last-from-feed" ]; then
    python -m agoras.cli publish \
        --network twitter \
        --action last-from-feed \
        --twitter-consumer-key "${TWITTER_CONSUMER_KEY}" \
        --twitter-consumer-secret "${TWITTER_CONSUMER_SECRET}" \
        --twitter-oauth-token "${TWITTER_OAUTH_TOKEN}" \
        --twitter-oauth-secret "${TWITTER_OAUTH_SECRET}" \
        --feed-url "${FEED_URL}" \
        --max-count "${MAX_COUNT}" \
        --post-lookback "${POST_LOOKBACK}" \

elif [ "${1}" == "twitter-random-from-feed" ]; then
    python -m agoras.cli publish \
        --network twitter \
        --action random-from-feed \
        --twitter-consumer-key "${TWITTER_CONSUMER_KEY}" \
        --twitter-consumer-secret "${TWITTER_CONSUMER_SECRET}" \
        --twitter-oauth-token "${TWITTER_OAUTH_TOKEN}" \
        --twitter-oauth-secret "${TWITTER_OAUTH_SECRET}" \
        --feed-url "${FEED_URL}" \
        --max-post-age "${MAX_POST_AGE}" \

elif [ "${1}" == "twitter-schedule" ]; then
    python -m agoras.cli publish \
        --network twitter \
        --action schedule \
        --twitter-consumer-key "${TWITTER_CONSUMER_KEY}" \
        --twitter-consumer-secret "${TWITTER_CONSUMER_SECRET}" \
        --twitter-oauth-token "${TWITTER_OAUTH_TOKEN}" \
        --twitter-oauth-secret "${TWITTER_OAUTH_SECRET}" \
        --google-sheets-id "${GOOGLE_SHEETS_ID}" \
        --google-sheets-client-email "${GOOGLE_SHEETS_CLIENT_EMAIL}" \
        --google-sheets-private-key "${GOOGLE_SHEETS_PRIVATE_KEY}" \

elif [ "${1}" == "facebook-post" ]; then
    python -m agoras.cli publish \
        --network facebook \
        --action post \
        --facebook-access-token "${FACEBOOK_ACCESS_TOKEN}" \
        --facebook-object-id "${FACEBOOK_OBJECT_ID}" \
        --status-text "${STATUS_TEXT}" \
        --status-image-url-1 "${STATUS_IMAGE_URL_1}" \
        --status-image-url-2 "${STATUS_IMAGE_URL_2}" \
        --status-image-url-3 "${STATUS_IMAGE_URL_3}" \
        --status-image-url-4 "${STATUS_IMAGE_URL_4}" \

elif [ "${1}" == "facebook-like" ]; then
    python -m agoras.cli publish \
        --network facebook \
        --action like \
        --facebook-access-token "${FACEBOOK_ACCESS_TOKEN}" \
        --facebook-object-id "${FACEBOOK_OBJECT_ID}" \
        --facebook-post-id "${FACEBOOK_POST_ID}" \

elif [ "${1}" == "facebook-share" ]; then
    python -m agoras.cli publish \
        --network facebook \
        --action share \
        --facebook-access-token "${FACEBOOK_ACCESS_TOKEN}" \
        --facebook-profile-id "${FACEBOOK_PROFILE_ID}" \
        --facebook-object-id "${FACEBOOK_OBJECT_ID}" \
        --facebook-post-id "${FACEBOOK_POST_ID}" \

elif [ "${1}" == "facebook-delete" ]; then
    python -m agoras.cli publish \
        --network facebook \
        --action delete \
        --facebook-access-token "${FACEBOOK_ACCESS_TOKEN}" \
        --facebook-object-id "${FACEBOOK_OBJECT_ID}" \
        --facebook-post-id "${FACEBOOK_POST_ID}" \

elif [ "${1}" == "facebook-last-from-feed" ]; then
    python -m agoras.cli publish \
        --network facebook \
        --action last-from-feed \
        --facebook-access-token "${FACEBOOK_ACCESS_TOKEN}" \
        --facebook-object-id "${FACEBOOK_OBJECT_ID}" \
        --feed-url "${FEED_URL}" \
        --max-count "${MAX_COUNT}" \
        --post-lookback "${POST_LOOKBACK}" \

elif [ "${1}" == "facebook-random-from-feed" ]; then
    python -m agoras.cli publish \
        --network facebook \
        --action random-from-feed \
        --facebook-access-token "${FACEBOOK_ACCESS_TOKEN}" \
        --facebook-object-id "${FACEBOOK_OBJECT_ID}" \
        --feed-url "${FEED_URL}" \
        --max-post-age "${MAX_POST_AGE}" \

elif [ "${1}" == "facebook-schedule" ]; then
    python -m agoras.cli publish \
        --network facebook \
        --action schedule \
        --facebook-access-token "${FACEBOOK_ACCESS_TOKEN}" \
        --facebook-object-id "${FACEBOOK_OBJECT_ID}" \
        --google-sheets-id "${GOOGLE_SHEETS_ID}" \
        --google-sheets-name "${GOOGLE_SHEETS_NAME}" \
        --google-sheets-client-email "${GOOGLE_SHEETS_CLIENT_EMAIL}" \
        --google-sheets-private-key "${GOOGLE_SHEETS_PRIVATE_KEY}" \

elif [ "${1}" == "instagram-post" ]; then
    python -m agoras.cli publish \
        --network instagram \
        --action post \
        --instagram-access-token "${INSTAGRAM_ACCESS_TOKEN}" \
        --instagram-object-id "${INSTAGRAM_OBJECT_ID}" \
        --status-text "${STATUS_TEXT}" \
        --status-image-url-1 "${STATUS_IMAGE_URL_1}" \
        --status-image-url-2 "${STATUS_IMAGE_URL_2}" \
        --status-image-url-3 "${STATUS_IMAGE_URL_3}" \
        --status-image-url-4 "${STATUS_IMAGE_URL_4}" \

elif [ "${1}" == "instagram-like" ]; then
    python -m agoras.cli publish \
        --network instagram \
        --action like \
        --instagram-access-token "${INSTAGRAM_ACCESS_TOKEN}" \
        --instagram-object-id "${INSTAGRAM_OBJECT_ID}" \
        --instagram-post-id "${INSTAGRAM_POST_ID}" \

elif [ "${1}" == "instagram-share" ]; then
    python -m agoras.cli publish \
        --network instagram \
        --action share \
        --instagram-access-token "${INSTAGRAM_ACCESS_TOKEN}" \
        --instagram-profile-id "${INSTAGRAM_PROFILE_ID}" \
        --instagram-object-id "${INSTAGRAM_OBJECT_ID}" \
        --instagram-post-id "${INSTAGRAM_POST_ID}" \

elif [ "${1}" == "instagram-delete" ]; then
    python -m agoras.cli publish \
        --network instagram \
        --action delete \
        --instagram-access-token "${INSTAGRAM_ACCESS_TOKEN}" \
        --instagram-object-id "${INSTAGRAM_OBJECT_ID}" \
        --instagram-post-id "${INSTAGRAM_POST_ID}" \

elif [ "${1}" == "instagram-last-from-feed" ]; then
    python -m agoras.cli publish \
        --network instagram \
        --action last-from-feed \
        --instagram-access-token "${INSTAGRAM_ACCESS_TOKEN}" \
        --instagram-object-id "${INSTAGRAM_OBJECT_ID}" \
        --feed-url "${FEED_URL}" \
        --max-count "${MAX_COUNT}" \
        --post-lookback "${POST_LOOKBACK}" \

elif [ "${1}" == "instagram-random-from-feed" ]; then
    python -m agoras.cli publish \
        --network instagram \
        --action random-from-feed \
        --instagram-access-token "${INSTAGRAM_ACCESS_TOKEN}" \
        --instagram-object-id "${INSTAGRAM_OBJECT_ID}" \
        --feed-url "${FEED_URL}" \
        --max-post-age "${MAX_POST_AGE}" \

elif [ "${1}" == "instagram-schedule" ]; then
    python -m agoras.cli publish \
        --network instagram \
        --action schedule \
        --instagram-access-token "${INSTAGRAM_ACCESS_TOKEN}" \
        --instagram-object-id "${INSTAGRAM_OBJECT_ID}" \
        --google-sheets-id "${GOOGLE_SHEETS_ID}" \
        --google-sheets-name "${GOOGLE_SHEETS_NAME}" \
        --google-sheets-client-email "${GOOGLE_SHEETS_CLIENT_EMAIL}" \
        --google-sheets-private-key "${GOOGLE_SHEETS_PRIVATE_KEY}" \

elif [ "${1}" == "linkedin-post" ]; then
    python -m agoras.cli publish \
        --network linkedin \
        --action post \
        --linkedin-username "${LINKEDIN_USERNAME}" \
        --linkedin-password "${LINKEDIN_PASSWORD}" \
        --status-text "${STATUS_TEXT}" \
        --status-image-url-1 "${STATUS_IMAGE_URL_1}" \
        --status-image-url-2 "${STATUS_IMAGE_URL_2}" \
        --status-image-url-3 "${STATUS_IMAGE_URL_3}" \
        --status-image-url-4 "${STATUS_IMAGE_URL_4}" \

elif [ "${1}" == "linkedin-like" ]; then
    python -m agoras.cli publish \
        --network linkedin \
        --action like \
        --linkedin-username "${LINKEDIN_USERNAME}" \
        --linkedin-password "${LINKEDIN_PASSWORD}" \
        --linkedin-post-id "${LINKEDIN_POST_ID}" \

elif [ "${1}" == "linkedin-share" ]; then
    python -m agoras.cli publish \
        --network linkedin \
        --action share \
        --linkedin-username "${LINKEDIN_USERNAME}" \
        --linkedin-password "${LINKEDIN_PASSWORD}" \
        --linkedin-post-id "${LINKEDIN_POST_ID}" \

elif [ "${1}" == "linkedin-delete" ]; then
    python -m agoras.cli publish \
        --network linkedin \
        --action delete \
        --linkedin-username "${LINKEDIN_USERNAME}" \
        --linkedin-password "${LINKEDIN_PASSWORD}" \
        --linkedin-post-id "${LINKEDIN_POST_ID}" \

elif [ "${1}" == "linkedin-last-from-feed" ]; then
    python -m agoras.cli publish \
        --network linkedin \
        --action last-from-feed \
        --linkedin-username "${LINKEDIN_USERNAME}" \
        --linkedin-password "${LINKEDIN_PASSWORD}" \
        --feed-url "${FEED_URL}" \
        --max-count "${MAX_COUNT}" \
        --post-lookback "${POST_LOOKBACK}" \

elif [ "${1}" == "linkedin-post-from-feed" ]; then
    python -m agoras.cli publish \
        --network linkedin \
        --action random-from-feed \
        --linkedin-username "${LINKEDIN_USERNAME}" \
        --linkedin-password "${LINKEDIN_PASSWORD}" \
        --feed-url "${FEED_URL}" \
        --max-post-age "${MAX_POST_AGE}" \

elif [ "${1}" == "linkedin-schedule" ]; then
    python -m agoras.cli publish \
        --network linkedin \
        --action schedule \
        --linkedin-username "${LINKEDIN_USERNAME}" \
        --linkedin-password "${LINKEDIN_PASSWORD}" \
        --google-sheets-id "${GOOGLE_SHEETS_ID}" \
        --google-sheets-name "${GOOGLE_SHEETS_NAME}" \
        --google-sheets-client-email "${GOOGLE_SHEETS_CLIENT_EMAIL}" \
        --google-sheets-private-key "${GOOGLE_SHEETS_PRIVATE_KEY}" \

else
    echo "Unsupported action ${1}"
fi
