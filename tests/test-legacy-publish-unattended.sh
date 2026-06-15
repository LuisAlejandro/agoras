#!/usr/bin/env bash

# Legacy publish command cases for unattended-path runner (env var credentials)

set -exuo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# shellcheck source=lib/common.sh
source "${SCRIPT_DIR}/lib/common.sh"

source "${PROJECT_ROOT}/unattended.env"
init_agoras_bin "${PROJECT_ROOT}"
trap cleanup_test_posts EXIT

if [ "${1}" == "x" ]; then
    POST_X_ID=$(
        run_agoras_capture_id '.id' publish \
            --network twitter \
            --action post \
            --status-text "This is a test post. It should delete itself in a couple of minutes." \
            --status-image-url-1 "${TEST_IMAGE_URL}"
    )

    register_test_post_cleanup x "${POST_X_ID}"

    sleep 5

    if [ -n "${POST_X_ID}" ]; then
        run_agoras publish --network twitter --action like --tweet-id "${POST_X_ID}" || true
        sleep 5
        run_agoras publish --network twitter --action share --tweet-id "${POST_X_ID}" || true
        sleep 5
        run_agoras publish --network twitter --action delete --tweet-id "${POST_X_ID}" || true
    fi

    sleep 5

    set +e
    POST_X_VIDEO_ID=$(
        run_agoras_capture_id '.id' publish \
            --network twitter \
            --action video \
            --twitter-video-url "${TEST_VIDEO_URL}" \
            --twitter-video-title "E2E test video"
    )
    x_video_exit=$?
    set -e

    if [ "${x_video_exit}" -ne 0 ] || [ -z "${POST_X_VIDEO_ID}" ]; then
        skip_case "x video upload unavailable or not permitted"
    else
        register_test_post_cleanup x "${POST_X_VIDEO_ID}"
        sleep 5
        run_agoras publish --network twitter --action delete --tweet-id "${POST_X_VIDEO_ID}" || true
    fi

    complete_platform_test_cleanup

elif [ "${1}" == "tiktok" ]; then
    set +e
    POST_TIKTOK_PHOTO_ID=$(
        run_agoras_capture_id '.publish_id // .data.publish_id // empty' publish \
            --network tiktok \
            --action post \
            --tiktok-title "This is a test slideshow. It should delete itself in a couple of minutes." \
            --status-image-url-1 "${TEST_TIKTOK_IMAGE_URL}" \
            --tiktok-privacy-status SELF_ONLY
    )
    tiktok_post_exit=$?
    set -e

    if [ "${tiktok_post_exit}" -ne 0 ] || [ -z "${POST_TIKTOK_PHOTO_ID}" ]; then
        skip_case "tiktok post slideshow unavailable or not permitted"
    else
        register_test_post_cleanup tiktok "${POST_TIKTOK_PHOTO_ID}"
        echo "TikTok post test created with ID: ${POST_TIKTOK_PHOTO_ID}"
    fi

    POST_TIKTOK_ID=$(
        run_agoras_capture_id '.publish_id // .data.publish_id' publish \
            --network tiktok \
            --action video \
            --tiktok-title "This is a test post. It should delete itself in a couple of minutes." \
            --tiktok-video-url "${TEST_VIDEO_URL}"
    )

    register_test_post_cleanup tiktok "${POST_TIKTOK_ID}"
    echo "TikTok video test created with ID: ${POST_TIKTOK_ID}"
    [ -n "${POST_TIKTOK_PHOTO_ID:-}" ] && warn_manual_test_post_cleanup tiktok "${POST_TIKTOK_PHOTO_ID}"
    warn_manual_test_post_cleanup tiktok "${POST_TIKTOK_ID}"

    complete_platform_test_cleanup

elif [ "${1}" == "facebook-video" ]; then
    POST_FACEBOOK_VIDEO_ID=$(
        run_agoras_capture_id '.id' publish \
            --network facebook \
            --action video \
            --facebook-video-url "${TEST_VIDEO_URL}" \
            --facebook-video-type "url" \
            --facebook-video-title "This is a test post. It should delete itself in a couple of minutes." \
            --facebook-video-description "This is a test post. It should delete itself in a couple of minutes."
    )

    register_test_post_cleanup facebook "${POST_FACEBOOK_VIDEO_ID}"

    sleep 5

    run_agoras publish \
        --network facebook \
        --action delete \
        --facebook-post-id "${POST_FACEBOOK_VIDEO_ID}" || true

    complete_platform_test_cleanup

