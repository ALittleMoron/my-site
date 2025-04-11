# Use Python 3.12 slim image
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends curl ca-certificates make
ADD https://astral.sh/uv/install.sh /uv-installer.sh
RUN sh /uv-installer.sh && rm /uv-installer.sh
ENV PATH="/root/.local/bin/:$PATH"

WORKDIR /app

COPY backend/README.md backend/pyproject.toml backend/uv.lock ./
RUN uv sync --frozen
COPY backend/ .

RUN make collectstatic
RUN make migrate

EXPOSE ${APP_PORT}

CMD ["uv", "run", "gunicorn", "src.asgi:application", "--bind", "${APP_HOST}:{APP_PORT}", "--workers", "4"]