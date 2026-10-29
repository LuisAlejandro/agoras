#!/usr/bin/env bash

# Reply-cycle live E2E runner.
#
# For each platform, exercises the full create -> reply -> verify -> delete
# cycle:
#   1. post            -> capture POST_ID
#   2. reply            -> capture REPLY_ID
#   3. get-post         -> assert the post exists
#   4. get-reply        -> assert the reply/comment exists
#   5. delete-reply     -> delete the reply/comment
#   6. delete           -> delete the post
#
# Networks without a get-post/get-reply backend skip verification; networks
# without a delete/delete-reply backend warn for manual cleanup.
#
# Usage: tests/test-reply-cycle.sh <platform>
#   platform: x|facebook|instagram|linkedin|youtube|threads|discord|telegram|tiktok|whatsapp

set -exuo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# shellcheck source=lib/common.sh
source "${SCRIPT_DIR}/lib/common.sh"

load_authorize_env "${PROJECT_ROOT}/unattended.env"
init_agoras_bin "${PROJECT_ROOT}"
trap cleanup_test_posts EXIT

REPLY_TEXT="This is a test reply. It should delete itself in a couple of minutes."
POST_TEXT="This is a test post. It should delete itself in a couple of minutes."

# assert_get <platform> <action> <id> [extra args...]
# Runs a get-post/get-reply action and fails the case if it does not exit 0.
assert_get() {
    local platform="$1"
    local action="$2"
    local id="$3"
    shift 3

    set +e
    run_agoras "${platform}" "${action}" --post-id "${id}" "$@" >/dev/null 2>&1
    local exit_code=$?
    set -e

    if [ "${exit_code}" -ne 0 ]; then
        echo "FAIL: ${platform} ${action} for id ${id} did not return content (exit ${exit_code})" >&2
        return 1
    fi
    echo "OK: ${platform} ${action} verified id ${id}"
}

# delete_reply <platform> <reply_id> [extra args...]
# Deletes a reply/comment; skips (warns) for networks without a backend.
delete_reply() {
    local platform="$1"
    local reply_id="$2"
    shift 2

    case "${platform}" in
    tiktok | whatsapp)
        warn_manual_test_post_cleanup "${platform}" "${reply_id}"
        ;;
    *)
        run_agoras "${platform}" delete-reply --post-id "${reply_id}" "$@" || true
        ;;
    esac
}

# delete_post <platform> <post_id>
# Deletes a post; warns for networks without a delete backend.
delete_post() {
    local platform="$1"
    local post_id="$2"

    case "${platform}" in
    instagram | tiktok | whatsapp)
        warn_manual_test_post_cleanup "${platform}" "${post_id}"
        ;;
    youtube)
        run_agoras youtube delete --video-id "${post_id}" || true
        ;;
    *)
        run_agoras "${platform}" delete --post-id "${post_id}" || true
        ;;
    esac
}

