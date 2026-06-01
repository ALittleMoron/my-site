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

action="${1:?action is required}"

require_uv

case "$action" in
    install)
        uv sync --locked --all-extras
        ;;
    install-performance)
        uv sync --locked --group performance
        ;;
    *)
        echo "Unknown install action: $action" >&2
        exit 2
        ;;
esac
