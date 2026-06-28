#!/usr/bin/env bash
set -euo pipefail

action="${1:?action is required}"

case "$action" in
    init)
        if [ "${OWNER_INIT_ENABLED}" != "true" ] && [ "${OWNER_INIT_ENABLED}" != "false" ]; then
            echo "OWNER_INIT_ENABLED must be true or false" >&2
            exit 2
        fi
        alembic -c src/infra/postgresql/alembic/alembic.ini upgrade head
        LITESTAR_APP=cli:create_cli litestar invalidatecache
        LITESTAR_APP=cli:create_cli litestar initbuckets
        if [ "${OWNER_INIT_ENABLED}" = "true" ]; then
            LITESTAR_APP=cli:create_cli litestar createsuperuser \
                --username "${OWNER_INIT_LOGIN}" \
                --password "${OWNER_INIT_PASSWORD}"
        fi
        ;;
    run)
        granian --interface asgi --factory --host 0.0.0.0 --port 8080 main:create_app
        ;;
    *)
        echo "Unknown application action: ${action}" >&2
        exit 2
        ;;
esac
