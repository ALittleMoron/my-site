# Competency Matrix Question Editing Design

## Summary

Build admin-only create and edit flows for competency matrix questions in the existing Angular matrix page. The feature keeps the current question detail modal as the single interaction surface: admins can switch a loaded question from view mode to edit mode, or open the same modal in create mode from one global "Add question" button.

The feature also corrects the external resource model. External resources are reusable materials with `name` and `url`; the explanatory `context` belongs to the attachment between a question and a resource.

## Goals

- Admins can create competency matrix questions.
- Admins can edit existing competency matrix questions from the detail modal.
- Admins can attach existing external resources to a question.
- Admins can create a new external resource inline while editing a question.
- Admins can detach resources from a question.
- Admins can edit attachment context per question-resource pair.
- Both markdown answer fields use Toast UI Editor with image upload through `/api/files/presign-put`.
- Non-admin users cannot see or use create, edit, delete, publish, or unpublish controls.

## Non-Goals

- No separate resource management screen in this feature.
- No global update or delete for external resources in this feature.
- No per-section add buttons in this feature.
- No route-level edit/create pages; editing stays inside the matrix page modal.

## Backend Domain Model

`ExternalResource` represents reusable learning material:

- `id`
- `name`
- `url`

The question-resource attachment represents how a resource relates to one matrix question:

- `item_id`
- `resource_id`
- `context`

`context` is required in request and storage payloads. An explicit empty string means the resource is useful without extra explanation, and the frontend should omit the context text in view mode.

## Database Schema

Because the service is not deployed, update the current `0001_init.py` migration instead of adding a new Alembic migration.

`competency_matrix__external_resource_model`:

- keep `id`
- keep `name`
- keep `url`
- remove `context`

`competency_matrix__resource_to_item_secondary_model`:

- keep `id`
- keep `item_id`
- keep `resource_id`
- add `context`, non-null string without a server default

Add PostgreSQL trigram search support for resource autocomplete:

- `CREATE EXTENSION IF NOT EXISTS pg_trgm`
- GIN trigram index for `lower(name)`
- GIN trigram index for `lower(url)`

The codebase should continue to run tests against the existing test database setup. If SQLite compatibility matters for unit or integration helpers, trigram-specific DDL should be guarded or expressed in a PostgreSQL-safe Alembic way that does not break the configured test runner.

## Backend API

Keep the existing public endpoint shape where practical:

- `GET /api/competency-matrix/resources/search`
- `POST /api/competency-matrix/items`
- `PUT /api/competency-matrix/items/detail/{pk}`
- `GET /api/competency-matrix/items/detail/{pk}`

### Resource Search

`GET /api/competency-matrix/resources/search`

Query params:

- `searchName`: required search string
- `limit`: required integer, maximum `50`

Behavior:

- trim and normalize the search query using existing `SearchName` behavior;
- return an empty list for empty normalized search;
- search by resource `name` and `url`;
- sort exact or prefix `name` matches above weaker substring matches;
- cap results by `limit`.

Response stays:

```json
{
  "resources": [
    {
      "id": 1,
      "name": "Python docs",
      "url": "https://docs.python.org"
    }
  ]
}
```

### Question Detail Response

Question detail should stay convenient for the frontend by returning attached resources with their per-question context:

```json
{
  "id": 1,
  "question": "What is PEP8?",
  "answer": "...",
  "interviewExpectedAnswer": "...",
  "sheet": "Python",
  "grade": "Junior",
  "section": "Style",
  "subsection": "PEP8",
  "publishStatus": "Draft",
  "resources": [
    {
      "id": 10,
      "name": "PEP8",
      "url": "https://peps.python.org/pep-0008/",
      "context": "Official style guide."
    }
  ]
}
```

### Question Create/Update Request

Update the request contract so resources are explicit attachments.

Existing resource attachment:

```json
{
  "resourceId": 10,
  "context": "Official style guide."
}
```

New resource attachment:

```json
{
  "resource": {
    "name": "PEP8",
    "url": "https://peps.python.org/pep-0008/"
  },
  "context": "Official style guide."
}
```

Full request:

