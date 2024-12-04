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

.PHONY: lint
lint:
	@if [ -z $(PDM) ]; then echo "PDM could not be found."; exit 2; fi
	$(PDM) run mypy --explicit-package-bases --config-file pyproject.toml src
	$(PDM) run pyright $(NAME)
	$(PDM) run isort --settings-path ./pyproject.toml --check-only $(NAME)
	$(PDM) run black --config ./pyproject.toml --check $(NAME) --diff
	$(PDM) run ruff check $(NAME)
	$(PDM) run vulture $(NAME) --min-confidence 100
	$(PDM) run bandit --configfile ./pyproject.toml -r ./$(NAME)

.PHONY: fix
fix:
	@if [ -z $(PDM) ]; then echo "PDM could not be found."; exit 2; fi
	$(PDM) run ruff check $(NAME) --config ./pyproject.toml --fix
	$(PDM) run black --config ./pyproject.toml $(NAME)

.PHONY: test
tests:
	@if [ -z $(PDM) ]; then echo "PDM could not be found."; exit 2; fi
	PYTHONPATH=src $(PDM) run coverage run -m pytest -vv
	$(PDM) run coverage xml
	$(PDM) run coverage report --fail-under=95