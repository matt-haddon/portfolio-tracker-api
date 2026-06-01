from celery import Celery
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', "portfolio_tracker_api.settings.local")

app = Celery('portfolio_tracker_api')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()


