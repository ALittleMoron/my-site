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
| `core/editor/markdown-editor.component.ts`   | Shared modular CodeMirror 6 Markdown editor with uploads and preview   |
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
- Require all RU/EN competency matrix question, answer, interview answer explanation, structure
  inline-create, resource-name, and resource-context fields in frontend forms. Do not reintroduce manual
  sheet/section/subsection text fields on question forms; use the admin structure picker.
  Do not add frontend-only language fallbacks for localized content.
- Resume workspace content is single-language per resume. Forms must send required `language` plus
  one content shape, must not add resume-specific RU/EN controls, and must not validate whether the
  authored text matches the selected language. Editor chrome follows the current UI bundle; resume
  preview labels should render from the saved/selected resume language using backend i18n bundles.
- Do not localise other database/content text in this layer until the backend supports that content
  explicitly.

## Markdown Editor Architecture

- Treat the shared Markdown editor as an Obsidian-like, keyboard-first source-authoring product.
  Markdown text remains the source of truth, while syntax-aware presentation makes headings,
  inline and fenced code, lists, tasks, quotes, callouts, tables, and future supported constructs
  easy to scan. The product has three global modes on one `EditorView`: Editor enables structural
  pseudo-renderers, Source exposes plain Markdown with basic syntax highlighting, and Preview uses
  the centralized sanitized renderer. Both authoring modes share one wrapping icon toolbar derived
  from the same typed registry as hotkeys. Every action keeps its localized accessible name and
  hover title; do not add another toolbar, live split view, WYSIWYG mode, or a per-consumer renderer
  without an explicit product decision.
- Keep the editor auto-height with a `20rem` minimum: the page or modal owns vertical scrolling,
  not CodeMirror or consumer wrappers. Keep the mode/command header and status/shortcut footer
  sticky within the editor's bounds with zero visible scrollport-edge inset, including compensation
  for `modal-body` padding. The sticky header must redraw the editor frame above its content so its
  rounded border remains visible while the original frame scrolls away. Report both controls' live
  heights through CodeMirror scroll margins so they do not hide the cursor.
- Fullscreen is an app-owned fixed overlay on the existing editor shell, never a replacement editor
  or the browser Fullscreen API. Preserve the same `EditorView`, document, history, selections,
  Editor/Source/Preview mode, uploads, and unsaved value. Trap focus, use the shared
  reference-counted page scroll lock, let editor-owned surfaces consume Escape first, and restore
  the nearest external scroll position and the original focus without closing an owning modal.
- Build on direct modular CodeMirror 6 packages, not an Angular wrapper, `basicSetup`, a fork, or
  copied internals. Use CodeMirror's public extension points—facets, compartments, state fields,
  view plugins, syntax trees, decorations, keymaps, and transactions—so library upgrades and
  future editor features remain replaceable at module boundaries.
- Keep the Angular component an integration shell for browser/SSR lifecycle, required inputs and
  outputs, focus and tab behavior, backend-driven i18n, and image-upload orchestration. Keep
  commands, Markdown configuration, and semantic presentation in focused editor modules that do
  not depend on Angular. Add substantial capabilities as cohesive extensions with tests instead
  of accumulating unrelated logic in the component.
- Apply authoring commands as minimal CodeMirror change sets. Never rebuild the whole document for
  a local edit; preserve history, selections, snippets, upload anchors, scroll, and incremental
  parser state. A table structural command may replace only its owning table in one undoable
  transaction, and explicit table formatting may canonicalize that table. A full-document
  replacement is allowed only for a genuinely changed external input value and must stay out of
  undo history.
- Derive Editor-mode presentation from the CodeMirror syntax tree in a viewport-aware view plugin.
  Use decorations and stable semantic classes rather than regex-scanning the entire document,
  rewriting editor DOM, or maintaining a parallel document model. Product CSS and extension-scoped
  CodeMirror themes own visual design; parser and transaction code own document semantics.
  Highlight fenced-code contents through the centralized Prism language registry shared with
  preview; do not introduce a second source-mode language registry or bundle every CodeMirror
  language package by default.
