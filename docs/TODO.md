# TODOs

## Development Stages

### Minimum Viable Product (MVP)

- [x] Competency matrix grid/table view
- [x] Public site-build case-study home
- [x] Contact form
- [x] Articles (previous MVP core-only implementation)
- [x] Admin panel via SQLAdmin

- [x] Add Databasus for database backups
- [x] Configure Let's Encrypt
- [x] Remove password_hash from the User domain model
- [x] Remove the mentorship section.
- [x] Fix static files on MinIO and the backup service.
- [x] (SEO) Add a canonical link
- [x] Validate CSS (focus on overriding Bootstrap variables)
- [x] Move Bootstrap (and other files as needed) to the static folder
- [x] Rebuild admin panel on Litestar
  - [x] Remove SQLAdmin
    - [x] Remove admin startup (docker, create_admin + Makefile)
    - [x] Move file upload handling to Litestar admin handlers
    - [x] Move apply_template_callables to Litestar
    - [x] Remove unused Litestar settings (admin, auth)
    - [x] Remove admin usage from code
    - [x] Remove sqladmin dependencies from uv
  - [x] Edit competency matrix directly on the site (partial)
    - [x] (BACK) Published filter for matrix questions (admin only)
    - [x] (FRONT) Toggle for question list view: published only vs all
    - [x] (BACK) Extended detail response for matrix questions (includes question status)
    - [x] (BACK) CRUD for matrix questions (including nested entities) + guard
      - [x] Create
      - [x] Update
    - [x] Delete
    - [x] Publish
    - [x] Unpublish
    - [x] Normalize sheet/section/subsection structure into database tables and use an inline admin picker for question authoring
    - [x] (BACK) Guard admin file upload endpoints
    - [x] (FRONT) Delete button on question detail
    - [x] (FRONT) Publish/Unpublish button (depending on status)
    - [x] Import competency matrix questions into the shared queued-question model
    - [x] Quick-create competency matrix questions into the shared queued-question model
  - [x] Basic auth and edit permissions (PASETO without sessions. Sessions later)
    - [x] (FRONT) Login page with login button on the main page (hidden for now)
    - [x] (BACK) Login logic
    - [x] (FRONT) Logout button on the main page (hidden for now)
    - [x] (BACK) Logout logic (no-op for now)
    - [x] (BACK) Auth guard (only admins can log in for now)
    - [x] (BACK) Anonymous user
- [x] Smoke test
  - [x] Competency matrix search works as before in grid/table view
  - [x] Matrix question modal opens, code blocks render correctly
  - [x] Run docker-compose and verify related services

### MVP Improvements

- [x] (SEO) Add schemaMarkup link
- [x] Check site performance
  - [x] Add Locust smoke/baseline scaffolding and CI report artifacts
  - [x] Validate selected Locust API responses against backend response schemas
  - [x] Add reusable PostgreSQL query-plan harness for real compiled search queries
  - [x] Tune Locust thresholds from real baseline reports
  - [x] Expand Locust scenarios with seeded article/detail/matrix data
  - [x] Add Lighthouse CI with strict quality/performance gates for Angular hybrid SSR/CSR routes
  - [x] Lighthouse audit — fix non-performance errors and enforce strict gates
- [x] Add public "how this site is built" engineering case-study page.
- [x] Add privacy-safe article analytics (public views, engaged views, anonymous reactions).
- [x] Move tests to backend and create a src subfolder for backend
- [ ] Deploy to a remote server
  - [x] Choose hosting
  - [x] Wire up missing secrets and vars
  - [x] Run deployment strictly from the GitHub workflow
  - [x] Remove the unpublished-contract compatibility rule from `AGENTS.md`
  - [x] After deployment, log in to internal services over WireGuard and verify auth
    - [x] MinIO Console via `http://<VPN_BIND_ADDRESS>:18081`
    - [x] Databasus via `http://<VPN_BIND_ADDRESS>:18082`
  - [x] Load the real competency matrix content from the current Google Docs source into the database before first deployment.
  - [ ] Closed beta test with real users (friends, colleagues). Collect feedback and fix critical bugs.

### Security and Infrastructure

