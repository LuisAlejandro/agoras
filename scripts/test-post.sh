#!/usr/bin/env bash

# Exit early if there are errors and be verbose
set -exuo pipefail

source ../secrets.env

if [ "${1}" == "twitter" ]; then
    POST_TWITTER_ID=$(
        python3 -m agoras.cli publish \
            --network twitter \
            --action post \
            --twitter-consumer-key "${TWITTER_CONSUMER_KEY}" \
            --twitter-consumer-secret "${TWITTER_CONSUMER_SECRET}" \
            --twitter-oauth-token "${TWITTER_OAUTH_TOKEN}" \
            --twitter-oauth-secret "${TWITTER_OAUTH_SECRET}" \
            --status-text "${TWITTER_STATUS_TEXT}" \
            --status-image-url-1 "${TWITTER_STATUS_IMAGE_URL_1}" | jq --unbuffered '.' | jq -r '.id'
    )

    sleep 5

    [ -n "${POST_TWITTER_ID}" ] && python3 -m agoras.cli publish \
        --network twitter \
        --action delete \
        --twitter-consumer-key "${TWITTER_CONSUMER_KEY}" \
        --twitter-consumer-secret "${TWITTER_CONSUMER_SECRET}" \
        --twitter-oauth-token "${TWITTER_OAUTH_TOKEN}" \
        --twitter-oauth-secret "${TWITTER_OAUTH_SECRET}" \
        --tweet-id "${POST_TWITTER_ID}" || true

elif [ "${1}" == "tiktok" ]; then
    python3 -m agoras.cli publish \
        --network tiktok \
        --action authorize \
        --tiktok-username "${TIKTOK_USERNAME}" \
        --tiktok-client-key "${TIKTOK_CLIENT_KEY}" \
        --tiktok-client-secret "${TIKTOK_CLIENT_SECRET}"

    POST_TIKTOK_ID=$(
        python3 -m agoras.cli publish \
            --network tiktok \
            --action video \
            --tiktok-username "${TIKTOK_USERNAME}" \
            --tiktok-client-key "${TIKTOK_CLIENT_KEY}" \
            --tiktok-client-secret "${TIKTOK_CLIENT_SECRET}" \
            --tiktok-title "${TIKTOK_TITLE}" \
            --tiktok-video-url "${TIKTOK_VIDEO_URL}" | jq --unbuffered '.' | jq -r '.publish_id'
    )

    echo "TikTok video test created with ID: ${POST_TIKTOK_ID}"
    echo "Note: TikTok does not support delete, like, or share actions"

elif [ "${1}" == "facebook-video" ]; then
    python3 -m agoras.cli publish \
        --network facebook \
        --action video \
        --facebook-access-token "${FACEBOOK_ACCESS_TOKEN}" \
        --facebook-app-id "${FACEBOOK_APP_ID}" \
        --facebook-object-id "${FACEBOOK_OBJECT_ID}" \
        --facebook-video-url "${FACEBOOK_VIDEO_URL}" \
        --facebook-video-type "${FACEBOOK_VIDEO_TYPE}" \
        --facebook-video-title "${FACEBOOK_VIDEO_TITLE}" \
        --facebook-video-description "${FACEBOOK_VIDEO_DESCRIPTION}"

elif [ "${1}" == "youtube" ]; then
    POST_YOUTUBE_ID=$(
        python3 -m agoras.cli publish \
            --network youtube \
            --action video \
            --youtube-client-id "${YOUTUBE_CLIENT_ID}" \
            --youtube-client-secret "${YOUTUBE_CLIENT_SECRET}" \
            --youtube-title "${YOUTUBE_TITLE}" \
            --youtube-video-url "${YOUTUBE_VIDEO_URL}" | jq --unbuffered '.' | jq -r '.id'
    )

    sleep 5

    [ -n "${POST_YOUTUBE_ID}" ] && python3 -m agoras.cli publish \
        --network youtube \
        --action like \
        --youtube-client-id "${YOUTUBE_CLIENT_ID}" \
        --youtube-client-secret "${YOUTUBE_CLIENT_SECRET}" \
        --youtube-video-id "${POST_YOUTUBE_ID}" || true

    sleep 5

    [ -n "${POST_YOUTUBE_ID}" ] && python3 -m agoras.cli publish \
        --network youtube \
        --action delete \
        --youtube-client-id "${YOUTUBE_CLIENT_ID}" \
        --youtube-client-secret "${YOUTUBE_CLIENT_SECRET}" \
        --youtube-video-id "${POST_YOUTUBE_ID}" || true

