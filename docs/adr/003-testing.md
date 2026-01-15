# ADR-003: Тестирование

## Статус
Принято

## Контекст
Необходимо определить стратегию тестирования для личного сайта-портфолио с Clean Architecture. Требования: демонстрация профессионального подхода к тестированию, 100% покрытие Core слоя, простота и понятность тестов, интеграция с CI/CD, поддержка различных типов тестов.

**Альтернативы:**
- TDD (Test-Driven Development) — избыточная сложность для портфолио-проекта
- BDD (Behavior-Driven Development) — требует дополнительных инструментов и обучения
- Минимальное тестирование — не демонстрирует профессиональный подход
- Только unit тесты — недостаточное покрытие интеграций

**Ключевые факторы выбора:**
- Фокус на критической бизнес-логике (Core слой)
- Простота написания и поддержки тестов
- Демонстрация навыков тестирования
- Интеграция с архитектурой проекта
- Готовность к CI/CD

## Решение
Принято решение использовать **многоуровневую стратегию тестирования** с фокусом на Core слой и простые, понятные тесты:

### Основные принципы тестирования

1. **Фокус на простых и понятных тестах** — приоритет читаемости над сложностью
2. **100% покрытие Core слоя** — все use_cases, правила домена, исключения
3. **Приоритет критической бизнес-логики** — тестирование важных бизнес-правил
4. **Fixtures** — переиспользуемые тестовые данные и настройки
5. **Изоляция тестов** — каждый тест независим и не влияет на другие
6. **Мокирование внешних зависимостей** — тестирование в изоляции от БД и внешних сервисов
7. **TDD как дополнительная практика** — тестирование может предшествовать написанию кода, но не является обязательным требованием

### Структура тестирования

**1. Core Tests (tests/core_tests/)** — тестирование бизнес-логики
- **Назначение**: Тестирование Use Cases и доменной логики
- **Принципы**: Мокирование всех зависимостей, фокус на бизнес-логике
- **Покрытие**: 100% Use Cases, все исключения, все бизнес-правила

**2. API Tests (tests/api_tests/)** — тестирование HTTP endpoints
- **Назначение**: Тестирование REST API и HTTP responses
- **Принципы**: Мокирование Use Cases, проверка HTTP статусов и JSON
- **Покрытие**: Все публичные API endpoints

**3. DB Tests (tests/db_tests/)** — тестирование работы с базой данных
- **Назначение**: Тестирование Storage реализаций и SQL запросов
- **Принципы**: Реальная БД, изоляция через транзакции
- **Покрытие**: Все Storage методы, миграции, сложные запросы

**4. Config Tests (tests/config_tests/)** — тестирование конфигурации
- **Назначение**: Тестирование property методов настроек
- **Принципы**: Тестирование вычисляемых свойств конфигурации
- **Покрытие**: Все property методы, формирование URL, настройки

**5. Auth Tests (tests/auth_tests/)** — тестирование аутентификации
- **Назначение**: Тестирование auth backends и handlers
- **Принципы**: Мокирование внешних сервисов, тестирование токенов
- **Покрытие**: Все auth компоненты, токены, права доступа

### Технологический стек

**Основные инструменты:**
- **pytest** — основной фреймворк тестирования
- **pytest-asyncio** — поддержка async/await тестов
- **unittest.mock** — мокирование зависимостей
- **TestClient** — тестирование HTTP endpoints
- **Factory Pattern** — создание тестовых данных

**Дополнительные инструменты:**
- **coverage** — измерение покрытия кода
- **pytest-cov** — интеграция coverage с pytest
- **pytest-xdist** — параллельное выполнение тестов
- **pytest-mock** — улучшенные моки

### Архитектура тестов

**1. Фикстуры и хелперы**

