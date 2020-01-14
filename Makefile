.PHONY: dc-start
dc-start:
	@docker-compose -f docker-compose-flask.yml stop;
	@docker-compose -f docker-compose-flask.yml up -d;

.PHONY: dc-stop
dc-stop:
	@docker-compose -f docker-compose-flask.yml stop;

.PHONY: dc-reboot
dc-reboot:
	@docker-compose -f docker-compose-flask.yml stop;
	printf 'y' | docker system prune;
	@docker-compose -f docker-compose-flask.yml up -d;

.PHONY: dc-start-nginx
dc-start-nginx:
	@docker-compose -f docker-compose-nginx.yml stop;
	@docker-compose -f docker-compose-nginx.yml up -d;

.PHONY: dc-stop-nginx
dc-stop-nginx:
	@docker-compose -f docker-compose-nginx.yml stop;

.PHONY: dc-reboot-nginx
dc-reboot-nginx:
	@docker-compose -f docker-compose-nginx.yml stop;
	printf 'y' | docker system prune;
	@docker-compose -f docker-compose-nginx.yml up -d;

.PHONY: dc-cleanup
dc-cleanup:
	@docker rm $(shell docker ps -qa --no-trunc --filter "status=exited");
	@docker rmi $(shell docker images --filter "dangling=true" -q --no-trunc);
