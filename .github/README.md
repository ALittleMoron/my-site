# My Knowledge Base

[🇷🇺 Russian version](./README_RU.md)

| Category | Technologies |
|----------|--------------|
| Coverage | ![coverage-backend](./badges/coverage-backend.svg) ![coverage-frontend](./badges/coverage-frontend.svg) |
| Backend | ![python](./badges/python.svg) ![litestar](./badges/litestar.svg) ![async](./badges/async.svg) ![pydantic](./badges/pydantic.svg) ![dishka](./badges/dishka.svg) ![taskiq](./badges/taskiq.svg) ![paseto](./badges/paseto.svg) ![argon2](./badges/argon2.svg) |
| Database | ![postgresql](./badges/postgresql.svg) ![sqlalchemy](./badges/sqlalchemy.svg) ![alembic](./badges/alembic.svg) |
| Cache | ![valkey](./badges/valkey.svg) |
| Frontend | ![angular](./badges/angular.svg) ![typescript](./badges/typescript.svg) ![bootstrap](./badges/bootstrap.svg) |
| Testing | ![pytest](./badges/pytest.svg) ![jest](./badges/jest.svg) ![locust](./badges/locust.svg) ![lhci](./badges/lhci.svg) |
| DevOps | ![docker](./badges/docker.svg) ![nginx](./badges/nginx.svg) ![minio](./badges/minio.svg) ![docker-compose](./badges/docker-compose.svg) |
| Quality | ![ruff](./badges/ruff.svg) ![mypy](./badges/mypy.svg) ![bandit](./badges/bandit.svg) ![pip-audit](./badges/pip-audit.svg) ![trivy](./badges/trivy.svg) ![hadolint](./badges/hadolint.svg) ![dockle](./badges/dockle.svg) ![vulture](./badges/vulture.svg) ![eslint](./badges/eslint.svg) ![prettier](./badges/prettier.svg) |
| Logging | ![structlog](./badges/structlog.svg) ![ecs-logging](./badges/ecs-logging.svg) ![sentry](./badges/sentry.svg) |
| Architecture | ![clean-architecture](./badges/clean-architecture.svg) ![type-safe](./badges/type-safe.svg) |
| Tools | ![uv](./badges/uv.svg) ![granian](./badges/granian.svg) ![node](./badges/node.svg) ![npm](./badges/npm.svg) |
| CI/CD | ![github-actions](./badges/github-actions.svg) ![dependabot](./badges/dependabot.svg) |

> [!NOTE]
> Backend coverage — pytest (Python). Frontend coverage — Jest (TypeScript). Both generated in separate CI jobs.

A knowledge base with an engineering case-study page, a competency matrix, localized articles, and
protected owner/admin/moderator workspaces.

## 📖 Documentation

- [Project idea](../docs/idea.md)  
- [Project TODOs](../docs/TODO.md)

## 📂 Project Structure

```
my-site/
├── infra/          # nginx reverse proxy, run scripts
├── frontend/       # Angular 22 hybrid SSR/CSR (served by its own Node.js image)
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

- Competency matrix with priority-ordered localized sheets, sections, and subsections, search, a grid/table view, detailed Q&A, public SEO question pages, admin structure picker/reordering, and linked resources
- Articles with localized RU/EN content, folders, tags, search, date/tag filters, publish visibility, and SSR public article pages
- Protected owner/admin/moderator panel for creating, editing, publishing, and unpublishing articles and matrix questions, plus owner/admin team governance where admins manage moderators and the single owner has full team access
- Privacy-safe article analytics with public view counters, engaged views, source categories, and anonymous reactions
- Public "how this site is built" case-study page covering architecture, quality, and operations
- Russian/English UI and content localization driven by the backend
- PASETO-protected owner/admin/moderator authentication with inactive-account enforcement

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
  s3.<your-domain>
mkdir -p ./infra/nginx/certs
mv <your-domain>.pem ./infra/nginx/certs/fullchain.pem
mv <your-domain>-key.pem ./infra/nginx/certs/privkey.pem
```

The nginx container runs as UID/GID `101:101`, so mounted certificate and private key files
must be readable by that user. For local `mkcert` files, `chmod 644 ./infra/nginx/certs/<file>`
is enough; for production, prefer owner/group permissions that grant read access only to nginx.
Production Let's Encrypt issuance and renewal are handled through the compose-backed
`make certbot-issue`, `make certbot-renew`, and `make certbot-sync` targets. See
[Production Deploy](../docs/production-deploy.md).

4. Update `.env` with your values.

5. Run via `Makefile`:
```bash
make run
```

`make run` validates the required `.env` values before Compose starts services. It brings
PostgreSQL, Valkey, MinIO, Databasus, backend, frontend, and nginx up through Docker
health checks, runs one-shot backend initialization, and switches public traffic between
blue/green backend/frontend slots with a graceful nginx reload.

## ⚙️ Endpoints

Local edge nginx redirects HTTP to HTTPS, so use the HTTPS URLs in the browser.

- Frontend: `https://localhost`
- API: `https://localhost/api`
- API liveness: `https://localhost/api/healthcheck`
- API readiness: `https://localhost/api/healthcheck/ready`
- API docs: `https://localhost/api/docs`
- OpenAPI spec: `https://localhost/api/docs/openapi.json`

Internal web panels are available only through host-level WireGuard and nginx
ports bound to `VPN_BIND_ADDRESS`:

- MinIO Console: `http://<VPN_BIND_ADDRESS>:18081`
- Databasus: `http://<VPN_BIND_ADDRESS>:18082`

The production public firewall baseline is `80/tcp`, `443/tcp`, and the chosen
WireGuard UDP port. See [WireGuard internal access](../docs/wireguard-internal-access.md).

See [docker-compose.yml](../docker-compose.yml) for all services.

## 🧪 Tests

```bash
make tests-compose              # starts/reuses test DB, backend + frontend, owned cleanup
make tests-fast                 # backend unit + frontend tests; no backend test DB
make tests                      # full backend + frontend tests
make test-env-up                # start reusable test PostgreSQL
make test-env-down              # stop reusable test PostgreSQL and remove data
make test-backend               # backend unit + integration + serial migrations
make test-backend-unit          # backend unit tests, no DB required
make test-backend-integration   # backend integration tests, auto test DB
make tests-coverage             # backend coverage report
make tests-coverage-frontend    # frontend coverage report
make test-frontend              # frontend only (jest)
make -C frontend ssr-smoke      # production SSR build + public article, case-study, and matrix question HTML smoke
make performance-smoke          # auto local backend + seeded short Locust smoke profile
make performance-lighthouse     # production Angular SSR build + strict Lighthouse CI quality/performance gates
make query-plans-balanced       # auto test DB, storage-wide SQL capture + EXPLAIN ANALYZE gate
```

Backend pytest targets run with an explicit pytest-xdist worker count based on physical CPU cores,
not `-n auto`. Set `BACKEND_PYTEST_WORKERS=0` or `1` for serial execution, or set any value greater
than `1` to force that exact worker count. Unit tests run without a test database; integration tests
clone a migrated run-scoped template into isolated per-worker PostgreSQL databases, while Alembic
migration tests stay serial against the base test database.
