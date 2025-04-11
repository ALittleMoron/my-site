# My Site

A full-stack web application with a Django backend and React frontend, featuring a competency matrix system.

## Project Structure

```
my-site/
├── backend/           # Django backend application
│   ├── src/          # Source code
│   └── README.md     # Backend documentation
└── frontend/         # React frontend application
    ├── src/          # Source code
    └── README.md     # Frontend documentation
```

## Features

- Competency matrix management system
- Interactive grid and list views
- Detailed question and answer display
- Resource management
- Dark theme UI

## Documentation

- [Backend Documentation](backend/README.md) - Django setup, API endpoints, and database configuration
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

# ... add custom variables to .env
```

3. Add exec permission for run.sh file
```bash
chmod +x ./docker/scripts/run.sh
```

4. Run makefile
```bash
make run
```

## Development

- Backend runs on `http://localhost:8000`
- Frontend runs on `http://localhost:8080`
- API documentation available at `http://localhost:8000/api/docs`
