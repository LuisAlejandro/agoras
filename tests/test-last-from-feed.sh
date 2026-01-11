#!/usr/bin/env bash

# Exit early if there are errors and be verbose
set -exuo pipefail

source ../secrets.env

if [ "${1}" == "twitter" ]; then
    LAST_FROM_FEED_TWEET_ID=$(
        python3 -m agoras.cli utils feed-publish \
            --network twitter \
            --mode last \
            --twitter-consumer-key "${TWITTER_CONSUMER_KEY}" \
            --twitter-consumer-secret "${TWITTER_CONSUMER_SECRET}" \
            --twitter-oauth-token "${TWITTER_OAUTH_TOKEN}" \
            --twitter-oauth-secret "${TWITTER_OAUTH_SECRET}" \
            --feed-url "${FEED_URL}" \
            --max-count 1 \
            --post-lookback "${POST_LOOKBACK}" | jq --unbuffered '.' | jq -r '.id'
    )

    sleep 5

    [ -n "${LAST_FROM_FEED_TWEET_ID}" ] && python3 -m agoras.cli twitter delete \
        --consumer-key "${TWITTER_CONSUMER_KEY}" \
        --consumer-secret "${TWITTER_CONSUMER_SECRET}" \
        --oauth-token "${TWITTER_OAUTH_TOKEN}" \
        --oauth-secret "${TWITTER_OAUTH_SECRET}" \
        --post-id "${LAST_FROM_FEED_TWEET_ID}" || true

elif [ "${1}" == "tiktok" ]; then
    python3 -m agoras.cli tiktok authorize \
        --client-key "${TIKTOK_CLIENT_KEY}" \
        --client-secret "${TIKTOK_CLIENT_SECRET}"

    LAST_FROM_FEED_TIKTOK_ID=$(
        python3 -m agoras.cli utils feed-publish \
            --network tiktok \
            --mode last \
            --tiktok-username "${TIKTOK_USERNAME}" \
            --tiktok-client-key "${TIKTOK_CLIENT_KEY}" \
            --tiktok-client-secret "${TIKTOK_CLIENT_SECRET}" \
            --tiktok-access-token "${TIKTOK_ACCESS_TOKEN}" \
            --feed-url "${FEED_URL}" \
            --max-count 1 \
            --post-lookback "${POST_LOOKBACK}" | jq --unbuffered '.' | jq -r '.publish_id'
    )

    echo "TikTok last from feed test created with ID: ${LAST_FROM_FEED_TIKTOK_ID}"
    echo "Note: TikTok does not support delete action"

elif [ "${1}" == "youtube" ]; then
    LAST_FROM_FEED_YOUTUBE_ID=$(
        python3 -m agoras.cli utils feed-publish \
            --network youtube \
            --mode last \
            --youtube-client-id "${YOUTUBE_CLIENT_ID}" \
            --youtube-client-secret "${YOUTUBE_CLIENT_SECRET}" \
            --feed-url "${FEED_URL}" \
            --max-count 1 \
            --post-lookback "${POST_LOOKBACK}" | jq --unbuffered '.' | jq -r '.id'
    )

    sleep 5

    [ -n "${LAST_FROM_FEED_YOUTUBE_ID}" ] && python3 -m agoras.cli youtube delete \
        --client-id "${YOUTUBE_CLIENT_ID}" \
        --client-secret "${YOUTUBE_CLIENT_SECRET}" \
        --video-id "${LAST_FROM_FEED_YOUTUBE_ID}" || true

elif [ "${1}" == "facebook" ]; then
    LAST_FROM_FEED_FACEBOOK_ID=$(
        python3 -m agoras.cli utils feed-publish \
            --network facebook \
            --mode last \
            --facebook-access-token "${FACEBOOK_ACCESS_TOKEN}" \
            --facebook-object-id "${FACEBOOK_OBJECT_ID}" \
            --feed-url "${FEED_URL}" \
            --max-count 1 \
            --post-lookback "${POST_LOOKBACK}" | jq --unbuffered '.' | jq -r '.id'
    )

    sleep 5

    [ -n "${LAST_FROM_FEED_FACEBOOK_ID}" ] && python3 -m agoras.cli facebook delete \
        --access-token "${FACEBOOK_ACCESS_TOKEN}" \
        --post-id "${LAST_FROM_FEED_FACEBOOK_ID}" || true

elif [ "${1}" == "instagram" ]; then
    LAST_FROM_FEED_INSTAGRAM_ID=$(
        python3 -m agoras.cli utils feed-publish \
            --network instagram \
            --mode last \
            --instagram-access-token "${INSTAGRAM_ACCESS_TOKEN}" \
            --instagram-object-id "${INSTAGRAM_OBJECT_ID}" \
            --feed-url "${FEED_URL}" \
            --max-count 1 \
            --post-lookback "${POST_LOOKBACK}" | jq --unbuffered '.' | jq -r '.id'
    )

    echo "Instagram last from feed test created with ID: ${LAST_FROM_FEED_INSTAGRAM_ID}"
    echo "Note: Instagram does not support delete action"

elif [ "${1}" == "discord" ]; then
    LAST_FROM_FEED_DISCORD_ID=$(
        python3 -m agoras.cli utils feed-publish \
            --network discord \
            --mode last \
            --discord-bot-token "${DISCORD_BOT_TOKEN}" \
            --discord-server-name "${DISCORD_SERVER_NAME}" \
            --discord-channel-name "${DISCORD_CHANNEL_NAME}" \
            --feed-url "${FEED_URL}" \
            --max-count 1 \
            --post-lookback "${POST_LOOKBACK}" | jq --unbuffered '.' | jq -r '.id'
    )

    sleep 5

    [ -n "${LAST_FROM_FEED_DISCORD_ID}" ] && python3 -m agoras.cli discord delete \
        --bot-token "${DISCORD_BOT_TOKEN}" \
        --server-name "${DISCORD_SERVER_NAME}" \
        --channel-name "${DISCORD_CHANNEL_NAME}" \
        --post-id "${LAST_FROM_FEED_DISCORD_ID}" || true

elif [ "${1}" == "linkedin" ]; then
    LAST_FROM_FEED_LINKEDIN_ID=$(
        python3 -m agoras.cli utils feed-publish \
            --network linkedin \
            --mode last \
            --linkedin-client-id "${LINKEDIN_CLIENT_ID}" \
            --linkedin-client-secret "${LINKEDIN_CLIENT_SECRET}" \
            --linkedin-access-token "${LINKEDIN_ACCESS_TOKEN}" \
            --feed-url "${FEED_URL}" \
            --max-count 1 \
            --post-lookback "${POST_LOOKBACK}" | jq --unbuffered '.' | jq -r '.id'
    )

    sleep 5

    [ -n "${LAST_FROM_FEED_LINKEDIN_ID}" ] && python3 -m agoras.cli linkedin delete \
        --client-id "${LINKEDIN_CLIENT_ID}" \
        --client-secret "${LINKEDIN_CLIENT_SECRET}" \
        --access-token "${LINKEDIN_ACCESS_TOKEN}" \
        --post-id "${LAST_FROM_FEED_LINKEDIN_ID}" || true

else
    echo "Unsupported platform ${1}"
    echo "Usage: $0 {twitter|tiktok|youtube|facebook|instagram|discord|linkedin}"
fi
