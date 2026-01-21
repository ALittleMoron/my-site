FROM astral/uv:python3.13-trixie-slim AS builder

ENV UV_VENV_PATH=/build/.venv

WORKDIR /build

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-cache --all-extras --no-install-project

FROM astral/uv:python3.13-trixie-slim

ENV CUSTOM_USER=python-user
ENV APP_PATH=/project
ENV PYTHONPATH=$APP_PATH/src
ENV PATH=/project/.venv/bin:${PATH}

RUN groupadd $CUSTOM_USER && useradd -g $CUSTOM_USER $CUSTOM_USER \
    && mkdir -p $APP_PATH && chown -R $CUSTOM_USER:$CUSTOM_USER $APP_PATH

WORKDIR $APP_PATH

RUN apt-get update && apt-get -y install make --no-install-recommends

COPY --from=builder /build/.venv ./.venv
COPY . ./
USER $CUSTOM_USER:$CUSTOM_USER
EXPOSE 8080
CMD ["sh", "./docker/backend/start_application.sh"]
