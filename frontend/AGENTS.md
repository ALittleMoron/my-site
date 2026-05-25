# Frontend Instructions

These rules apply to frontend Angular files under `frontend/**/*.ts`, `frontend/**/*.html`, and `frontend/**/*.scss`.

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
- Add co-located `.spec.ts` for new components and services unless the behavior is truly trivial.

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
- Sanitize any backend or user-provided Markdown/HTML before binding it with `[innerHTML]`.
- Keep direct `localStorage` access in core services; feature components may use it only for local UI preferences and must cover that behavior with tests.

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

## Frontend Testing

These testing rules apply when editing `frontend/src/**/*.spec.ts`.

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

### Signals in Tests

- Set signal values directly on the component instance.
- Call `fixture.detectChanges()` after mutating signals.
- Assert on template output, not signal internals.

### File Naming

`<subject>.component.spec.ts` / `<subject>.service.spec.ts` — co-located with source file.

### No E2E

E2e tests are a separate future project. Do not scaffold Cypress or Playwright here.
