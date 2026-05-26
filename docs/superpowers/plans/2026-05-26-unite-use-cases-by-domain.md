# Unite Use Cases By Domain Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace one-class-per-action use cases with one use-case interface and implementation per backend domain, using activity-named methods instead of `execute`.

**Architecture:** Each domain keeps `backend/src/core/<domain>/use_cases.py`, but exposes one abstract class and one concrete class for the domain. Controllers and middleware request the domain interface from Dishka and call activity methods. DI providers return one use-case object per domain, and unit mock providers expose one mock per domain.

**Tech Stack:** Python 3.14, Litestar, Dishka, SQLAlchemy async, pytest, unittest.mock.

---

### Task 1: TDD Red For New Domain Use-Case API

**Files:**
- Modify: `backend/tests/unit/test_core/auth/use_cases/test_login_use_case.py`
- Modify: `backend/tests/unit/test_core/auth/use_cases/test_authenticate_use_case.py`
- Modify: `backend/tests/unit/test_core/contacts/test_create_contact_me_purchase_use_case.py`
- Modify: `backend/tests/unit/test_core/files/test_presign_put_object_use_case.py`
- Modify: `backend/tests/unit/test_core/blog/test_get_blog_post_use_case.py`
- Modify: `backend/tests/unit/test_core/blog/test_list_blog_posts_use_case.py`
- Modify: `backend/tests/unit/test_core/competency_matrix/test_list_sheets_use_case.py`
- Modify: `backend/tests/unit/test_core/competency_matrix/test_find_resources_use_case.py`
- Modify: `backend/tests/unit/test_core/competency_matrix/test_list_items_use_case.py`
- Modify: `backend/tests/unit/test_core/competency_matrix/test_get_item_use_case.py`
- Modify: `backend/tests/unit/test_core/competency_matrix/test_upsert_item_use_case.py`
- Modify: `backend/tests/unit/test_core/competency_matrix/test_delete_item_use_case.py`
- Modify: `backend/tests/unit/test_core/competency_matrix/test_publish_switch_item_use_case.py`

- [ ] **Step 1: Change core tests to import domain use cases**

Replace concrete class imports:

```python
from core.auth.use_cases import AuthUseCase
from core.blog.use_cases import BlogUseCase
from core.competency_matrix.use_cases import CompetencyMatrixUseCase
from core.contacts.use_cases import ContactsUseCase
from core.files.use_cases import FilesUseCase
```

Instantiate the domain class once in each test setup. For auth, construct `AuthUseCase(hasher=..., token_handler=..., auth_storage=..., user_storage=...)`. For blog, contacts, and competency matrix use `storage=...`. For files, use `file_storage=...` and `file_name_generator=...`.

- [ ] **Step 2: Change core tests to call activity methods**

Rename method calls in tests:

```python
await self.use_case.login(username="test", password="password", required_role=RoleEnum.ADMIN)
await self.use_case.authenticate(token=Token(b"TOKEN"), required_role=RoleEnum.ADMIN)
await self.use_case.logout(token=Token(b"TOKEN"))
await self.use_case.create_contact_me_request(form=form)
await self.use_case.presign_put_object(params=params)
await self.use_case.get_blog_post(slug="slug")
await self.use_case.list_blog_posts(filters=filters)
await self.use_case.list_sheets()
await self.use_case.find_resources(search_name=search_name)
await self.use_case.list_items(sheet_name="Python", only_published=True)
await self.use_case.get_item(item_id=item_id, only_published=True)
await self.use_case.upsert_item(params=params)
await self.use_case.delete_item(item_id=item_id)
await self.use_case.switch_item_publish_status(
    item_id=item_id,
    publish_status=PublishStatusEnum.PUBLISHED,
)
```

- [ ] **Step 3: Run red core tests**

Run:

```bash
cd backend && make test-unit
```

Expected: FAIL with import errors for missing `AuthUseCase`, `BlogUseCase`, `ContactsUseCase`, `FilesUseCase`, and `CompetencyMatrixUseCase`, or attribute errors for missing activity methods.

### Task 2: Implement Domain Use-Case Classes

**Files:**
- Modify: `backend/src/core/auth/use_cases.py`
- Modify: `backend/src/core/blog/use_cases.py`
- Modify: `backend/src/core/contacts/use_cases.py`
- Modify: `backend/src/core/files/use_cases.py`
- Modify: `backend/src/core/competency_matrix/use_cases.py`
- Check: `backend/src/core/AGENTS.md`

- [ ] **Step 1: Replace action-specific classes with domain interfaces**

Use these public abstractions:

```python
class AbstractAuthUseCase(ABC):
    @abstractmethod
    async def login(self, username: str, password: str, required_role: RoleEnum) -> Token: ...

    @abstractmethod
    async def authenticate(self, token: Token, required_role: RoleEnum) -> User: ...

    @abstractmethod
    async def logout(self, token: Token) -> None: ...
```

