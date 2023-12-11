#!/usr/bin/env bash

# Exit early if there are errors and be verbose
set -exuo pipefail

source secrets.env

python3 -m utils.schedule "${GOOGLE_SHEETS_ID}" "${GOOGLE_SHEETS_NAME}" "${GOOGLE_SHEETS_CLIENT_EMAIL}" "${GOOGLE_SHEETS_PRIVATE_KEY}"

if [ "${1}" == "twitter" ]; then
    POST_TWITTER_ID=$(
        python3 -m agoras.cli publish \
            --network twitter \
            --action post \
            --twitter-consumer-key "${TWITTER_CONSUMER_KEY}" \
            --twitter-consumer-secret "${TWITTER_CONSUMER_SECRET}" \
            --twitter-oauth-token "${TWITTER_OAUTH_TOKEN}" \
            --twitter-oauth-secret "${TWITTER_OAUTH_SECRET}" \
            --status-text "${TWITTER_STATUS_TEXT}" \
            --status-image-url-1 "${TWITTER_STATUS_IMAGE_URL_1}" | jq --unbuffered '.' | jq -r '.id'
    )

    sleep 5

    LAST_FROM_FEED_TWEET_ID=$(
        python3 -m agoras.cli publish \
            --network twitter \
            --action last-from-feed \
            --twitter-consumer-key "${TWITTER_CONSUMER_KEY}" \
            --twitter-consumer-secret "${TWITTER_CONSUMER_SECRET}" \
            --twitter-oauth-token "${TWITTER_OAUTH_TOKEN}" \
            --twitter-oauth-secret "${TWITTER_OAUTH_SECRET}" \
            --feed-url "${FEED_URL}" \
            --max-count 1 \
            --post-lookback "${POST_LOOKBACK}" | jq --unbuffered '.' | jq -r '.id'
    )

    sleep 5

    RANDOM_FROM_FEED_TWEET_ID=$(
        python3 -m agoras.cli publish \
            --network twitter \
            --action random-from-feed \
            --twitter-consumer-key "${TWITTER_CONSUMER_KEY}" \
            --twitter-consumer-secret "${TWITTER_CONSUMER_SECRET}" \
            --twitter-oauth-token "${TWITTER_OAUTH_TOKEN}" \
            --twitter-oauth-secret "${TWITTER_OAUTH_SECRET}" \
            --feed-url "${FEED_URL}" \
            --max-post-age 365 | jq --unbuffered '.' | jq -r '.id'
    )

    sleep 5

    SCHEDULE_TWEET_ID=$(
        python3 -m agoras.cli publish \
            --network twitter \
            --action schedule \
            --twitter-consumer-key "${TWITTER_CONSUMER_KEY}" \
            --twitter-consumer-secret "${TWITTER_CONSUMER_SECRET}" \
            --twitter-oauth-token "${TWITTER_OAUTH_TOKEN}" \
            --twitter-oauth-secret "${TWITTER_OAUTH_SECRET}" \
            --max-count 1 \
            --google-sheets-id "${GOOGLE_SHEETS_ID}" \
            --google-sheets-name "${GOOGLE_SHEETS_NAME}" \
            --google-sheets-client-email "${GOOGLE_SHEETS_CLIENT_EMAIL}" \
            --google-sheets-private-key "${GOOGLE_SHEETS_PRIVATE_KEY}" | jq --unbuffered '.' | jq -r '.id'
    )

    sleep 5

    [ -n "${POST_TWITTER_ID}" ] && python3 -m agoras.cli publish \
        --network twitter \
        --action delete \
        --twitter-consumer-key "${TWITTER_CONSUMER_KEY}" \
        --twitter-consumer-secret "${TWITTER_CONSUMER_SECRET}" \
        --twitter-oauth-token "${TWITTER_OAUTH_TOKEN}" \
        --twitter-oauth-secret "${TWITTER_OAUTH_SECRET}" \
        --tweet-id "${POST_TWITTER_ID}" || true

    sleep 5

    [ -n "${LAST_FROM_FEED_TWEET_ID}" ] && python3 -m agoras.cli publish \
        --network twitter \
        --action delete \
        --twitter-consumer-key "${TWITTER_CONSUMER_KEY}" \
        --twitter-consumer-secret "${TWITTER_CONSUMER_SECRET}" \
        --twitter-oauth-token "${TWITTER_OAUTH_TOKEN}" \
        --twitter-oauth-secret "${TWITTER_OAUTH_SECRET}" \
        --tweet-id "${LAST_FROM_FEED_TWEET_ID}" || true

    sleep 5

    [ -n "${RANDOM_FROM_FEED_TWEET_ID}" ] && python3 -m agoras.cli publish \
        --network twitter \
        --action delete \
        --twitter-consumer-key "${TWITTER_CONSUMER_KEY}" \
        --twitter-consumer-secret "${TWITTER_CONSUMER_SECRET}" \
        --twitter-oauth-token "${TWITTER_OAUTH_TOKEN}" \
        --twitter-oauth-secret "${TWITTER_OAUTH_SECRET}" \
        --tweet-id "${RANDOM_FROM_FEED_TWEET_ID}" || true

    sleep 5

    [ -n "${SCHEDULE_TWEET_ID}" ] && python3 -m agoras.cli publish \
        --network twitter \
        --action delete \
        --twitter-consumer-key "${TWITTER_CONSUMER_KEY}" \
        --twitter-consumer-secret "${TWITTER_CONSUMER_SECRET}" \
        --twitter-oauth-token "${TWITTER_OAUTH_TOKEN}" \
        --twitter-oauth-secret "${TWITTER_OAUTH_SECRET}" \
        --tweet-id "${SCHEDULE_TWEET_ID}" || true

