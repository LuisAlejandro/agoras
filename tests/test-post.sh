#!/usr/bin/env bash

# Integration Test - End-to-End testing with real API credentials
# Uses the installed agoras CLI command
# Part of agoras v2.0 modular package structure

# Exit early if there are errors and be verbose
set -exuo pipefail

source ../secrets.env

if [ "${1}" == "x" ]; then
    POST_X_ID=$(
        agoras x post \
            --consumer-key "${TWITTER_CONSUMER_KEY}" \
            --consumer-secret "${TWITTER_CONSUMER_SECRET}" \
            --oauth-token "${TWITTER_OAUTH_TOKEN}" \
            --oauth-secret "${TWITTER_OAUTH_SECRET}" \
            --text "${TWITTER_STATUS_TEXT}" \
            --image-1 "${TWITTER_STATUS_IMAGE_URL_1}" | jq --unbuffered '.' | jq -r '.id'
    )

    sleep 5

    [ -n "${POST_X_ID}" ] && agoras x delete \
        --consumer-key "${TWITTER_CONSUMER_KEY}" \
        --consumer-secret "${TWITTER_CONSUMER_SECRET}" \
        --oauth-token "${TWITTER_OAUTH_TOKEN}" \
        --oauth-secret "${TWITTER_OAUTH_SECRET}" \
        --post-id "${POST_X_ID}" || true

elif [ "${1}" == "tiktok" ]; then
    POST_TIKTOK_ID=$(
        agoras tiktok video \
            --client-key "${TIKTOK_CLIENT_KEY}" \
            --client-secret "${TIKTOK_CLIENT_SECRET}" \
            --access-token "${TIKTOK_ACCESS_TOKEN}" \
            --username "${TIKTOK_USERNAME}" \
            --title "${TIKTOK_TITLE}" \
            --video-url "${TIKTOK_VIDEO_URL}" | jq --unbuffered '.' | jq -r '.publish_id'
    )

    echo "TikTok video test created with ID: ${POST_TIKTOK_ID}"
    echo "Note: TikTok does not support delete, like, or share actions"

elif [ "${1}" == "facebook-video" ]; then
    agoras facebook video \
        --access-token "${FACEBOOK_ACCESS_TOKEN}" \
        --app-id "${FACEBOOK_APP_ID}" \
        --object-id "${FACEBOOK_OBJECT_ID}" \
        --video-url "${FACEBOOK_VIDEO_URL}" \
        --video-type "${FACEBOOK_VIDEO_TYPE}" \
        --video-title "${FACEBOOK_VIDEO_TITLE}" \
        --video-description "${FACEBOOK_VIDEO_DESCRIPTION}"

elif [ "${1}" == "youtube" ]; then
    POST_YOUTUBE_ID=$(
        agoras youtube video \
            --client-id "${YOUTUBE_CLIENT_ID}" \
            --client-secret "${YOUTUBE_CLIENT_SECRET}" \
            --title "${YOUTUBE_TITLE}" \
            --video-url "${YOUTUBE_VIDEO_URL}" | jq --unbuffered '.' | jq -r '.id'
    )

    sleep 5

    [ -n "${POST_YOUTUBE_ID}" ] && agoras youtube like \
        --client-id "${YOUTUBE_CLIENT_ID}" \
        --client-secret "${YOUTUBE_CLIENT_SECRET}" \
        --video-id "${POST_YOUTUBE_ID}" || true

    sleep 5

    [ -n "${POST_YOUTUBE_ID}" ] && agoras youtube delete \
        --client-id "${YOUTUBE_CLIENT_ID}" \
        --client-secret "${YOUTUBE_CLIENT_SECRET}" \
        --video-id "${POST_YOUTUBE_ID}" || true

elif [ "${1}" == "facebook" ]; then
    POST_FACEBOOK_ID=$(
        agoras facebook post \
            --access-token "${FACEBOOK_ACCESS_TOKEN}" \
            --object-id "${FACEBOOK_OBJECT_ID}" \
            --text "${FACEBOOK_STATUS_TEXT}" \
            --image-1 "${FACEBOOK_STATUS_IMAGE_URL_1}" | jq --unbuffered '.' | jq -r '.id'
    )

    sleep 5

    SHARED_POST_FACEBOOK_ID=$(
        agoras facebook share \
            --access-token "${FACEBOOK_ACCESS_TOKEN}" \
            --profile-id "${FACEBOOK_PROFILE_ID}" \
            --post-id "${POST_FACEBOOK_ID}" | jq --unbuffered '.' | jq -r '.id'
    )

    sleep 5

    [ -n "${POST_FACEBOOK_ID}" ] && agoras facebook like \
        --access-token "${FACEBOOK_ACCESS_TOKEN}" \
        --post-id "${POST_FACEBOOK_ID}" || true

    sleep 5

    [ -n "${SHARED_POST_FACEBOOK_ID}" ] && agoras facebook delete \
        --access-token "${FACEBOOK_ACCESS_TOKEN}" \
        --post-id "${SHARED_POST_FACEBOOK_ID}" || true

    sleep 5

    [ -n "${POST_FACEBOOK_ID}" ] && agoras facebook delete \
        --access-token "${FACEBOOK_ACCESS_TOKEN}" \
        --post-id "${POST_FACEBOOK_ID}" || true

elif [ "${1}" == "instagram" ]; then
    POST_INSTAGRAM_ID=$(
        agoras instagram post \
            --access-token "${INSTAGRAM_ACCESS_TOKEN}" \
            --object-id "${INSTAGRAM_OBJECT_ID}" \
            --text "${INSTAGRAM_STATUS_TEXT}" \
            --image-1 "${INSTAGRAM_STATUS_IMAGE_URL_1}" | jq --unbuffered '.' | jq -r '.id'
    )

    echo "Instagram post test created with ID: ${POST_INSTAGRAM_ID}"
    echo "Note: Instagram does not support delete, like, or share actions"

