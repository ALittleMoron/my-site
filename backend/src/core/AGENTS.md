# Core Layer Instructions

These rules apply to backend core code under `backend/src/core/**/*.py`.

## Strict Import Rules

Never violate these boundaries:

- `backend/src/core/**` may import only the Python standard library and other objects from
  `backend/src/core/**` (`core.*`). All external imports are forbidden.
- `backend/src/core/**` must not import `sqlalchemy`, `litestar`, `dishka`, `aiobotocore`,
  `pyseto`, `structlog`, `sentry_sdk`, `verbose_http_exceptions`, or any other third-party
  framework/infrastructure packages.
- `backend/src/core/**` must not import from `infra/postgresql/`, `entrypoints/`, `infra/ioc/`, `infra/s3`, or any outer layers.
- Do not add new imports from `infra.config` or logging into core; pass configurable values through parameters or injected abstractions.
- Keep reusable parser rules, supported formats, limits, headers, and other code-owned constants in
  `backend/src/infra/config/constants.py`. Core code must receive those values through schemas,
  constructor parameters, or IOC wiring, never by importing infra config or creating feature-local
  constants modules.
- Core exception modules must stay free of `verbose_http_exceptions` imports.

## Shared Core Files

Shared files can be used across all domains.

```text
schemas.py      # Shared domain schemas
enums.py        # Shared enums
types.py        # Shared type aliases
exceptions.py   # Shared domain exceptions
generators.py   # Shared generators
```

## Domain Structure

Common files per domain in `backend/core/<domain>/`. Not all files are required.

```text
schemas.py              # domain models (dataclasses or class with init dunder method)
use_cases.py            # Business logic - concrete use cases only, no ABC/Protocol/base inheritance.
storages.py             # Storage ABC - repository pattern (SQLAlchemy, Mongo, etc.)
file_storages.py        # File storages ABC - for manipluating files (S3-compatible, local files, etc.)
exceptions.py           # Domain exceptions
parsers.py              # Domain parsers
readers.py              # Reader interfaces
enums.py                # Domain enumerations
types.py                # Domain type aliases or NewType
services.py             # Domain services - shared business logic, uses in use cases
event_dispatchers.py    # Domain event dispatchers - kafka or rest event publishers
```

## Domain Rules

- New core code must be domain dataclasses, value objects, use cases, services, interfaces, exceptions, or generators.
- Use cases must be concrete standalone classes. Do not add abstract use-case interfaces,
  `Protocol` contracts, base use-case classes, or inheritance between use cases.
- Use cases must not depend on or call other use cases. When the logic belongs to only one
  use case, keep it in that use case and inject storage abstractions directly. Put shared
  cross-use-case business logic in the relevant domain `services.py` as a concrete service.
- Core exceptions must express domain failures and inherit only from `Exception` or project domain
  exception bases that themselves inherit from `Exception`. Litestar/HTTP representation belongs in
  the Litestar entrypoint layer, where core exceptions should be mapped to
  `verbose_http_exceptions`.
- Put parser input/output schemas, parser rule objects, and value objects in `schemas.py`; put
  parser classes in `parsers.py`; put reader interfaces in `readers.py`; put parser/domain errors
  in `exceptions.py`. Do not create feature-specific modules when an existing standard domain file
  type fits the object.
- Do not log secrets, password hashes, tokens, raw credentials, or other sensitive values.
