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
- VPN-only, mTLS-authenticated private Agent API and local stdio MCP bridge for constrained
  competency-matrix draft authoring.

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
| User accounts | Password hashes, account roles, active/inactive state, owner/admin/moderator boundaries, bearer tokens, server-side session state, and coarse session metadata. |
| Database data | PostgreSQL content, auth records, analytics aggregates, file metadata, migrations, and relational integrity. |
| Object storage | Uploaded images/files, object metadata, public object URLs, and MinIO root credentials. |
| Backups | Backup confidentiality, integrity, availability, and restore confidence. |
| Runtime secrets | Application secret, PASETO private key, database password, MinIO keys, Sentry DSN, owner bootstrap password, TLS private key, and deploy SSH key. |
| CI/deploy path | GitHub Actions workflows, protected production environment, deploy renderer, source sync, and image tags. |
| Service availability | nginx, backend, frontend SSR runtime, PostgreSQL, Valkey, MinIO, Databasus, TaskIQ workers, and scheduled tasks. |
| Privacy-sensitive signals | Article view/reaction aggregates and any request metadata available at the edge or backend. |
| Agent credentials and actions | Offline root CA, issuing CA, per-client private keys and certificates, scopes, claims, draft integrity, and privacy-safe audit records. |

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
| Compromised or prompt-injected agent | Exceed granted scope, follow instructions embedded in queue/web content, publish content, or reach files, shell, private connectors, or internal networks. |

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

Individually certified agent over WireGuard
        |
        v
nginx mTLS :18083 --> private Compose network --> main Litestar backend
                                              --> route-scoped Agent contour
        ^
        |
local five-tool stdio MCP bridge

GitHub protected production deploy
        |
        v
