#!/usr/bin/env bash

# Integration Test - End-to-End testing with real API credentials
# Uses the installed agoras CLI command
# Part of agoras v2.0 modular package structure

# Exit early if there are errors and be verbose
set -exuo pipefail

source ../secrets.env

if [ "${1}" == "twitter" ]; then
    SCHEDULE_TWEET_ID=$(
        agoras utils schedule-run \
            --network twitter \
            --twitter-consumer-key "${TWITTER_CONSUMER_KEY}" \
            --twitter-consumer-secret "${TWITTER_CONSUMER_SECRET}" \
            --twitter-oauth-token "${TWITTER_OAUTH_TOKEN}" \
            --twitter-oauth-secret "${TWITTER_OAUTH_SECRET}" \
            --max-count 1 \
            --sheets-id "${GOOGLE_SHEETS_ID}" \
            --sheets-name "${GOOGLE_SHEETS_NAME}" \
            --sheets-client-email "${GOOGLE_SHEETS_CLIENT_EMAIL}" \
            --sheets-private-key "${GOOGLE_SHEETS_PRIVATE_KEY}" | jq --unbuffered '.' | jq -r '.id'
    )

    sleep 5

    [ -n "${SCHEDULE_TWEET_ID}" ] && agoras publish \
        --network twitter \
        --action delete \
        --twitter-consumer-key "${TWITTER_CONSUMER_KEY}" \
        --twitter-consumer-secret "${TWITTER_CONSUMER_SECRET}" \
        --twitter-oauth-token "${TWITTER_OAUTH_TOKEN}" \
        --twitter-oauth-secret "${TWITTER_OAUTH_SECRET}" \
        --tweet-id "${SCHEDULE_TWEET_ID}" || true

elif [ "${1}" == "tiktok" ]; then
    agoras publish \
        --network tiktok \
        --action authorize \
        --tiktok-username "${TIKTOK_USERNAME}" \
        --tiktok-client-key "${TIKTOK_CLIENT_KEY}" \
        --tiktok-client-secret "${TIKTOK_CLIENT_SECRET}"

    SCHEDULE_TIKTOK_ID=$(
        agoras publish \
            --network tiktok \
            --action schedule \
            --tiktok-username "${TIKTOK_USERNAME}" \
            --tiktok-client-key "${TIKTOK_CLIENT_KEY}" \
            --tiktok-client-secret "${TIKTOK_CLIENT_SECRET}" \
            --max-count 1 \
            --sheets-id "${GOOGLE_SHEETS_ID}" \
            --sheets-name "${GOOGLE_SHEETS_NAME}" \
            --sheets-client-email "${GOOGLE_SHEETS_CLIENT_EMAIL}" \
            --sheets-private-key "${GOOGLE_SHEETS_PRIVATE_KEY}" | jq --unbuffered '.' | jq -r '.publish_id'
    )

    echo "TikTok schedule test created with ID: ${SCHEDULE_TIKTOK_ID}"
    echo "Note: TikTok does not support delete action"

elif [ "${1}" == "youtube" ]; then
    SCHEDULE_YOUTUBE_ID=$(
        agoras publish \
            --network youtube \
            --action schedule \
            --youtube-client-id "${YOUTUBE_CLIENT_ID}" \
            --youtube-client-secret "${YOUTUBE_CLIENT_SECRET}" \
            --max-count 1 \
            --sheets-id "${GOOGLE_SHEETS_ID}" \
            --sheets-name "${GOOGLE_SHEETS_NAME}" \
            --sheets-client-email "${GOOGLE_SHEETS_CLIENT_EMAIL}" \
            --sheets-private-key "${GOOGLE_SHEETS_PRIVATE_KEY}" | jq --unbuffered '.' | jq -r '.id'
    )

    sleep 5

    [ -n "${SCHEDULE_YOUTUBE_ID}" ] && agoras publish \
        --network youtube \
        --action delete \
        --youtube-client-id "${YOUTUBE_CLIENT_ID}" \
        --youtube-client-secret "${YOUTUBE_CLIENT_SECRET}" \
        --youtube-video-id "${SCHEDULE_YOUTUBE_ID}" || true

