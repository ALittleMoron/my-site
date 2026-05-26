.PHONY: install
install:
	npm ci --legacy-peer-deps

.PHONY: test
test:
	npm test -- --watchAll=false

.PHONY: test-watch
test-watch:
	npm run test:watch

.PHONY: test-coverage
test-coverage:
	npm run test:coverage

.PHONY: tests-coverage
tests-coverage:
	npm test -- --watchAll=false --coverage

.PHONY: format
format:
	npx prettier --write src

.PHONY: format-check
format-check:
	npx prettier --check src

.PHONY: lint
lint:
	npm run lint

.PHONY: typecheck
typecheck:
	npx tsc --noEmit -p tsconfig.app.json

.PHONY: quality
quality:
	$(MAKE) format
	$(MAKE) lint
	$(MAKE) typecheck
	$(MAKE) test
