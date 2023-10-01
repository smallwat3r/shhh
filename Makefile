SHELL    = /bin/bash
SRC_DIR  = shhh
TEST_DIR = tests

.PHONY: help
help:  ## Show this help menu
	@echo "Usage: make [TARGET ...]"
	@echo ""
	@grep --no-filename -E '^[a-zA-Z_%-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "%-10s %s\n", $$1, $$2}'

.PHONY: dc-start
dc-start: dc-stop  ## Start dev docker server
	@docker compose -f docker-compose.yml up --build --scale adminer=0 -d;

.PHONY: dc-start-adminer
dc-start-adminer: dc-stop  ## Start dev docker server (with adminer)
	@docker compose -f docker-compose.yml up --build -d;

.PHONY: dc-stop
dc-stop:  ## Stop dev docker server
	@docker compose -f docker-compose.yml stop;

VENV          = venv
VENV_PYTHON   = $(VENV)/bin/python
SYSTEM_PYTHON = $(or $(shell which python3.10), $(shell which python))
PYTHON        = $(or $(wildcard $(VENV_PYTHON)), $(SYSTEM_PYTHON))

$(VENV_PYTHON):
	rm -rf $(VENV)
	$(SYSTEM_PYTHON) -m venv $(VENV)

.PHONY: venv
venv: $(VENV_PYTHON)  ## Create a Python virtual environment

.PHONY: deps
deps:  ## Install Python requirements in virtual environment
	$(PYTHON) -m pip install --upgrade pip
	$(PYTHON) -m pip install -r requirements.txt -r dev-requirements.txt

.PHONY: checks
checks: tests ruff mypy bandit  ## Run all checks (unit tests, ruff, mypy, bandit)

.PHONY: tests
tests:  ## Run unit tests
	@echo "Running tests..."
	$(PYTHON) -m pytest --cov=shhh tests

.PHONY: yapf
yapf:  ## Format python code with yapf
	@echo "Running Yapf..."
	$(PYTHON) -m yapf --recursive --in-place $(SRC_DIR) $(TEST_DIR)

.PHONY: ruff
ruff:  ## Run ruff
	@echo "Running Ruff report..."
	$(PYTHON) -m ruff $(SRC_DIR) $(TEST_DIR)

.PHONY: mypy
mypy:  ## Run mypy
	@echo "Running Mypy report..."
	$(PYTHON) -m mypy $(SRC_DIR)

.PHONY: bandit
bandit:  ## Run bandit
	@echo "Running Bandit report..."
	$(PYTHON) -m bandit -r $(SRC_DIR) -x $(SRC_DIR)/static

.PHONY: yarn
yarn:  ## Install frontend deps using Yarn
	@echo "Installing yarn deps..."
	@yarn install >/dev/null

.PHONY: shell
shell:  ## Pop up a Flask shell in Shhh
	docker exec -it shhh-app-1 flask shell

.PHONY: logs
logs:  ## Follow Flask logs
	docker logs shhh-app-1 -f -n 10

.PHONY: db-logs
db-logs:  ## Follow Postgre logs
	docker logs shhh-db-1 -f -n 10