- [x] Dependency scanning (pip-audit, Bandit, Trivy)
- [x] VPN for accessing internal systems
- [x] Add Dependabot to the repository
- [ ] Prepare repository split
  - [x] Move Angular serving into a frontend-owned Docker image
  - [x] Keep infrastructure nginx as the edge reverse proxy
  - [ ] Move root AGENTS.md rules to backend and frontend
  - [ ] Move backend, frontend, and infrastructure into separate repositories
  - [ ] Configure independent image publishing for backend and frontend
  - [ ] Update deployment workflow to consume published images from the infrastructure repository
- [ ] Bot protection for the site
  - [x] Basic nginx edge rate limits for login, contact, public articles, and admin search endpoints
- [ ] Pin Docker image tags currently using latest in compose/build workflows.
- [x] Make frontend/matrix localStorage usage SSR-safe where services/components still access it directly.
- [x] Add architecture-boundary checks so core code cannot import infrastructure/framework modules directly.
- [x] Move DB migration out of app_lifespan into a separate task (possible in docker-compose)
- [x] Replace uvicorn with Granian
- [ ] OWASP Top 10 compliance check
- [ ] Check for AI-based vulnerability scanning tools. Try one.
- [ ] Security audit
  - [x] Find a web application security checklist and go through it.
  - [x] Regular users cannot access internal web panels without VPN.
  - [ ] Build a threat model (who is the attacker, what do they want, etc.). Write to docs.
  - [x] HTTP security headers in responses
    - [x] Strict-Transport-Security
    - [x] X-Content-Type-Options: nosniff
    - [x] X-Frame-Options: DENY
    - [x] Referrer-Policy: no-referrer
    - [x] Content-Security-Policy
  - [ ] CSRF (deferred until cookie-based auth; current admin auth uses Authorization bearer tokens)
    - [ ] All POST/PUT/PATCH/DELETE is protected from CSRF
    - [ ] CSRF token in cookie + header
    - [ ] CSRF verified on server
  - [ ] HTTPS and TLS
    - [ ] Everything redirects to HTTPS
    - [ ] Public HTTP redirects to HTTPS; internal VPN panels may use HTTP over WireGuard.
    - [ ] TLS ≥ 1.2
    - [ ] Certbot auto-renews
    - [ ] No internal services are exposed to the public
  - [ ] XSS
    - [ ] All user-supplied data is escaped
    - [ ] No `| safe` without 100% certainty
    - [ ] Cannot save `<script>` to DB and render it. Check DB for such entries.
    - [x] CSP in place
  - [ ] Passwords never logged
  - [ ] Hashing: unique salt used
  - [ ] Every protected handler checks the user (guards where needed)
  - [ ] No role-based "hide button" logic without backend enforcement
  - [ ] All validation exists on the backend. Frontend can duplicate it, but never be the only layer.
  - [ ] Docker and infrastructure
    - [ ] App runs with `read_only: true`
    - [ ] Writable only for `/tmp` and explicitly needed `volumes:`
    - [ ] No writes to `/etc`, `/usr`, `/bin`
    - [ ] No bind mounts like: `- ./:/app`
    - [ ] Containers do not run as root
    - [ ] UID/GID not 0
    - [ ] No sudo inside containers
    - [ ] User-defined networks used
    - [ ] Only nginx exposed to the public
    - [ ] No hardcoded IPs
    - [ ] Services accessible only by network name
    - [ ] No localhost references between services
    - [ ] No sensitive data in `docker inspect`
    - [ ] Logs aren’t written to files inside containers
    - [ ] Log rotation in place
    - [x] All services have health checks
    - [x] Nginx does not forward traffic to an unhealthy backend
    - [ ] Adequate restart policy
    - [ ] Image versions pinned
    - [ ] No `latest` tags
    - [ ] Images updated regularly
    - [ ] Minimal packages
    - [x] Nginx not root
    - [ ] Nginx has no write access
    - [ ] No `proxy_pass` to localhost
    - [ ] No `network_mode: host`
    - [ ] No `privileged: true`
    - [ ] No `/var/run/docker.sock` bind mount
    - [ ] No `cap_add` unless strictly necessary
    - [ ] No `devices:` unless strictly necessary
    - [ ] `cap_drop: [ALL]` where possible
    - [ ] No secrets in images
    - [ ] Infrastructure services are not exposed externally
      - [ ] PostgreSQL
      - [ ] Valkey
    - [ ] Postgres, Valkey, MinIO have no `ports`
    - [ ] MinIO protected by auth
    - [ ] Databasus protected by auth
    - [ ] `.env` not in git
    - [ ] No secrets in logs
    - [ ] All keys are long and random
    - [ ] No stacktrace shown to users
    - [ ] Firewall enabled on host (ufw/iptables)
    - [ ] Only `80/tcp`, `443/tcp`, and the chosen WireGuard UDP port are open publicly.
    - [ ] SSH by key only. Password login disabled.
  - [x] Rate limiting and bot protection
    - [x] Rate limit on login, registration, and password reset (registration/password reset are not implemented)
    - [x] IP / fingerprint-based limiting (IP-based at nginx edge)
    - [x] No unlimited requests to heavy endpoints
  - [ ] Backup & recovery
    - [ ] Backups encrypted
    - [ ] Backups are not publicly accessible
    - [ ] Restore tested
    - [ ] No access to back up a panel without auth
  - [ ] Supply chain
    - [ ] Dependency versions pinned
    - [x] Dependencies updated regularly
    - [ ] No pip install from untrusted sources