**Централизованные фикстуры** в `tests/conftest.py`:
```python
@pytest.fixture(scope="session")
def test_settings() -> Generator[Settings, None, None]:
    settings.database.name = "my_site_database_test"
    yield settings
    settings.database.name = "my_site_database"

@pytest_asyncio.fixture(loop_scope="session")
async def container(
    test_settings: Settings,
    global_random_uuid: uuid.UUID,
) -> AsyncGenerator[AsyncContainer, None]:
    container = make_async_container(
        MockGeneralProvider(uuid_=global_random_uuid),
        MockCompetencyMatrixProvider(),
        MockContactsProvider(),
        MockAuthProvider(settings=test_settings),
    )
    yield container
    await container.close()
```

**Базовые фикстуры** в `tests/fixtures.py`:
```python
class FactoryFixture:
    factory: FactoryHelper

    @pytest.fixture(autouse=True)
    def _setup_factory(self) -> None:
        self.factory = FactoryHelper()

class ContainerFixture:
    container: IocContainerHelper

    @pytest.fixture(autouse=True)
    def _setup_app(self, container: AsyncContainer) -> None:
        self.container = IocContainerHelper(container=container)

class ApiFixture:
    api: APIHelper

    @pytest.fixture(autouse=True)
    def _setup_api(self, client: TestClient) -> None:
        self.api = APIHelper(client=client)

class StorageFixture:
    db_session: AsyncSession
    storage_helper: StorageHelper

    @pytest_asyncio.fixture(autouse=True)
    async def _setup_storage(self, session: AsyncSession):
        self.db_session = session
        self.storage_helper = StorageHelper(session=session)
        yield
        await self.db_session.rollback()
```

**2. Factory Pattern для тестовых данных**

**Core Factory** в `tests/helpers/factories/core.py`:
```python
class CoreFactoryHelper:
    @classmethod
    def entity(
        cls,
        entity_id: uuid.UUID | None = None,
        name: str = "Test Entity",
        description: str = "This is a test entity description.",
        slug: str = "test-entity",
        status: StatusEnum = StatusEnum.ACTIVE,
        published_at: str | None = None,
        created_at: str | None = None,
        updated_at: str | None = None,
    ) -> Entity:
        now = datetime.now(tz=UTC)
        return Entity(
            id=entity_id or uuid.uuid4(),
            name=name,
            description=description,
            slug=slug,
            status=status,
            published_at=(
                datetime.fromisoformat(published_at).replace(tzinfo=UTC)
                if published_at is not None
                else None
            ),
            created_at=(
                datetime.fromisoformat(created_at).replace(tzinfo=UTC)
                if created_at is not None
                else now
            ),
            updated_at=(
                datetime.fromisoformat(updated_at).replace(tzinfo=UTC)
                if updated_at is not None
                else now
            ),
        )

    @classmethod
    def item(
        cls,
        item_id: int,
        title: str = "Test Item",
        status: StatusEnum = StatusEnum.ACTIVE,
        content: str = "Content",
        expected_value: str = "Expected Value",
        category: str = "Category",
        level: str = "Basic",
        section: str = "Section",
        subsection: str = "Subsection",
        resources: list[Resource] | None = None,
    ) -> Item:
        return Item(
            id=item_id,
            title=title,
            status=status,
            content=content,
            expected_value=expected_value,
            category=category,
            level=level,
            section=section,
            subsection=subsection,
            resources=Resources(values=resources or []),
        )
```

**3. Mock Providers для DI**

**Mock провайдеры** в `tests/mocks/providers/`:
```python
# tests/mocks/providers/general.py
class MockGeneralProvider(Provider):
    def __init__(self, uuid_: uuid.UUID | None = None):
        super().__init__()
        self.uuid_ = uuid_ or uuid.uuid4()

    @provide(scope=Scope.APP)
    async def provide_random_uuid(self) -> uuid.UUID:
        return self.uuid_

# tests/mocks/providers/domain.py
class MockDomainProvider(Provider):
    @provide(scope=Scope.APP)
    async def provide_get_entity_use_case(self) -> Mock:
        return Mock(spec=AbstractGetEntityUseCase)

    @provide(scope=Scope.APP)
    async def provide_list_entities_use_case(self) -> Mock:
        return Mock(spec=AbstractListEntitiesUseCase)
```

### Стили тестов

**1. Core Tests — Unit тесты с моками**

