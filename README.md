# My Site

A web application with a Litestar as backend with HTMX as frontend (Server Side Rendering). 
My site with blog, mentoring things and others.

## Project Structure

```
my-site/
├── certs/        # Folder with certificates for auth system works
├── docker/       # Docker configuration files (scripts, Dockerfile, nginx conf, etc.)
├── src/          # Source code
├── tests/        # Project autotests
├── .env.example  # Example of project envs
├── ...
└── README.md     # Project readme (current file)
```

## Features

- Competency matrix with questions and answers
- Simple dynamic frontend using HTMX
- API with documentation
- Dark theme UI

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

5. Run Makefile
```bash
make run
```

## Development

- Frontend runs on `http://localhost`
- API runs on `http://localhost/api`
- API documentation available at `http://localhost/api/docs`

For other routes see [docker-compose.yaml](./docker-compose.yml)
