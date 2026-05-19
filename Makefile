BACKEND_DIR := backend
FRONTEND_DIR := frontend
NAME := src
TESTS := tests
UV := $(shell command -v uv 2> /dev/null)
UV_RUN := $(UV) --directory $(BACKEND_DIR) run
LITESTAR_CLI_APP := "cli:create_cli"
PYTHONPATH := src
ALEMBIC_CONFIG := src/infra/postgresql/alembic/alembic.ini
LINT_FILE := $(patsubst $(BACKEND_DIR)/%,%,$(file))

.PHONY: run
run:
	chmod +x ./infra/run.sh
	./infra/run.sh

.PHONY: stop
stop:
	docker compose stop
	docker compose down

.PHONY: start_app
start_app:
	PYTHONPATH=$(PYTHONPATH) $(UV_RUN) uvicorn main:create_app --port 8080 --host 0.0.0.0

.PHONY: start_local_app
start_local_app:
	PYTHONPATH=$(PYTHONPATH) APP_DEBUG=true DB_HOST=localhost MINIO_HOST=localhost VALKEY_HOST=localhost $(UV_RUN) python src/main.py

.PHONY: cli
cli:
	PYTHONPATH=$(PYTHONPATH) LITESTAR_APP=$(LITESTAR_CLI_APP) $(UV_RUN) litestar $(command)

.PHONY: collectstatic
collectstatic:
	make cli command="collectstatic"

.PHONY: initbuckets
initbuckets:
	make cli command="initbuckets"

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

.PHONY: install
install:
	@if [ -z $(UV) ]; then echo "UV could not be found."; exit 2; fi
	$(UV) --directory $(BACKEND_DIR) sync --locked --all-extras

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
	$(UV_RUN) ruff format $(TESTS) --config ./pyproject.toml
	$(UV_RUN) ruff format $(NAME) --config ./pyproject.toml

# Usage: make lint-file file=backend/src/core/blog/use_cases.py
.PHONY: lint-file
lint-file:
	@if [ -z $(UV) ]; then echo "UV could not be found."; exit 2; fi
	$(UV_RUN) ruff check --fix $(LINT_FILE) --config ./pyproject.toml
	$(UV_RUN) ruff format $(LINT_FILE) --config ./pyproject.toml

.PHONY: ruff-check
ruff-check:
	@if [ -z $(UV) ]; then echo "UV could not be found."; exit 2; fi
	$(UV_RUN) ruff check $(NAME) $(TESTS) --fix

.PHONY: tests
tests: test-backend test-frontend

.PHONY: test-backend
test-backend:
	@if [ -z $(UV) ]; then echo "UV could not be found."; exit 2; fi
	PYTHONPATH=$(PYTHONPATH) APP_USE_CACHE=false $(UV_RUN) pytest --durations=10 -vvv -x $(TESTS)/

.PHONY: test-backend-unit
test-backend-unit:
	@if [ -z $(UV) ]; then echo "UV could not be found."; exit 2; fi
	PYTHONPATH=$(PYTHONPATH) APP_USE_CACHE=false $(UV_RUN) pytest --durations=10 -vvv -x $(TESTS)/unit/

.PHONY: test-backend-integration
test-backend-integration:
	@if [ -z $(UV) ]; then echo "UV could not be found."; exit 2; fi
	PYTHONPATH=$(PYTHONPATH) APP_USE_CACHE=false $(UV_RUN) pytest --durations=10 -vvv -x $(TESTS)/integration/

.PHONY: test-frontend
test-frontend:
	cd $(FRONTEND_DIR) && npm test -- --watchAll=false

.PHONY: tests-coverage
tests-coverage:
	@if [ -z $(UV) ]; then echo "UV could not be found."; exit 2; fi
	PYTHONPATH=$(PYTHONPATH) APP_USE_CACHE=false $(UV_RUN) coverage run -m pytest $(TESTS)/
	PYTHONPATH=$(PYTHONPATH) APP_USE_CACHE=false $(UV_RUN) coverage xml
	PYTHONPATH=$(PYTHONPATH) APP_USE_CACHE=false $(UV_RUN) coverage report --fail-under=60

.PHONY: quality
quality:
	-make bandit
	-make vulture
	make fix
	make types
	make ruff-check
	make tests
