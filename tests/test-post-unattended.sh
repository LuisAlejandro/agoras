#!/usr/bin/env bash

# Platform post cases for unattended-path runner (env var credentials)

set -exuo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# shellcheck source=lib/common.sh
source "${SCRIPT_DIR}/lib/common.sh"

source "${PROJECT_ROOT}/unattended.env"
init_agoras_bin "${PROJECT_ROOT}"

if [ "${1}" == "x" ]; then
    POST_X_ID=$(
        run_agoras x post \
            --text "This is a test post. It should delete itself in a couple of minutes." \
            --image-1 "${TEST_IMAGE_URL}" | tee /dev/stderr | jq --unbuffered '.' | jq -r '.id'
    )

    sleep 5

    if [ -n "${POST_X_ID}" ]; then
        run_agoras x like --post-id "${POST_X_ID}" || true
        sleep 5
        run_agoras x share --post-id "${POST_X_ID}" || true
        sleep 5
        run_agoras x delete --post-id "${POST_X_ID}" || true
    fi

    sleep 5

    set +e
    POST_X_VIDEO_ID=$(
        run_agoras_capture_id '.id' x video \
            --video-url "${TEST_VIDEO_URL}" \
            --video-title "E2E test video"
    )
    x_video_exit=$?
    set -e

    if [ "${x_video_exit}" -ne 0 ] || [ -z "${POST_X_VIDEO_ID}" ]; then
        skip_case "x video upload unavailable or not permitted"
    else
        sleep 5
        run_agoras x delete --post-id "${POST_X_VIDEO_ID}" || true
    fi

elif [ "${1}" == "tiktok" ]; then
    set +e
    POST_TIKTOK_PHOTO_ID=$(
        run_agoras tiktok post \
            --title "This is a test slideshow. It should delete itself in a couple of minutes." \
            --image-1 "${TEST_TIKTOK_IMAGE_URL}" \
            --privacy SELF_ONLY | tee /dev/stderr | jq --unbuffered '.' | jq -r '.publish_id // empty'
    )
    tiktok_post_exit=$?
    set -e

    if [ "${tiktok_post_exit}" -ne 0 ] || [ -z "${POST_TIKTOK_PHOTO_ID}" ]; then
        skip_case "tiktok post slideshow unavailable or not permitted"
    else
        echo "TikTok post test created with ID: ${POST_TIKTOK_PHOTO_ID}"
    fi

    POST_TIKTOK_ID=$(
        run_agoras tiktok video \
            --title "This is a test post. It should delete itself in a couple of minutes." \
            --video-url "${TEST_VIDEO_URL}" | tee /dev/stderr | jq --unbuffered '.' | jq -r '.publish_id'
    )

    echo "TikTok video test created with ID: ${POST_TIKTOK_ID}"
    echo "Note: TikTok does not support delete, like, or share actions"

elif [ "${1}" == "facebook-video" ]; then
    run_agoras facebook video \
        --video-url "${TEST_VIDEO_URL}" \
        --video-type "url" \
        --video-title "This is a test post. It should delete itself in a couple of minutes." \
        --video-description "This is a test post. It should delete itself in a couple of minutes."

elif [ "${1}" == "youtube" ]; then
    POST_YOUTUBE_ID=$(
        run_agoras youtube video \
            --title "This is a test post. It should delete itself in a couple of minutes." \
            --video-url "${TEST_VIDEO_URL}" | tee /dev/stderr | jq --unbuffered '.' | jq -r '.id'
    )

    sleep 5

    [ -n "${POST_YOUTUBE_ID}" ] && run_agoras youtube like --video-id "${POST_YOUTUBE_ID}" || true

    sleep 5

    [ -n "${POST_YOUTUBE_ID}" ] && run_agoras youtube delete --video-id "${POST_YOUTUBE_ID}" || true

elif [ "${1}" == "facebook" ]; then
    POST_FACEBOOK_ID=$(
        run_agoras facebook post \
            --text "This is a test post. It should delete itself in a couple of minutes." \
            --image-1 "${TEST_IMAGE_URL}" | tee /dev/stderr | jq --unbuffered '.' | jq -r '.id'
    )

    sleep 5

    SHARED_POST_FACEBOOK_ID=$(
        run_agoras facebook share \
            --profile-id "${FACEBOOK_OBJECT_ID}" \
            --post-id "${POST_FACEBOOK_ID}" | tee /dev/stderr | jq --unbuffered '.' | jq -r '.id'
    )

    sleep 5

    [ -n "${POST_FACEBOOK_ID}" ] && run_agoras facebook like --post-id "${POST_FACEBOOK_ID}" || true

    sleep 5

    [ -n "${SHARED_POST_FACEBOOK_ID}" ] && run_agoras facebook delete --post-id "${SHARED_POST_FACEBOOK_ID}" || true

    sleep 5

    [ -n "${POST_FACEBOOK_ID}" ] && run_agoras facebook delete --post-id "${POST_FACEBOOK_ID}" || true

elif [ "${1}" == "instagram" ]; then
    POST_INSTAGRAM_ID=$(
        run_agoras instagram post \
            --text "This is a test post. It should delete itself in a couple of minutes." \
            --image-1 "${TEST_IMAGE_URL}" | tee /dev/stderr | jq --unbuffered '.' | jq -r '.id'
    )

    echo "Instagram post test created with ID: ${POST_INSTAGRAM_ID}"

    sleep 5

    try_agoras_or_skip "instagram video upload unavailable or not permitted" \
        run_agoras instagram video \
            --video-url "${TEST_VIDEO_URL}" \
            --video-caption "E2E test video"

