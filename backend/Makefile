NAME := src
TESTS := tests
UV := $(shell command -v uv 2> /dev/null)

.PHONY: collectstatic
collectstatic:
	@if [ -z $(UV) ]; then echo "UV could not be found."; exit 2; fi
	$(UV) run manage.py collectstatic --noinput

.PHONY: migrate
migrate:
	@if [ -z $(UV) ]; then echo "UV could not be found."; exit 2; fi
	$(UV) run manage.py migrate

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
	$(UV) run pytest -vvv -x

.PHONY: tests-coverage
tests-coverage:
	@if [ -z $(UV) ]; then echo "UV could not be found."; exit 2; fi
	$(UV) run coverage run -m pytest -v
	$(UV) run coverage xml
	$(UV) run coverage report --fail-under=95

.PHONY: quality
quality:
	-make bandit
	-make vulture
	make fix
	make types
	make ruff-check
	make tests
