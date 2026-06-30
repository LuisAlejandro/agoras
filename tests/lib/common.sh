#!/usr/bin/env bash
# Shared helpers for live E2E integration runners.

_AGORAS_TEST_LIB="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# generic image — see: agoras utils media-limits --platform discord --kind image
TEST_IMAGE_URL="https://wakatime.com/share/@LuisAlejandro/5a56439c-b3af-44e6-8164-c0b9128872b8.png"
# TikTok image max 20MB, url_pull — domain must be verified in TikTok developer app
TEST_TIKTOK_IMAGE_URL="${TEST_TIKTOK_IMAGE_URL:-https://luisalejandro.org/images/banner.png}"
# generic video ~20MB — exceeds discord 8MB cap; see agoras utils media-limits
TEST_VIDEO_URL="https://luisalejandro.org/files/videos/test.mp4"
# discord video max 8MB — see agoras utils media-limits (default ~770KB sample)
TEST_DISCORD_VIDEO_URL="${TEST_DISCORD_VIDEO_URL:-https://www.w3schools.com/html/mov_bbb.mp4}"
INTER_PLATFORM_SLEEP="${INTER_PLATFORM_SLEEP:-10}"

assert_ci_not_set() {
    if [[ -n "${CI:-}${GITHUB_ACTIONS:-}" ]]; then
        echo "❌ Live E2E tests cannot run in CI" >&2
        exit 1
    fi
}

require_cmd() {
    command -v "$1" >/dev/null 2>&1 || {
        echo "❌ Required command not found: $1" >&2
        exit 1
    }
}

skip_case() {
    echo "SKIP: $*"
    return 0
}

load_authorize_env() {
    local env_file="$1"
    if [ ! -f "${env_file}" ]; then
        echo "❌ Missing ${env_file}" >&2
        exit 1
    fi
    # Export all variables from env file to child processes (agoras CLI).
    set -a
    # shellcheck disable=SC1090
    source "${env_file}"
    set +a
}

verify_agoras_storage_dir() {
    if [ -z "${AGORAS_STORAGE_DIR:-}" ]; then
        echo "❌ AGORAS_STORAGE_DIR is not set" >&2
        echo "Use an ephemeral directory, e.g. export AGORAS_STORAGE_DIR=/tmp/agoras-test-e2e" >&2
        exit 1
    fi
    if [ "${AGORAS_STORAGE_DIR}" = "${HOME}/.agoras" ]; then
        echo "❌ AGORAS_STORAGE_DIR must not point at ~/.agoras" >&2
        exit 1
    fi
}

clear_credentials() {
    echo "🧹 Clearing stored credentials..."

    local agoras_dir="${AGORAS_STORAGE_DIR}"

    if [ -d "$agoras_dir" ]; then
        if [ -d "$agoras_dir/tokens" ]; then
            rm -rf "$agoras_dir/tokens"
            echo "✅ Removed tokens directory"
        fi

        if [ -f "$agoras_dir/.key" ]; then
            rm -f "$agoras_dir/.key"
            echo "✅ Removed encryption key file"
        fi

        if [ -z "$(ls -A "$agoras_dir" 2>/dev/null)" ]; then
            rmdir "$agoras_dir"
            echo "✅ Removed agoras config directory (was empty)"
        fi
    else
        echo "ℹ️  No credentials directory found at $agoras_dir"
    fi

    echo "🎉 Stored credentials cleared from $agoras_dir!"
    echo ""
}

init_agoras_bin() {
    local project_root="$1"
    AGORAS_BIN="${project_root}/virtualenv/bin/agoras"
    AGORAS_PYTHON="${project_root}/virtualenv/bin/python3"
    if [ ! -x "${AGORAS_BIN}" ]; then
        echo "❌ agoras CLI not found at ${AGORAS_BIN}" >&2
        exit 1
    fi
    if [ ! -x "${AGORAS_PYTHON}" ]; then
        echo "❌ Python not found at ${AGORAS_PYTHON}" >&2
        exit 1
    fi
    require_cmd jq
}

run_agoras() {
    PYTHONUNBUFFERED=1 "${AGORAS_BIN}" "$@"
}

refresh_unattended_tokens() {
    PYTHONUNBUFFERED=1 "${AGORAS_PYTHON}" "${_AGORAS_TEST_LIB}/refresh-unattended-tokens.py" || true
}

sync_unattended_refresh_tokens() {
    local env_file="${1:-${UNATTENDED_ENV_FILE:-}}"
    if [[ -z "${env_file}" ]]; then
        return 0
    fi
    if [[ ! -f "${env_file}" ]]; then
        return 0
    fi
    PYTHONUNBUFFERED=1 "${AGORAS_PYTHON}" "${_AGORAS_TEST_LIB}/sync-unattended-env.py" --file "${env_file}" || true
}

