#!/usr/bin/env bash

# Reply-cycle master runner - runs the create -> reply -> verify -> delete
# cycle across all 10 networks.
#
# Networks with full automation: x, facebook, instagram, linkedin, youtube,
# threads, discord.
# Networks with no get-post/get-reply backend (verify skipped, delete auto):
# telegram.
# Networks with manual delete only: tiktok, whatsapp.
#
# Usage: tests/test-reply-cycle-all.sh [platform]
#   (no arg) runs all 10 networks
#   platform  runs a single network

set -exuo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# shellcheck source=lib/common.sh
source "${SCRIPT_DIR}/lib/common.sh"

load_authorize_env "${PROJECT_ROOT}/unattended.env"
UNATTENDED_ENV_FILE="${PROJECT_ROOT}/unattended.env"

assert_ci_not_set
init_agoras_bin "${PROJECT_ROOT}"
verify_agoras_storage_dir
clear_credentials
trap 'finish_unattended_run "${UNATTENDED_ENV_FILE}"' EXIT

ALL_PLATFORMS="x facebook instagram linkedin youtube threads discord telegram tiktok whatsapp"

run_cycle_for_platform() {
    local platform="$1"
    echo "======================================"
    echo "Reply cycle: ${platform}"
    echo "======================================"
    set +e
    "${SCRIPT_DIR}/test-reply-cycle.sh" "${platform}"
    local exit_code=$?
    set -e
    if [ "${exit_code}" -ne 0 ]; then
        skip_case "reply cycle exited with errors for ${platform}"
    fi
    echo ""
}

if [ $# -eq 1 ]; then
    run_cycle_for_platform "$1"
else
    for platform in ${ALL_PLATFORMS}; do
        run_cycle_for_platform "${platform}"
        sleep "${INTER_PLATFORM_SLEEP}"
    done
fi

echo "🎉 Reply cycle tests completed!"
