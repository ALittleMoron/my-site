# PostgreSQL Infrastructure Instructions

These rules apply to SQLAlchemy models, PostgreSQL storages, and Alembic migrations under `backend/src/infra/postgresql/`.

## Performance Query Plans

- Any changes under `backend/src/infra/postgresql/` must also be reflected in `backend/performance/query_plans/` by updating the relevant query capture, seed data, expectations, docs, or tests so the query-plan harness continues to exercise the changed PostgreSQL behavior.

## Data Models

- SQLAlchemy data models may use only database-native PostgreSQL enum types for enum-valued
  columns. Do not set `native_enum=False` or emulate enums with `VARCHAR` plus check constraints;
  matching migrations must preserve native PostgreSQL enum types for those columns.
- When adding or changing SQLAlchemy data models, look for repeated field groups and repeated model
  behavior before writing them inline. Prefer an existing project mixin, a small new project mixin,
  or a suitable third-party mixin from `sqlalchemy_dev_utils` when the same columns, constraints,
  indexes, conversion helpers, or lifecycle behavior appear across multiple models.

## Storages

- Storage mutation methods must not hide preliminary read/get operations. Public use cases should
  perform reads needed for domain decisions, while storage create/update/delete methods should
  execute the named write operation directly. Use `RETURNING` when a mutation needs to return the
  changed row.

## Migrations

- Do not hand-write new Alembic revision files from scratch. Generate new migrations with the
  project's Alembic autogeneration Make target first, then edit the generated revision only for
  intentional data updates, naming cleanup, operation ordering, or other explicit refinements.
- Do not write raw SQL in Alembic migrations when SQLAlchemy can express the operation.
- Schema changes, including indexes and constraints, must be represented in SQLAlchemy ORM models,
  and matching migrations must use Alembic operations plus SQLAlchemy expressions. Do not leave an
  index, constraint, or column in a migration without the corresponding ORM model metadata.
- Data reads or writes inside migrations must be built with SQLAlchemy Core query builder constructs (`sa.select`, `sa.update`, `sa.insert`, `sa.delete`, expressions, functions, and bind parameters).
- Raw SQL is allowed only for database features that cannot reasonably be represented through Alembic operations, SQLAlchemy Core, or SQLAlchemy ORM model metadata.
