#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
repo_dir="$(cd -- "${script_dir}/../.." && pwd)"
cd "$repo_dir"

# shellcheck source=compose_secrets.sh
. "$script_dir/compose_secrets.sh"

if [ -f .env ]; then
    set -a
    . .env
    set +a
    prepare_compose_secret_files
fi

docker compose stop
docker compose down
