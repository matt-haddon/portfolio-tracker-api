"""
ASGI config for portfolio_tracker_api project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application

def get_settings_module():
    env = os.getenv("DJANGO_ENV", "local").lower()
    if env == "production":
        return "portfolio_tracker_api.settings.production"
    elif env == "staging":
        return "portfolio_tracker_api.settings.staging" 
    else:
        return "portfolio_tracker_api.settings.local"

os.environ.setdefault('DJANGO_SETTINGS_MODULE', get_settings_module())

application = get_asgi_application()