### Tracing and Monitoring

- [x] Add optional app-side slow SQL query timing logs without raw parameter values
- [ ] Enable slow SQL query timing logs in staging/production with explicit thresholds
- [ ] Error alerts to Telegram bot
- [ ] Wire frontend GlobalErrorHandler to Sentry in production.
- [ ] Add Web Vitals collection/reporting for public SSR routes after deployment.
- [ ] Add maintainer status dashboard for uptime, backups, restore tests, service health, and production errors.
- [ ] Set up Grafana + Prometheus + Loki
- [ ] Set up PostgreSQL performance visibility
  - [ ] Enable `pg_stat_statements` for aggregate query timing, calls, rows, and cache-hit signals
  - [ ] Enable safe `auto_explain` logging for slow query plans
  - [ ] Alert on long-running queries, lock waits, deadlocks, and connection pool saturation
  - [ ] Add dashboard panels for top queries by total time, mean time, p95-ish latency, and calls
- [ ] Detect likely N+1 and query explosions
  - [ ] Count SQL statements per HTTP request
  - [ ] Warn when one request exceeds the query-count threshold
  - [ ] Add tests for query-count budgets on expensive API endpoints
- [ ] Add Prometheus exporters
  - [ ] PostgreSQL exporter
  - [ ] nginx exporter
  - [ ] node/container exporter
  - [ ] Valkey-compatible Redis exporter
  - [ ] MinIO exporter or built-in metrics scrape
- [ ] Add Grafana dashboards
  - [ ] API latency p50/p95/p99, request rate, and 4xx/5xx rate
  - [ ] DB query latency, locks, connections, and disk usage
  - [ ] nginx upstream status and response latency
  - [ ] container CPU/RAM/restarts
  - [ ] backup freshness and restore-test status
- [ ] Add operational alerts
  - [ ] p95 latency regression
  - [ ] 5xx spikes
  - [ ] event loop lag
  - [ ] TLS certificate expiry
  - [ ] backup failure or stale backup
  - [ ] disk pressure
- [ ] Set up a container health monitoring service
  - [ ] Send notifications on a container crash
  - [ ] Send notifications on high resource usage (CPU, RAM)
- [ ] Security audit
  - [ ] Regular users cannot access Grafana without VPN.

### Frontend

- [x] Make frontend adaptive and flexible to correctly opening on smartphones and thin screens.
- [ ] Optimize page load times (CSS/JS minification, image optimization). Consider CDN for static files.
- [x] Cookie consent
- [x] Fix question search on the frontend: empty sections should also be removed
- [x] Make text selection colour match the site theme
- [x] Add more feedback during API requests (notifications, errors, etc.)
- [x] Improve the custom date picker with in-calendar month and year selection.
  - [x] Make the current month and year in the calendar header clickable.
  - [x] Open month/year selection in the same calendar popover.
  - [x] Use a predefined localized month list for month selection.
  - [x] Support year selection with an in-calendar stepper.
