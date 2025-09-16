# ADR-001: Логирование

## Статус
Принято

## Контекст
Необходимо выбрать систему логирования для веб-приложения на Litestar. Требования: структурированные логи для мониторинга, трейсинг запросов, интеграция с Sentry, разные форматы для dev/prod.

**Альтернативы:**
- Python logging — неструктурированный вывод, сложность настройки JSON
- Loguru — простота использования, но ограниченная гибкость конфигурации  
- Python logging + JSON formatter — требует ручной реализации многих функций

**Ключевые факторы выбора:**
- Структурированность логов для анализа
- Встроенная поддержка контекстных переменных
- Готовность к интеграции с системами мониторинга
- Гибкость конфигурации для разных окружений

## Решение
Принято решение использовать **структурированное логирование** на основе следующих технологий:

### Основные компоненты
1. **Structlog** — основной инструмент для структурированного логирования
2. **ECS Logging** — формат логов Elastic Common Schema для production
3. **Sentry** — мониторинг ошибок и исключений
4. **Request ID** — трейсинг запросов через middleware

### Конфигурация логирования

**Централизованная конфигурация** происходит в файле `src/config/loggers.py`. Все настройки логирования собраны в одном месте для упрощения управления и поддержки.

**Режимы логирования** определяются переменной окружения `APP_DEBUG`:
- `APP_DEBUG=true` — режим разработки
- `APP_DEBUG=false` — production режим

#### Debug режим (разработка)
- Цветной консольный вывод через `structlog.dev.ConsoleRenderer()`
- Временные метки в формате `%Y-%m-%d %H:%M:%S`
- Уровень логирования: `DEBUG`
- Отключен Sentry для избежания спама во время разработки
- Удобочитаемый формат для разработчика

#### Production режим
- ECS формат через `ecs_logging.StructlogFormatter()`
- Уровень логирования: `INFO`
- Включен Sentry для мониторинга ошибок
- JSON-формат для интеграции с ELK Stack
- Структурированные логи для автоматической обработки

### Структура процессоров

Базовые процессоры (общие для всех режимов):
```python
processors: list[Processor] = [
    structlog.contextvars.merge_contextvars,  # Контекстные переменные
    structlog.processors.add_log_level,       # Уровень логирования
    structlog.processors.UnicodeDecoder(),    # Декодирование Unicode
    structlog.dev.set_exc_info,              # Информация об исключениях
    structlog.processors.StackInfoRenderer(), # Информация о стеке
]
```

Дополнительные процессоры для debug режима:
```python
if settings.app.debug:
    processors += [
        structlog.processors.TimeStamper(fmt="%Y-%m-%d %H:%M:%S", utc=False),
        structlog.dev.ConsoleRenderer(),
    ]
    wrapper_class = structlog.make_filtering_bound_logger(logging.DEBUG)
```

Дополнительные процессоры для production режима:
```python
else:
    processors += [
        ecs_logging.StructlogFormatter(),  # ECS формат
    ]
    wrapper_class = structlog.make_filtering_bound_logger(logging.INFO)
```

### Инициализация Sentry

Sentry инициализируется в файле `src/config/initializers.py` и вызывается при старте приложения:

```python
def init_sentry() -> None:
    if settings.app.debug:
        # Отключен в debug режиме для избежания спама
        return
    
    sentry_sdk.init(
        dsn=settings.sentry.dsn,
        send_default_pii=True,  # Отправка персональных данных для диагностики
        integrations=[LitestarIntegration()],  # Интеграция с Litestar
    )
```

**Место вызова**: Sentry инициализируется в `src/main.py` при создании приложения:
```python
def create_app() -> Litestar:
    init_sentry()  # Инициализация Sentry
    # ... остальная конфигурация
```

**Настройки Sentry**:
- DSN берется из переменной окружения `SENTRY_DSN`
- Включена отправка PII данных для лучшей диагностики
- Интеграция с Litestar для автоматического отслеживания ошибок
- Отключен в debug режиме для избежания спама во время разработки

### Request ID Middleware

Реализован `RequestIdLoggingMiddleware` для трейсинга запросов:

```python
class RequestIdLoggingMiddleware(ASGIMiddleware):
    async def handle(self, scope: Scope, receive: Receive, send: Send, next_app: ASGIApp) -> None:
        structlog.contextvars.unbind_contextvars("request_id")
        structlog.contextvars.bind_contextvars(request_id=uuid.uuid4().__str__())
        await next_app(scope, receive, send)
```

**Функциональность**:
- Генерирует уникальный UUID для каждого запроса
- Привязывает `request_id` к контексту через `structlog.contextvars`
- Очищает контекст после обработки запроса
- Автоматически добавляется ко всем логам в рамках запроса

