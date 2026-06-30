#!/usr/bin/env bash

# Run agoras <platform> authorize for E2E authorize-path testing.
# Requires authorize.env at repo root (with export AGORAS_STORAGE_DIR).

set -euo pipefail

export PYTHONUNBUFFERED=1
export PYTHONWARNINGS="${PYTHONWARNINGS:-ignore::DeprecationWarning:authlib._joserfc_helpers}"

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# shellcheck source=lib/common.sh
source "${SCRIPT_DIR}/lib/common.sh"

load_authorize_env "${PROJECT_ROOT}/authorize.env"

AUTHORIZE_PLATFORMS=(
    x
    tiktok
    youtube
    facebook
    instagram
    discord
    linkedin
    threads
    telegram
    whatsapp
)

verify_authorize_env_vars() {
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
        ;;
    *)
        echo "❌ Unsupported platform: $platform" >&2
        exit 1
        ;;
    esac

    if [ ${#missing_vars[@]} -gt 0 ]; then
        echo "❌ Missing required environment variables for $platform:" >&2
        printf '  - %s\n' "${missing_vars[@]}" >&2
        exit 1
    fi
}

platform_authorize_hint() {
    local platform="$1"

    case "${platform}" in
    x)
        if [[ -n "${TWITTER_OAUTH_TOKEN:-}" && -n "${TWITTER_OAUTH_SECRET:-}" ]]; then
            echo "ℹ️  OAuth tokens in env — will store credentials without opening a browser."
        else
            echo "ℹ️  Interactive OAuth: contacts api.x.com, opens browser, waits up to 5 min for callback."
            echo "   Ensure your X app callback URL includes https://localhost:3456/callback"
        fi
        ;;
    tiktok | youtube | facebook | instagram | linkedin | threads)
        echo "ℹ️  Interactive OAuth: opens browser, waits up to 5 min for localhost callback."
        ;;
    discord | telegram | whatsapp)
        echo "ℹ️  Stores credentials from env (no browser)."
        ;;
    esac
}

authorize_platform() {
    local platform="$1"

    verify_authorize_env_vars "${platform}"

    echo "======================================"
    echo "Authorizing: ${platform}"
    echo "======================================"
    platform_authorize_hint "${platform}"

    case "${platform}" in
    x)
        run_agoras x authorize \
            --consumer-key "${TWITTER_CONSUMER_KEY}" \
            --consumer-secret "${TWITTER_CONSUMER_SECRET}"
        ;;
    tiktok)
        run_agoras tiktok authorize \
            --client-key "${TIKTOK_CLIENT_KEY}" \
            --client-secret "${TIKTOK_CLIENT_SECRET}" \
            --username "${TIKTOK_USERNAME}"
        ;;
    youtube)
        run_agoras youtube authorize \
            --client-id "${YOUTUBE_CLIENT_ID}" \
            --client-secret "${YOUTUBE_CLIENT_SECRET}"
        ;;
    facebook)
        run_agoras facebook authorize \
            --client-id "${FACEBOOK_CLIENT_ID}" \
            --client-secret "${FACEBOOK_CLIENT_SECRET}" \
            --app-id "${FACEBOOK_APP_ID}" \
            --object-id "${FACEBOOK_OBJECT_ID}"
        ;;
    instagram)
        run_agoras instagram authorize \
            --client-id "${INSTAGRAM_CLIENT_ID}" \
            --client-secret "${INSTAGRAM_CLIENT_SECRET}" \
            --object-id "${INSTAGRAM_OBJECT_ID}"
        ;;
    discord)
        run_agoras discord authorize \
            --bot-token "${DISCORD_BOT_TOKEN}" \
            --server-name "${DISCORD_SERVER_NAME}" \
            --channel-name "${DISCORD_CHANNEL_NAME}"
        ;;
    linkedin)
        run_agoras linkedin authorize \
            --client-id "${LINKEDIN_CLIENT_ID}" \
            --client-secret "${LINKEDIN_CLIENT_SECRET}" \
            --object-id "${LINKEDIN_OBJECT_ID}"
        ;;
    threads)
        run_agoras threads authorize \
            --app-id "${THREADS_APP_ID}" \
            --app-secret "${THREADS_APP_SECRET}"
        ;;
    telegram)
        run_agoras telegram authorize \
            --bot-token "${TELEGRAM_BOT_TOKEN}" \
            --chat-id "${TELEGRAM_CHAT_ID}"
        ;;
    whatsapp)
        run_agoras whatsapp authorize \
            --access-token "${WHATSAPP_ACCESS_TOKEN}" \
            --phone-number-id "${WHATSAPP_PHONE_NUMBER_ID}"
        ;;
    esac

    echo "✅ Authorized ${platform}"
    echo ""
}

usage() {
    cat <<EOF
Usage: $0 [platform]

Run agoras authorize for E2E authorize-path testing.

Prerequisites:
  - authorize.env at repo root (export AGORAS_STORAGE_DIR and platform creds)
  - virtualenv/bin/agoras installed

Platforms:
  all (default)  Authorize every platform used by test-authorize.sh
  x              X (Twitter)
  tiktok         TikTok
  youtube        YouTube
  facebook       Facebook (also used by facebook-video tests)
  instagram      Instagram
  discord        Discord
  linkedin       LinkedIn
  threads        Threads
  telegram       Telegram
  whatsapp       WhatsApp

Examples:
  $0
  $0 facebook
  $0 x

After authorization, run: tests/test-authorize.sh [platform]
EOF
}

PLATFORM="all"

while [[ $# -gt 0 ]]; do
    case $1 in
    -h | --help)
        usage
        exit 0
        ;;
    *)
        PLATFORM="$1"
        shift
        ;;
    esac
done

init_agoras_bin "${PROJECT_ROOT}"
verify_agoras_storage_dir

echo "Using AGORAS_STORAGE_DIR=${AGORAS_STORAGE_DIR}"
echo ""
echo "OAuth platforms need a browser and network access to provider APIs."
echo "If a step appears stuck, check terminal messages (not only the deprecation warning)."
echo ""

if [ "${PLATFORM}" == "all" ]; then
    for platform in "${AUTHORIZE_PLATFORMS[@]}"; do
        authorize_platform "${platform}"
        sleep "${INTER_PLATFORM_SLEEP:-5}"
    done
    echo "🎉 All platforms authorized"
elif [[ " ${AUTHORIZE_PLATFORMS[*]} " == *" ${PLATFORM} "* ]]; then
    authorize_platform "${PLATFORM}"
else
    usage >&2
    exit 1
fi
