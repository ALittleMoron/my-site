# TODOs

## Development Stages

### Minimum Viable Product (MVP)

- [x] Competency matrix list as grid and list views
- [x] About me section
- [x] Contact form
- [x] Blog (no API, core functionality only)
- [x] Admin panel via SQLAdmin

- [x] Add Databasus for database backups
- [x] Configure Let's Encrypt
- [x] Remove password_hash from the User domain model
- [x] Remove the mentorship section. Keep "about me".
- [x] Fix static files on MinIO and the backup service.
- [x] (SEO) Add a canonical link
- [x] Validate CSS (focus on overriding Bootstrap variables)
- [x] Move Bootstrap (and other files as needed) to the static folder
- [x] Rebuild admin panel on Litestar
  - [x] Remove SQLAdmin
    - [x] Remove admin startup (docker, create_admin + Makefile)
    - [x] Move /presign-put to a Litestar handler
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
    - [x] (BACK) Guard on /api/files/presign-put
    - [x] (FRONT) Delete button on question detail
    - [x] (FRONT) Publish/Unpublish button (depending on status)
  - [x] Basic auth and edit permissions (PASETO without sessions. Sessions later)
    - [x] (FRONT) Login page with login button on the main page (hidden for now)
    - [x] (BACK) Login logic
    - [x] (FRONT) Logout button on the main page (hidden for now)
    - [x] (BACK) Logout logic (no-op for now)
    - [x] (BACK) Auth guard (only admins can log in for now)
    - [x] (BACK) Anonymous user
- [x] Smoke test
  - [x] Competency matrix search works as before: search, layout
  - [x] Matrix question modal opens, code blocks render correctly
  - [x] Run docker-compose and verify related services

### MVP Improvements

- [ ] (SEO) Add schemaMarkup link
- [ ] Check site performance
  - [ ] Load testing (Locust)
  - [ ] Lighthouse audit — fixes errors and improves scores
