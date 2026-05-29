import os
from datetime import timedelta
from pathlib import Path
from typing import Any

import dj_database_url
from dotenv import load_dotenv

# ------------------------------------------------------------
# CORE PATHS & ENV
# ------------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR.parent / ".env")

SECRET_KEY = os.getenv("SECRET_KEY", "unsafe-default")
DEBUG = os.getenv("DEBUG", "False").lower() == "true"
ALLOWED_HOSTS = [h for h in os.getenv("ALLOWED_HOSTS", "").split(",") if h] or [
    "localhost",
    "127.0.0.1",
    "0.0.0.0",  # Docker
    "web",  # docker-compose service name
]

# ------------------------------------------------------------
# APPLICATIONS
# ------------------------------------------------------------


INSTALLED_APPS = [
    # Django essentials
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django_filters",
    # REST Framework
    "rest_framework",
    "corsheaders",
    # Swagger
    "drf_spectacular",
    # Third Party Apps
    "django_celery_beat",
    # Local apps
    "core",
    "users",
    "portfolio",
    "prices",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]


CORS_ALLOWED_ORIGINS = [
    "https://app.yoursite.com",
    "http://localhost:3000",  # during local dev
]

ROOT_URLCONF = "portfolio_tracker_api.urls"
WSGI_APPLICATION = "portfolio_tracker_api.wsgi.application"
ASGI_APPLICATION = "portfolio_tracker_api.asgi.application"

SPECTACULAR_SETTINGS = {
    "TITLE": "Portfolio Tracker API",
    "DESCRIPTION": "Endpoints for portfolios, holdings, valuations, and auth.",
    "VERSION": "1.0.0",
    # Optional niceties:
    "SERVE_INCLUDE_SCHEMA": False,
}

# ------------------------------------------------------------
# DATABASE CONFIGURATION
# ------------------------------------------------------------

DATABASES: dict[str, Any]

# Database: prefer DATABASE_URL, else fall back to discrete vars
_db_url = os.getenv("DATABASE_URL")

if _db_url:
    # ✅ Production / Cloud / CI — use DATABASE_URL
    DATABASES = {
        "default": dj_database_url.parse(
            _db_url,
            conn_max_age=600,  # keeps connections open
            ssl_require=False,  # change to True in production if needed
        )
    }
else:
    # ✅ Local / Docker development — use explicit variables
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": os.getenv("POSTGRES_DB", "portfolio"),
            "USER": os.getenv("POSTGRES_USER", "postgres"),
            "PASSWORD": os.getenv("POSTGRES_PASSWORD", ""),
            "HOST": os.getenv("POSTGRES_HOST", "db"),
            "PORT": os.getenv("POSTGRES_PORT", "5432"),
        }
    }

# Safe for all environments
DATABASES["default"]["ATOMIC_REQUESTS"] = True
DATABASES["default"]["CONN_HEALTH_CHECKS"] = True

# ------------------------------------------------
# AUTH / USERS
# ------------------------------------------------
AUTH_USER_MODEL = "users.CustomUser"


# ------------------------------------------------------------
# INTERNATIONALIZATION
# ------------------------------------------------------------

LANGUAGE_CODE = "en-gb"
TIME_ZONE = "Europe/London"
USE_I18N = True
USE_TZ = True

# ------------------------------------------------------------
# REST FRAMEWORK CONFIGURATION
# ------------------------------------------------------------

REST_FRAMEWORK = {
    # Renderers
    "DEFAULT_RENDERER_CLASSES": ("rest_framework.renderers.JSONRenderer",),
    "DEFAULT_PARSER_CLASSES": ("rest_framework.parsers.JSONParser",),
    # Authentication / Permissions
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    # Filtering / Ordering (for portfolio endpoints)
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.SearchFilter",
        "rest_framework.filters.OrderingFilter",
    ],
    # Pagination
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 25,
    # Schema
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    # Exceptions handler
    "EXCEPTION_HANDLER": "core.exceptions.exception_handler",
}

if DEBUG:
    REST_FRAMEWORK["DEFAULT_RENDERER_CLASSES"] += ("rest_framework.renderers.BrowsableAPIRenderer",)


# ------------------------------------------------------------
# PASSWORD VALIDATORS
# (Keep these for Django's auth system even if you use API tokens)
# ------------------------------------------------------------


AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# ------------------------------------------------
# JWT CONFIG
# ------------------------------------------------


SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=30),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "AUTH_HEADER_TYPES": ("Bearer",),
    "UPDATE_LAST_LOGIN": True,
}

# ------------------------------------------------------------
# REDIS
# ------------------------------------------------------------

REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")

# ------------------------------------------------------------
# CELERY
# ------------------------------------------------------------

CELERY_BROKER_URL = REDIS_URL
CELERY_RESULT_BACKEND = REDIS_URL
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = TIME_ZONE
CELERY_BEAT_SCHEDULER = "django_celery_beat.schedulers:DatabaseScheduler"

# ------------------------------------------------------------
# CACHE
# ------------------------------------------------------------

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": REDIS_URL,
        "TIMEOUT": 300,  # 5 minutes default
    }
}

PRICE_CACHE_TTL = int(os.getenv("PRICE_CACHE_TTL", 900))  # 15 minutes

# ------------------------------------------------------------
# MISC SETTINGS
# ------------------------------------------------------------

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
APPEND_SLASH = False  # friendlier for pure APIs; keeps /api/v1/users/me (no trailing slash)
