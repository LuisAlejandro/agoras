#!/bin/bash
# Simple script to authorize platforms using secrets from secrets.env
# Usage: ./authorize.sh [platform-name | all]

# Exit early if there are errors and be verbose
set -exuo pipefail

# Get the absolute path of the script's directory
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
# Get the project root (parent of tests directory)
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Load secrets from secrets.env
if [ ! -f "${PROJECT_ROOT}/secrets.env" ]; then
    echo "Error: ${PROJECT_ROOT}/secrets.env file not found"
    exit 1
fi

source "${PROJECT_ROOT}/secrets.env"

# Get platform from command line argument, default to "all"
TARGET_PLATFORM="${1:-all}"

# Check virtualenv exists and install agoras in development mode
if [ ! -d "${PROJECT_ROOT}/virtualenv" ]; then
    echo "Error: ${PROJECT_ROOT}/virtualenv directory not found"
    exit 1
fi

# Install agoras packages in development mode (in dependency order)
# echo "Installing agoras packages in development mode..."
# "${PROJECT_ROOT}/virtualenv/bin/pip" install -e "${PROJECT_ROOT}/packages/common"
# "${PROJECT_ROOT}/virtualenv/bin/pip" install -e "${PROJECT_ROOT}/packages/media"
# "${PROJECT_ROOT}/virtualenv/bin/pip" install -e "${PROJECT_ROOT}/packages/core"
# "${PROJECT_ROOT}/virtualenv/bin/pip" install -e "${PROJECT_ROOT}/packages/platforms"
# "${PROJECT_ROOT}/virtualenv/bin/pip" install -e "${PROJECT_ROOT}/packages/cli"
# echo "✓ All packages installed in development mode"
# echo ""

# Load secrets from secrets.env
if [ ! -f "${PROJECT_ROOT}/secrets.env" ]; then
    echo "Error: ${PROJECT_ROOT}/secrets.env file not found"
    exit 1
fi

source "${PROJECT_ROOT}/secrets.env"

# Function to verify required environment variables are set
verify_env_vars() {
    local platform=$1
    local missing_vars=()

    case "$platform" in
        x)
            [[ -z "${TWITTER_CONSUMER_KEY:-}" ]] && missing_vars+=("TWITTER_CONSUMER_KEY")
            [[ -z "${TWITTER_CONSUMER_SECRET:-}" ]] && missing_vars+=("TWITTER_CONSUMER_SECRET")
            ;;
        facebook)
            [[ -z "${FACEBOOK_CLIENT_ID:-}" ]] && missing_vars+=("FACEBOOK_CLIENT_ID")
            [[ -z "${FACEBOOK_CLIENT_SECRET:-}" ]] && missing_vars+=("FACEBOOK_CLIENT_SECRET")
            [[ -z "${FACEBOOK_APP_ID:-}" ]] && missing_vars+=("FACEBOOK_APP_ID")
            [[ -z "${FACEBOOK_OBJECT_ID:-}" ]] && missing_vars+=("FACEBOOK_OBJECT_ID")
            ;;
        instagram)
            [[ -z "${INSTAGRAM_CLIENT_ID:-}" ]] && missing_vars+=("INSTAGRAM_CLIENT_ID")
            [[ -z "${INSTAGRAM_CLIENT_SECRET:-}" ]] && missing_vars+=("INSTAGRAM_CLIENT_SECRET")
            [[ -z "${INSTAGRAM_OBJECT_ID:-}" ]] && missing_vars+=("INSTAGRAM_OBJECT_ID")
            ;;
        linkedin)
            [[ -z "${LINKEDIN_CLIENT_ID:-}" ]] && missing_vars+=("LINKEDIN_CLIENT_ID")
            [[ -z "${LINKEDIN_CLIENT_SECRET:-}" ]] && missing_vars+=("LINKEDIN_CLIENT_SECRET")
            [[ -z "${LINKEDIN_OBJECT_ID:-}" ]] && missing_vars+=("LINKEDIN_OBJECT_ID")
            ;;
        discord)
            [[ -z "${DISCORD_BOT_TOKEN:-}" ]] && missing_vars+=("DISCORD_BOT_TOKEN")
            [[ -z "${DISCORD_SERVER_NAME:-}" ]] && missing_vars+=("DISCORD_SERVER_NAME")
            [[ -z "${DISCORD_CHANNEL_NAME:-}" ]] && missing_vars+=("DISCORD_CHANNEL_NAME")
            ;;
        youtube)
            [[ -z "${YOUTUBE_CLIENT_ID:-}" ]] && missing_vars+=("YOUTUBE_CLIENT_ID")
            [[ -z "${YOUTUBE_CLIENT_SECRET:-}" ]] && missing_vars+=("YOUTUBE_CLIENT_SECRET")
            ;;
        tiktok)
            [[ -z "${TIKTOK_CLIENT_KEY:-}" ]] && missing_vars+=("TIKTOK_CLIENT_KEY")
            [[ -z "${TIKTOK_CLIENT_SECRET:-}" ]] && missing_vars+=("TIKTOK_CLIENT_SECRET")
            [[ -z "${TIKTOK_USERNAME:-}" ]] && missing_vars+=("TIKTOK_USERNAME")
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
            ;;
    esac

    if [ ${#missing_vars[@]} -gt 0 ]; then
        echo "❌ Missing required environment variables for $platform:"
        printf '  - %s\n' "${missing_vars[@]}"
        exit 1
    fi

    echo "✅ All required environment variables for $platform are set"
}

# Verify environment variables (will be done per platform or all at once)

# Function to authorize a platform
authorize_platform() {
    local platform="$1"

    echo "======================================"
    echo "Authorizing platform: $platform"
    echo "======================================"

    case "$platform" in
        x)
            "${PROJECT_ROOT}/virtualenv/bin/agoras" "$platform" authorize \
                --consumer-key "${TWITTER_CONSUMER_KEY}" \
                --consumer-secret "${TWITTER_CONSUMER_SECRET}"
            ;;
        facebook)
            "${PROJECT_ROOT}/virtualenv/bin/agoras" "$platform" authorize \
                --client-id "${FACEBOOK_CLIENT_ID}" \
                --client-secret "${FACEBOOK_CLIENT_SECRET}" \
                --app-id "${FACEBOOK_APP_ID}" \
                --object-id "${FACEBOOK_OBJECT_ID}"
            ;;
        instagram)
            "${PROJECT_ROOT}/virtualenv/bin/agoras" "$platform" authorize \
                --client-id "${INSTAGRAM_CLIENT_ID}" \
                --client-secret "${INSTAGRAM_CLIENT_SECRET}" \
                --object-id "${INSTAGRAM_OBJECT_ID}"
            ;;
        linkedin)
            "${PROJECT_ROOT}/virtualenv/bin/agoras" "$platform" authorize \
                --client-id "${LINKEDIN_CLIENT_ID}" \
                --client-secret "${LINKEDIN_CLIENT_SECRET}" \
                --object-id "${LINKEDIN_OBJECT_ID}"
            ;;
        discord)
            "${PROJECT_ROOT}/virtualenv/bin/agoras" "$platform" authorize \
                --bot-token "${DISCORD_BOT_TOKEN}" \
                --server-name "${DISCORD_SERVER_NAME}" \
                --channel-name "${DISCORD_CHANNEL_NAME}"
            ;;
        youtube)
            "${PROJECT_ROOT}/virtualenv/bin/agoras" "$platform" authorize \
                --client-id "${YOUTUBE_CLIENT_ID}" \
                --client-secret "${YOUTUBE_CLIENT_SECRET}"
            ;;
        tiktok)
            "${PROJECT_ROOT}/virtualenv/bin/agoras" "$platform" authorize \
                --client-key "${TIKTOK_CLIENT_KEY}" \
                --client-secret "${TIKTOK_CLIENT_SECRET}" \
                --username "${TIKTOK_USERNAME}"
            ;;
        threads)
            "${PROJECT_ROOT}/virtualenv/bin/agoras" "$platform" authorize \
                --app-id "${THREADS_APP_ID}" \
                --app-secret "${THREADS_APP_SECRET}"
            ;;
        telegram)
            "${PROJECT_ROOT}/virtualenv/bin/agoras" "$platform" authorize \
                --bot-token "${TELEGRAM_BOT_TOKEN}" \
                --chat-id "${TELEGRAM_CHAT_ID}"
            ;;
        whatsapp)
            "${PROJECT_ROOT}/virtualenv/bin/agoras" "$platform" authorize \
                --access-token "${WHATSAPP_ACCESS_TOKEN}" \
                --phone-number-id "${WHATSAPP_PHONE_NUMBER_ID}"
            ;;
        *)
            echo "❌ Unsupported platform: $platform"
            exit 1
            ;;
    esac

    echo "✅ $platform authorized successfully"
    echo ""
}

