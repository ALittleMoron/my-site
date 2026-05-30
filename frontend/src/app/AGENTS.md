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

## `core/` Contents

| Path                                         | Responsibility                                                        |
| -------------------------------------------- | --------------------------------------------------------------------- |
| `core/http/api-client.service.ts`            | Typed `HttpClient` wrapper, sets base URL                             |
| `core/interceptors/auth.interceptor.ts`      | Attaches PASETO token to outgoing requests                            |
| `core/interceptors/error.interceptor.ts`     | Maps `HttpErrorResponse` -> `ApiError`                                |
| `core/editor/markdown-editor.component.ts`   | Shared ToastUI Markdown editor with image upload hook                 |
| `core/editor/editor-image-upload.service.ts` | Presign + unsigned upload flow for editor images                      |
| `core/auth/auth.service.ts`                  | Login/logout, `isAdmin()` signal, session state                       |
| `core/auth/auth-session.service.ts`          | Current account signal and derived local auth state                   |
| `core/auth/auth-token.service.ts`            | Token read/write from `localStorage`                                  |
| `core/auth/auth-modal.service.ts`            | Login modal open/close signal                                         |
| `core/auth/auth.guard.ts`                    | `CanActivateFn` — redirects to `/about-me` if not admin               |
| `core/layout/theme.service.ts`               | Dark/light theme toggle, persists to `localStorage`                   |
| `core/layout/layout-preferences.service.ts`  | Layout state shared across shell components                           |
| `core/seo/seo.service.ts`                    | Sets `<title>` and meta tags per route                                |
| `core/notifications/notification.service.ts` | App-wide transient success/error notifications                        |
| `core/privacy/consent.service.ts`            | Frontend-only local consent persistence                               |
| `core/privacy/anonymous-reaction.service.ts` | Frontend-only anonymous reaction token and selection persistence      |
| `core/error/global-error-handler.ts`         | `ErrorHandler` impl — console in dev, Sentry in prod                  |
| `core/models/api-error.model.ts`             | `ApiError` interface matching backend `verbose_http_exceptions` shape |

## I18n

- Runtime i18n is loaded once on app startup from the backend: request available languages first,
  then request the selected language bundle.
- Do not hardcode user-facing interface strings in Angular templates or components. Use
  `TranslatePipe` in templates and `I18nService.translate()` in TypeScript code.
- Persist only supported language codes returned by the backend. Do not introduce frontend-only
  languages or language fallbacks that bypass the backend enum/catalog.
- Do not localise database/content text in this layer yet; only interface chrome, labels,
  validation copy, notifications, SEO chrome, and enum labels belong in the UI i18n bundle.

## `shared/ui/` Rules

- Add a component here only when 2+ features already use it.
- Standalone, `OnPush`, `@Input()`/`@Output()` only — no service injection, no logic.
- Current primitives: `LoadingSpinnerComponent`, `ErrorMessageComponent`, `EmptyStateComponent`.

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

| Feature     | Route                | Notes                                                                             |
| ----------- | -------------------- | --------------------------------------------------------------------------------- |
| `about`     | `/about-me`          | Static page with contact form                                                     |
| `auth`      | `/login`             | Login page, no guard                                                              |
| `matrix`    | `/competency-matrix` | Auth-guarded, filter/grid/detail                                                  |
| `notes`     | `/notes`             | Public list/detail, admin CRUD, folders side-panel, tags                          |
| `sitemap`   | `/sitemap`           | Static                                                                            |
| `not-found` | `/404`               | Wildcard redirect target                                                          |
| `shell`     | n/a                  | `SiteHeaderComponent`, `SiteFooterComponent` — not routed, used in `AppComponent` |

## Routing

- `app.routes.ts` — top-level only. Lazy-loads feature routes via `loadChildren`.
- Feature `routes.ts` — owns all sub-routes for that feature (`''`, `':id'`, etc.).
- Use `loadChildren` (not `loadComponent`) so adding sub-routes never touches `app.routes.ts`.
- Auth guard applied at protected parent route level — not per-leaf-route.

## `app.config.ts`

Single place for all providers:

- `provideRouter(routes, withComponentInputBinding(), withInMemoryScrolling({ anchorScrolling: 'enabled' }))`
- `provideHttpClient(withInterceptors([authInterceptor, errorInterceptor]))` — auth interceptor always first
- `{ provide: ErrorHandler, useClass: GlobalErrorHandler }`

No `AppModule`. No `NgModule` anywhere.
Keep `app.config.ts` as the only place for app-wide providers, interceptors, and global error-handler wiring.

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