```json
{
  "question": "What is PEP8?",
  "answer": "...",
  "interviewExpectedAnswer": "...",
  "sheet": "Python",
  "grade": "Junior",
  "section": "Style",
  "subsection": "PEP8",
  "publishStatus": "Draft",
  "resources": [
    {
      "resourceId": 10,
      "context": "Official style guide."
    },
    {
      "resource": {
        "name": "Some article",
        "url": "https://example.com/article"
      },
      "context": ""
    }
  ]
}
```

The backend should reject malformed resource attachments that contain neither `resourceId` nor `resource`, or contain both.

## Frontend UX

### Modal Modes

Use one modal shell with explicit modes:

- `view`: current read-only question detail.
- `edit`: form for the selected question.
- `create`: empty form for a new question.

Do not open a second modal over the existing detail modal.

### Entry Points

For admins:

- show one global "Add question" button on the matrix page near existing filters;
- show "Edit" in question detail view;
- keep existing publish, unpublish, and delete actions in detail view.

For non-admin users:

- hide all mutation controls.

### Save Behavior

After successful create or edit:

- update the list for the selected sheet;
- show a success notification;
- keep the modal open;
- switch to `view` mode and show the saved question detail.

Create mode defaults:

- `publishStatus`: `Draft`;
- all other fields empty.

### Question Form

Fields:

- question text
- answer markdown
- interview expected answer markdown
- sheet
- grade
- section
- subsection
- publish status
- attached resources

`answer` and `interviewExpectedAnswer` use Toast UI Editor.

### Toast UI Editor

Implement a reusable Angular wrapper component around `@toast-ui/editor`.

Expected behavior:

- initialize from a string value;
- emit markdown changes into typed Angular forms;
- support dark theme if current app theme exposes enough state for that;
- use markdown edit mode;
- vertical preview;
- hide mode switch;
- toolbar includes heading, bold, italic, strike, lists, table, link, image, code, and codeblock;
- upload images via the current backend file flow.

Image upload flow:

1. Ask backend for upload URLs: `GET /api/files/presign-put?contentType=<mime>`.
2. Upload the blob with `PUT uploadUrl` and `Content-Type`.
3. Insert `accessUrl` into the editor markdown.

The old HTMX/Jinja implementation used `toastui.Editor` with `addImageBlobHook`; the Angular wrapper should preserve the same behavior, adapted to Angular service boundaries.

### Resource Picker

The resource form section supports:

- live search with debounce;
- search starts after 2 non-whitespace characters;
- attach an existing resource from search results;
- add a new resource inline by `name` and `url`;
- edit attachment context for each attached resource;
- detach an attached resource.

Existing resource `name` and `url` are read-only in the question form. Global editing and deletion of resources are reserved for a future resource management feature.

## Testing Strategy

### Backend

Use TDD for domain, storage, and API changes.

Cover:

- external resource no longer has global context;
- question detail returns resource context from the attachment;
- create question with existing resource attachment and context;
- create question with new resource attachment and context;
- update question changes attached resources and attachment contexts;
- detach by omission in update request;
- malformed resource attachment request is rejected;
- resource search trims query, applies limit, and returns expected matches;
- admin guards still protect create, update, delete, publish, and unpublish.

### Frontend

Cover:

- `MatrixService` create/update/search methods call correct endpoints and map DTOs;
- create button is visible only for admins;
- create opens modal in create mode with `Draft` default;
- edit button switches current detail modal into edit mode;
- save create/update returns to view mode with saved question;
- resource search debounces and attaches existing resources;
- inline new resource can be added;
- resource context can be edited independently from resource name/url;
- detach removes attachment from the outgoing request;
- Toast UI wrapper initializes, emits markdown changes, and calls upload flow.

Jest tests should mock Toast UI internals rather than test the third-party editor implementation itself.

## Documentation And Infrastructure Impact

- `docs/TODO.md` should be updated after implementation to reflect completed subtasks.
- The frontend dependency list and `frontend/package-lock.json` will change intentionally when adding `@toast-ui/editor`.
- The Docker/nginx split should not need changes because `/api/files/presign-put` already exists under the backend API route.
- No secrets or environment values are required.

## Open Implementation Notes

- Keep git state unchanged unless explicitly asked.
- Do not create a separate resource CRUD screen in this implementation.
- Prefer small feature-owned Angular components under the matrix feature.
- Prefer existing `make` targets for checks.
