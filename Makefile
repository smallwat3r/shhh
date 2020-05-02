.PHONY: help dc-start dc-stop env test-env tests lint

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

dc-start:
	@docker-compose -f docker-compose.yml stop;
	@docker-compose -f docker-compose.yml up --build -d;

dc-stop:
	@docker-compose -f docker-compose.yml stop;

env:
	./bin/build-env

test-env:
	./bin/test-deps

tests: env test-env
	./bin/run-tests

lint: env test-env
	pylint --rcfile=.pylintrc shhh
