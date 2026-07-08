# Security Threat Model

This document records the public-safe threat model for the portfolio, articles, and knowledge
database site. It is intended to support the security audit checklist in `docs/TODO.md` and to make
security assumptions explicit for future changes.

It deliberately avoids secrets, exact private host details, production IP addresses, and exploit
playbooks. Operational runbooks remain in narrower deployment documents where needed.

## Method

This model follows the lightweight OWASP threat-modeling shape: describe what is being built, what
can go wrong, what controls exist, and whether the remaining risk is acceptable. Threat categories
use STRIDE as a checklist, with extra privacy and operational-availability notes because the site
stores authored content, account credentials, analytics aggregates, files, and backups.

References:

- [OWASP Threat Modeling Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Threat_Modeling_Cheat_Sheet.html)
- [OWASP Application Security Verification Standard](https://owasp.org/www-project-application-security-verification-standard/)

## Scope

In scope:

- Public website routes served by Angular hybrid SSR/CSR.
- Public backend routes under `/api/*`, `/sitemap.xml`, and `/robots.txt`.
- Protected admin-panel API routes under `/api/admin/*`.
- Authentication and account-management flows using PASETO bearer tokens.
- PostgreSQL, Valkey, MinIO object storage, Databasus backups, TaskIQ workers, and nginx edge
  routing.
- GitHub Actions CI/deploy path and runtime Compose deployment on the production host.
- Public MinIO object endpoint for intentionally published file objects.
- VPN-only internal web panels for MinIO Console and Databasus.

Out of scope for this version:

- A separate enterprise risk register.
- Full incident-response and disaster-recovery runbooks.
- Browser or operating-system compromise on visitor devices.
- Advanced targeted attacks against GitHub, the hosting provider, or the maintainer's hardware.

## Assets

| Asset | What must be protected |
| --- | --- |
| Public content | Integrity and availability of articles, competency matrix content, resume exports, sitemap, robots.txt, and the public case-study/updates pages. |
| Admin-authored content | Integrity of unpublished drafts, article metadata, matrix structure, file metadata, and resume content. |
| User accounts | Password hashes, account roles, active/inactive state, owner/admin/moderator boundaries, and bearer tokens. |
| Database data | PostgreSQL content, auth records, analytics aggregates, file metadata, migrations, and relational integrity. |
| Object storage | Uploaded images/files, object metadata, public object URLs, and MinIO root credentials. |
| Backups | Backup confidentiality, integrity, availability, and restore confidence. |
| Runtime secrets | Application secret, PASETO private key, database password, MinIO keys, Sentry DSN, owner bootstrap password, TLS private key, and deploy SSH key. |
| CI/deploy path | GitHub Actions workflows, protected production environment, deploy renderer, source sync, and image tags. |
| Service availability | nginx, backend, frontend SSR runtime, PostgreSQL, Valkey, MinIO, Databasus, TaskIQ workers, and scheduled tasks. |
| Privacy-sensitive signals | Article view/reaction aggregates and any request metadata available at the edge or backend. |

## Actors And Goals

| Actor | Goal |
| --- | --- |
| Anonymous visitor | Read public content and fetch public files. |
| Search crawler | Index public pages, sitemap, and article/matrix detail routes. |
| Bot or scraper | Enumerate content, send high-volume requests, spam contact/suggestion endpoints, or increase analytics counters. |
| Credential attacker | Guess, stuff, phish, or replay owner/admin/moderator credentials or bearer tokens. |
| Malicious content editor | Abuse legitimate content permissions to publish unsafe, misleading, or destructive content. |
| Compromised maintainer device or token | Use VPN, GitHub, SSH, or browser auth access as the maintainer. |
| Network attacker | Observe or alter traffic, downgrade transport security, or reach internal panels. |
| Dependency or supply-chain attacker | Introduce vulnerable, malicious, or unexpected code through dependencies, images, or build tooling. |
| Accidental maintainer mistake | Misconfigure public ports, secrets, deploy variables, routes, CSP, backups, or role guards. |

## Trust Boundaries

```text
Public browser / crawler / bot
        |
        v
nginx edge: TLS, redirects, headers, CSP, rate limits, public routing
        |
        +--> Angular frontend SSR runtime
        |
        +--> Litestar backend API
        |       |
        |       +--> PostgreSQL
        |       +--> Valkey
        |       +--> MinIO API
        |       +--> TaskIQ workers/scheduler
        |
        +--> public MinIO object endpoint

Maintainer browser over WireGuard
        |
        v
VPN-bound nginx listeners
        |
        +--> MinIO Console
        +--> Databasus

GitHub protected production deploy
        |
        v
Host filesystem, rendered runtime env, Compose secrets, Docker Compose stack
```

Important boundaries:

- The public internet crosses into the system only through nginx public `80/tcp` and `443/tcp`.
- Internal web panels are reachable only through host-level WireGuard and nginx ports bound to
  `VPN_BIND_ADDRESS`.
- PostgreSQL, Valkey, backend, frontend, MinIO, and Databasus do not publish their own public
  Docker ports.
- Admin API authorization uses explicit short-lived bearer access tokens. A separate HttpOnly,
  Secure, SameSite=Lax session cookie under `/api/auth` is used only to refresh access tokens,
  refresh the session's idle expiration, and revoke the current session on logout.
- Runtime secrets are mounted as Compose secret files instead of service environment values where
  the application stack needs secrets.
- Deploy requires the manual GitHub production workflow and the protected `production` environment.

## Main Data Flows

1. Public page read: browser requests the public domain, nginx enforces HTTPS/security headers/rate
   limits, Angular SSR or the backend reads public content, and the response returns without exposing
   private admin data.
2. Public API read: browser requests `/api/*`, nginx forwards to the backend, public use cases apply
   publish/language filters, and PostgreSQL/MinIO data is projected into public response schemas.
3. Admin auth refresh: browser sends the `/api/auth` scoped session cookie to `/api/auth/refresh`
   with `X-CSRF-Guard: 1`; the backend rejects cross-site Fetch Metadata, verifies the server-side
   session, reloads the current user, extends the session idle expiration, reissues the session
   cookie with the refreshed lifetime, and returns a fresh short-lived PASETO access token.
4. Admin content write: authenticated admin-panel browser sends a PASETO bearer token, backend
   middleware authenticates the access token and active session, route guards enforce content/team
   permissions, and use cases update PostgreSQL or file storage.
5. Markdown rendering: authorized content users save authored Markdown, the frontend renders it only
   through the centralized sanitized renderer before binding HTML.
6. File upload/read: authorized admin upload endpoints store file bytes and metadata through the S3
   adapter; published Markdown can reference computed public object URLs from MinIO.
7. Article analytics: public read UI sends view, engaged-view, or reaction events; the backend stores
   aggregate counts and article-scoped derived reaction identifiers without raw IPs, raw user agents,
   raw referrers, analytics cookies, or third-party analytics IDs.
8. Backup access: Databasus and MinIO Console are routed only through WireGuard-bound nginx
   listeners; backups must remain encrypted and non-public.
9. Deploy: GitHub Actions renders required runtime configuration, syncs source/config to the host,
   the host materializes Compose secret files, builds locally tagged images, runs initialization, and
   switches the healthy blue/green slot.

## Threats, Controls, And Residual Risk

### Spoofing

| Threat | Existing controls | Residual risk / follow-up |
| --- | --- | --- |
| Attacker impersonates an admin with guessed or reused credentials. | Argon2 password hashing, login rate limit at nginx, backend required-role checks, inactive-account enforcement, 15-minute PASETO access tokens, 30-day sliding-idle server-side sessions stored as SHA-256 hashes, session revocation on logout/account changes, and access-token revocation storage on logout. | Browser-held bearer tokens can still be stolen by endpoint compromise, malicious extensions, or successful XSS until they expire. Keep XSS controls strict and consider stronger account protections if the admin surface grows. |
| Attacker forges or tampers with auth tokens. | PASETO v4 public signing/verification with explicit private/public keys and expiration validation. Access tokens carry only username and stable session id; backend authentication re-loads the active server session and current user role from storage. | Private-key exposure would allow token issuance. Keep key material in secret files and out of logs, images, and `docker inspect`. |
| Attacker reaches internal panels as if they were an internal user. | MinIO Console and Databasus are routed only through WireGuard-bound nginx listeners; old public panel virtual hosts are absent; public firewall baseline allows only web and WireGuard ingress. | A compromised maintainer device or VPN key can still access panel login surfaces. Revoke WireGuard peers promptly and keep panel auth enabled. |

### Tampering

| Threat | Existing controls | Residual risk / follow-up |
| --- | --- | --- |
| Unauthorized user changes articles, matrix questions, files, resumes, or team accounts. | Admin APIs live under `/api/admin/*`; guards enforce content/team boundaries; backend use cases enforce privileged behavior instead of relying on hidden UI controls. | New handlers must keep the explicit public/admin/internal classification and matching backend authorization tests. |
| Malicious editor publishes unsafe Markdown or links. | Admin write access is role-limited; public rendering uses the centralized sanitized Markdown/wiki-link renderer; CSP blocks broad inline script execution on normal public routes. | Authorized editors can still publish misleading content or harmful external text. Treat account governance and review discipline as part of the control. |
| Cross-site request tricks browser-sent auth cookies into refreshing or revoking a session. | Cookie-authenticated auth endpoints require `X-CSRF-Guard: 1`, reject `Sec-Fetch-Site: cross-site`, keep SameSite=Lax/Secure/HttpOnly cookies, and do not make admin APIs cookie-authenticated. | Fetch Metadata is a browser signal; keep no CORS expansion for auth endpoints and reassess CSRF controls before adding any cookie-authenticated state-changing API. |
| Deploy or runtime config is modified unexpectedly. | Deploy is manual through GitHub `workflow_dispatch`, should be restricted to `main`, waits for protected production environment approval, and requires explicit runtime values. Locally built runtime images use the required `IMAGE_TAG`. | A compromised GitHub account, approved malicious commit, or host access can tamper with production. Keep branch/environment protections and review deploy changes carefully. |
| Uploaded file metadata or object URLs are abused. | File operations go through admin endpoints and backend-owned metadata; public URLs are computed read-model fields, not write-payload fields. MinIO CORS is restricted to the app origin. | Public object endpoint intentionally serves published objects. Continue to validate upload types/processing when expanding file support. |

### Repudiation

| Threat | Existing controls | Residual risk / follow-up |
| --- | --- | --- |
| Maintainer cannot tell whether auth abuse or protected access attempts happened. | Structured logging reports failed login/authentication states without logging passwords or tokens; Sentry can collect production errors when enabled. | Monitoring and alerting are still tracked as future work. Add production alerts for auth anomalies, production errors, and stale backups. |
| Content changes cannot be attributed or reversed precisely. | Protected content changes require authenticated roles and database persistence. | Rich article/matrix revision history remains future work. Until then, recovery depends on backups, database state, and source history for static code/content. |
| Backup/restore confidence cannot be proven. | Databasus exists, backups are intended to be encrypted and non-public, and the panel is VPN/auth protected. | Restore testing is still pending in `docs/TODO.md`; this remains the largest backup/recovery residual risk. |

### Information Disclosure

| Threat | Existing controls | Residual risk / follow-up |
| --- | --- | --- |
| Secrets leak through containers, images, logs, repo, or `docker inspect`. | Runtime secrets are supplied as Compose secret files; app-owned runtime services avoid putting secret values in service environment entries; project rules forbid committing `.env` values, tokens, keys, and real secrets. | Host filesystem compromise or broad deploy access can still expose secrets. Keep host permissions narrow and rotate exposed credentials. |
| Private admin or unpublished content leaks through public APIs or SSR. | Public and admin routes are separated; public read APIs apply published filters; frontend transfer cache excludes private/side-effect endpoints; admin panel is protected CSR. | Every new route must preserve the public/admin contour split and avoid caching private data in SSR transfer state. |
| Internal panels or infrastructure services become public. | nginx is the only public Compose service; PostgreSQL, Valkey, backend, frontend, MinIO, and Databasus do not publish their own ports; panel listeners bind to `VPN_BIND_ADDRESS`; `infra/scripts/security_check.sh` checks key routing invariants. | Docker and host firewall behavior must be verified after deployment because Docker port publishing can bypass naive host-firewall assumptions. |
| User privacy is harmed by analytics. | Article analytics stores aggregates and article-scoped derived reaction identifiers; raw IPs, raw user agents, raw referrers, analytics cookies, and third-party analytics IDs are out of scope by policy. | Public counters can be gamed by bots. Keep analytics advisory and avoid using them for sensitive decisions. |
| API docs expose more surface detail than needed. | API docs are under `/api/docs`; normal auth middleware excludes docs intentionally; nginx route-scopes the relaxed Swagger CSP to docs. | Public docs aid attackers in route discovery. Keep write endpoints backend-guarded and reassess docs exposure if the threat profile changes. |

### Denial Of Service

| Threat | Existing controls | Residual risk / follow-up |
| --- | --- | --- |
| Bots overload login, auth refresh, contact, suggestion, article list, admin search, or generic API routes. | nginx edge rate limits cover login, auth refresh, contact, matrix suggestions, public article list, admin search endpoints, and generic API traffic. Heavy read paths have narrower limits. | IP-based limits are coarse and may be bypassed by distributed traffic. Future identity-aware quotas would need an explicit design. |
| Backend, frontend SSR, DB, Valkey, or MinIO becomes unavailable. | Docker health checks, restart policies, blue/green backend/frontend slots, nginx health endpoint, and separate readiness checks reduce single-deploy downtime. | Full production observability and alerts are future work; outages may not be detected quickly without external monitoring. |
| Expensive queries or content growth degrade performance. | Existing performance smoke, query-plan harness, Lighthouse checks, and cache-warming support cover major regressions. | Query-count/N+1 detection, dashboards, and slow-query production thresholds are still tracked as future monitoring work. |

### Elevation Of Privilege

| Threat | Existing controls | Residual risk / follow-up |
| --- | --- | --- |
| Moderator gains admin/owner-only team privileges. | Role hierarchy is explicit in backend user schemas; content-management and team-management guards are separate; managed-account use cases restrict account operations. | Any new privileged flow must add backend authorization tests and avoid relying on frontend-only button hiding. |
| Container compromise becomes host compromise. | Backend, frontend, and nginx run as explicit non-root users with read-only root filesystems, dropped Linux capabilities, and `no-new-privileges`. nginx has no write access outside `/tmp`. The MinIO wrapper runs as a non-root UID/GID and writes through its data volume. | Third-party infrastructure services and the host itself still require normal patching and operational hardening. |
| Dependency or base-image compromise grants code execution. | Dependabot, pip-audit, Bandit, Trivy/image/config scans, Dockerfile linting, pinned runtime image tags, and CI quality gates reduce known-vulnerability and drift risk. | Scanners do not prove absence of malicious code. Keep dependency updates reviewed and avoid untrusted package sources. |

## Cross-Cutting Controls

- Security headers are enforced at the nginx edge: HSTS, `X-Content-Type-Options`, `X-Frame-Options`,
  `Referrer-Policy`, and CSP.
- Public HTTP redirects to HTTPS; production TLS allows TLS 1.2 and TLS 1.3.
- Coarse public request limiting belongs to nginx, not backend middleware.
- Backend authentication treats missing/invalid bearer tokens as anonymous, then route guards and use
  cases enforce protected behavior. Authenticated bearer tokens must point to an active server-side
  session.
- Auth/account flows use explicit `Authorization` bearer tokens for admin APIs. The `/api/auth`
  session cookie is scoped to access-token refresh, sliding idle-session renewal, and logout; those
  cookie-authenticated endpoints are protected by CSRF guard checks.
- User-authored Markdown/HTML must render only through the centralized sanitized renderer.
- PostgreSQL, Valkey, MinIO, Databasus, backend, and frontend are reachable by Docker network name,
  not public service ports.
- Compose runtime images for app-owned backend, frontend, nginx, and MinIO require explicit image
  tags and fail early without the tag.
- Deployment and runtime configuration require explicit environment variables; production code should
  not silently invent defaults for security-sensitive settings.

## Highest Residual Risks

1. Restore has not yet been tested. Backups are only as trustworthy as the last successful restore
   exercise.
2. Monitoring and alerting are still incomplete. Security-relevant failures may be visible in logs
   before they are actively alerted.
3. Browser-stored bearer tokens remain sensitive. XSS prevention, extension/device hygiene, token
   lifetime, and revocation remain important.
4. Public Swagger UI/docs intentionally expose route shapes and use route-scoped relaxed CSP for the
   docs UI.
5. A compromised maintainer device, GitHub account, deploy SSH key, or production host remains a
   high-impact event outside what application controls can fully prevent.
6. Bot traffic can still distort public analytics and consume resources despite edge rate limiting.

## Maintenance Triggers

Update this threat model when any of these change:

- Authentication mode, token storage, cookies/sessions, CSRF strategy, or role policy.
- New public or admin HTTP route families.
- New public file/object access paths or external origins in CSP.
- New analytics, tracking, notification, subscription, or user-generated-content feature.
- Backup, restore, deploy, hosting, network, or Docker/nginx routing changes.
- Repository split, independent image publishing, or CI/deploy trust-boundary changes.
- Material security findings from audits, dependency scans, incidents, or restore tests.
