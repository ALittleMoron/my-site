alembic -c src/infra/postgresql/alembic/alembic.ini upgrade head
LITESTAR_APP=cli:create_cli litestar initbuckets
LITESTAR_APP=cli:create_cli litestar collectstatic
LITESTAR_APP=cli:create_cli litestar createsuperuser --username "${ADMIN_INIT_LOGIN}" --password "${ADMIN_INIT_PASSWORD}"
uvicorn main:create_app --port 8080 --host 0.0.0.0
