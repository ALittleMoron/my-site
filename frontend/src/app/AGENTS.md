# Frontend Architecture Instructions

These rules apply to Angular app code under `frontend/src/app/**/*.ts`.

## Layer Structure

```text
frontend/src/app/
├── core/          # App-wide infrastructure only
├── shared/ui/     # Reusable primitives (only if 2+ features need it)
└── features/      # Feature modules — all domain code lives here
```

## Strict Import Rules

Never violate these boundaries:

- `core/` must not import from `features/` or `shared/ui/`.
- `features/<a>/` must not import from `features/<b>/`.
- `shared/ui/` must not import from `features/` or `core/`.
- Feature services must not inject `HttpClient` directly; use `ApiClient` from `core/http/`.
- When one feature needs data that is also used by another feature, do not import that other
  feature's service or model just for convenience. Add a small feature-owned service/model over the
  shared backend endpoint, or move a genuinely reusable primitive to an allowed shared layer.

## `core/` Contents

| Path                                         | Responsibility                                                         |
| -------------------------------------------- | ---------------------------------------------------------------------- |
| `core/http/api-client.service.ts`            | Typed `HttpClient` wrapper, sets base URL                              |
| `core/interceptors/auth.interceptor.ts`      | Attaches in-memory PASETO access token unless request context opts out |
| `core/interceptors/error.interceptor.ts`     | Maps `HttpErrorResponse`, refreshes once on protected 401s             |
| `core/editor/markdown-editor.component.ts`   | Shared ToastUI Markdown editor with image upload hook                  |
| `core/editor/editor-image-upload.service.ts` | Backend multipart upload flow for editor images                        |
| `core/auth/auth.service.ts`                  | Login/logout/refresh, startup restore, role capability signals         |
| `core/auth/auth-session.service.ts`          | Current account signal and derived local auth state                    |
| `core/auth/auth-token.service.ts`            | In-memory access token signal; never persist auth tokens               |
| `core/auth/auth-modal.service.ts`            | Login modal open/close signal                                          |
| `core/auth/auth.guard.ts`                    | `CanActivateFn` guards for content access and stricter team areas      |
| `core/layout/theme.service.ts`               | SSR-safe dark/light theme toggle, persists to `localStorage`           |
| `core/seo/seo.service.ts`                    | Sets `<title>`, meta, canonical, alternates, social tags, and JSON-LD  |
| `core/notifications/notification.service.ts` | App-wide transient success/error notifications                         |
| `core/privacy/consent.service.ts`            | SSR-safe frontend-only local consent persistence                       |
| `core/privacy/anonymous-reaction.service.ts` | Frontend-only anonymous reaction token and selection persistence       |
| `core/error/global-error-handler.ts`         | `ErrorHandler` impl — console in dev, Sentry in prod                   |
| `core/models/api-error.model.ts`             | `ApiError` interface matching backend `verbose_http_exceptions` shape  |

## I18n

- Runtime i18n is loaded once on app startup from the backend: request available languages first,
  then request the selected language bundle.
- Public prefixed routes (`/ru/...` and `/en/...`) must initialize UI/content language from the URL.
  Keep legacy unprefixed routes only for compatibility/protected SPA access, not canonical SEO.
- Do not hardcode user-facing interface strings in Angular templates or components. Use
  `TranslatePipe` in templates and `I18nService.translate()` in TypeScript code.
- The public updates page is static authored content, not UI catalog content. Keep accumulating
  changelog entries in `features/updates/updates.timeline.ts` as typed objects with `id`, `month`,
  `order`, localized RU/EN `title` and `summary`, and finite `tagIds`. Do not add
  `updates.month.*` or `updates.entry.*` keys to backend i18n; backend i18n for updates stays
  limited to page chrome, SEO text, footer label, and finite tag labels. Do not add tests that pin
  exact milestone copy, dates, ordering, or tag assignments; tests may cover grouping/localization
  behavior and the structural content shape.
- For sufficiently large user-visible, architectural, security, operations, or delivery changes,
  ask whether they should be added to the public updates page. Skip routine refactors, small fixes,
  incidental cleanup, dependency churn, and implementation-only details; group related work under a
  larger milestone when that is more natural.
