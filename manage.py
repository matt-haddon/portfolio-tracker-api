#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys

def get_settings_module():
    env = os.getenv("DJANGO_ENV", "local").lower()
    if env == "production":
        return "portfolio_tracker_api.settings.production"
    elif env == "staging":
        return "portfolio_tracker_api.settings.staging" 
    else:
        return "portfolio_tracker_api.settings.local"


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', get_settings_module())
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