- [x] Resolve frontend npm peer dependency conflicts and remove `--legacy-peer-deps` from install flows
  - [x] Align TypeScript with Angular CLI/build tooling peer dependency ranges so `npm ls typescript` exits cleanly
  - [x] Remove `--legacy-peer-deps` from frontend dependency installation scripts and Docker build
- [x] Migrate to the Angular
  - [x] Target architecture
    - [x] Use Angular as a hybrid SSR/CSR frontend served by a frontend-owned Node.js runtime
    - [x] Keep Litestar as the backend API only (`/api/*`, `/api/docs`, service endpoints)
    - [x] Configure frontend fallback/hydration for CSR routes
    - [x] Keep legacy Litestar/Jinja/HTMX views only during migration
    - [x] Remove legacy views, templates, HTMX, Hyperscript, and template-only static files after parity
  - [x] API contracts and client integration
    - [x] Align Angular services with public/admin backend endpoints (`/api/competency-matrix/*`, `/api/admin/competency-matrix/*`, `/api/contacts`, `/api/auth`, `/api/account`, `/api/admin/files`, `/api/admin/wiki-links`)
    - [x] Add DTO interfaces matching backend camelCase response aliases
    - [x] Add explicit DTO -> UI model mapping functions in feature `models/`
    - [x] Add frontend service tests for endpoint URLs, query params, and response mapping
    - [x] Add missing backend API endpoints only where data currently exists only in Jinja templates
    - [x] Keep feature services using `ApiClient`; do not inject raw `HttpClient` outside `core/http/`
  - [x] Frontend app shell
    - [x] Route parity: `/how-this-site-is-built`, `/competency-matrix`, `/sitemap`, `/404`
    - [x] Redirect `/` to the localized site-build case study
    - [x] Header with current navigation and active route state
    - [x] Footer with docs, source, sitemap, and social links
    - [x] Global alert/notification area for API success and error feedback
    - [x] Theme service with `data-bs-theme`, localStorage persistence, and initial theme application
    - [x] Grid-only competency matrix view
    - [x] Move shared styles from `backend/src/static/styles.css` to Angular SCSS structure
    - [x] Move public assets from `backend/src/static/` to `frontend/public/`
  - [x] SEO and root files
    - [x] Page title and meta description per route
    - [x] Open Graph and Twitter meta tags for public pages
    - [x] Canonical URL per route
    - [x] favicon and icon variants
    - [x] Backend-generated `robots.txt`
    - [x] Backend-generated `sitemap.xml`
    - [x] sitemap page
    - [x] `/.well-known/appspecific/com.chrome.devtools.json`
  - [x] Competency matrix
    - [x] Sheets loading from `/api/competency-matrix/sheets`
    - [x] Selected sheet persistence in localStorage
    - [x] Question grid/table from `/api/competency-matrix/items`
    - [x] Preserve section -> subsection -> grade grouping
    - [x] Grid/table layout
    - [x] Search that hides empty sections and subsections
    - [x] Public matrix always uses public endpoints; admin `onlyPublished` filters live in the admin matrix workspace
    - [x] Question detail modal/page from public detail endpoints
    - [x] Markdown rendering for answers and resource context
    - [x] Code highlighting for Markdown code blocks
    - [x] External resources list
    - [x] Loading, empty, and error states for every API-backed view
  - [x] Public home
    - [x] Use the site-build case study as the public home
    - [x] Keep direct contact via footer links
  - [x] Auth and account
    - [x] Auth token storage strategy
    - [x] HTTP interceptor that sends `Authorization: Bearer <token>`
    - [x] 401 handling that opens login flow or redirects to login state
    - [x] Login modal
    - [x] Logout button
    - [x] navbar profile info
    - [x] Current user loading from `/api/account/base`
    - [x] Moderator/admin panel access based on account role, with backend guards still enforced
  - [x] Deployment and legacy cleanup
    - [x] Build Angular in CI/CD
    - [x] Build Angular as an independent frontend Docker image
    - [x] Serve Angular hybrid SSR/CSR from a frontend Node.js runtime
    - [x] Proxy `/api/*` and `/api/docs` from nginx to Litestar
    - [x] Smoke test direct route loads (`/how-this-site-is-built`, `/competency-matrix`, `/sitemap`)
    - [x] Smoke test browser refresh on Angular routes
    - [x] Remove `views_router` from Litestar app after Angular parity
    - [x] Remove Jinja templates and HTMX/Hyperscript dependencies after Angular parity
    - [x] Remove backend static vendor files replaced by Angular build assets
