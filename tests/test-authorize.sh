#!/usr/bin/env bash

# Integration Test Master Runner - End-to-End testing after authorization
# Orchestrates all integration tests across multiple platforms
# Assumes 'agoras <platform> authorize' has already been run
# Part of agoras v2.0 modular package structure
#
# This script runs tests using credentials stored after authorization.
# It clears credentials at the start to ensure a clean test state.


# Exit early if there are errors and be verbose
set -exuo pipefail

# Get the absolute path of the script's directory
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
# Get the project root (parent of tests directory)
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

source "${PROJECT_ROOT}/authorize.env"

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

# Function to verify required environment variables
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
        facebook)
            [[ -z "${FACEBOOK_CLIENT_ID:-}" ]] && missing_vars+=("FACEBOOK_CLIENT_ID")
            [[ -z "${FACEBOOK_CLIENT_SECRET:-}" ]] && missing_vars+=("FACEBOOK_CLIENT_SECRET")
            [[ -z "${FACEBOOK_APP_ID:-}" ]] && missing_vars+=("FACEBOOK_APP_ID")
            [[ -z "${FACEBOOK_OBJECT_ID:-}" ]] && missing_vars+=("FACEBOOK_OBJECT_ID")
            ;;
        facebook-video)
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

# Always clear credentials at the start (ensures clean test state)
clear_credentials

# Verify AGORAS_STORAGE_DIR is set
if [ -z "${AGORAS_STORAGE_DIR:-}" ]; then
    echo "❌ Error: AGORAS_STORAGE_DIR environment variable is not set"
    echo ""
    echo "This script requires AGORAS_STORAGE_DIR to be set to prevent accidentally"
    echo "deleting your real credentials in ~/.agoras"
    echo ""
    echo "Please set AGORAS_STORAGE_DIR in authorize.env or export it, for example:"
    echo "  export AGORAS_STORAGE_DIR=/tmp/agoras-test"
    echo ""
    exit 1
fi

# Verify environment variables for all platforms (always, regardless of which platform is tested)
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

# Function to run all test types for a given platform
run_all_tests_for_platform() {
    local platform="$1"

    echo "======================================"
    echo "Testing platform: $platform"
    echo "======================================"

    echo "--- Running POST tests for $platform ---"
    "${SCRIPT_DIR}/test-post-authorize.sh" "$platform"

    echo "✅ All tests completed for $platform"
    echo ""
}

# Function to run Facebook video test (special case)
run_facebook_video_test() {
    echo "--- Running FACEBOOK VIDEO test ---"
    "${SCRIPT_DIR}/test-post-authorize.sh" "facebook-video"
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
    echo ""
    echo "Note: This script assumes 'agoras <platform> authorize' has already been run."
    echo "      AGORAS_STORAGE_DIR environment variable is REQUIRED for safety."
    exit 1
fi