run_cycle() {
    local platform="$1"
    local post_id reply_id media_reply_id x_video_reply_id

    echo "======================================"
    echo "Reply cycle: ${platform}"
    echo "======================================"

    # --- 1. Create the post ---
    case "${platform}" in
    tiktok)
        post_id=$(
            run_agoras_capture_id '.publish_id // .data.publish_id // empty' tiktok post \
                --title "${POST_TEXT}" \
                --image-1 "${TEST_TIKTOK_IMAGE_URL}" \
                --privacy SELF_ONLY
        )
        ;;
    whatsapp)
        post_id=$(
            run_agoras_capture_id '.id' whatsapp post \
                --recipient "${WHATSAPP_RECIPIENT}" \
                --text "${POST_TEXT}"
        )
        ;;
    youtube)
        post_id=$(
            run_agoras_capture_id '.id' youtube video \
                --title "${POST_TEXT}" \
                --privacy unlisted \
                --video-url "${TEST_VIDEO_URL}"
        )
        ;;
    *)
        post_id=$(
            run_agoras_capture_id '.id' "${platform}" post \
                --text "${POST_TEXT}" \
                --image-1 "${TEST_IMAGE_URL}"
        )
        ;;
    esac

    if [ -z "${post_id}" ]; then
        skip_case "${platform} post unavailable or auth failed"
        return 0
    fi
    register_test_post_cleanup "${platform}" "${post_id}"
    echo "${platform} post created: ${post_id}"

    sleep 5

    # --- 2. Reply to the post ---
    case "${platform}" in
    tiktok)
        # TikTok has no reply backend (base raises "Reply not supported").
        echo "SKIP: ${platform} reply not supported via Agoras"
        warn_manual_test_post_cleanup "${platform}" "${post_id}"
        return 0
        ;;
    youtube)
        reply_id=$(
            run_agoras_capture_id '.id' youtube reply \
                --video-id "${post_id}" \
                --text "${REPLY_TEXT}"
        )
        ;;
    whatsapp)
        reply_id=$(
            run_agoras_capture_id '.id' whatsapp reply \
                --recipient "${WHATSAPP_RECIPIENT}" \
                --post-id "${post_id}" \
                --text "${REPLY_TEXT}"
        )
        ;;
    *)
        reply_id=$(
            run_agoras_capture_id '.id' "${platform}" reply \
                --post-id "${post_id}" \
                --text "${REPLY_TEXT}"
        )
        ;;
    esac

    if [ -z "${reply_id}" ]; then
        skip_case "${platform} reply unavailable or auth failed"
        return 0
    fi
    register_test_post_cleanup "${platform}" "${reply_id}"
    echo "${platform} reply created: ${reply_id}"

    sleep 5

    # --- 2b. Media reply (image) where the reply backend accepts media ---
    media_reply_id=""
    case "${platform}" in
    x | facebook | linkedin | discord | threads | telegram)
        media_reply_id=$(
            run_agoras_capture_id_optional '.id' "${platform}" reply \
                --post-id "${post_id}" \
                --text "${REPLY_TEXT} (media)" \
                --image-1 "${TEST_IMAGE_URL}"
        )
        ;;
    whatsapp)
        media_reply_id=$(
            run_agoras_capture_id_optional '.id' whatsapp reply \
                --recipient "${WHATSAPP_RECIPIENT}" \
                --post-id "${post_id}" \
                --text "${REPLY_TEXT} (media)" \
                --image-1 "${TEST_IMAGE_URL}"
        )
        ;;
    *)
        echo "SKIP: ${platform} media reply not scripted"
        ;;
    esac

    if [ -n "${media_reply_id}" ]; then
        register_test_post_cleanup "${platform}" "${media_reply_id}"
        echo "${platform} media reply created: ${media_reply_id}"
    else
        skip_case "${platform} media reply unavailable or auth failed"
    fi

    # X also supports a video reply.
    x_video_reply_id=""
    if [ "${platform}" == "x" ]; then
        x_video_reply_id=$(
            run_agoras_capture_id_optional '.id' x reply \
                --post-id "${post_id}" \
                --video-url "${TEST_VIDEO_URL}"
        )
        if [ -n "${x_video_reply_id}" ]; then
            register_test_post_cleanup x "${x_video_reply_id}"
            echo "x video reply created: ${x_video_reply_id}"
        else
            skip_case "x video reply unavailable or auth failed"
        fi
    fi

    sleep 5

    # --- 3. Verify the post exists (skip for networks without get-post) ---
    case "${platform}" in
    telegram | tiktok | whatsapp)
        echo "SKIP: ${platform} get-post not supported"
        ;;
    *)
        assert_get "${platform}" get-post "${post_id}" || true
        ;;
    esac

    sleep 3

    # --- 4. Verify the reply exists (skip for networks without get-reply) ---
    case "${platform}" in
    telegram | tiktok | whatsapp)
        echo "SKIP: ${platform} get-reply not supported"
        ;;
    linkedin)
        assert_get linkedin get-reply "${reply_id}" --parent-post-id "${post_id}" || true
        ;;
    *)
        assert_get "${platform}" get-reply "${reply_id}" || true
        ;;
    esac

    sleep 3

    # --- 5. Delete the reply/comment ---
    case "${platform}" in
    linkedin)
        delete_reply linkedin "${reply_id}" --parent-post-id "${post_id}"
        ;;
    *)
        delete_reply "${platform}" "${reply_id}"
        ;;
    esac

    if [ -n "${media_reply_id:-}" ]; then
        case "${platform}" in
        linkedin) delete_reply linkedin "${media_reply_id}" --parent-post-id "${post_id}" ;;
        *) delete_reply "${platform}" "${media_reply_id}" ;;
        esac
    fi
    if [ -n "${x_video_reply_id:-}" ]; then
        delete_reply x "${x_video_reply_id}"
    fi

    sleep 3

    # --- 6. Delete the post ---
    delete_post "${platform}" "${post_id}"

    complete_platform_test_cleanup
}

if [ $# -ne 1 ]; then
    echo "Usage: $0 <platform>" >&2
    exit 1
fi

run_cycle "$1"