elif [ "${1}" == "youtube" ]; then
    POST_YOUTUBE_ID=$(
        run_agoras_capture_id '.id' publish \
            --network youtube \
            --action video \
            --youtube-title "This is a test post. It should delete itself in a couple of minutes." \
            --youtube-video-url "${TEST_VIDEO_URL}"
    )

    register_test_post_cleanup youtube "${POST_YOUTUBE_ID}"

    sleep 5

    [ -n "${POST_YOUTUBE_ID}" ] && run_agoras publish \
        --network youtube \
        --action like \
        --youtube-video-id "${POST_YOUTUBE_ID}" || true

    sleep 5

    [ -n "${POST_YOUTUBE_ID}" ] && run_agoras publish \
        --network youtube \
        --action delete \
        --youtube-video-id "${POST_YOUTUBE_ID}" || true

    complete_platform_test_cleanup

elif [ "${1}" == "facebook" ]; then
    POST_FACEBOOK_ID=$(
        run_agoras_capture_id '.id' publish \
            --network facebook \
            --action post \
            --facebook-object-id "${FACEBOOK_OBJECT_ID}" \
            --status-text "This is a test post. It should delete itself in a couple of minutes." \
            --status-image-url-1 "${TEST_IMAGE_URL}"
    )

    register_test_post_cleanup facebook "${POST_FACEBOOK_ID}"

    sleep 5

    SHARED_POST_FACEBOOK_ID=$(
        run_agoras_capture_id '.id' publish \
            --network facebook \
            --action share \
            --facebook-profile-id "${FACEBOOK_OBJECT_ID}" \
            --facebook-post-id "${POST_FACEBOOK_ID}"
    )

    register_test_post_cleanup facebook "${SHARED_POST_FACEBOOK_ID}"

    sleep 5

    [ -n "${POST_FACEBOOK_ID}" ] && run_agoras publish \
        --network facebook \
        --action like \
        --facebook-post-id "${POST_FACEBOOK_ID}" || true

    sleep 5

    [ -n "${SHARED_POST_FACEBOOK_ID}" ] && run_agoras publish \
        --network facebook \
        --action delete \
        --facebook-post-id "${SHARED_POST_FACEBOOK_ID}" || true

    sleep 5

    [ -n "${POST_FACEBOOK_ID}" ] && run_agoras publish \
        --network facebook \
        --action delete \
        --facebook-post-id "${POST_FACEBOOK_ID}" || true

    complete_platform_test_cleanup

elif [ "${1}" == "instagram" ]; then
    POST_INSTAGRAM_ID=$(
        run_agoras_capture_id '.id' publish \
            --network instagram \
            --action post \
            --instagram-object-id "${INSTAGRAM_OBJECT_ID}" \
            --status-text "This is a test post. It should delete itself in a couple of minutes." \
            --status-image-url-1 "${TEST_IMAGE_URL}"
    )

    register_test_post_cleanup instagram "${POST_INSTAGRAM_ID}"
    echo "Instagram post test created with ID: ${POST_INSTAGRAM_ID}"
    warn_manual_test_post_cleanup instagram "${POST_INSTAGRAM_ID}"

    sleep 5

    set +e
    POST_INSTAGRAM_VIDEO_ID=$(
        run_agoras_capture_id '.id' publish \
            --network instagram \
            --action video \
            --instagram-video-url "${TEST_VIDEO_URL}" \
            --instagram-video-caption "E2E test video"
    )
    instagram_video_exit=$?
    set -e

    if [ "${instagram_video_exit}" -ne 0 ] || [ -z "${POST_INSTAGRAM_VIDEO_ID}" ]; then
        skip_case "instagram video upload unavailable or not permitted"
    else
        register_test_post_cleanup instagram "${POST_INSTAGRAM_VIDEO_ID}"
        warn_manual_test_post_cleanup instagram "${POST_INSTAGRAM_VIDEO_ID}"
    fi

    complete_platform_test_cleanup

