#!/usr/bin/env bash

# Platform post cases for unattended-path runner (env var credentials)

set -exuo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# shellcheck source=lib/common.sh
source "${SCRIPT_DIR}/lib/common.sh"

load_authorize_env "${PROJECT_ROOT}/unattended.env"
init_agoras_bin "${PROJECT_ROOT}"
trap cleanup_test_posts EXIT

if [ "${1}" == "x" ]; then
    set +e
    POST_X_ID=$(
        run_agoras_capture_id '.id' x post \
            --text "This is a test post. It should delete itself in a couple of minutes." \
            --image-1 "${TEST_IMAGE_URL}"
    )
    x_post_exit=$?
    set -e

    if [ "${x_post_exit}" -ne 0 ] || [ -z "${POST_X_ID}" ]; then
        skip_case "x post unavailable or network error"
    else
        sleep 5

        register_test_post_cleanup x "${POST_X_ID}"
        run_agoras x like --post-id "${POST_X_ID}" || true
        sleep 5
        run_agoras x share --post-id "${POST_X_ID}" || true
        sleep 5
        delete_test_post x "${POST_X_ID}"
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
        register_test_post_cleanup x "${POST_X_VIDEO_ID}"
        sleep 5
        delete_test_post x "${POST_X_VIDEO_ID}"
    fi

    complete_platform_test_cleanup

elif [ "${1}" == "tiktok" ]; then
    set +e
    POST_TIKTOK_PHOTO_ID=$(
        run_agoras_capture_id '.publish_id // .data.publish_id // empty' tiktok post \
            --title "This is a test slideshow. It should delete itself in a couple of minutes." \
            --image-1 "${TEST_TIKTOK_IMAGE_URL}" \
            --privacy SELF_ONLY
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
        run_agoras_capture_id_optional '.publish_id // .data.publish_id' tiktok video \
            --title "This is a test post. It should delete itself in a couple of minutes." \
            --video-url "${TEST_VIDEO_URL}"
    )

    if [ -n "${POST_TIKTOK_ID}" ]; then
        register_test_post_cleanup tiktok "${POST_TIKTOK_ID}"
        echo "TikTok video test created with ID: ${POST_TIKTOK_ID}"
        warn_manual_test_post_cleanup tiktok "${POST_TIKTOK_ID}"
    else
        skip_case "tiktok video unavailable or not permitted"
    fi

    [ -n "${POST_TIKTOK_PHOTO_ID:-}" ] && warn_manual_test_post_cleanup tiktok "${POST_TIKTOK_PHOTO_ID}"

    complete_platform_test_cleanup

elif [ "${1}" == "facebook-video" ]; then
    POST_FACEBOOK_VIDEO_ID=$(
        run_agoras_capture_id_optional '.id' facebook video \
            --video-url "${TEST_VIDEO_URL}" \
            --video-type "url" \
            --video-title "This is a test post. It should delete itself in a couple of minutes." \
            --video-description "This is a test post. It should delete itself in a couple of minutes."
    )

    if [ -z "${POST_FACEBOOK_VIDEO_ID}" ]; then
        skip_case "facebook video unavailable or auth failed"
    else
        register_test_post_cleanup facebook "${POST_FACEBOOK_VIDEO_ID}"

        sleep 5

        delete_test_post facebook "${POST_FACEBOOK_VIDEO_ID}"
    fi

    complete_platform_test_cleanup

elif [ "${1}" == "youtube" ]; then
    POST_YOUTUBE_ID=$(
        run_agoras_capture_id_optional '.id' youtube video \
            --title "This is a test post. It should delete itself in a couple of minutes." \
            --video-url "${TEST_VIDEO_URL}"
    )

    if [ -z "${POST_YOUTUBE_ID}" ]; then
        skip_case "youtube video unavailable or auth failed"
    else
        register_test_post_cleanup youtube "${POST_YOUTUBE_ID}"

        sleep 5

        run_agoras youtube like --video-id "${POST_YOUTUBE_ID}" || true

        sleep 5

        delete_test_post youtube "${POST_YOUTUBE_ID}"
    fi

    complete_platform_test_cleanup

elif [ "${1}" == "facebook" ]; then
    POST_FACEBOOK_ID=$(
        run_agoras_capture_id_optional '.id' facebook post \
            --text "This is a test post. It should delete itself in a couple of minutes." \
            --image-1 "${TEST_IMAGE_URL}"
    )

    if [ -z "${POST_FACEBOOK_ID}" ]; then
        skip_case "facebook post unavailable or auth failed"
    else
        register_test_post_cleanup facebook "${POST_FACEBOOK_ID}"

        sleep 5

        SHARED_POST_FACEBOOK_ID=$(
            run_agoras_capture_id_optional '.id' facebook share \
                --profile-id "${FACEBOOK_OBJECT_ID}" \
                --post-id "${POST_FACEBOOK_ID}"
        )

        if [ -n "${SHARED_POST_FACEBOOK_ID}" ]; then
            register_test_post_cleanup facebook "${SHARED_POST_FACEBOOK_ID}"
        fi

        sleep 5

        run_agoras facebook like --post-id "${POST_FACEBOOK_ID}" || true

        sleep 5

        [ -n "${SHARED_POST_FACEBOOK_ID}" ] && delete_test_post facebook "${SHARED_POST_FACEBOOK_ID}"

        sleep 5

        delete_test_post facebook "${POST_FACEBOOK_ID}"
    fi

    complete_platform_test_cleanup

