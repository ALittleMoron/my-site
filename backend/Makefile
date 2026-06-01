TEST_ENV_FILE ?= ../.env.test
TEST_ENV_OVERRIDES ?=
PERFORMANCE_ENV_FILE ?= ../.env
QUERY_PLANS_ENV_FILE ?= ../.env.test

.PHONY: install
install:
	bash scripts/install.sh install

.PHONY: install-performance
install-performance:
	bash scripts/install.sh install-performance

.PHONY: run
run:
	bash scripts/app.sh run

.PHONY: run-local
run-local:
	bash scripts/app.sh run-local

.PHONY: cli
cli:
	bash scripts/app.sh cli $(command)

.PHONY: collectstatic
collectstatic:
	bash scripts/app.sh collectstatic

.PHONY: initbuckets
initbuckets:
	bash scripts/app.sh initbuckets

.PHONY: revision
revision:
	bash scripts/alembic.sh revision "$(message)"

.PHONY: migrate
migrate:
	bash scripts/alembic.sh migrate

.PHONY: downgrade
downgrade:
	bash scripts/alembic.sh downgrade

.PHONY: shell
shell:
	bash scripts/app.sh shell

.PHONY: clean
clean:
	bash scripts/quality.sh clean

.PHONY: types
types:
	bash scripts/quality.sh types

.PHONY: bandit
bandit:
	bash scripts/quality.sh bandit

.PHONY: vulture
vulture:
	bash scripts/quality.sh vulture

.PHONY: fix
fix:
	bash scripts/quality.sh fix

# Usage: make lint-file file=src/core/notes/use_cases.py
.PHONY: lint-file
lint-file:
	bash scripts/quality.sh lint-file "$(file)"

.PHONY: ruff-check
ruff-check:
	bash scripts/quality.sh ruff-check

.PHONY: lint-check
lint-check:
	bash scripts/quality.sh lint-check

.PHONY: test
test:
	bash scripts/test.sh test "$(TEST_ENV_FILE)" "$(TEST_ENV_OVERRIDES)"

.PHONY: test-unit
test-unit:
	bash scripts/test.sh test-unit "$(TEST_ENV_FILE)" "$(TEST_ENV_OVERRIDES)"

.PHONY: test-integration
test-integration:
	bash scripts/test.sh test-integration "$(TEST_ENV_FILE)" "$(TEST_ENV_OVERRIDES)"

.PHONY: tests-coverage
tests-coverage:
	bash scripts/test.sh tests-coverage "$(TEST_ENV_FILE)" "$(TEST_ENV_OVERRIDES)"

.PHONY: quality
quality:
	bash scripts/quality.sh quality "$(TEST_ENV_FILE)" "$(TEST_ENV_OVERRIDES)"

.PHONY: performance-smoke
performance-smoke:
	bash scripts/run_locust.sh smoke "$(PERFORMANCE_ENV_FILE)"

.PHONY: performance-baseline
performance-baseline:
	bash scripts/run_locust.sh baseline "$(PERFORMANCE_ENV_FILE)"

.PHONY: performance-report-clean
performance-report-clean:
	bash scripts/run_locust.sh clean "$(PERFORMANCE_ENV_FILE)"

.PHONY: query-plans-balanced
query-plans-balanced:
	bash scripts/run_query_plans.sh balanced "$(QUERY_PLANS_ENV_FILE)"
