#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
frontend_dir="$(cd -- "${script_dir}/.." && pwd)"
cd "$frontend_dir"

action="${1:?action is required}"

case "$action" in
    install)
        npm ci --legacy-peer-deps
        ;;
    test)
        npm test -- --watchAll=false
        ;;
    test-watch)
        npm run test:watch
        ;;
    test-coverage)
        npm run test:coverage
        ;;
    tests-coverage)
        npm test -- --watchAll=false --coverage
        ;;
    format)
        npx prettier --write src
        ;;
    format-check)
        npx prettier --check src
        ;;
    lint)
        npm run lint
        ;;
    typecheck)
        npx tsc --noEmit -p tsconfig.app.json
        ;;
    build)
        npm run build
        ;;
    quality)
        bash "$script_dir/npm_task.sh" format
        bash "$script_dir/npm_task.sh" lint
        bash "$script_dir/npm_task.sh" typecheck
        bash "$script_dir/npm_task.sh" build
        bash "$script_dir/npm_task.sh" test
        ;;
    *)
        echo "Unknown frontend action: $action" >&2
        exit 2
        ;;
esac