elif [ "${1}" == "facebook" ]; then
    POST_FACEBOOK_ID=$(
        python3 -m agoras.cli publish \
            --network facebook \
            --action post \
            --facebook-access-token "${FACEBOOK_ACCESS_TOKEN}" \
            --facebook-object-id "${FACEBOOK_OBJECT_ID}" \
            --status-text "${FACEBOOK_STATUS_TEXT}" \
            --status-image-url-1 "${FACEBOOK_STATUS_IMAGE_URL_1}" | jq --unbuffered '.' | jq -r '.id'
    )

    sleep 5

    SHARED_POST_FACEBOOK_ID=$(
        python3 -m agoras.cli publish \
            --network facebook \
            --action share \
            --facebook-access-token "${FACEBOOK_ACCESS_TOKEN}" \
            --facebook-profile-id "${FACEBOOK_PROFILE_ID}" \
            --facebook-object-id "${FACEBOOK_OBJECT_ID}" \
            --facebook-post-id "${POST_FACEBOOK_ID}" | jq --unbuffered '.' | jq -r '.id'
    )

    sleep 5

    [ -n "${POST_FACEBOOK_ID}" ] && python3 -m agoras.cli publish \
        --network facebook \
        --action like \
        --facebook-access-token "${FACEBOOK_ACCESS_TOKEN}" \
        --facebook-object-id "${FACEBOOK_OBJECT_ID}" \
        --facebook-post-id "${POST_FACEBOOK_ID}" || true

    sleep 5

    [ -n "${SHARED_POST_FACEBOOK_ID}" ] && python3 -m agoras.cli publish \
        --network facebook \
        --action delete \
        --facebook-access-token "${FACEBOOK_ACCESS_TOKEN}" \
        --facebook-object-id "${FACEBOOK_OBJECT_ID}" \
        --facebook-post-id "${SHARED_POST_FACEBOOK_ID}" || true

    sleep 5

    [ -n "${POST_FACEBOOK_ID}" ] && python3 -m agoras.cli publish \
        --network facebook \
        --action delete \
        --facebook-access-token "${FACEBOOK_ACCESS_TOKEN}" \
        --facebook-object-id "${FACEBOOK_OBJECT_ID}" \
        --facebook-post-id "${POST_FACEBOOK_ID}" || true

elif [ "${1}" == "instagram" ]; then
    POST_INSTAGRAM_ID=$(
        python3 -m agoras.cli publish \
            --network instagram \
            --action post \
            --instagram-access-token "${INSTAGRAM_ACCESS_TOKEN}" \
            --instagram-object-id "${INSTAGRAM_OBJECT_ID}" \
            --status-text "${INSTAGRAM_STATUS_TEXT}" \
            --status-image-url-1 "${INSTAGRAM_STATUS_IMAGE_URL_1}" | jq --unbuffered '.' | jq -r '.id'
    )

    echo "Instagram post test created with ID: ${POST_INSTAGRAM_ID}"
    echo "Note: Instagram does not support delete, like, or share actions"

