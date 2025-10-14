from .base import *
import os

# -----------------------------------------
# Core
# -----------------------------------------
DEBUG = False  # keep False to mirror prod behaviour

ALLOWED_HOSTS = [h for h in os.getenv("ALLOWED_HOSTS", "").split(",") if h] or [
    "staging.yourdomain.com"
]
CSRF_TRUSTED_ORIGINS = [
    f"https://{h}"
    for h in ALLOWED_HOSTS
    if h and not h.startswith(("localhost", "127.0.0.1"))
]

# -----------------------------------------
# DRF renderers (JSON only by default; optionally enable Browsable)
# -----------------------------------------
_ENABLE_BROWSABLE = os.getenv("STAGING_BROWSABLE_API", "true").lower() == "true"

REST_FRAMEWORK["DEFAULT_RENDERER_CLASSES"] = (
    ("rest_framework.renderers.JSONRenderer",)
    if not _ENABLE_BROWSABLE
    else (
        "rest_framework.renderers.JSONRenderer",
        "rest_framework.renderers.BrowsableAPIRenderer",
    )
)

# -----------------------------------------
# Docs (Swagger/ReDoc)
# -----------------------------------------
# Keep docs on by default in staging (toggle with env if needed)
SPECTACULAR_SETTINGS["SERVE_INCLUDE_SCHEMA"] = True
# If you prefer to hide docs, set STAGING_DOCS_PUBLIC=false and
# guard urls in urls.py (see note below).
STAGING_DOCS_PUBLIC = os.getenv("STAGING_DOCS_PUBLIC", "true").lower() == "true"

# -----------------------------------------
# Security (slightly softer than prod)
# -----------------------------------------
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# Shorter HSTS in staging; no preload
SECURE_HSTS_SECONDS = int(os.getenv("SECURE_HSTS_SECONDS", "86400"))  # 1 day
SECURE_HSTS_INCLUDE_SUBDOMAINS = False
SECURE_HSTS_PRELOAD = False
# If behind a proxy that sets X-Forwarded-Proto:
# SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# -----------------------------------------
# Logging (more chatty than prod)
# -----------------------------------------
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {"console": {"class": "logging.StreamHandler"}},
    "loggers": {
        "django.request": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
        "django.db.backends": {  # set to DEBUG temporarily if you need SQL traces
            "handlers": ["console"],
            "level": os.getenv("DJANGO_DB_LOG_LEVEL", "WARNING"),
        },
    },
    "root": {"handlers": ["console"], "level": "INFO"},
}

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],  # you don't need any project templates
        "APP_DIRS": True,  # load templates from installed apps
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]