if [ "$TARGET_PLATFORM" == "all" ]; then
    echo "🚀 Authorizing all platforms"
    echo "============================"

    # Verify environment variables for all platforms
    for platform in x facebook instagram linkedin discord youtube tiktok threads telegram whatsapp; do
        verify_env_vars "$platform"
    done
    echo ""

    # Authorize all platforms
    for platform in x facebook instagram linkedin discord youtube tiktok threads telegram whatsapp; do
        authorize_platform "$platform"
        sleep 2 # Brief pause between platforms
    done

    echo "🎉 All platforms authorized successfully!"

elif [ "$TARGET_PLATFORM" == "x" ] || [ "$TARGET_PLATFORM" == "facebook" ] || [ "$TARGET_PLATFORM" == "instagram" ] || [ "$TARGET_PLATFORM" == "linkedin" ] || [ "$TARGET_PLATFORM" == "discord" ] || [ "$TARGET_PLATFORM" == "youtube" ] || [ "$TARGET_PLATFORM" == "tiktok" ] || [ "$TARGET_PLATFORM" == "threads" ] || [ "$TARGET_PLATFORM" == "telegram" ] || [ "$TARGET_PLATFORM" == "whatsapp" ]; then
    # Verify environment variables for the specific platform
    verify_env_vars "$TARGET_PLATFORM"
    authorize_platform "$TARGET_PLATFORM"

else
    echo "❌ Unsupported platform: $TARGET_PLATFORM"
    echo ""
    echo "Usage: $0 [platform]"
    echo ""
    echo "Supported platforms:"
    echo "  all              - Authorize all platforms (default)"
    echo "  x                - Authorize X (formerly Twitter)"
    echo "  facebook         - Authorize Facebook"
    echo "  instagram        - Authorize Instagram"
    echo "  linkedin         - Authorize LinkedIn"
    echo "  discord          - Authorize Discord"
    echo "  youtube          - Authorize YouTube"
    echo "  tiktok           - Authorize TikTok"
    echo "  threads          - Authorize Threads"
    echo "  telegram         - Authorize Telegram"
    echo "  whatsapp         - Authorize WhatsApp"
    echo ""
    exit 1
fi
