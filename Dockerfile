FROM python:3.13-slim

WORKDIR /app

# System deps for psycopg/pgclient
RUN apt-get update && apt-get install -y --no-install-recommends libpq-dev \
  && rm -rf /var/lib/apt/lists/*

# Python deps (Pipenv → system)
COPY Pipfile Pipfile.lock ./
RUN pip install --no-cache-dir pipenv \
  && pipenv install --system --deploy

# App code
COPY . .

# Production defaults; compose will set DJANGO_SETTINGS_MODULE
ENV DJANGO_ENV=production
EXPOSE 8000

# Gunicorn for API-only Django
CMD ["gunicorn", "portfolio_tracker_api.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3", "--timeout", "60"]