### Интеграция с Litestar

Используется `StructlogPlugin` для автоматического логирования HTTP запросов:

```python
StructlogPlugin(
    config=StructlogConfig(
        structlog_logging_config=StructLoggingConfig(
            processors=loggers.processors,
            wrapper_class=loggers.wrapper_class,
            logger_factory=loggers.logger_factory,
            cache_logger_on_first_use=loggers.cache_logger_on_first_use,
        ),
        middleware_logging_config=LoggingMiddlewareConfig(
            request_log_fields=["path", "method", "query", "path_params"],
            response_log_fields=["status_code"],
        ),
    ),
)
```

**Настройки логирования**:
- Поля запросов: `path`, `method`, `query`, `path_params`
- Поля ответов: `status_code`
- Автоматическое логирование всех HTTP запросов
- Интеграция с middleware для Request ID

## Последствия

### Положительные
- **Структурированность**: JSON-формат логов упрощает парсинг и анализ
- **Контекстность**: Request ID позволяет трейсить запросы через всю систему
- **Гибкость**: Разные форматы для dev/prod окружений
- **Интеграция**: ECS формат совместим с Elasticsearch/Kibana
- **Мониторинг**: Sentry обеспечивает отслеживание ошибок
- **Производительность**: Асинхронное логирование не блокирует основной поток

### Отрицательные
- **Сложность настройки**: Требует понимания структуры процессоров и их взаимодействия
- **Зависимости**: Дополнительные пакеты (structlog, ecs-logging, sentry-sdk)
- **Кривая обучения**: Необходимо изучить принципы структурированного логирования
- **Overhead**: Больше кода для простых случаев логирования по сравнению с print()

## Альтернативы

### Рассмотренные варианты

#### 1. Стандартное Python logging
**Проблемы**:
- Отсутствие структурированности по умолчанию
- Сложность настройки JSON-формата
- Нет встроенной поддержки контекстных переменных
- Ограниченные возможности для обработки логов

**Пример проблематичного кода**:
```python
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Неструктурированный вывод
logger.error(f"Database error: {exc}, user: {user_id}")
# Результат: "Database error: Connection timeout, user: 123"
```

#### 2. Loguru
**Преимущества**:
- Простота использования
- Красивый вывод по умолчанию
- Встроенная ротация логов

**Недостатки**:
- Меньшая гибкость конфигурации
- Ограниченная поддержка структурированного логирования
- Сложность интеграции с ECS форматом
- Меньше возможностей для кастомизации процессоров

#### 3. Python logging + JSON formatter
**Проблемы**:
- Требует дополнительных зависимостей
- Сложность настройки структурированного вывода
- Нет встроенной поддержки контекстных переменных
- Необходимость ручной реализации многих функций

### Обоснование выбора Structlog

#### Почему структурированное логирование?
1. **Анализируемость**: JSON-формат легко парсится системами мониторинга
2. **Поиск**: Упрощенный поиск по конкретным полям
3. **Агрегация**: Группировка логов по типам событий
4. **Мониторинг**: Автоматическое создание алертов и дашбордов

#### Почему именно Structlog?

**1. Мощная система процессоров**
```python
# Легко добавлять новые процессоры
processors = [
    structlog.contextvars.merge_contextvars,  # Контекст
    structlog.processors.add_log_level,       # Уровень
    structlog.processors.TimeStamper(),       # Время
    ecs_logging.StructlogFormatter(),         # ECS формат
]
```

**2. Встроенная поддержка контекстных переменных**
```python
# Автоматическое добавление контекста ко всем логам
structlog.contextvars.bind_contextvars(request_id="123", user_id="456")
logger.info("Processing request")  # Автоматически включает request_id и user_id
```

**3. Гибкость конфигурации**
- Разные форматы для разных окружений
- Легкое переключение между debug и production
- Возможность добавления custom процессоров

**4. Отличная интеграция с современными фреймворками**
- Встроенная поддержка Litestar
- Автоматическое логирование HTTP запросов
- Интеграция с Sentry

**5. ECS формат из коробки**
- Совместимость с Elasticsearch/Kibana
- Стандартизированные поля логов
- Готовность к enterprise-мониторингу

#### Сравнение подходов

| Критерий | Python logging | Loguru | Structlog |
|----------|----------------|--------|-----------|
| Простота использования | ⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ |
| Структурированность | ⭐ | ⭐⭐ | ⭐⭐⭐⭐⭐ |
| Гибкость конфигурации | ⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| Контекстные переменные | ❌ | ⭐⭐ | ⭐⭐⭐⭐⭐ |
| ECS поддержка | ❌ | ⭐ | ⭐⭐⭐⭐⭐ |
| Интеграция с фреймворками | ⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |

