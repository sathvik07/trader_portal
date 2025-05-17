# traders_portal/celery.py
import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'traders_portal.settings')

app = Celery('traders_portal')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
