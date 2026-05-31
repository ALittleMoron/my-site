set -euo pipefail

profile="${1:?profile is required}"
env_file="${2:?env file path is required}"

if [ ! -f "$env_file" ]; then
    echo "Environment file does not exist: $env_file" >&2
    exit 2
fi

set -a
. "$env_file"
set +a

require_var() {
    name="$1"
    if [ -z "${!name:-}" ]; then
        echo "$name is required. Set it in $env_file or pass it in the environment." >&2
        exit 2
    fi
}

require_var PERFORMANCE_REPORT_DIR

PYTHONPATH=src uv run --locked python -m performance.query_plans \
    --profile "$profile" \
    --report-dir "$PERFORMANCE_REPORT_DIR/query-plans" \
    --fail-on-finding
