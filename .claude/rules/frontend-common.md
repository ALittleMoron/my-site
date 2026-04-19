---
paths:
  - "frontend/**/*.ts"
  - "frontend/**/*.html"
  - "frontend/**/*.scss"
---

# Frontend common rules

## Stack

- Angular (latest stable), standalone components only
- SCSS for styles
- Bootstrap 5 via `styles/main.scss`
- Jest via `jest-preset-angular` for tests

## TypeScript

- `strict: true` — no exceptions
- No `any`. Use `unknown` + type narrowing if shape is unknown
- Explicit return types on public methods and functions
- Prefer `interface` over `type` for object shapes

## Naming

- Files: `kebab-case` (e.g. `matrix-question-card.component.ts`)
- Classes and interfaces: `PascalCase`
- Signals: noun only — `questions`, `loading`, `error` (not `questionsSignal`, not `isLoading$`)
- Observables: noun + `$` suffix — `questions$`
- Services: `PascalCase` + `Service` suffix

## Components

- `OnPush` change detection — no exceptions
- `inject()` over constructor injection
- Standalone only — no `NgModule`
- No logic in templates. Move conditions and transforms to component class or `computed()`
- Semantic HTML. Accessibility attributes where meaningful (`aria-label`, `role`, etc.)

## State

| Mechanism | Use |
|---|---|
| `signal()` | Mutable local component state |
| `computed()` | Derived values — never duplicated signal state |
| `effect()` | True side effects only (e.g. syncing to query params) |
| `toSignal()` | Converting `Observable` to signal for template consumption |
| Service state | Only when state is shared across multiple routed components |

## HTTP

- Feature services inject `ApiClient` — never raw `HttpClient`
- Services return `Observable<T>` — no Promises
- Components consume via `toSignal()` or explicit `subscribe` with `DestroyRef` cleanup
- DTOs mapped to UI models explicitly when field names or shapes differ

## Forms

- `FormControl<T>` and `FormGroup<T>` — always typed
- No `any` in form types
- Single field → `FormControl<T>`. Multiple related fields → `FormGroup`

## Comments

- No comments explaining WHAT the code does
- Comments only for non-obvious WHY: hidden constraint, workaround, subtle invariant