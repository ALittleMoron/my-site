#!/usr/bin/env bash
set -euo pipefail

action="${1:?action is required}"

case "$action" in
    init)
        alembic -c src/infra/postgresql/alembic/alembic.ini upgrade head
        LITESTAR_APP=cli:create_cli litestar invalidatecache
        LITESTAR_APP=cli:create_cli litestar initbuckets
        LITESTAR_APP=cli:create_cli litestar createsuperuser \
            --username "${ADMIN_INIT_LOGIN}" \
            --password "${ADMIN_INIT_PASSWORD}"
        ;;
    run)
        uvicorn main:create_app --port 8080 --host 0.0.0.0
        ;;
    *)
        echo "Unknown application action: ${action}" >&2
        exit 2
        ;;
esac
