#!/usr/bin/env bash

# Exit early if there are errors and be verbose
set -exuo pipefail

# source assert.sh
source secrets.env

python3 -m utils.schedule

if [ "${1}" == "twitter" ]; then
    LA_POST_TWITTER_ID=$(
        python3 -m agoras.cli publish \
            --network twitter \
            --action post \
            --twitter-consumer-key "${LA_TWITTER_CONSUMER_KEY}" \
            --twitter-consumer-secret "${LA_TWITTER_CONSUMER_SECRET}" \
            --twitter-oauth-token "${LA_TWITTER_OAUTH_TOKEN}" \
            --twitter-oauth-secret "${LA_TWITTER_OAUTH_SECRET}" \
            --status-text "${LA_TWITTER_STATUS_TEXT}" \
            --status-image-url-1 "${LA_TWITTER_STATUS_IMAGE_URL_1}" | jq -r '.id'
    )

    sleep 5

    python3 -m agoras.cli publish \
        --network twitter \
        --action delete \
        --twitter-consumer-key "${LA_TWITTER_CONSUMER_KEY}" \
        --twitter-consumer-secret "${LA_TWITTER_CONSUMER_SECRET}" \
        --twitter-oauth-token "${LA_TWITTER_OAUTH_TOKEN}" \
        --twitter-oauth-secret "${LA_TWITTER_OAUTH_SECRET}" \
        --tweet-id "${LA_POST_TWITTER_ID}"

    sleep 5

    LD_POST_TWITTER_ID=$(
        python3 -m agoras.cli publish \
            --network twitter \
            --action post \
            --twitter-consumer-key "${LD_TWITTER_CONSUMER_KEY}" \
            --twitter-consumer-secret "${LD_TWITTER_CONSUMER_SECRET}" \
            --twitter-oauth-token "${LD_TWITTER_OAUTH_TOKEN}" \
            --twitter-oauth-secret "${LD_TWITTER_OAUTH_SECRET}" \
            --status-text "${LD_TWITTER_STATUS_TEXT}" \
            --status-image-url-1 "${LD_TWITTER_STATUS_IMAGE_URL_1}" | jq -r '.id'
    )

    sleep 5

    python3 -m agoras.cli publish \
        --network twitter \
        --action delete \
        --twitter-consumer-key "${LD_TWITTER_CONSUMER_KEY}" \
        --twitter-consumer-secret "${LD_TWITTER_CONSUMER_SECRET}" \
        --twitter-oauth-token "${LD_TWITTER_OAUTH_TOKEN}" \
        --twitter-oauth-secret "${LD_TWITTER_OAUTH_SECRET}" \
        --tweet-id "${LD_POST_TWITTER_ID}"

    sleep 5

    LD_LAST_FROM_FEED_TWEET_ID=$(
        python3 -m agoras.cli publish \
            --network twitter \
            --action last-from-feed \
            --twitter-consumer-key "${LD_TWITTER_CONSUMER_KEY}" \
            --twitter-consumer-secret "${LD_TWITTER_CONSUMER_SECRET}" \
            --twitter-oauth-token "${LD_TWITTER_OAUTH_TOKEN}" \
            --twitter-oauth-secret "${LD_TWITTER_OAUTH_SECRET}" \
            --feed-url "${FEED_URL}" \
            --max-count "${MAX_COUNT}" \
            --post-lookback "${POST_LOOKBACK}" | jq -r '.id'
    )

    sleep 5

    LD_RANDOM_FROM_FEED_TWEET_ID=$(
        python3 -m agoras.cli publish \
            --network twitter \
            --action random-from-feed \
            --twitter-consumer-key "${LD_TWITTER_CONSUMER_KEY}" \
            --twitter-consumer-secret "${LD_TWITTER_CONSUMER_SECRET}" \
            --twitter-oauth-token "${LD_TWITTER_OAUTH_TOKEN}" \
            --twitter-oauth-secret "${LD_TWITTER_OAUTH_SECRET}" \
            --feed-url "${FEED_URL}" \
            --max-post-age "${MAX_POST_AGE}" | jq -r '.id'
    )

    sleep 5

    LD_SCHEDULE_TWEET_ID=$(
        python3 -m agoras.cli publish \
            --network twitter \
            --action schedule \
            --twitter-consumer-key "${LD_TWITTER_CONSUMER_KEY}" \
            --twitter-consumer-secret "${LD_TWITTER_CONSUMER_SECRET}" \
            --twitter-oauth-token "${LD_TWITTER_OAUTH_TOKEN}" \
            --twitter-oauth-secret "${LD_TWITTER_OAUTH_SECRET}" \
            --max-count "${MAX_COUNT}" \
            --google-sheets-id "${GOOGLE_SHEETS_ID}" \
            --google-sheets-client-email "${GOOGLE_SHEETS_CLIENT_EMAIL}" \
            --google-sheets-private-key "${GOOGLE_SHEETS_PRIVATE_KEY}" | jq -r '.id'
    )

    sleep 5

    python3 -m agoras.cli publish \
        --network twitter \
        --action delete \
        --twitter-consumer-key "${LD_TWITTER_CONSUMER_KEY}" \
        --twitter-consumer-secret "${LD_TWITTER_CONSUMER_SECRET}" \
        --twitter-oauth-token "${LD_TWITTER_OAUTH_TOKEN}" \
        --twitter-oauth-secret "${LD_TWITTER_OAUTH_SECRET}" \
        --tweet-id "${LD_LAST_FROM_FEED_TWEET_ID}"

    sleep 5

    python3 -m agoras.cli publish \
        --network twitter \
        --action delete \
        --twitter-consumer-key "${LD_TWITTER_CONSUMER_KEY}" \
        --twitter-consumer-secret "${LD_TWITTER_CONSUMER_SECRET}" \
        --twitter-oauth-token "${LD_TWITTER_OAUTH_TOKEN}" \
        --twitter-oauth-secret "${LD_TWITTER_OAUTH_SECRET}" \
        --tweet-id "${LD_RANDOM_FROM_FEED_TWEET_ID}"

    sleep 5

    python3 -m agoras.cli publish \
        --network twitter \
        --action delete \
        --twitter-consumer-key "${LD_TWITTER_CONSUMER_KEY}" \
        --twitter-consumer-secret "${LD_TWITTER_CONSUMER_SECRET}" \
        --twitter-oauth-token "${LD_TWITTER_OAUTH_TOKEN}" \
        --twitter-oauth-secret "${LD_TWITTER_OAUTH_SECRET}" \
        --tweet-id "${LD_SCHEDULE_TWEET_ID}"

