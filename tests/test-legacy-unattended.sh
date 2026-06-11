#!/usr/bin/env bash

# Integration Test Master Runner - legacy publish command, unattended credentials via env vars

set -exuo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# shellcheck source=lib/common.sh
source "${SCRIPT_DIR}/lib/common.sh"

source "${PROJECT_ROOT}/unattended.env"

verify_env_vars() {
    local platform=$1
    local missing_vars=()

    case "$platform" in
        x)
            [[ -z "${TWITTER_CONSUMER_KEY:-}" ]] && missing_vars+=("TWITTER_CONSUMER_KEY")
            [[ -z "${TWITTER_CONSUMER_SECRET:-}" ]] && missing_vars+=("TWITTER_CONSUMER_SECRET")
            [[ -z "${TWITTER_OAUTH_TOKEN:-}" ]] && missing_vars+=("TWITTER_OAUTH_TOKEN")
            [[ -z "${TWITTER_OAUTH_SECRET:-}" ]] && missing_vars+=("TWITTER_OAUTH_SECRET")
            ;;
        youtube)
            [[ -z "${YOUTUBE_CLIENT_ID:-}" ]] && missing_vars+=("YOUTUBE_CLIENT_ID")
            [[ -z "${YOUTUBE_CLIENT_SECRET:-}" ]] && missing_vars+=("YOUTUBE_CLIENT_SECRET")
            [[ -z "${YOUTUBE_REFRESH_TOKEN:-}" ]] && missing_vars+=("YOUTUBE_REFRESH_TOKEN")
            ;;
        facebook|facebook-video)
            [[ -z "${FACEBOOK_OBJECT_ID:-}" ]] && missing_vars+=("FACEBOOK_OBJECT_ID")
            [[ -z "${FACEBOOK_CLIENT_ID:-}" ]] && missing_vars+=("FACEBOOK_CLIENT_ID")
            [[ -z "${FACEBOOK_CLIENT_SECRET:-}" ]] && missing_vars+=("FACEBOOK_CLIENT_SECRET")
            [[ -z "${FACEBOOK_REFRESH_TOKEN:-}" ]] && missing_vars+=("FACEBOOK_REFRESH_TOKEN")
            ;;
        instagram)
            [[ -z "${INSTAGRAM_OBJECT_ID:-}" ]] && missing_vars+=("INSTAGRAM_OBJECT_ID")
            [[ -z "${INSTAGRAM_CLIENT_ID:-}" ]] && missing_vars+=("INSTAGRAM_CLIENT_ID")
            [[ -z "${INSTAGRAM_CLIENT_SECRET:-}" ]] && missing_vars+=("INSTAGRAM_CLIENT_SECRET")
            [[ -z "${INSTAGRAM_REFRESH_TOKEN:-}" ]] && missing_vars+=("INSTAGRAM_REFRESH_TOKEN")
            ;;
        discord)
            [[ -z "${DISCORD_BOT_TOKEN:-}" ]] && missing_vars+=("DISCORD_BOT_TOKEN")
            [[ -z "${DISCORD_SERVER_NAME:-}" ]] && missing_vars+=("DISCORD_SERVER_NAME")
            [[ -z "${DISCORD_CHANNEL_NAME:-}" ]] && missing_vars+=("DISCORD_CHANNEL_NAME")
            ;;
        linkedin)
            [[ -z "${LINKEDIN_OBJECT_ID:-}" ]] && missing_vars+=("LINKEDIN_OBJECT_ID")
            [[ -z "${LINKEDIN_CLIENT_ID:-}" ]] && missing_vars+=("LINKEDIN_CLIENT_ID")
            [[ -z "${LINKEDIN_CLIENT_SECRET:-}" ]] && missing_vars+=("LINKEDIN_CLIENT_SECRET")
            [[ -z "${LINKEDIN_REFRESH_TOKEN:-}" ]] && missing_vars+=("LINKEDIN_REFRESH_TOKEN")
            ;;
        tiktok)
            [[ -z "${TIKTOK_USERNAME:-}" ]] && missing_vars+=("TIKTOK_USERNAME")
            [[ -z "${TIKTOK_CLIENT_KEY:-}" ]] && missing_vars+=("TIKTOK_CLIENT_KEY")
            [[ -z "${TIKTOK_CLIENT_SECRET:-}" ]] && missing_vars+=("TIKTOK_CLIENT_SECRET")
            [[ -z "${TIKTOK_REFRESH_TOKEN:-}" ]] && missing_vars+=("TIKTOK_REFRESH_TOKEN")
            ;;
        threads)
            [[ -z "${THREADS_APP_ID:-}" ]] && missing_vars+=("THREADS_APP_ID")
            [[ -z "${THREADS_APP_SECRET:-}" ]] && missing_vars+=("THREADS_APP_SECRET")
            [[ -z "${THREADS_REFRESH_TOKEN:-}" ]] && missing_vars+=("THREADS_REFRESH_TOKEN")
            [[ -z "${THREADS_USER_ID:-}" ]] && missing_vars+=("THREADS_USER_ID")
            ;;
        telegram)
            [[ -z "${TELEGRAM_BOT_TOKEN:-}" ]] && missing_vars+=("TELEGRAM_BOT_TOKEN")
            [[ -z "${TELEGRAM_CHAT_ID:-}" ]] && missing_vars+=("TELEGRAM_CHAT_ID")
            ;;
        whatsapp)
            [[ -z "${WHATSAPP_ACCESS_TOKEN:-}" ]] && missing_vars+=("WHATSAPP_ACCESS_TOKEN")
            [[ -z "${WHATSAPP_PHONE_NUMBER_ID:-}" ]] && missing_vars+=("WHATSAPP_PHONE_NUMBER_ID")
            [[ -z "${WHATSAPP_RECIPIENT:-}" ]] && missing_vars+=("WHATSAPP_RECIPIENT")
            ;;
    esac

    if [[ "$platform" != "facebook-video" ]]; then
        [[ -z "${FEED_URL:-}" ]] && missing_vars+=("FEED_URL")
        [[ -z "${GOOGLE_SHEETS_ID:-}" ]] && missing_vars+=("GOOGLE_SHEETS_ID")
        [[ -z "${GOOGLE_SHEETS_NAME:-}" ]] && missing_vars+=("GOOGLE_SHEETS_NAME")
        [[ -z "${GOOGLE_SHEETS_CLIENT_EMAIL:-}" ]] && missing_vars+=("GOOGLE_SHEETS_CLIENT_EMAIL")
        [[ -z "${GOOGLE_SHEETS_PRIVATE_KEY:-}" ]] && missing_vars+=("GOOGLE_SHEETS_PRIVATE_KEY")
    fi

    if [ ${#missing_vars[@]} -gt 0 ]; then
        echo "❌ Missing required environment variables for $platform:"
        printf '  - %s\n' "${missing_vars[@]}"
        exit 1
    fi

    echo "✅ All required environment variables for $platform are set"
}

normalize_platform_arg() {
    local platform="$1"
    if [[ "${platform}" == "twitter" ]]; then
        echo "x"
    else
        echo "${platform}"
    fi
}

PLATFORM="all"

while [[ $# -gt 0 ]]; do
    case $1 in
        *)
            PLATFORM="$1"
            shift
            ;;
    esac
done

assert_ci_not_set
init_agoras_bin "${PROJECT_ROOT}"
verify_agoras_storage_dir
clear_credentials

echo "🔍 Verifying environment variables..."
verify_env_vars "x"
verify_env_vars "tiktok"
verify_env_vars "youtube"
verify_env_vars "facebook"
verify_env_vars "facebook-video"
verify_env_vars "instagram"
verify_env_vars "discord"
verify_env_vars "linkedin"
verify_env_vars "threads"
verify_env_vars "telegram"
verify_env_vars "whatsapp"
echo "✅ All environment variables verified"
echo ""

run_legacy_utils_if_applicable() {
    if [[ "${PLATFORM}" == "facebook-video" ]]; then
        skip_case "legacy utils tests skipped for facebook-video-only run"
        return 0
    fi
    run_legacy_utils_unattended
}

run_all_tests_for_platform() {
    local platform
    platform="$(normalize_platform_arg "$1")"

    echo "======================================"
    echo "Testing platform (legacy publish): $platform"
    echo "======================================"

    echo "--- Running legacy publish tests for $platform ---"
    "${SCRIPT_DIR}/test-legacy-publish-unattended.sh" "$platform"

    echo "✅ All legacy publish tests completed for $platform"
    echo ""
}

run_facebook_video_test() {
    echo "--- Running FACEBOOK VIDEO legacy publish test ---"
    "${SCRIPT_DIR}/test-legacy-publish-unattended.sh" "facebook-video"
    echo "✅ Facebook video legacy publish test completed"
    echo ""
}

PLATFORM="$(normalize_platform_arg "${PLATFORM}")"

if [ "$PLATFORM" == "all" ]; then
    echo "🚀 Running comprehensive legacy publish unattended test suite"
    echo "============================================================"

    for platform in x tiktok youtube facebook instagram discord linkedin threads telegram whatsapp; do
        run_all_tests_for_platform "$platform"
        sleep "${INTER_PLATFORM_SLEEP}"
    done

    run_facebook_video_test
    run_legacy_utils_if_applicable

    echo "🎉 All legacy publish platform tests completed successfully!"

elif [ "$PLATFORM" == "facebook-video" ]; then
    run_facebook_video_test

elif [ "$PLATFORM" == "x" ] || [ "$PLATFORM" == "tiktok" ] || [ "$PLATFORM" == "youtube" ] || [ "$PLATFORM" == "facebook" ] || [ "$PLATFORM" == "instagram" ] || [ "$PLATFORM" == "discord" ] || [ "$PLATFORM" == "linkedin" ] || [ "$PLATFORM" == "threads" ] || [ "$PLATFORM" == "telegram" ] || [ "$PLATFORM" == "whatsapp" ]; then
    run_all_tests_for_platform "$PLATFORM"
    run_legacy_utils_if_applicable

else
    echo "❌ Unsupported platform: $PLATFORM"
    exit 1
fi
