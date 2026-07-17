#!/usr/bin/env bash

backend_script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
backend_dir="$(cd -- "${backend_script_dir}/.." && pwd)"
repo_dir="$(cd -- "${backend_dir}/.." && pwd)"

# shellcheck source=../../infra/scripts/test_services.sh
. "${repo_dir}/infra/scripts/test_services.sh"

require_uv() {
    if ! command -v uv >/dev/null 2>&1; then
        echo "UV could not be found." >&2
        exit 2
    fi
}

ensure_backend_deps() {
    local marker=".venv/.self-contained-all-groups"

    require_uv

    if [ -x .venv/bin/python ] \
        && [ -f "$marker" ] \
        && [ ! pyproject.toml -nt "$marker" ] \
        && [ ! uv.lock -nt "$marker" ]; then
        return
    fi

    uv sync --locked --all-groups
    mkdir -p .venv
    touch "$marker"
}

invalidate_backend_deps_marker() {
    rm -f .venv/.self-contained-all-groups
}

performance_report_timestamp() {
    date -u +"%Y%m%dT%H%M%SZ"
}

create_performance_report_run_dir() {
    local report_root="$1"
    local report_type="$2"
    local timestamp
    local report_type_dir
    local candidate
    local suffix

    timestamp="$(performance_report_timestamp)"
    report_type_dir="${report_root%/}/${report_type}"
    candidate="${report_type_dir}/${timestamp}"
    suffix=2

    mkdir -p "$report_type_dir"
    while ! mkdir "$candidate" 2>/dev/null; do
        candidate="${report_type_dir}/${timestamp}-${suffix}"
        suffix=$((suffix + 1))
    done

    printf '%s\n' "$candidate"
}

run_with_test_env() {
    # Intentional word splitting preserves the previous Makefile's KEY=value override form.
    env ${TEST_ENV_OVERRIDES:-} PYTHONPATH=src APP_USE_CACHE=false "$@"
}

ensure_backend_test_db() {
    local compose_file="${1:-docker-compose.test.yml}"
    local forced_port="${2:-}"

    ensure_test_db "$TEST_ENV_FILE" "$compose_file" "$forced_port"
}

is_local_performance_host() {
    local url="$1"
    local without_scheme="${url#*://}"
    local host_port="${without_scheme%%/*}"
    local host="${host_port%%:*}"

    case "$host" in
        localhost|127.0.0.1|0.0.0.0|"[::1]")
            return 0
            ;;
        *)
            return 1
            ;;
    esac
}

performance_host_port() {
    local url="$1"
    local without_scheme="${url#*://}"
    local host_port="${without_scheme%%/*}"
    local scheme="${url%%://*}"

    if [[ "$host_port" == *:* ]]; then
        printf '%s\n' "${host_port##*:}"
        return
    fi

    if [ "$scheme" = "https" ]; then
        printf '443\n'
    else
        printf '80\n'
    fi
}

performance_health_url() {
    local host="${PERFORMANCE_HOST%/}"

    printf '%s/api/healthcheck\n' "$host"
}

wait_for_backend_healthcheck() {
    local health_url="$1"
    local log_file="$2"

    for _attempt in {1..60}; do
        if curl --fail --silent "$health_url" >/dev/null; then
            return 0
        fi
        sleep 1
    done

    if [ -f "$log_file" ]; then
        cat "$log_file" >&2
    fi
    return 1
}
