# --------------------------------------------
# DJANGO / DOCKER MAKEFILE
# --------------------------------------------
# Usage:
#   make dev            → run local dev stack (hot reload)
#   make staging        → run staging stack (Gunicorn + docs)
#   make prod           → run production-like stack (Gunicorn)
#   make down           → stop all containers
#   make clean          → stop + remove volumes (wipe DB)
#   make logs           → follow logs
#   make shell          → open shell in web container
#   make migrate        → run Django migrations
#   make makemigrations → create migrations from model changes
#   make superuser      → create Django superuser
#   make build          → build containers only
#   make test           → run tests inside the web container
#   make test-local     → run tests via Pipenv on host
#   make lint           → ruff+isort+black checks (no changes)
#   make format         → isort+black (writes changes)
#   make precommit      → run pre-commit on all files
#   make help           → show this list
# --------------------------------------------

# ---- Compose runner (switch to "docker-compose" if you use legacy) ----
DC ?= docker compose

# --------------------------------------------
# COMPOSE FILE PATHS
# --------------------------------------------
COMPOSE_DEV = -f docker-compose.yml -f docker-compose.dev.yml
COMPOSE_STAGING = -f docker-compose.yml -f docker-compose.staging.yml
COMPOSE_PROD = -f docker-compose.yml

# --------------------------------------------
# PHONY TARGETS
# --------------------------------------------
.PHONY: help dev staging prod down clean logs shell migrate makemigrations superuser build \
        test test-local lint format precommit


# --------------------------------------------
# TARGETS
# --------------------------------------------

help:
	@echo ""
	@echo "Usage: make [target]"
	@echo ""
	@echo "Targets:"
	@echo "  dev        - Build and run local development stack (hot reload)"
	@echo "  staging    - Build and run staging stack (Gunicorn + docs enabled)"
	@echo "  prod       - Build and run production-like stack (Gunicorn)"
	@echo "  down       - Stop and remove containers (keep volumes)"
	@echo "  clean      - Stop containers and remove volumes (wipe DB)"
	@echo "  logs       - Follow logs for all services"
	@echo "  shell      - Open shell in web container"
	@echo "  migrate    - Run Django migrations"
	@echo "  makemigrations - Create migrations from model changes"
	@echo "  superuser      - Create Django superuser"
	@echo "  build          - Build containers only"
	@echo "  test           - Run tests inside the web container"
	@echo "  test-local     - Run tests via Pipenv on host"
	@echo "  lint           - Ruff+isort+Black checks"
	@echo "  format         - Apply isort+Black formatting"
	@echo "  precommit      - Run pre-commit on all files"
	@echo ""

dev:
	$(DC) $(COMPOSE_DEV) up -d --build
	@echo "Dev stack running at http://localhost:8000"

staging:
	$(DC) $(COMPOSE_STAGING) up -d --build
	@echo "Staging stack running at http://localhost:8001"

prod-build:
	$(DC) $(COMPOSE_PROD) build

prod-up:
	$(DC) $(COMPOSE_PROD) up -d --build
	@echo "Production-like stack running at http://localhost:8000"

prod-down:
	$(DC) $(COMPOSE_PROD) down -v

prod-logs:
	$(DC) $(COMPOSE_PROD) logs -f web

down:
	$(DC) down
	@echo "Containers stopped (volumes preserved)"

clean:
	$(DC) down -v
	@echo "Containers and volumes removed (DB wiped)"

logs:
	$(DC) logs -f

shell:
	$(DC) exec web /bin/bash

migrate:
	$(DC) exec web python manage.py migrate

makemigrations:
	$(DC) exec web python manage.py makemigrations

superuser:
	$(DC) exec web python manage.py createsuperuser

build:
	$(DC) build
	@echo "Containers rebuilt successfully"

# ---- Testing ----
# Inside the container (parity with CI)
test:
	$(DC) exec web pytest --maxfail=1 --disable-warnings -q

# On host via Pipenv (fast local loop)
test-local:
	pipenv run pytest --maxfail=1 --disable-warnings -q --cov --cov-report=term-missing

# ---- Linting / Formatting ----
lint:
	pipenv run ruff check .
	pipenv run isort --check-only .
	pipenv run black --check .

format:
	pipenv run isort .
	pipenv run black .

precommit:
	pipenv run pre-commit run --all-files