**Принципы:**
- Мокирование всех зависимостей (Storage, Logger, внешние сервисы)
- Фокус на бизнес-логике Use Cases
- Тестирование всех путей выполнения (happy path, error cases)
- Проверка взаимодействия с зависимостями

**Пример Core теста:**
```python
# tests/core_tests/domain/test_get_entity_use_case.py
class TestGetEntityUseCase(FactoryFixture):
    @pytest.fixture(autouse=True)
    def setup(self) -> None:
        self.storage = Mock(spec=EntityStorage)
        self.use_case = GetEntityUseCase(storage=self.storage)

    async def test_get_entity(self) -> None:
        slug = "test-entity"
        expected_entity = self.factory.core.entity(slug=slug)
        self.storage.get_entity_by_slug.return_value = expected_entity

        result = await self.use_case.execute(slug=slug)

        assert result == expected_entity
        self.storage.get_entity_by_slug.assert_called_once_with(slug=slug)

    async def test_get_entity_not_found_by_not_available(self) -> None:
        slug = "test-entity"
        expected_entity = self.factory.core.entity(
            slug=slug, status=StatusEnum.DRAFT
        )
        self.storage.get_entity_by_slug.return_value = expected_entity

        with pytest.raises(EntityNotFoundError):
            await self.use_case.execute(slug=slug)

    async def test_get_entity_not_found_by_not_found(self) -> None:
        self.storage.get_entity_by_slug.side_effect = EntityNotFoundError

        with pytest.raises(EntityNotFoundError):
            await self.use_case.execute(slug="some-slug")
```

**2. API Tests — HTTP endpoint тесты**

**Принципы:**
- Мокирование Use Cases через DI контейнер
- Проверка HTTP статусов и JSON responses
- Тестирование error handling и валидации
- Проверка правильности вызовов Use Cases

**Пример API теста:**
```python
# tests/api_tests/domain/test_get_entity.py
class TestGetEntityAPI(ContainerFixture, ApiFixture, FactoryFixture):
    @pytest_asyncio.fixture(autouse=True)
    async def setup(self) -> None:
        self.use_case = await self.container.get_mock_get_entity_use_case()

    def test_not_found(self) -> None:
        self.use_case.execute.side_effect = EntityNotFoundError()
        response = self.api.get_entity(entity_id=-100)
        self.use_case.execute.assert_called_once_with(entity_id=-100)
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json() == {
            "code": "client_error",
            "type": "not_found",
            "message": "Entity not found",
            "attr": None,
            "location": None,
        }

    def test_found(self) -> None:
        self.use_case.execute.return_value = self.factory.core.entity(
            entity_id=1,
            name="Test Entity",
            status=StatusEnum.ACTIVE,
            description="Test description",
            slug="test-entity",
            category="Category",
            level="Basic",
            section="Section",
            subsection="Subsection",
            resources=[
                self.factory.core.resource(
                    resource_id=1,
                    name="resource",
                    url="http://example.com",
                    context="resource context",
                ),
            ],
        )
        response = self.api.get_entity(entity_id=1)
        self.use_case.execute.assert_called_once_with(entity_id=1)
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {
            "id": 1,
            "name": "Test Entity",
            "description": "Test description",
            "slug": "test-entity",
            "category": "Category",
            "level": "Basic",
            "section": "Section",
            "subsection": "Subsection",
            "resources": [
                {
                    "id": 1,
                    "name": "resource",
                    "url": "http://example.com",
                    "context": "resource context",
                }
            ],
        }
```

**3. DB Tests — Интеграционные тесты с БД**

**Принципы:**
- Реальная база данных для тестирования
- Изоляция через транзакции и rollback
- Тестирование SQL запросов и миграций
- Проверка преобразования моделей в доменные объекты

