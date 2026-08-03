# Knowledge Database

The knowledge database is a private owner/admin workspace. Its first typed item workspaces are
People and Dates. The common item, taxonomy, file, and access boundaries remain reusable for future
knowledge types. It is not a public content API and is not part of Angular SSR.

## Architecture

The model uses a typed extension pattern:

- `KnowledgeItem` owns the common identity, `kind`, `author_username`, display name, description,
  tags, and timestamps.
- `PersonDetails` is a required one-to-one extension of a `person` item and owns person-specific
  names, contact fields, and birthday.
- `KnowledgeDateDetails` is a required one-to-one extension of a `date` item and owns a recurring
  calendar day/month plus an optional non-future first year.
- Date-to-Person links are author-scoped normalized many-to-many rows. Dates own link editing;
  People expose read-only backlinks.
- People-specific relationships and relationship types stay in their own normalized tables.
- The core layer exposes generic knowledge-item and file contracts plus typed `PeopleUseCase` and
  `KnowledgeDatesUseCase` facades. People and Dates expose author-scoped month reads to the
  standalone Calendar read domain; Calendar owns cross-domain conversion, relationship projection,
  summary counts, and ordering. PostgreSQL, S3, Litestar, and Angular remain outside the core model.

Knowledge code is physically partitioned by ownership:

- `core/knowledge/{items,files,people,dates}` contains the matching domain enums, schemas, contracts,
  services, and use cases.
- `entrypoints/litestar/api/knowledge/{items,files,people,dates}` contains transport schemas and
  controllers; `knowledge/router.py` only composes those controllers.
- `infra/postgresql/{models,storages}/knowledge/{items,files,people,dates}` and
  `infra/ioc/prodivers/knowledge/` mirror the same boundaries.

Future item types should add their own typed one-to-one extension and feature facade. A universal
JSON/EAV field bag or a universal dynamic form renderer would discard database constraints,
searchability, type safety, and explicit product behavior, so it is not the extension mechanism.

## Access And Isolation

All knowledge endpoints are admin-classified under `/api/admin/knowledge/*`, guarded for owner and
administrator roles, excluded from OpenAPI, and returned with `Cache-Control: no-store`.
`/admin-panel/knowledge/people`, `/admin-panel/knowledge/dates`, and the knowledge detail routes are
protected CSR routes; they are never SSR or Angular transfer-cache inputs. The standalone
`/admin-panel/dashboard` is a cross-domain page: its owner/admin view consumes the standalone
Calendar projection, while its moderator view consumes competency-matrix work summaries. Calendar
architecture and its private API are documented in [calendar.md](calendar.md).

Knowledge data is private per author account. `author_username` is part of every list, lookup,
mutation, relationship, tag, and file predicate. Composite foreign keys repeat the author beside
entity IDs, so a guessed ID from another author cannot be joined into the caller's graph. Missing
and foreign-owned IDs follow the same not-found behavior. This invariant is covered by storage,
use-case, and API IDOR tests and must be preserved for every new knowledge type.

## PostgreSQL Model

Migrations `0014_add_knowledge_people_and_private_files.py`,
`0015_add_knowledge_dates.py`, and `0016_add_people_birthday_calendar_index.py` add:

| Table | Purpose and main invariants |
| --- | --- |
| `knowledge__knowledge_item_model` | Common item with `KnowledgeItemKind.PERSON` or `DATE`, author, display name, description up to 100,000 characters, timestamps, and unique `(id, author_username)`. |
| `knowledge__person_details_model` | Required one-to-one person extension keyed by `item_id`; composite item/author FK; required first and last names; blankable email, phone, and Telegram contact fields; optional all-or-nothing day/month birthday with optional year; calendar-valid and non-future dated birthdays. |
| `knowledge__date_details_model` | Required one-to-one Date extension; calendar-valid required day/month, optional year, composite item/author FK, and author/calendar index. |
| `knowledge__date_person_model` | Author-scoped Date↔Person links with composite FKs, cascade cleanup, and indexes for both date-side loading and Person backlinks. |
| `knowledge__knowledge_tag_model` | Author-owned taxonomy; case-insensitive unique name per author. |
| `knowledge__knowledge_item_tag_model` | Author-scoped many-to-many item/tag link; item deletion cascades and an in-use tag is restricted from deletion. |
| `knowledge__person_relationship_type_model` | Author-owned symmetric or directional labels. Symmetric types use one identical forward/reverse label; directional types require both. |
| `knowledge__person_relationship_model` | Author-scoped edge between two distinct people; typed, directional view with an optional note up to 10,000 characters; one edge for each unordered person pair and type. |
| `knowledge__knowledge_file_model` | Private attachment/photo metadata, object path, MIME, size, names, SHA-256, and `KnowledgeFileKind`; composite item/author FK and unique object path. |