- Keep editor-only compiled theme files attached to the lazy standalone editor component; do not
  import them from `styles/main.scss` or another initial stylesheet. Keep each theme slice within
  the existing component-style budget instead of raising bundle budgets.
- Keep interactive Markdown tables in the Angular-independent table extension. Gate them on valid
  Lezer `Table` nodes, keep cell content as real Markdown source, use public block wrappers,
  decorations, widgets, state effects, public tooltip/gutter APIs, and transactions, and leave
  malformed tables untouched. Cell selection is one contiguous rectangular `anchor`/`head` range:
  same-cell pointer gestures remain native text editing, crossing a cell boundary starts table
  selection, Shift extends it, and Escape or an outside click clears it. Delete, Backspace, and Cut
  must adapt in one undoable transaction: the whole grid deletes the table, full-width ranges
  delete rows and may promote the next row to header, full-height ranges delete columns, and partial
  ranges clear only cell contents. Keep edge-only add controls and Pointer Events drag handles out
  of table geometry. The table must remain a quiet continuation of the editor, not a bordered or
  elevated card. Keep each semantic row on its own CodeMirror source line and lay its semantic cells
  out as one responsive equal-track grid; do not use CSS table formatting that can merge unrelated
  editor lines into one visual row. Empty and populated cells share a stable minimum row height,
  every track may shrink without creating a phantom cell or horizontal page overflow, and controls
  stay inside the editor viewport and transparent until their own edge hover/focus target is reached.
  Remove the Markdown delimiter and its line break from Editor-mode height geometry with a direct
  block replacement; never collapse that source line with `display: none`. Block wrappers must not
  use vertical margins because CodeMirror cannot reliably include collapsing margins in its height
  map; reserve edge-control space with measured padding instead. Normalize uneven rows to the common
  column count and show one gutter number for the whole table only in Editor mode. Clicking an empty
  cell or an edge control and typing in any cell must not scroll the owning page. Keep the focused
  cell unambiguous with a source-position caret drawn through a public CodeMirror layer, never an
  inline content widget. At a visible cell end, keep the DOM selection associated with that cell
  instead of the next one so repeated Chrome and Firefox input cannot drift across the grid.
  Drag handles must remain absolute siblings outside editable cell marks, expose distinct hit areas
  for every row and column, and show both pickup and drop state without changing grid geometry.
  Cross-cell selection must collapse CodeMirror's ordinary document selection so only the bounded
  rectangular overlay remains. When a table ends at document EOF, preserve one final protected
  blank Markdown line as the valid place to type outside the grid. When later content exists, every
  line after the table remains ordinary editable content; terminator protection must not spread to
  the first or second following line. Input on a protected EOF terminator must move following prose
  after the separator in the same undoable transaction, and deletion must not collapse the
  separator and turn prose into a table row. Editor and Preview must consume that same unchanged
  source contract. Arrow navigation must stay cell-aware inside the grid without skipping or
  misaligning ordinary source lines around a table. Preserve TSV/CSV clipboard, keyboard
  navigation, context-menu accessibility, alignment, sorting, touch controls, and one-step undo.
  Keep the table theme extension-scoped so it stays in the lazy authoring bundle instead of the
  global initial stylesheet. Do not add formulas, merged cells, typed columns, filters, persisted
  widths, a second editor, or raw DOM mutation.
- Pass Angular's CSP nonce into `EditorView.cspNonce` and let CodeMirror provide its runtime base
  layout and accessibility rules. Compiled editor-scoped CSS may theme public CodeMirror classes
  and stable `classHighlighter`/semantic classes, but must not copy or override CodeMirror's
  internal base-theme mechanics.
- Render preview only through `WikiLinkRendererService`, preserving typed wiki links, Prism
  highlighting, and DOMPurify as the shared XSS boundary. Never add raw `[innerHTML]`, a second
  Markdown parser, or consumer-specific sanitization.