```python
class AbstractBlogUseCase(ABC):
    @abstractmethod
    async def get_blog_post(self, slug: str) -> BlogPost: ...

    @abstractmethod
    async def list_blog_posts(self, filters: BlogPostFilters) -> BlogPostList: ...
```

```python
class AbstractContactsUseCase(ABC):
    @abstractmethod
    async def create_contact_me_request(self, form: ContactMe) -> None: ...
```

```python
class AbstractFilesUseCase(ABC):
    @abstractmethod
    async def presign_put_object(self, params: PresignPutObjectParams) -> PresignPutObject: ...
```

```python
class AbstractCompetencyMatrixUseCase(ABC):
    @abstractmethod
    async def list_sheets(self) -> Sheets: ...

    @abstractmethod
    async def find_resources(self, *, search_name: SearchName) -> ExternalResources: ...

    @abstractmethod
    async def list_items(self, *, sheet_name: str, only_published: bool) -> CompetencyMatrixItems: ...

    @abstractmethod
    async def get_item(self, *, item_id: IntId, only_published: bool) -> CompetencyMatrixItem: ...

    @abstractmethod
    async def upsert_item(self, *, params: CompetencyMatrixItemUpsertParams) -> CompetencyMatrixItem: ...

    @abstractmethod
    async def delete_item(self, *, item_id: IntId) -> None: ...

    @abstractmethod
    async def switch_item_publish_status(
        self,
        *,
        item_id: IntId,
        publish_status: PublishStatusEnum,
    ) -> None: ...
```

- [ ] **Step 2: Move existing logic into concrete domain classes**

Create concrete dataclasses `AuthUseCase`, `BlogUseCase`, `ContactsUseCase`, `FilesUseCase`, and `CompetencyMatrixUseCase`. Move the existing method bodies unchanged, only renaming methods from `execute` to the activity names above.

- [ ] **Step 3: Run core tests**

Run:

```bash
cd backend && make test-unit
```

Expected: core use-case tests pass further than Task 1 and remaining failures point to controllers, DI providers, or test mocks still using old abstract classes and `execute`.

### Task 3: Simplify Real DI Providers

**Files:**
- Modify: `backend/src/infra/ioc/prodivers/auth_provider.py`
- Modify: `backend/src/infra/ioc/prodivers/blog_provider.py`
- Modify: `backend/src/infra/ioc/prodivers/contacts_provider.py`
- Modify: `backend/src/infra/ioc/prodivers/files_provider.py`
- Modify: `backend/src/infra/ioc/prodivers/competency_matrix_provider.py`

- [ ] **Step 1: Provide one domain use case per provider**

Change provider imports to use only domain interfaces and classes. Example for competency matrix:

```python
from core.competency_matrix.use_cases import (
    AbstractCompetencyMatrixUseCase,
    CompetencyMatrixUseCase,
)
```

Replace multiple `provide_*_use_case` methods with one method:

```python
@provide(scope=Scope.REQUEST)
async def provide_competency_matrix_use_case(
    self,
    storage: CompetencyMatrixStorage,
) -> AbstractCompetencyMatrixUseCase:
    return CompetencyMatrixUseCase(storage=storage)
```

Apply the same pattern:

```python
provide_auth_use_case(...) -> AbstractAuthUseCase
provide_blog_use_case(storage: BlogStorage) -> AbstractBlogUseCase
provide_contacts_use_case(storage: ContactMeStorage) -> AbstractContactsUseCase
provide_files_use_case(...) -> AbstractFilesUseCase
```

- [ ] **Step 2: Run provider-related tests**

Run:

```bash
cd backend && make test-unit
```

Expected: remaining failures are imports in entrypoints and test helper/mocks.

### Task 4: Update Entrypoints To Call Activity Methods

**Files:**
- Modify: `backend/src/entrypoints/litestar/auth.py`
- Modify: `backend/src/entrypoints/litestar/api/auth/endpoints.py`
- Modify: `backend/src/entrypoints/litestar/api/contacts/endpoints.py`
- Modify: `backend/src/entrypoints/litestar/api/files/endpoints.py`
- Modify: `backend/src/entrypoints/litestar/api/competency_matrix/endpoints.py`

- [ ] **Step 1: Replace injected abstract types**

Use:

```python
from core.auth.use_cases import AbstractAuthUseCase
from core.contacts.use_cases import AbstractContactsUseCase
from core.files.use_cases import AbstractFilesUseCase
from core.competency_matrix.use_cases import AbstractCompetencyMatrixUseCase
```

Each controller method should receive the domain use case once, for example:

```python
use_case: FromDishka[AbstractCompetencyMatrixUseCase]
```

- [ ] **Step 2: Rename entrypoint calls**

Use these replacements:

```python
await use_case.login(...)
await use_case.logout(...)
await use_case.authenticate(...)
await use_case.create_contact_me_request(...)
await use_case.presign_put_object(...)
await use_case.list_sheets()
await use_case.find_resources(...)
await use_case.list_items(...)
await use_case.get_item(...)
await use_case.upsert_item(...)
await use_case.delete_item(...)
await use_case.switch_item_publish_status(...)
```

