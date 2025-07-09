NAME := src
TESTS := tests
UV := $(shell command -v uv 2> /dev/null)
LITESTAR_APP := "src.main:create_cli_app"

.PHONY: run
run:
	./docker/scripts/run.sh

.PHONY: start_app
start_app:
	PYTHONPATH=src uv run uvicorn src.main:create_app --port 8000 --host 0.0.0.0

.PHONY: start_admin
start_admin:
	PYTHONPATH=src uv run uvicorn src.main:create_admin_app --port 8000 --host 0.0.0.0

.PHONY: start_local_app
start_local_app:
	PYTHONPATH=src APP_DEBUG=true DB_HOST=localhost MINIO_HOST=localhost uv run src/main.py

.PHONY: litestar
litestar:
	PYTHONPATH=src LITESTAR_APP=$(LITESTAR_APP) uv run litestar $(command)

.PHONY: revision
revision:
	@if [ -z $(UV) ]; then echo "UV could not be found."; exit 2; fi
	$(UV) run alembic -c src/db/alembic/alembic.ini revision -m "$(word 2, $(MAKECMDGOALS)))" --autogenerate

.PHONY: migrate
migrate:
	@if [ -z $(UV) ]; then echo "UV could not be found."; exit 2; fi
	$(UV) run alembic -c src/db/alembic/alembic.ini upgrade head

.PHONY: downgrade
downgrade:
	@if [ -z $(UV) ]; then echo "UV could not be found."; exit 2; fi
	$(UV) run alembic -c src/db/alembic/alembic.ini downgrade -1

.PHONY: install
install:
	@if [ -z $(UV) ]; then echo "PDM could not be found."; exit 2; fi
	$(UV) install -G:all --no-self

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
	$(UV) run ruff format $(TESTS) --config ./pyproject.toml
	$(UV) run ruff format $(NAME) --config ./pyproject.toml

.PHONY: ruff-check
ruff-check:
	@if [ -z $(UV) ]; then echo "UV could not be found."; exit 2; fi
	$(UV) run ruff check $(NAME) --fix

.PHONY: tests
tests:
	@if [ -z $(UV) ]; then echo "UV could not be found."; exit 2; fi
	PYTHONPATH=src $(UV) run pytest -vvv -x $(TESTS)

.PHONY: tests-coverage
tests-coverage:
	@if [ -z $(UV) ]; then echo "UV could not be found."; exit 2; fi
	PYTHONPATH=src $(UV) run coverage run -m pytest -v
	PYTHONPATH=src $(UV) run coverage xml
	PYTHONPATH=src $(UV) run coverage report --fail-under=95

.PHONY: quality
quality:
	-make bandit
	-make vulture
	make fix
	make types
	make ruff-check
	make tests