- Keep formatting actions in the typed command registry with stable command IDs and physical
  `KeyboardEvent.code` mappings for RU/EN layouts. User-facing labels, key explanations, search
  phrases, upload states, and errors come from backend i18n. Preserve IME composition, native
  platform undo/redo/navigation, multi-selection, and the CodeMirror `Escape`, then `Tab`
  keyboard-trap escape hatch.
- Preserve readable padding, line numbers, line wrapping, light/dark variables,
  Editor/Source/Preview focus restoration, validation classes, unsaved-value propagation, and image
  paste/drop/picker ordering. New settings, palettes, syntax features, and attachment flows must
  extend these foundations rather than bypass them.

## Editor Platform Quality and Testing Standard

- Apply this standard to the current Markdown-first editor and every future Editor platform mode,
  including any programming-course assignment editor that reuses only part of the shared
  foundation. A mode may omit irrelevant Markdown features, but every behavior it does expose must
  meet the same regression standard.
- Treat the Editor platform as a high-risk interaction system. Test every observable behavior and
  every meaningful equivalence class, including combinations, boundary states, and sequences that
  were not part of the original bug report. Do not limit a change to one happy path or the exact
  reproduction the user happened to find.
- Do not spend coverage effort on unsupported external tampering such as a user manually deleting
  editor-owned DOM nodes. Do cover all interactions available through the product, browser input,
  CodeMirror transactions, commands, pointer/keyboard events, clipboard, focus, and mode changes.
- Use TDD for every editor behavior change or bug fix. Add the smallest focused failing behavioral
  test first, expand it into the complete parameterized regression matrix, confirm that it fails
  for the expected reason, and only then edit production code.
- Before implementation, identify the shared invariant behind all reported symptoms. Fix that
  invariant once; do not accumulate special cases for ArrowLeft, ArrowRight, ArrowUp, ArrowDown,
  Space, a particular row count, one browser timing path, or one source spelling.
- An existing green suite is not proof that a reported editor bug is fixed. The suite has already
  missed real cursor, selection, scrolling, whitespace, and table-boundary regressions. Every
  report requires a new failing regression test even when nearby tests pass.
- Never weaken, delete, skip, narrow, or rewrite an existing test merely to accept a new
  implementation. If a previous expectation conflicts with the clarified product contract, record
  the contract change explicitly and replace it with stronger coverage for both the new behavior
  and the old regression boundary.
- Build parameterized interaction matrices across every applicable dimension:
  - Editor, Source, and Preview modes;
  - focused and unfocused state, normal and fullscreen layout, page and modal ownership;
  - document start, middle, and end, with zero, one, and multiple visible lines before and after the
    edited construct;
  - empty, short, long, partially filled, and malformed content;
  - ASCII, Cyrillic, other Unicode, emoji, punctuation, escaped delimiters, links, inline/fenced
    code, Markdown syntax, and leading, trailing, repeated, or replacement whitespace;
  - forward and reverse direction;
  - collapsed, non-empty, rectangular, cross-boundary, and multiple selections;
  - a fresh editor, repeated actions in one editor, undo/redo, and repeated equivalent editors
    after CodeMirror measurement/update cycles.
- For interactive tables, cover the full applicable cross-product of header, first/middle/final
  body row; first/middle/final column; one, two, and many semantic rows and columns; even and uneven
  rows; empty and populated cells; canonical spaces, `||`, `| |`, `|cell|`, missing outer pipes,
  and rows without a trailing pipe; and tables at every document boundary.
- Enumerate every valid and forbidden table caret position. Valid positions are authored cell
  content, the valid empty-cell input position, and ordinary visible lines outside the table.
  Forbidden positions include leading/trailing/inter-cell pipes, the delimiter row, structural
  padding, hidden line-break geometry, and positions beyond an editable cell edge. Test direct
  selection, input, deletion, and all navigation directions from every class.
- If CodeMirror or browser geometry temporarily yields a forbidden caret position, test that
  recovery is deterministic and direction-aware. It must reach the intended adjacent cell or
  immediately adjacent ordinary line, never an arbitrary globally "next" position.