elif [ "${1}" == "discord" ]; then
    POST_DISCORD_ID=$(
        run_agoras_capture_id '.id' publish \
            --network discord \
            --action post \
            --status-text "This is a test post. It should delete itself in a couple of minutes." \
            --status-image-url-1 "${TEST_IMAGE_URL}"
    )

    register_test_post_cleanup discord "${POST_DISCORD_ID}"

    sleep 5

    set +e
    POST_DISCORD_VIDEO_ID=$(
        run_agoras_capture_id '.id' publish \
            --network discord \
            --action video \
            --discord-video-url "${TEST_DISCORD_VIDEO_URL}"
    )
    discord_video_exit=$?
    set -e

    if [ "${discord_video_exit}" -ne 0 ] || [ -z "${POST_DISCORD_VIDEO_ID}" ]; then
        skip_case "discord video upload unavailable or file too large"
    else
        register_test_post_cleanup discord "${POST_DISCORD_VIDEO_ID}"
        sleep 5
        run_agoras publish \
            --network discord \
            --action delete \
            --discord-post-id "${POST_DISCORD_VIDEO_ID}" || true
    fi

    sleep 5

    [ -n "${POST_DISCORD_ID}" ] && run_agoras publish \
        --network discord \
        --action delete \
        --discord-post-id "${POST_DISCORD_ID}" || true

    complete_platform_test_cleanup

elif [ "${1}" == "linkedin" ]; then
    POST_LINKEDIN_ID=$(
        run_agoras_capture_id '.id' publish \
            --network linkedin \
            --action post \
            --status-text "This is a test post. It should delete itself in a couple of minutes." \
            --status-image-url-1 "${TEST_IMAGE_URL}"
    )

    register_test_post_cleanup linkedin "${POST_LINKEDIN_ID}"

    sleep 5

    SHARED_POST_LINKEDIN_ID=$(
        run_agoras_capture_id '.id' publish \
            --network linkedin \
            --action share \
            --linkedin-post-id "${POST_LINKEDIN_ID}"
    )

    register_test_post_cleanup linkedin "${SHARED_POST_LINKEDIN_ID}"

    sleep 5

    [ -n "${POST_LINKEDIN_ID}" ] && run_agoras publish \
        --network linkedin \
        --action like \
        --linkedin-post-id "${POST_LINKEDIN_ID}" || true

    sleep 5

    [ -n "${SHARED_POST_LINKEDIN_ID}" ] && run_agoras publish \
        --network linkedin \
        --action delete \
        --linkedin-post-id "${SHARED_POST_LINKEDIN_ID}" || true

    sleep 5

    [ -n "${POST_LINKEDIN_ID}" ] && run_agoras publish \
        --network linkedin \
        --action delete \
        --linkedin-post-id "${POST_LINKEDIN_ID}" || true

    sleep 5

    set +e
    POST_LINKEDIN_VIDEO_ID=$(
        env LINKEDIN_VIDEO_URL="${TEST_VIDEO_URL}" \
            run_agoras_capture_id '.id' publish \
                --network linkedin \
                --action video
    )
    linkedin_video_exit=$?
    set -e

    if [ "${linkedin_video_exit}" -ne 0 ] || [ -z "${POST_LINKEDIN_VIDEO_ID}" ]; then
        skip_case "linkedin video upload unavailable or not permitted"
    else
        register_test_post_cleanup linkedin "${POST_LINKEDIN_VIDEO_ID}"
        sleep 5
        run_agoras publish \
            --network linkedin \
            --action delete \
            --linkedin-post-id "${POST_LINKEDIN_VIDEO_ID}" || true
    fi

    complete_platform_test_cleanup

