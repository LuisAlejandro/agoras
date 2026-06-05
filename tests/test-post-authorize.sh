#!/usr/bin/env bash

# Integration Test - End-to-End testing with real API credentials
# Uses the installed "${PROJECT_ROOT}/virtualenv/bin/agoras" CLI command
# Part of "${PROJECT_ROOT}/virtualenv/bin/agoras" v2.0 modular package structure
#
# This script is used by test-authorize.sh and sources authorize.env
# instead of unattended.env. Make sure you have copied authorize.env.example
# to authorize.env and filled in your credentials.

# Exit early if there are errors and be verbose
set -exuo pipefail

# Get the absolute path of the script's directory
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
# Get the project root (parent of tests directory)
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

source "${PROJECT_ROOT}/authorize.env"

if [ "${1}" == "x" ]; then
    POST_X_ID=$(
        "${PROJECT_ROOT}/virtualenv/bin/agoras" x post \
            --text "This is a test post. It should delete itself in a couple of minutes." \
            --image-1 "https://wakatime.com/share/@LuisAlejandro/5a56439c-b3af-44e6-8164-c0b9128872b8.png" | tee /dev/stderr | jq --unbuffered '.' | jq -r '.id'
    )

    sleep 5

    [ -n "${POST_X_ID}" ] && "${PROJECT_ROOT}/virtualenv/bin/agoras" x delete \
        --post-id "${POST_X_ID}" || true

elif [ "${1}" == "tiktok" ]; then
    POST_TIKTOK_ID=$(
        "${PROJECT_ROOT}/virtualenv/bin/agoras" tiktok video \
            --title "This is a test post. It should delete itself in a couple of minutes." \
            --video-url "https://luisalejandro.org/files/videos/test.mp4" | tee /dev/stderr | jq --unbuffered '.' | jq -r '.publish_id'
    )

    echo "TikTok video test created with ID: ${POST_TIKTOK_ID}"
    echo "Note: TikTok does not support delete, like, or share actions"

elif [ "${1}" == "facebook-video" ]; then
    "${PROJECT_ROOT}/virtualenv/bin/agoras" facebook video \
        --video-url "https://luisalejandro.org/files/videos/test.mp4" \
        --video-type "url" \
        --video-title "This is a test post. It should delete itself in a couple of minutes." \
        --video-description "This is a test post. It should delete itself in a couple of minutes."

elif [ "${1}" == "youtube" ]; then
    POST_YOUTUBE_ID=$(
        "${PROJECT_ROOT}/virtualenv/bin/agoras" youtube video \
            --title "This is a test post. It should delete itself in a couple of minutes." \
            --video-url "https://luisalejandro.org/files/videos/test.mp4" | tee /dev/stderr | jq --unbuffered '.' | jq -r '.id'
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
            --text "This is a test post. It should delete itself in a couple of minutes." \
            --image-1 "https://wakatime.com/share/@LuisAlejandro/5a56439c-b3af-44e6-8164-c0b9128872b8.png" | tee /dev/stderr | jq --unbuffered '.' | jq -r '.id'
    )

    sleep 5

    SHARED_POST_FACEBOOK_ID=$(
        "${PROJECT_ROOT}/virtualenv/bin/agoras" facebook share \
            --profile-id "${FACEBOOK_OBJECT_ID}" \
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
            --text "This is a test post. It should delete itself in a couple of minutes." \
            --image-1 "https://wakatime.com/share/@LuisAlejandro/5a56439c-b3af-44e6-8164-c0b9128872b8.png" | tee /dev/stderr | jq --unbuffered '.' | jq -r '.id'
    )

    echo "Instagram post test created with ID: ${POST_INSTAGRAM_ID}"
    echo "Note: Instagram does not support delete, like, or share actions"

elif [ "${1}" == "discord" ]; then
    POST_DISCORD_ID=$(
        "${PROJECT_ROOT}/virtualenv/bin/agoras" discord post \
            --text "This is a test post. It should delete itself in a couple of minutes." \
            --image-1 "https://wakatime.com/share/@LuisAlejandro/5a56439c-b3af-44e6-8164-c0b9128872b8.png" | tee /dev/stderr | jq --unbuffered '.' | jq -r '.id'
    )

    sleep 5

    echo "Note: Discord does not support 'like' action (uses reactions instead)"

    sleep 5

    [ -n "${POST_DISCORD_ID}" ] && "${PROJECT_ROOT}/virtualenv/bin/agoras" discord delete \
        --post-id "${POST_DISCORD_ID}" || true

elif [ "${1}" == "linkedin" ]; then
    POST_LINKEDIN_ID=$(
        "${PROJECT_ROOT}/virtualenv/bin/agoras" linkedin post \
            --text "This is a test post. It should delete itself in a couple of minutes." \
            --image-1 "https://wakatime.com/share/@LuisAlejandro/5a56439c-b3af-44e6-8164-c0b9128872b8.png" | tee /dev/stderr | jq --unbuffered '.' | jq -r '.id'
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
            --text "This is a test post. It should delete itself in a couple of minutes." \
            --image-1 "https://wakatime.com/share/@LuisAlejandro/5a56439c-b3af-44e6-8164-c0b9128872b8.png" | tee /dev/stderr | jq --unbuffered '.' | jq -r '.id'
    )

    echo "Threads post test created with ID: ${POST_THREADS_ID}"
    echo "Note: Threads does not support delete or like actions"

elif [ "${1}" == "telegram" ]; then
    POST_TELEGRAM_ID=$(
        "${PROJECT_ROOT}/virtualenv/bin/agoras" telegram post \
            --text "This is a test post. It should delete itself in a couple of minutes." \
            --image-1 "https://wakatime.com/share/@LuisAlejandro/5a56439c-b3af-44e6-8164-c0b9128872b8.png" | tee /dev/stderr | jq --unbuffered '.' | jq -r '.id'
    )

    sleep 5

    [ -n "${POST_TELEGRAM_ID}" ] && "${PROJECT_ROOT}/virtualenv/bin/agoras" telegram delete \
        --post-id "${POST_TELEGRAM_ID}" || true

elif [ "${1}" == "whatsapp" ]; then
    POST_WHATSAPP_ID=$(
        "${PROJECT_ROOT}/virtualenv/bin/agoras" whatsapp post \
            --recipient "${WHATSAPP_RECIPIENT}" \
            --text "This is a test post. It should delete itself in a couple of minutes." | tee /dev/stderr | jq --unbuffered '.' | jq -r '.id'
    )

    echo "WhatsApp post test created with ID: ${POST_WHATSAPP_ID}"
    echo "Note: WhatsApp does not support delete, like, or share actions"

else
    echo "Unsupported platform ${1}"
    echo "Usage: $0 {x|tiktok|facebook-video|youtube|facebook|instagram|discord|linkedin|threads|telegram|whatsapp}"
fi