#### Результат выбора
Structlog обеспечивает оптимальный баланс между простотой использования и мощностью функционала, что критично для личного проекта, который должен демонстрировать профессиональный подход к разработке и готовность к production-развертыванию. Это особенно важно для портфолио-проекта, где качество кода и архитектурные решения имеют первостепенное значение.

## Реализация

### Импорт логгера
```python
from config.loggers import logger
```

### Примеры использования

#### Простое логирование
```python
logger.info("User created successfully")
logger.debug("Processing user data")
logger.warning("Deprecated API endpoint used")
```

#### Структурированное логирование
```python
logger.error(
    event="Payload fields set is not valid",
    payload=payload,
    required_keys=required_keys,
)
```

#### Логирование с обработкой исключений
```python
def decode_token(self, token: bytes) -> Payload:
    try:
        decoded = pyseto.decode(keys=self.public_key, token=token).payload
    except (pyseto.DecryptError, pyseto.VerifyError, binascii.Error, ValueError) as err:
        logger.warning(
            event="Pyseto decode error", 
            exc=err, 
            token=token,
            error_type=type(err).__name__
        )
        raise UnauthorizedHTTPException from err
    
    payload_dict = json.loads(decoded) if isinstance(decoded, bytes) else decoded
    if not validate_payload_dict(payload_dict):
        logger.error(
            event="Decoded payload is not valid", 
            payload=payload_dict,
            validation_failed=True
        )
        raise UnauthorizedHTTPException
```

#### Логирование в CLI командах
```python
async def create_admin_command(username: str, password: str) -> None:
    try:
        # ... создание администратора
        logger.info("Administrator created successfully", username=username)
    except SQLAlchemyError as exc:
        logger.error(
            event="Database error during admin creation",
            exc=exc,
            username=username,
            error_type="SQLAlchemyError"
        )
        await session.rollback()
    except Exception as exc:
        logger.error(
            event="Unexpected error during admin creation",
            exc=exc,
            username=username,
            error_type=type(exc).__name__
        )
```

#### Логирование с контекстными переменными
```python
# Request ID автоматически добавляется через middleware
logger.info("Processing user request", user_id=user.id, action="login")

# Ручное добавление контекста
structlog.contextvars.bind_contextvars(operation="user_creation")
logger.info("Starting user creation process")
# ... логика создания пользователя
logger.info("User creation completed")
```

### Переменные окружения

**Основные настройки**:
- `APP_DEBUG=true/false` — режим отладки (влияет на формат логов и Sentry)
- `SENTRY_DSN` — DSN для отправки ошибок в Sentry

**Пример .env файла**:
```bash
# Режим разработки
APP_DEBUG=true

# Sentry (только для production)
SENTRY_DSN=https://your-sentry-dsn@sentry.io/project-id
```

### Архитектурные принципы

**Централизованная конфигурация**:
- Все настройки логирования в `src/config/loggers.py`
- Единая точка конфигурации для всего приложения
- Легкость изменения форматов и процессоров

**Разделение по окружениям**:
- Debug режим: удобочитаемый формат для разработки
- Production режим: структурированный JSON для мониторинга
- Автоматическое переключение через переменные окружения

**Контекстность**:
- Request ID для трейсинга запросов
- Контекстные переменные для группировки логов
- Автоматическое добавление метаданных

**Производительность**:
- Асинхронное логирование через Litestar plugin
- Кэширование логгеров (`cache_logger_on_first_use=True`)
- Минимальное влияние на производительность приложения

## Мониторинг и алерты

### Текущие возможности
- **Sentry**: Автоматические алерты на ошибки и исключения
- **Request ID**: Трейсинг запросов через логи
- **ECS формат**: Готовность к интеграции с ELK Stack
- **Structured logs**: Упрощенный поиск и анализ

### Формат логов в production
```json
{
  "@timestamp": "2024-01-15T10:30:00.000Z",
  "log.level": "ERROR",
  "message": "Database error during admin creation",
  "ecs.version": "1.6.0",
  "service.name": "my-site",
  "request_id": "550e8400-e29b-41d4-a716-446655440000",
  "error.type": "SQLAlchemyError",
  "error.message": "Connection timeout",
  "username": "admin_user"
}
```

### Интеграция с системами мониторинга
- **ELK Stack**: ECS формат готов для Elasticsearch
- **Grafana**: Визуализация логов через Loki
- **Sentry**: Отслеживание ошибок и производительности
- **Custom dashboards**: Анализ структурированных логов

