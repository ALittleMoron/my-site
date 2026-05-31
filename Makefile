# Infrastructure

.PHONY: run
run:
	chmod +x ./infra/run.sh
	./infra/run.sh

.PHONY: stop
stop:
	docker compose stop
	docker compose down

# Backend

TEST_COMPOSE := docker compose --env-file .env.test -f docker-compose.test.yml

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
	$(MAKE) -C backend test TEST_ENV_FILE=../.env.test

.PHONY: test-backend-unit
test-backend-unit:
	$(MAKE) -C backend test-unit

.PHONY: test-backend-unit-fast
test-backend-unit-fast:
	$(MAKE) -C backend test-unit TEST_ENV_FILE=../.env.test

.PHONY: test-backend-integration
test-backend-integration:
	$(MAKE) -C backend test-integration

.PHONY: test-backend-integration-fast
test-backend-integration-fast:
	$(MAKE) -C backend test-integration TEST_ENV_FILE=../.env.test

.PHONY: test-env-up
test-env-up:
	$(TEST_COMPOSE) up -d --wait postgres-test

.PHONY: test-env-down
test-env-down:
	$(TEST_COMPOSE) down -v --remove-orphans

.PHONY: test-backend-compose
test-backend-compose:
	$(MAKE) test-env-up
	@status=0; \
	$(MAKE) -C backend test TEST_ENV_FILE=../.env.test || status=$$?; \
	$(MAKE) test-env-down; \
	exit $$status

.PHONY: tests-coverage
tests-coverage:
	$(MAKE) -C backend tests-coverage

.PHONY: tests-coverage-frontend
tests-coverage-frontend:
	$(MAKE) -C frontend tests-coverage

.PHONY: quality-backend
quality-backend:
	$(MAKE) -C backend quality

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

# Combined

.PHONY: install
install: install-backend install-frontend

.PHONY: tests
tests: test-backend test-frontend

.PHONY: tests-fast
tests-fast: test-backend-fast test-frontend

.PHONY: tests-compose
tests-compose: test-env-up
	@status=0; \
	$(MAKE) -C backend test TEST_ENV_FILE=../.env.test || status=$$?; \
	if [ $$status -eq 0 ]; then $(MAKE) test-frontend || status=$$?; fi; \
	$(MAKE) test-env-down; \
	exit $$status

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

.PHONY: clean
clean:
	$(MAKE) -C backend clean
