# Мой личный сайт

[🇺🇸 English version](./README.md)

| Категория | Технологии |
|----------|------------|
| Покрытие | ![coverage-backend](./badges/coverage-backend.svg) ![coverage-frontend](./badges/coverage-frontend.svg) |
| Backend | ![python](./badges/python.svg) ![litestar](./badges/litestar.svg) ![async](./badges/async.svg) ![pydantic](./badges/pydantic.svg) ![dishka](./badges/dishka.svg) ![taskiq](./badges/taskiq.svg) ![paseto](./badges/paseto.svg) ![argon2](./badges/argon2.svg) |
| База данных | ![postgresql](./badges/postgresql.svg) ![sqlalchemy](./badges/sqlalchemy.svg) ![alembic](./badges/alembic.svg) |
| Кэш | ![valkey](./badges/valkey.svg) |
| Frontend | ![angular](./badges/angular.svg) ![typescript](./badges/typescript.svg) ![bootstrap](./badges/bootstrap.svg) |
| Тестирование | ![pytest](./badges/pytest.svg) ![jest](./badges/jest.svg) ![locust](./badges/locust.svg) ![lhci](./badges/lhci.svg) |
| DevOps | ![docker](./badges/docker.svg) ![nginx](./badges/nginx.svg) ![minio](./badges/minio.svg) ![docker-compose](./badges/docker-compose.svg) |
| Качество | ![ruff](./badges/ruff.svg) ![mypy](./badges/mypy.svg) ![bandit](./badges/bandit.svg) ![pip-audit](./badges/pip-audit.svg) ![trivy](./badges/trivy.svg) ![hadolint](./badges/hadolint.svg) ![dockle](./badges/dockle.svg) ![vulture](./badges/vulture.svg) ![eslint](./badges/eslint.svg) ![prettier](./badges/prettier.svg) |
| Логирование | ![structlog](./badges/structlog.svg) ![ecs-logging](./badges/ecs-logging.svg) ![sentry](./badges/sentry.svg) |
| Архитектура | ![clean-architecture](./badges/clean-architecture.svg) ![type-safe](./badges/type-safe.svg) |
| Инструменты | ![uv](./badges/uv.svg) ![granian](./badges/granian.svg) ![node](./badges/node.svg) ![npm](./badges/npm.svg) |
| CI/CD | ![github-actions](./badges/github-actions.svg) ![dependabot](./badges/dependabot.svg) |

> [!NOTE]
> Backend coverage — pytest (Python). Frontend coverage — Jest (TypeScript). Оба генерируются в отдельных CI job-ах.

Личный сайт-база знаний с портфолио, case-study страницами, матрицей компетенций, локализованными статьями
и защищёнными рабочими областями админки.

## 📖 Документация

- [Идея проекта](../docs/idea.md)  
- [Что нужно сделать](../docs/TODO.md)

## 📂 Структура проекта

```
my-site/
├── infra/          # nginx reverse proxy, скрипты запуска
├── frontend/       # Angular 22 hybrid SSR/CSR (собственный Node.js-образ)
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

- Матрица компетенций: локализованные листы, разделы и подразделы с управляемым приоритетом, поиск, табличная сетка, детальные ответы, публичные SEO-страницы вопросов, пикер и сортировка структуры в админке, внешние ресурсы
- Статьи: RU/EN-контент, папки, теги, поиск, фильтры по датам/тегам, управление публикацией и SSR-страницы публичных статей
- Защищённая панель владельца/администратора/модератора: создание, редактирование, публикация и снятие с публикации статей и вопросов матрицы, плюс управление командой, где администраторы управляют модераторами, а единственный владелец имеет полный доступ к команде
- Приватная аналитика статей: публичные счётчики просмотров, вовлечённые просмотры, категории источников и анонимные реакции
- Публичная case-study страница «как устроен сайт» про архитектуру, качество и эксплуатацию
- Локализация интерфейса и контента на русском и английском языках
- PASETO-аутентификация для защищённого режима владельца/администратора/модератора с блокировкой неактивных аккаунтов

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
  s3.<your-domain>
mkdir -p ./infra/nginx/certs
mv <your-domain>.pem ./infra/nginx/certs/fullchain.pem
mv <your-domain>-key.pem ./infra/nginx/certs/privkey.pem
```

Контейнер nginx запускается с UID/GID `101:101`, поэтому смонтированные сертификат и
приватный ключ должны быть читаемы этим пользователем. Для локальных файлов `mkcert`
достаточно `chmod 644 ./infra/nginx/certs/<file>`; для production лучше настроить
owner/group-права так, чтобы доступ на чтение был только у nginx.
Production выпуск и renewal Let's Encrypt сертификатов идут через compose-backed
targets `make certbot-issue`, `make certbot-renew` и `make certbot-sync`. Подробнее:
[Production Deploy](../docs/production-deploy.md).

4. Обновить переменные в `.env`.

5. Запустить через `Makefile`:
```bash
make run
```

`make run` заранее проверяет обязательные значения `.env`. Затем он поднимает
PostgreSQL, Valkey, MinIO, Databasus, backend, frontend и nginx через Docker
health checks, выполняет одноразовую backend-инициализацию и переключает публичный
трафик между blue/green backend/frontend слотами через graceful nginx reload.

## ⚙️ Важные ссылки

- Frontend: `http://localhost`
- API: `http://localhost/api`
- API liveness: `http://localhost/api/healthcheck`
- API readiness: `http://localhost/api/healthcheck/ready`
- Документация API: `http://localhost/api/docs`
- OpenAPI спецификация: `http://localhost/api/docs/openapi.json`

Внутренние web-панели доступны только через host-level WireGuard и nginx-порты,
привязанные к `VPN_BIND_ADDRESS`:

- MinIO Console: `http://<VPN_BIND_ADDRESS>:18081`
- Databasus: `http://<VPN_BIND_ADDRESS>:18082`

Production firewall baseline: `80/tcp`, `443/tcp` и выбранный WireGuard UDP
port. Подробнее: [WireGuard internal access](../docs/wireguard-internal-access.md).

Другие сервисы — в [docker-compose.yml](../docker-compose.yml).

## 🧪 Тесты

```bash
make tests-compose              # запустить/переиспользовать test DB, backend + frontend, очистить своё
make tests-fast                 # backend + frontend; test DB готовится автоматически
make test-env-up                # запустить переиспользуемый test PostgreSQL
make test-env-down              # остановить test PostgreSQL и удалить данные
make test-backend-unit          # unit-тесты backend, DB не нужна
make test-backend-integration   # интеграционные тесты backend, test DB готовится автоматически
make test-frontend              # только frontend (jest)
make -C frontend ssr-smoke      # production SSR build + smoke HTML публичной статьи, case-study и вопроса матрицы
make performance-smoke          # автоматический local backend + seed-данные + короткий Locust smoke-профиль
make performance-lighthouse     # production Angular SSR build + strict Lighthouse CI quality/performance gates
make query-plans-balanced       # test DB, storage-wide SQL capture и EXPLAIN ANALYZE gate
```
