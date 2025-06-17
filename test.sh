#!/usr/bin/env bash

# Exit early if there are errors and be verbose
set -exuo pipefail

source secrets.env

# Initial setup - prepare schedules
echo "=== Setting up Google Sheets schedules ==="
python3 -m utils.schedule "${GOOGLE_SHEETS_ID}" "${GOOGLE_SHEETS_NAME}" "${GOOGLE_SHEETS_CLIENT_EMAIL}" "${GOOGLE_SHEETS_PRIVATE_KEY}"
python3 -m utils.schedule "${GOOGLE_SHEETS_ID}" "Youtube" "${GOOGLE_SHEETS_CLIENT_EMAIL}" "${GOOGLE_SHEETS_PRIVATE_KEY}"
python3 -m utils.schedule "${GOOGLE_SHEETS_ID}" "Tiktok" "${GOOGLE_SHEETS_CLIENT_EMAIL}" "${GOOGLE_SHEETS_PRIVATE_KEY}"

# Get platform from command line argument, default to "all"
PLATFORM="${1:-all}"

# Function to run all test types for a given platform
run_all_tests_for_platform() {
    local platform="$1"
    
    echo "======================================"
    echo "Testing platform: $platform"
    echo "======================================"
    
    echo "--- Running POST tests for $platform ---"
    ./test-post.sh "$platform"
    
    echo "--- Running SCHEDULE tests for $platform ---"
    ./test-schedule.sh "$platform"
    
    echo "--- Running LAST FROM FEED tests for $platform ---"
    ./test-last-from-feed.sh "$platform"
    
    echo "--- Running RANDOM FROM FEED tests for $platform ---"
    ./test-random-feed.sh "$platform"
    
    echo "✅ All tests completed for $platform"
    echo ""
}

# Function to run Facebook video test (special case)
run_facebook_video_test() {
    echo "--- Running FACEBOOK VIDEO test ---"
    ./test-post.sh "facebook-video"
    echo "✅ Facebook video test completed"
    echo ""
}

if [ "$PLATFORM" == "all" ]; then
    echo "🚀 Running comprehensive test suite for all platforms"
    echo "======================================================"
    
    # Test all regular platforms
    for platform in twitter youtube facebook instagram discord linkedin; do
        run_all_tests_for_platform "$platform"
        sleep 10  # Longer pause between platforms
    done
    
    # Test TikTok (has special authorization step)
    run_all_tests_for_platform "tiktok"
    sleep 10
    
    # Test Facebook video (special case)
    run_facebook_video_test
    
    echo "🎉 All platform tests completed successfully!"
    
elif [ "$PLATFORM" == "facebook-video" ]; then
    run_facebook_video_test
    
elif [ "$PLATFORM" == "twitter" ] || [ "$PLATFORM" == "tiktok" ] || [ "$PLATFORM" == "youtube" ] || [ "$PLATFORM" == "facebook" ] || [ "$PLATFORM" == "instagram" ] || [ "$PLATFORM" == "discord" ] || [ "$PLATFORM" == "linkedin" ]; then
    run_all_tests_for_platform "$PLATFORM"
    
else
    echo "❌ Unsupported platform: $PLATFORM"
    echo ""
    echo "Usage: $0 [platform]"
    echo ""
    echo "Supported platforms:"
    echo "  all              - Run tests for all platforms (default)"
    echo "  twitter          - Run all tests for Twitter"
    echo "  tiktok           - Run all tests for TikTok"
    echo "  youtube          - Run all tests for YouTube"
    echo "  facebook         - Run all tests for Facebook"
    echo "  facebook-video   - Run Facebook video test only"
    echo "  instagram        - Run all tests for Instagram"
    echo "  discord          - Run all tests for Discord"
    echo "  linkedin         - Run all tests for LinkedIn"
    echo ""
    echo "Test types included:"
    echo "  - Post/Video tests (including like and share)"
    echo "  - Schedule tests"
    echo "  - Last from feed tests"
    echo "  - Random from feed tests"
    exit 1
fi