- Cover all selection shapes in both directions: part/all of ordinary text, part/all of one cell,
  adjacent and non-adjacent source cell content, semantic single cell, partial/full row,
  partial/full column, rectangular group, whole table, delimiter/pipe boundaries, prose entering or
  leaving a table, prose surrounding part/all of a table, whole document, and disjoint
  multi-selection.
- For every applicable selection shape, verify rendering, replacement, typing, Backspace, Delete,
  Cut, Copy, undo, redo, structural protection, and selection direction. Assert that ordinary text
  selection does not create a full-editor geometric block, semantic rectangular selection stays
  inside its selected cells, selected content remains readable in light/dark themes, and duplicate
  selection layers do not appear.
- Cover every keyboard action inside content, at both edges of every cell, at all grid edges, and on
  adjacent ordinary lines: ArrowLeft/Right/Up/Down, Shift/Alt-or-Option/Ctrl/Meta plus every arrow,
  Tab, Shift+Tab, Enter, Shift+Enter, Space and repeated/replacement spaces, Backspace, Delete, Home,
  End, PageUp, PageDown, Insert, Escape, native undo/redo, and every registered editor hotkey on RU
  and EN physical keyboard layouts.
- Preserve and test native IME composition, platform navigation/modifiers, browser text selection,
  spellcheck-facing content, clipboard behavior, drag/drop, pointer/touch input, focus transitions,
  and the CodeMirror Escape then Tab keyboard-trap escape hatch. A custom editor keymap must not
  consume a native interaction outside its exact contract.
- Assert complete observable state after each action, not just a boolean return: exact document
  source; selection anchor, head, association, and range count; active semantic cell; table
  validity and dimensions; scroll request and rendered target; caret/selection layer count and
  bounds; focus; history grouping; and exact one-step undo/redo result.
- Cursor and selection visuals are behavior. Test that exactly the intended cursor(s) exist, no
  duplicate native/custom cursor appears, empty and populated cell carets remain within one cell
  line, blinking/custom layers address the correct source position, and selection/caret geometry
  cannot span unrelated rows or cells.
- Scrolling is behavior. Test both transaction `scrollIntoView` intent and the rendered DOM target.
  Hidden Markdown geometry must never move the owning page when the visible destination is a
  pseudo-rendered cell. Do not "fix" this by disabling scrolling for one key while leaving the same
  invalid geometry reachable by other actions.
- For timing-dependent or intermittent reports, never write probabilistic or flaky assertions.
  Recreate the same initial state repeatedly, drive all relevant CodeMirror update/measurement
  phases deterministically, and require the same exact outcome on every iteration.
- Prefer public CodeMirror state, transactions, commands, events, stable semantic classes, and
  rendered behavior over private helpers or copied internals. Do not assert source-code strings,
  private method names, arbitrary DOM nesting, or exact implementation details.
- JSDOM cannot prove real browser selection color, caret geometry, font metrics, or page scrolling.
  Automate every state/DOM contract it can represent, keep production build/style-budget checks
  green, and list the remaining real-browser visual checks explicitly. Do not perform manual
  browser testing until the user requests it for the current editor change.
- Treat line/branch coverage as a diagnostic, not a substitute for the interaction matrix. Aim for
  literal 100% coverage of changed editor behavior and review every uncovered changed branch.
  Report exact coverage honestly and never describe it as 100% unless it is literally 100%.
- After each focused red/green cycle, run all related editor suites to catch immediate interaction
  regressions. Before completion, run the complete frontend tests and coverage, formatting, lint,
  type checking, and production build through existing Make targets, then perform a dedicated
  self-review for missing combinations, weakened tests, flaky timing, browser-only gaps, and
  violations of these standards.

## `shared/ui/` Rules

- Add a component here only when 2+ features already use it.
- Standalone, `OnPush`, `@Input()`/`@Output()` or signal `input()`/`output()` only — no service
  injection or feature/domain state. Keep logic UI-local.
- Current primitives: `LoadingSpinnerComponent`, `ErrorMessageComponent`, `EmptyStateComponent`,
  `LocalizedDatePickerComponent`, `SiteSelectComponent`.
