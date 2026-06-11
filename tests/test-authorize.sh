#!/usr/bin/env bash

# Integration Test Master Runner - End-to-End testing after authorization
# Assumes 'agoras <platform> authorize' has already been run into AGORAS_STORAGE_DIR

set -exuo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# shellcheck source=lib/common.sh
source "${SCRIPT_DIR}/lib/common.sh"

load_authorize_env "${PROJECT_ROOT}/authorize.env"

verify_env_vars() {
    local platform=$1
    local missing_vars=()

    case "$platform" in
        x)
            [[ -z "${TWITTER_CONSUMER_KEY:-}" ]] && missing_vars+=("TWITTER_CONSUMER_KEY")
            [[ -z "${TWITTER_CONSUMER_SECRET:-}" ]] && missing_vars+=("TWITTER_CONSUMER_SECRET")
            ;;
        tiktok)
            [[ -z "${TIKTOK_CLIENT_KEY:-}" ]] && missing_vars+=("TIKTOK_CLIENT_KEY")
            [[ -z "${TIKTOK_CLIENT_SECRET:-}" ]] && missing_vars+=("TIKTOK_CLIENT_SECRET")
            [[ -z "${TIKTOK_USERNAME:-}" ]] && missing_vars+=("TIKTOK_USERNAME")
            ;;
        facebook|facebook-video)
            [[ -z "${FACEBOOK_CLIENT_ID:-}" ]] && missing_vars+=("FACEBOOK_CLIENT_ID")
            [[ -z "${FACEBOOK_CLIENT_SECRET:-}" ]] && missing_vars+=("FACEBOOK_CLIENT_SECRET")
            [[ -z "${FACEBOOK_APP_ID:-}" ]] && missing_vars+=("FACEBOOK_APP_ID")
            [[ -z "${FACEBOOK_OBJECT_ID:-}" ]] && missing_vars+=("FACEBOOK_OBJECT_ID")
            ;;
        youtube)
            [[ -z "${YOUTUBE_CLIENT_ID:-}" ]] && missing_vars+=("YOUTUBE_CLIENT_ID")
            [[ -z "${YOUTUBE_CLIENT_SECRET:-}" ]] && missing_vars+=("YOUTUBE_CLIENT_SECRET")
            ;;
        instagram)
            [[ -z "${INSTAGRAM_CLIENT_ID:-}" ]] && missing_vars+=("INSTAGRAM_CLIENT_ID")
            [[ -z "${INSTAGRAM_CLIENT_SECRET:-}" ]] && missing_vars+=("INSTAGRAM_CLIENT_SECRET")
            [[ -z "${INSTAGRAM_OBJECT_ID:-}" ]] && missing_vars+=("INSTAGRAM_OBJECT_ID")
            ;;
        discord)
            [[ -z "${DISCORD_BOT_TOKEN:-}" ]] && missing_vars+=("DISCORD_BOT_TOKEN")
            [[ -z "${DISCORD_SERVER_NAME:-}" ]] && missing_vars+=("DISCORD_SERVER_NAME")
            [[ -z "${DISCORD_CHANNEL_NAME:-}" ]] && missing_vars+=("DISCORD_CHANNEL_NAME")
            ;;
        linkedin)
            [[ -z "${LINKEDIN_CLIENT_ID:-}" ]] && missing_vars+=("LINKEDIN_CLIENT_ID")
            [[ -z "${LINKEDIN_CLIENT_SECRET:-}" ]] && missing_vars+=("LINKEDIN_CLIENT_SECRET")
            [[ -z "${LINKEDIN_OBJECT_ID:-}" ]] && missing_vars+=("LINKEDIN_OBJECT_ID")
            ;;
        threads)
            [[ -z "${THREADS_APP_ID:-}" ]] && missing_vars+=("THREADS_APP_ID")
            [[ -z "${THREADS_APP_SECRET:-}" ]] && missing_vars+=("THREADS_APP_SECRET")
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

    if [ ${#missing_vars[@]} -gt 0 ]; then
        echo "❌ Missing required environment variables for $platform:"
        printf '  - %s\n' "${missing_vars[@]}"
        exit 1
    fi

    echo "✅ All required environment variables for $platform are set"
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

echo "🔍 Verifying environment variables for all platforms..."
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

run_all_tests_for_platform() {
    local platform="$1"

    echo "======================================"
    echo "Testing platform: $platform"
    echo "======================================"

    preflight_authorize_tokens_for_platform "${platform}"

    echo "--- Running POST tests for $platform ---"
    "${SCRIPT_DIR}/test-post-authorize.sh" "$platform"

    echo "--- Running tokens list smoke for $platform ---"
    case "${platform}" in
        facebook-video) run_tokens_list_smoke "facebook" ;;
        *) run_tokens_list_smoke "${platform}" ;;
    esac

    echo "✅ All tests completed for $platform"
    echo ""
}

run_facebook_video_test() {
    preflight_authorize_tokens "facebook"
    echo "--- Running FACEBOOK VIDEO test ---"
    "${SCRIPT_DIR}/test-post-authorize.sh" "facebook-video"
    run_tokens_list_smoke "facebook"
    echo "✅ Facebook video test completed"
    echo ""
}

if [ "$PLATFORM" == "all" ]; then
    echo "🚀 Running comprehensive authorize-path test suite"
    echo "================================================"

    for platform in x tiktok youtube facebook instagram discord linkedin threads telegram whatsapp; do
        run_all_tests_for_platform "$platform"
        sleep "${INTER_PLATFORM_SLEEP}"
    done

    run_facebook_video_test

    echo "🎉 All platform tests completed successfully!"

elif [ "$PLATFORM" == "facebook-video" ]; then
    run_facebook_video_test

elif [ "$PLATFORM" == "x" ] || [ "$PLATFORM" == "tiktok" ] || [ "$PLATFORM" == "youtube" ] || [ "$PLATFORM" == "facebook" ] || [ "$PLATFORM" == "instagram" ] || [ "$PLATFORM" == "discord" ] || [ "$PLATFORM" == "linkedin" ] || [ "$PLATFORM" == "threads" ] || [ "$PLATFORM" == "telegram" ] || [ "$PLATFORM" == "whatsapp" ]; then
    run_all_tests_for_platform "$PLATFORM"

else
    echo "❌ Unsupported platform: $PLATFORM"
    echo ""
    echo "Usage: $0 [platform]"
    echo ""
    echo "Prereq: agoras <platform> authorize for each OAuth platform into AGORAS_STORAGE_DIR"
    echo "        AGORAS_STORAGE_DIR must be set (never ~/.agoras)"
    exit 1
fi
