#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=common.sh
. "$script_dir/common.sh"
cd "$backend_dir"

profile="${1:?profile is required}"
env_file="${2:?env file path is required}"
PERFORMANCE_BACKEND_PID=""

require_var() {
    name="$1"
    if [ -z "${!name:-}" ]; then
        echo "$name is required. Set it in $env_file or pass it in the environment." >&2
        exit 2
    fi
}

require_common_vars() {
    require_var PERFORMANCE_HOST
    require_var PERFORMANCE_REPORT_DIR
    require_var PERFORMANCE_LANGUAGE
    require_var PERFORMANCE_INCLUDE_SPA
    require_var PERFORMANCE_VALIDATE_RESPONSES
    require_var LOCUST_MAX_FAILURE_RATIO
    require_var LOCUST_MAX_AVG_RESPONSE_MS
    require_var LOCUST_MAX_P95_RESPONSE_MS
}

run_locust() {
    users="$1"
    spawn_rate="$2"
    run_time="$3"

    mkdir -p "$PERFORMANCE_REPORT_DIR"
    PYTHONPATH=src uv run --locked --all-groups locust \
        -f performance/locust/locustfile.py \
        --host "$PERFORMANCE_HOST" \
        --headless \
        --only-summary \
        --exit-code-on-error 0 \
        --html "$PERFORMANCE_REPORT_DIR/locust-report.html" \
        --csv "$PERFORMANCE_REPORT_DIR/locust" \
        --csv-full-history \
        --users "$users" \
        --spawn-rate "$spawn_rate" \
        --run-time "$run_time"
}

cleanup_performance() {
    if [ -n "${PERFORMANCE_BACKEND_PID:-}" ]; then
        kill "$PERFORMANCE_BACKEND_PID" >/dev/null 2>&1 || true
        wait "$PERFORMANCE_BACKEND_PID" >/dev/null 2>&1 || true
    fi
    cleanup_owned_test_db
}

start_local_backend_if_needed() {
    local health_url
    local port
    local log_file

    if ! is_local_performance_host "$PERFORMANCE_HOST"; then
        return
    fi

    health_url="$(performance_health_url)"
    if curl --fail --silent "$health_url" >/dev/null; then
        return
    fi

    TEST_ENV_FILE="$env_file"
    ensure_backend_test_db

    mkdir -p "$PERFORMANCE_REPORT_DIR"
    port="$(performance_host_port "$PERFORMANCE_HOST")"
    log_file="${PERFORMANCE_BACKEND_LOG:-${PERFORMANCE_REPORT_DIR}/backend.log}"

    PYTHONPATH=src uv run uvicorn main:create_app --port "$port" --host 127.0.0.1 \
        >"$log_file" 2>&1 &
    PERFORMANCE_BACKEND_PID="$!"

    wait_for_backend_healthcheck "$health_url" "$log_file"
}

prepare_performance_run() {
    ensure_backend_deps
    load_env_file "$env_file"
    require_common_vars
    trap cleanup_performance EXIT
    start_local_backend_if_needed
}

case "$profile" in
    smoke)
        prepare_performance_run
        require_var PERFORMANCE_USERS
        require_var PERFORMANCE_SPAWN_RATE
        require_var PERFORMANCE_RUN_TIME
        run_locust "$PERFORMANCE_USERS" "$PERFORMANCE_SPAWN_RATE" "$PERFORMANCE_RUN_TIME"
        ;;
    baseline)
        prepare_performance_run
        require_var PERFORMANCE_BASELINE_USERS
        require_var PERFORMANCE_BASELINE_SPAWN_RATE
        require_var PERFORMANCE_BASELINE_RUN_TIME
        run_locust \
            "$PERFORMANCE_BASELINE_USERS" \
            "$PERFORMANCE_BASELINE_SPAWN_RATE" \
            "$PERFORMANCE_BASELINE_RUN_TIME"
        ;;
    clean)
        load_env_file "$env_file"
        require_var PERFORMANCE_REPORT_DIR
        rm -rf "$PERFORMANCE_REPORT_DIR"
        ;;
    *)
        echo "Unknown profile: $profile" >&2
        exit 2
        ;;
esac