finish_unattended_run() {
    local exit_code=$?
    local env_file="${1:-${UNATTENDED_ENV_FILE:-}}"

    refresh_unattended_tokens
    sync_unattended_refresh_tokens "${env_file}"
    cleanup_test_posts || true

    exit "${exit_code}"
}

preflight_authorize_tokens() {
    local platform="$1"
    if ! run_agoras utils tokens list --platform "${platform}" >/dev/null 2>&1; then
        echo "❌ No stored tokens for ${platform}." >&2
        echo "   Run: agoras ${platform} authorize (with AGORAS_STORAGE_DIR set)" >&2
        exit 1
    fi
    echo "✅ Stored tokens found for ${platform}"
}

preflight_authorize_tokens_for_platform() {
    local platform="$1"
    case "${platform}" in
    facebook-video) preflight_authorize_tokens "facebook" ;;
    *) preflight_authorize_tokens "${platform}" ;;
    esac
}

try_agoras_or_skip() {
    local skip_reason="$1"
    shift

    set +e
    "$@"
    local exit_code=$?
    set -e

    if [ "${exit_code}" -ne 0 ]; then
        skip_case "${skip_reason}"
        return 0
    fi
    return 0
}

run_agoras_capture_id() {
    local jq_field="$1"
    shift
    local tmp_stderr output exit_code parsed line

    tmp_stderr=$(mktemp)

    set +e
    output=$(run_agoras "$@" 2>"${tmp_stderr}")
    exit_code=$?
    set -e

    cat "${tmp_stderr}" >&2
    rm -f "${tmp_stderr}"

    if [ "${exit_code}" -ne 0 ]; then
        return "${exit_code}"
    fi

    if parsed=$(printf '%s\n' "${output}" | jq -er "${jq_field}" 2>/dev/null); then
        printf '%s' "${parsed}"
        return 0
    fi

    while IFS= read -r line; do
        case "${line}" in
        \{*)
            if parsed=$(printf '%s\n' "${line}" | jq -er "${jq_field}" 2>/dev/null); then
                if [ -n "${parsed}" ] && [ "${parsed}" != "null" ]; then
                    printf '%s' "${parsed}"
                    return 0
                fi
            fi
            ;;
        esac
    done <<<"${output}"

    return 1
}

# Like run_agoras_capture_id but safe under set -e in command substitutions.
run_agoras_capture_id_optional() {
    local captured

    set +e
    captured=$(run_agoras_capture_id "$@")
    set -e
    printf '%s' "${captured}"
}

# Extract post IDs from agoras JSON stdout (one object per line).
extract_post_ids_from_agoras_output() {
    local output="$1"
    local line parsed

    while IFS= read -r line; do
        case "${line}" in
        \{*)
            if parsed=$(printf '%s\n' "${line}" | jq -er '.id // .publish_id // .data.publish_id // empty' 2>/dev/null); then
                if [ -n "${parsed}" ] && [ "${parsed}" != "null" ]; then
                    printf '%s\n' "${parsed}"
                fi
            fi
            ;;
        esac
    done <<<"${output}"
}

# Run a utils publish command; skip on failure; delete any created posts afterward.
run_utils_publish_with_cleanup() {
    local platform="$1"
    local skip_reason="$2"
    shift 2
    local tmp_stderr output exit_code post_id

    tmp_stderr=$(mktemp)

    set +e
    output=$(run_agoras "$@" 2>"${tmp_stderr}")
    exit_code=$?
    set -e

    cat "${tmp_stderr}" >&2
    rm -f "${tmp_stderr}"

    if [ "${exit_code}" -ne 0 ]; then
        skip_case "${skip_reason}"
        return 0
    fi

    while IFS= read -r post_id; do
        if [ -n "${post_id}" ]; then
            register_test_post_cleanup "${platform}" "${post_id}"
            delete_test_post "${platform}" "${post_id}"
        fi
    done < <(extract_post_ids_from_agoras_output "${output}")

    return 0
}

utils_test_network() {
    # Single network for feed/schedule utils — platform posting is covered elsewhere.
    echo "${UTILS_TEST_NETWORK:-x}"
}

_TEST_POST_CLEANUPS=()

register_test_post_cleanup() {
    local platform="$1"
    local post_id="$2"

    if [ -z "${post_id}" ]; then
        return 0
    fi

    _TEST_POST_CLEANUPS+=("${platform}|${post_id}")
}