elif [ "${1}" == "discord" ]; then
    POST_DISCORD_ID=$(
        run_agoras discord post \
            --text "This is a test post. It should delete itself in a couple of minutes." \
            --image-1 "${TEST_IMAGE_URL}" | tee /dev/stderr | jq --unbuffered '.' | jq -r '.id'
    )

    sleep 5

    try_agoras_or_skip "discord video upload unavailable or file too large" \
        run_agoras discord video --video-url "${TEST_DISCORD_VIDEO_URL}"

    sleep 5

    [ -n "${POST_DISCORD_ID}" ] && run_agoras discord delete --post-id "${POST_DISCORD_ID}" || true

elif [ "${1}" == "linkedin" ]; then
    POST_LINKEDIN_ID=$(
        run_agoras linkedin post \
            --text "This is a test post. It should delete itself in a couple of minutes." \
            --image-1 "${TEST_IMAGE_URL}" | tee /dev/stderr | jq --unbuffered '.' | jq -r '.id'
    )

    sleep 5

    SHARED_POST_LINKEDIN_ID=$(
        run_agoras linkedin share \
            --post-id "${POST_LINKEDIN_ID}" | tee /dev/stderr | jq --unbuffered '.' | jq -r '.id'
    )

    sleep 5

    [ -n "${POST_LINKEDIN_ID}" ] && run_agoras linkedin like --post-id "${POST_LINKEDIN_ID}" || true

    sleep 5

    [ -n "${SHARED_POST_LINKEDIN_ID}" ] && run_agoras linkedin delete --post-id "${SHARED_POST_LINKEDIN_ID}" || true

    sleep 5

    [ -n "${POST_LINKEDIN_ID}" ] && run_agoras linkedin delete --post-id "${POST_LINKEDIN_ID}" || true

    sleep 5

    try_agoras_or_skip "linkedin video upload unavailable or not permitted" \
        run_agoras linkedin video --video-url "${TEST_VIDEO_URL}"

elif [ "${1}" == "threads" ]; then
    POST_THREADS_ID=$(
        run_agoras threads post \
            --text "This is a test post. It should delete itself in a couple of minutes." \
            --image-1 "${TEST_IMAGE_URL}" | tee /dev/stderr | jq --unbuffered '.' | jq -r '.id'
    )

    sleep 5

    if [ -n "${POST_THREADS_ID}" ]; then
        run_agoras threads share --post-id "${POST_THREADS_ID}" || true
    fi

    echo "Threads post test created with ID: ${POST_THREADS_ID}"

    sleep 5

    try_agoras_or_skip "threads video upload unavailable or not permitted" \
        run_agoras threads video \
            --video-url "${TEST_VIDEO_URL}" \
            --video-title "E2E test video"

elif [ "${1}" == "telegram" ]; then
    POST_TELEGRAM_ID=$(
        run_agoras telegram post \
            --text "This is a test post. It should delete itself in a couple of minutes." \
            --image-1 "${TEST_IMAGE_URL}" | tee /dev/stderr | jq --unbuffered '.' | jq -r '.id'
    )

    sleep 5

    set +e
    TELEGRAM_VIDEO_ID=$(
        run_agoras_capture_id '.id' telegram video --video-url "${TEST_VIDEO_URL}"
    )
    telegram_video_exit=$?
    set -e

    if [ "${telegram_video_exit}" -ne 0 ] || [ -z "${TELEGRAM_VIDEO_ID}" ]; then
        skip_case "telegram video send unavailable or not permitted"
    else
        sleep 5
        run_agoras telegram delete --post-id "${TELEGRAM_VIDEO_ID}" || true
    fi

    sleep 5

    [ -n "${POST_TELEGRAM_ID}" ] && run_agoras telegram delete --post-id "${POST_TELEGRAM_ID}" || true

elif [ "${1}" == "whatsapp" ]; then
    POST_WHATSAPP_ID=$(
        run_agoras whatsapp post \
            --recipient "${WHATSAPP_RECIPIENT}" \
            --text "This is a test post. It should delete itself in a couple of minutes." | tee /dev/stderr | jq --unbuffered '.' | jq -r '.id'
    )

    echo "WhatsApp post test created with ID: ${POST_WHATSAPP_ID}"

    sleep 5

    try_agoras_or_skip "whatsapp video send unavailable or not permitted" \
        run_agoras whatsapp video \
            --recipient "${WHATSAPP_RECIPIENT}" \
            --video-url "${TEST_VIDEO_URL}"

    if [ -n "${WHATSAPP_TEMPLATE_NAME:-}" ]; then
        sleep 5
        try_agoras_or_skip "whatsapp template send unavailable or not permitted" \
            run_agoras whatsapp template \
                --recipient "${WHATSAPP_RECIPIENT}" \
                --template-name "${WHATSAPP_TEMPLATE_NAME}" \
                --language-code "${WHATSAPP_TEMPLATE_LANGUAGE:-en}"
    else
        skip_case "whatsapp template skipped (set WHATSAPP_TEMPLATE_NAME in env)"
    fi

else
    echo "Unsupported platform ${1}"
    exit 1
fi
