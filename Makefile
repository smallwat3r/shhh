SHELL=/bin/bash

SRC_DIR=shhh
TESTS_DIR=tests

.PHONY: help
help: ## Show this help menu
	@echo "Usage: make [TARGET ...]"
	@echo ""
	@grep --no-filename -E '^[a-zA-Z_%-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "%-10s %s\n", $$1, $$2}'

.PHONY: dc-start
dc-start: dc-stop  ## Start dev docker server
	@docker-compose -f docker-compose.yml up --build --scale adminer=0 -d;

.PHONY: dc-start-adminer
dc-start-adminer: dc-stop  ## Start dev docker server (with adminer)
	@docker-compose -f docker-compose.yml up --build -d;

.PHONY: dc-stop
dc-stop: ## Stop dev docker server
	@docker-compose -f docker-compose.yml stop;

.PHONY: local
local: yarn env ## Run a local flask server (needs environments/local.env setup)
	@echo "Starting local server ..."
	@./bin/local

.PHONY: checks
checks: tests pylint mypy bandit  ## Run all checks (unit tests, pylint, mypy, bandit)

.PHONY: tests
tests: env test-env ## Run unit tests
	@echo "Running tests ..."
	@./bin/run-tests

.PHONY: fmt
fmt: test-env ## Format python code with black
	@echo "Running Black ..."
	@source env/bin/activate \
		&& black --line-length 100 --target-version py38 $(SRC_DIR) \
		&& black --line-length 100 --target-version py38 $(TESTS_DIR)

.PHONY: pylint
pylint: test-env ## Run pylint
	@echo "Running Pylint report ..."
	@source env/bin/activate || true \
		&& pylint --rcfile=.pylintrc $(SRC_DIR)

.PHONY: mypy
mypy: env test-env ## Run mypy
	@echo "Running Mypy report ..."
	@source env/bin/activate || true \
		&& mypy --ignore-missing-imports $(SRC_DIR)

.PHONY: bandit
bandit: env test-env ## Run bandit
	@echo "Running Bandit report ..."
	@source env/bin/activate || true \
		&& bandit -r $(SRC_DIR) -x $(SRC_DIR)/static

.PHONY: env
env:
	@./bin/build-env

.PHONY: test-env
test-env:
	@./bin/test-deps

.PHONY: yarn
yarn:
	@echo "Installing yarn deps ..."
	@yarn install >/dev/null
