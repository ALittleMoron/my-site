# Frontend Instructions

These rules apply to frontend Angular files under `frontend/**/*.ts`, `frontend/**/*.html`, and `frontend/**/*.scss`.

## Stack

- Angular 21, standalone components only
- Angular hybrid rendering with `@angular/ssr`: public article and competency matrix question routes use SSR, interactive protected routes remain CSR/hydrated Angular.
- Keep Angular framework packages, Angular CLI/build tooling, and `angular-eslint` on the same Angular major.
- SCSS for styles
- Bootstrap 5 via `styles/main.scss`
- Jest via `jest-preset-angular` for tests
- Node.js production runtime for the frontend Docker image; do not reintroduce a frontend-owned nginx runtime unless a new design explicitly asks for it.

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
- Add co-located `.spec.ts` for new components and services unless the behavior is truly trivial.
- Treat public reading/detail views differently from management workspaces: keep detail pages focused
  on the content being read, and avoid showing list filters, tree navigation, bulk controls, or other
  workspace-only controls unless they are directly needed for the detail workflow.
- Icon-only controls must expose an accessible name and make their current state clear through icon,
  title, ARIA state, or surrounding context.
- Prefer native form controls for standard input types. When users need format guidance, provide
  visible localized hints and titles instead of replacing the control or adding custom parsing unless
  the product behavior explicitly requires it.

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
- Sanitize any backend or user-provided Markdown/HTML before binding it with `[innerHTML]`; SSR paths must not depend on browser-only sanitizer APIs.
- Put reusable frontend upload helpers under `core/uploads/`, not `core/media/`; the latter matches
  a repository ignore pattern.
- Keep direct `localStorage` access in core services; feature components may use it only for local UI preferences and must cover that behavior with tests. All storage, `window`, `document.defaultView`, timer, analytics, reaction, upload, and DOM-download behavior must be guarded so public SSR detail pages can render without browser APIs.

## SSR and Browser APIs

- Treat SSR as a pure render path. Browser-only capabilities such as storage, crypto, DOM mutation,
  timers, analytics, reactions, downloads, uploads, and editor setup must be behind platform guards or
  injected browser-document accessors and must not run during server rendering.
- Browser capability helpers should fail closed: return `null`, skip work, or no-op when no browser
  context exists, and callers must handle that absence explicitly instead of assuming the browser is
  always available.
- When adding or changing storage-backed UI preferences, preserve browser persistence and add tests
  that prove the same code path does not touch browser-only APIs with a server-like document.

## Forms

- `FormControl<T>` and `FormGroup<T>` — always typed
- No `any` in form types
- Single field -> `FormControl<T>`. Multiple related fields -> `FormGroup`

## Comments

- No comments explaining WHAT the code does
- Comments only for non-obvious WHY: hidden constraint, workaround, subtle invariant

## Styles

- Prefer Bootstrap utilities and existing CSS variables before adding component SCSS.
- Component SCSS must stay focused on local layout/overrides, not global theme concerns.
- Add new colors through theme variables, not hardcoded component palettes.
- Keep action hierarchy consistent across public and admin UI. Primary create/save/edit actions may
  use the positive accent; destructive or publication-state-changing actions should usually be less
  visually dominant unless the surrounding design establishes a stronger pattern.

## Frontend Testing

These testing rules apply when editing `frontend/src/**/*.spec.ts`.

### Manual Browser Checks

- When manually testing frontend routes in a browser, start the local service stack from the
  repository root with `make run` and test the app served by that stack. Do not replace this with
  ad hoc Node/SSR harnesses, one-off mock servers, or direct `ng serve` runs unless `make run` is
  unavailable or the task explicitly needs a narrower fallback; if a fallback is used, state why and
  clean it up before finishing.

### Philosophy

Test behavior, not implementation. Focus on what the component/service does, not how it does it internally.

### Runner

Jest via `jest-preset-angular`. No Karma, no browser. Fast, CI-friendly.

### What to Test

| Subject | What to verify |
|---|---|
| Page components | All states render: loading, error, empty, populated |
| Presentational components | Inputs render correctly, outputs emit on interaction |
| Services | Correct endpoint called, response mapped to model |
| `ApiClient` | Base URL prepended, error shape passed through |
| Guards | Return value (stub guard returns `true`) |

### What Not to Test

- Angular framework internals (router wiring, DI resolution)
- Third-party library behavior
- Template structure unrelated to state (CSS classes, exact DOM nesting)

### Patterns

```ts
TestBed.configureTestingModule({
  imports: [ComponentUnderTest],
  providers: [
    { provide: SomeService, useValue: mockService },
  ],
});
```

- Use `jasmine.createSpyObj` or `jest.fn()` for service mocks.
- Test via rendered DOM state, not internal signal values.
- Trigger CD with `fixture.detectChanges()`.

```ts
TestBed.configureTestingModule({
  providers: [provideHttpClientTesting(), MatrixService, ApiClient],
});
```

- Use `HttpTestingController` to assert requests and flush responses.
- Test: correct URL called, response mapped to expected model shape.
- Always call `httpMock.verify()` after each test.
- When changing SSR route config, server entrypoints, public detail SEO, or transfer-cache behavior, update focused unit tests and `make ssr-smoke`.

### Signals in Tests

- Set signal values directly on the component instance.
- Call `fixture.detectChanges()` after mutating signals.
- Assert on template output, not signal internals.

### File Naming

`<subject>.component.spec.ts` / `<subject>.service.spec.ts` — co-located with source file.

### No E2E

E2e tests are a separate future project. Do not scaffold Cypress or Playwright here.
