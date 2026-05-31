# Мой личный сайт

[🇺🇸 English version](./README.md)

| Категория | Технологии |
|----------|------------|
| Покрытие | ![coverage-backend](./badges/coverage-backend.svg) ![coverage-frontend](./badges/coverage-frontend.svg) |
| Backend | ![python](./badges/python.svg) ![litestar](./badges/litestar.svg) ![async](./badges/async.svg) ![pydantic](./badges/pydantic.svg) ![dishka](./badges/dishka.svg) ![argon2](./badges/argon2.svg) |
| База данных | ![postgresql](./badges/postgresql.svg) ![sqlalchemy](./badges/sqlalchemy.svg) ![alembic](./badges/alembic.svg) |
| Frontend | ![angular](./badges/angular.svg) ![typescript](./badges/typescript.svg) ![bootstrap](./badges/bootstrap.svg) |
| Тестирование | ![pytest](./badges/pytest.svg) ![jest](./badges/jest.svg) ![locust](./badges/locust.svg) |
| DevOps | ![docker](./badges/docker.svg) ![nginx](./badges/nginx.svg) ![minio](./badges/minio.svg) ![docker-compose](./badges/docker-compose.svg) |
| Качество | ![ruff](./badges/ruff.svg) ![mypy](./badges/mypy.svg) ![bandit](./badges/bandit.svg) ![vulture](./badges/vulture.svg) |
| Логирование | ![structlog](./badges/structlog.svg) ![ecs-logging](./badges/ecs-logging.svg) ![sentry](./badges/sentry.svg) |
| Архитектура | ![clean-architecture](./badges/clean-architecture.svg) ![type-safe](./badges/type-safe.svg) |
| Инструменты | ![uv](./badges/uv.svg) ![uvicorn](./badges/uvicorn.svg) |
| CI/CD | ![github-actions](./badges/github-actions.svg) |

> [!NOTE]
> Backend coverage — pytest (Python). Frontend coverage — Jest (TypeScript). Оба генерируются в отдельных CI job-ах.

Личный сайт с REST API на **Litestar** и SPA-фронтендом на **Angular 19**.
Матрица компетенций, заметки, форма обратной связи и панель администратора.

## 📖 Документация

- [Идея проекта](../docs/idea.md)  
- [Что нужно сделать](../docs/TODO.md)

## 📂 Структура проекта

```
my-site/
├── infra/          # nginx reverse proxy, скрипты запуска
├── frontend/       # Angular 19 SPA (собственный nginx-образ)
├── backend/        # Litestar API + доменная логика
│   ├── src/        # Исходный код приложения
│   ├── tests/      # Backend-тесты (pytest)
│   └── performance/ # сценарии нагрузочного тестирования Locust и отчёты
├── .env.example    # Пример переменных окружения
├── .env.test       # Безопасные переменные для тестового окружения
├── docker-compose.test.yml
└── docker-compose.yml
```

## ✨ Возможности

- Матрица компетенций с вопросами, ответами и рендерингом Markdown
- Заметки с папками, тегами, Markdown-рендерингом и управлением публикацией
- Angular SPA с тёмной/светлой темой и режимами списка/таблицы
- REST API с документацией OpenAPI
- Панель администратора: создание, редактирование, публикация вопросов и заметок
- Форма обратной связи
- Аутентификация на базе PASETO

## 🚀 Запуск

1. Клонировать репозиторий:
```bash
git clone git@github.com:ALittleMoron/my-site.git
cd my-site
```

2. Создать файл `.env`:
```bash
cp .env.example .env
```

3. Сгенерировать сертификаты для `nginx` (опционально для локального запуска):

```bash
mkcert -install
mkcert \
  <your-domain> \
  s3.<your-domain> \
  s3-panel.<your-domain> \
  backup.<your-domain>
mv <your-domain>.pem ./infra/nginx/certs/
mv <your-domain>-key.pem ./infra/nginx/certs/
```

4. Обновить переменные в `.env`.

5. Запустить через `Makefile`:
```bash
make run
```

## ⚙️ Важные ссылки

- Frontend: `http://localhost`
- API: `http://localhost/api`
- Документация API: `http://localhost/api/docs`
- OpenAPI спецификация: `http://localhost/api/docs/openapi.json`

Другие сервисы — в [docker-compose.yml](../docker-compose.yml).

## 🧪 Тесты

```bash
make tests-compose              # изолированная test DB, backend + frontend, автоочистка
make tests-fast                 # backend + frontend с уже запущенной test DB
make test-env-up                # запустить переиспользуемый test PostgreSQL
make test-env-down              # остановить test PostgreSQL и удалить данные
make test-backend-unit          # unit-тесты backend, DB не нужна
make test-backend-integration   # интеграционные тесты backend, нужна test DB
make test-frontend              # только frontend (jest)
make install-performance        # установить dependency group Locust для IDE/локальных запусков
make performance-smoke          # короткий Locust smoke-профиль, пишет backend/performance/reports
make query-plans-balanced       # наполнить test DB и выполнить EXPLAIN ANALYZE реальных search-запросов
```
