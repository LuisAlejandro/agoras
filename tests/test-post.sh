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
    POST_X_ID=$(
        "${PROJECT_ROOT}/virtualenv/bin/agoras" x post \
            --text "${TWITTER_STATUS_TEXT}" \
            --image-1 "${TWITTER_STATUS_IMAGE_URL_1}" | tee /dev/stderr | jq --unbuffered '.' | jq -r '.id'
    )

    sleep 5

    [ -n "${POST_X_ID}" ] && "${PROJECT_ROOT}/virtualenv/bin/agoras" x delete \
        --post-id "${POST_X_ID}" || true

elif [ "${1}" == "tiktok" ]; then
    POST_TIKTOK_ID=$(
        "${PROJECT_ROOT}/virtualenv/bin/agoras" tiktok video \
            --title "${TIKTOK_TITLE}" \
            --video-url "${TIKTOK_VIDEO_URL}" | tee /dev/stderr | jq --unbuffered '.' | jq -r '.publish_id'
    )

    echo "TikTok video test created with ID: ${POST_TIKTOK_ID}"
    echo "Note: TikTok does not support delete, like, or share actions"

elif [ "${1}" == "facebook-video" ]; then
    "${PROJECT_ROOT}/virtualenv/bin/agoras" facebook video \
        --video-url "${FACEBOOK_VIDEO_URL}" \
        --video-type "${FACEBOOK_VIDEO_TYPE}" \
        --video-title "${FACEBOOK_VIDEO_TITLE}" \
        --video-description "${FACEBOOK_VIDEO_DESCRIPTION}"

elif [ "${1}" == "youtube" ]; then
    POST_YOUTUBE_ID=$(
        "${PROJECT_ROOT}/virtualenv/bin/agoras" youtube video \
            --title "${YOUTUBE_TITLE}" \
            --video-url "${YOUTUBE_VIDEO_URL}" | tee /dev/stderr | jq --unbuffered '.' | jq -r '.id'
    )

    sleep 5

    [ -n "${POST_YOUTUBE_ID}" ] && "${PROJECT_ROOT}/virtualenv/bin/agoras" youtube like \
        --video-id "${POST_YOUTUBE_ID}" || true

    sleep 5

    [ -n "${POST_YOUTUBE_ID}" ] && "${PROJECT_ROOT}/virtualenv/bin/agoras" youtube delete \
        --video-id "${POST_YOUTUBE_ID}" || true

elif [ "${1}" == "facebook" ]; then
    POST_FACEBOOK_ID=$(
        "${PROJECT_ROOT}/virtualenv/bin/agoras" facebook post \
            --text "${FACEBOOK_STATUS_TEXT}" \
            --image-1 "${FACEBOOK_STATUS_IMAGE_URL_1}" | tee /dev/stderr | jq --unbuffered '.' | jq -r '.id'
    )

    sleep 5

    SHARED_POST_FACEBOOK_ID=$(
        "${PROJECT_ROOT}/virtualenv/bin/agoras" facebook share \
            --profile-id "${FACEBOOK_PROFILE_ID}" \
            --post-id "${POST_FACEBOOK_ID}" | tee /dev/stderr | jq --unbuffered '.' | jq -r '.id'
    )

    sleep 5

    [ -n "${POST_FACEBOOK_ID}" ] && "${PROJECT_ROOT}/virtualenv/bin/agoras" facebook like \
        --post-id "${POST_FACEBOOK_ID}" || true

    sleep 5

    [ -n "${SHARED_POST_FACEBOOK_ID}" ] && "${PROJECT_ROOT}/virtualenv/bin/agoras" facebook delete \
        --post-id "${SHARED_POST_FACEBOOK_ID}" || true

    sleep 5

    [ -n "${POST_FACEBOOK_ID}" ] && "${PROJECT_ROOT}/virtualenv/bin/agoras" facebook delete \
        --post-id "${POST_FACEBOOK_ID}" || true

elif [ "${1}" == "instagram" ]; then
    POST_INSTAGRAM_ID=$(
        "${PROJECT_ROOT}/virtualenv/bin/agoras" instagram post \
            --text "${INSTAGRAM_STATUS_TEXT}" \
            --image-1 "${INSTAGRAM_STATUS_IMAGE_URL_1}" | tee /dev/stderr | jq --unbuffered '.' | jq -r '.id'
    )

    echo "Instagram post test created with ID: ${POST_INSTAGRAM_ID}"
    echo "Note: Instagram does not support delete, like, or share actions"

