# Production Deploy

Production deploy is a CI-gated server-build deploy:

1. GitHub Actions runs backend and frontend static checks in parallel.
2. Backend and frontend tests start only after every static check passes.
3. Backend performance smoke, query-plan smoke, and frontend SSR/Lighthouse smoke run after tests.
4. Docker/image scans and infrastructure security checks run after the smoke gates.
5. The deploy job is part of the same **test, lint and publish** workflow and depends on
   `post-smoke-security`.
6. The deploy job targets the protected `production` environment, so GitHub waits for the
   **Review deployments** / **Approve and deploy** action before running deploy steps.
7. The deploy job renders a runtime `.env` from `infra/deploy/runtime-env.manifest.json`.
8. GitHub Actions syncs source/config to the server.
9. The server runs `make run`, which builds images locally and switches the healthy blue/green slot.

Deploy is manual through the `production` environment review inside the **test, lint and publish**
workflow. The repository environment must restrict production deployments to `main` and require
reviewer approval. Without those GitHub Environment protection rules, GitHub Actions will start the
deploy job automatically after its `needs` succeed.

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

Certificate issuance is no longer part of the CI deploy path. The deployed host already owns its
certificate lifecycle, while the deploy startup script still syncs certbot-owned certificates into
`infra/nginx/certs/` for the unprivileged nginx container.

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
configured deploy user. The CI deploy job syncs `Makefile`, `docker-compose.yml`, `backend/`,
`frontend/`, `infra/`, and generated `.env`.