delete_test_post() {
    local platform="$1"
    local post_id="$2"

    if [ -z "${post_id}" ]; then
        return 0
    fi

    case "${platform}" in
    x) run_agoras x delete --post-id "${post_id}" || true ;;
    facebook) run_agoras facebook delete --post-id "${post_id}" || true ;;
    youtube) run_agoras youtube delete --video-id "${post_id}" || true ;;
    discord) run_agoras discord delete --post-id "${post_id}" || true ;;
    linkedin) run_agoras linkedin delete --post-id "${post_id}" || true ;;
    threads) run_agoras threads delete --post-id "${post_id}" || true ;;
    telegram) run_agoras telegram delete --post-id "${post_id}" || true ;;
    instagram | tiktok | whatsapp)
        warn_manual_test_post_cleanup "${platform}" "${post_id}"
        ;;
    esac
}

warn_manual_test_post_cleanup() {
    local platform="$1"
    local post_id="$2"

    echo "WARN: ${platform} post ${post_id} cannot be deleted via API — remove manually" >&2
}

cleanup_test_posts() {
    local entry platform post_id

    if [ "${#_TEST_POST_CLEANUPS[@]}" -eq 0 ]; then
        return 0
    fi

    for entry in "${_TEST_POST_CLEANUPS[@]}"; do
        platform="${entry%%|*}"
        post_id="${entry#*|}"
        delete_test_post "${platform}" "${post_id}"
    done
}

complete_platform_test_cleanup() {
    _TEST_POST_CLEANUPS=()
}

finish_platform_post_tests() {
    cleanup_test_posts
    complete_platform_test_cleanup
}

run_platform_post_tests() {
    local runner_script="$1"
    local platform="$2"

    set +e
    "${runner_script}" "${platform}"
    local exit_code=$?
    set -e
    finish_platform_post_tests
    if [ "${exit_code}" -ne 0 ]; then
        skip_case "platform post tests exited with errors for ${platform}"
    fi
}

run_utils_unattended() {
    local feed_network
    feed_network="$(utils_test_network)"

    echo "--- Running utils feed-publish (last) for ${feed_network} ---"
    run_utils_publish_with_cleanup "${feed_network}" "feed-publish last failed for ${feed_network}" \
        utils feed-publish \
        --network "${feed_network}" \
        --mode last \
        --feed-url "${FEED_URL}"

    echo "--- Running utils feed-publish (random) for ${feed_network} ---"
    run_utils_publish_with_cleanup "${feed_network}" "feed-publish random failed for ${feed_network}" \
        utils feed-publish \
        --network "${feed_network}" \
        --mode random \
        --feed-url "${FEED_URL}"

    echo "--- Running utils schedule-run for ${feed_network} ---"
    run_utils_publish_with_cleanup "${feed_network}" "schedule-run failed for ${feed_network}" \
        utils schedule-run \
        --network "${feed_network}" \
        --sheets-id "${GOOGLE_SHEETS_ID}" \
        --sheets-name "${GOOGLE_SHEETS_NAME}" \
        --sheets-client-email "${GOOGLE_SHEETS_CLIENT_EMAIL}" \
        --sheets-private-key "${GOOGLE_SHEETS_PRIVATE_KEY}"
}

legacy_network_name() {
    local platform="$1"
    if [[ "${platform}" == "x" ]]; then
        echo "twitter"
    else
        echo "${platform}"
    fi
}

run_legacy_utils_unattended() {
    local feed_network legacy_network
    feed_network="$(utils_test_network)"
    legacy_network="$(legacy_network_name "${feed_network}")"

    echo "--- Running legacy publish feed (last) for ${feed_network} ---"
    run_utils_publish_with_cleanup "${feed_network}" "legacy feed last failed for ${feed_network}" \
        publish \
        --network "${legacy_network}" \
        --action last-from-feed \
        --feed-url "${FEED_URL}"

    echo "--- Running legacy publish feed (random) for ${feed_network} ---"
    run_utils_publish_with_cleanup "${feed_network}" "legacy feed random failed for ${feed_network}" \
        publish \
        --network "${legacy_network}" \
        --action random-from-feed \
        --feed-url "${FEED_URL}"

    echo "--- Running legacy publish schedule for ${feed_network} ---"
    run_utils_publish_with_cleanup "${feed_network}" "legacy schedule failed for ${feed_network}" \
        publish \
        --network "${legacy_network}" \
        --action schedule \
        --google-sheets-id "${GOOGLE_SHEETS_ID}" \
        --google-sheets-name "${GOOGLE_SHEETS_NAME}" \
        --google-sheets-client-email "${GOOGLE_SHEETS_CLIENT_EMAIL}" \
        --google-sheets-private-key "${GOOGLE_SHEETS_PRIVATE_KEY}"
}
