# My Site Frontend

Angular SPA for the personal site. The frontend is packaged as an independent Docker image and serves its compiled static files through its own nginx runtime.

In the full application stack, infrastructure nginx remains the public edge proxy:

- `/` is proxied to the frontend nginx container.
- `/api/*` is proxied to the backend service.
- TLS, public domains, MinIO, and backup UI routing stay in the infrastructure layer.

## Development server

Use Node.js 22.18+ for local frontend commands (`.nvmrc` matches CI and the Docker builder).

To start a local development server, run:

```bash
npm start
```

Once the server is running, open your browser and navigate to `http://localhost:4200/`. The application will automatically reload whenever you modify any of the source files.

## Building

Frontend Make targets prepare npm dependencies automatically when `node_modules` is missing or stale.

```bash
make build
```

The production build is written to `dist/my-site-frontend/browser`.

## Docker image

Build the frontend image from this directory:

```bash
docker build -t my_site_frontend:latest .
```

The image uses:

- `node:22.18.0-alpine` to install dependencies and run the Angular production build.
- `nginx:1.29.4-alpine` to serve `/usr/share/nginx/html`.
- `nginx.conf` for SPA fallback to `index.html`.
- `docker-entrypoint.d/20-envsubst-sitemap.sh` to substitute `APP_DOMAIN` in `sitemap.xml` at container start.

## Repository split boundary

This directory is intended to become a standalone frontend repository later. Frontend-owned files should stay here, including Angular source code, public assets, the frontend Dockerfile, and frontend nginx config.

The frontend should not own TLS, public domain routing, backend proxy rules, MinIO routing, or backup service routing. Those belong to the infrastructure repository.

## Running unit tests

```bash
make test
```

## Linting

```bash
make lint
```
