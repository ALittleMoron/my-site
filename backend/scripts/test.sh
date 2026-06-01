#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
backend_dir="$(cd -- "${script_dir}/.." && pwd)"
cd "$backend_dir"

require_uv() {
    if ! command -v uv >/dev/null 2>&1; then
        echo "UV could not be found." >&2
        exit 2
    fi
}

load_test_env() {
    if [ -f "$TEST_ENV_FILE" ]; then
        set -a
        . "$TEST_ENV_FILE"
        set +a
    fi
}

run_with_test_env() {
    # Intentional word splitting preserves the previous Makefile's KEY=value override form.
    env ${TEST_ENV_OVERRIDES:-} PYTHONPATH=src APP_USE_CACHE=false "$@"
}

action="${1:?action is required}"
TEST_ENV_FILE="${2:-${TEST_ENV_FILE:-../.env.test}}"
TEST_ENV_OVERRIDES="${3:-${TEST_ENV_OVERRIDES:-}}"

require_uv
load_test_env

case "$action" in
    test)
        run_with_test_env uv run pytest --durations=10 -vvv -x tests/
        ;;
    test-unit)
        run_with_test_env uv run pytest --durations=10 -vvv -x tests/unit/
        ;;
    test-integration)
        run_with_test_env uv run pytest --durations=10 -vvv -x tests/integration/
        ;;
    tests-coverage)
        run_with_test_env uv run coverage run -m pytest tests/
        run_with_test_env uv run coverage xml
        run_with_test_env uv run coverage report --fail-under=60
        ;;
    *)
        echo "Unknown test action: $action" >&2
        exit 2
        ;;
esac