List and relation indexes start with `author_username`. Stable list indexes support name and
updated-at sorting, item-tag membership, file lookup, and relationship traversal from either side.
The Date calendar index and the Person `(author_username, birthday_month, birthday_day, item_id)`
index support the two-month calendar projection without scanning another author's private rows.
GIN trigram indexes cover the common item display name plus case-insensitive tag,
first/middle/last name, and email search.
A partial unique index allows at most one `PERSON_PHOTO` for a person. Composite author FKs and
unique keys prevent cross-author references even if application validation regresses.

People list search covers person names and email only; phone and Telegram remain intentionally
non-searchable contact fields. Multiple tag IDs use AND semantics. Supported sorts are
newest/oldest update and ascending/descending name, with explicit pagination.

Dates list search covers the common display name. Multiple tag IDs use AND semantics and an
optional `relatedPersonId` applies an author-scoped backlink filter. Supported sorts are recurring
calendar order, newest/oldest update, and ascending/descending name, with explicit pagination.

## Admin API

People and Dates keep their typed CRUD APIs below. Their author-scoped month reads are storage
contracts consumed internally by the standalone Calendar domain; they are not additional Knowledge
HTTP handlers. See [calendar.md](calendar.md) for `/api/admin/calendar`.

People:

| Method | Path | Purpose |
| --- | --- | --- |
| `GET` | `/api/admin/knowledge/people` | Paginated list with `page`, `pageSize`, `sort`, optional `searchQuery`, and repeated `tagIds`. |
| `POST` | `/api/admin/knowledge/people` | Quick-create from required first and last name. |
| `GET` | `/api/admin/knowledge/people/{personId}` | Full person, tags, relationships, photo metadata, and attachments. |
| `PUT` | `/api/admin/knowledge/people/{personId}` | Replace editable details and apply typed relationship create/update/delete commands. |
| `DELETE` | `/api/admin/knowledge/people/{personId}` | Delete the person graph and schedule object cleanup after commit. |
| `GET` | `/api/admin/knowledge/people/relationship-types` | List the current author's relationship types. |
| `POST` | `/api/admin/knowledge/people/relationship-types` | Create a symmetric or directional type. |
| `PUT` | `/api/admin/knowledge/people/relationship-types/{typeId}` | Replace an existing type. |
| `DELETE` | `/api/admin/knowledge/people/relationship-types/{typeId}` | Delete an unused type. |

Person detail responses also include required `relatedDates` backlinks. Link mutations remain
Date-owned.

Dates:

| Method | Path | Purpose |
| --- | --- | --- |
| `GET` | `/api/admin/knowledge/dates` | Paginated search, AND-tag and Person filters, plus calendar/update/name sorting. |
| `POST` | `/api/admin/knowledge/dates` | Quick-create from a display name and annual date. |
| `GET` | `/api/admin/knowledge/dates/{dateId}` | Full date, tags, related People, private attachments, and timestamps. |
| `PUT` | `/api/admin/knowledge/dates/{dateId}` | Replace the date, description, tags, and People links. |
| `DELETE` | `/api/admin/knowledge/dates/{dateId}` | Delete the Date graph and schedule attachment cleanup after commit. |

Taxonomy and private files:

| Method | Path | Purpose |
| --- | --- | --- |
| `GET` / `POST` | `/api/admin/knowledge/tags` | List/search or create an author-owned tag. |
| `PUT` / `DELETE` | `/api/admin/knowledge/tags/{tagId}` | Rename or delete an unused tag. |
| `PUT` / `DELETE` | `/api/admin/knowledge/people/{personId}/photo` | Replace or remove the single protected photo. |
| `POST` | `/api/admin/knowledge/items/{itemId}/attachments` | Upload a protected attachment. |
| `PUT` / `DELETE` | `/api/admin/knowledge/items/{itemId}/attachments/{fileId}` | Rename or remove an attachment. |
| `GET` | `/api/admin/knowledge/files/{fileId}/content` | Author-check and stream protected bytes. |

The API returns a protected `contentPath` for file reads, never an S3 URL or presigned URL.

## Private Files

Private knowledge objects live in the dedicated `knowledge-private` MinIO bucket. The backend uses
the internal authenticated S3 client only. Storage initialization creates the bucket when needed
and removes any bucket policy and bucket CORS configuration; it never enables anonymous reads.
The public `s3.<APP_DOMAIN>` nginx listener returns `404` for both `/knowledge-private` and
`/knowledge-private/*` before the general MinIO proxy.

Photos accept JPEG, PNG, or WebP up to 5 MiB. Pillow fully decodes the supplied bytes, verifies that
the detected type matches the declared MIME type, rejects animated images and decompression-bomb
warnings/errors, applies EXIF orientation, bounds the image to 2048×2048, and always writes WebP.
Attachments accept arbitrary MIME types up to 20 MiB and are served as downloads rather than
trusted active content. Each upload route has a request-body limit equal to its advertised file
limit plus bounded multipart overhead, and the backend reads at most the file limit plus one byte
before applying the core size rule. Persisted original names and MIME types are capped at 255
characters.