elif [ "${1}" == "facebook" ]; then
    POST_FACEBOOK_ID=$(
        python3 -m agoras.cli publish \
            --network facebook \
            --action post \
            --facebook-access-token "${FACEBOOK_ACCESS_TOKEN}" \
            --facebook-object-id "${FACEBOOK_OBJECT_ID}" \
            --status-text "${FACEBOOK_STATUS_TEXT}" \
            --status-image-url-1 "${FACEBOOK_STATUS_IMAGE_URL_1}" | jq --unbuffered '.' | jq -r '.id'
    )

    sleep 5

    SHARED_POST_FACEBOOK_ID=$(
        python3 -m agoras.cli publish \
            --network facebook \
            --action share \
            --facebook-access-token "${FACEBOOK_ACCESS_TOKEN}" \
            --facebook-profile-id "${FACEBOOK_PROFILE_ID}" \
            --facebook-object-id "${FACEBOOK_OBJECT_ID}" \
            --facebook-post-id "${POST_FACEBOOK_ID}" | jq --unbuffered '.' | jq -r '.id'
    )

    sleep 5

    LAST_FROM_FEED_FACEBOOK_ID=$(
        python3 -m agoras.cli publish \
            --network facebook \
            --action last-from-feed \
            --facebook-access-token "${FACEBOOK_ACCESS_TOKEN}" \
            --facebook-object-id "${FACEBOOK_OBJECT_ID}" \
            --feed-url "${FEED_URL}" \
            --max-count 1 \
            --post-lookback "${POST_LOOKBACK}" | jq --unbuffered '.' | jq -r '.id'
    )

    sleep 5

    RANDOM_FROM_FEED_FACEBOOK_ID=$(
        python3 -m agoras.cli publish \
            --network facebook \
            --action random-from-feed \
            --facebook-access-token "${FACEBOOK_ACCESS_TOKEN}" \
            --facebook-object-id "${FACEBOOK_OBJECT_ID}" \
            --feed-url "${FEED_URL}" \
            --max-post-age 365 | jq --unbuffered '.' | jq -r '.id'
    )

    sleep 5

    SCHEDULE_FACEBOOK_ID=$(
        python3 -m agoras.cli publish \
            --network facebook \
            --action schedule \
            --facebook-access-token "${FACEBOOK_ACCESS_TOKEN}" \
            --facebook-object-id "${FACEBOOK_OBJECT_ID}" \
            --max-count 1 \
            --google-sheets-id "${GOOGLE_SHEETS_ID}" \
            --google-sheets-name "${GOOGLE_SHEETS_NAME}" \
            --google-sheets-client-email "${GOOGLE_SHEETS_CLIENT_EMAIL}" \
            --google-sheets-private-key "${GOOGLE_SHEETS_PRIVATE_KEY}" | jq --unbuffered '.' | jq -r '.id'
    )

    sleep 5

    [ -n "${POST_FACEBOOK_ID}" ] && python3 -m agoras.cli publish \
        --network facebook \
        --action like \
        --facebook-access-token "${FACEBOOK_ACCESS_TOKEN}" \
        --facebook-object-id "${FACEBOOK_OBJECT_ID}" \
        --facebook-post-id "${POST_FACEBOOK_ID}" || true

    sleep 5

    [ -n "${SHARED_POST_FACEBOOK_ID}" ] && python3 -m agoras.cli publish \
        --network facebook \
        --action delete \
        --facebook-access-token "${FACEBOOK_ACCESS_TOKEN}" \
        --facebook-object-id "${FACEBOOK_OBJECT_ID}" \
        --facebook-post-id "${SHARED_POST_FACEBOOK_ID}" || true

    sleep 5

    [ -n "${POST_FACEBOOK_ID}" ] && python3 -m agoras.cli publish \
        --network facebook \
        --action delete \
        --facebook-access-token "${FACEBOOK_ACCESS_TOKEN}" \
        --facebook-object-id "${FACEBOOK_OBJECT_ID}" \
        --facebook-post-id "${POST_FACEBOOK_ID}" || true

    sleep 5

    [ -n "${LAST_FROM_FEED_FACEBOOK_ID}" ] && python3 -m agoras.cli publish \
        --network facebook \
        --action delete \
        --facebook-access-token "${FACEBOOK_ACCESS_TOKEN}" \
        --facebook-object-id "${FACEBOOK_OBJECT_ID}" \
        --facebook-post-id "${LAST_FROM_FEED_FACEBOOK_ID}" || true

    sleep 5

    [ -n "${RANDOM_FROM_FEED_FACEBOOK_ID}" ] && python3 -m agoras.cli publish \
        --network facebook \
        --action delete \
        --facebook-access-token "${FACEBOOK_ACCESS_TOKEN}" \
        --facebook-object-id "${FACEBOOK_OBJECT_ID}" \
        --facebook-post-id "${RANDOM_FROM_FEED_FACEBOOK_ID}" || true

    sleep 5

    [ -n "${SCHEDULE_FACEBOOK_ID}" ] && python3 -m agoras.cli publish \
        --network facebook \
        --action delete \
        --facebook-access-token "${FACEBOOK_ACCESS_TOKEN}" \
        --facebook-object-id "${FACEBOOK_OBJECT_ID}" \
        --facebook-post-id "${SCHEDULE_FACEBOOK_ID}" || true

