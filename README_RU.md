# My Personal Site

[🇺🇸 English version](./README.md)

![coverage](./coverage.svg)

> [!WARNING]
> Значок coverage.svg показывает процент покрытия не всего проекта.  
> Я сделал это намеренно, так как некоторые части кода я тестировал вручную (CLI, HTMX-фронтенд),  
> а для некоторых частей (например, провайдеры IOC или конфигурация SQLAdmin views)  
> нет смысла писать pytest-тесты, так как это тривиальный код без бизнес-логики. Возможно, в
> будущем я добавь тесты через какой-нибудь selenium или тому подобный инструментарий, но пока
> такое тестирую вручную.

Веб-приложение с **Litestar** в качестве backend и **HTMX** в качестве frontend (Server Side
Rendering). Мой сайт с блогом, матрицей компетенций, материалами по менторству и другими вещами.

## 📖 Документация

- [Идея проекта](docs/idea.md)  
- [Техническое видение](docs/vision.md) 

## 📂 Структура проекта

```
my-site/
├── docker/ # Файлы конфигурации Docker (скрипты, Dockerfile, конфиги nginx и др.)
├── src/ # Исходный код
├── tests/ # Автотесты проекта
├── .env.example # Пример файла окружения
├── ...
└── README.md # Этот файл
```

## ✨ Возможности

- Матрица компетенций с вопросами и ответами  
- Простой динамический фронтенд на HTMX  
- API с документацией  
- Тёмная тема интерфейса  

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

3. Изменить переменные в `.env` под свои значения

4. Запустить с помощью `Makefile`
```bash
make run
```

## ⚙️ Важные ссылки

- Frontend: `http://localhost`
- API: `http://localhost/api`
- Документация API: `http://localhost/api/docs`
- OpenAPI спецификация: `http://localhost/api/docs/openapi.json`

Другие ссылки см. в [docker-compose.yaml](./docker-compose.yml)

