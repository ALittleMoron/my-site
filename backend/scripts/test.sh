#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=common.sh
. "$script_dir/common.sh"
cd "$backend_dir"

action="${1:?action is required}"
TEST_ENV_FILE="${2:-${TEST_ENV_FILE:-../.env.test}}"
TEST_ENV_OVERRIDES="${3:-${TEST_ENV_OVERRIDES:-}}"

ensure_backend_deps
load_env_file "$TEST_ENV_FILE"

case "$action" in
    test)
        ensure_backend_test_db
        trap cleanup_owned_test_db EXIT
        run_with_test_env uv run pytest --durations=10 -vvv -x tests/
        ;;
    test-unit)
        run_with_test_env uv run pytest --durations=10 -vvv -x tests/unit/
        ;;
    test-integration)
        ensure_backend_test_db
        trap cleanup_owned_test_db EXIT
        run_with_test_env uv run pytest --durations=10 -vvv -x tests/integration/ tests/migrations/
        ;;
    tests-coverage)
        ensure_backend_test_db
        trap cleanup_owned_test_db EXIT
        run_with_test_env uv run coverage run -m pytest tests/
        run_with_test_env uv run coverage xml
        run_with_test_env uv run coverage report --fail-under=60
        ;;
    *)
        echo "Unknown test action: $action" >&2
        exit 2
        ;;
esac
