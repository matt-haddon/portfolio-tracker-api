# 📊 Portfolio Tracker API

![Python](https://img.shields.io/badge/Python-3.13-blue?logo=python)
![Django](https://img.shields.io/badge/Django-5.1-green?logo=django)
![Docker](https://img.shields.io/badge/Docker-Compose-blue?logo=docker)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-blue?logo=postgresql)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)
![Build](https://img.shields.io/badge/Status-Active-success)

A fully containerised **Django REST Framework** backend for managing investment portfolios and holdings.

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
```

---

# 📚 API Overview

This project exposes a **versioned REST API** under:

```
/api/v1/
```

Authentication is via **JWT (JSON Web Tokens)**, using SimpleJWT.

```
POST /api/v1/auth/token/          # obtain access + refresh tokens
POST /api/v1/auth/token/refresh/  # refresh access token
```

All protected routes require:

```
Authorization: Bearer <access_token>
```

---

# 🗂 Portfolios API

Portfolios represent independently named collections of financial holdings.  
Each portfolio belongs exclusively to a single authenticated user.

### 🔒 Multi-Tenant Isolation

Every portfolio is automatically scoped to the authenticated user:

- You **can only list your own portfolios**
- You **cannot read/update/delete** portfolios belonging to another user  
- Cross-tenant access returns **404 Not Found** for safety

---

## 📌 Endpoints

| Method | Endpoint | Description |
|--------|-----------|-------------|
| `GET` | `/api/v1/portfolios/` | List your portfolios |
| `POST` | `/api/v1/portfolios/` | Create a portfolio |
| `GET` | `/api/v1/portfolios/{id}/` | Retrieve one portfolio (only your own) |
| `PUT/PATCH` | `/api/v1/portfolios/{id}/` | Update a portfolio |
| `DELETE` | `/api/v1/portfolios/{id}/` | Delete a portfolio |

---

### Example: Create a portfolio

**Request**

```json
POST /api/v1/portfolios/
{
  "name": "Core",
  "currency": "GBP"
}
```

**Response**

```json
{
  "id": 1,
  "name": "Core",
  "currency": "GBP",
  "owner": 5,
  "created_at": "...",
  "updated_at": "..."
}
```

---

# 📈 Holdings API

Holdings represent individual assets inside a portfolio (e.g. stocks, ETFs).

A holding:

- **must** belong to a portfolio owned by the authenticated user  
- enforces **case-insensitive uniqueness** on `symbol` per portfolio  
- automatically uppercases `symbol` before saving  
- provides a computed `cost_basis` property (`quantity * avg_price`)

### 🔒 Multi-Tenant Isolation

- You **cannot create a holding** inside another user’s portfolio  
- Listing holdings returns **only your own holdings**  
- Attempts to update/delete another user’s holdings return **404**

---

## 📌 Endpoints

| Method | Endpoint | Description |
|--------|-----------|-------------|
| `GET` | `/api/v1/holdings/` | List your holdings (search/filter/order supported) |
| `POST` | `/api/v1/holdings/` | Create a holding in one of your portfolios |
| `GET` | `/api/v1/holdings/{id}/` | Retrieve a holding (your own only) |
| `PUT/PATCH` | `/api/v1/holdings/{id}/` | Update a holding |
| `DELETE` | `/api/v1/holdings/{id}/` | Delete a holding |

---

## 📘 Example: Create a holding

**Request**

```json
POST /api/v1/holdings/
{
  "portfolio": 1,
  "symbol": "AAPL",
  "quantity": "10",
  "avg_price": "150"
}
```

**Response**

```json
{
  "id": 2,
  "portfolio": 1,
  "symbol": "AAPL",
  "display_name": "",
  "quantity": "10.00000000",
  "avg_price": "150.00000000",
  "cost_basis": "1500.00000000",
  "created_at": "...",
  "updated_at": "..."
}
```

---

# 🔍 Searching, Filtering & Ordering

The API supports:

### For Portfolios
```
?search=<name>
?ordering=name
```

### For Holdings
```
?search=<symbol or display_name>
?ordering=quantity
?portfolio=<portfolio_id>
```

---

# 📑 API Documentation

When `DEBUG = True`, Swagger & ReDoc are available:

```
/api/docs/
/api/redoc/
/api/schema/
```

---

# 🧪 Testing

The project includes:

- pytest + pytest-django  
- 95%+ overall coverage  
- Multi-user tenancy fixtures  
- CRUD + validation + isolation tests  
- Unified JSON error-handling tests  

Run the test suite:

```bash
make test
```

---

# 📦 Deployment

The project ships with:

- `docker-compose.local.yml` – local dev
- `docker-compose.prod.yml` – production image
- Split Django settings for local/staging/production
- Ready for deployment to AWS, GCP, Azure or Render

Production build:

```bash
make prod
```

---
