# My Site

A full-stack web application with a FastAPI backend and React frontend. My site with blog,
mentoring things and others.

## Project Structure

```
my-site/
├── backend/           # FastAPI backend application
│   ├── src/          # Source code
│   └── README.md     # Backend documentation
└── frontend/         # React frontend application
    ├── src/          # Source code
    └── README.md     # Frontend documentation
```

## Features

- Competency matrix with questions and answers
- Dark theme UI

## Documentation

- [Backend Documentation](backend/README.md) - FastAPI setup, API endpoints, and database configuration
- [Frontend Documentation](frontend/README.md) - React setup, component structure, and development guide

## Quick Start

1. Clone the repository:
```bash
git clone git@github.com:ALittleMoron/my-site.git
cd my-site
```

2. Make .env file
```bash
cp .env.example .env
```

3. Change .env file variables to yours

4. Add exec permission for run.sh file
```bash
chmod +x ./docker/scripts/run.sh
```

5. Run makefile
```bash
make run
```

## Development

- Backend runs on `http://localhost/api`
- Frontend runs on `http://localhost`
- API documentation available at `http://localhost/api/docs`

For other routes see [docker-compose.yaml](./docker-compose.yml)
