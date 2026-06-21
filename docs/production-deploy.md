# Production Deploy

The first production deploy is a server-build deploy:

1. GitHub Actions builds and scans Docker images as a quality gate.
2. The deploy job renders a runtime `.env` from `infra/deploy/runtime-env.manifest.json`.
3. GitHub Actions syncs source/config to the server.
4. The server runs `make run`, which builds images locally and switches the healthy blue/green slot.

Deploy is manual from GitHub Actions: run **Deploy to Remote Server** and choose whether to issue
Let's Encrypt certificates before starting the stack.

## GitHub Environment

Create a GitHub Environment named `production`.

Deploy connection variables:

- `REMOTE_HOST`
- `REMOTE_USER`
- `REMOTE_PATH`

Deploy-only secret:

- `SSH_PRIVATE_KEY`

Runtime variables:

- `ADMIN_INIT_LOGIN`
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
- `MINIO_PRESIGN_PUT_EXPIRES_SECONDS`
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

- `ADMIN_INIT_PASSWORD`
- `APP_SECRET_KEY`
- `AUTH_PRIVATE_KEY`
- `DB_PASSWORD`
- `MINIO_ACCESS_KEY`
- `MINIO_SECRET_KEY`
- `SENTRY_DSN`

Use `SSL_CERT=/certs/fullchain.pem` and `SSL_KEY=/certs/privkey.pem` for the compose-managed
certificate sync path. Keep deploy-only values such as `REMOTE_HOST`, `REMOTE_USER`,
`REMOTE_PATH`, `SSH_PRIVATE_KEY`, and registry passwords out of runtime `.env`.

Use `MINIO_HOST=minio` and `MINIO_PORT=9000` for the backend-internal S3 endpoint in the Compose
network. Use `MINIO_PUBLIC_URL=https://s3.<APP_DOMAIN>` for browser-facing object access and
presigned upload URLs. `MINIO_REGION` must be explicit for SigV4 signing; `us-east-1` is suitable
for the bundled MinIO service unless deployment policy chooses another region string. The Compose
MinIO service derives `MINIO_API_CORS_ALLOW_ORIGIN` from `APP_URL_SCHEMA` and `APP_DOMAIN` because
the bundled MinIO release does not accept bucket-level CORS setup through `PutBucketCors`.

## TLS

For the first deploy on a new server, run the workflow with `issue_certificates=true`.
The certificate issue step uses certbot standalone mode, so port `80/tcp` must be free before the
stack starts. The deploy then runs `make run`; the startup script syncs certbot-owned certificates
into `infra/nginx/certs/` for the unprivileged nginx container.

For later certificate maintenance on a running stack:

```bash
make certbot-renew
```

To resync existing certbot certificates without renewal:

```bash
make certbot-sync
```

## Server Expectations

The remote host needs Docker with the Compose plugin, `make`, `curl`, and SSH access for the
configured deploy user. The deploy workflow syncs `Makefile`, `docker-compose.yml`, `backend/`,
`frontend/`, `infra/`, and generated `.env`.
