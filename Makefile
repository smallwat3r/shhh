.PHONY: help dc-start dc-stop env test-env tests lint secure

.DEFAULT: help
help:
	@echo "make dc-start"
	@echo "  Start dev server using docker-compose."
	@echo "make dc-stop"
	@echo "  Stop dev docker server."
	@echo "make tests"
	@echo "  Run tests"
	@echo "make lint"
	@echo "  Run pylint"
	@echo "make mypy"
	@echo "  Run mypy"
	@echo "make secure"
	@echo "  Run bandit"

dc-stop:
	@docker-compose -f docker-compose.yml stop;

dc-start: dc-stop
	@docker-compose -f docker-compose.yml up --build -d;

env:
	@./bin/build-env

test-env:
	@./bin/test-deps

tests: env test-env
	@./bin/run-tests

lint: env test-env
	@pylint --rcfile=.pylintrc shhh

mypy: env test-env
	@mypy --ignore-missing-imports shhh

secure: env test-env
	@bandit -r shhh
