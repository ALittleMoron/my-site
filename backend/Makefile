UV := $(shell command -v uv 2> /dev/null)
UV_RUN := $(UV) run
PYTHONPATH := src
ALEMBIC_CONFIG := src/infra/postgresql/alembic/alembic.ini
NAME := src
TESTS := tests

.PHONY: install
install:
	@if [ -z $(UV) ]; then echo "UV could not be found."; exit 2; fi
	$(UV) sync --locked --all-extras

.PHONY: run
run:
	PYTHONPATH=$(PYTHONPATH) $(UV_RUN) uvicorn main:create_app --port 8080 --host 0.0.0.0

.PHONY: run-local
run-local:
	PYTHONPATH=$(PYTHONPATH) APP_DEBUG=true DB_HOST=localhost MINIO_HOST=localhost VALKEY_HOST=localhost $(UV_RUN) python src/main.py

.PHONY: cli
cli:
	PYTHONPATH=$(PYTHONPATH) LITESTAR_APP="cli:create_cli" $(UV_RUN) litestar $(command)

.PHONY: collectstatic
collectstatic:
	$(MAKE) cli command="collectstatic"

.PHONY: initbuckets
initbuckets:
	$(MAKE) cli command="initbuckets"

.PHONY: revision
revision:
	@if [ -z $(UV) ]; then echo "UV could not be found."; exit 2; fi
	PYTHONPATH=$(PYTHONPATH) $(UV_RUN) alembic -c $(ALEMBIC_CONFIG) revision -m "$(word 2, $(MAKECMDGOALS)))" --autogenerate

.PHONY: migrate
migrate:
	@if [ -z $(UV) ]; then echo "UV could not be found."; exit 2; fi
	PYTHONPATH=$(PYTHONPATH) $(UV_RUN) alembic -c $(ALEMBIC_CONFIG) upgrade head

.PHONY: downgrade
downgrade:
	@if [ -z $(UV) ]; then echo "UV could not be found."; exit 2; fi
	PYTHONPATH=$(PYTHONPATH) $(UV_RUN) alembic -c $(ALEMBIC_CONFIG) downgrade -1

.PHONY: shell
shell:
	@if [ -z $(UV) ]; then echo "UV could not be found."; exit 2; fi
	PYTHONPATH=$(PYTHONPATH) $(UV_RUN) ipython --no-confirm-exit --no-banner --quick \
	--InteractiveShellApp.extensions="autoreload" \
	--InteractiveShellApp.exec_lines="%autoreload 2"

.PHONY: clean
clean:
	find . -type d -name "__pycache__" | xargs rm -rf {};

.PHONY: types
types:
	@if [ -z $(UV) ]; then echo "UV could not be found."; exit 2; fi
	PYTHONPATH=$(PYTHONPATH) $(UV_RUN) mypy --explicit-package-bases --namespace-packages --config-file pyproject.toml $(NAME)
	PYTHONPATH=$(PYTHONPATH) $(UV_RUN) mypy --explicit-package-bases --namespace-packages --config-file pyproject.toml $(TESTS)

.PHONY: bandit
bandit:
	@if [ -z $(UV) ]; then echo "UV could not be found."; exit 2; fi
	$(UV_RUN) bandit --configfile ./pyproject.toml -r ./$(NAME)

.PHONY: vulture
vulture:
	@if [ -z $(UV) ]; then echo "UV could not be found."; exit 2; fi
	PYTHONPATH=$(PYTHONPATH) $(UV_RUN) vulture $(NAME) --min-confidence 100

.PHONY: fix
fix:
	@if [ -z $(UV) ]; then echo "UV could not be found."; exit 2; fi
	$(UV_RUN) ruff format $(NAME) $(TESTS) --config ./pyproject.toml

# Usage: make lint-file file=src/core/blog/use_cases.py
.PHONY: lint-file
lint-file:
	@if [ -z $(UV) ]; then echo "UV could not be found."; exit 2; fi
	$(UV_RUN) ruff check --fix $(file) --config ./pyproject.toml
	$(UV_RUN) ruff format $(file) --config ./pyproject.toml

.PHONY: ruff-check
ruff-check:
	@if [ -z $(UV) ]; then echo "UV could not be found."; exit 2; fi
	$(UV_RUN) ruff check $(NAME) $(TESTS) --fix

.PHONY: lint-check
lint-check:
	@if [ -z $(UV) ]; then echo "UV could not be found."; exit 2; fi
	$(UV_RUN) ruff format $(NAME) $(TESTS) --check --config ./pyproject.toml
	$(UV_RUN) ruff check $(NAME) $(TESTS) --config ./pyproject.toml

.PHONY: test
test:
	@if [ -z $(UV) ]; then echo "UV could not be found."; exit 2; fi
	PYTHONPATH=$(PYTHONPATH) APP_USE_CACHE=false $(UV_RUN) pytest --durations=10 -vvv -x $(TESTS)/

.PHONY: test-unit
test-unit:
	@if [ -z $(UV) ]; then echo "UV could not be found."; exit 2; fi
	PYTHONPATH=$(PYTHONPATH) APP_USE_CACHE=false $(UV_RUN) pytest --durations=10 -vvv -x $(TESTS)/unit/

.PHONY: test-integration
test-integration:
	@if [ -z $(UV) ]; then echo "UV could not be found."; exit 2; fi
	PYTHONPATH=$(PYTHONPATH) APP_USE_CACHE=false $(UV_RUN) pytest --durations=10 -vvv -x $(TESTS)/integration/

.PHONY: tests-coverage
tests-coverage:
	@if [ -z $(UV) ]; then echo "UV could not be found."; exit 2; fi
	PYTHONPATH=$(PYTHONPATH) APP_USE_CACHE=false $(UV_RUN) coverage run -m pytest $(TESTS)/
	PYTHONPATH=$(PYTHONPATH) APP_USE_CACHE=false $(UV_RUN) coverage xml
	PYTHONPATH=$(PYTHONPATH) APP_USE_CACHE=false $(UV_RUN) coverage report --fail-under=60

.PHONY: quality
quality:
	-$(MAKE) bandit
	-$(MAKE) vulture
	$(MAKE) fix
	$(MAKE) types
	$(MAKE) ruff-check
	$(MAKE) test
