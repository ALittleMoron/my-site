# My Personal Site

[🇷🇺 Русская версия](./README_RU.md)

| Category | Technologies |
|----------|--------------|
| Coverage | ![coverage-backend](./badges/coverage-backend.svg) ![coverage-frontend](./badges/coverage-frontend.svg) |
| Backend | ![python](./badges/python.svg) ![litestar](./badges/litestar.svg) ![async](./badges/async.svg) ![pydantic](./badges/pydantic.svg) ![dishka](./badges/dishka.svg) ![argon2](./badges/argon2.svg) |
| Database | ![postgresql](./badges/postgresql.svg) ![sqlalchemy](./badges/sqlalchemy.svg) ![alembic](./badges/alembic.svg) |
| Frontend | ![angular](./badges/angular.svg) ![typescript](./badges/typescript.svg) ![bootstrap](./badges/bootstrap.svg) |
| Testing | ![pytest](./badges/pytest.svg) ![jest](./badges/jest.svg) ![locust](./badges/locust.svg) |
| DevOps | ![docker](./badges/docker.svg) ![nginx](./badges/nginx.svg) ![minio](./badges/minio.svg) ![docker-compose](./badges/docker-compose.svg) |
| Quality | ![ruff](./badges/ruff.svg) ![mypy](./badges/mypy.svg) ![bandit](./badges/bandit.svg) ![vulture](./badges/vulture.svg) |
| Logging | ![structlog](./badges/structlog.svg) ![ecs-logging](./badges/ecs-logging.svg) ![sentry](./badges/sentry.svg) |
| Architecture | ![clean-architecture](./badges/clean-architecture.svg) ![type-safe](./badges/type-safe.svg) |
| Tools | ![uv](./badges/uv.svg) ![uvicorn](./badges/uvicorn.svg) |
| CI/CD | ![github-actions](./badges/github-actions.svg) |

> [!NOTE]
> Backend coverage — pytest (Python). Frontend coverage — Jest (TypeScript). Both generated in separate CI jobs.

A personal site with a Litestar REST API backend and an Angular 19 SPA frontend.
Features a competency matrix, notes, contact form, and admin panel.

## 📖 Documentation

- [Project idea](../docs/idea.md)  
- [Project TODOs](../docs/TODO.md)

## 📂 Project Structure

```
my-site/
├── infra/          # nginx reverse proxy, run scripts
├── frontend/       # Angular 19 SPA (served by its own nginx image)
├── backend/        # Litestar API + domain logic
│   ├── src/        # Application source
│   ├── tests/      # Backend tests (pytest)
│   └── performance/ # Locust load-test scenarios and reports
├── .env.example    # Example environment variables
├── .env.test       # Safe test-only environment variables
├── docker-compose.test.yml
└── docker-compose.yml
```

## ✨ Features

- Competency matrix with questions, answers, and Markdown rendering
- Notes with folders, tags, Markdown rendering, and publish visibility
- Angular SPA with dark/light theme and list/grid layouts
- REST API with OpenAPI documentation
- Admin panel: create, edit, publish/unpublish matrix questions and notes
- Contact form
- PASETO-based authentication

## 🚀 Quick Start

1. Clone the repository:
```bash
git clone git@github.com:ALittleMoron/my-site.git
cd my-site
```

2. Create `.env` file:
```bash
cp .env.example .env
```

3. Create certs for `nginx` (optional for local development):

```bash
mkcert -install
mkcert \
  <your-domain> \
  s3.<your-domain> \
  s3-panel.<your-domain> \
  backup.<your-domain>
mv <your-domain>.pem ./infra/nginx/certs/
mv <your-domain>-key.pem ./infra/nginx/certs/
```

4. Update `.env` with your values.

5. Run via `Makefile`:
```bash
make run
```

## ⚙️ Endpoints

- Frontend: `http://localhost`
- API: `http://localhost/api`
- API docs: `http://localhost/api/docs`
- OpenAPI spec: `http://localhost/api/docs/openapi.json`

See [docker-compose.yml](../docker-compose.yml) for all services.

## 🧪 Tests

```bash
make tests-compose              # isolated test DB, backend + frontend, auto cleanup
make tests-fast                 # backend + frontend with an already running test DB
make test-env-up                # start reusable test PostgreSQL
make test-env-down              # stop reusable test PostgreSQL and remove data
make test-backend-unit          # backend unit tests, no DB required
make test-backend-integration   # backend integration tests, needs test DB
make test-frontend              # frontend only (jest)
make install-performance        # install Locust dependency group for local IDE/runs
make performance-smoke          # short Locust smoke profile, writes backend/performance/reports
make query-plans-balanced       # seed test DB and EXPLAIN ANALYZE real search queries
```