**Пример DB теста:**
```python
# tests/db_tests/test_entity_storage.py
class TestEntityDatabaseStorage(StorageFixture, FactoryFixture):
    @pytest_asyncio.fixture(autouse=True)
    async def setup(self) -> None:
        self.storage = EntityDatabaseStorage(session=self.db_session)

    async def test_get_entity_by_slug_success(self) -> None:
        await self.storage_helper.create_entity(
            entity=self.factory.core.entity(
                name="Test Entity",
                description="Test content",
                slug="test-entity",
                status=StatusEnum.ACTIVE,
                published_at="2024-01-01T00:00:00",
                created_at="2024-01-01T00:00:00",
                updated_at="2024-01-01T00:00:00",
            ),
        )

        result = await self.storage.get_entity_by_slug(slug="test-entity")

        assert result.name == "Test Entity"
        assert result.slug == "test-entity"
        assert result.status == StatusEnum.ACTIVE

    async def test_get_entity_by_slug_not_found(self) -> None:
        storage = EntityDatabaseStorage(session=self.storage_helper.session)

        with pytest.raises(EntityNotFoundError):
            await storage.get_entity_by_slug(slug="non-existent")

    async def test_list_entities_only_available(self) -> None:
        filters = EntityFilters(page=1, page_size=10, only_available=True)
        await self.storage_helper.create_entities(
            entities=[
                self.factory.core.entity(status=StatusEnum.ACTIVE, slug=str(i))
                for i in range(5)
            ]
        )
        await self.storage_helper.create_entities(
            entities=[
                self.factory.core.entity(status=StatusEnum.DRAFT, slug=str(i + 5))
                for i in range(15)
            ]
        )
        result = await self.storage.list_entities(filters=filters)
        assert len(result.entities) == 5
        assert result.total_count == 5
        assert result.total_pages == 1
```

**4. Config Tests — Тестирование конфигурации**

**Принципы:**
- Тестирование property методов настроек
- Проверка вычисляемых свойств конфигурации
- Тестирование формирования URL и ссылок
- Проверка корректности property методов

**Пример Config теста:**
```python
# tests/config_tests/test_settings.py
class TestSettings:
    @pytest.fixture(autouse=True)
    def setup(self, test_settings: Settings) -> None:
        self.settings = test_settings
        self.settings.app.domain = "example.com"

    def test_base_url(self) -> None:
        assert self.settings.base_url == "https://example.com"

    def test_get_minio_object_url(self) -> None:
        assert (
            self.settings.get_minio_object_url(bucket="media", object_path="test.txt")
            == "https://example.com/media/test.txt"
        )

    def test_get_minio_object_url_object_path_startswith_slash(self) -> None:
        assert (
            self.settings.get_minio_object_url(bucket="media", object_path="/test.txt")
            == "https://example.com/media/test.txt"
        )
```

### Принципы написания тестов

**1. Структура тестового класса**

**Использование фикстур:**
```python
class TestUseCase(FactoryFixture, ContainerFixture):
    @pytest.fixture(autouse=True)
    def setup(self) -> None:
        self.storage = Mock(spec=StorageInterface)
        self.use_case = UseCase(storage=self.storage)
```

**2. Именование тестов**

**Паттерн именования:**
- `test_<method>_<scenario>_<expected_result>`
- `test_get_entity_success`
- `test_get_entity_not_found`
- `test_create_entity_invalid_data`

**3. Arrange-Act-Assert паттерн**

**Структура теста:**
```python
async def test_get_entity_success(self) -> None:
    # Arrange - подготовка данных
    slug = "test-entity"
    expected_entity = self.factory.core.entity(slug=slug)
    self.storage.get_entity_by_slug.return_value = expected_entity

    # Act - выполнение действия
    result = await self.use_case.execute(slug=slug)

    # Assert - проверка результата
    assert result == expected_entity
    self.storage.get_entity_by_slug.assert_called_once_with(slug=slug)
```

**4. Тестирование исключений**

**Проверка исключений:**
```python
async def test_get_entity_not_found(self) -> None:
    self.storage.get_entity_by_slug.side_effect = EntityNotFoundError

    with pytest.raises(EntityNotFoundError):
        await self.use_case.execute(slug="some-slug")
```

**5. Параметризованные тесты**

