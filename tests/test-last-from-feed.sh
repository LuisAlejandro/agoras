#!/usr/bin/env bash

# Integration Test - End-to-End testing with real API credentials
# Uses the installed "${PROJECT_ROOT}/virtualenv/bin/agoras" CLI command
# Part of "${PROJECT_ROOT}/virtualenv/bin/agoras" v2.0 modular package structure

# Exit early if there are errors and be verbose
set -exuo pipefail

# Get the absolute path of the script's directory
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
# Get the project root (parent of tests directory)
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

source "${PROJECT_ROOT}/secrets.env"

if [ "${1}" == "x" ]; then
    LAST_FROM_FEED_X_ID=$(
        "${PROJECT_ROOT}/virtualenv/bin/agoras" utils feed-publish \
            --network x \
            --mode last \
            --x-consumer-key "${TWITTER_CONSUMER_KEY}" \
            --x-consumer-secret "${TWITTER_CONSUMER_SECRET}" \
            --x-oauth-token "${TWITTER_OAUTH_TOKEN}" \
            --x-oauth-secret "${TWITTER_OAUTH_SECRET}" \
            --feed-url "${FEED_URL}" \
            --max-count 1 \
            --post-lookback "${POST_LOOKBACK}" | jq --unbuffered '.' | jq -r '.id'
    )

    sleep 5

    [ -n "${LAST_FROM_FEED_X_ID}" ] && "${PROJECT_ROOT}/virtualenv/bin/agoras" x delete \
        --consumer-key "${TWITTER_CONSUMER_KEY}" \
        --consumer-secret "${TWITTER_CONSUMER_SECRET}" \
        --oauth-token "${TWITTER_OAUTH_TOKEN}" \
        --oauth-secret "${TWITTER_OAUTH_SECRET}" \
        --post-id "${LAST_FROM_FEED_X_ID}" || true

elif [ "${1}" == "tiktok" ]; then
    LAST_FROM_FEED_TIKTOK_ID=$(
        "${PROJECT_ROOT}/virtualenv/bin/agoras" utils feed-publish \
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
        "${PROJECT_ROOT}/virtualenv/bin/agoras" utils feed-publish \
            --network youtube \
            --mode last \
            --youtube-client-id "${YOUTUBE_CLIENT_ID}" \
            --youtube-client-secret "${YOUTUBE_CLIENT_SECRET}" \
            --feed-url "${FEED_URL}" \
            --max-count 1 \
            --post-lookback "${POST_LOOKBACK}" | jq --unbuffered '.' | jq -r '.id'
    )

    sleep 5

    [ -n "${LAST_FROM_FEED_YOUTUBE_ID}" ] && "${PROJECT_ROOT}/virtualenv/bin/agoras" youtube delete \
        --client-id "${YOUTUBE_CLIENT_ID}" \
        --client-secret "${YOUTUBE_CLIENT_SECRET}" \
        --video-id "${LAST_FROM_FEED_YOUTUBE_ID}" || true

elif [ "${1}" == "facebook" ]; then
    LAST_FROM_FEED_FACEBOOK_ID=$(
        "${PROJECT_ROOT}/virtualenv/bin/agoras" utils feed-publish \
            --network facebook \
            --mode last \
            --facebook-access-token "${FACEBOOK_ACCESS_TOKEN}" \
            --facebook-object-id "${FACEBOOK_OBJECT_ID}" \
            --feed-url "${FEED_URL}" \
            --max-count 1 \
            --post-lookback "${POST_LOOKBACK}" | jq --unbuffered '.' | jq -r '.id'
    )

    sleep 5

    [ -n "${LAST_FROM_FEED_FACEBOOK_ID}" ] && "${PROJECT_ROOT}/virtualenv/bin/agoras" facebook delete \
        --access-token "${FACEBOOK_ACCESS_TOKEN}" \
        --post-id "${LAST_FROM_FEED_FACEBOOK_ID}" || true

