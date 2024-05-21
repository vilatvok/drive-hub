import os

from django.conf import settings

from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'drive_hub.settings')

app = Celery('drive_hub')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.conf.broker_url = settings.CELERY_BROKER_URL
app.conf.beat_scheduler = settings.CELERY_BEAT_SCHEDULER
app.autodiscover_tasks()