elif [ "${1}" == "discord" ]; then
    POST_DISCORD_ID=$(
        "${PROJECT_ROOT}/virtualenv/bin/agoras" discord post \
            --text "${DISCORD_STATUS_TEXT}" \
            --image-1 "${DISCORD_STATUS_IMAGE_URL_1}" | tee /dev/stderr | jq --unbuffered '.' | jq -r '.id'
    )

    sleep 5

    echo "Note: Discord does not support 'like' action (uses reactions instead)"

    sleep 5

    [ -n "${POST_DISCORD_ID}" ] && "${PROJECT_ROOT}/virtualenv/bin/agoras" discord delete \
        --post-id "${POST_DISCORD_ID}" || true

elif [ "${1}" == "linkedin" ]; then
    POST_LINKEDIN_ID=$(
        "${PROJECT_ROOT}/virtualenv/bin/agoras" linkedin post \
            --text "${LINKEDIN_STATUS_TEXT}" \
            --image-1 "${LINKEDIN_STATUS_IMAGE_URL_1}" | tee /dev/stderr | jq --unbuffered '.' | jq -r '.id'
    )

    sleep 5

    SHARED_POST_LINKEDIN_ID=$(
        "${PROJECT_ROOT}/virtualenv/bin/agoras" linkedin share \
            --post-id "${POST_LINKEDIN_ID}" | tee /dev/stderr | jq --unbuffered '.' | jq -r '.id'
    )

    sleep 5

    [ -n "${POST_LINKEDIN_ID}" ] && "${PROJECT_ROOT}/virtualenv/bin/agoras" linkedin like \
        --post-id "${POST_LINKEDIN_ID}" || true

    sleep 5

    [ -n "${SHARED_POST_LINKEDIN_ID}" ] && "${PROJECT_ROOT}/virtualenv/bin/agoras" linkedin delete \
        --post-id "${SHARED_POST_LINKEDIN_ID}" || true

    sleep 5

    [ -n "${POST_LINKEDIN_ID}" ] && "${PROJECT_ROOT}/virtualenv/bin/agoras" linkedin delete \
        --post-id "${POST_LINKEDIN_ID}" || true

elif [ "${1}" == "threads" ]; then
    POST_THREADS_ID=$(
        "${PROJECT_ROOT}/virtualenv/bin/agoras" threads post \
            --text "${THREADS_STATUS_TEXT}" \
            --image-1 "${THREADS_STATUS_IMAGE_URL_1}" | tee /dev/stderr | jq --unbuffered '.' | jq -r '.id'
    )

    echo "Threads post test created with ID: ${POST_THREADS_ID}"
    echo "Note: Threads does not support delete or like actions"

elif [ "${1}" == "telegram" ]; then
    POST_TELEGRAM_ID=$(
        "${PROJECT_ROOT}/virtualenv/bin/agoras" telegram post \
            --text "${TELEGRAM_STATUS_TEXT}" \
            --image-1 "${TELEGRAM_STATUS_IMAGE_URL_1}" | tee /dev/stderr | jq --unbuffered '.' | jq -r '.id'
    )

    sleep 5

    [ -n "${POST_TELEGRAM_ID}" ] && "${PROJECT_ROOT}/virtualenv/bin/agoras" telegram delete \
        --post-id "${POST_TELEGRAM_ID}" || true

elif [ "${1}" == "whatsapp" ]; then
    POST_WHATSAPP_ID=$(
        "${PROJECT_ROOT}/virtualenv/bin/agoras" whatsapp post \
            --recipient "${WHATSAPP_RECIPIENT}" \
            --text "${WHATSAPP_STATUS_TEXT}" | tee /dev/stderr | jq --unbuffered '.' | jq -r '.id'
    )

    echo "WhatsApp post test created with ID: ${POST_WHATSAPP_ID}"
    echo "Note: WhatsApp does not support delete, like, or share actions"

else
    echo "Unsupported platform ${1}"
    echo "Usage: $0 {x|tiktok|facebook-video|youtube|facebook|instagram|discord|linkedin|threads|telegram|whatsapp}"
fi