elif [ "${1}" == "facebook" ]; then
    LD_POST_FACEBOOK_ID=$(
        python3 -m agoras.cli publish \
            --network facebook \
            --action post \
            --facebook-access-token "${LD_FACEBOOK_ACCESS_TOKEN}" \
            --facebook-object-id "${LD_FACEBOOK_OBJECT_ID}" \
            --status-text "${LD_FACEBOOK_STATUS_TEXT}" \
            --status-image-url-1 "${LD_FACEBOOK_STATUS_IMAGE_URL_1}" | jq -r '.id' | awk -F '_' '{print $2}'
    )

    sleep 5

    python3 -m agoras.cli publish \
        --network facebook \
        --action like \
        --facebook-access-token "${LD_FACEBOOK_ACCESS_TOKEN}" \
        --facebook-object-id "${LD_FACEBOOK_OBJECT_ID}" \
        --facebook-post-id "${LD_POST_FACEBOOK_ID}"

    sleep 5

    LD_SHARED_POST_FACEBOOK_ID=$(
        python3 -m agoras.cli publish \
            --network facebook \
            --action share \
            --facebook-access-token "${LD_FACEBOOK_ACCESS_TOKEN}" \
            --facebook-profile-id "${LD_FACEBOOK_PROFILE_ID}" \
            --facebook-object-id "${LD_FACEBOOK_OBJECT_ID}" \
            --facebook-post-id "${LD_POST_FACEBOOK_ID}" | jq -r '.id' | awk -F '_' '{print $2}'
    )

    sleep 5

    LD_LAST_FROM_FEED_FACEBOOK_ID=$(
        python3 -m agoras.cli publish \
            --network facebook \
            --action last-from-feed \
            --facebook-access-token "${LD_FACEBOOK_ACCESS_TOKEN}" \
            --facebook-object-id "${LD_FACEBOOK_OBJECT_ID}" \
            --feed-url "${FEED_URL}" \
            --max-count "${MAX_COUNT}" \
            --post-lookback "${POST_LOOKBACK}" | jq -r '.id' | awk -F '_' '{print $2}'
    )

    sleep 5

    LD_RANDOM_FROM_FEED_FACEBOOK_ID=$(
        python3 -m agoras.cli publish \
            --network facebook \
            --action random-from-feed \
            --facebook-access-token "${LD_FACEBOOK_ACCESS_TOKEN}" \
            --facebook-object-id "${LD_FACEBOOK_OBJECT_ID}" \
            --feed-url "${FEED_URL}" \
            --max-post-age "${MAX_POST_AGE}" | jq -r '.id' | awk -F '_' '{print $2}'
    )

    sleep 5

    LD_SCHEDULE_FACEBOOK_ID=$(
        python3 -m agoras.cli publish \
            --network facebook \
            --action schedule \
            --facebook-access-token "${LD_FACEBOOK_ACCESS_TOKEN}" \
            --facebook-object-id "${LD_FACEBOOK_OBJECT_ID}" \
            --max-count "${MAX_COUNT}" \
            --google-sheets-id "${GOOGLE_SHEETS_ID}" \
            --google-sheets-name "${GOOGLE_SHEETS_NAME}" \
            --google-sheets-client-email "${GOOGLE_SHEETS_CLIENT_EMAIL}" \
            --google-sheets-private-key "${GOOGLE_SHEETS_PRIVATE_KEY}" | jq -r '.id' | awk -F '_' '{print $2}'
    )

    sleep 5

    python3 -m agoras.cli publish \
        --network facebook \
        --action delete \
        --facebook-access-token "${LD_FACEBOOK_ACCESS_TOKEN}" \
        --facebook-object-id "${LD_FACEBOOK_OBJECT_ID}" \
        --facebook-post-id "${LD_POST_FACEBOOK_ID}"

    sleep 5

    python3 -m agoras.cli publish \
        --network facebook \
        --action delete \
        --facebook-access-token "${LD_FACEBOOK_ACCESS_TOKEN}" \
        --facebook-object-id "${LD_FACEBOOK_OBJECT_ID}" \
        --facebook-post-id "${LD_LAST_FROM_FEED_FACEBOOK_ID}"

    sleep 5

    python3 -m agoras.cli publish \
        --network facebook \
        --action delete \
        --facebook-access-token "${LD_FACEBOOK_ACCESS_TOKEN}" \
        --facebook-object-id "${LD_FACEBOOK_OBJECT_ID}" \
        --facebook-post-id "${LD_RANDOM_FROM_FEED_FACEBOOK_ID}"

    sleep 5

    python3 -m agoras.cli publish \
        --network facebook \
        --action delete \
        --facebook-access-token "${LD_FACEBOOK_ACCESS_TOKEN}" \
        --facebook-object-id "${LD_FACEBOOK_OBJECT_ID}" \
        --facebook-post-id "${LD_SCHEDULE_FACEBOOK_ID}"

    sleep 5

    python3 -m agoras.cli publish \
        --network facebook \
        --action delete \
        --facebook-access-token "${LD_FACEBOOK_ACCESS_TOKEN}" \
        --facebook-object-id "${LD_FACEBOOK_OBJECT_ID}" \
        --facebook-post-id "${LD_SHARED_POST_FACEBOOK_ID}"

