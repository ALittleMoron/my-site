NAME := backend
TESTS := tests
UV := $(shell command -v uv 2> /dev/null)
LITESTAR_CLI_APP := "backend.cli:create_cli"

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
	PYTHONPATH=backend uv run uvicorn backend.main:create_app --port 8080 --host 0.0.0.0

.PHONY: start_local_app
start_local_app:
	PYTHONPATH=backend APP_DEBUG=true DB_HOST=localhost MINIO_HOST=localhost VALKEY_HOST=localhost uv run backend/main.py

.PHONY: cli
cli:
	PYTHONPATH=backend LITESTAR_APP=$(LITESTAR_CLI_APP) uv run litestar $(command)

.PHONY: collectstatic
collectstatic:
	make cli command="collectstatic"

.PHONY: initbuckets
initbuckets:
	make cli command="initbuckets"

.PHONY: revision
revision:
	@if [ -z $(UV) ]; then echo "UV could not be found."; exit 2; fi
	$(UV) run alembic -c backend/db/alembic/alembic.ini revision -m "$(word 2, $(MAKECMDGOALS)))" --autogenerate

.PHONY: migrate
migrate:
	@if [ -z $(UV) ]; then echo "UV could not be found."; exit 2; fi
	$(UV) run alembic -c backend/db/alembic/alembic.ini upgrade head

.PHONY: downgrade
downgrade:
	@if [ -z $(UV) ]; then echo "UV could not be found."; exit 2; fi
	$(UV) run alembic -c backend/db/alembic/alembic.ini downgrade -1

.PHONY: install
install:
	@if [ -z $(UV) ]; then echo "PDM could not be found."; exit 2; fi
	$(UV) sync --locked --all-extras

.PHONY: shell
shell:
	@if [ -z $(UV) ]; then echo "UV could not be found."; exit 2; fi
	$(UV) run ipython --no-confirm-exit --no-banner --quick \
	--InteractiveShellApp.extensions="autoreload" \
	--InteractiveShellApp.exec_lines="%autoreload 2"

.PHONY: clean
clean:
	find . -type d -name "__pycache__" | xargs rm -rf {};

.PHONY: types
types:
	@if [ -z $(UV) ]; then echo "UV could not be found."; exit 2; fi
	$(UV) run mypy --explicit-package-bases --namespace-packages --config-file pyproject.toml $(NAME)
	$(UV) run mypy --explicit-package-bases --namespace-packages --config-file pyproject.toml $(TESTS)

.PHONY: bandit
bandit:
	@if [ -z $(UV) ]; then echo "UV could not be found."; exit 2; fi
	$(UV) run bandit --configfile ./pyproject.toml -r ./$(NAME)

.PHONY: vulture
vulture:
	@if [ -z $(UV) ]; then echo "UV could not be found."; exit 2; fi
	$(UV) run vulture $(NAME) --min-confidence 100

.PHONY: fix
fix:
	@if [ -z $(UV) ]; then echo "UV could not be found."; exit 2; fi
	$(UV) run djlint "$(NAME)/templates" --reformat
	$(UV) run djlint "$(NAME)/static" --reformat
	$(UV) run ruff format $(TESTS) --config ./pyproject.toml
	$(UV) run ruff format $(NAME) --config ./pyproject.toml

# Usage: make lint-file file=backend/core/blog/use_cases.py
.PHONY: lint-file
lint-file:
	@if [ -z $(UV) ]; then echo "UV could not be found."; exit 2; fi
	$(UV) run ruff check --fix $(file) --config ./pyproject.toml
	$(UV) run ruff format $(file) --config ./pyproject.toml

.PHONY: ruff-check
ruff-check:
	@if [ -z $(UV) ]; then echo "UV could not be found."; exit 2; fi
	$(UV) run ruff check $(NAME) --fix

.PHONY: tests
tests:
	@if [ -z $(UV) ]; then echo "UV could not be found."; exit 2; fi
	PYTHONPATH=backend APP_USE_CACHE=false $(UV) run pytest --durations=10 -vvv -x tests/

.PHONY: test-unit
test-unit:
	@if [ -z $(UV) ]; then echo "UV could not be found."; exit 2; fi
	PYTHONPATH=backend APP_USE_CACHE=false $(UV) run pytest --durations=10 -vvv -x tests/unit/

.PHONY: test-integration
test-integration:
	@if [ -z $(UV) ]; then echo "UV could not be found."; exit 2; fi
	PYTHONPATH=backend APP_USE_CACHE=false $(UV) run pytest --durations=10 -vvv -x tests/integration/

.PHONY: tests-coverage
tests-coverage:
	@if [ -z $(UV) ]; then echo "UV could not be found."; exit 2; fi
	PYTHONPATH=backend APP_USE_CACHE=false $(UV) run coverage run -m pytest tests/
	PYTHONPATH=backend APP_USE_CACHE=false $(UV) run coverage xml
	PYTHONPATH=backend APP_USE_CACHE=false $(UV) run coverage report --fail-under=60

.PHONY: quality
quality:
	-make bandit
	-make vulture
	make fix
	make types
	make ruff-check
	make tests