elif [ "${1}" == "instagram" ]; then
    python3 -m agoras.cli publish \
        --network instagram \
        --action post \
        --instagram-access-token "${INSTAGRAM_ACCESS_TOKEN}" \
        --instagram-object-id "${INSTAGRAM_OBJECT_ID}" \
        --status-text "${INSTAGRAM_STATUS_TEXT}" \
        --status-image-url-1 "${INSTAGRAM_STATUS_IMAGE_URL_1}"

    sleep 5

    python3 -m agoras.cli publish \
        --network instagram \
        --action last-from-feed \
        --instagram-access-token "${INSTAGRAM_ACCESS_TOKEN}" \
        --instagram-object-id "${INSTAGRAM_OBJECT_ID}" \
        --feed-url "${FEED_URL}" \
        --max-count 1 \
        --post-lookback "${POST_LOOKBACK}"

    sleep 5

    python3 -m agoras.cli publish \
        --network instagram \
        --action random-from-feed \
        --instagram-access-token "${INSTAGRAM_ACCESS_TOKEN}" \
        --instagram-object-id "${INSTAGRAM_OBJECT_ID}" \
        --feed-url "${FEED_URL}" \
        --max-post-age 365

    sleep 5

    python3 -m agoras.cli publish \
        --network instagram \
        --action schedule \
        --instagram-access-token "${INSTAGRAM_ACCESS_TOKEN}" \
        --instagram-object-id "${INSTAGRAM_OBJECT_ID}" \
        --max-count 1 \
        --google-sheets-id "${GOOGLE_SHEETS_ID}" \
        --google-sheets-name "${GOOGLE_SHEETS_NAME}" \
        --google-sheets-client-email "${GOOGLE_SHEETS_CLIENT_EMAIL}" \
        --google-sheets-private-key "${GOOGLE_SHEETS_PRIVATE_KEY}"