- [ ] Closed beta test with real users (friends, colleagues). Collect feedback and fix critical bugs.
- [ ] Add basic analytics (Matomo) for user behavior tracking.
- [ ] Optimize page load times (CSS/JS minification, image optimization). Consider CDN for static files.
- [ ] Migrate competency matrix from Google Docs to a database.
- [x] Move tests to backend and create a src subfolder for backend
- [ ] Deploy to a remote server
  - [ ] Choose hosting
  - [ ] Wire up missing secrets
  - [ ] Migrate deployment to Coolify
    - [ ] Install Coolify
    - [ ] Separate production and local Docker Compose
    - [ ] Configure the project per [this guide](https://dev.to/mandrasch/simple-coolify-example-with-docker-compose-github-deployments-53m)
  - [ ] Run deployment strictly from the GitHub workflow
  - [ ] After deployment, log in to exposed services and verify auth
    - [ ] MinIO admin panel
    - [ ] Databasus

### Security and Infrastructure

- [ ] Dependency scanning (Safety, Bandit, Trivy)
- [ ] VPN for accessing internal systems
- [ ] Add Dependabot to the repository
- [ ] Prepare repository split
    - [x] Move Angular static serving into a frontend-owned Docker image
    - [x] Keep infrastructure nginx as the edge reverse proxy
    - [ ] Move backend, frontend, and infrastructure into separate repositories
    - [ ] Configure independent image publishing for backend and frontend
    - [ ] Update deployment workflow to consume published images from the infrastructure repository
- [ ] Bot protection for the site
- [ ] Move DB migration out of app_lifespan into a separate task (possible in docker-compose)
- [ ] Replace uvicorn with Granian
- [ ] OWASP Top 10 compliance check
- [ ] Check for AI-based vulnerability scanning tools. Try one.
- [ ] Security audit
    - [x] Find a web application security checklist and go through it.
    - [ ] Regular users cannot access internal systems without VPN.
    - [ ] Build a threat model (who is the attacker, what do they want, etc.). Write to docs.
    - [ ] HTTP security headers in responses
        - [ ] Strict-Transport-Security
        - [ ] X-Content-Type-Options: nosniff
        - [ ] X-Frame-Options: DENY
        - [ ] Referrer-Policy: no-referrer
        - [ ] Content-Security-Policy
    - [ ] CSRF
        - [ ] All POST/PUT/PATCH/DELETE is protected from CSRF
        - [ ] CSRF token in cookie + header
        - [ ] CSRF verified on server
    - [ ] HTTPS and TLS
        - [ ] Everything redirects to HTTPS
        - [ ] HTTP isn’t served at all
        - [ ] TLS ≥ 1.2
        - [ ] Certbot auto-renews
        - [ ] No internal services are exposed to the public
    - [ ] XSS
        - [ ] All user-supplied data is escaped
        - [ ] No `| safe` without 100% certainty
        - [ ] Cannot save `<script>` to DB and render it. Check DB for such entries.
        - [ ] CSP in place
    - [ ] Passwords never logged
    - [ ] Hashing: unique salt used
    - [ ] Every protected handler checks the user (guards where needed)
    - [ ] No "hide button if not admin" logic without backend enforcement
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
        - [ ] All services have health checks
        - [ ] Nginx does not forward traffic to an unhealthy backend
        - [ ] Adequate restart policy
        - [ ] Image versions pinned
        - [ ] No `latest` tags
        - [ ] Images updated regularly
        - [ ] Minimal packages
        - [ ] Nginx not root
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
        - [ ] Only ports 80 and 443 are open
        - [ ] SSH by key only. Password login disabled.
    - [ ] Rate limiting and bot protection
        - [ ] Rate limit on login, registration, and password reset
        - [ ] IP / fingerprint-based limiting
        - [ ] No unlimited requests to heavy endpoints
    - [ ] Backup & recovery
        - [ ] Backups encrypted
        - [ ] Backups are not publicly accessible
        - [ ] Restore tested
        - [ ] No access to back up a panel without auth
    - [ ] Supply chain
        - [ ] Dependency versions pinned
        - [ ] Dependencies updated regularly
        - [ ] No pip install from untrusted sources

### Tracing and Monitoring

- [ ] Error alerts to Telegram bot
- [ ] Set up Grafana + Prometheus + Loki
- [ ] Set up a container health monitoring service
    - [ ] Send notifications on a container crash
    - [ ] Send notifications on high resource usage (CPU, RAM)
- [ ] Security audit
    - [ ] Regular users cannot access Grafana without VPN.

### Frontend

- [ ] Cookie consent
- [x] Fix question search on the frontend: empty sections should also be removed
- [ ] Make text selection colour match the site theme
- [ ] Add more feedback during API requests (notifications, errors, etc.)
- [ ] Migrate to the Angular
  - [ ] Target architecture
    - [x] Use Angular as an SPA served by frontend nginx
    - [x] Keep Litestar as the backend API only (`/api/*`, `/api/docs`, service endpoints)
    - [x] Configure nginx fallback to Angular `index.html` for frontend routes
    - [x] Keep legacy Litestar/Jinja/HTMX views only during migration
    - [x] Remove legacy views, templates, HTMX, Hyperscript, and template-only static files after parity
  - [x] API contracts and client integration
    - [x] Align Angular services with existing backend endpoints (`/api/competency-matrix/*`, `/api/contacts`, `/api/auth`, `/api/account`, `/api/files`)
    - [x] Add DTO interfaces matching backend camelCase response aliases
    - [x] Add explicit DTO -> UI model mapping functions in feature `models/`
    - [x] Add frontend service tests for endpoint URLs, query params, and response mapping
    - [x] Add missing backend API endpoints only where data currently exists only in Jinja templates
    - [x] Keep feature services using `ApiClient`; do not inject raw `HttpClient` outside `core/http/`
  - [ ] Frontend app shell
    - [x] Route parity: `/about-me`, `/competency-matrix`, `/sitemap`, `/404`
    - [x] Redirect `/` to `/about-me`
    - [x] Header with current navigation and active route state
    - [x] Footer with docs, source, sitemap, and social links
    - [ ] Global alert/notification area for API success and error feedback
    - [x] Theme service with `data-bs-theme`, localStorage persistence, and initial theme application
    - [x] Layout preference service for competency matrix list/grid view
    - [x] Move shared styles from `backend/src/static/styles.css` to Angular SCSS structure
    - [x] Move public assets from `backend/src/static/` to `frontend/public/`
  - [ ] SEO and root files
    - [x] Page title and meta description per route
    - [x] Open Graph and Twitter meta tags for public pages
    - [ ] Canonical URL per route
    - [x] favicon and icon variants
    - [x] `robots.txt`
    - [x] `sitemap.xml`
    - [x] sitemap page
    - [x] `/.well-known/appspecific/com.chrome.devtools.json`
  - [ ] Competency matrix
    - [x] Sheets loading from `/api/competency-matrix/sheets`
    - [x] Selected sheet persistence in localStorage
    - [x] Question list/table from `/api/competency-matrix/items`
    - [x] Preserve section -> subsection -> grade grouping
    - [x] List layout
    - [x] Grid/table layout
    - [x] Search that hides empty sections and subsections
    - [x] Admin-only published/all toggle using `onlyPublished`
    - [x] Question detail modal/page from `/api/competency-matrix/items/detail/{pk}`
    - [x] Markdown rendering for answers and resource context
    - [ ] Code highlighting for Markdown code blocks
    - [x] External resources list
    - [x] Loading, empty, and error states for every API-backed view
  - [x] About me
    - [x] landing
    - [x] Contact me form
    - [x] Preserve current image and content assets
    - [x] Typed reactive contact form
    - [x] Client validation matching backend constraints
    - [x] Backend validation error rendering, including nested errors
    - [x] Success notification after request creation
  - [ ] Auth and account
    - [x] Auth token storage strategy
    - [x] HTTP interceptor that sends `Authorization: Bearer <token>`
    - [ ] 401 handling that opens login flow or redirects to login state
    - [x] Login modal
    - [x] Logout button
    - [x] navbar profile info
    - [x] Current user loading from `/api/account/base`
    - [x] Admin-only controls based on account role, with backend guards still enforced
  - [ ] Deployment and legacy cleanup
    - [ ] Build Angular in CI/CD
    - [x] Build Angular as an independent frontend Docker image
    - [x] Serve Angular static files from frontend nginx
    - [x] Proxy `/api/*` and `/api/docs` from nginx to Litestar
    - [ ] Smoke test direct route loads (`/about-me`, `/competency-matrix`, `/sitemap`)
    - [ ] Smoke test browser refresh on Angular routes
    - [x] Remove `views_router` from Litestar app after Angular parity
    - [x] Remove Jinja templates and HTMX/Hyperscript dependencies after Angular parity
    - [x] Remove backend static vendor files replaced by Angular build assets
  - [ ] Verification
    - [x] Jest tests for page states: loading, error, empty, populated
    - [x] Jest tests for presentational component inputs and outputs
    - [x] Jest tests for services and DTO mapping
    - [ ] Backend unit/integration tests for any changed or new API endpoint
    - [ ] Manual parity checklist against former Litestar/Jinja/HTMX pages
    - [ ] Lighthouse audit after migration
    - [ ] Accessibility pass for navigation, forms, modals, and keyboard focus
- [ ] Add and edit competency matrix questions
  - [ ] Search through existing external resources
  - [ ] Edit mode for a specific question (button and form on question detail)
  - [ ] Button and form for adding a question to a matrix section
  - [ ] ToastUI should work as before: file uploads via /presign-put, display uploaded files, edit content, save content.
- [ ] "404" page 
- [ ] Check for possible convert raw Markdown to HTML on the frontend side only
- [ ] Security audit
  - [ ] Only admins can edit, add, and delete matrix questions

### Notes

- [ ] Hide/Publish notes
- [ ] Show notes sorted by publication date
- [ ] Show notes in a side panel with a tree view
- [ ] Filters by tags, categories, and date
- [ ] Search notes by title and content
- [ ] Obsidian-like note editor
    - [ ] Rich text editor
    - [ ] Tags
    - [ ] Attachments
    - [ ] links with other notes with `[[note]]` syntax
    - [ ] Properties
- [ ] Security audit
  - [ ] Only admins can edit, add, and delete posts
  - [ ] Regular users cannot view hidden posts

### Knowledge database

Knowledge database is a collection of knowledge items of two types: general and specific.

General knowledge item has common CRUD logic and looks the same as notes. A specific knowledge item has additional fields and has its own logic.

- [ ] Dashboard
  - [ ] Important info (in-dashboard CRUD – only text items)
  - [ ] dates and birthdays (current and next month)
  - [ ] recently changed files
  - [ ] statistics
- [ ] General Knowledge item
  - [ ] folders and subfolders
  - [ ] Hide/Publish items
  - [ ] CRUD with a rich text editor
- [ ] Specific Knowledge item
  - [ ] Shared logic
    - [ ] Hide/Publish the entire category
    - [ ] CRUD with a rich text editor
    - [ ] Tags
    - [ ] Attachments
  - [ ] Books
  - [ ] Companies
  - [ ] Dates
  - [ ] Offers
  - [ ] OS
  - [ ] People
  - [ ] Places
  - [ ] Projects
  - [ ] Prompts
  - [ ] Recipes
  - [ ] Software
  - [ ] Techchecks
  - [ ] Techniques
  - [ ] Technologies
- [ ] Export Obsidian vault to knowledge database

# Flashcards

- [ ] Create flashcards from competency matrix (stateless — no persistence, restart = new set)
- [ ] Create custom flashcards
- [ ] Export user flashcards to .apkg format

### Auth and Users

- [ ] User authentication improvements (possibly via OAuth2)
  - [ ] (FRONT) Register button and form
  - [ ] (BACK) Registration logic
  - [ ] (FRONT) Password recovery button and form (simple confirmation email)
  - [ ] (BACK) Password recovery logic
  - [ ] (BACK) Add session cookie (set on login/register, delete on logout)
- [ ] Privacy policy
- [ ] Terms of service
- [ ] Personal data processing consent
- [ ] Password recovery
- [ ] Password confirmation
- [ ] Flashcards from competency matrix (stateful — saved per user)
- [ ] Comments on blog posts
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

### Competency Matrix Improvements

- [ ] Add a separate queue list for questions I want to add to the matrix
- [ ] Ability to suggest a question for the competency matrix
- [ ] Ability to report a typo in the competency matrix

### Courses

- [ ] Link courses to competency matrix
- [ ] Browse available courses
- [ ] Create a course material step (can include video, text, images, files, tests)
- [ ] Playground for course tests
- [ ] Create courses consisting of material steps
- [ ] Security audit
    - [ ] User cannot edit another user's course progress

### Other tasks

- [ ] Split monorepo into separate repos: front, back, infra.
- [ ] UI localisation
- [ ] Migrate from Makefile to Just

## Bugs

- [ ] Search does not work in "table" view mode
- [ ] Resource search is suboptimal. Connect full-text search via [sqlalchemy-searchable](https://sqlalchemy-searchable.readthedocs.io/en/latest/quickstart.html)

## Documentation

- [ ] Add parameter details to the API and include examples and other fields.

## Refactoring

- [ ] Simplify BootstrapRenderer
- [x] Add pre-commit hooks (ruff, mypy, pytest)
- [x] Move CLI to a separate entry point (from main.py)
- [x] Use GradeEnum in API and core layer.
- [x] Rewrite NewType as regular classes.
- [x] Unite use-cases into a single class (separated by domain).
- [ ] Unite all repositories to the "unit of work" pattern.