- [x] Replace static sitemap page with content-driven localized sitemap links.
- [x] Add and edit competency matrix questions
  - [x] Search through existing external resources
  - [x] Edit mode for a specific question in the admin matrix workspace
  - [x] Button and form for adding a question to a matrix section in the admin matrix workspace
  - [x] ToastUI should work through backend-owned file uploads, display uploaded files, edit content, save content.
- [x] "404" page
- [x] Check for possible convert raw Markdown to HTML on the frontend side only
- [x] Security audit
  - [x] Moderators and admins can edit, add, and delete matrix questions in the admin panel

### Articles

- [x] Content localisation for articles
  - [x] Store article `title_ru`, `title_en`, and `content_ru` / `content_en` as required columns, with article folders normalized into a required localized folder table
  - [x] Store tag `name_ru` and `name_en` as required columns
  - [x] Keep article `slug` and tag `slug` as single stable English identifiers shared across languages
  - [x] Require all RU/EN fields on create and update for both draft and published articles
  - [x] Read article list, detail, tree, tag list, and tag search results in the selected content language
  - [x] Search by `search_vector_ru` or `search_vector_en` depending on requested language
  - [x] Keep `tagSlug` as one language-neutral English filter
  - [x] Add admin-panel content authoring UI controls for editing RU and EN article and tag fields in one form
  - [x] Update the init Alembic migration during pre-deployment development
  - [x] Generate one follow-up autogen migration to verify SQLAlchemy models and migrations are consistent
  - [x] Cover backend and frontend behaviour with focused tests
- [x] Hide/Publish articles
- [x] Show articles sorted by publication date
- [x] Show articles in a side panel with a tree view
- [x] Show public article view counters and anonymous reactions
- [x] Admin article statistics by date range, source category, and reactions
- [x] Filters by tags
- [x] Filters by publish date range
- [x] Search articles by title and content
- [x] Article authoring and public articles release
  - [x] Use articles as the authored content model and keep save/publish independent from SEO warnings
  - [x] Add nullable RU/EN SEO metadata, managed cover file id, computed cover URL, and cover alt fields to article storage/API
  - [x] Require an explicit `metadata` request object while allowing individual metadata fields to be `null`
  - [x] Add article form controls for SEO metadata and cover upload through the backend file flow
  - [x] Expand the live admin SEO panel with metadata, cover, alt, and wiki-link checks
  - [x] Add in-form article/social preview for the active language
  - [x] Render typed `[[articles:<slug>]]` / `[[matrix:<slug>]]` links as internal localized links
  - [x] Warn when wiki links point to missing targets available in the admin target registry
- [ ] Extend managed `FileModel` metadata when the next file workflow needs it:
  - [ ] lifecycle status (`uploading`, `ready`, `deleteFailed`, `processingFailed`)
  - [ ] integrity metadata (`sha256`, S3 `etag`)
  - [ ] backend identifier (`storage_backend`) for future S3/local/CDN switching
  - [ ] ownership/audit metadata (`uploaded_by_username`)
  - [ ] image metadata (`width_px`, `height_px`) for cover/content image validation
  - [ ] processing metadata (`original_mime_type`, `original_size_bytes`, `processing_status`) for WebP conversion/compression
  - [ ] attachment safety metadata (`scan_status`, `scanned_at`) before broader attachment workflows
  - [ ] separate file variants table instead of adding variant columns to `FileModel`
- [ ] Add backend file-content signature checks during upload so duplicate files are not uploaded
  repeatedly; compute a stable signature such as `sha256`, return or link to an existing matching
  managed file when appropriate, and upload a new object only when no reusable file exists.
- [x] SEO Foundation release
  - [x] Add Angular hybrid rendering for public article routes while keeping interactive/admin routes CSR
  - [x] Add `/ru` and `/en` canonical URL prefixes
  - [x] Generate dynamic `sitemap.xml` and `robots.txt`
  - [x] Emit Article JSON-LD/Open Graph metadata from stored article metadata
  - [x] Add HTML smoke tests for public article pages and missing-article `404/noindex`