- Grouped navigation item labels should not repeat the parent section domain when the section
  heading already provides that context. For example, under an Articles section use "Folders"
  rather than "Article folders", and under a Competency matrix section use "Questions" or
  "Structure" rather than repeating "matrix" in each item. Keep the domain in the item label only
  when removing it would make the label ambiguous or unnatural.
- Persist only supported language codes returned by the backend. Do not introduce frontend-only
  languages or language fallbacks that bypass the backend enum/catalog.
- Articles and article tags localise content through the articles API, not through the UI i18n bundle. Pass
  the current `I18nService.language()` value as the explicit `language` query parameter for
  localized read requests, edit both RU/EN article and tag `translations` in authoring forms, and send
  both languages in write payloads.
- Article authoring must send an explicit `metadata` object with article create/update payloads.
  Individual metadata fields may be null. Keep SEO analysis advisory-only, keep in-form
  article/social previews derived from the active language, and do not block save/publish on SEO
  warnings. Render typed wiki links from Markdown, currently `[[articles:<slug>]]` and
  `[[matrix:<slug>]]` with optional labels such as `[[matrix:<slug>|Custom label]]`, as internal
  localized links, and only warn about missing targets when the typed target registry is known.
- Require all RU/EN article and tag translation fields in frontend forms. Do not add frontend-only
  language fallbacks for localized content.
- Competency matrix content localises through the matrix API, not through the UI i18n bundle. Pass
  the current `I18nService.language()` value as the explicit `language` query parameter for sheets,
  structure trees, item lists, item details, resource search, and create/update responses; use stable
  `sheetKey` values for public sheet selection and required `subsectionId` values for question
  create/update persistence.
- Require all RU/EN competency matrix question, answer, expected-answer, structure inline-create,
  resource-name, and resource-context fields in frontend forms. Do not reintroduce manual
  sheet/section/subsection text fields on question forms; use the admin structure picker.
  Do not add frontend-only language fallbacks for localized content.
- Resume workspace content is single-language per resume. Forms must send required `language` plus
  one content shape, must not add resume-specific RU/EN controls, and must not validate whether the
  authored text matches the selected language. Editor chrome follows the current UI bundle; resume
  preview labels should render from the saved/selected resume language using backend i18n bundles.
- Do not localise other database/content text in this layer until the backend supports that content
  explicitly.

## `shared/ui/` Rules

- Add a component here only when 2+ features already use it.
- Standalone, `OnPush`, `@Input()`/`@Output()` or signal `input()`/`output()` only — no service
  injection or feature/domain state. Keep logic UI-local.
- Current primitives: `LoadingSpinnerComponent`, `ErrorMessageComponent`, `EmptyStateComponent`,
  `LocalizedDatePickerComponent`.

## Feature Structure

Each feature owns everything it needs:

```text
features/<name>/
├── <name>.routes.ts          # Feature routes (lazy-loaded sub-routes)
├── models/                   # Interfaces and DTO mapping functions
├── services/                 # HTTP services using ApiClient
└── pages/
    └── <page-name>/
        ├── <page>.component.ts/html/scss/spec.ts
        └── components/       # Presentational components used only by this page
```

- Page components: smart — hold signals, inject services, handle loading/error/empty.
- Presentational components: dumb — `@Input()`/`@Output()` only, no injection.
- Feature models must separate backend DTOs from UI models when their shapes differ.
- Feature services own endpoint calls and DTO-to-UI mapping; components should not depend on backend DTO shape.

## Existing Features

