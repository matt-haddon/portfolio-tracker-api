from pathlib import Path
import os
from dotenv import load_dotenv
import dj_database_url

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
]

# ------------------------------------------------------------
# APPLICATIONS
# ------------------------------------------------------------


INSTALLED_APPS = [
    # Django essentials
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    # REST Framework
    "rest_framework",
    "corsheaders",
    # Swagger
    "drf_spectacular",
    "drf_spectacular_sidecar",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]


CORS_ALLOWED_ORIGINS = [
    "https://app.yoursite.com",
    # "http://localhost:3000",  # during local dev
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
    "DEFAULT_RENDERER_CLASSES": ("rest_framework.renderers.JSONRenderer",),
    "DEFAULT_PARSER_CLASSES": ("rest_framework.parsers.JSONParser",),
    "DEFAULT_AUTHENTICATION_CLASSES": [],
    "DEFAULT_PERMISSION_CLASSES": [],
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}


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

# ------------------------------------------------------------
# MISC SETTINGS
# ------------------------------------------------------------

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
