from __future__ import annotations

import os
import sys

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine, URL
from sqlalchemy.pool import NullPool

from infra.config.settings import settings
from pytest_parallel import build_template_database_name, quote_postgresql_identifier

_TEMPLATE_DATABASE_RUN_ID_ENV = "BACKEND_PYTEST_DB_TEMPLATE_ID"


def main(argv: list[str]) -> int:
    if len(argv) != 2 or argv[1] != "drop-template":
        print("Usage: pytest_databases.py drop-template", file=sys.stderr)
        return 2

    run_id = os.environ.get(_TEMPLATE_DATABASE_RUN_ID_ENV)
    if run_id is None:
        return 0

    template_database_name = build_template_database_name(
        base_database_name=settings.database.name,
        run_id=run_id,
    )
    engine = create_engine(
        _maintenance_database_url(),
        isolation_level="AUTOCOMMIT",
        poolclass=NullPool,
    )
    try:
        _drop_database(engine=engine, database_name=template_database_name)
    finally:
        engine.dispose()
    return 0


def _maintenance_database_url() -> URL:
    return URL.create(
        drivername=settings.database.driver,
        username=settings.database.user,
        password=settings.database.password.get_secret_value(),
        host=settings.database.host,
        port=int(settings.database.port),
        database="postgres",
    )


def _drop_database(engine: Engine, database_name: str) -> None:
    with engine.connect() as connection:
        connection.execute(
            text(
                "SELECT pg_terminate_backend(pid) "
                "FROM pg_stat_activity "
                "WHERE datname = :database_name AND pid <> pg_backend_pid()",
            ),
            {"database_name": database_name},
        )
        drop_database_statement = text(
            f"DROP DATABASE IF EXISTS {quote_postgresql_identifier(database_name)}"
        )
        connection.execute(drop_database_statement)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
