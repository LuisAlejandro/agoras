#!/usr/bin/env bash

# Exit early if there are errors and be verbose
set -exuo pipefail

source ../secrets.env

if [ "${1}" == "twitter" ]; then
    POST_TWITTER_ID=$(
        python3 -m agoras.cli twitter post \
            --consumer-key "${TWITTER_CONSUMER_KEY}" \
            --consumer-secret "${TWITTER_CONSUMER_SECRET}" \
            --oauth-token "${TWITTER_OAUTH_TOKEN}" \
            --oauth-secret "${TWITTER_OAUTH_SECRET}" \
            --text "${TWITTER_STATUS_TEXT}" \
            --image-1 "${TWITTER_STATUS_IMAGE_URL_1}" | jq --unbuffered '.' | jq -r '.id'
    )

    sleep 5

    [ -n "${POST_TWITTER_ID}" ] && python3 -m agoras.cli twitter delete \
        --consumer-key "${TWITTER_CONSUMER_KEY}" \
        --consumer-secret "${TWITTER_CONSUMER_SECRET}" \
        --oauth-token "${TWITTER_OAUTH_TOKEN}" \
        --oauth-secret "${TWITTER_OAUTH_SECRET}" \
        --post-id "${POST_TWITTER_ID}" || true

elif [ "${1}" == "tiktok" ]; then
    python3 -m agoras.cli tiktok authorize \
        --client-key "${TIKTOK_CLIENT_KEY}" \
        --client-secret "${TIKTOK_CLIENT_SECRET}"

    POST_TIKTOK_ID=$(
        python3 -m agoras.cli tiktok video \
            --client-key "${TIKTOK_CLIENT_KEY}" \
            --client-secret "${TIKTOK_CLIENT_SECRET}" \
            --access-token "${TIKTOK_ACCESS_TOKEN}" \
            --username "${TIKTOK_USERNAME}" \
            --title "${TIKTOK_TITLE}" \
            --video-url "${TIKTOK_VIDEO_URL}" | jq --unbuffered '.' | jq -r '.publish_id'
    )

    echo "TikTok video test created with ID: ${POST_TIKTOK_ID}"
    echo "Note: TikTok does not support delete, like, or share actions"

elif [ "${1}" == "facebook-video" ]; then
    python3 -m agoras.cli facebook video \
        --access-token "${FACEBOOK_ACCESS_TOKEN}" \
        --app-id "${FACEBOOK_APP_ID}" \
        --object-id "${FACEBOOK_OBJECT_ID}" \
        --video-url "${FACEBOOK_VIDEO_URL}" \
        --video-type "${FACEBOOK_VIDEO_TYPE}" \
        --video-title "${FACEBOOK_VIDEO_TITLE}" \
        --video-description "${FACEBOOK_VIDEO_DESCRIPTION}"

elif [ "${1}" == "youtube" ]; then
    POST_YOUTUBE_ID=$(
        python3 -m agoras.cli youtube video \
            --client-id "${YOUTUBE_CLIENT_ID}" \
            --client-secret "${YOUTUBE_CLIENT_SECRET}" \
            --title "${YOUTUBE_TITLE}" \
            --video-url "${YOUTUBE_VIDEO_URL}" | jq --unbuffered '.' | jq -r '.id'
    )

    sleep 5

    [ -n "${POST_YOUTUBE_ID}" ] && python3 -m agoras.cli youtube like \
        --client-id "${YOUTUBE_CLIENT_ID}" \
        --client-secret "${YOUTUBE_CLIENT_SECRET}" \
        --video-id "${POST_YOUTUBE_ID}" || true

    sleep 5

    [ -n "${POST_YOUTUBE_ID}" ] && python3 -m agoras.cli youtube delete \
        --client-id "${YOUTUBE_CLIENT_ID}" \
        --client-secret "${YOUTUBE_CLIENT_SECRET}" \
        --video-id "${POST_YOUTUBE_ID}" || true

elif [ "${1}" == "facebook" ]; then
    POST_FACEBOOK_ID=$(
        python3 -m agoras.cli facebook post \
            --access-token "${FACEBOOK_ACCESS_TOKEN}" \
            --object-id "${FACEBOOK_OBJECT_ID}" \
            --text "${FACEBOOK_STATUS_TEXT}" \
            --image-1 "${FACEBOOK_STATUS_IMAGE_URL_1}" | jq --unbuffered '.' | jq -r '.id'
    )

    sleep 5

    SHARED_POST_FACEBOOK_ID=$(
        python3 -m agoras.cli facebook share \
            --access-token "${FACEBOOK_ACCESS_TOKEN}" \
            --profile-id "${FACEBOOK_PROFILE_ID}" \
            --post-id "${POST_FACEBOOK_ID}" | jq --unbuffered '.' | jq -r '.id'
    )

    sleep 5

    [ -n "${POST_FACEBOOK_ID}" ] && python3 -m agoras.cli facebook like \
        --access-token "${FACEBOOK_ACCESS_TOKEN}" \
        --post-id "${POST_FACEBOOK_ID}" || true

    sleep 5

    [ -n "${SHARED_POST_FACEBOOK_ID}" ] && python3 -m agoras.cli facebook delete \
        --access-token "${FACEBOOK_ACCESS_TOKEN}" \
        --post-id "${SHARED_POST_FACEBOOK_ID}" || true

    sleep 5

    [ -n "${POST_FACEBOOK_ID}" ] && python3 -m agoras.cli facebook delete \
        --access-token "${FACEBOOK_ACCESS_TOKEN}" \
        --post-id "${POST_FACEBOOK_ID}" || true