elif [ "${1}" == "instagram" ]; then
    POST_INSTAGRAM_ID=$(
        run_agoras_capture_id_optional '.id' instagram post \
            --text "This is a test post. It should delete itself in a couple of minutes." \
            --image-1 "${TEST_IMAGE_URL}"
    )

    if [ -z "${POST_INSTAGRAM_ID}" ]; then
        skip_case "instagram post unavailable or auth failed"
    else
        register_test_post_cleanup instagram "${POST_INSTAGRAM_ID}"
        echo "Instagram post test created with ID: ${POST_INSTAGRAM_ID}"

        sleep 5

        set +e
        POST_INSTAGRAM_VIDEO_ID=$(
            run_agoras_capture_id_optional '.id' instagram video \
                --video-url "${TEST_VIDEO_URL}" \
                --video-caption "E2E test video"
        )
        instagram_video_exit=$?
        set -e

        if [ "${instagram_video_exit}" -ne 0 ] || [ -z "${POST_INSTAGRAM_VIDEO_ID}" ]; then
            skip_case "instagram video upload unavailable or not permitted"
            warn_manual_test_post_cleanup instagram "${POST_INSTAGRAM_ID}"
        else
            register_test_post_cleanup instagram "${POST_INSTAGRAM_VIDEO_ID}"
            warn_manual_test_post_cleanup instagram "${POST_INSTAGRAM_ID}"
            warn_manual_test_post_cleanup instagram "${POST_INSTAGRAM_VIDEO_ID}"
        fi
    fi

    complete_platform_test_cleanup

elif [ "${1}" == "discord" ]; then
    POST_DISCORD_ID=$(
        run_agoras_capture_id_optional '.id' discord post \
            --text "This is a test post. It should delete itself in a couple of minutes." \
            --image-1 "${TEST_IMAGE_URL}"
    )

    if [ -z "${POST_DISCORD_ID}" ]; then
        skip_case "discord post unavailable or auth failed"
    else
        register_test_post_cleanup discord "${POST_DISCORD_ID}"

        sleep 5

        set +e
        POST_DISCORD_VIDEO_ID=$(
            run_agoras_capture_id_optional '.id' discord video --video-url "${TEST_DISCORD_VIDEO_URL}"
        )
        discord_video_exit=$?
        set -e

        if [ "${discord_video_exit}" -ne 0 ] || [ -z "${POST_DISCORD_VIDEO_ID}" ]; then
            skip_case "discord video upload unavailable or file too large"
        else
            register_test_post_cleanup discord "${POST_DISCORD_VIDEO_ID}"
            sleep 5
            delete_test_post discord "${POST_DISCORD_VIDEO_ID}"
        fi

        sleep 5

        delete_test_post discord "${POST_DISCORD_ID}"
    fi

    complete_platform_test_cleanup

elif [ "${1}" == "linkedin" ]; then
    POST_LINKEDIN_ID=$(
        run_agoras_capture_id_optional '.id' linkedin post \
            --text "This is a test post. It should delete itself in a couple of minutes." \
            --image-1 "${TEST_IMAGE_URL}"
    )

    if [ -z "${POST_LINKEDIN_ID}" ]; then
        skip_case "linkedin post unavailable or auth failed"
    else
        register_test_post_cleanup linkedin "${POST_LINKEDIN_ID}"

        sleep 5

        SHARED_POST_LINKEDIN_ID=$(
            run_agoras_capture_id_optional '.id' linkedin share \
                --post-id "${POST_LINKEDIN_ID}"
        )

        if [ -n "${SHARED_POST_LINKEDIN_ID}" ]; then
            register_test_post_cleanup linkedin "${SHARED_POST_LINKEDIN_ID}"
        fi

        sleep 5

        run_agoras linkedin like --post-id "${POST_LINKEDIN_ID}" || true

        sleep 5

        [ -n "${SHARED_POST_LINKEDIN_ID}" ] && delete_test_post linkedin "${SHARED_POST_LINKEDIN_ID}"

        sleep 5

        delete_test_post linkedin "${POST_LINKEDIN_ID}"

        sleep 5

        set +e
        POST_LINKEDIN_VIDEO_ID=$(
            run_agoras_capture_id_optional '.id' linkedin video --video-url "${TEST_VIDEO_URL}"
        )
        linkedin_video_exit=$?
        set -e

        if [ "${linkedin_video_exit}" -ne 0 ] || [ -z "${POST_LINKEDIN_VIDEO_ID}" ]; then
            skip_case "linkedin video upload unavailable or not permitted"
        else
            register_test_post_cleanup linkedin "${POST_LINKEDIN_VIDEO_ID}"
            sleep 5
            delete_test_post linkedin "${POST_LINKEDIN_VIDEO_ID}"
        fi
    fi

    complete_platform_test_cleanup