elif [ "${1}" == "discord" ]; then
    POST_DISCORD_ID=$(
        python3 -m agoras.cli publish \
            --network discord \
            --action post \
            --discord-bot-token "${DISCORD_BOT_TOKEN}" \
            --discord-server-name "${DISCORD_SERVER_NAME}" \
            --discord-channel-name "${DISCORD_CHANNEL_NAME}" \
            --status-text "${DISCORD_STATUS_TEXT}" \
            --status-image-url-1 "${DISCORD_STATUS_IMAGE_URL_1}" | jq --unbuffered '.' | jq -r '.id'
    )

    sleep 5

    LAST_FROM_FEED_DISCORD_ID=$(
        python3 -m agoras.cli publish \
            --network discord \
            --action last-from-feed \
            --discord-bot-token "${DISCORD_BOT_TOKEN}" \
            --discord-server-name "${DISCORD_SERVER_NAME}" \
            --discord-channel-name "${DISCORD_CHANNEL_NAME}" \
            --feed-url "${FEED_URL}" \
            --max-count 1 \
            --post-lookback "${POST_LOOKBACK}" | jq --unbuffered '.' | jq -r '.id'
    )

    sleep 5

    RANDOM_FROM_FEED_DISCORD_ID=$(
        python3 -m agoras.cli publish \
            --network discord \
            --action random-from-feed \
            --discord-bot-token "${DISCORD_BOT_TOKEN}" \
            --discord-server-name "${DISCORD_SERVER_NAME}" \
            --discord-channel-name "${DISCORD_CHANNEL_NAME}" \
            --feed-url "${FEED_URL}" \
            --max-post-age 365 | jq --unbuffered '.' | jq -r '.id'
    )

    sleep 5

    SCHEDULE_DISCORD_ID=$(
        python3 -m agoras.cli publish \
            --network discord \
            --action schedule \
            --discord-bot-token "${DISCORD_BOT_TOKEN}" \
            --discord-server-name "${DISCORD_SERVER_NAME}" \
            --discord-channel-name "${DISCORD_CHANNEL_NAME}" \
            --max-count 1 \
            --google-sheets-id "${GOOGLE_SHEETS_ID}" \
            --google-sheets-name "${GOOGLE_SHEETS_NAME}" \
            --google-sheets-client-email "${GOOGLE_SHEETS_CLIENT_EMAIL}" \
            --google-sheets-private-key "${GOOGLE_SHEETS_PRIVATE_KEY}" | jq --unbuffered '.' | jq -r '.id'
    )

    sleep 5

    [ -n "${POST_DISCORD_ID}" ] && python3 -m agoras.cli publish \
        --network discord \
        --action like \
        --discord-bot-token "${DISCORD_BOT_TOKEN}" \
        --discord-server-name "${DISCORD_SERVER_NAME}" \
        --discord-channel-name "${DISCORD_CHANNEL_NAME}" \
        --discord-post-id "${POST_DISCORD_ID}" || true

    sleep 5

    [ -n "${POST_DISCORD_ID}" ] && python3 -m agoras.cli publish \
        --network discord \
        --action delete \
        --discord-bot-token "${DISCORD_BOT_TOKEN}" \
        --discord-server-name "${DISCORD_SERVER_NAME}" \
        --discord-channel-name "${DISCORD_CHANNEL_NAME}" \
        --discord-post-id "${POST_DISCORD_ID}" || true

    sleep 5

    [ -n "${LAST_FROM_FEED_DISCORD_ID}" ] && python3 -m agoras.cli publish \
        --network discord \
        --action delete \
        --discord-bot-token "${DISCORD_BOT_TOKEN}" \
        --discord-server-name "${DISCORD_SERVER_NAME}" \
        --discord-channel-name "${DISCORD_CHANNEL_NAME}" \
        --discord-post-id "${LAST_FROM_FEED_DISCORD_ID}" || true

    sleep 5

    [ -n "${RANDOM_FROM_FEED_DISCORD_ID}" ] && python3 -m agoras.cli publish \
        --network discord \
        --action delete \
        --discord-bot-token "${DISCORD_BOT_TOKEN}" \
        --discord-server-name "${DISCORD_SERVER_NAME}" \
        --discord-channel-name "${DISCORD_CHANNEL_NAME}" \
        --discord-post-id "${RANDOM_FROM_FEED_DISCORD_ID}" || true

    sleep 5

    [ -n "${SCHEDULE_DISCORD_ID}" ] && python3 -m agoras.cli publish \
        --network discord \
        --action delete \
        --discord-bot-token "${DISCORD_BOT_TOKEN}" \
        --discord-server-name "${DISCORD_SERVER_NAME}" \
        --discord-channel-name "${DISCORD_CHANNEL_NAME}" \
        --discord-post-id "${SCHEDULE_DISCORD_ID}" || true

