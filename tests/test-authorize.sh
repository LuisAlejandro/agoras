#!/usr/bin/env bash

# Integration Test Master Runner - End-to-End testing after authorization
# Assumes 'agoras <platform> authorize' has already been run into AGORAS_STORAGE_DIR

set -exuo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# shellcheck source=lib/common.sh
source "${SCRIPT_DIR}/lib/common.sh"

load_authorize_env "${PROJECT_ROOT}/authorize.env"

# Env vars required at test time (not OAuth app creds — those live in stored tokens).
verify_test_env_vars_for_platform() {
    local platform=$1
    local missing_vars=()

    case "$platform" in
    facebook)
        [[ -z "${FACEBOOK_OBJECT_ID:-}" ]] && missing_vars+=("FACEBOOK_OBJECT_ID")
        ;;
    whatsapp)
        [[ -z "${WHATSAPP_RECIPIENT:-}" ]] && missing_vars+=("WHATSAPP_RECIPIENT")
        ;;
    esac

    if [ ${#missing_vars[@]} -gt 0 ]; then
        echo "❌ Missing test-time environment variables for $platform:"
        printf '  - %s\n' "${missing_vars[@]}"
        exit 1
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
trap cleanup_test_posts EXIT

run_all_tests_for_platform() {
    local platform="$1"

    echo "======================================"
    echo "Testing platform: $platform"
    echo "======================================"

    verify_test_env_vars_for_platform "${platform}"
    preflight_authorize_tokens_for_platform "${platform}"

    echo "--- Running POST tests for $platform ---"
    run_platform_post_tests "${SCRIPT_DIR}/test-post-authorize.sh" "$platform"

    echo "✅ All tests completed for $platform"
    echo ""
}

run_facebook_video_test() {
    preflight_authorize_tokens "facebook"
    echo "--- Running FACEBOOK VIDEO test ---"
    run_platform_post_tests "${SCRIPT_DIR}/test-post-authorize.sh" "facebook-video"
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