- [ ] **Step 3: Run API unit tests red/green**

Run:

```bash
cd backend && make test-unit
```

Expected: API tests now fail only where mocks/helpers still expect old per-action use-case objects or `.execute`.

### Task 5: Update Unit Mock Providers And Helpers

**Files:**
- Modify: `backend/tests/unit/mocks/providers/auth.py`
- Modify: `backend/tests/unit/mocks/providers/contacts.py`
- Modify: `backend/tests/unit/mocks/providers/files.py`
- Modify: `backend/tests/unit/mocks/providers/competency_matrix.py`
- Modify: `backend/tests/helpers/app.py`

- [ ] **Step 1: Provide one mock per domain**

Mock providers should return one mock with the new abstract spec:

```python
mock = Mock(spec=AbstractAuthUseCase)
mock.authenticate.return_value = self.user
return mock
```

For other domains:

```python
return Mock(spec=AbstractContactsUseCase)
return Mock(spec=AbstractFilesUseCase)
return Mock(spec=AbstractCompetencyMatrixUseCase)
```

- [ ] **Step 2: Simplify helper getters**

Replace per-action getters with domain getters:

```python
async def get_auth_use_case(self) -> Mock:
    use_case = await self.container.get(AbstractAuthUseCase)
    return cast("Mock", use_case)

async def get_contacts_use_case(self) -> Mock: ...
async def get_files_use_case(self) -> Mock: ...
async def get_competency_matrix_use_case(self) -> Mock: ...
```

Keep compatibility aliases only if many API tests need an intermediate green step, but remove them before completion.

- [ ] **Step 3: Run unit tests**

Run:

```bash
cd backend && make test-unit
```

Expected: failures now point to test assertions that still call `.execute`.

### Task 6: Update API Unit Tests And Assertions

**Files:**
- Modify all files under `backend/tests/unit/test_api/` that call `get_*_use_case`, assign `.execute`, or assert `.execute`.
- Modify `backend/tests/unit/test_auth/test_authentication_middleware.py`.

- [ ] **Step 1: Replace helper calls**

Use:

```python
self.use_case = await self.container.get_auth_use_case()
self.use_case = await self.container.get_contacts_use_case()
self.use_case = await self.container.get_files_use_case()
self.use_case = await self.container.get_competency_matrix_use_case()
```

- [ ] **Step 2: Replace mock method setup and assertions**

Use activity names:

```python
self.use_case.login.return_value = Token(b"TOKEN")
self.use_case.authenticate.return_value = self.user
self.use_case.create_contact_me_request.assert_called_once_with(form=...)
self.use_case.presign_put_object.assert_called_once_with(params=...)
self.use_case.list_sheets.return_value = ...
self.use_case.find_resources.assert_called_once_with(search_name=SearchName("query"))
self.use_case.list_items.assert_called_once_with(sheet_name="Python", only_published=True)
self.use_case.get_item.assert_called_once_with(item_id=IntId(1), only_published=True)
self.use_case.upsert_item.assert_called_once_with(params=...)
self.use_case.delete_item.assert_called_once_with(item_id=IntId(1))
self.use_case.switch_item_publish_status.assert_called_once_with(
    item_id=IntId(1),
    publish_status=PublishStatusEnum.PUBLISHED,
)
```

- [ ] **Step 3: Run unit tests**

Run:

```bash
cd backend && make test-unit
```

Expected: all unit tests pass.

### Task 7: Cleanup And Verification

**Files:**
- Check: `backend/src/core/use_cases.py`
- Check: `backend/src/core/AGENTS.md`
- Check: `backend/AGENTS.md`
- Check: docs for use-case naming references if any.

- [ ] **Step 1: Remove stale names**

Run:

```bash
rg -n "Abstract(Login|Logout|Authenticate|ListSheets|ListItems|GetItem|UpsertItem|DeleteItem|PublishSwitchItem|FindResources|CreateContactMeRequest|PresignPutObject|GetBlogPost|ListBlogPosts)UseCase|\\b(Login|Logout|Authenticate|ListSheets|ListItems|GetItem|UpsertItem|DeleteItem|PublishSwitchItem|FindResources|CreateContactMeRequest|PresignPutObject|GetBlogPost|ListBlogPosts)UseCase\\b|\\.execute\\(" backend/src backend/tests
```

Expected: no stale per-action use-case classes; `.execute(` remains only where it belongs outside use-case mocks/classes or not at all.

- [ ] **Step 2: Run lint/type/test verification**

Use existing make targets:

```bash
cd backend && make test-unit
cd backend && make lint
```

If `make lint` is not available or points to another target name, inspect `backend/Makefile` and use the matching existing check target.

- [ ] **Step 3: Decide documentation/infrastructure impact**

No Docker, nginx, Alembic, settings, or dependency lock changes are expected. Update docs only if a checked document references one-action use-case classes or `execute` as the required use-case API.
