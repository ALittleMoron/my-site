# Production Deploy

Production deploy is a manual server-build deploy:

1. The root CI workflow is an orchestration graph: each job delegates its implementation to a
   private reusable workflow under `.github/workflows/_*.yaml`.
2. GitHub Actions runs backend and frontend quality gates in parallel.
3. Backend tests wait only for backend gates, while frontend tests wait only for frontend gates.
4. Backend performance smoke and query-plan smoke run after backend tests.
5. Frontend SSR smoke and Lighthouse CI run as separate jobs after frontend tests.
6. Dockerfile lint, Trivy config scan, per-image Docker build/image scans, and infrastructure
   security checks run in parallel after the smoke gates.
7. Deploy is a separate **Deploy to production** workflow triggered only by
   `workflow_dispatch`.
8. The deploy workflow has no CI `needs` graph and does not run tests, linters, smoke checks,
   Docker/image scans, or infrastructure security checks.
9. The deploy workflow calls the private reusable `.github/workflows/_deploy.yaml` workflow.
10. The deploy job targets the protected `production` environment, so GitHub waits for the
   **Review deployments** / **Approve and deploy** action before running deploy steps.
11. The deploy job renders a runtime `.env` from `infra/deploy/runtime-env.manifest.json`.
12. GitHub Actions syncs source/config to the server.
13. The server runs `make run`, which builds images locally and switches the healthy blue/green
    slot.

Locally built runtime images use the GitHub commit SHA from the required `IMAGE_TAG` runtime
environment entry. `docker-compose.yml` intentionally has no `latest` fallback for the backend,
frontend, nginx, or MinIO wrapper images, so a production start fails early if the deploy renderer
does not provide the tag.

Start deploy from **Actions** -> **Deploy to production** -> **Run workflow** on `main`. The
repository environment must restrict production deployments to `main` and require reviewer
approval. Without those GitHub Environment protection rules, the workflow remains manual, but
production deploys would no longer have the environment approval and branch protections described
here.

## GitHub Environment

Create a GitHub Environment named `production`.

Required protection rules:

- Required reviewers are enabled, so the deploy job waits for **Approve and deploy**.
- Deployment branches are restricted to `main`.

Deploy connection variables:

- `REMOTE_HOST`
- `REMOTE_USER`
- `REMOTE_PATH`

Deploy-only secret:

- `SSH_PRIVATE_KEY`

Runtime variables:

- `OWNER_INIT_LOGIN`
- `APP_CONTACT_REQUESTS_ENABLED`
- `APP_DEBUG`
- `APP_DOMAIN`
- `APP_URL_SCHEMA`
- `APP_USE_CACHE`
- `AUTH_PUBLIC_KEY`
- `AUTH_TOKEN_EXPIRE_SECONDS`
- `AUTH_SESSION_EXPIRE_SECONDS`
- `AUTH_TOKEN_HEADER_NAME`
- `AUTH_TOKEN_PREFIX`
- `CACHE_WARM_ARTICLES_PAGE_SIZE`
- `COMPETENCY_MATRIX_QUESTION_SUGGESTION_ANONYMOUS_DAILY_LIMIT`
- `DB_DRIVER`
- `DB_EXPIRE_ON_COMMIT`
- `DB_HOST`
- `DB_LOG_QUERY_METRICS`
- `DB_MAX_OVERFLOW`
- `DB_NAME`
- `DB_POOL_PRE_PING`
- `DB_POOL_SIZE`
- `DB_PORT`
- `DB_SLOW_QUERY_LOG_STATEMENT_MAX_LENGTH`
- `DB_SLOW_QUERY_LOG_THRESHOLD_MS`
- `DB_USER`
- `I18N_DEFAULT_LANGUAGE`
- `LE_EMAIL`
- `MINIO_HOST`
- `MINIO_PORT`
- `MINIO_REGION`
- `MINIO_CORS_MAX_AGE_SECONDS`
- `MINIO_PUBLIC_URL`
- `MINIO_SECURE`
- `SENTRY_USE`
- `SSL_CERT`
- `SSL_KEY`
- `TASKIQ_AUTH_SESSION_PRUNE_INTERVAL_SECONDS`
- `TASKIQ_CACHE_WARM_INTERVAL_SECONDS`
- `TASKIQ_RESULT_EXPIRE_SECONDS`
- `VALKEY_HOST`
- `VALKEY_PORT`
- `VPN_BIND_ADDRESS`

