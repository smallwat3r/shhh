SHELL    = /bin/bash
SRC_DIR  = shhh
TEST_DIR = tests

.PHONY: help
help:  ## Show this help menu
	@echo "Usage: make [TARGET ...]"
	@echo ""
	@grep --no-filename -E '^[a-zA-Z_%-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "%-25s %s\n", $$1, $$2}'

.PHONY: dc-start
dc-start: dc-stop  ## Start dev docker server
	@docker compose -f docker-compose-postgres.yml up --build --scale adminer=0 -d;

.PHONY: dc-start-adminer
dc-start-adminer: dc-stop  ## Start dev docker server (with adminer)
	@docker compose -f docker-compose-postgres.yml up --build -d;

.PHONY: dc-stop
dc-stop:  ## Stop dev docker server
	@docker compose -f docker-compose-postgres.yml stop;

.PHONY: dc-start-mysql
dc-start-mysql: dc-stop  ## Start dev docker server using MySQL
	@docker compose -f docker-compose-mysql.yml up --build --scale adminer=0 -d;

.PHONY: dc-start-adminer-mysql
dc-start-adminer-mysql: dc-stop  ## Start dev docker server using MySQL (with adminer)
	@docker compose -f docker-compose-mysql.yml up --build -d;

.PHONY: dc-stop-mysql
dc-stop-mysql:  ## Stop dev docker server using MySQL
	@docker compose -f docker-compose-mysql.yml stop;

VENV           = .venv
VENV_PYTHON    = $(VENV)/bin/python
SYSTEM_PYTHON  = $(shell which python3.12)
PYTHON         = $(wildcard $(VENV_PYTHON))

$(VENV_PYTHON):
	rm -rf $(VENV)
	$(SYSTEM_PYTHON) -m venv $(VENV)

.PHONY: venv
venv: $(VENV_PYTHON)  ## Create a Python virtual environment

.PHONY: deps
deps:  ## Install Python requirements in virtual environment
	$(PYTHON) -m pip install --upgrade pip
	$(PYTHON) -m pip install --no-cache-dir -r requirements.txt -r requirements.dev.txt

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
	$(PYTHON) -m ruff check $(SRC_DIR) $(TEST_DIR) --exclude shhh/migrations/ --exclude shhh/static/

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

.PHONY: db
db:  ## Run flask db command, ex: `make db c='--help'`
	docker exec -it shhh-app-1 flask db $(c)

.PHONY: logs
logs:  ## Follow Flask logs
	docker logs shhh-app-1 -f -n 10

.PHONY: db-logs
db-logs:  ## Follow database logs
	docker logs shhh-db-1 -f -n 10