- [x] Matrix public SEO release
  - [x] Add explicit matrix question slugs
  - [x] Add separate public matrix question pages
  - [x] Preserve modal interaction from the matrix overview
  - [x] Emit FAQPage structured data after public question pages exist
- [x] Add owner/admin/moderator content workspace for articles with admin filters, create modal, edit detail route, tag management, and publish/delete dropdown actions.
- [ ] Add article editorial queues and richer workspace views.
- [ ] Add content health checks for articles: SEO metadata, cover alt text, stale translations, wiki-link issues, and broken external links.
- [ ] Add article revision history with diff and restore.
- [ ] Add autosave / local draft recovery for article editing.
- [ ] Add protected preview links for unpublished articles.
- [ ] Add scheduled publishing for articles.
- [ ] Add editorial workflow statuses for articles: idea, draft, review, ready, published, archived.
- [ ] Add Obsidian-compatible Markdown import/export for articles.
- [ ] Add privacy-safe AI-assisted authoring for spelling, SEO hints, tags, and RU/EN consistency.
- [ ] TTL (5 min) cache for analytics data
- [ ] Obsidian-like article editor
  - [x] Rich text editor
  - [x] Tags
  - [ ] Attachments
  - [x] typed links with articles and matrix questions using `[[articles:<slug>]]` / `[[matrix:<slug>]]`
  - [ ] Spell checking for Russian and English.
  - [ ] Check and warn when a wiki-link references unpublished material.
- [x] Security audit
  - [x] Moderators and admins can edit, add, and delete articles in the admin panel
  - [x] Regular users cannot view hidden articles

### Workspace

Workspace is protected owner/admin utilities that live only in the admin panel.

- [x] Resume
  - [x] Store private structured ATS-oriented resume documents outside the knowledge database.
  - [x] Store each resume as a single-language document with required saved RU/EN language.
  - [x] Add owner/admin backend CRUD API under `/api/admin/resumes`.
  - [x] Scope resume CRUD to the authenticated author so users only list and mutate their own resumes.
  - [x] Add owner/admin Workspace navigation and routes under `/admin-panel/workspace/resumes`.
  - [x] Add list, create with language selection, detail edit, language badge, selected-language preview, and delete UI.
  - [x] Keep resumes private: no public pages, sitemap entries, SEO, or themes in v1.
  - [x] Fix resume multilines fields: text with \\n to array.
  - [ ] Resume customization
    - [ ] Blocks order (Title, Photo, Summary, Experience, etc.)
    - [ ] Blocks visibility
    - [ ] Themes
  - [x] Resume export
    - [x] To PDF
    - [x] To DOCX
    - [x] Step-by-step maximize resume export ATS score.
    - [x] Fix readability of exported resume
- [x] Team
  - [x] Add owner/admin backend CRUD API under `/api/admin/accounts`.
  - [x] Add team Workspace navigation and routes under `/admin-panel/workspace/team`.
  - [x] Manage owner/admin/moderator usernames, roles, passwords, and active status with owner/admin governance.
  - [x] Enforce a single owner at the database level; reject owner self role/deactivation/delete actions.

### Knowledge database

Each knowledge item has its own subfolder in "knowledge database" folder on side-panel in admin panel.

- [ ] Workspace
  - [ ] Main page
    - [ ] Important info (in-dashboard CRUD – only text oneline items)
    - [ ] Dates and birthdays (current and next month)
    - [ ] Recently changed files
    - [ ] Statistics
      - [ ] Files per category count - badge next to folder name with amount of files.
  - [ ] Calendar (separated page. List of all dates and people birthdays in interactive calendar)
  - [ ] Access
    - [ ] V1: Owner/admin only, per-account knowledge items (users can see only their own items)
    - [ ] V2: Public knowledge items, users access to shared dashboard
    - [ ] V3: All users public and private items, per user dashboard
- [ ] Knowledge item
  - [ ] Books
    - [ ] All books page
    - [ ] All read books page
    - [ ] Books to buy page
    - [ ] Books by categories page
    - [ ] Books to reread page
  - [ ] Companies
  - [ ] Dates
  - [ ] People
  - [ ] Places
  - [ ] Projects
  - [ ] Recipes
  - [ ] Software
  - [ ] Techchecks
  - [ ] Techniques
  - [ ] Technologies