elif [ "${1}" == "linkedin" ]; then
    POST_LINKEDIN_ID=$(
        python3 -m agoras.cli publish \
            --network linkedin \
            --action post \
            --linkedin-access-token "${LINKEDIN_ACCESS_TOKEN}" \
            --status-text "${LINKEDIN_STATUS_TEXT}" \
            --status-image-url-1 "${LINKEDIN_STATUS_IMAGE_URL_1}" | jq --unbuffered '.' | jq -r '.id'
    )

    sleep 5

    SHARED_POST_LINKEDIN_ID=$(
        python3 -m agoras.cli publish \
            --network linkedin \
            --action share \
            --linkedin-access-token "${LINKEDIN_ACCESS_TOKEN}" \
            --linkedin-post-id "${POST_LINKEDIN_ID}" | jq --unbuffered '.' | jq -r '.id'
    )

    sleep 5

    LAST_FROM_FEED_LINKEDIN_ID=$(
        python3 -m agoras.cli publish \
            --network linkedin \
            --action last-from-feed \
            --linkedin-access-token "${LINKEDIN_ACCESS_TOKEN}" \
            --feed-url "${FEED_URL}" \
            --max-count 1 \
            --post-lookback "${POST_LOOKBACK}" | jq --unbuffered '.' | jq -r '.id'
    )

    sleep 5

    RANDOM_FROM_FEED_LINKEDIN_ID=$(
        python3 -m agoras.cli publish \
            --network linkedin \
            --action random-from-feed \
            --linkedin-access-token "${LINKEDIN_ACCESS_TOKEN}" \
            --feed-url "${FEED_URL}" \
            --max-post-age 365 | jq --unbuffered '.' | jq -r '.id'
    )

    sleep 5

    SCHEDULE_LINKEDIN_ID=$(
        python3 -m agoras.cli publish \
            --network linkedin \
            --action schedule \
            --linkedin-access-token "${LINKEDIN_ACCESS_TOKEN}" \
            --max-count 1 \
            --google-sheets-id "${GOOGLE_SHEETS_ID}" \
            --google-sheets-name "${GOOGLE_SHEETS_NAME}" \
            --google-sheets-client-email "${GOOGLE_SHEETS_CLIENT_EMAIL}" \
            --google-sheets-private-key "${GOOGLE_SHEETS_PRIVATE_KEY}" | jq --unbuffered '.' | jq -r '.id'
    )

    sleep 5

    [ -n "${POST_LINKEDIN_ID}" ] && python3 -m agoras.cli publish \
        --network linkedin \
        --action like \
        --linkedin-access-token "${LINKEDIN_ACCESS_TOKEN}" \
        --linkedin-post-id "${POST_LINKEDIN_ID}" || true

    sleep 5

    [ -n "${SHARED_POST_LINKEDIN_ID}" ] && python3 -m agoras.cli publish \
        --network linkedin \
        --action delete \
        --linkedin-access-token "${LINKEDIN_ACCESS_TOKEN}" \
        --linkedin-post-id "${SHARED_POST_LINKEDIN_ID}" || true

    sleep 5

    [ -n "${POST_LINKEDIN_ID}" ] && python3 -m agoras.cli publish \
        --network linkedin \
        --action delete \
        --linkedin-access-token "${LINKEDIN_ACCESS_TOKEN}" \
        --linkedin-post-id "${POST_LINKEDIN_ID}" || true

    sleep 5

    [ -n "${LAST_FROM_FEED_LINKEDIN_ID}" ] && python3 -m agoras.cli publish \
        --network linkedin \
        --action delete \
        --linkedin-access-token "${LINKEDIN_ACCESS_TOKEN}" \
        --linkedin-post-id "${LAST_FROM_FEED_LINKEDIN_ID}" || true

    sleep 5

    [ -n "${RANDOM_FROM_FEED_LINKEDIN_ID}" ] && python3 -m agoras.cli publish \
        --network linkedin \
        --action delete \
        --linkedin-access-token "${LINKEDIN_ACCESS_TOKEN}" \
        --linkedin-post-id "${RANDOM_FROM_FEED_LINKEDIN_ID}" || true

    sleep 5

    [ -n "${SCHEDULE_LINKEDIN_ID}" ] && python3 -m agoras.cli publish \
        --network linkedin \
        --action delete \
        --linkedin-access-token "${LINKEDIN_ACCESS_TOKEN}" \
        --linkedin-post-id "${SCHEDULE_LINKEDIN_ID}" || true

else
    echo "Unsupported action ${1}"
fi
