#!/usr/bin/env bash

# Exit early if there are errors and be verbose
set -exuo pipefail

source secrets.env

python3 -m utils.schedule "${GOOGLE_SHEETS_ID}" "${GOOGLE_SHEETS_NAME}" "${GOOGLE_SHEETS_CLIENT_EMAIL}" "${GOOGLE_SHEETS_PRIVATE_KEY}"
python3 -m utils.schedule "${GOOGLE_SHEETS_ID}" "Youtube" "${GOOGLE_SHEETS_CLIENT_EMAIL}" "${GOOGLE_SHEETS_PRIVATE_KEY}"
python3 -m utils.schedule "${GOOGLE_SHEETS_ID}" "Tiktok" "${GOOGLE_SHEETS_CLIENT_EMAIL}" "${GOOGLE_SHEETS_PRIVATE_KEY}"

if [ "${1}" == "twitter" ]; then
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

    [ -n "${RANDOM_FROM_FEED_TWEET_ID}" ] && python3 -m agoras.cli publish \
        --network twitter \
        --action delete \
        --twitter-consumer-key "${TWITTER_CONSUMER_KEY}" \
        --twitter-consumer-secret "${TWITTER_CONSUMER_SECRET}" \
        --twitter-oauth-token "${TWITTER_OAUTH_TOKEN}" \
        --twitter-oauth-secret "${TWITTER_OAUTH_SECRET}" \
        --tweet-id "${RANDOM_FROM_FEED_TWEET_ID}" || true

elif [ "${1}" == "tiktok" ]; then
    python3 -m agoras.cli publish \
        --network tiktok \
        --action authorize \
        --tiktok-username "${TIKTOK_USERNAME}" \
        --tiktok-client-key "${TIKTOK_CLIENT_KEY}" \
        --tiktok-client-secret "${TIKTOK_CLIENT_SECRET}"

    RANDOM_FROM_FEED_TIKTOK_ID=$(
        python3 -m agoras.cli publish \
            --network tiktok \
            --action random-from-feed \
            --tiktok-username "${TIKTOK_USERNAME}" \
            --tiktok-client-key "${TIKTOK_CLIENT_KEY}" \
            --tiktok-client-secret "${TIKTOK_CLIENT_SECRET}" \
            --feed-url "${FEED_URL}" \
            --max-post-age 365 | jq --unbuffered '.' | jq -r '.publish_id'
    )

    echo "TikTok random from feed test created with ID: ${RANDOM_FROM_FEED_TIKTOK_ID}"
    echo "Note: TikTok does not support delete action"

elif [ "${1}" == "youtube" ]; then
    RANDOM_FROM_FEED_YOUTUBE_ID=$(
        python3 -m agoras.cli publish \
            --network youtube \
            --action random-from-feed \
            --youtube-client-id "${YOUTUBE_CLIENT_ID}" \
            --youtube-client-secret "${YOUTUBE_CLIENT_SECRET}" \
            --feed-url "${FEED_URL}" \
            --max-post-age 365 | jq --unbuffered '.' | jq -r '.id'
    )

    sleep 5

    [ -n "${RANDOM_FROM_FEED_YOUTUBE_ID}" ] && python3 -m agoras.cli publish \
        --network youtube \
        --action delete \
        --youtube-client-id "${YOUTUBE_CLIENT_ID}" \
        --youtube-client-secret "${YOUTUBE_CLIENT_SECRET}" \
        --youtube-video-id "${RANDOM_FROM_FEED_YOUTUBE_ID}" || true

elif [ "${1}" == "facebook" ]; then
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

    [ -n "${RANDOM_FROM_FEED_FACEBOOK_ID}" ] && python3 -m agoras.cli publish \
        --network facebook \
        --action delete \
        --facebook-access-token "${FACEBOOK_ACCESS_TOKEN}" \
        --facebook-object-id "${FACEBOOK_OBJECT_ID}" \
        --facebook-post-id "${RANDOM_FROM_FEED_FACEBOOK_ID}" || true

elif [ "${1}" == "instagram" ]; then
    RANDOM_FROM_FEED_INSTAGRAM_ID=$(
        python3 -m agoras.cli publish \
            --network instagram \
            --action random-from-feed \
            --instagram-access-token "${INSTAGRAM_ACCESS_TOKEN}" \
            --instagram-object-id "${INSTAGRAM_OBJECT_ID}" \
            --feed-url "${FEED_URL}" \
            --max-post-age 365 | jq --unbuffered '.' | jq -r '.id'
    )

    echo "Instagram random from feed test created with ID: ${RANDOM_FROM_FEED_INSTAGRAM_ID}"
    echo "Note: Instagram does not support delete action"

elif [ "${1}" == "discord" ]; then
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

    [ -n "${RANDOM_FROM_FEED_DISCORD_ID}" ] && python3 -m agoras.cli publish \
        --network discord \
        --action delete \
        --discord-bot-token "${DISCORD_BOT_TOKEN}" \
        --discord-server-name "${DISCORD_SERVER_NAME}" \
        --discord-channel-name "${DISCORD_CHANNEL_NAME}" \
        --discord-post-id "${RANDOM_FROM_FEED_DISCORD_ID}" || true

elif [ "${1}" == "linkedin" ]; then
    RANDOM_FROM_FEED_LINKEDIN_ID=$(
        python3 -m agoras.cli publish \
            --network linkedin \
            --action random-from-feed \
            --linkedin-client-id "${LINKEDIN_CLIENT_ID}" \
            --linkedin-client-secret "${LINKEDIN_CLIENT_SECRET}" \
            --linkedin-access-token "${LINKEDIN_ACCESS_TOKEN}" \
            --feed-url "${FEED_URL}" \
            --max-post-age 365 | jq --unbuffered '.' | jq -r '.id'
    )

    sleep 5

    [ -n "${RANDOM_FROM_FEED_LINKEDIN_ID}" ] && python3 -m agoras.cli publish \
        --network linkedin \
        --action delete \
        --linkedin-client-id "${LINKEDIN_CLIENT_ID}" \
        --linkedin-client-secret "${LINKEDIN_CLIENT_SECRET}" \
        --linkedin-access-token "${LINKEDIN_ACCESS_TOKEN}" \
        --linkedin-post-id "${RANDOM_FROM_FEED_LINKEDIN_ID}" || true

else
    echo "Unsupported platform ${1}"
    echo "Usage: $0 {twitter|tiktok|youtube|facebook|instagram|discord|linkedin}"
fi 