- [ ] Export Obsidian vault to knowledge database

### Auth and Users

- [ ] User authentication improvements (possibly via OAuth2)
  - [ ] (FRONT) Register button and form
  - [ ] (BACK) Registration logic
  - [ ] Remove the owner/admin/moderator-only login warning after regular-user authorization/login is implemented
  - [ ] (FRONT) Password recovery button and form (simple confirmation email)
  - [ ] (BACK) Password recovery logic
  - [ ] (BACK) Add session cookie (set on login/register, delete on logout)
- [ ] Privacy policy
- [ ] Terms of service
- [x] Personal data processing consent (frontend-only on contact form)
- [ ] Persist personal data processing consent on the backend with timestamp and source when contact requests or user accounts are stored.
- [ ] Add personal-data export/delete request flow.
- [ ] Add retention rules for contact requests, feedback reports, typo reports, subscriptions, and accounts.
- [ ] Password recovery
- [ ] Password confirmation
- [ ] Flashcards from competency matrix (stateful — saved per user)
- [ ] Comments on articles
- [ ] 2FA/MFA for users
- [ ] User profile
  - [ ] Course completion statistics
  - [ ] Edit personal details
  - [ ] Notification settings
  - [ ] Saved flashcard list
  - [ ] List of devices where the account was logged in
- [ ] Security audit
  - [ ] Users cannot interact with other users' profiles. Read-only.
  - [ ] No tokens in localStorage
  - [ ] Auth based on secure cookies: HttpOnly, Secure, SameSite=Lax
  - [ ] Session rotation on login
  - [ ] Session invalidation on logout
  - [ ] Expired sessions actually deleted / not accepted

### Flashcards

Flashcards should be implemented strictly after auth implementation for common users.

- [ ] Create flashcards from competency matrix (stateless — no persistence, restart = new set)
- [ ] Create custom flashcards
- [ ] Export user flashcards to .apkg format

### Competency Matrix Improvements

- [x] Content localisation for competency matrix
  - [x] Use stable `sheetKey` values as language-neutral sheet identifiers
  - [x] Localise sheets, sections, subsections, questions, answers, expected answers, resource names, and resource context
- [x] Move sheet, section, subsection to separated tables
- [x] Priority for matrix sheets, sections, and subsections with drag-and-drop admin ordering
- [x] Add a queue list for questions I want to add to the matrix
- [x] Ability to suggest a question for the competency matrix
- [x] Add moderation inbox for suggested matrix questions.
- [ ] Ability to report a typo in the competency matrix
- [ ] Add moderation inbox for report a typo in the matrix questions.
- [x] Add owner/admin/moderator content workspace for matrix questions with richer filters, public preview, edit detail route, and dropdown actions.
- [ ] Add content health checks for matrix questions: stale translations, wiki-link issues, resource issues, and broken external links.
- [ ] Add self-assessment / interview mode with expected-answer reveal.
- [ ] Track weak matrix topics for later study recommendations.
- [ ] Add matrix question revision history with diff and restore.
- [ ] Add matrix analytics panel for views, engagement, typo reports, and suggestions.
- [ ] Add matrix resource library with deduplication, reuse, tagging, and link checks.

### Competency roadmaps

- [ ] Add public direction roadmaps such as Python Backend, Frontend, etc.
- [ ] Dynamic roadmap rendering
- [ ] Links to matrix questions
- [ ] Links to articles
- [ ] Links to resources
- [ ] Links to courses
- [ ] Links to another roadmap (step, after which you may go to the next roadmap)

### Courses

- [ ] Link courses to competency matrix
- [ ] Browse available courses
- [ ] Create a course material step (can include video, text, images, files, tests)
- [ ] Playground for course tests (leetcode- or codewars-like checks)
- [ ] Create courses consisting of material steps
- [ ] Security audit
  - [ ] User cannot edit another user's course progress

### Other tasks