elif [ "${1}" == "facebook" ]; then
    SCHEDULE_FACEBOOK_ID=$(
        agoras utils schedule-run \
            --network facebook \
            --facebook-access-token "${FACEBOOK_ACCESS_TOKEN}" \
            --facebook-object-id "${FACEBOOK_OBJECT_ID}" \
            --max-count 1 \
            --sheets-id "${GOOGLE_SHEETS_ID}" \
            --sheets-name "${GOOGLE_SHEETS_NAME}" \
            --sheets-client-email "${GOOGLE_SHEETS_CLIENT_EMAIL}" \
            --sheets-private-key "${GOOGLE_SHEETS_PRIVATE_KEY}" | jq --unbuffered '.' | jq -r '.id'
    )

    sleep 5

    [ -n "${SCHEDULE_FACEBOOK_ID}" ] && agoras publish \
        --network facebook \
        --action delete \
        --facebook-access-token "${FACEBOOK_ACCESS_TOKEN}" \
        --facebook-object-id "${FACEBOOK_OBJECT_ID}" \
        --facebook-post-id "${SCHEDULE_FACEBOOK_ID}" || true

elif [ "${1}" == "instagram" ]; then
    SCHEDULE_INSTAGRAM_ID=$(
        agoras utils schedule-run \
            --network instagram \
            --instagram-access-token "${INSTAGRAM_ACCESS_TOKEN}" \
            --instagram-object-id "${INSTAGRAM_OBJECT_ID}" \
            --max-count 1 \
            --sheets-id "${GOOGLE_SHEETS_ID}" \
            --sheets-name "${GOOGLE_SHEETS_NAME}" \
            --sheets-client-email "${GOOGLE_SHEETS_CLIENT_EMAIL}" \
            --sheets-private-key "${GOOGLE_SHEETS_PRIVATE_KEY}" | jq --unbuffered '.' | jq -r '.id'
    )

    echo "Instagram schedule test created with ID: ${SCHEDULE_INSTAGRAM_ID}"
    echo "Note: Instagram does not support delete action"

elif [ "${1}" == "discord" ]; then
    SCHEDULE_DISCORD_ID=$(
        agoras publish \
            --network discord \
            --action schedule \
            --discord-bot-token "${DISCORD_BOT_TOKEN}" \
            --discord-server-name "${DISCORD_SERVER_NAME}" \
            --discord-channel-name "${DISCORD_CHANNEL_NAME}" \
            --max-count 1 \
            --sheets-id "${GOOGLE_SHEETS_ID}" \
            --sheets-name "${GOOGLE_SHEETS_NAME}" \
            --sheets-client-email "${GOOGLE_SHEETS_CLIENT_EMAIL}" \
            --sheets-private-key "${GOOGLE_SHEETS_PRIVATE_KEY}" | jq --unbuffered '.' | jq -r '.id'
    )

    sleep 5

    [ -n "${SCHEDULE_DISCORD_ID}" ] && agoras publish \
        --network discord \
        --action delete \
        --discord-bot-token "${DISCORD_BOT_TOKEN}" \
        --discord-server-name "${DISCORD_SERVER_NAME}" \
        --discord-channel-name "${DISCORD_CHANNEL_NAME}" \
        --discord-post-id "${SCHEDULE_DISCORD_ID}" || true

elif [ "${1}" == "linkedin" ]; then
    SCHEDULE_LINKEDIN_ID=$(
        agoras utils schedule-run \
            --network linkedin \
            --linkedin-client-id "${LINKEDIN_CLIENT_ID}" \
            --linkedin-client-secret "${LINKEDIN_CLIENT_SECRET}" \
            --linkedin-access-token "${LINKEDIN_ACCESS_TOKEN}" \
            --max-count 1 \
            --sheets-id "${GOOGLE_SHEETS_ID}" \
            --sheets-name "${GOOGLE_SHEETS_NAME}" \
            --sheets-client-email "${GOOGLE_SHEETS_CLIENT_EMAIL}" \
            --sheets-private-key "${GOOGLE_SHEETS_PRIVATE_KEY}" | jq --unbuffered '.' | jq -r '.id'
    )

    sleep 5

    [ -n "${SCHEDULE_LINKEDIN_ID}" ] && agoras publish \
        --network linkedin \
        --action delete \
        --linkedin-client-id "${LINKEDIN_CLIENT_ID}" \
        --linkedin-client-secret "${LINKEDIN_CLIENT_SECRET}" \
        --linkedin-access-token "${LINKEDIN_ACCESS_TOKEN}" \
        --linkedin-post-id "${SCHEDULE_LINKEDIN_ID}" || true

else
    echo "Unsupported platform ${1}"
    echo "Usage: $0 {twitter|tiktok|youtube|facebook|instagram|discord|linkedin}"
fi
