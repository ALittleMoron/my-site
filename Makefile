# Infrastructure

.PHONY: run
run:
	bash infra/scripts/run.sh

.PHONY: stop
stop:
	bash infra/scripts/stop.sh

# Backend

.PHONY: install-backend
install-backend:
	$(MAKE) -C backend install

.PHONY: install-performance
install-performance:
	$(MAKE) -C backend install-performance

.PHONY: migrate
migrate:
	$(MAKE) -C backend migrate

.PHONY: downgrade
downgrade:
	$(MAKE) -C backend downgrade

.PHONY: revision
revision:
	$(MAKE) -C backend revision

.PHONY: test-backend
test-backend:
	$(MAKE) -C backend test

.PHONY: test-backend-fast
test-backend-fast:
	$(MAKE) -C backend test

.PHONY: test-backend-unit
test-backend-unit:
	$(MAKE) -C backend test-unit

.PHONY: test-backend-unit-fast
test-backend-unit-fast:
	$(MAKE) -C backend test-unit

.PHONY: test-backend-integration
test-backend-integration:
	$(MAKE) -C backend test-integration

.PHONY: test-backend-integration-fast
test-backend-integration-fast:
	$(MAKE) -C backend test-integration

.PHONY: test-env-up
test-env-up:
	bash infra/scripts/test_env.sh up

.PHONY: test-env-down
test-env-down:
	bash infra/scripts/test_env.sh down

.PHONY: test-backend-compose
test-backend-compose:
	bash infra/scripts/tests_compose.sh backend

.PHONY: taskiq-worker
taskiq-worker:
	$(MAKE) -C backend taskiq-worker

.PHONY: taskiq-scheduler
taskiq-scheduler:
	$(MAKE) -C backend taskiq-scheduler

.PHONY: tests-coverage
tests-coverage:
	$(MAKE) -C backend tests-coverage

.PHONY: tests-coverage-frontend
tests-coverage-frontend:
	$(MAKE) -C frontend tests-coverage

.PHONY: quality-backend
quality-backend:
	$(MAKE) -C backend quality

.PHONY: security-backend
security-backend:
	$(MAKE) -C backend security

# Frontend

.PHONY: install-frontend
install-frontend:
	$(MAKE) -C frontend install

.PHONY: test-frontend
test-frontend:
	$(MAKE) -C frontend test

.PHONY: quality-frontend
quality-frontend:
	$(MAKE) -C frontend quality

.PHONY: security-frontend
security-frontend:
	$(MAKE) -C frontend security

# Security

.PHONY: lint-dockerfiles
lint-dockerfiles:
	bash infra/scripts/docker_lint.sh hadolint

.PHONY: lint-docker-images
lint-docker-images:
	bash infra/scripts/docker_lint.sh dockle $(DOCKLE_IMAGE_REFS)

.PHONY: security-infra
security-infra:
	bash infra/scripts/security_check.sh

.PHONY: security
security: security-backend security-frontend security-infra

# Combined

.PHONY: install
install: install-backend install-frontend

.PHONY: tests
tests: test-backend test-frontend

.PHONY: tests-fast
tests-fast: test-backend-fast test-frontend

.PHONY: tests-compose
tests-compose:
	bash infra/scripts/tests_compose.sh all

# Performance

.PHONY: performance-smoke
performance-smoke:
	$(MAKE) -C backend performance-smoke

.PHONY: performance-baseline
performance-baseline:
	$(MAKE) -C backend performance-baseline

.PHONY: performance-report-clean
performance-report-clean:
	$(MAKE) -C backend performance-report-clean

.PHONY: query-plans-balanced
query-plans-balanced:
	$(MAKE) -C backend query-plans-balanced

.PHONY: clean
clean:
	$(MAKE) -C backend clean