| Feature           | Route                                                                                                                              | Description                                                                                                                |
| ----------------- | ---------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------- |
| `admin-panel`     | `/admin-panel`                                                                                                                     | Protected CSR admin shell, owner/admin/moderator article/matrix workspaces, and owner/admin resume/team workspaces; no SSR |
| `auth`            | `/login`                                                                                                                           | Login page, no guard                                                                                                       |
| `matrix`          | `/ru/competency-matrix`, `/en/competency-matrix`, `/ru/competency-matrix/questions/:slug`, `/en/competency-matrix/questions/:slug` | CSR/hydrated matrix overview, SSR public question detail; unprefixed compatibility route remains                           |
| `articles`        | `/ru/articles/:slug`, `/en/articles/:slug`                                                                                         | SSR public article detail, CSR public list, folders side-panel, and tags                                                   |
| `site-case-study` | `/ru/how-this-site-is-built`, `/en/how-this-site-is-built`                                                                         | SSR public home and engineering case-study page; unprefixed compatibility route remains                                    |
| `updates`         | `/ru/updates`, `/en/updates`                                                                                                       | SSR public static updates/changelog page; unprefixed compatibility route remains                                           |
| `sitemap`         | `/ru/sitemap`, `/en/sitemap`                                                                                                       | Static Angular sitemap page; XML sitemap is backend-generated at `/sitemap.xml`                                            |
| `not-found`       | `/404`                                                                                                                             | Wildcard redirect target                                                                                                   |
| `shell`           | n/a                                                                                                                                | `SiteHeaderComponent`, `SiteFooterComponent` — not routed, used in `AppComponent`                                          |

## Routing

- `app.routes.ts` — top-level only. Lazy-loads feature routes via `loadChildren`.
- `/` redirects to the localized site-build case study using the initialized backend-driven UI
  language; keep shared public-home URL construction in `core/routing/`.
- Public canonical routes are language-prefixed. Keep `/ru/articles/:slug`, `/en/articles/:slug`,
  `/ru/how-this-site-is-built`, `/en/how-this-site-is-built`, `/ru/updates`, `/en/updates`,
  `/ru/competency-matrix/questions/:slug`, and `/en/competency-matrix/questions/:slug` as SSR
  routes, and render internal article/wiki links with the active language prefix.
- Protected CSR routes such as `/admin-panel` stay unprefixed and use runtime i18n state.
- Feature `routes.ts` — owns all sub-routes for that feature (`''`, `':id'`, etc.).
- Use `loadChildren` (not `loadComponent`) so adding sub-routes never touches `app.routes.ts`.
- Apply the broad content-access guard at protected parent route level. Add stricter child guards
  only for narrower role boundaries, such as owner/admin team workspaces inside `/admin-panel`.

## `app.config.ts`

Single place for all providers:

- `provideRouter(routes, withComponentInputBinding(), withInMemoryScrolling({ anchorScrolling: 'enabled', scrollPositionRestoration: 'enabled' }))`
- `provideHttpClient(withInterceptors([authInterceptor, errorInterceptor]))` — auth interceptor always first
- `provideAppInitializer(() => initializeAuth())` restores admin auth from `/api/auth/refresh`
  only for protected admin startup routes; public routes must not send anonymous refresh probes.
  Protected guards may restore from the same session cookie when no in-memory token exists. Keep
  auth refresh requests cookie + CSRF based, with no `Authorization` header.
- `provideClientHydration(...)` with transfer cache limited to safe public GETs only. Do not transfer
  auth, account, analytics, reaction, upload, file-management, or other private/side-effect endpoints.
- `{ provide: ErrorHandler, useClass: GlobalErrorHandler }`

No `AppModule`. No `NgModule` anywhere.
Keep `app.config.ts` as the only place for app-wide providers, interceptors, and global error-handler wiring.

## `app.config.server.ts` / SSR

- Server-only providers belong in `app.config.server.ts`.
- SSR API calls must rewrite relative `/api/*` URLs through the required `SSR_API_ORIGIN`
  environment variable.
- Public origin for canonical/transfer-cache mapping must come from explicit `SSR_PUBLIC_ORIGIN` or
  required `APP_URL_SCHEMA` + `APP_DOMAIN`.
- Browser-only features such as view tracking, engaged-view timers, reaction selection, downloads,
  storage-backed preferences, and content authoring interactions must not run during SSR.
- Browser-only access should go through injected Angular platform/document abstractions or narrowly
  scoped helpers. Do not read browser globals at module scope, and do not make public SSR routes
  depend on browser APIs being present.

## `ApiError` Shape

Matches `verbose_http_exceptions` backend library:

```ts
interface ApiError {
  code: string;
  type: string;
  message: string;
  location: string | null;
  attr: string | null;
  nested_errors?: ApiError[];
}
```

## What Not to Introduce

- NgRx or any global state library (unless proven necessary)
- Repository classes that only proxy `ApiClient`
- Abstract base components
- Facades over services
- Additional global state services unless 2+ features already need them
- Premature generic abstractions
