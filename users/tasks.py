from celery import shared_task


# check count of days user registered
@shared_task
def check_days(user_id):
    from django.contrib.auth import get_user_model
    from .models import Achievement, UserAchievement

    user = get_user_model().objects.get(id=user_id)

    ach = Achievement.objects.get(title="Days registered")
    user_ach = UserAchievement.objects.get(user=user)
    user_ach.user_achievement.add(ach)


# check how many orders user has
@shared_task
def check_orders(user_id):
    from django.contrib.auth import get_user_model
    from .models import Achievement, UserAchievement

    user = get_user_model().objects.get(id=user_id)

    ach = Achievement.objects.get(title="Count orders")
    user_ach = UserAchievement.objects.get(user=user)
    user_ach.user_achievement.add(ach)