After the author predicate succeeds, the backend streams S3 content in bounded chunks and closes
the response body. Photos use `image/webp` with inline disposition; attachments use
`application/octet-stream` with a sanitized attachment filename. Every response adds
`Cache-Control: no-store` and `X-Content-Type-Options: nosniff`.

Database deletion is transaction-owned. Replaced/deleted object names are registered as
post-commit cleanup actions, so rollback cannot remove still-referenced data. Cleanup is best
effort and logs only bucket-level outcome/counts, not private object content. Newly uploaded objects
are separately registered for request rollback and commit-failure cleanup, while successful commit
discards those rollback actions. A failed cleanup can still leave an orphan and needs operational
follow-up; it must not replace the original request/commit error or turn a committed database
mutation into a misleading client failure.

## Angular Workspaces And Dashboard

The lazy CSR routes are:

- `/admin-panel/dashboard` — the standalone `/admin-panel` landing page described in
  [calendar.md](calendar.md). People and Date names in its calendar widgets link back to their typed
  detail routes; moderators instead see queue and matrix work summaries.
- `/admin-panel/knowledge/people` — URL-synchronized search, AND-tag filters, sorting, page size,
  pagination, loading/error/empty/populated states, quick create, tag management, and delete.
- `/admin-panel/knowledge/people/:id` — typed person form, day/month birthday with optional year,
  Markdown description, tags, symmetric/directional relationships, relationship type management,
  Date backlinks, photo, attachments, protected downloads, and unsaved-change protection.
  Relationship forms show five rows initially, while the one-line Date backlinks show ten; longer
  lists expose an explicit show-all/collapse control.
- `/admin-panel/knowledge/dates` — URL-synchronized search, AND-tag and Person filters, calendar
  sorting, pagination, related People with ten initially visible links per row, quick create, and
  delete.
- `/admin-panel/knowledge/dates/:id` — typed recurring-date form, searchable People suggestions,
  People links with ten initially visible rows, shared tag selection and management, Markdown
  description, private attachments, protected downloads, and unsaved-change protection.

Knowledge file sizes use the smallest meaningful localized unit: bytes below 1 KiB, kilobytes below
1 MiB, then megabytes, gigabytes, and terabytes.

The workspace uses explicit typed forms and feature models. It does not render a schema-driven
universal form. Protected photos are fetched as blobs and displayed through short-lived browser
object URLs; old URLs are revoked on replacement, navigation, errors, and component destruction.
The shared Markdown editor has image uploads disabled for People and Dates descriptions, because
inline images would bypass the private knowledge-file workflow. A shared locale-aware annual-date
formatter renders day/month values with or without the optional year in both workspaces.

## Operations

`make run` invokes backend initialization, which initializes both the public `media` bucket and the
private `knowledge-private` bucket. After a deployment:

1. Confirm backend readiness and that initialization completed without an S3 error.
2. In the VPN-only MinIO Console, confirm `knowledge-private` exists and has no anonymous policy
   and no bucket CORS configuration.
3. From the public side, confirm both
   `https://s3.<APP_DOMAIN>/knowledge-private` and a path below it return `404`.
4. As an owner/admin, upload and download a small photo and attachment through the People UI and an
   attachment through Dates. Confirm replacement/deletion removes obsolete objects only after the
   request commits.
5. Confirm the knowledge controllers are absent from `/api/docs/openapi.json` and private responses
   carry `no-store`.

Run `make security-infra`, `make query-plans-realistic`, and the relevant backend/frontend test
targets after changing this contour. Query-plan fixtures cover realistic and stress People and
Dates lists, details, Calendar source reads for Dates and birthdays, tags, relationships/backlinks,
calendar/name search indexes, and files.

## Backup And Restore

PostgreSQL and `knowledge-private` are one logical dataset: database rows contain object paths, so a
usable recovery point needs both the database backup and the private bucket contents. Databasus
covers PostgreSQL; the MinIO data volume or an authenticated object-storage backup must separately
cover `knowledge-private`. Backups must remain encrypted, access-controlled, non-public, and subject
to the same retention policy as the personal data.

For recovery, restore to an isolated environment first:

1. Restore PostgreSQL and the private bucket from a coordinated recovery point.
2. Run normal migrations and the bucket initializer; initialization must remove restored public
   policy/CORS state from `knowledge-private`.
3. Compare knowledge file metadata/object paths with restored objects, sample authorized photo and
   attachment reads, and record missing rows, missing objects, or orphans.
4. Re-run the public exact/prefix `404` checks before allowing traffic.
5. Record the recovery point, duration, integrity results, and deletion/cleanup exceptions.

Automated private-bucket backup/restore and recurring restore tests remain roadmap work. Until a
restore exercise passes, the existence of backups is not a recovery guarantee.
