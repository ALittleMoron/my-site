# Calendar

Calendar is a standalone, read-only core domain that composes private People birthdays and
memorable Dates. It does not belong to the Knowledge Dates domain and it is not a Dashboard domain:
Dashboard is a role-specific page that renders Calendar and other source-owned widgets.

## Architecture

`core/calendar` owns the calendar window, entry, summary, relationship projection, conversion, and
sorting schemas. `CalendarUseCase` only orchestrates the existing author-scoped
`KnowledgeDatesStorage`, `PeopleStorage`, and `KnowledgeItemsStorage` contracts. Collection
conversion and indexing stay in domain schema classmethods. Calendar has no tables or storage of its
own.

The source domains keep their persistence responsibilities:

- Dates select details for the requested months and load Date-to-Person links.
- People select birthday details for the requested months.
- Knowledge Items project display names for Dates and People.

The Date calendar index and the Person
`(author_username, birthday_month, birthday_day, item_id)` index support these reads. Query-plan
scenarios remain with their source storages.

## Admin API

```text
GET /api/admin/calendar
    ?referenceDate=YYYY-MM-DD
    &window=month|currentAndNextMonths
```

`month` returns the full month containing `referenceDate`.
`currentAndNextMonths` returns the full reference month plus the following month. The response
contains the explicit reference date and window, `memorableDateCount` and `birthdayCount`, and
ordered entries with an annual date, occurrence year, period, kind, display name, and related
People.

Entries are ordered by month in the requested window, day, memorable Date before birthday,
case-insensitive display name, and ID. December-to-January increments the occurrence year. February
29 remains an annual February value and is never moved to another day in a non-leap year.

The handler is classified as admin, guarded by `team_manager_guard` for owner/admin access, scoped
to the authenticated author's username, excluded from OpenAPI, uncached, and returned with
`Cache-Control: no-store`. Moderator, user, and anonymous callers are rejected. It is consumed only
from protected CSR routes.

## Dashboard Widgets

`/admin-panel` redirects to the standalone `/admin-panel/dashboard`. Dashboard is the first root
item in the shared sidebar tree and derives its selected state from the router URL.

Owner/admin Dashboard sections are selected through the same horizontal, wrapping tab pattern as
the Resume editor:

- Home is the general composition tab. It currently contains the independent foldable widget for
  upcoming memorable Dates and birthdays in the browser-local current and next months, and may gain
  other source-owned widgets without changing the tab identity;
- Calendar contains the foldable month-grid widget;
- Tools contains the foldable response-cache and expired-session widget.

Moderator Dashboard tabs instead show question-queue and competency-matrix work summaries. Only the
selected tab panel is visible, while every widget keeps its independent state. The panel header
remains visible inside its tab with a localized summary and accessible expanded state. Closed section
keys are stored per username under `adminDashboardSections:v1:<username>`; missing, corrupt, unknown,
or unavailable browser storage leaves sections open. Widget loading and errors remain independent,
so one failed request does not hide the other tabs.

The upcoming table links Dates and People to their existing details, formats only day/month, and
renders next-month, anniversary, and age information as a semantic list with locale-aware plural
rules.

The month grid starts at the browser-local current month. It supports previous/next navigation,
year stepping and a twelve-month chooser, localized weekday order, multiple linked entries per day,
today highlighting, stale-response rejection, and a responsive seven-column table. A February 29
entry in a non-leap selected year appears below the grid under “No day this year”.

The Tools widget preserves cache inspection, clear and asynchronous warm polling, session status
and pruning, confirmations, notifications, and independent retry states. The old
`/admin-panel/workspace/tools` URL redirects to Dashboard; `/api/admin/tools/*` is unchanged.

## Verification

Backend unit/API tests cover both windows, summary counts, sorting, related People,
December-to-January and leap-day behavior, empty results, author isolation, role access, `no-store`,
and OpenAPI exclusion. Storage tests and the realistic query-plan harness cover both month filters
and their indexes.

Frontend tests cover Calendar request serialization, horizontal role-specific Dashboard tabs,
accessible tab/panel relationships, per-user fold state, independent failures and retries,
localized summaries and plurals, the month grid and chooser, year transitions, locale week starts,
stale responses, February 29, links, multiple daily entries, and the embedded Tools workflow.
