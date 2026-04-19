---
paths:
  - "frontend/src/app/**/*.ts"
---

# Frontend architecture rules

## Layer structure

```
frontend/src/app/
├── core/          # App-wide infrastructure only
├── shared/ui/     # Reusable primitives (only if 2+ features need it)
└── features/      # Feature modules — all domain code lives here
```

## Strict import rules — NEVER violate

- `core/` — NO imports from `features/` or `shared/ui/`
- `features/<a>/` — NO imports from `features/<b>/`
- `shared/ui/` — NO imports from `features/` or `core/`
- Feature services — NO direct `HttpClient` injection; use `ApiClient` from `core/http/`

## core/ contents

| Path | Responsibility |
|---|---|
| `core/http/api-client.service.ts` | Typed `HttpClient` wrapper, sets base URL |
| `core/interceptors/error.interceptor.ts` | Maps `HttpErrorResponse` → `ApiError` |
| `core/auth/auth.guard.ts` | Auth guard (`CanActivateFn`). Stub until PASETO auth implemented |
| `core/models/api-error.model.ts` | `ApiError` interface matching backend `verbose_http_exceptions` shape |

## shared/ui/ rules

- Add a component here only when 2+ features already use it
- Standalone, `OnPush`, `@Input()`/`@Output()` only — no service injection, no logic
- Current primitives: `LoadingSpinnerComponent`, `ErrorMessageComponent`, `EmptyStateComponent`

## Feature structure

Each feature owns everything it needs:

```
features/<name>/
├── <name>.routes.ts          # Feature routes (lazy-loaded sub-routes)
├── models/                   # Interfaces and DTO mapping functions
├── services/                 # HTTP services using ApiClient
└── pages/
    └── <page-name>/
        ├── <page>.component.ts/html/scss/spec.ts
        └── components/       # Presentational components used only by this page
```

- Page components: smart — hold signals, inject services, handle loading/error/empty
- Presentational components: dumb — `@Input()`/`@Output()` only, no injection

## Routing

- `app.routes.ts` — top-level only. Lazy-loads feature routes via `loadChildren`
- Feature `routes.ts` — owns all sub-routes for that feature (`''`, `':id'`, etc.)
- Use `loadChildren` (not `loadComponent`) so adding sub-routes never touches `app.routes.ts`
- Auth guard applied at protected parent route level — not per-leaf-route

## app.config.ts

Single place for all providers:
- `provideRouter(routes, withComponentInputBinding())`
- `provideHttpClient(withInterceptors([errorInterceptor]))`
- Custom `ErrorHandler` (console in dev, Sentry in prod via `environment.production`)

No `AppModule`. No `NgModule` anywhere.

## ApiError shape

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

## What NOT to introduce

- NgRx or any global state library (unless proven necessary)
- Repository classes that only proxy `ApiClient`
- Abstract base components
- Facades over services
- Global notification/toast service (until 2+ features need it)
- Premature generic abstractions