FROM python:3.13-slim

# Avoid .pyc files and ensure logs are unbuffered
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# System deps for psycopg/pgclient
RUN apt-get update && apt-get install -y --no-install-recommends libpq-dev \
  && rm -rf /var/lib/apt/lists/*

# Python deps (Pipenv → system)
COPY Pipfile Pipfile.lock ./
RUN pip install --no-cache-dir pipenv \
  && pipenv install --system --deploy --ignore-pipfile \
  && pip uninstall -y pipenv || true

# App code
COPY . .

# Create non-root user
RUN adduser --disabled-password --gecos '' appuser \
  && chown -R appuser:appuser /app
USER appuser

# Production defaults; compose will set DJANGO_SETTINGS_MODULE
ENV DJANGO_ENV=production
EXPOSE 8000

# Gunicorn for API-only Django
CMD ["gunicorn", "portfolio_tracker_api.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3", "--timeout", "60"]