**Тестирование множественных сценариев:**
```python
@pytest.mark.parametrize(
    "status,expected_count",
    [
        (StatusEnum.ACTIVE, 5),
        (StatusEnum.DRAFT, 10),
        (StatusEnum.ARCHIVED, 3),
    ],
)
async def test_list_entities_by_status(self, status, expected_count) -> None:
    # Тест для разных статусов сущностей
    pass
```

### Покрытие кода

**Цели покрытия:**
- **Core слой**: 100% покрытие (use_cases, schemas, exceptions)
- **API слой**: 95% покрытие (все endpoints, error handling)
- **DB слой**: 95% покрытие (storage методы, миграции)
- **Config слой**: 95% покрытие (все настройки, валидация)

**Измерение покрытия:**
```bash
# Запуск тестов с измерением покрытия
pytest --cov=src --cov-report=html --cov-report=term

# Генерация отчета в HTML
pytest --cov=src --cov-report=html
```

**Исключения из покрытия:**
- `__init__.py` файлы
- `main.py` (точка входа)
- Миграции Alembic
- Тестовые файлы

**Проверки качества:**
- Все тесты должны проходить
- Покрытие Core слоя должно быть 100%
- Линтеры должны проходить без ошибок
- Типизация должна быть корректной

### Тестирование с DI контейнером

**Mock провайдеры:**
```python
# tests/mocks/providers/domain_provider.py
class MockDomainProvider(Provider):
    @provide(scope=Scope.APP)
    async def provide_use_case(self) -> Mock:
        return Mock(spec=AbstractUseCase)

    @provide(scope=Scope.APP)
    async def provide_storage(self) -> Mock:
        return Mock(spec=AbstractStorage)
```

**Использование в тестах:**
```python
class TestUseCase(ContainerFixture, FactoryFixture):
    async def test_use_case_execution(self) -> None:
        use_case = await self.container.get_mock_use_case()
        use_case.execute.return_value = expected_result

        result = await use_case.execute(test_data)

        assert result == expected_result
        use_case.execute.assert_called_once_with(test_data)
```

### Тестирование асинхронного кода

**Async фикстуры:**
```python
@pytest_asyncio.fixture
async def async_setup() -> None:
    # Асинхронная настройка
    await setup_database()
    yield
    await cleanup_database()
```

**Async тесты:**
```python
async def test_async_operation(self) -> None:
    result = await self.async_service.perform_operation()
    assert result is not None
```


## Последствия

### Положительные

**1. Качество кода**
- Высокое покрытие критической бизнес-логики
- Раннее обнаружение ошибок
- Уверенность в изменениях кода
- Документирование поведения через тесты

**2. Демонстрация навыков**
- Показывает профессиональный подход к тестированию
- Демонстрирует понимание различных типов тестов
- Готовность к работе в команде
- Понимание принципов Clean Architecture

**3. Поддержка и развитие**
- Легкость рефакторинга с уверенностью
- Простота добавления новой функциональности
- Быстрое обнаружение регрессий
- Документация поведения системы

**4. CI/CD готовность**
- Автоматическая проверка качества
- Быстрая обратная связь при изменениях
- Интеграция с системами мониторинга
- Готовность к production развертыванию

### Отрицательные

**1. Время разработки**
- Дополнительное время на написание тестов
- Необходимость поддержки тестов при изменениях
- Кривая обучения для новых разработчиков
- Сложность настройки тестового окружения

**2. Сложность поддержки**
- Необходимость обновления тестов при изменениях API
- Сложность отладки падающих тестов
- Overhead от mock объектов
- Необходимость понимания архитектуры для написания тестов

**3. Производительность**
- Время выполнения тестов
- Использование ресурсов для тестирования
- Сложность настройки тестовой БД
- Overhead от покрытия кода

## Альтернативы

### Рассмотренные варианты

#### 1. TDD (Test-Driven Development)
**Принято как дополнительная практика**:
- Может использоваться для сложной бизнес-логики
- Не является обязательным требованием
- Применяется по необходимости
- Дополняет основную стратегию тестирования

#### 2. BDD (Behavior-Driven Development)
**Проблемы**:
- Требует дополнительных инструментов (Gherkin, Cucumber)
- Сложность для простых проектов
- Overhead от написания feature файлов
- Необходимость обучения команды

