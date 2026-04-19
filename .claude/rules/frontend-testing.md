---
paths:
  - "frontend/src/**/*.spec.ts"
---

# Frontend testing rules

## Philosophy

Test behavior, not implementation. Focus on what the component/service does, not how it does it internally.

## Runner

Jest via `jest-preset-angular`. No Karma, no browser. Fast, CI-friendly.

## What to test

| Subject | What to verify |
|---|---|
| Page components | All states render: loading, error, empty, populated |
| Presentational components | Inputs render correctly, outputs emit on interaction |
| Services | Correct endpoint called, response mapped to model |
| `ApiClient` | Base URL prepended, error shape passed through |
| Guards | Return value (stub guard returns `true`) |

## What NOT to test

- Angular framework internals (router wiring, DI resolution)
- Third-party library behavior
- Template structure unrelated to state (CSS classes, exact DOM nesting)

## Patterns

### Component tests

```ts
TestBed.configureTestingModule({
  imports: [ComponentUnderTest],
  providers: [
    { provide: SomeService, useValue: mockService },
  ],
});
```

- Use `jasmine.createSpyObj` or `jest.fn()` for service mocks
- Test via rendered DOM state, not internal signal values
- Trigger CD with `fixture.detectChanges()`

### Service tests

```ts
TestBed.configureTestingModule({
  providers: [provideHttpClientTesting(), MatrixService, ApiClient],
});
```

- Use `HttpTestingController` to assert requests and flush responses
- Test: correct URL called, response mapped to expected model shape
- Always call `httpMock.verify()` after each test

### Signals in tests

- Set signal values directly on the component instance
- Call `fixture.detectChanges()` after mutating signals
- Assert on template output, not signal internals

## File naming

`<subject>.component.spec.ts` / `<subject>.service.spec.ts` — co-located with source file.

## No e2e

E2e tests are a separate future project. Do not scaffold Cypress or Playwright here.