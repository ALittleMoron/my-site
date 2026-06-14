# My Site Frontend

Angular hybrid SSR/CSR frontend for the personal site. The frontend is packaged as an independent Docker image and runs the Angular Node.js SSR runtime: public article pages, the public site-build case study, and public competency matrix question pages are server-rendered for SEO, while protected content-authoring and interactive areas stay hydrated Angular.

In the full application stack, infrastructure nginx remains the public edge proxy:

- `/` is proxied to the frontend Node.js SSR container.
- `/api/*` is proxied to the backend service.
- `/sitemap.xml` and `/robots.txt` are proxied to backend-generated discovery endpoints.
- TLS, public domains, MinIO, and backup UI routing stay in the infrastructure layer.

## Development server

Use Node.js 24.16.0 for local frontend commands (`.nvmrc` matches CI and the Docker builder).

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

SSR output is written to `dist/my-site-frontend/server`. To build and run the public SEO HTML smoke check for article, site-build case-study, and matrix question pages, run:

```bash
make ssr-smoke
```

## Docker image

Build the frontend image from this directory:

```bash
docker build -t my_site_frontend:latest .
```

The image uses:

- `node:26.3.0-alpine` to install dependencies and run the Angular production build.
- `node:26.3.0-alpine` as the production runtime for `dist/my-site-frontend/server/server.mjs`.
- Explicit runtime environment: `PORT`, `SSR_API_ORIGIN`, `APP_URL_SCHEMA`, `APP_DOMAIN`, and optionally `SSR_PUBLIC_ORIGIN` / `NG_ALLOWED_HOSTS`.

Canonical SEO routes served by the frontend SSR runtime include `/ru/notes/:slug`, `/en/notes/:slug`, `/ru/how-this-site-is-built`, `/en/how-this-site-is-built`, `/ru/competency-matrix/questions/:slug`, and `/en/competency-matrix/questions/:slug`. The matrix overview routes remain hydrated Angular pages.

## Repository split boundary

This directory is intended to become a standalone frontend repository later. Frontend-owned files should stay here, including Angular source code, public assets, the frontend Dockerfile, and the Angular SSR runtime entrypoint.

The frontend should not own TLS, public domain routing, backend proxy rules, sitemap/robots routing, MinIO routing, or backup service routing. Those belong to the infrastructure repository.

## Running unit tests

```bash
make test
```

## Linting

```bash
make lint
```
