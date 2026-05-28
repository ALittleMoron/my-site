# PostgreSQL Infrastructure Instructions

These rules apply to SQLAlchemy models, PostgreSQL storages, and Alembic migrations under `backend/src/infra/postgresql/`.

## Migrations

- Do not write raw SQL in Alembic migrations when SQLAlchemy can express the operation.
- Schema changes must be represented in SQLAlchemy ORM models, and matching migrations must use Alembic operations plus SQLAlchemy expressions.
- Data reads or writes inside migrations must be built with SQLAlchemy Core query builder constructs (`sa.select`, `sa.update`, `sa.insert`, `sa.delete`, expressions, functions, and bind parameters).
- Raw SQL is allowed only for database features that cannot reasonably be represented through Alembic operations, SQLAlchemy Core, or SQLAlchemy ORM model metadata.
