#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
backend_dir="$(cd -- "${script_dir}/.." && pwd)"
cd "$backend_dir"

profile="${1:?profile is required}"
env_file="${2:?env file path is required}"

if [ -f "$env_file" ]; then
    set -a
    . "$env_file"
    set +a
fi

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
    PYTHONPATH=src uv run --locked --group performance locust \
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

case "$profile" in
    smoke)
        require_common_vars
        require_var PERFORMANCE_USERS
        require_var PERFORMANCE_SPAWN_RATE
        require_var PERFORMANCE_RUN_TIME
        run_locust "$PERFORMANCE_USERS" "$PERFORMANCE_SPAWN_RATE" "$PERFORMANCE_RUN_TIME"
        ;;
    baseline)
        require_common_vars
        require_var PERFORMANCE_BASELINE_USERS
        require_var PERFORMANCE_BASELINE_SPAWN_RATE
        require_var PERFORMANCE_BASELINE_RUN_TIME
        run_locust \
            "$PERFORMANCE_BASELINE_USERS" \
            "$PERFORMANCE_BASELINE_SPAWN_RATE" \
            "$PERFORMANCE_BASELINE_RUN_TIME"
        ;;
    clean)
        require_var PERFORMANCE_REPORT_DIR
        rm -rf "$PERFORMANCE_REPORT_DIR"
        ;;
    *)
        echo "Unknown profile: $profile" >&2
        exit 2
        ;;
esac
