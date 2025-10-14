# 📊 Portfolio Tracker API

![Python](https://img.shields.io/badge/Python-3.13-blue?logo=python)
![Django](https://img.shields.io/badge/Django-5.1-green?logo=django)
![Docker](https://img.shields.io/badge/Docker-Compose-blue?logo=docker)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-blue?logo=postgresql)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)
![Build](https://img.shields.io/badge/Status-Active-success)

A fully containerised **Django REST Framework** backend for managing investment portfolios and holdings.  
Built as part of a backend/infrastructure learning plan — designed for real-world development, testing, and deployment.

---

## 🚀 Features

- Django REST Framework with OpenAPI (Swagger + ReDoc)
- PostgreSQL database running in Docker
- Local and production Docker Compose configurations
- Makefile for one-line setup commands
- Ready for CI/CD integration and cloud deployment
- Developer-friendly structure (local, staging, production settings)

---

## 🧱 Tech Stack

| Layer | Technology |
|-------|-------------|
| **Language** | Python 3.13 |
| **Framework** | Django 5.1 / Django REST Framework |
| **Database** | PostgreSQL 15 |
| **Containerisation** | Docker + docker-compose |
| **Docs** | drf-spectacular (Swagger UI / ReDoc) |

---

## ⚙️ Local Development

```bash
# Build and start containers
make dev
# or manually:
docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d --build