#### 3. Минимальное тестирование
**Проблемы**:
- Не демонстрирует профессиональный подход
- Высокий риск ошибок в production
- Сложность рефакторинга
- Отсутствие документации поведения

#### 4. Только unit тесты
**Проблемы**:
- Недостаточное покрытие интеграций
- Отсутствие тестирования API
- Сложность тестирования работы с БД
- Неполная картина качества системы

### Обоснование выбора

#### Почему многоуровневое тестирование?

**1. Баланс качества и сложности**
- Достаточное покрытие для демонстрации навыков
- Не избыточная сложность для личного проекта
- Фокус на критически важных компонентах
- Простота понимания и поддержки

**2. Соответствие архитектуре**
- Тесты следуют структуре Clean Architecture
- Разделение по слоям (Core, API, DB, Config)
- Использование DI контейнера для тестирования
- Соответствие принципам проекта

**3. Готовность к развитию**
- Легкость добавления новых типов тестов
- Масштабируемость при росте проекта
- Готовность к работе в команде
- Интеграция с современными инструментами

#### Почему именно такие принципы?

**1. Фокус на Core слое**
- Бизнес-логика — самая критичная часть
- 100% покрытие обеспечивает надежность
- Легкость тестирования в изоляции
- Демонстрация понимания Clean Architecture

**2. Factory Pattern**
- Переиспользование тестовых данных
- Читаемость и поддерживаемость
- Консистентность тестовых данных
- Легкость создания сложных объектов

**3. Mock провайдеры**
- Изоляция тестов от внешних зависимостей
- Быстрое выполнение тестов
- Предсказуемость результатов
- Соответствие принципам DI

**4. Простые и понятные тесты**
- Легкость понимания и поддержки
- Быстрая обратная связь при ошибках
- Документирование поведения системы
- Готовность к работе в команде

**5. Гибкость в подходах**
- TDD применяется по необходимости
- Основной фокус на качестве тестов
- Адаптация под конкретные задачи
- Баланс между скоростью и качеством

## Реализация

### Структура тестов

```
tests/
├── conftest.py                 # Глобальные фикстуры
├── fixtures.py                 # Базовые фикстуры
├── core_tests/                 # Тесты бизнес-логики
│   ├── domain_a/               # Тесты домена domain_a
│   ├── domain_b/               # Тесты домена domain_b
│   └── domain_c/               # Тесты домена domain_c
├── api_tests/                  # Тесты HTTP endpoints
│   ├── domain_a/               # API тесты domain_a
│   ├── domain_b/               # API тесты domain_b
│   └── test_healthcheck.py     # Тесты healthcheck
├── db_tests/                   # Тесты работы с БД
│   ├── test_auth_storage.py    # Тесты auth storage
│   ├── test_domain_a_storage.py    # Тесты domain_a storage
│   ├── test_domain_b_storage.py
│   └── test_domain_c_storage.py
├── config_tests/               # Тесты конфигурации
│   └── test_settings.py
├── auth_tests/                 # Тесты аутентификации
│   ├── test_backends.py
│   └── test_handlers.py
├── helpers/                    # Вспомогательные классы
│   ├── api.py                  # API хелперы
│   ├── app.py                  # App хелперы
│   ├── factory.py              # Factory хелперы
│   ├── storage.py              # Storage хелперы
│   └── factories/              # Factory классы
│       ├── api.py
│       └── core.py
└── mocks/                      # Mock провайдеры
    └── providers/
        ├── auth.py
        ├── domain_a.py
        ├── domain_b.py
        └── general.py
```

### Конфигурация pytest

**pyproject.toml:**
```toml
[tool.pytest]
testpath = "tests"

[tool.pytest.ini_options]
asyncio_mode = "auto"
asyncio_default_fixture_loop_scope = "function"
```

### Запуск тестов

**Основные команды:**
```bash
# Запуск всех тестов
make tests

# Запуск тестов с покрытием
make tests-coverage
```

### Интеграция с Makefile