elif [ "${1}" == "threads" ]; then
    POST_THREADS_ID=$(
        run_agoras_capture_id_optional '.id' threads post \
            --text "This is a test post. It should delete itself in a couple of minutes." \
            --image-1 "${TEST_IMAGE_URL}"
    )

    if [ -z "${POST_THREADS_ID}" ]; then
        skip_case "threads post unavailable or auth failed"
    else
        register_test_post_cleanup threads "${POST_THREADS_ID}"

        sleep 5

        SHARED_POST_THREADS_ID=""
        SHARED_POST_THREADS_ID=$(
            run_agoras_capture_id_optional '.id' threads share \
                --post-id "${POST_THREADS_ID}"
        )
        if [ -n "${SHARED_POST_THREADS_ID}" ]; then
            register_test_post_cleanup threads "${SHARED_POST_THREADS_ID}"
        fi

        echo "Threads post test created with ID: ${POST_THREADS_ID}"

        sleep 5

        set +e
        POST_THREADS_VIDEO_ID=$(
            run_agoras_capture_id_optional '.id' threads video \
                --video-url "${TEST_VIDEO_URL}" \
                --video-title "E2E test video"
        )
        threads_video_exit=$?
        set -e

        if [ "${threads_video_exit}" -ne 0 ] || [ -z "${POST_THREADS_VIDEO_ID}" ]; then
            skip_case "threads video upload unavailable or not permitted"
        else
            register_test_post_cleanup threads "${POST_THREADS_VIDEO_ID}"
        fi

        sleep 5

        [ -n "${SHARED_POST_THREADS_ID}" ] && delete_test_post threads "${SHARED_POST_THREADS_ID}"

        sleep 5

        delete_test_post threads "${POST_THREADS_ID}"

        sleep 5

        [ -n "${POST_THREADS_VIDEO_ID:-}" ] && delete_test_post threads "${POST_THREADS_VIDEO_ID}"
    fi

    complete_platform_test_cleanup

elif [ "${1}" == "telegram" ]; then
    POST_TELEGRAM_ID=$(
        run_agoras_capture_id_optional '.id' telegram post \
            --text "This is a test post. It should delete itself in a couple of minutes." \
            --image-1 "${TEST_IMAGE_URL}"
    )

    if [ -z "${POST_TELEGRAM_ID}" ]; then
        skip_case "telegram post unavailable or auth failed"
    else
        register_test_post_cleanup telegram "${POST_TELEGRAM_ID}"

        sleep 5

        set +e
        TELEGRAM_VIDEO_ID=$(
            run_agoras_capture_id_optional '.id' telegram video --video-url "${TEST_VIDEO_URL}"
        )
        telegram_video_exit=$?
        set -e

        if [ "${telegram_video_exit}" -ne 0 ] || [ -z "${TELEGRAM_VIDEO_ID}" ]; then
            skip_case "telegram video send unavailable or not permitted"
        else
            register_test_post_cleanup telegram "${TELEGRAM_VIDEO_ID}"
            sleep 5
            delete_test_post telegram "${TELEGRAM_VIDEO_ID}"
        fi

        sleep 5

        delete_test_post telegram "${POST_TELEGRAM_ID}"
    fi

    complete_platform_test_cleanup

elif [ "${1}" == "whatsapp" ]; then
    POST_WHATSAPP_ID=$(
        run_agoras_capture_id_optional '.id' whatsapp post \
            --recipient "${WHATSAPP_RECIPIENT}" \
            --text "This is a test post. It should delete itself in a couple of minutes."
    )

    if [ -z "${POST_WHATSAPP_ID}" ]; then
        skip_case "whatsapp post unavailable or auth failed"
    else
        register_test_post_cleanup whatsapp "${POST_WHATSAPP_ID}"
        echo "WhatsApp post test created with ID: ${POST_WHATSAPP_ID}"

        sleep 5

        set +e
        POST_WHATSAPP_VIDEO_ID=$(
            run_agoras_capture_id_optional '.id' whatsapp video \
                --recipient "${WHATSAPP_RECIPIENT}" \
                --video-url "${TEST_VIDEO_URL}"
        )
        whatsapp_video_exit=$?
        set -e

        if [ "${whatsapp_video_exit}" -ne 0 ] || [ -z "${POST_WHATSAPP_VIDEO_ID}" ]; then
            skip_case "whatsapp video send unavailable or not permitted"
            warn_manual_test_post_cleanup whatsapp "${POST_WHATSAPP_ID}"
        else
            register_test_post_cleanup whatsapp "${POST_WHATSAPP_VIDEO_ID}"
            warn_manual_test_post_cleanup whatsapp "${POST_WHATSAPP_ID}"
            warn_manual_test_post_cleanup whatsapp "${POST_WHATSAPP_VIDEO_ID}"
        fi

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
    fi

    complete_platform_test_cleanup

else
    echo "Unsupported platform ${1}"
    exit 1
fi
