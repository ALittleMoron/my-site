NAME := src
PDM := $(shell command -v pdm 2> /dev/null)

.PHONY: install
install:
	@if [ -z $(PDM) ]; then echo "PDM could not be found."; exit 2; fi
	$(PDM) install -G:all --no-self


.PHONY: shell
shell:
	@if [ -z $(PDM) ]; then echo "PDM could not be found."; exit 2; fi
	$(PDM) run ipython --no-confirm-exit --no-banner --quick \
	--InteractiveShellApp.extensions="autoreload" \
	--InteractiveShellApp.exec_lines="%autoreload 2"

.PHONY: clean
clean:
	find . -type d -name "__pycache__" | xargs rm -rf {};

.PHONY: types
types:
	@if [ -z $(PDM) ]; then echo "PDM could not be found."; exit 2; fi
	$(PDM) run mypy --explicit-package-bases --namespace-packages --config-file pyproject.toml src

.PHONY: bandit
bandit:
	@if [ -z $(PDM) ]; then echo "PDM could not be found."; exit 2; fi
	$(PDM) run bandit --configfile ./pyproject.toml -r ./$(NAME)

.PHONY: vulture
vulture:
	@if [ -z $(PDM) ]; then echo "PDM could not be found."; exit 2; fi
	$(PDM) run vulture $(NAME) --min-confidence 100

.PHONY: black-check
black-check:
	@if [ -z $(PDM) ]; then echo "PDM could not be found."; exit 2; fi
	$(PDM) run black --config ./pyproject.toml --check $(NAME) --diff

.PHONY: ruff-check
ruff-check:
	@if [ -z $(PDM) ]; then echo "PDM could not be found."; exit 2; fi
	$(PDM) run ruff check $(NAME)

.PHONY: fix
fix:
	@if [ -z $(PDM) ]; then echo "PDM could not be found."; exit 2; fi
	$(PDM) run ruff check $(NAME) --config ./pyproject.toml --fix
	$(PDM) run black --config ./pyproject.toml $(NAME)

.PHONY: tests
tests:
	@if [ -z $(PDM) ]; then echo "PDM could not be found."; exit 2; fi
	PYTHONPATH=src DB_NAME=my_site_database_test $(PDM) run behave --stop
	PYTHONPATH=src DB_NAME=my_site_database_test $(PDM) run pytest -vvv -x

.PHONY: tests-coverage
tests-coverage:
	@if [ -z $(PDM) ]; then echo "PDM could not be found."; exit 2; fi
	PYTHONPATH=src DB_NAME=my_site_database_test $(PDM) run coverage run -m behave
	PYTHONPATH=src DB_NAME=my_site_database_test $(PDM) run coverage run -a -m pytest -v
	$(PDM) run coverage xml
	$(PDM) run coverage report --fail-under=95

.PHONY: quality
quality:
	-make bandit
	-make vulture
	make types
	make ruff-check
	make black-check
	make tests