elif [ "${1}" == "instagram" ]; then
    python3 -m agoras.cli publish \
        --network instagram \
        --action post \
        --instagram-access-token "${INSTAGRAM_ACCESS_TOKEN}" \
        --instagram-object-id "${INSTAGRAM_OBJECT_ID}" \
        --status-text "${STATUS_TEXT}" \
        --status-image-url-1 "${STATUS_IMAGE_URL_1}"

    sleep 5

    python3 -m agoras.cli publish \
        --network instagram \
        --action last-from-feed \
        --instagram-access-token "${INSTAGRAM_ACCESS_TOKEN}" \
        --instagram-object-id "${INSTAGRAM_OBJECT_ID}" \
        --feed-url "${FEED_URL}" \
        --max-count "${MAX_COUNT}" \
        --post-lookback "${POST_LOOKBACK}"

    sleep 5

    python3 -m agoras.cli publish \
        --network instagram \
        --action random-from-feed \
        --instagram-access-token "${INSTAGRAM_ACCESS_TOKEN}" \
        --instagram-object-id "${INSTAGRAM_OBJECT_ID}" \
        --feed-url "${FEED_URL}" \
        --max-post-age "${MAX_POST_AGE}"

    sleep 5

    python3 -m agoras.cli publish \
        --network instagram \
        --action schedule \
        --instagram-access-token "${INSTAGRAM_ACCESS_TOKEN}" \
        --instagram-object-id "${INSTAGRAM_OBJECT_ID}" \
        --max-count "${MAX_COUNT}" \
        --google-sheets-id "${GOOGLE_SHEETS_ID}" \
        --google-sheets-name "${GOOGLE_SHEETS_NAME}" \
        --google-sheets-client-email "${GOOGLE_SHEETS_CLIENT_EMAIL}" \
        --google-sheets-private-key "${GOOGLE_SHEETS_PRIVATE_KEY}"