Host filesystem, rendered runtime env, Compose secrets, Docker Compose stack
```

Important boundaries:

- The public internet crosses into the system only through nginx public `80/tcp` and `443/tcp`.
- Internal web panels are reachable only through host-level WireGuard and nginx ports bound to
  `VPN_BIND_ADDRESS`.
- The Agent API listener is also bound only to `VPN_BIND_ADDRESS`, requires a distinct valid client
  certificate, and forwards only seven exact REST operations to the backend on the private Compose
  network. The public agent hostname returns `404` except for its ACME challenge path; the normal
  public listener also returns `404` for `/internal/agent/v1` and strips caller-supplied
  `X-Agent-Client-Certificate` headers before proxying other backend routes.
- The Agent router is mounted in the main Litestar application and reuses its settings, Dishka
  container, request session factory, database role, process, secrets, and availability boundary.
  Route-scoped machine authentication, exact transport, scopes, validation, core rules, and
  operation-specific storages constrain supported requests, but do not sandbox a compromised
  backend, SQL injection, or erroneous arbitrary SQL. Those cases have the main backend role's
  database blast radius and can expose unrelated backend secrets or disrupt public/admin traffic.
- The backend has no published port and is reachable from nginx only on the private application
  network. A compromised service on that network can forge the certificate header, so network
  isolation and the nginx-to-backend trust assumption are part of the boundary.
- PostgreSQL, Valkey, backend, frontend, MinIO, and Databasus do not publish their own public
  Docker ports.
- Admin API authorization uses explicit short-lived bearer access tokens. A separate HttpOnly,
  Secure, SameSite=Lax session cookie under `/api/auth` is used only to refresh access tokens,
  refresh the session's idle expiration within the session's absolute lifetime cap, and revoke the
  current session on logout.
- Auth sessions store server-side secret hashes, current effective expiration timestamps, original
  absolute expiration timestamps, last-used timestamps, auth method, and coarse privacy-safe device
  labels derived from the request user agent. They do not store raw IP addresses, raw user-agent
  strings, or fingerprinting fields.
- Idle-expired and absolute-lifetime-expired server-side auth sessions are physically pruned by a
  scheduled TaskIQ cleanup task. Owners and administrators may invoke the same bounded cleanup from
  `/api/admin/tools/*`; the backend guard, rather than frontend visibility, enforces access.
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
   session, reloads the current user, updates the session's last-used timestamp, extends the
   session idle expiration only up to the original absolute lifetime cap, reissues the session
   cookie with the remaining effective lifetime, and returns a fresh short-lived PASETO access
   token.
4. Auth session cleanup: the TaskIQ scheduler enqueues the internal cleanup task, which deletes
   sessions whose effective `expires_at` or original `absolute_expires_at` is at or before the
   scheduler-provided current time.
5. Admin operational tools: an authenticated owner or administrator can inspect only the defined
   response-cache namespaces, synchronously clear those domains, enqueue the shared full-warm
   service through a manual lifecycle wrapper, poll its bounded-TTL operation record, or invoke the
   same expired-session cleanup as the scheduler. Frontend confirmations reduce mistakes but are
   not an authorization control.
6. Admin session management: authenticated team managers use `/api/admin/accounts/*/sessions`
   endpoints to list active sessions for accounts they may manage, revoke one session, revoke all
   sessions, or revoke only their own other sessions; responses expose current-session markers and
   coarse device labels, not raw request metadata.
7. Admin content write: authenticated admin-panel browser sends a PASETO bearer token, backend
   middleware authenticates the access token and active session, route guards enforce content/team
   permissions, and use cases update PostgreSQL or file storage.
8. Markdown rendering: authorized content users save authored Markdown, the frontend renders it only
   through the centralized sanitized renderer before binding HTML.
9. File upload/read: authorized admin upload endpoints store file bytes and metadata through the S3
   adapter; published Markdown can reference computed public object URLs from MinIO.
10. Article analytics: public read UI sends view, engaged-view, or reaction events; the backend stores
   aggregate counts and article-scoped derived reaction identifiers without raw IPs, raw user agents,
   raw referrers, analytics cookies, or third-party analytics IDs.
11. Backup access: Databasus and MinIO Console are routed only through WireGuard-bound nginx
   listeners; backups must remain encrypted and non-public.
12. Deploy: GitHub Actions renders required runtime configuration, syncs source/config to the host,
   the host materializes Compose secret files, builds locally tagged images, runs initialization, and
   switches the healthy blue/green slot.
13. Agent draft authoring: a separately certified client connects over WireGuard and mTLS, claims a
   queue item for at most two hours, treats queue/web text as untrusted data, reads matrix context,
   references an existing resource ID or a new HTTPS URL without server-side fetching, and
   atomically creates a server-forced draft. Each action receives a privacy-safe audit record.

## Threats, Controls, And Residual Risk

### Spoofing

| Threat | Existing controls | Residual risk / follow-up |
| --- | --- | --- |
| Attacker impersonates an admin with guessed or reused credentials. | Argon2 password hashing, login rate limit at nginx, backend required-role checks, inactive-account enforcement, 15-minute PASETO access tokens, 30-day sliding-idle server-side sessions stored as SHA-256 hashes, admin-visible session management with current-session markers and revocation controls, session revocation on logout/account changes, daily expired-session pruning, and access-token revocation storage on logout. | Browser-held bearer tokens can still be stolen by endpoint compromise, malicious extensions, or successful XSS until they expire. Keep XSS controls strict and consider stronger account protections if the admin surface grows. |
| Attacker forges or tampers with auth tokens. | PASETO v4 public signing/verification with explicit private/public keys and expiration validation. Access tokens carry only username and stable session id; backend authentication re-loads the active server session and current user role from storage. | Private-key exposure would allow token issuance. Keep key material in secret files and out of logs, images, and `docker inspect`. |
| Attacker reaches internal panels as if they were an internal user. | MinIO Console and Databasus are routed only through WireGuard-bound nginx listeners; old public panel virtual hosts are absent; public firewall baseline allows only web and WireGuard ingress. | A compromised maintainer device or VPN key can still access panel login surfaces. Revoke WireGuard peers promptly and keep panel auth enabled. |
| Attacker impersonates an agent or reuses another workflow's authority. | nginx mTLS, P-256 certificate validation, distinct clients/certificates, short certificate lifetime, owner-only registration/revocation, explicit scopes, and per-client audit. | A stolen client key remains usable until revocation or expiry; keep it local with mode `0600` and revoke the client and VPN peer promptly. |
| A compromised backend reaches unrelated application data or secrets. | The supported Agent REST surface has only five business and two rotation operations, with no generic SQL, shell, arbitrary fetch, publish, delete-item, or administration operation. The backend remains non-root, read-only, capability-free, and has no published port or Docker socket. | Agent routes share the main backend process, database role, secrets, and availability boundary. Backend compromise, SQL injection, or erroneous arbitrary SQL is not contained by a separate process or PostgreSQL role. Prevent injection, keep adapters/storages narrow, and patch the shared backend promptly. |
| A compromised application-network service forges an agent certificate header. | Public callers cannot reach the backend directly; nginx returns `404` for the internal path, strips caller-supplied certificate headers on public proxying, and creates the trusted header only after mTLS verification on the VPN-bound listener. | A service that can reach the backend on the private Compose network can forge the header. Keep network membership narrow, isolate the backend from untrusted networks, and treat the nginx-to-backend hop as trusted. |

### Tampering

| Threat | Existing controls | Residual risk / follow-up |
| --- | --- | --- |
| Unauthorized user changes articles, matrix questions, files, resumes, or team accounts. | Admin APIs live under `/api/admin/*`; guards enforce content/team boundaries; backend use cases enforce privileged behavior instead of relying on hidden UI controls. | New handlers must keep the explicit public/admin/internal classification and matching backend authorization tests. |
| Malicious editor publishes unsafe Markdown or links. | Admin write access is role-limited; public rendering uses the centralized sanitized Markdown/wiki-link renderer; CSP blocks broad inline script execution on normal public routes. | Authorized editors can still publish misleading content or harmful external text. Treat account governance and review discipline as part of the control. |
| Cross-site request tricks browser-sent auth cookies into refreshing or revoking a session. | Cookie-authenticated auth endpoints require `X-CSRF-Guard: 1`, reject `Sec-Fetch-Site: cross-site`, keep SameSite=Lax/Secure/HttpOnly cookies, and do not make admin APIs cookie-authenticated. | Fetch Metadata is a browser signal; keep no CORS expansion for auth endpoints and reassess CSRF controls before adding any cookie-authenticated state-changing API. |
| Deploy or runtime config is modified unexpectedly. | Deploy is manual through GitHub `workflow_dispatch`, should be restricted to `main`, waits for protected production environment approval, and requires explicit runtime values. Locally built runtime images use the required `IMAGE_TAG`. | A compromised GitHub account, approved malicious commit, or host access can tamper with production. Keep branch/environment protections and review deploy changes carefully. |
| Uploaded file metadata or object URLs are abused. | File operations go through admin endpoints and backend-owned metadata; public URLs are computed read-model fields, not write-payload fields. MinIO CORS is restricted to the app origin. | Public object endpoint intentionally serves published objects. Continue to validate upload types/processing when expanding file support. |
| Prompt-injected queue or web text makes an agent exceed its task. | The five-tool allowlist has no shell, generic HTTP, SQL, publish, delete, or structure operation; queue text is explicitly untrusted; scopes and draft-only behavior are enforced server-side. | An ordinary agent workspace may still have separately approved shell, file, or connector capabilities. Prefer an isolated profile for queue work. |

### Repudiation

| Threat | Existing controls | Residual risk / follow-up |
| --- | --- | --- |
| Maintainer cannot tell whether auth abuse or protected access attempts happened. | Structured logging reports failed login/authentication states without logging passwords or tokens; Sentry can collect production errors when enabled. | Monitoring and alerting are still tracked as future work. Add production alerts for auth anomalies, production errors, and stale backups. |
| Content changes cannot be attributed or reversed precisely. | Protected content changes require authenticated roles and database persistence. | Rich article/matrix revision history remains future work. Until then, recovery depends on backups, database state, and source history for static code/content. |
| Agent actions cannot be attributed without retaining sensitive prompts. | Every REST action records client/certificate identity, action, related IDs, result, request ID, timestamp, and input digest without prompts, secrets, or full authored content. Events are cursor-paged for the owner and pruned after 365 days without deleting draft idempotency records. | Endpoint or host compromise can still tamper with logs and database records; export/alerting remains future operational work. |
| Backup/restore confidence cannot be proven. | Databasus exists, backups are intended to be encrypted and non-public, and the panel is VPN/auth protected. | Restore testing is still pending in `docs/TODO.md`; this remains the largest backup/recovery residual risk. |

### Information Disclosure

| Threat | Existing controls | Residual risk / follow-up |
| --- | --- | --- |
| Secrets leak through containers, images, logs, repo, or `docker inspect`. | Runtime secrets are supplied as Compose secret files; app-owned runtime services avoid putting secret values in service environment entries; project rules forbid committing `.env` values, tokens, keys, and real secrets. | Host filesystem compromise or broad deploy access can still expose secrets. Keep host permissions narrow and rotate exposed credentials. |
| Private admin or unpublished content leaks through public APIs or SSR. | Public and admin routes are separated; public read APIs apply published filters; frontend transfer cache excludes private/side-effect endpoints; admin panel is protected CSR. | Every new route must preserve the public/admin contour split and avoid caching private data in SSR transfer state. |
| Internal panels or infrastructure services become public. | nginx is the only public Compose service; PostgreSQL, Valkey, backend, frontend, MinIO, and Databasus do not publish their own ports; panel listeners bind to `VPN_BIND_ADDRESS`; `infra/scripts/security_check.sh` checks key routing invariants. | Docker and host firewall behavior must be verified after deployment because Docker port publishing can bypass naive host-firewall assumptions. |
| User privacy is harmed by analytics. | Article analytics stores aggregates and article-scoped derived reaction identifiers; raw IPs, raw user agents, raw referrers, analytics cookies, and third-party analytics IDs are out of scope by policy. | Public counters can be gamed by bots. Keep analytics advisory and avoid using them for sensitive decisions. |
| User privacy is harmed by session/device management. | Auth session rows store only coarse user-agent labels, auth method, timestamps, and revocation state; raw user-agent strings and raw IP addresses stay out of persistent session metadata. | Coarse labels can still hint at a user's device family. Keep labels intentionally broad and avoid adding fingerprinting fields without a privacy review. |
| API docs expose more surface detail than needed. | API docs are under `/api/docs`; normal auth middleware excludes docs intentionally; nginx route-scopes the relaxed Swagger CSP to docs. | Public docs aid attackers in route discovery. Keep write endpoints backend-guarded and reassess docs exposure if the threat profile changes. |
| Agent API becomes a secret oracle, SSRF proxy, or content leak. | The private REST boundary exposes seven fixed operations only; the local MCP bridge exposes five typed business tools; new resources accept HTTPS metadata but are never fetched; audit excludes prompts, secrets, and authored bodies; nginx never routes the Agent contour from the public listener and the backend has no published port. | The agent itself can research public URLs and may disclose workspace data if separately granted file/connector access. Keep those approvals outside the queue workflow. |

### Denial Of Service

| Threat | Existing controls | Residual risk / follow-up |
| --- | --- | --- |
| Bots overload login, auth refresh, contact, suggestion, article list, admin search, or generic API routes. | nginx edge rate limits cover login, auth refresh, contact, matrix suggestions, public article list, admin search endpoints, and generic API traffic. Heavy read paths have narrower limits. | IP-based limits are coarse and may be bypassed by distributed traffic. Future identity-aware quotas would need an explicit design. |
| A valid agent exhausts claims or shared backend capacity. | Per-certificate nginx limits, a two-hour lease, one active claim per queue item and client, bounded resource count, and explicit release limit impact. | A compromised client can still delay work until claims expire or consume capacity shared with public/admin traffic; revoke it and release affected claims from the human admin flow. |
| A compromised owner or administrator repeatedly clears or warms the cache. | Backend team-management guards protect every operation; clear is restricted to response-cache domains; warm reuses the bounded TaskIQ path; destructive UI actions require confirmation. | Confirmation is only a UX guard, and there is no per-operator business quota. Repeated authorized operations can still increase backend and Valkey load; revoke the session and investigate operator activity. |
| Backend, frontend SSR, DB, Valkey, or MinIO becomes unavailable. | Docker health checks, restart policies, blue/green backend/frontend slots, nginx health endpoint, and separate readiness checks reduce single-deploy downtime. | Full production observability and alerts are future work; outages may not be detected quickly without external monitoring. |
| Expensive queries or content growth degrade performance. | Existing performance smoke, query-plan harness, Lighthouse checks, and cache-warming support cover major regressions. | Query-count/N+1 detection, dashboards, and slow-query production thresholds are still tracked as future monitoring work. |

### Elevation Of Privilege

| Threat | Existing controls | Residual risk / follow-up |
| --- | --- | --- |
| Moderator gains admin/owner-only team privileges. | Role hierarchy is explicit in backend user schemas; content-management and team-management guards are separate; managed-account use cases restrict account operations. | Any new privileged flow must add backend authorization tests and avoid relying on frontend-only button hiding. |
| Container compromise becomes host compromise. | Backend, frontend, and nginx run as explicit non-root users with read-only root filesystems, dropped Linux capabilities, and `no-new-privileges`. nginx has no write access outside `/tmp`. The MinIO wrapper runs as a non-root UID/GID and writes through its data volume. | Third-party infrastructure services and the host itself still require normal patching and operational hardening. |
| Dependency or base-image compromise grants code execution. | Dependabot, pip-audit, Bandit, Trivy/image/config scans, Dockerfile linting, pinned runtime image tags, and CI quality gates reduce known-vulnerability and drift risk. | Scanners do not prove absence of malicious code. Keep dependency updates reviewed and avoid untrusted package sources. |
| Agent converts draft authority into publication or general administration. | `save_matrix_question_draft` always forces `Draft`; scopes are checked in backend use cases; the private REST contour and local MCP bridge have no human token, generic CRUD, publish, delete, structure, shell, SQL, or arbitrary fetch operation. | A human with publication rights can still publish a poor draft. Draft review remains a required human control. |

## Cross-Cutting Controls

- Security headers are enforced at the nginx edge: HSTS, `X-Content-Type-Options`, `X-Frame-Options`,
  `Referrer-Policy`, and CSP.
- Public HTTP redirects to HTTPS; production TLS allows TLS 1.2 and TLS 1.3.
- Coarse public request limiting belongs to nginx, not backend middleware.
- Backend authentication treats missing/invalid bearer tokens as anonymous, then route guards and use
  cases enforce protected behavior. Authenticated bearer tokens must point to an active server-side
  session.
- Auth/account flows use explicit `Authorization` bearer tokens for admin APIs. The `/api/auth`
  session cookie is scoped to access-token refresh, sliding idle-session renewal capped by the
  session's original absolute lifetime, and logout; those cookie-authenticated endpoints are
  protected by CSRF guard checks. Expired server-side auth sessions are cleaned up by the scheduled
  TaskIQ worker path and are not a login activity signal.
- Admin session management stays under `/api/admin/*` and is guarded by backend team-management
  authorization. Current-session detection comes from the authenticated bearer token's session id,
  while last-used timestamps are updated only on login and successful refresh.
- Admin operational controls stay under `/api/admin/tools/*`, use the backend team-management guard,
  and may touch only the declared response-cache domains or the shared expired-session cleanup use
  case. Cache metrics are non-transactional snapshots and must not be presented as a freshness or
  completeness guarantee.
- User-authored Markdown/HTML must render only through the centralized sanitized renderer.
- PostgreSQL, Valkey, MinIO, Databasus, backend, and frontend are reachable by Docker network name,
  not public service ports.
- Compose runtime images for app-owned backend, frontend, nginx, and MinIO require explicit image
  tags and fail early without the tag.
- Deployment and runtime configuration require explicit environment variables; production code should
  not silently invent defaults for security-sensitive settings.
- Agent access uses an offline P-256 root, an issuing CA mounted as Compose secrets, locally generated
  per-client P-256 keys/CSRs, 90-day certificates, and recoverable two-phase mTLS rotation within
  14 days of expiry. Production terminates mTLS at the VPN-bound nginx listener and forwards only
  the seven allowlisted operations to the route-scoped Agent contour in the main Litestar backend;
  MCP remains a local stdio bridge. The public listener returns `404` for the internal path and
  strips the trusted header. Core owns Agent Access business contracts and orchestration, infra owns
  HTTP/mTLS, crypto, and file adapters, and the transport entrypoints contain only protocol mapping
  and exception boundaries.
  Availability problems must never trigger a downgrade to public, plaintext, shared, or bearer-only
  agent access.

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
6. The Agent contour shares the main backend process, database identity, secrets, and availability.
   A compromise or injection has no process or PostgreSQL-role containment even though supported
   agent requests remain limited by the closed REST/core surface. A private application-network
   compromise can also bypass nginx and forge the forwarded certificate header.
7. Bot traffic can still distort public analytics and consume resources despite edge rate limiting.
8. A normally configured Codex workspace may retain separately approved shell, filesystem, web, or
   private-connector authority. The MCP boundary limits the site, not every capability of the local
   agent process; an isolated profile/workspace reduces this residual risk.

## Maintenance Triggers

Update this threat model when any of these change:

- Authentication mode, token storage, cookies/sessions, CSRF strategy, or role policy.
- New public or admin HTTP route families.
- New public file/object access paths or external origins in CSP.
- New analytics, tracking, notification, subscription, or user-generated-content feature.
- Backup, restore, deploy, hosting, network, or Docker/nginx routing changes.
- Repository split, independent image publishing, or CI/deploy trust-boundary changes.
- Material security findings from audits, dependency scans, incidents, or restore tests.
- Agent API operations, local MCP tools, scopes, shared process/database/secrets/availability,
  certificate hierarchy/lifetime, claim rules, audit data, agent workspace capabilities, or
  VPN/mTLS/private-network routing and forwarded-certificate trust.
