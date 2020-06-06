.PHONY: help dc-start dc-stop env test-env tests local lint mypy secure checks

.DEFAULT: help
help:
	@echo "make dc-start"
	@echo "  Start dev server using docker-compose"
	@echo "make dc-stop"
	@echo "  Stop dev docker server"
	@echo "make local"
	@echo "  Run a local flask server (need envs/local.env setup)"
	@echo "make tests"
	@echo "  Run tests"
	@echo "make lint"
	@echo "  Run pylint"
	@echo "make mypy"
	@echo "  Run mypy"
	@echo "make secure"
	@echo "  Run bandit"
	@echo "make checks"
	@echo "  Run all checks"

dc-stop:
	@docker-compose -f docker-compose.yml stop;

dc-start: dc-stop
	@docker-compose -f docker-compose.yml up --build -d;

env:
	@./bin/build-env

test-env:
	@./bin/test-deps

frontend:
	@yarn install >/dev/null

local: frontend env
	@./bin/local

tests: env test-env
	@./bin/run-tests

lint: env test-env
	@pylint --rcfile=.pylintrc shhh

mypy: env test-env
	@mypy --ignore-missing-imports shhh

secure: env test-env
	@bandit -r shhh

checks: tests lint mypy secure
