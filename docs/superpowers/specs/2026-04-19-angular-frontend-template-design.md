# Angular Frontend Template Design

**Date:** 2026-04-19
**Status:** Approved

## Overview

Production-ready Angular application template replacing the existing HTMX/Jinja2 frontend. Lives in `frontend/`. Demonstrates architecture through the competency matrix list feature. Backend is Litestar with `verbose_http_exceptions` error format.

---

## Folder Structure

```
frontend/
└── src/
    ├── app/
    │   ├── core/
    │   │   ├── http/
    │   │   │   └── api-client.service.ts
    │   │   ├── auth/
    │   │   │   └── auth.guard.ts
    │   │   ├── interceptors/
    │   │   │   └── error.interceptor.ts
    │   │   └── models/
    │   │       └── api-error.model.ts
    │   │
    │   ├── shared/
    │   │   └── ui/
    │   │       ├── loading-spinner/
    │   │       ├── error-message/
    │   │       └── empty-state/
    │   │
    │   ├── features/
    │   │   └── matrix/
    │   │       ├── matrix.routes.ts
    │   │       ├── models/
    │   │       │   └── matrix-question.model.ts
    │   │       ├── services/
    │   │       │   └── matrix.service.ts
    │   │       └── pages/
    │   │           └── matrix-list/
    │   │               ├── matrix-list.component.ts
    │   │               ├── matrix-list.component.html
    │   │               ├── matrix-list.component.scss
    │   │               ├── matrix-list.component.spec.ts
    │   │               └── components/
    │   │                   └── matrix-question-card/
    │   │                       ├── matrix-question-card.component.ts
    │   │                       ├── matrix-question-card.component.html
    │   │                       └── matrix-question-card.component.spec.ts
    │   │
    │   ├── app.component.ts
    │   ├── app.config.ts
    │   └── app.routes.ts
    │
    ├── environments/
    │   ├── environment.ts
    │   └── environment.prod.ts
    └── styles/
        └── main.scss
```

---

## Architecture

### Core Layer (`app/core/`)

Single responsibility: app-wide infrastructure. No feature logic here.

**`ApiClient`** — typed wrapper around `HttpClient`. Feature services inject this, never `HttpClient` directly. Sets base URL from `environment.apiUrl`. One method per HTTP verb with generic typed return.

**Error interceptor** — catches all `HttpErrorResponse`, maps the response body to `ApiError`. Passes typed errors up to feature services.

**Auth guard** — stub `CanActivateFn` always returning `true`. Wiring exists for PASETO auth later. Applied to protected parent routes now.

**`app.config.ts`** — single entry point for `provideRouter`, `provideHttpClient(withInterceptors([...]))`, custom `ErrorHandler`. No `AppModule`.

### Shared UI Layer (`app/shared/ui/`)

Only three primitives, all justified by the matrix list page:

| Component | Purpose |
|---|---|
| `LoadingSpinnerComponent` | Shown during HTTP pending state |
| `ErrorMessageComponent` | Accepts `ApiError` input, emits retry output |
| `EmptyStateComponent` | Accepts `message` input, shown on empty list |

All standalone, `OnPush`, input/output only, no logic. Nothing added here until two features need it.

### Features (`app/features/`)

Feature-based structure. Each feature owns its routes, models, services, and page components. Features never import from each other.

### Global Error Handler

`ErrorHandler` overridden in `app.config.ts`. Logs to console in dev, to Sentry in prod (behind `environment.production` flag). Catches unhandled errors without coupling features to Sentry.

---

## Error Model

Matches `verbose_http_exceptions` backend library response shape:

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

---

## Routing

**`app.routes.ts`:**
```
/         → redirect to /matrix
/matrix   → loadChildren(() => matrix.routes)
```

**`matrix.routes.ts`:**
```
''    → MatrixListComponent
':id' → stub (detail page placeholder)
```

Lazy loading via `loadChildren` (not `loadComponent`) so adding sub-routes never touches `app.routes.ts`.

Auth guard applied to a protected parent route — stub now, PASETO later.

---

## Matrix Feature

### Models

`MatrixQuestion` interface matching backend DTO. Explicit mapping function when field names or shapes differ.

### `MatrixService`

- `getQuestions(search?: string): Observable<MatrixQuestion[]>`
- `getQuestion(id: string): Observable<MatrixQuestion>` — stub for detail page

### `MatrixListComponent` (page, OnPush)

Signals:
- `questions = signal<MatrixQuestion[]>([])`
- `loading = signal(false)`
- `error = signal<ApiError | null>(null)`
- `layoutMode = signal<'list' | 'grid'>('list')` — ephemeral, not in URL

Search:
- Read from `ActivatedRoute` query params on init
- Written back to URL on input change via `Router.navigate`
- Implemented as `FormControl<string>` (typed reactive form, single field)

States covered: loading, error (with retry), empty, populated list.

### `MatrixQuestionCardComponent` (presentational, OnPush)

- `@Input() question: MatrixQuestion`
- No logic, no injection
- Renders one card

---

## State Conventions

| Mechanism | Use |
|---|---|
| `signal()` | Mutable local component state |
| `computed()` | Derived values from signals |
| `effect()` | True side effects only (e.g. query param sync) |
| `toSignal()` | Converting `Observable` to signal in template |
| Service state | Only when state is shared across routes |

---

## Testing

**What is tested:**

| Subject | Approach |
|---|---|
| `MatrixService` | Unit test, `HttpClientTestingModule`, verifies endpoint + mapping |
| `MatrixListComponent` | `TestBed`, verifies all four states render correctly |
| `MatrixQuestionCardComponent` | Input test, verifies card renders question data |
| `ApiClient` | Unit test, base URL prepended, typed response |
| Auth guard stub | One test, returns `true` |

**Runner:** Jest via `jest-preset-angular`. No Karma, no browser.

**No e2e** — will be a separate project/setup in the future.

---

## Conventions

### Naming
- Files: `kebab-case`
- Classes/interfaces: `PascalCase`
- Signals: noun only — `questions`, `loading`, `error` (not `questionsSignal`)
- Services: `PascalCase` + `Service` suffix

### Components
- `OnPush` by default, no exceptions
- `inject()` over constructor injection
- Standalone only, no NgModules

### HTTP
- Feature services use `ApiClient`, never raw `HttpClient`
- Services return `Observable`
- Components consume via `toSignal()` or explicit subscribe with cleanup

### Forms
- `FormControl<T>` / `FormGroup` strictly typed
- No `any` in form types

### Imports
- Core never imports from features
- Features never import from other features
- Shared imports only from `shared/ui/`

---

## What Is NOT in This Template

- NgRx or heavy state management
- Repository pattern (services call ApiClient directly)
- Abstract base components
- Facades
- Global toast/notification service
- e2e tests
- Premature generic abstractions
