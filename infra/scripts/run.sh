#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
repo_dir="$(cd -- "${script_dir}/../.." && pwd)"
cd "$repo_dir"

if [ ! -f .env ]; then
    echo ".env file could not be found" >&2
    echo "Please create a .env file in the root directory" >&2
    exit 1
fi

if ! docker compose version >/dev/null 2>&1; then
    echo "docker compose plugin could not be found. Install it." >&2
    exit 1
fi

set -a
. .env
set +a

if [ -z "${VPN_BIND_ADDRESS:-}" ]; then
    echo "VPN_BIND_ADDRESS must be set to a host address that Docker can bind for internal panels." >&2
    exit 1
fi

docker compose up --build -d