**Команды в Makefile:**
```makefile
.PHONY: tests tests-coverage

tests: ## Run all tests
	@if [ -z $(UV) ]; then echo "UV could not be found."; exit 2; fi
	PYTHONPATH=src APP_CACHE_CACHE=false $(UV) run pytest -vvv -x $(TESTS)

tests-coverage: ## Run tests with coverage
	@if [ -z $(UV) ]; then echo "UV could not be found."; exit 2; fi
	PYTHONPATH=src APP_CACHE_CACHE=false APP_USE_RATE_LIMIT=false $(UV) run coverage run -m pytest -vvv
	PYTHONPATH=src APP_CACHE_CACHE=false APP_USE_RATE_LIMIT=false $(UV) run coverage xml
	PYTHONPATH=src APP_CACHE_CACHE=false APP_USE_RATE_LIMIT=false $(UV) run coverage report --fail-under=95
```

### Примеры тестов

#### 1. Core Test — Use Case с моками

```python
# tests/core_tests/domain/test_get_entity_use_case.py
from unittest.mock import Mock
import pytest
from core.domain.exceptions import EntityNotFoundError
from core.domain.storages import EntityStorage
from core.domain.use_cases import GetEntityUseCase
from core.enums import StatusEnum
from tests.fixtures import FactoryFixture

class TestGetEntityUseCase(FactoryFixture):
    @pytest.fixture(autouse=True)
    def setup(self) -> None:
        self.storage = Mock(spec=EntityStorage)
        self.use_case = GetEntityUseCase(storage=self.storage)

    async def test_not_available(self) -> None:
        # Arrange
        entity = self.factory.core.entity(
            entity_id=2,
            name="Test Entity",
            status=StatusEnum.DRAFT,
            category="Category",
            level="",
            section="",
            subsection="",
        )
        self.storage.get_entity.return_value = entity

        # Act & Assert
        with pytest.raises(EntityNotFoundError):
            await self.use_case.execute(entity_id=2)

    async def test_available(self) -> None:
        # Arrange
        entity = self.factory.core.entity(
            entity_id=1,
            name="Test Entity",
            status=StatusEnum.ACTIVE,
            category="Category",
            level="Basic",
            section="Section",
            subsection="Subsection",
        )
        self.storage.get_entity.return_value = entity

        # Act
        result = await self.use_case.execute(entity_id=1)

        # Assert
        assert entity == result
```

#### 2. API Test — HTTP endpoint с моками

```python
# tests/api_tests/domain/test_get_entity.py
import pytest_asyncio
from verbose_http_exceptions import status
from core.domain.exceptions import EntityNotFoundError
from core.enums import StatusEnum
from tests.fixtures import ApiFixture, FactoryFixture, ContainerFixture


class TestGetEntityAPI(ContainerFixture, ApiFixture, FactoryFixture):
    @pytest_asyncio.fixture(autouse=True)
    async def setup(self) -> None:
        self.use_case = await self.container.get_mock_get_entity_use_case()

    def test_not_found(self) -> None:
        # Arrange
        self.use_case.execute.side_effect = EntityNotFoundError()

        # Act
        response = self.api.get_entity(entity_id=-100)

        # Assert
        self.use_case.execute.assert_called_once_with(entity_id=-100)
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json() == {
            "code": "client_error",
            "type": "not_found",
            "message": "Entity not found",
            "attr": None,
            "location": None,
        }

    def test_found(self) -> None:
        # Arrange
        self.use_case.execute.return_value = self.factory.core.entity(
            entity_id=1,
            name="Test Entity",
            status=StatusEnum.ACTIVE,
            description="Test description",
            slug="test-entity",
            category="Category",
            level="Basic",
            section="Section",
            subsection="Subsection",
            resources=[
                self.factory.core.resource(
                    resource_id=1,
                    name="resource",
                    url="http://example.com",
                    context="resource context",
                ),
            ],
        )

        # Act
        response = self.api.get_entity(entity_id=1)

        # Assert
        self.use_case.execute.assert_called_once_with(entity_id=1)
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {
            "id": 1,
            "name": "Test Entity",
            "description": "Test description",
            "slug": "test-entity",
            "category": "Category",
            "level": "Basic",
            "section": "Section",
            "subsection": "Subsection",
            "resources": [
                {
                    "id": 1,
                    "name": "resource",
                    "url": "http://example.com",
                    "context": "resource context",
                }
            ],
        }
```