- [ ] Split monorepo into separate repos: front, back, infra.
- [x] UI localisation
- [x] Database localisation
- [ ] Migrate from Makefile to Just
- [x] Move complex logic out of Makefiles into dedicated script folders (`backend/scripts/`, `frontend/scripts/`, `infra/scripts/`); keep Makefiles as thin wrappers that only call Bash scripts or nested Makefiles.
- [x] Refactor project scripts so `make <command>` fully prepares and runs tests, linters, checkers, and similar commands without manual setup (start required Docker services, prepare data, and run other prerequisites as needed).
- [x] Cache on API get methods + cache invalidation on changes
- [x] Background cache warm
- [ ] Evaluate/migrate TaskIQ results to a durable backend when durable task history/auditing is needed.
- [ ] Filestorage service for files in MinIO with moderators(and admins)-only access
- [x] docker infra should be hotswap: no 502 errors caused by service restart lag (change docker-compose if its not possible)
- [ ] Add public changelog/updates page.
- [ ] Add RSS/Atom feeds for published articles and matrix updates.
- [ ] Add lightweight subscription channel for new articles, matrix items, and courses.
- [ ] Add public roadmap page for site/product development.

## Bugs

- [ ] Fix initial bundle big size.
- [x] Search does not work in "table" view mode (false positive; covered by frontend regression test)
- [x] Resource search is suboptimal (optimized through existing PostgreSQL pg_trgm support)
- [x] Production public UI QA
  - [x] Make the active `ru/en` language switch green instead of blue, matching the competency matrix active controls.
  - [x] Make the "to question" button on the competency matrix detail page green, consistent with the existing project button style.
  - [x] Localise the date-range filter placeholder: Russian may stay day-month-year format, but English should use a clearer US-style `mm.dd.yyyy` format.
  - [x] Add comfortable left and right padding to article text in the public articles list.
  - [x] Make the active article reaction state green instead of blue.
  - [x] On article detail pages, visually separate the back button from tags and make it green.
  - [x] Make the articles filter search button green.
  - [x] Prevent the English `Login` button text from wrapping as `Log` / `in`, so the header does not shift when switching languages.
  - [x] Move the `Folders` side-panel toggle to the left, replace the text button with an icon-only side-panel toggle whose icon reflects open/closed state, and add a simple open/close animation.
  - [x] Restyle the articles side panel so folders and articles read as a tree: reduce the default article background contrast, use hover background for articles, increase article indentation inside folders, and consider cohesive tree connector glyphs.
  - [x] Fix the sitemap page title overlapping the header.
  - [x] Show the list of published articles on the sitemap page.
  - [x] Remove the former public biography/contact surface from the unauthenticated site.
- [x] Production admin UI QA
  - [x] Make the logout control borderless: red text only, separated from the username by a vertical `|` delimiter.
  - [x] Prevent the English `Logout` button text from wrapping as `Log` / `out`.
  - [x] Make the add competency matrix question button green and move it inline after search.
  - [x] Make `published only` toggles green when enabled in admin matrix and article workspaces.
  - [x] Simplify admin actions for matrix questions and articles: use one actions dropdown in list rows and edit detail pages instead of several inline buttons.
  - [x] Make the admin `add article` control and article statistics navigation/action styling consistent with the admin UI.
  - [x] Move article statistics out of the public articles page and keep it in a dedicated admin page.
  - [x] Hide folders and filters when opening an article detail page.
  - [x] Fix Toast UI editor styling in dark theme so editing text and preview text remain readable and do not blend into the background.
  - [x] Fix the external resources modal: the Russian `add` button overflows the form, and both it and the save button should be green.
  - [x] Clarify which created external resource context field is Russian and which is English in the competency matrix question form.

## Documentation

- [x] Add parameter details to the API and include examples and other fields.
- [ ] Add public architecture, quality, and security articles as engineering documentation.

## Refactoring

- [x] Simplify BootstrapRenderer
- [x] Add pre-commit hooks (ruff, mypy, pytest)
- [x] Move CLI to a separate entry point (from main.py)
- [x] Use GradeEnum in API and core layer.
- [x] Rewrite NewType as regular classes.
- [x] Unite use-cases into a single class (separated by domain).
- [ ] Unite all repositories to the "unit of work" pattern.
- [ ] Fix taskiq not used imports of tasks from subpackages.
- [x] Move ResponseCacheKeyBuilder.build to target.
- [x] Move ResponseCachePayloadCodec to BaseModel.
- [x] Refactor core exceptions to inherit only from `Exception`/domain exception bases and move
  `verbose_http_exceptions` mapping to the Litestar entrypoint layer.
