.PHONY: help dc-start dc-stop env test-env yarn tests local lint mypy secure fmt checks

SHELL=/bin/bash

help: ## Show this help menu
	@echo "Usage: make [TARGET ...]"
	@echo ""
	@grep --no-filename -E '^[a-zA-Z_%-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "%-10s %s\n", $$1, $$2}'

dc-start: dc-stop  ## Start dev docker server
	@docker-compose -f docker-compose.yml up --build -d;

dc-stop: ## Stop dev docker server
	@docker-compose -f docker-compose.yml stop;

local: yarn env ## Run a local flask server (needs envs/local.env setup)
	@./bin/local

checks: tests lint mypy secure  ## Run all checks (unit tests, pylint, mypy, bandit)

tests: env test-env ## Run unit tests
	@echo "Running tests ..."
	@./bin/run-tests

fmt: test-env ## Format python code with black
	@echo "Running Black ..."
	@source env/bin/activate \
		&& black --line-length 88 --target-version py38 shhh \
		&& black --line-length 88 --target-version py38 tests

lint: test-env ## Run pylint
	@echo "Running Pylint report ..."
	@source env/bin/activate || true \
		&& pylint --rcfile=.pylintrc shhh

mypy: env test-env ## Run mypy
	@echo "Running Mypy report ..."
	@source env/bin/activate || true \
		&& mypy --ignore-missing-imports shhh

secure: env test-env ## Run bandit
	@echo "Running Bandit report ..."
	@source env/bin/activate || true \
		&& bandit -r shhh

env:
	@./bin/build-env

test-env:
	@./bin/test-deps

yarn:
	@echo "Installing yarn deps ..."
	@yarn install >/dev/null
