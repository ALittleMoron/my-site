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

.PHONY: install-backend
install-backend:
	$(MAKE) -C backend install

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

.PHONY: test-backend-unit
test-backend-unit:
	$(MAKE) -C backend test-unit

.PHONY: test-backend-integration
test-backend-integration:
	$(MAKE) -C backend test-integration

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

.PHONY: clean
clean:
	$(MAKE) -C backend clean
