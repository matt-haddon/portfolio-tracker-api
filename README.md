# 📊 Portfolio Tracker API

![Python](https://img.shields.io/badge/Python-3.13-blue?logo=python)
![Django](https://img.shields.io/badge/Django-5.1-green?logo=django)
![Docker](https://img.shields.io/badge/Docker-Compose-blue?logo=docker)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-blue?logo=postgresql)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)
![Build](https://img.shields.io/badge/Status-Active-success)

A fully containerised **Django REST Framework** backend for managing investment portfolios and holdings.

---

## ⚡ Quickstart TL;DR

```bash
# 1. Clone the repo
git clone <your-repo-url>
cd portfolio-tracker-api

# 2. Copy env template (if exists) or create .env
cp .env.example .env  # or create .env manually

# 3. Start the local stack
make dev

# 4. Run migrations and tests
make migrate
make test

# 5. Obtain a JWT
curl -X POST http://localhost:8000/api/v1/auth/token/   -H "Content-Type: application/json"   -d '{"email": "you@example.com", "password": "yourpassword"}'

# 6. Open API docs
open http://localhost:8000/api/docs/
```

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
make dev
# or:
docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d --build
```

---

# 📚 API Overview

Base URL:

```
/api/v1/
```

Authentication uses **JWT** via SimpleJWT:

```
POST /api/v1/auth/token/
POST /api/v1/auth/token/refresh/
```

Include JWT in all protected requests:

```
Authorization: Bearer <access_token>
```

---

# 🗂 Portfolios API

Portfolios represent collections of investments owned by a single user.

### 🔒 Multi-Tenant Isolation

- You **only see your own portfolios**
- You **cannot access another user's data**
- Cross-tenant operations return **404 Not Found**

## 📌 Endpoints

| Method | Endpoint | Description |
|--------|-----------|-------------|
| GET | `/api/v1/portfolios/` | List your portfolios |
| POST | `/api/v1/portfolios/` | Create a portfolio |
| GET | `/api/v1/portfolios/{id}/` | Get one portfolio |
| PUT/PATCH | `/api/v1/portfolios/{id}/` | Update a portfolio |
| DELETE | `/api/v1/portfolios/{id}/` | Delete a portfolio |

### Example: Create a Portfolio

```json
POST /api/v1/portfolios/
{
  "name": "Core",
  "currency": "GBP"
}
```

---

# 📈 Holdings API

Holdings represent individual assets within a portfolio.

### Rules:

- Must belong to a portfolio you own  
- Symbol uniqueness is case-insensitive  
- Symbol is always stored **uppercase**  
- Includes computed `cost_basis`

### 🔒 Multi-Tenant Isolation

- You cannot create holdings in another user's portfolio  
- You only see your own holdings  
- Cross-user access returns **404**  

## 📌 Endpoints

| Method | Endpoint | Description |
|--------|-----------|-------------|
| GET | `/api/v1/holdings/` | List your holdings |
| POST | `/api/v1/holdings/` | Create a holding |
| GET | `/api/v1/holdings/{id}/` | Retrieve a holding |
| PUT/PATCH | `/api/v1/holdings/{id}/` | Update |
| DELETE | `/api/v1/holdings/{id}/` | Delete |

### Example: Create a Holding

```json
POST /api/v1/holdings/
{
  "portfolio": 1,
  "symbol": "AAPL",
  "quantity": "10",
  "avg_price": "150"
}
```

---

# 🔍 Searching, Filtering & Ordering

### Portfolios

```
?search=<name>
?ordering=name
```

### Holdings

```
?search=<symbol/display_name>
?ordering=quantity
?portfolio=<id>
```

---

# 🔧 Environment Variables

Typical `.env` variables:

### Django

| Variable | Description | Example |
|----------|-------------|---------|
| `DJANGO_SETTINGS_MODULE` | Settings path | `portfolio_tracker_api.settings.local` |
| `SECRET_KEY` | Django secret key | `changeme` |
| `DEBUG` | Debug mode | `True` |

### Database

| Variable | Description | Example |
|----------|-------------|---------|
| `DATABASE_URL` | Full DB URL | `postgres://postgres:postgres@db:5432/portfolio_tracker` |
| `POSTGRES_DB` | DB name | `portfolio_tracker` |
| `POSTGRES_USER` | User | `postgres` |
| `POSTGRES_PASSWORD` | Password | `postgres` |
| `POSTGRES_HOST` | Host | `db` |
| `POSTGRES_PORT` | Port | `5432` |

### CORS / Hosts

| Variable | Description | Example |
|----------|-------------|---------|
| `ALLOWED_HOSTS` | Hosts | `localhost,127.0.0.1` |
| `CSRF_TRUSTED_ORIGINS` | CSRF origins | `http://localhost:8000` |

---

# 📑 API Documentation

With `DEBUG=True`:

```
/api/docs/
/api/redoc/
/api/schema/
```

---

# 🧪 Testing

- pytest + pytest-django  
- 95%+ coverage  
- Multi-user tenancy tests  
- CRUD + validation tests  
- Unified error-handling tests  

```bash
make test
```

---

# 📦 Deployment

Local + production Docker configs included.

```bash
make prod
```

Ready for AWS, Render, GCP, Azure, Railway, Fly.io, etc.

---