elif [ "${1}" == "instagram" ]; then
    LAST_FROM_FEED_INSTAGRAM_ID=$(
        "${PROJECT_ROOT}/virtualenv/bin/agoras" utils feed-publish \
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
        "${PROJECT_ROOT}/virtualenv/bin/agoras" utils feed-publish \
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

    [ -n "${LAST_FROM_FEED_DISCORD_ID}" ] && "${PROJECT_ROOT}/virtualenv/bin/agoras" discord delete \
        --bot-token "${DISCORD_BOT_TOKEN}" \
        --server-name "${DISCORD_SERVER_NAME}" \
        --channel-name "${DISCORD_CHANNEL_NAME}" \
        --post-id "${LAST_FROM_FEED_DISCORD_ID}" || true

elif [ "${1}" == "linkedin" ]; then
    LAST_FROM_FEED_LINKEDIN_ID=$(
        "${PROJECT_ROOT}/virtualenv/bin/agoras" utils feed-publish \
            --network linkedin \
            --mode last \
            --linkedin-client-id "${LINKEDIN_CLIENT_ID}" \
            --linkedin-client-secret "${LINKEDIN_CLIENT_SECRET}" \
            --feed-url "${FEED_URL}" \
            --max-count 1 \
            --post-lookback "${POST_LOOKBACK}" | jq --unbuffered '.' | jq -r '.id'
    )

    sleep 5

    [ -n "${LAST_FROM_FEED_LINKEDIN_ID}" ] && "${PROJECT_ROOT}/virtualenv/bin/agoras" linkedin delete \
        --client-id "${LINKEDIN_CLIENT_ID}" \
        --client-secret "${LINKEDIN_CLIENT_SECRET}" \
        --post-id "${LAST_FROM_FEED_LINKEDIN_ID}" || true

elif [ "${1}" == "threads" ]; then
    LAST_FROM_FEED_THREADS_ID=$(
        "${PROJECT_ROOT}/virtualenv/bin/agoras" utils feed-publish \
            --network threads \
            --mode last \
            --threads-app-id "${THREADS_APP_ID}" \
            --threads-app-secret "${THREADS_APP_SECRET}" \
            --feed-url "${FEED_URL}" \
            --max-count 1 \
            --post-lookback "${POST_LOOKBACK}" | jq --unbuffered '.' | jq -r '.id'
    )

    echo "Threads last from feed test created with ID: ${LAST_FROM_FEED_THREADS_ID}"
    echo "Note: Threads does not support delete action"

elif [ "${1}" == "telegram" ]; then
    LAST_FROM_FEED_TELEGRAM_ID=$(
        "${PROJECT_ROOT}/virtualenv/bin/agoras" utils feed-publish \
            --network telegram \
            --mode last \
            --telegram-bot-token "${TELEGRAM_BOT_TOKEN}" \
            --telegram-chat-id "${TELEGRAM_CHAT_ID}" \
            --feed-url "${FEED_URL}" \
            --max-count 1 \
            --post-lookback "${POST_LOOKBACK}" | jq --unbuffered '.' | jq -r '.id'
    )

    sleep 5

    [ -n "${LAST_FROM_FEED_TELEGRAM_ID}" ] && "${PROJECT_ROOT}/virtualenv/bin/agoras" telegram delete \
        --bot-token "${TELEGRAM_BOT_TOKEN}" \
        --chat-id "${TELEGRAM_CHAT_ID}" \
        --post-id "${LAST_FROM_FEED_TELEGRAM_ID}" || true

elif [ "${1}" == "whatsapp" ]; then
    LAST_FROM_FEED_WHATSAPP_ID=$(
        "${PROJECT_ROOT}/virtualenv/bin/agoras" utils feed-publish \
            --network whatsapp \
            --mode last \
            --whatsapp-access-token "${WHATSAPP_ACCESS_TOKEN}" \
            --whatsapp-phone-number-id "${WHATSAPP_PHONE_NUMBER_ID}" \
            --feed-url "${FEED_URL}" \
            --max-count 1 \
            --post-lookback "${POST_LOOKBACK}" | jq --unbuffered '.' | jq -r '.id'
    )

    echo "WhatsApp last from feed test created with ID: ${LAST_FROM_FEED_WHATSAPP_ID}"
    echo "Note: WhatsApp does not support delete action"

else
    echo "Unsupported platform ${1}"
    echo "Usage: $0 {x|tiktok|youtube|facebook|instagram|discord|linkedin|threads|telegram|whatsapp}"
fi
