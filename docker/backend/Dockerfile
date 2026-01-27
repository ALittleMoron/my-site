FROM astral/uv:python3.14-trixie-slim AS builder

ENV APP_PATH=/project
ENV UV_VENV_PATH=/project/.venv

WORKDIR $APP_PATH

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-cache --all-extras --no-install-project


FROM astral/uv:python3.14ixie-slim

ENV CUSTOM_USER=python-user
ENV APP_PATH=/project
ENV UV_CACHE_DIR=/project/.cache/uv
ENV PYTHONPATH=$APP_PATH/src
ENV PATH=$APP_PATH/.venv/bin:${PATH}

RUN groupadd $CUSTOM_USER \
 && useradd -g $CUSTOM_USER $CUSTOM_USER \
 && mkdir -p $APP_PATH /project/.cache/uv \
 && chown -R $CUSTOM_USER:$CUSTOM_USER $APP_PATH /project/.cache

WORKDIR $APP_PATH

RUN apt-get update \
 && apt-get -y install make --no-install-recommends \
 && rm -rf /var/lib/apt/lists/*

COPY --from=builder /project/.venv /project/.venv
COPY . ./

USER $CUSTOM_USER:$CUSTOM_USER

EXPOSE 8080
CMD ["sh", "./docker/backend/start_application.sh"]
