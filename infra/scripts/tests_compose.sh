#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
repo_dir="$(cd -- "${script_dir}/../.." && pwd)"
cd "$repo_dir"

mode="${1:?mode is required}"
status=0

cleanup() {
    bash infra/scripts/test_env.sh down || true
}

trap cleanup EXIT

bash infra/scripts/test_env.sh up

case "$mode" in
    backend)
        make -C backend test TEST_ENV_FILE=../.env.test || status=$?
        ;;
    all)
        make -C backend test TEST_ENV_FILE=../.env.test || status=$?
        if [ "$status" -eq 0 ]; then
            make test-frontend || status=$?
        fi
        ;;
    *)
        echo "Unknown compose test mode: $mode" >&2
        exit 2
        ;;
esac

exit "$status"
