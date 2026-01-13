FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends curl ca-certificates make
ADD https://astral.sh/uv/install.sh /uv-installer.sh
RUN sh /uv-installer.sh && rm /uv-installer.sh
ENV PATH="/root/.local/bin/:$PATH"

WORKDIR /app

COPY README.md pyproject.toml uv.lock / .env ./
RUN uv sync --no-dev --frozen

EXPOSE ${APP_PORT}

CMD ["sh", "./docker/backend/start_application.sh"]
