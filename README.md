# Portfolio Tracker API

A backend service for managing investment portfolios and holdings, built with **Django REST Framework**, **PostgreSQL**, and **Docker**.

## 🚀 Features
- Django REST API with OpenAPI (Swagger & ReDoc) documentation
- PostgreSQL via Docker Compose
- Fully containerised development environment
- Ready for CI/CD and cloud deployment

## 🧱 Tech Stack
- Python 3.13
- Django 5
- Django REST Framework
- drf-spectacular (Swagger / ReDoc)
- PostgreSQL 15
- Docker + docker-compose

## 🧰 Development Setup
```bash
make dev
# or
docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d --build
