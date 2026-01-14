#!/usr/bin/env bash

# Integration Test - End-to-End testing with real API credentials
# Uses the installed agoras CLI command
# Part of agoras v2.0 modular package structure

# Exit early if there are errors and be verbose
set -exuo pipefail

source ../secrets.env

if [ "${1}" == "x" ]; then
    RANDOM_FROM_FEED_X_ID=$(
        agoras utils feed-publish \
            --network x \
            --mode random \
            --x-consumer-key "${TWITTER_CONSUMER_KEY}" \
            --x-consumer-secret "${TWITTER_CONSUMER_SECRET}" \
            --x-oauth-token "${TWITTER_OAUTH_TOKEN}" \
            --x-oauth-secret "${TWITTER_OAUTH_SECRET}" \
            --feed-url "${FEED_URL}" \
            --max-post-age 365 | jq --unbuffered '.' | jq -r '.id'
    )

    sleep 5

    [ -n "${RANDOM_FROM_FEED_X_ID}" ] && agoras x delete \
        --consumer-key "${TWITTER_CONSUMER_KEY}" \
        --consumer-secret "${TWITTER_CONSUMER_SECRET}" \
        --oauth-token "${TWITTER_OAUTH_TOKEN}" \
        --oauth-secret "${TWITTER_OAUTH_SECRET}" \
        --post-id "${RANDOM_FROM_FEED_X_ID}" || true

elif [ "${1}" == "tiktok" ]; then
    RANDOM_FROM_FEED_TIKTOK_ID=$(
        agoras utils feed-publish \
            --network tiktok \
            --mode random \
            --tiktok-username "${TIKTOK_USERNAME}" \
            --tiktok-client-key "${TIKTOK_CLIENT_KEY}" \
            --tiktok-client-secret "${TIKTOK_CLIENT_SECRET}" \
            --tiktok-access-token "${TIKTOK_ACCESS_TOKEN}" \
            --feed-url "${FEED_URL}" \
            --max-post-age 365 | jq --unbuffered '.' | jq -r '.publish_id'
    )

    echo "TikTok random from feed test created with ID: ${RANDOM_FROM_FEED_TIKTOK_ID}"
    echo "Note: TikTok does not support delete action"

elif [ "${1}" == "youtube" ]; then
    RANDOM_FROM_FEED_YOUTUBE_ID=$(
        agoras utils feed-publish \
            --network youtube \
            --mode random \
            --youtube-client-id "${YOUTUBE_CLIENT_ID}" \
            --youtube-client-secret "${YOUTUBE_CLIENT_SECRET}" \
            --feed-url "${FEED_URL}" \
            --max-post-age 365 | jq --unbuffered '.' | jq -r '.id'
    )

    sleep 5

    [ -n "${RANDOM_FROM_FEED_YOUTUBE_ID}" ] && agoras youtube delete \
        --client-id "${YOUTUBE_CLIENT_ID}" \
        --client-secret "${YOUTUBE_CLIENT_SECRET}" \
        --video-id "${RANDOM_FROM_FEED_YOUTUBE_ID}" || true

elif [ "${1}" == "facebook" ]; then
    RANDOM_FROM_FEED_FACEBOOK_ID=$(
        agoras utils feed-publish \
            --network facebook \
            --mode random \
            --facebook-access-token "${FACEBOOK_ACCESS_TOKEN}" \
            --facebook-object-id "${FACEBOOK_OBJECT_ID}" \
            --feed-url "${FEED_URL}" \
            --max-post-age 365 | jq --unbuffered '.' | jq -r '.id'
    )

    sleep 5

    [ -n "${RANDOM_FROM_FEED_FACEBOOK_ID}" ] && agoras facebook delete \
        --access-token "${FACEBOOK_ACCESS_TOKEN}" \
        --post-id "${RANDOM_FROM_FEED_FACEBOOK_ID}" || true

elif [ "${1}" == "instagram" ]; then
    RANDOM_FROM_FEED_INSTAGRAM_ID=$(
        agoras utils feed-publish \
            --network instagram \
            --mode random \
            --instagram-access-token "${INSTAGRAM_ACCESS_TOKEN}" \
            --instagram-object-id "${INSTAGRAM_OBJECT_ID}" \
            --feed-url "${FEED_URL}" \
            --max-post-age 365 | jq --unbuffered '.' | jq -r '.id'
    )

    echo "Instagram random from feed test created with ID: ${RANDOM_FROM_FEED_INSTAGRAM_ID}"
    echo "Note: Instagram does not support delete action"

elif [ "${1}" == "discord" ]; then
    RANDOM_FROM_FEED_DISCORD_ID=$(
        agoras utils feed-publish \
            --network discord \
            --mode random \
            --discord-bot-token "${DISCORD_BOT_TOKEN}" \
            --discord-server-name "${DISCORD_SERVER_NAME}" \
            --discord-channel-name "${DISCORD_CHANNEL_NAME}" \
            --feed-url "${FEED_URL}" \
            --max-post-age 365 | jq --unbuffered '.' | jq -r '.id'
    )

    sleep 5

    [ -n "${RANDOM_FROM_FEED_DISCORD_ID}" ] && agoras discord delete \
        --bot-token "${DISCORD_BOT_TOKEN}" \
        --server-name "${DISCORD_SERVER_NAME}" \
        --channel-name "${DISCORD_CHANNEL_NAME}" \
        --post-id "${RANDOM_FROM_FEED_DISCORD_ID}" || true

elif [ "${1}" == "linkedin" ]; then
    RANDOM_FROM_FEED_LINKEDIN_ID=$(
        agoras utils feed-publish \
            --network linkedin \
            --mode random \
            --linkedin-client-id "${LINKEDIN_CLIENT_ID}" \
            --linkedin-client-secret "${LINKEDIN_CLIENT_SECRET}" \
            --linkedin-access-token "${LINKEDIN_ACCESS_TOKEN}" \
            --feed-url "${FEED_URL}" \
            --max-post-age 365 | jq --unbuffered '.' | jq -r '.id'
    )

    sleep 5

    [ -n "${RANDOM_FROM_FEED_LINKEDIN_ID}" ] && agoras linkedin delete \
        --client-id "${LINKEDIN_CLIENT_ID}" \
        --client-secret "${LINKEDIN_CLIENT_SECRET}" \
        --access-token "${LINKEDIN_ACCESS_TOKEN}" \
        --post-id "${RANDOM_FROM_FEED_LINKEDIN_ID}" || true

else
    echo "Unsupported platform ${1}"
    echo "Usage: $0 {x|tiktok|youtube|facebook|instagram|discord|linkedin}"
fi