elif [ "${1}" == "discord" ]; then
    POST_DISCORD_ID=$(
        agoras discord post \
            --bot-token "${DISCORD_BOT_TOKEN}" \
            --server-name "${DISCORD_SERVER_NAME}" \
            --channel-name "${DISCORD_CHANNEL_NAME}" \
            --text "${DISCORD_STATUS_TEXT}" \
            --image-1 "${DISCORD_STATUS_IMAGE_URL_1}" | jq --unbuffered '.' | jq -r '.id'
    )

    sleep 5

    echo "Note: Discord does not support 'like' action (uses reactions instead)"

    sleep 5

    [ -n "${POST_DISCORD_ID}" ] && agoras discord delete \
        --bot-token "${DISCORD_BOT_TOKEN}" \
        --server-name "${DISCORD_SERVER_NAME}" \
        --channel-name "${DISCORD_CHANNEL_NAME}" \
        --post-id "${POST_DISCORD_ID}" || true

elif [ "${1}" == "linkedin" ]; then
    POST_LINKEDIN_ID=$(
        agoras linkedin post \
            --client-id "${LINKEDIN_CLIENT_ID}" \
            --client-secret "${LINKEDIN_CLIENT_SECRET}" \
            --access-token "${LINKEDIN_ACCESS_TOKEN}" \
            --text "${LINKEDIN_STATUS_TEXT}" \
            --image-1 "${LINKEDIN_STATUS_IMAGE_URL_1}" | jq --unbuffered '.' | jq -r '.id'
    )

    sleep 5

    SHARED_POST_LINKEDIN_ID=$(
        agoras linkedin share \
            --client-id "${LINKEDIN_CLIENT_ID}" \
            --client-secret "${LINKEDIN_CLIENT_SECRET}" \
            --access-token "${LINKEDIN_ACCESS_TOKEN}" \
            --post-id "${POST_LINKEDIN_ID}" | jq --unbuffered '.' | jq -r '.id'
    )

    sleep 5

    [ -n "${POST_LINKEDIN_ID}" ] && agoras linkedin like \
        --client-id "${LINKEDIN_CLIENT_ID}" \
        --client-secret "${LINKEDIN_CLIENT_SECRET}" \
        --access-token "${LINKEDIN_ACCESS_TOKEN}" \
        --post-id "${POST_LINKEDIN_ID}" || true

    sleep 5

    [ -n "${SHARED_POST_LINKEDIN_ID}" ] && agoras linkedin delete \
        --client-id "${LINKEDIN_CLIENT_ID}" \
        --client-secret "${LINKEDIN_CLIENT_SECRET}" \
        --access-token "${LINKEDIN_ACCESS_TOKEN}" \
        --post-id "${SHARED_POST_LINKEDIN_ID}" || true

    sleep 5

    [ -n "${POST_LINKEDIN_ID}" ] && agoras linkedin delete \
        --client-id "${LINKEDIN_CLIENT_ID}" \
        --client-secret "${LINKEDIN_CLIENT_SECRET}" \
        --access-token "${LINKEDIN_ACCESS_TOKEN}" \
        --post-id "${POST_LINKEDIN_ID}" || true

elif [ "${1}" == "threads" ]; then
    POST_THREADS_ID=$(
        agoras threads post \
            --app-id "${THREADS_APP_ID}" \
            --app-secret "${THREADS_APP_SECRET}" \
            --redirect-uri "${THREADS_REDIRECT_URI}" \
            --text "${THREADS_STATUS_TEXT}" \
            --image-1 "${THREADS_STATUS_IMAGE_URL_1}" | jq --unbuffered '.' | jq -r '.id'
    )

    echo "Threads post test created with ID: ${POST_THREADS_ID}"
    echo "Note: Threads does not support delete or like actions"

elif [ "${1}" == "telegram" ]; then
    POST_TELEGRAM_ID=$(
        agoras telegram post \
            --bot-token "${TELEGRAM_BOT_TOKEN}" \
            --chat-id "${TELEGRAM_CHAT_ID}" \
            --text "${TELEGRAM_STATUS_TEXT}" \
            --image-1 "${TELEGRAM_STATUS_IMAGE_URL_1}" | jq --unbuffered '.' | jq -r '.id'
    )

    sleep 5

    [ -n "${POST_TELEGRAM_ID}" ] && agoras telegram delete \
        --bot-token "${TELEGRAM_BOT_TOKEN}" \
        --chat-id "${TELEGRAM_CHAT_ID}" \
        --post-id "${POST_TELEGRAM_ID}" || true

elif [ "${1}" == "whatsapp" ]; then
    POST_WHATSAPP_ID=$(
        agoras whatsapp post \
            --access-token "${WHATSAPP_ACCESS_TOKEN}" \
            --phone-number-id "${WHATSAPP_PHONE_NUMBER_ID}" \
            --recipient "${WHATSAPP_RECIPIENT}" \
            --text "${WHATSAPP_STATUS_TEXT}" \
            --image-1 "${WHATSAPP_STATUS_IMAGE_URL_1}" | jq --unbuffered '.' | jq -r '.id'
    )

    echo "WhatsApp post test created with ID: ${POST_WHATSAPP_ID}"
    echo "Note: WhatsApp does not support delete, like, or share actions"

else
    echo "Unsupported platform ${1}"
    echo "Usage: $0 {x|tiktok|facebook-video|youtube|facebook|instagram|discord|linkedin|threads|telegram|whatsapp}"
fi