Runtime secrets:

- `OWNER_INIT_PASSWORD`
- `APP_SECRET_KEY`
- `AUTH_PRIVATE_KEY`
- `DB_PASSWORD`
- `MINIO_ACCESS_KEY`
- `MINIO_SECRET_KEY`
- `SENTRY_DSN`

The deploy renderer still writes these values into the host-side runtime `.env`, but
the Compose helper materializes them as read-only files under `.deploy-state/compose-secrets/`
before Docker Compose starts. The secret directory is host-user-only, while the files keep a read bit
for non-root container UIDs because local Compose file-backed secrets are bind mounts.
`docker-compose.yml` grants those files to containers through Compose secrets. Backend processes
read the matching `/run/secrets/*` files at startup, PostgreSQL uses `POSTGRES_PASSWORD_FILE`, and
MinIO loads root credentials from secret files in its non-root wrapper image. Do not move these
values back into service `environment` entries or `env_file`, because those values are visible in
`docker inspect`.

MinIO runs as UID/GID `10002:10002`. During `make run`, the deploy script runs a transient
maintenance container as root to repair ownership on the `minio_data` volume before starting the
non-root MinIO runtime container. This keeps upgrades from older root-owned MinIO volumes working
without granting root to the long-running MinIO service.

Use `SSL_CERT=/certs/fullchain.pem` and `SSL_KEY=/certs/privkey.pem` for the compose-managed
certificate sync path. Keep deploy-only values such as `REMOTE_HOST`, `REMOTE_USER`,
`REMOTE_PATH`, `SSH_PRIVATE_KEY`, and registry passwords out of runtime `.env`.

The initial database migration creates the owner account from `OWNER_INIT_LOGIN` and
`OWNER_INIT_PASSWORD`. The migration runs once per database and uses an idempotent insert, so there
is no separate owner-init toggle.

Use `MINIO_HOST=minio` and `MINIO_PORT=9000` for the backend-internal S3 endpoint in the Compose
network. Use `MINIO_PUBLIC_URL=https://s3.<APP_DOMAIN>` for browser-facing object access and
computed public file URLs. `MINIO_REGION` must be explicit for SigV4 S3 client operations;
`us-east-1` is suitable for the bundled MinIO service unless deployment policy chooses another
region string. The Compose MinIO service derives `MINIO_API_CORS_ALLOW_ORIGIN` from
`APP_URL_SCHEMA` and `APP_DOMAIN` because the bundled MinIO release does not accept bucket-level
CORS setup through `PutBucketCors`.

## TLS

Certificate issuance is no longer part of the GitHub Actions deploy path. The deployed host already
owns its certificate lifecycle, while the deploy startup script still syncs certbot-owned
certificates into `infra/nginx/certs/` for the unprivileged nginx container.
In production, keep renewal host-owned too: a systemd timer or equivalent scheduler should run
`make certbot-renew` from the deployed project directory and let the target resync certificates and
reload nginx.

If certificates must be issued again on the server, run the maintenance target directly on the
host while port `80/tcp` is free:

```bash
make certbot-issue
```

For certificate renewal on a running stack:

```bash
make certbot-renew
```

To resync existing certbot certificates without renewal:

```bash
make certbot-sync
```

## Server Expectations

The remote host needs Docker with the Compose plugin, `make`, `curl`, and SSH access for the
configured deploy user. The manual deploy job syncs `Makefile`, `docker-compose.yml`, `backend/`,
`frontend/`, `infra/`, and generated `.env`.
