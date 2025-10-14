# --------------------------------------------
# DJANGO / DOCKER MAKEFILE
# --------------------------------------------
# Usage:
#   make dev       → run local dev stack (hot reload)
#   make staging   → run staging stack (Gunicorn + docs)
#   make prod      → run production-like stack (Gunicorn)
#   make down      → stop all containers
#   make clean     → stop + remove volumes (wipe DB)
#   make logs      → follow logs
#   make shell     → open shell in web container
#   make migrate   → run Django migrations
#   make superuser → create Django superuser
#   make build     → build containers only
#   make help      → show this list
# --------------------------------------------

.PHONY: help dev staging prod down clean logs shell migrate superuser build

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
	@echo "  superuser  - Create Django superuser"
	@echo "  build      - Build containers only"
	@echo ""

# --------------------------------------------
# COMPOSE FILE PATHS
# --------------------------------------------
COMPOSE_DEV = -f docker-compose.yml -f docker-compose.dev.yml
COMPOSE_STAGING = -f docker-compose.yml -f docker-compose.staging.yml
COMPOSE_PROD = -f docker-compose.yml

# --------------------------------------------
# TARGETS
# --------------------------------------------

dev:
	docker-compose $(COMPOSE_DEV) up -d --build
	@echo "🚀 Dev stack running at http://localhost:8000"

staging:
	docker-compose $(COMPOSE_STAGING) up -d --build
	@echo "🚀 Staging stack running at http://localhost:8001 (Swagger docs enabled)"

prod:
	docker-compose $(COMPOSE_PROD) up -d --build
	@echo "🚀 Production-like stack running at http://localhost:8000"

down:
	docker-compose down
	@echo "🛑 Containers stopped (volumes preserved)"

clean:
	docker-compose down -v
	@echo "🧹 Containers and volumes removed (DB wiped)"

logs:
	docker-compose logs -f

shell:
	docker-compose exec web /bin/bash

migrate:
	docker-compose exec web python manage.py migrate

superuser:
	docker-compose exec web python manage.py createsuperuser

build:
	docker-compose build
	@echo "🏗️ Containers rebuilt successfully"
