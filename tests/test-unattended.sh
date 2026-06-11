#!/usr/bin/env bash

# Integration Test Master Runner - End-to-End testing with real API credentials
# Orchestrates all integration tests across multiple platforms
# Part of agoras v2.0 modular package structure

# Exit early if there are errors and be verbose
set -exuo pipefail

# Get the absolute path of the script's directory
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
# Get the project root (parent of tests directory)
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

source "${PROJECT_ROOT}/unattended.env"

# Function to clear all stored credentials
clear_credentials() {
    echo "🧹 Clearing all stored credentials..."

    AGORAS_DIR="${AGORAS_STORAGE_DIR}"

    if [ -d "$AGORAS_DIR" ]; then
        # Remove tokens directory
        if [ -d "$AGORAS_DIR/tokens" ]; then
            rm -rf "$AGORAS_DIR/tokens"
            echo "✅ Removed tokens directory"
        fi

        # Remove encryption key file
        if [ -f "$AGORAS_DIR/.key" ]; then
            rm -f "$AGORAS_DIR/.key"
            echo "✅ Removed encryption key file"
        fi

        # Remove entire agoras directory if empty
        if [ -z "$(ls -A "$AGORAS_DIR" 2>/dev/null)" ]; then
            rmdir "$AGORAS_DIR"
            echo "✅ Removed agoras config directory (was empty)"
        fi
    else
        echo "ℹ️  No credentials directory found at $AGORAS_DIR"
    fi

    echo "🎉 All stored credentials cleared from $AGORAS_DIR!"
    echo ""
}

# Always clear credentials before running unattended tests
clear_credentials

# Function to verify required environment variables
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
        facebook)
            [[ -z "${FACEBOOK_OBJECT_ID:-}" ]] && missing_vars+=("FACEBOOK_OBJECT_ID")
            [[ -z "${FACEBOOK_CLIENT_ID:-}" ]] && missing_vars+=("FACEBOOK_CLIENT_ID")
            [[ -z "${FACEBOOK_CLIENT_SECRET:-}" ]] && missing_vars+=("FACEBOOK_CLIENT_SECRET")
            [[ -z "${FACEBOOK_REFRESH_TOKEN:-}" ]] && missing_vars+=("FACEBOOK_REFRESH_TOKEN")
            ;;
        facebook-video)
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

    # Common variables for feed and schedule tests
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

# Verify environment variables
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

# Parse command line arguments
PLATFORM="all"

while [[ $# -gt 0 ]]; do
    case $1 in
        *)
            PLATFORM="$1"
            shift
            ;;
    esac
done

# Function to run all test types for a given platform
run_all_tests_for_platform() {
    local platform="$1"

    echo "======================================"
    echo "Testing platform: $platform"
    echo "======================================"

    echo "--- Running POST tests for $platform ---"
    "${SCRIPT_DIR}/test-post-unattended.sh" "$platform"

    echo "✅ All tests completed for $platform"
    echo ""
}

# Function to run Facebook video test (special case)
run_facebook_video_test() {
    echo "--- Running FACEBOOK VIDEO test ---"
    "${SCRIPT_DIR}/test-post-unattended.sh" "facebook-video"
    echo "✅ Facebook video test completed"
    echo ""
}

if [ "$PLATFORM" == "all" ]; then
    echo "🚀 Running comprehensive test suite for all platforms"
    echo "======================================================"

    # Test all regular platforms (using x instead of twitter for consistency)
    for platform in x tiktok youtube facebook instagram discord linkedin threads telegram whatsapp; do
        run_all_tests_for_platform "$platform"
        sleep 10 # Longer pause between platforms
    done

    # Test Facebook video (special case)
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
    echo "Supported platforms:"
    echo "  all              - Run tests for all platforms (default)"
    echo "  x                - Run all tests for X (formerly Twitter)"
    echo "  tiktok           - Run all tests for TikTok"
    echo "  youtube          - Run all tests for YouTube"
    echo "  facebook         - Run all tests for Facebook"
    echo "  facebook-video   - Run Facebook video test only"
    echo "  instagram        - Run all tests for Instagram"
    echo "  discord          - Run all tests for Discord"
    echo "  linkedin         - Run all tests for LinkedIn"
    echo "  threads          - Run all tests for Threads"
    echo "  telegram         - Run all tests for Telegram"
    echo "  whatsapp         - Run all tests for WhatsApp"
    echo ""
    echo "Test types included:"
    echo "  - Post/Video tests (including like and share)"
    echo "  - Schedule tests"
    echo "  - Last from feed tests"
    echo "  - Random from feed tests"
    exit 1
fi
