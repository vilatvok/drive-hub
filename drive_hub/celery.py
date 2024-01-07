import os

from celery import Celery
from celery.schedules import crontab

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "drive_hub.settings")

from django.apps import apps
from django.conf import settings

apps.populate(settings.INSTALLED_APPS)

from datetime import timedelta
from django.contrib.auth import get_user_model
from fuel_store.models import Coupon

app = Celery("drive_hub")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.conf.broker_url = settings.CELERY_BROKER_REDIS_URL
app.autodiscover_tasks()

app.conf.beat_schedule = {}

dates_for_delete = [c.date_end for c in Coupon.objects.all()]
dates_for_set = [c.date_start for c in Coupon.objects.all()]

dates = [("set_coupon", dates_for_set), ("cancel_coupon", dates_for_delete)]

for task_type, date_list in dates:
    for idx, date in enumerate(date_list):
        key = f"{task_type}_{idx}"
        app.conf.beat_schedule[key] = {
            "task": f"fuel_store.tasks.{task_type}",
            "schedule": crontab(
                minute=date.minute,
                hour=date.hour,
                day_of_month=date.day,
                month_of_year=date.month,
            ),
        }

dates_users = [(user, user.date_joined + timedelta(days=365))
               for user in get_user_model().objects.all()]

for user, date in dates_users:
    app.conf.beat_schedule[f"check_days_{user.get_username()}"] = {
        "task": "users.tasks.check_days",
        "schedule": crontab(
            day_of_month=date.day,
            month_of_year=date.month,
        ),
        "args": (user.id,)
    }