- Use `LocalizedDatePickerComponent` for calendar-date fields because native date-picker popovers
  cannot be themed consistently with the site. Keep values as ISO `YYYY-MM-DD`, pass all labels
  from backend i18n, and use `controlSize="small"` when the picker sits beside compact inline
  controls. Preserve its modal dialog/grid semantics, roving focus, keyboard navigation, Angular
  Forms validation, and stylesheet-owned positioning; do not replace the native dialog top layer
  with runtime inline positioning that would weaken the strict CSP.
- Use `SiteSelectComponent` for single-select controls instead of native `<select>`. Feature owners
  must build localized `readonly SiteSelectOption[]` values and preserve transport/query values
  exactly; the shared component must not inject `I18nService` or know feature enums. Keep its
  select-only combobox/listbox ARIA contract, native-like keyboard/typeahead commit and cancel
  behavior, Angular Forms/CVA integration, top-layer popover, and stylesheet-owned anchor
  positioning. Do not add runtime inline positioning, visible search, or a separate mobile modal.

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

| Feature           | Route                                                                                                                              | Description                                                                                                                       |
| ----------------- | ---------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------- |
| `admin-panel`     | `/admin-panel`                                                                                                                     | Protected CSR admin shell, owner/admin/moderator article/matrix workspaces, and owner/admin People/resume/team workspaces; no SSR |
| `auth`            | `/login`                                                                                                                           | Login page, no guard                                                                                                              |
| `matrix`          | `/ru/competency-matrix`, `/en/competency-matrix`, `/ru/competency-matrix/questions/:slug`, `/en/competency-matrix/questions/:slug` | CSR/hydrated matrix overview, SSR public question detail; unprefixed compatibility route remains                                  |
| `articles`        | `/ru/articles/:slug`, `/en/articles/:slug`                                                                                         | SSR public article detail, CSR public list, folders side-panel, and tags                                                          |
| `site-case-study` | `/ru/how-this-site-is-built`, `/en/how-this-site-is-built`                                                                         | SSR public home and engineering case-study page; unprefixed compatibility route remains                                           |
| `updates`         | `/ru/updates`, `/en/updates`                                                                                                       | SSR public static updates/changelog page; unprefixed compatibility route remains                                                  |
| `sitemap`         | `/ru/sitemap`, `/en/sitemap`                                                                                                       | Static Angular sitemap page; XML sitemap is backend-generated at `/sitemap.xml`                                                   |
| `not-found`       | `/404`                                                                                                                             | Wildcard redirect target                                                                                                          |
| `shell`           | n/a                                                                                                                                | `SiteHeaderComponent`, `SiteFooterComponent` — not routed, used in `AppComponent`                                                 |

## Agent Client Administration

- Keep lifecycle and audit views in the owner-only admin contour backed by the owner-guarded
  `/api/admin/agent-clients` API. Do not broaden them to admin/moderator roles or public routes.
- Registration accepts only a client-generated CSR, name, and explicit least-privilege scopes.
  Never request, upload, cache, or render a client private key. Make the one-time certificate return
  clear and require explicit confirmation for permanent client revocation.
- Present agent-created matrix items as drafts requiring human review. Do not add direct private
  Agent API/MCP execution, publishing, generic CRUD, structure changes, URL fetching, shell/HTTP
  controls, or imply a claim grants broader authority.

## Knowledge People

- Keep People under the owner/admin-protected CSR routes
  `/admin-panel/knowledge/people` and `/admin-panel/knowledge/people/:id`; never add these private
  responses to SSR or transfer cache.
- Use explicit typed People forms/models for person details, birthday, tags, relationships, photo,
  and attachments. Do not introduce a schema-driven universal knowledge form renderer; future
  knowledge types should own their typed feature facade and interaction design.
- Read private photos/downloads only through protected blob responses and revoke every object URL
  when it is replaced or no longer displayed. People descriptions may use the shared sanitized
  Markdown editor, but image paste/drop/picker uploads must remain disabled because inline public
  media would bypass the private knowledge-file workflow.

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