elif [ "${1}" == "threads" ]; then
    POST_THREADS_ID=$(
        run_agoras_capture_id '.id' publish \
            --network threads \
            --action post \
            --status-text "This is a test post. It should delete itself in a couple of minutes." \
            --status-image-url-1 "${TEST_IMAGE_URL}"
    )

    register_test_post_cleanup threads "${POST_THREADS_ID}"

    sleep 5

    SHARED_POST_THREADS_ID=""
    if [ -n "${POST_THREADS_ID}" ]; then
        SHARED_POST_THREADS_ID=$(
            env THREADS_POST_ID="${POST_THREADS_ID}" \
                run_agoras_capture_id '.id' publish \
                    --network threads \
                    --action share
        )
        register_test_post_cleanup threads "${SHARED_POST_THREADS_ID}"
    fi

    echo "Threads post test created with ID: ${POST_THREADS_ID}"

    sleep 5

    set +e
    POST_THREADS_VIDEO_ID=$(
        env THREADS_VIDEO_URL="${TEST_VIDEO_URL}" THREADS_VIDEO_TITLE="E2E test video" \
            run_agoras_capture_id '.id' publish \
                --network threads \
                --action video
    )
    threads_video_exit=$?
    set -e

    if [ "${threads_video_exit}" -ne 0 ] || [ -z "${POST_THREADS_VIDEO_ID}" ]; then
        skip_case "threads video upload unavailable or not permitted"
    else
        register_test_post_cleanup threads "${POST_THREADS_VIDEO_ID}"
    fi

    sleep 5

    [ -n "${SHARED_POST_THREADS_ID}" ] && env THREADS_POST_ID="${SHARED_POST_THREADS_ID}" \
        run_agoras publish --network threads --action delete || true

    sleep 5

    [ -n "${POST_THREADS_ID}" ] && env THREADS_POST_ID="${POST_THREADS_ID}" \
        run_agoras publish --network threads --action delete || true

    sleep 5

    [ -n "${POST_THREADS_VIDEO_ID}" ] && env THREADS_POST_ID="${POST_THREADS_VIDEO_ID}" \
        run_agoras publish --network threads --action delete || true

    complete_platform_test_cleanup

elif [ "${1}" == "telegram" ]; then
    POST_TELEGRAM_ID=$(
        run_agoras_capture_id '.id' publish \
            --network telegram \
            --action post \
            --status-text "This is a test post. It should delete itself in a couple of minutes." \
            --status-image-url-1 "${TEST_IMAGE_URL}"
    )

    register_test_post_cleanup telegram "${POST_TELEGRAM_ID}"

    sleep 5

    set +e
    TELEGRAM_VIDEO_ID=$(
        env VIDEO_URL="${TEST_VIDEO_URL}" \
            run_agoras_capture_id '.id' publish \
                --network telegram \
                --action video
    )
    telegram_video_exit=$?
    set -e

    if [ "${telegram_video_exit}" -ne 0 ] || [ -z "${TELEGRAM_VIDEO_ID}" ]; then
        skip_case "telegram video send unavailable or not permitted"
    else
        register_test_post_cleanup telegram "${TELEGRAM_VIDEO_ID}"
        sleep 5
        env TELEGRAM_MESSAGE_ID="${TELEGRAM_VIDEO_ID}" \
            run_agoras publish --network telegram --action delete || true
    fi

    sleep 5

    [ -n "${POST_TELEGRAM_ID}" ] && env TELEGRAM_MESSAGE_ID="${POST_TELEGRAM_ID}" \
        run_agoras publish --network telegram --action delete || true

    complete_platform_test_cleanup

elif [ "${1}" == "whatsapp" ]; then
    POST_WHATSAPP_ID=$(
        run_agoras_capture_id '.id' publish \
            --network whatsapp \
            --action post \
            --whatsapp-recipient "${WHATSAPP_RECIPIENT}" \
            --status-text "This is a test post. It should delete itself in a couple of minutes."
    )

    register_test_post_cleanup whatsapp "${POST_WHATSAPP_ID}"
    echo "WhatsApp post test created with ID: ${POST_WHATSAPP_ID}"
    warn_manual_test_post_cleanup whatsapp "${POST_WHATSAPP_ID}"

    sleep 5

    set +e
    POST_WHATSAPP_VIDEO_ID=$(
        env VIDEO_URL="${TEST_VIDEO_URL}" \
            run_agoras_capture_id '.id' publish \
                --network whatsapp \
                --action video \
                --whatsapp-recipient "${WHATSAPP_RECIPIENT}"
    )
    whatsapp_video_exit=$?
    set -e

    if [ "${whatsapp_video_exit}" -ne 0 ] || [ -z "${POST_WHATSAPP_VIDEO_ID}" ]; then
        skip_case "whatsapp video send unavailable or not permitted"
    else
        register_test_post_cleanup whatsapp "${POST_WHATSAPP_VIDEO_ID}"
        warn_manual_test_post_cleanup whatsapp "${POST_WHATSAPP_VIDEO_ID}"
    fi

    complete_platform_test_cleanup

else
    echo "Unsupported platform ${1}"
    exit 1
fi