elif [ "${1}" == "discord" ]; then
    POST_DISCORD_ID=$(
        python3 -m agoras.cli publish \
            --network discord \
            --action post \
            --discord-bot-token "${DISCORD_BOT_TOKEN}" \
            --discord-server-name "${DISCORD_SERVER_NAME}" \
            --discord-channel-name "${DISCORD_CHANNEL_NAME}" \
            --status-text "${DISCORD_STATUS_TEXT}" \
            --status-image-url-1 "${DISCORD_STATUS_IMAGE_URL_1}" | jq --unbuffered '.' | jq -r '.id'
    )

    sleep 5

    [ -n "${POST_DISCORD_ID}" ] && python3 -m agoras.cli publish \
        --network discord \
        --action like \
        --discord-bot-token "${DISCORD_BOT_TOKEN}" \
        --discord-server-name "${DISCORD_SERVER_NAME}" \
        --discord-channel-name "${DISCORD_CHANNEL_NAME}" \
        --discord-post-id "${POST_DISCORD_ID}" || true

    sleep 5

    [ -n "${POST_DISCORD_ID}" ] && python3 -m agoras.cli publish \
        --network discord \
        --action delete \
        --discord-bot-token "${DISCORD_BOT_TOKEN}" \
        --discord-server-name "${DISCORD_SERVER_NAME}" \
        --discord-channel-name "${DISCORD_CHANNEL_NAME}" \
        --discord-post-id "${POST_DISCORD_ID}" || true

elif [ "${1}" == "linkedin" ]; then
    POST_LINKEDIN_ID=$(
        python3 -m agoras.cli publish \
            --network linkedin \
            --action post \
            --linkedin-client-id "${LINKEDIN_CLIENT_ID}" \
            --linkedin-client-secret "${LINKEDIN_CLIENT_SECRET}" \
            --linkedin-access-token "${LINKEDIN_ACCESS_TOKEN}" \
            --status-text "${LINKEDIN_STATUS_TEXT}" \
            --status-image-url-1 "${LINKEDIN_STATUS_IMAGE_URL_1}" | jq --unbuffered '.' | jq -r '.id'
    )

    sleep 5

    SHARED_POST_LINKEDIN_ID=$(
        python3 -m agoras.cli publish \
            --network linkedin \
            --action share \
            --linkedin-client-id "${LINKEDIN_CLIENT_ID}" \
            --linkedin-client-secret "${LINKEDIN_CLIENT_SECRET}" \
            --linkedin-access-token "${LINKEDIN_ACCESS_TOKEN}" \
            --linkedin-post-id "${POST_LINKEDIN_ID}" | jq --unbuffered '.' | jq -r '.id'
    )

    sleep 5

    [ -n "${POST_LINKEDIN_ID}" ] && python3 -m agoras.cli publish \
        --network linkedin \
        --action like \
        --linkedin-client-id "${LINKEDIN_CLIENT_ID}" \
        --linkedin-client-secret "${LINKEDIN_CLIENT_SECRET}" \
        --linkedin-access-token "${LINKEDIN_ACCESS_TOKEN}" \
        --linkedin-post-id "${POST_LINKEDIN_ID}" || true

    sleep 5

    [ -n "${SHARED_POST_LINKEDIN_ID}" ] && python3 -m agoras.cli publish \
        --network linkedin \
        --action delete \
        --linkedin-client-id "${LINKEDIN_CLIENT_ID}" \
        --linkedin-client-secret "${LINKEDIN_CLIENT_SECRET}" \
        --linkedin-access-token "${LINKEDIN_ACCESS_TOKEN}" \
        --linkedin-post-id "${SHARED_POST_LINKEDIN_ID}" || true

    sleep 5

    [ -n "${POST_LINKEDIN_ID}" ] && python3 -m agoras.cli publish \
        --network linkedin \
        --action delete \
        --linkedin-client-id "${LINKEDIN_CLIENT_ID}" \
        --linkedin-client-secret "${LINKEDIN_CLIENT_SECRET}" \
        --linkedin-access-token "${LINKEDIN_ACCESS_TOKEN}" \
        --linkedin-post-id "${POST_LINKEDIN_ID}" || true

else
    echo "Unsupported platform ${1}"
    echo "Usage: $0 {twitter|tiktok|facebook-video|youtube|facebook|instagram|discord|linkedin}"
fi
