import json

from datetime import timedelta
from celery import shared_task

from django_celery_beat.models import CrontabSchedule, PeriodicTask


# check count of days user registered
@shared_task
def get_activity_achievement(user_id):
    from django.contrib.auth import get_user_model
    from users.models import Achievement, UserAchievement

    user = get_user_model().objects.get(id=user_id)

    ach = Achievement.objects.get(title='Active days')
    user_ach = UserAchievement.objects.get(user=user)
    user_ach.user_achievement.add(ach)


# check how many orders user has
@shared_task
def get_orders_achievement(user_id):
    from django.contrib.auth import get_user_model
    from users.models import Achievement, UserAchievement

    user = get_user_model().objects.get(id=user_id)

    ach = Achievement.objects.get(title='Count orders')
    user_ach = UserAchievement.objects.get(user=user)
    user_ach.user_achievement.add(ach)


def get_activity_scheduler(user_id, username, date_joined):
    date = date_joined + timedelta(days=365)
    crontab, _ = CrontabSchedule.objects.get_or_create(
        day_of_month=date.day,
        month_of_year=date.month,
    )

    PeriodicTask.objects.create(
        crontab=crontab,
        name=f'get-activity-achievement-{username}',
        task='users.tasks.get_activity_achievement',
        args=json.dumps([user_id]),
        one_off=True,
    )