elif [ "${1}" == "linkedin" ]; then
    LA_POST_LINKEDIN_ID=$(
        python3 -m agoras.cli publish \
            --network linkedin \
            --action post \
            --linkedin-username "${LINKEDIN_USERNAME}" \
            --linkedin-password "${LINKEDIN_PASSWORD}" \
            --status-text "${LINKEDIN_STATUS_TEXT}" \
            --status-image-url-1 "${LINKEDIN_STATUS_IMAGE_URL_1}" | jq -r '.id'
    )

    sleep 5

    python3 -m agoras.cli publish \
        --network linkedin \
        --action like \
        --linkedin-username "${LINKEDIN_USERNAME}" \
        --linkedin-password "${LINKEDIN_PASSWORD}" \
        --linkedin-post-id "${LA_POST_LINKEDIN_ID}"

    sleep 5

    LA_SHARED_POST_LINKEDIN_ID=$(
        python3 -m agoras.cli publish \
            --network linkedin \
            --action share \
            --linkedin-username "${LINKEDIN_USERNAME}" \
            --linkedin-password "${LINKEDIN_PASSWORD}" \
            --linkedin-post-id "${LA_POST_LINKEDIN_ID}" | jq -r '.id'
    )

    sleep 5

    LA_LAST_FROM_FEED_LINKEDIN_ID=$(
        python3 -m agoras.cli publish \
            --network linkedin \
            --action last-from-feed \
            --linkedin-username "${LINKEDIN_USERNAME}" \
            --linkedin-password "${LINKEDIN_PASSWORD}" \
            --feed-url "${FEED_URL}" \
            --max-count "${MAX_COUNT}" \
            --post-lookback "${POST_LOOKBACK}" | jq -r '.id'
    )

    sleep 5

    LA_RANDOM_FROM_FEED_LINKEDIN_ID=$(
        python3 -m agoras.cli publish \
            --network linkedin \
            --action random-from-feed \
            --linkedin-username "${LINKEDIN_USERNAME}" \
            --linkedin-password "${LINKEDIN_PASSWORD}" \
            --feed-url "${FEED_URL}" \
            --max-post-age "${MAX_POST_AGE}" | jq -r '.id'
    )

    sleep 5

    LA_SCHEDULE_LINKEDIN_ID=$(
        python3 -m agoras.cli publish \
            --network linkedin \
            --action schedule \
            --linkedin-username "${LINKEDIN_USERNAME}" \
            --linkedin-password "${LINKEDIN_PASSWORD}" \
            --max-count "${MAX_COUNT}" \
            --google-sheets-id "${GOOGLE_SHEETS_ID}" \
            --google-sheets-name "${GOOGLE_SHEETS_NAME}" \
            --google-sheets-client-email "${GOOGLE_SHEETS_CLIENT_EMAIL}" \
            --google-sheets-private-key "${GOOGLE_SHEETS_PRIVATE_KEY}" | jq -r '.id'
    )

    sleep 10

    python3 -m agoras.cli publish \
        --network linkedin \
        --action delete \
        --linkedin-username "${LINKEDIN_USERNAME}" \
        --linkedin-password "${LINKEDIN_PASSWORD}" \
        --linkedin-post-id "${LA_POST_LINKEDIN_ID}"

    sleep 10

    python3 -m agoras.cli publish \
        --network linkedin \
        --action delete \
        --linkedin-username "${LINKEDIN_USERNAME}" \
        --linkedin-password "${LINKEDIN_PASSWORD}" \
        --linkedin-post-id "${LA_SHARED_POST_LINKEDIN_ID}"

    sleep 10

    python3 -m agoras.cli publish \
        --network linkedin \
        --action delete \
        --linkedin-username "${LINKEDIN_USERNAME}" \
        --linkedin-password "${LINKEDIN_PASSWORD}" \
        --linkedin-post-id "${LA_LAST_FROM_FEED_LINKEDIN_ID}"

    sleep 10

    python3 -m agoras.cli publish \
        --network linkedin \
        --action delete \
        --linkedin-username "${LINKEDIN_USERNAME}" \
        --linkedin-password "${LINKEDIN_PASSWORD}" \
        --linkedin-post-id "${LA_RANDOM_FROM_FEED_LINKEDIN_ID}"

    sleep 10

    python3 -m agoras.cli publish \
        --network linkedin \
        --action delete \
        --linkedin-username "${LINKEDIN_USERNAME}" \
        --linkedin-password "${LINKEDIN_PASSWORD}" \
        --linkedin-post-id "${LA_SCHEDULE_LINKEDIN_ID}"

else
    echo "Unsupported action ${1}"
fi