#### 3. DB Test — Интеграционный тест с БД

```python
# tests/db_tests/test_entity_storage.py
import uuid
from datetime import datetime
from zoneinfo import ZoneInfo
import pytest
import pytest_asyncio
from core.domain.exceptions import EntityNotFoundError
from core.domain.schemas import EntityFilters
from core.enums import StatusEnum
from db.storages.entity import EntityDatabaseStorage
from tests.fixtures import StorageFixture, FactoryFixture

class TestEntityDatabaseStorage(StorageFixture, FactoryFixture):
    @pytest_asyncio.fixture(autouse=True)
    async def setup(self) -> None:
        self.storage = EntityDatabaseStorage(session=self.db_session)

    async def test_get_entity_by_slug_success(self) -> None:
        # Arrange
        await self.storage_helper.create_entity(
            entity=self.factory.core.entity(
                name="Test Entity",
                description="Test content",
                slug="test-entity",
                status=StatusEnum.ACTIVE,
                published_at="2024-01-01T00:00:00",
                created_at="2024-01-01T00:00:00",
                updated_at="2024-01-01T00:00:00",
            ),
        )

        # Act
        result = await self.storage.get_entity_by_slug(slug="test-entity")

        # Assert
        assert result.name == "Test Entity"
        assert result.slug == "test-entity"
        assert result.status == StatusEnum.ACTIVE

    async def test_get_entity_by_slug_not_found(self) -> None:
        # Arrange
        storage = EntityDatabaseStorage(session=self.storage_helper.session)

        # Act & Assert
        with pytest.raises(EntityNotFoundError):
            await storage.get_entity_by_slug(slug="non-existent")

    async def test_list_entities_only_available(self) -> None:
        # Arrange
        filters = EntityFilters(page=1, page_size=10, only_available=True)
        await self.storage_helper.create_entities(
            entities=[
                self.factory.core.entity(
                    status=StatusEnum.ACTIVE, 
                    slug=str(i)
                )
                for i in range(5)
            ]
        )
        await self.storage_helper.create_entities(
            entities=[
                self.factory.core.entity(
                    status=StatusEnum.DRAFT, 
                    slug=str(i + 5)
                )
                for i in range(15)
            ]
        )

        # Act
        result = await self.storage.list_entities(filters=filters)

        # Assert
        assert len(result.entities) == 5
        assert result.total_count == 5
        assert result.total_pages == 1
```

#### 4. Config Test — Тестирование настроек

```python
# tests/config_tests/test_settings.py
import pytest
from config.settings import Settings

class TestSettings:
    @pytest.fixture(autouse=True)
    def setup(self, test_settings: Settings) -> None:
        self.settings = test_settings
        self.settings.app.domain = "example.com"

    def test_base_url(self) -> None:
        assert self.settings.base_url == "https://example.com"

    def test_get_minio_object_url(self) -> None:
        assert (
            self.settings.get_minio_object_url(bucket="media", object_path="test.txt")
            == "https://example.com/media/test.txt"
        )

    def test_get_minio_object_url_object_path_startswith_slash(self) -> None:
        assert (
            self.settings.get_minio_object_url(bucket="media", object_path="/test.txt")
            == "https://example.com/media/test.txt"
        )
```


## Заключение

Выбранная стратегия тестирования обеспечивает:

1. **Качество кода** — высокое покрытие критической бизнес-логики
2. **Демонстрацию навыков** — профессиональный подход к тестированию
3. **Готовность к развитию** — легкость добавления новых тестов
4. **CI/CD готовность** — автоматическая проверка качества
5. **Поддерживаемость** — простые и понятные тесты

Стратегия идеально подходит для портфолио-проекта, демонстрируя понимание современных принципов тестирования и готовность к работе в команде.