elif [ "${1}" == "instagram" ]; then
    POST_INSTAGRAM_ID=$(
        python3 -m agoras.cli instagram post \
            --access-token "${INSTAGRAM_ACCESS_TOKEN}" \
            --object-id "${INSTAGRAM_OBJECT_ID}" \
            --text "${INSTAGRAM_STATUS_TEXT}" \
            --image-1 "${INSTAGRAM_STATUS_IMAGE_URL_1}" | jq --unbuffered '.' | jq -r '.id'
    )

    echo "Instagram post test created with ID: ${POST_INSTAGRAM_ID}"
    echo "Note: Instagram does not support delete, like, or share actions"

elif [ "${1}" == "discord" ]; then
    POST_DISCORD_ID=$(
        python3 -m agoras.cli discord post \
            --bot-token "${DISCORD_BOT_TOKEN}" \
            --server-name "${DISCORD_SERVER_NAME}" \
            --channel-name "${DISCORD_CHANNEL_NAME}" \
            --text "${DISCORD_STATUS_TEXT}" \
            --image-1 "${DISCORD_STATUS_IMAGE_URL_1}" | jq --unbuffered '.' | jq -r '.id'
    )

    sleep 5

    echo "Note: Discord does not support 'like' action (uses reactions instead)"

    sleep 5

    [ -n "${POST_DISCORD_ID}" ] && python3 -m agoras.cli discord delete \
        --bot-token "${DISCORD_BOT_TOKEN}" \
        --server-name "${DISCORD_SERVER_NAME}" \
        --channel-name "${DISCORD_CHANNEL_NAME}" \
        --post-id "${POST_DISCORD_ID}" || true

elif [ "${1}" == "linkedin" ]; then
    POST_LINKEDIN_ID=$(
        python3 -m agoras.cli linkedin post \
            --client-id "${LINKEDIN_CLIENT_ID}" \
            --client-secret "${LINKEDIN_CLIENT_SECRET}" \
            --access-token "${LINKEDIN_ACCESS_TOKEN}" \
            --text "${LINKEDIN_STATUS_TEXT}" \
            --image-1 "${LINKEDIN_STATUS_IMAGE_URL_1}" | jq --unbuffered '.' | jq -r '.id'
    )

    sleep 5

    SHARED_POST_LINKEDIN_ID=$(
        python3 -m agoras.cli linkedin share \
            --client-id "${LINKEDIN_CLIENT_ID}" \
            --client-secret "${LINKEDIN_CLIENT_SECRET}" \
            --access-token "${LINKEDIN_ACCESS_TOKEN}" \
            --post-id "${POST_LINKEDIN_ID}" | jq --unbuffered '.' | jq -r '.id'
    )

    sleep 5

    [ -n "${POST_LINKEDIN_ID}" ] && python3 -m agoras.cli linkedin like \
        --client-id "${LINKEDIN_CLIENT_ID}" \
        --client-secret "${LINKEDIN_CLIENT_SECRET}" \
        --access-token "${LINKEDIN_ACCESS_TOKEN}" \
        --post-id "${POST_LINKEDIN_ID}" || true

    sleep 5

    [ -n "${SHARED_POST_LINKEDIN_ID}" ] && python3 -m agoras.cli linkedin delete \
        --client-id "${LINKEDIN_CLIENT_ID}" \
        --client-secret "${LINKEDIN_CLIENT_SECRET}" \
        --access-token "${LINKEDIN_ACCESS_TOKEN}" \
        --post-id "${SHARED_POST_LINKEDIN_ID}" || true

    sleep 5

    [ -n "${POST_LINKEDIN_ID}" ] && python3 -m agoras.cli linkedin delete \
        --client-id "${LINKEDIN_CLIENT_ID}" \
        --client-secret "${LINKEDIN_CLIENT_SECRET}" \
        --access-token "${LINKEDIN_ACCESS_TOKEN}" \
        --post-id "${POST_LINKEDIN_ID}" || true

else
    echo "Unsupported platform ${1}"
    echo "Usage: $0 {twitter|tiktok|facebook-video|youtube|facebook|instagram|discord|linkedin}"
fi
