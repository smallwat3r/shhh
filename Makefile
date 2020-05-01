.PHONY: dc-start
dc-start:
	@docker-compose -f docker-compose.yml stop;
	@docker-compose -f docker-compose.yml up --build -d;

.PHONY: dc-stop
dc-stop:
	@docker-compose -f docker-compose.yml stop;

.PHONY: tests
tests:
	./run-tests.sh
